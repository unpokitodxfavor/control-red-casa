import asyncio
import threading
import time
import datetime
import psutil
import socket
from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from winotify import Notification, Registry
import logging

from database import SessionLocal, init_db, Device, Alert, Config
from scanner import scan_network_arp, resolve_hostname, get_vendor_from_mac

from pydantic import BaseModel
import logging
import os
import ctypes

# Setup Logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global cache for mDNS discovered names
MDNS_NAME_CACHE = {}

class MDNSListener:
    def remove_service(self, zeroconf, type, name):
        pass
    def add_service(self, zeroconf, type, name):
        try:
            info = zeroconf.get_service_info(type, name)
            if info:
                for addr in info.addresses:
                    ip = socket.inet_ntoa(addr)
                    # Get a clean name (e.g., Google-Nest-Mini)
                    clean_name = name.split('.')[0]
                    MDNS_NAME_CACHE[ip] = clean_name
                    logger.info(f"mDNS Discovery: {ip} is {clean_name}")
        except:
            pass
    def update_service(self, zc, type, name):
        self.add_service(zc, type, name)

def start_mdns_listener():
    try:
        from zeroconf import Zeroconf, ServiceBrowser
        zc = Zeroconf()
        listener = MDNSListener()
        # Common services to browse
        services = ["_googlecast._tcp.local.", "_hap._tcp.local.", "_printer._tcp.local.", "_smb._tcp.local."]
        ServiceBrowser(zc, services, listener)
        return zc
    except Exception as e:
        logger.error(f"Failed to start mDNS listener: {e}")
        return None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

app = FastAPI(title="Control Red Casa API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def guess_device_type(vendor, hostname):
    v = vendor.lower()
    h = (hostname or "").lower()
    
    if any(k in v or k in h for k in ["apple", "iphone", "ipad", "android", "samsung", "huawei", "xiaomi", "mobile", "phone"]):
        return "Mobile/Tablet"
    if any(k in v or k in h for k in ["cisco", "tplink", "tp-link", "dlink", "d-link", "huawei", "router", "gateway", "mikrotik"]):
        return "Router/Network"
    if any(k in v or k in h for k in ["hp", "canon", "epson", "brother", "printer", "lexmark"]):
        return "Printer"
    if any(k in v or k in h for k in ["raspberry", "esp32", "espressif", "iot", "arduino", "nest", "google home", "alexa"]):
        return "IoT/Device"
    if any(k in v or k in h for k in ["vmware", "virtualbox", "microsoft", "windows", "linux", "desktop", "laptop", "pc"]):
        return "PC/Server"
    
    return "Unknown"

def send_notification(title, msg):
    try:
        toast = Notification(
            app_id="control-red-casa",
            title=title,
            msg=msg,
            duration="short"
        )
        toast.show()
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

def get_local_network():
    """
    Refined detection to prioritize physical adapters (Ethernet/WiFi).
    """
    try:
        import psutil
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        # Sort interfaces: prioritize those that are UP and likely physical
        ifaces = sorted(addrs.keys(), key=lambda x: (
            not ("vEthernet" in x or "WSL" in x or "Docker" in x or "VMware" in x or "VirtualBox" in x),
            stats[x].isup if x in stats else False
        ), reverse=True)

        for iface in ifaces:
            if iface in stats and not stats[iface].isup:
                continue
                
            iface_addrs = addrs.get(iface, [])
            for addr in iface_addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    # Avoid common virtual subnets if possible
                    if addr.address.startswith("172.") or addr.address.startswith("169.254"):
                        continue
                        
                    ip = addr.address
                    base_ip = ".".join(ip.split(".")[:-1]) + ".0/24"
                    logger.info(f"Using network: {base_ip} on interface: {iface}")
                    return base_ip
                    
        # Fallback if no ideal physical found
        for iface, iface_addrs in addrs.items():
            for addr in iface_addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                     return ".".join(addr.address.split(".")[:-1]) + ".0/24"

    except Exception as e:
        logger.error(f"Error detecting network: {e}")
    
    return "192.168.1.0/24"

# Background Scan Loop
def background_scanner():
    logger.info("Background scanner started.")
    while True:
        db = SessionLocal()
        try:
            net_range = get_local_network()
            found_devices = scan_network_arp(net_range)
            
            now = datetime.datetime.utcnow()
            found_macs = [d['mac'] for d in found_devices]

            # Update existing or create new
            for d in found_devices:
                device = db.query(Device).filter(Device.mac == d['mac']).first()
                if not device:
                    # New Device!
                    hostname = resolve_hostname(d['ip'])
                    vendor = get_vendor_from_mac(d['mac'])
                    device_type = guess_device_type(vendor, hostname)
                    new_dev = Device(
                        mac=d['mac'],
                        ip=d['ip'],
                        hostname=hostname,
                        vendor=vendor,
                        device_type=device_type,
                        status="Online",
                        first_seen=now,
                        last_seen=now
                    )
                    db.add(new_dev)
                    db.commit()
                    db.refresh(new_dev)
                    
                    # Alert
                    alert_msg = f"Nuevo dispositivo detectado: {hostname or 'Desconocido'} ({d['ip']})"
                    new_alert = Alert(device_id=new_dev.id, type="NEW_DEVICE", message=alert_msg)
                    db.add(new_alert)
                    send_notification("Nuevo Dispositivo", alert_msg)
                else:
                    # Update existing
                    if device.status == "Offline":
                        alert_msg = f"Dispositivo ha vuelto: {device.hostname or device.ip}"
                        new_alert = Alert(device_id=device.id, type="REAPPEARED", message=alert_msg)
                        db.add(new_alert)
                        send_notification("Dispositivo en Red", alert_msg)
                    
                    # RE-IDENTIFY if currently unknown
                    # Try to get name from mDNS cache first, then standard resolution
                    if not device.hostname or device.hostname == "Unknown" or device.hostname == "":
                         m_name = MDNS_NAME_CACHE.get(d['ip'])
                         if m_name:
                             device.hostname = m_name
                         else:
                             device.hostname = resolve_hostname(d['ip'])
                    
                    if not device.vendor or device.vendor == "Unknown Vendor":
                         device.vendor = get_vendor_from_mac(d['mac'])
                         device.device_type = guess_device_type(device.vendor, device.hostname)

                    # Final fallback for better display: if still unknown, use Smart Alias
                    if device.hostname == "Unknown" and device.vendor != "Unknown Vendor":
                        device.hostname = f"Dispositivo {device.vendor}"

                    device.status = "Online"
                    device.ip = d['ip']
                    device.last_seen = now
                db.commit()

            # Mark Offline
            # Devices not found in this scan and last seen > 5 mins ago
            threshold = now - datetime.timedelta(minutes=5)
            offline_devices = db.query(Device).filter(
                Device.status == "Online",
                ~Device.mac.in_(found_macs),
                Device.last_seen < threshold
            ).all()

            for dev in offline_devices:
                dev.status = "Offline"
                alert_msg = f"Dispositivo desconectado: {dev.hostname or dev.ip}"
                new_alert = Alert(device_id=dev.id, type="OFFLINE", message=alert_msg)
                db.add(new_alert)
                send_notification("Dispositivo Offline", alert_msg)
            
            db.commit()
        except Exception as e:
            logger.error(f"Error in background scan: {e}")
        finally:
            db.close()
        
        time.sleep(60) # Scan every 60 seconds

@app.on_event("startup")
async def startup_event():
    init_db()
    
    # Start mDNS listener in background
    start_mdns_listener()

    if not is_admin():
        logger.warning("!!! LA APLICACION NO ESTA CORRIENDO COMO ADMINISTRADOR !!!")
        logger.warning("El escaneo ARP de Scapy probablemente fallará.")
    
    # Start scanning thread
    thread = threading.Thread(target=background_scanner, daemon=True)
    thread.start()

@app.get("/devices")
def get_devices(db: Session = Depends(get_db)):
    return db.query(Device).all()

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.timestamp.desc()).limit(50).all()

