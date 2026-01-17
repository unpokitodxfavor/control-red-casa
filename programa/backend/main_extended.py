"""
main_extended.py - Backend extendido con todas las funcionalidades PRTG-like.

INSTRUCCIONES DE USO:
1. Renombrar main.py actual a main_old.py (backup)
2. Renombrar este archivo a main.py
3. Ejecutar: pip install -r requirements.txt
4. Iniciar: python main.py

NUEVAS FUNCIONALIDADES:
- WebSockets para tiempo real
- Endpoints de métricas históricas
- Gestión de sensores
- Reglas de alertas
- Endpoints de grupos y tags
- Sistema de gráficos
"""

import asyncio
import threading
import time
import datetime
import psutil
import socket
from fastapi import FastAPI, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from winotify import Notification
import logging
from typing import List, Optional
from pydantic import BaseModel
import ctypes

# Importar modelos de base de datos
from database import (
    SessionLocal, init_db, Device, Alert, Config, Sensor, 
    MetricHistory, AlertRule, PortScan, DeviceGroup
)
from scanner import scan_network_arp, resolve_hostname, get_vendor_from_mac
from websocket_manager import manager as ws_manager
from metrics_worker import MetricsCollector, auto_create_ping_sensors

# Setup Logging
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

# Metrics collector instance
metrics_collector = None

class MDNSListener:
    def remove_service(self, zeroconf, type, name):
        pass
    def add_service(self, zeroconf, type, name):
        try:
            info = zeroconf.get_service_info(type, name)
            if info:
                for addr in info.addresses:
                    ip = socket.inet_ntoa(addr)
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

app = FastAPI(title="Control Red Casa Pro API", version="2.0.0")

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
            app_id="control-red-casa-pro",
            title=title,
            msg=msg,
            duration="short"
        )
        toast.show()
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

def get_local_network():
    """Detección mejorada de red local"""
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
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
                    if addr.address.startswith("172.") or addr.address.startswith("169.254"):
                        continue
                        
                    ip = addr.address
                    base_ip = ".".join(ip.split(".")[:-1]) + ".0/24"
                    logger.info(f"Using network: {base_ip} on interface: {iface}")
                    return base_ip
                    
        for iface, iface_addrs in addrs.items():
            for addr in iface_addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                     return ".".join(addr.address.split(".")[:-1]) + ".0/24"

    except Exception as e:
        logger.error(f"Error detecting network: {e}")
    
    return "192.168.1.0/24"

# Background Scanner (mejorado con broadcasting WebSocket)
def background_scanner():
    logger.info("Background scanner started.")
    while True:
        db = SessionLocal()
        try:
            net_range = get_local_network()
            found_devices = scan_network_arp(net_range)
            
            now = datetime.datetime.utcnow()
            found_macs = [d['mac'] for d in found_devices]

            for d in found_devices:
                device = db.query(Device).filter(Device.mac == d['mac']).first()
                if not device:
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
                    
                    alert_msg = f"Nuevo dispositivo detectado: {hostname or 'Desconocido'} ({d['ip']})"
                    new_alert = Alert(
                        device_id=new_dev.id, 
                        type="NEW_DEVICE",
                        level="INFO",
                        message=alert_msg
                    )
                    db.add(new_alert)
                    db.commit()
                    
                    send_notification("Nuevo Dispositivo", alert_msg)
                    
                    # Broadcast via WebSocket
                    asyncio.run(ws_manager.broadcast_device_update({
                        "id": new_dev.id,
                        "mac": new_dev.mac,
                        "ip": new_dev.ip,
                        "hostname": new_dev.hostname,
                        "status": "Online",
                        "vendor": new_dev.vendor
                    }))
                    asyncio.run(ws_manager.broadcast_alert({
                        "id": new_alert.id,
                        "type": "NEW_DEVICE",
                        "level": "INFO",
                        "message": alert_msg
                    }))
                    
                else:
                    if device.status == "Offline":
                        alert_msg = f"Dispositivo ha vuelto: {device.hostname or device.ip}"
                        new_alert = Alert(
                            device_id=device.id,
                            type="REAPPEARED",
                            level="INFO",
                            message=alert_msg
                        )
                        db.add(new_alert)
                        send_notification("Dispositivo en Red", alert_msg)
                    
                    if not device.hostname or device.hostname == "Unknown" or device.hostname == "":
                         m_name = MDNS_NAME_CACHE.get(d['ip'])
                         if m_name:
                             device.hostname = m_name
                         else:
                             device.hostname = resolve_hostname(d['ip'])
                    
                    if not device.vendor or device.vendor == "Unknown Vendor":
                         device.vendor = get_vendor_from_mac(d['mac'])
                         device.device_type = guess_device_type(device.vendor, device.hostname)

                    if device.hostname == "Unknown" and device.vendor != "Unknown Vendor":
                        device.hostname = f"Dispositivo {device.vendor}"

                    device.status = "Online"
                    device.ip = d['ip']
                    device.last_seen = now
                db.commit()

            # Mark Offline
            threshold = now - datetime.timedelta(minutes=5)
            offline_devices = db.query(Device).filter(
                Device.status == "Online",
                ~Device.mac.in_(found_macs),
                Device.last_seen < threshold
            ).all()

            for dev in offline_devices:
                dev.status = "Offline"
                alert_msg = f"Dispositivo desconectado: {dev.hostname or dev.ip}"
                new_alert = Alert(
                    device_id=dev.id,
                    type="OFFLINE",
                    level="WARNING",
                    message=alert_msg
                )
                db.add(new_alert)
                send_notification("Dispositivo Offline", alert_msg)
            
            db.commit()
            
            # Broadcast status update
            total = db.query(Device).count()
            online = db.query(Device).filter(Device.status == "Online").count()
            asyncio.run(ws_manager.broadcast_status({
                "total": total,
                "online": online
            }))
            
        except Exception as e:
            logger.error(f"Error in background scan: {e}")
        finally:
            db.close()
        
        time.sleep(60)

@app.on_event("startup")
async def startup_event():
    global metrics_collector
    
    init_db()
    start_mdns_listener()

    if not is_admin():
        logger.warning("!!! LA APLICACION NO ESTA CORRIENDO COMO ADMINISTRADOR !!!")
        logger.warning("El escaneo ARP de Scapy probablemente fallará.")
    
    # Auto-crear sensores de ping
    auto_create_ping_sensors()
    
    # Start scanning thread
    thread = threading.Thread(target=background_scanner, daemon=True)
    thread.start()
    
    # Start metrics collector
    metrics_collector = MetricsCollector()
    asyncio.create_task(metrics_collector.start())
    
    logger.info("🚀 Control Red Casa Pro iniciado correctamente")

# ============================================
# ENDPOINTS BÁSICOS (Existentes)
# ============================================

@app.get("/devices")
def get_devices(db: Session = Depends(get_db)):
    return db.query(Device).all()

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db), limit: int = 50):
    return db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()