@app.get("/status")
def get_status(db: Session = Depends(get_db)):
    total = db.query(Device).count()
    online = db.query(Device).filter(Device.status == "Online").count()
    new_today = db.query(Device).filter(Device.first_seen >= datetime.datetime.utcnow().replace(hour=0, minute=0, second=0)).count()
    return {
        "total": total,
        "online": online,
        "new_today": new_today
    }

class AliasUpdate(BaseModel):
    alias: str

@app.put("/devices/{device_mac}/alias")
def update_alias(device_mac: str, update: AliasUpdate, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.mac == device_mac).first()
    if not device:
        return {"error": "Device not found"}
    device.alias = update.alias
    db.commit()
    return {"status": "success", "alias": device.alias}

@app.post("/devices/reidentify")
def reidentify_unknown_devices(db: Session = Depends(get_db)):
    """
    Fuerza la re-identificación de todos los dispositivos con vendor desconocido.
    """
    logger.info("Iniciando re-identificación manual de dispositivos...")
    
    unknown_devices = db.query(Device).filter(
        (Device.vendor == "Unknown Vendor") | (Device.vendor == None)
    ).all()
    
    updated_count = 0
    for device in unknown_devices:
        old_vendor = device.vendor
        new_vendor = get_vendor_from_mac(device.mac)
        
        if new_vendor != "Unknown Vendor" and new_vendor != old_vendor:
            device.vendor = new_vendor
            device.device_type = guess_device_type(new_vendor, device.hostname)
            updated_count += 1
            logger.info(f"Actualizado {device.mac}: {old_vendor} -> {new_vendor}")
    
    db.commit()
    
    return {
        "status": "success",
        "total_unknown": len(unknown_devices),
        "updated": updated_count,
        "message": f"Se actualizaron {updated_count} de {len(unknown_devices)} dispositivos desconocidos"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