@app.get("/status")
def get_status(db: Session = Depends(get_db)):
    total = db.query(Device).count()
    online = db.query(Device).filter(Device.status == "Online").count()
    new_today = db.query(Device).filter(
        Device.first_seen >= datetime.datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()
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

# ============================================
# NUEVOS ENDPOINTS - MÉTRICAS
# ============================================

@app.get("/metrics/device/{device_id}")
def get_device_metrics(
    device_id: int,
    metric_name: Optional[str] = None,
    hours: int = Query(24, description="Horas de histórico"),
    db: Session = Depends(get_db)
):
    """Obtiene métricas históricas de un dispositivo"""
    since = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    
    query = db.query(MetricHistory).filter(
        MetricHistory.device_id == device_id,
        MetricHistory.timestamp >= since
    )
    
    if metric_name:
        query = query.filter(MetricHistory.metric_name == metric_name)
    
    metrics = query.order_by(MetricHistory.timestamp.asc()).all()
    
    return {
        "device_id": device_id,
        "metric_name": metric_name,
        "hours": hours,
        "count": len(metrics),
        "data": [
            {
                "timestamp": m.timestamp.isoformat(),
                "metric_name": m.metric_name,
                "value": m.value,
                "unit": m.unit
            } for m in metrics
        ]
    }

@app.get("/metrics/summary/{device_id}")
def get_metrics_summary(device_id: int, db: Session = Depends(get_db)):
    """Resumen de métricas de un dispositivo (últimas 24h)"""
    since = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    
    # Obtener estadísticas agregadas
    result = db.query(
        MetricHistory.metric_name,
        func.avg(MetricHistory.value).label('avg_value'),
        func.min(MetricHistory.value).label('min_value'),
        func.max(MetricHistory.value).label('max_value'),
        func.count(MetricHistory.id).label('count')
    ).filter(
        MetricHistory.device_id == device_id,
        MetricHistory.timestamp >= since
    ).group_by(MetricHistory.metric_name).all()
    
    return {
        "device_id": device_id,
        "period": "24h",
        "summary": [
            {
                "metric_name": r.metric_name,
                "avg": round(r.avg_value, 2) if r.avg_value else 0,
                "min": round(r.min_value, 2) if r.min_value else 0,
                "max": round(r.max_value, 2) if r.max_value else 0,
                "count": r.count
            } for r in result
        ]
    }

# ============================================
# NUEVOS ENDPOINTS - SENSORES
# ============================================

class SensorCreate(BaseModel):
    device_id: int
    name: str
    sensor_type: str
    config: dict = {}
    interval: int = 60
    enabled: bool = True

@app.get("/sensors")
def get_sensors(device_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Lista todos los sensores o por dispositivo"""
    query = db.query(Sensor)
    if device_id:
        query = query.filter(Sensor.device_id == device_id)
    return query.all()

@app.post("/sensors")
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    """Crea un nuevo sensor"""
    new_sensor = Sensor(
        device_id=sensor.device_id,
        name=sensor.name,
        sensor_type=sensor.sensor_type,
        config=sensor.config,
        interval=sensor.interval,
        enabled=sensor.enabled
    )
    db.add(new_sensor)
    db.commit()
    db.refresh(new_sensor)
    return new_sensor

@app.put("/sensors/{sensor_id}/toggle")
def toggle_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """Activa/desactiva un sensor"""
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        return {"error": "Sensor not found"}
    
    sensor.enabled = not sensor.enabled
    db.commit()
    return {"status": "success", "enabled": sensor.enabled}

@app.delete("/sensors/{sensor_id}")
def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """Elimina un sensor"""
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        return {"error": "Sensor not found"}
    
    db.delete(sensor)
    db.commit()
    return {"status": "success", "message": "Sensor eliminado"}

# ============================================
# NUEVOS ENDPOINTS - GRUPOS Y TAGS
# ============================================

class GroupCreate(BaseModel):
    name: str
    description: str = ""
    color: str = "#3b82f6"

@app.get("/groups")
def get_groups(db: Session = Depends(get_db)):
    """Lista todos los grupos"""
    return db.query(DeviceGroup).all()

@app.post("/groups")
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    """Crea un nuevo grupo"""
    new_group = DeviceGroup(
        name=group.name,
        description=group.description,
        color=group.color
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

class DeviceUpdate(BaseModel):
    tags: Optional[str] = None
    group_id: Optional[int] = None
    is_authorized: Optional[bool] = None
    notes: Optional[str] = None

@app.put("/devices/{device_id}")
def update_device(device_id: int, update: DeviceUpdate, db: Session = Depends(get_db)):
    """Actualiza tags, grupo, autorización, etc de un dispositivo"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        return {"error": "Device not found"}
    
    if update.tags is not None:
        device.tags = update.tags
    if update.group_id is not None:
        device.group_id = update.group_id
    if update.is_authorized is not None:
        device.is_authorized = update.is_authorized
    if update.notes is not None:
        device.notes = update.notes
    
    db.commit()
    return {"status": "success"}

# ============================================
# WEBSOCKET ENDPOINT
# ============================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para actualizaciones en tiempo real"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Mantener conexión abierta y recibir mensajes
            data = await websocket.receive_text()
            # Echo o procesar comandos del cliente
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("Cliente WebSocket desconectado")

# ============================================
# INICIO DE LA APLICACIÓN
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
