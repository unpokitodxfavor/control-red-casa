

import sys
import os


# Fix for PyInstaller noconsole mode where stdout/stderr are None
# Redirect to file for debugging
try:
    log_file = open("debug_boot.log", "w", encoding="utf-8")
    sys.stdout = log_file
    sys.stderr = log_file
except Exception as e:
    pass



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
import json
import mimetypes

# FORCE MIME TYPES (Fix for Windows Registry issues)
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('image/svg+xml', '.svg')


# Importar modelos de base de datos
from database import (
    SessionLocal, init_db, Device, Alert, Config, Sensor, 
    MetricHistory, AlertRule, PortScan, DeviceGroup
)
from scanner import scan_network_arp, resolve_hostname, get_vendor_from_mac
from websocket_manager import manager as ws_manager
from metrics_worker import MetricsCollector, auto_create_ping_sensors
from alerts import AlertManager, AlertLevel, AlertChannel, AlertCondition
from snmp_worker import SNMPWorker

# Global SNMP Worker
snmp_worker = None

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

# Alert manager instance
alert_manager = None

# Alert configuration
ALERT_CONFIG = {
    'email': {
        'enabled': False,  # Cambiar a True y configurar para usar
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': 'tu-email@gmail.com',
        'smtp_password': 'tu-password-o-app-password',
        'from_email': 'alerts@control-red-casa.com',
        'to_email': 'admin@ejemplo.com'
    },
    'telegram': {
        'enabled': False,  # Cambiar a True y configurar para usar
        'bot_token': 'YOUR_BOT_TOKEN_HERE',
        'chat_id': 'YOUR_CHAT_ID_HERE'
    },
    'webhook': {
        'enabled': False,
        'url': 'https://ejemplo.com/webhook',
        'headers': {}
    }
}

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

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sys
import os

# ... imports ...

app = FastAPI(title="Control Red Casa Pro API", version="2.2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files Logic for PyInstaller
if getattr(sys, 'frozen', False):
    # Running as compiled EXE
    base_path = sys._MEIPASS
    static_dir = os.path.join(base_path, "static")
else:
    # Running as script
    base_path = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_path, "static")

# Ensure static directory exists before mounting
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    # Serve index.html for root
    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(static_dir, "index.html"))

    # Catch-all for React Router
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # API requests should have already been handled by specific routes
        if full_path.startswith("api/") or full_path.startswith("config/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
             return {"status": "404", "message": "API Endpoint not found"}
        
        # Serve index.html for everything else
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    logger.warning(f"Static directory not found at {static_dir}. Frontend will not be served.")

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
                        last_seen=now,
                        detected_at=now
                    )
                    db.add(new_dev)
                    db.commit()
                    db.refresh(new_dev)
                    
                    alert_msg = f"Nuevo dispositivo detectado: {hostname or 'Desconocido'} ({d['ip']})"
                    new_alert = Alert(
                        device_id=new_dev.id, 
                        type="NEW_DEVICE",
                        condition="new_device",
                        level="INFO",
                        message=alert_msg,
                        device_name=hostname or 'Desconocido',
                        device_ip=d['ip']
                    )
                    db.add(new_alert)
                    db.commit()
                    
                    send_notification("Nuevo Dispositivo", alert_msg)
                    
                    # Disparar alerta con AlertManager
                    if alert_manager:
                        device_dict = {
                            'id': new_dev.id,
                            'ip': d['ip'],
                            'hostname': hostname,
                            'alias': new_dev.alias,
                            'status': 'Online',
                            'is_authorized': new_dev.is_authorized
                        }
                        alert_manager.process_device_event('new', device_dict)
                    
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
                        device.detected_at = now
                        alert_msg = f"Dispositivo ha vuelto: {device.hostname or device.ip}"
                        new_alert = Alert(
                            device_id=device.id,
                            type="REAPPEARED",
                            condition="device_online",
                            level="INFO",
                            message=alert_msg,
                            device_name=device.hostname or device.ip,
                            device_ip=d['ip']
                        )
                        db.add(new_alert)
                        send_notification("Dispositivo en Red", alert_msg)
                        
                        # Disparar alerta con AlertManager
                        if alert_manager:
                            device_dict = {
                                'id': device.id,
                                'ip': d['ip'],
                                'hostname': device.hostname,
                                'alias': device.alias,
                                'status': 'Online',
                                'is_authorized': device.is_authorized
                            }
                            alert_manager.process_device_event('online', device_dict)
                    
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
                    condition="device_offline",
                    level="WARNING",
                    message=alert_msg,
                    device_name=dev.hostname or dev.ip,
                    device_ip=dev.ip
                )
                db.add(new_alert)
                send_notification("Dispositivo Offline", alert_msg)
                
                # Disparar alerta con AlertManager
                if alert_manager:
                    device_dict = {
                        'id': dev.id,
                        'ip': dev.ip,
                        'hostname': dev.hostname,
                        'alias': dev.alias,
                        'status': 'Offline',
                        'is_authorized': dev.is_authorized
                    }
                    alert_manager.process_device_event('offline', device_dict)
            
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
    global metrics_collector, alert_manager, snmp_worker
    print("\n[STARTUP] 1. Initializing Database...")
    init_db()
    
    # Initialize detected_at if NULL for online devices
    try:
        db = SessionLocal()
        online_devices = db.query(Device).filter(Device.status == "Online", Device.detected_at == None).all()
        if online_devices:
            now = datetime.datetime.utcnow()
            for dev in online_devices:
                dev.detected_at = now
            db.commit()
            logger.info(f"✅ Initialized detected_at for {len(online_devices)} devices")
        db.close()
    except Exception as e:
        logger.error(f"Error initializing detected_at: {e}")
        
    print("[STARTUP] 1. DONE")
    
    # Cargar configuración desde BD
    try:
        print("[STARTUP] 2. Loading Config...")
        db = SessionLocal()
        tg_token = db.query(Config).filter(Config.key == 'telegram_bot_token').first()
        tg_chat_id = db.query(Config).filter(Config.key == 'telegram_chat_id').first()
        tg_enabled = db.query(Config).filter(Config.key == 'telegram_enabled').first()
        
        if tg_token: ALERT_CONFIG['telegram']['bot_token'] = tg_token.value
        if tg_chat_id: ALERT_CONFIG['telegram']['chat_id'] = tg_chat_id.value
        if tg_enabled: ALERT_CONFIG['telegram']['enabled'] = (tg_enabled.value == 'true')
        logger.info("✅ Configuración cargada desde base de datos")
        db.close()
        print("[STARTUP] 2. DONE")
    except Exception as e:
        logger.error(f"Error cargando configuración: {e}")

    # start_mdns_listener()

    if not is_admin():
        logger.warning("!!! LA APLICACION NO ESTA CORRIENDO COMO ADMINISTRADOR !!!")
        logger.warning("El escaneo ARP de Scapy probablemente fallará.")
    
    # Auto-crear sensores de ping en background
    # (Lo ejecutamos en un hilo aparte para que no bloquee el inicio de la API)
    print("[STARTUP] 4. Auto Ping Sensors...")
    threading.Thread(target=auto_create_ping_sensors, daemon=True).start()
    
    # Initialize Alert Manager
    print("[STARTUP] 5. Alert Manager...")
    db = SessionLocal()
    alert_manager = AlertManager(db, ALERT_CONFIG)
    alert_manager.load_rules()
    logger.info("✅ Alert Manager initialized")
    print("[STARTUP] 5. DONE")
    
    # Start scanning thread
    print("[STARTUP] 6. Scanner...")
    thread = threading.Thread(target=background_scanner, daemon=True)
    thread.start()
    
    # Start metrics collector
    print("[STARTUP] 7. Metrics...")
    metrics_collector = MetricsCollector()
    asyncio.create_task(metrics_collector.start())
    
    # Init SNMP Worker (DISABLED BY USER REQUEST)
    # try:
    #     print("[STARTUP] 8. SNMP Worker (Auto-Detecting Gateway)...")
    #     snmp_worker = SNMPWorker(ip="auto", community="public")
    #     asyncio.create_task(snmp_worker.start())
    # except Exception as e:
    #      logger.error(f"Failed to start SNMP Worker: {e}")

    logger.info("🚀 Control Red Casa Pro iniciado correctamente")
    print("[STARTUP] COMPLETED!\n")

@app.on_event("shutdown")
def shutdown_event():
    if metrics_collector:
        metrics_collector.stop()
    if snmp_worker:
        snmp_worker.stop()

# ============================================
# ENDPOINTS BÁSICOS (Existentes)
# ============================================

@app.get("/devices")
def get_devices(db: Session = Depends(get_db)):
    # Debug print
    count = db.query(Device).count()
    print(f"\n[API DEBUG] Sending {count} devices to frontend")
    return db.query(Device).all()

    return {"status": "ok", "message": "Backend is reachable via port 8001"}

# ============================================
# DASHBOARD CONFIGURATION
# ============================================

class DashboardLayout(BaseModel):
    layout: List[dict]
    visible_widgets: Optional[List[str]] = None

@app.get("/config/dashboard")
def get_dashboard_layout(db: Session = Depends(get_db)):
    """Recupera el layout del dashboard guardado"""
    config = db.query(Config).filter(Config.key == "dashboard_layout").first()
    if config and config.value:
        try:
            return {"layout": json.loads(config.value)}
        except:
             return {"layout": []}
    return {"layout": []}

@app.post("/config/dashboard")
def save_dashboard_layout(config: DashboardLayout, db: Session = Depends(get_db)):
    """Guarda el layout del dashboard"""
    db_config = db.query(Config).filter(Config.key == "dashboard_layout").first()
    if not db_config:
        db_config = Config(key="dashboard_layout", category="DASHBOARD", description="User custom layout")
        db.add(db_config)
    
    # Bugfix: Save both layout AND visible_widgets
    data_to_save = {
        "layout": config.layout,
        "visible_widgets": config.visible_widgets
    }
    db_config.value = json.dumps(data_to_save)
    db.commit()
    return {"status": "success"}

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
# NUEVOS ENDPOINTS - PORT SCANNING
# ============================================

from port_scanner import scan_common_ports, scan_ports_range, scan_custom_ports, scan_multiple_ips
from datetime import datetime as dt

class PortScanRequest(BaseModel):
    ips: List[str]
    scan_type: str = 'common'  # 'common', 'range', 'custom'
    custom_ports: Optional[List[int]] = None
    port_range_start: Optional[int] = None
    port_range_end: Optional[int] = None
    timeout: float = 1.0

@app.post("/scan/ports")
def scan_ports_endpoint(request: PortScanRequest, db: Session = Depends(get_db)):
    """
    Escanea puertos en una o más IPs
    """
    try:
        # Preparar parámetros según el tipo de escaneo
        if request.scan_type == 'range' and request.port_range_start and request.port_range_end:
            port_range = (request.port_range_start, request.port_range_end)
            results = scan_multiple_ips(
                request.ips, 
                scan_type='range',
                port_range=port_range,
                timeout=request.timeout
            )
        elif request.scan_type == 'custom' and request.custom_ports:
            results = scan_multiple_ips(
                request.ips,
                scan_type='custom',
                custom_ports=request.custom_ports,
                timeout=request.timeout
            )
        else:  # common
            results = scan_multiple_ips(
                request.ips,
                scan_type='common',
                timeout=request.timeout
            )
        
        # Guardar resultados en la base de datos
        for ip, ports in results.items():
            # Buscar dispositivo por IP
            device = db.query(Device).filter(Device.ip == ip).first()
            if device:
                # Guardar escaneo de puertos
                for port_info in ports:
                    port_scan = PortScan(
                        device_id=device.id,
                        port=port_info['port'],
                        state=port_info['state'],
                        service=port_info['service'],
                        timestamp=dt.utcnow()
                    )
                    db.add(port_scan)
        
        db.commit()
        
        return {
            "status": "success",
            "results": results,
            "total_ips": len(request.ips),
            "total_open_ports": sum(len(ports) for ports in results.values())
        }
    except Exception as e:
        logger.error(f"Error scanning ports: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/scan/ports/{device_id}")
def get_port_scan_history(device_id: int, db: Session = Depends(get_db)):
    """
    Obtiene el historial de escaneos de puertos de un dispositivo
    """
    scans = db.query(PortScan).filter(
        PortScan.device_id == device_id
    ).order_by(PortScan.scan_time.desc()).limit(100).all()
    
    # Agrupar por puerto
    ports_dict = {}
    for scan in scans:
        if scan.port not in ports_dict:
            ports_dict[scan.port] = {
                'port': scan.port,
                'service': scan.service,
                'state': scan.state,
                'last_seen': scan.scan_time.isoformat(),
                'scan_count': 1
            }
        else:
            ports_dict[scan.port]['scan_count'] += 1
    
    return {
        "device_id": device_id,
        "ports": list(ports_dict.values()),
        "total_scans": len(scans)
    }

# ============================================
# ENDPOINTS DE ALERTAS (EXISTENTES)
# ============================================

class TelegramConfig(BaseModel):
    bot_token: str
    chat_id: str
    enabled: bool
    notify_new_device: bool = True
    notify_device_offline: bool = True
    notify_device_online: bool = False

@app.get("/config/telegram")
def get_telegram_config(db: Session = Depends(get_db)):
    tg_token = db.query(Config).filter(Config.key == "telegram_bot_token").first()
    tg_chat_id = db.query(Config).filter(Config.key == "telegram_chat_id").first()
    tg_enabled = db.query(Config).filter(Config.key == "telegram_enabled").first()
    
    # Granular flags
    notify_new = db.query(Config).filter(Config.key == "telegram_notify_new").first()
    notify_offline = db.query(Config).filter(Config.key == "telegram_notify_offline").first()
    notify_online = db.query(Config).filter(Config.key == "telegram_notify_online").first()
    
    return {
        "bot_token": tg_token.value if tg_token else "",
        "chat_id": tg_chat_id.value if tg_chat_id else "",
        "enabled": (tg_enabled.value == "true") if tg_enabled else False,
        "notify_new_device": (notify_new.value == "true") if notify_new else True,
        "notify_device_offline": (notify_offline.value == "true") if notify_offline else True,
        "notify_device_online": (notify_online.value == "true") if notify_online else False
    }

@app.post("/config/telegram")
def save_telegram_config(config: TelegramConfig, db: Session = Depends(get_db)):
    # Helper to save or update
    def save_key(key, value):
        db_conf = db.query(Config).filter(Config.key == key).first()
        if not db_conf:
            db_conf = Config(key=key, category="TELEGRAM", description=f"Telegram {key}")
            db.add(db_conf)
        db_conf.value = str(value)
    
    save_key("telegram_bot_token", config.bot_token)
    save_key("telegram_chat_id", config.chat_id)
    save_key("telegram_enabled", "true" if config.enabled else "false")
    
    # Save granular flags
    save_key("telegram_notify_new", "true" if config.notify_new_device else "false")
    save_key("telegram_notify_offline", "true" if config.notify_device_offline else "false")
    save_key("telegram_notify_online", "true" if config.notify_device_online else "false")
    
    db.commit()
    
    # Update runtime config
    ALERT_CONFIG['telegram']['bot_token'] = config.bot_token
    ALERT_CONFIG['telegram']['chat_id'] = config.chat_id
    ALERT_CONFIG['telegram']['enabled'] = config.enabled
    
    ALERT_CONFIG['telegram']['notify_new_device'] = config.notify_new_device
    ALERT_CONFIG['telegram']['notify_device_offline'] = config.notify_device_offline
    ALERT_CONFIG['telegram']['notify_device_online'] = config.notify_device_online
    
    # Reload alert manager if initialized
    if alert_manager:
        alert_manager.config = ALERT_CONFIG
    
    return {"status": "success"}

@app.post("/api/test-telegram")
def test_telegram_notification(config: TelegramConfig):
    try:
        import requests
        url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"
        payload = {
            "chat_id": config.chat_id,
            "text": "🔔 Prueba exitosa: Control de Red Casa Pro conectado correctamente."
        }
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            return {"status": "success"}
        else:
            return {"status": "error", "message": f"Telegram Error: {resp.text}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, user: str = "admin", db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_acknowledged = True
    alert.acknowledged_by = user
    alert.acknowledged_at = datetime.datetime.utcnow()
    db.commit()
    return {"status": "success"}

@app.get("/api/router/stats")
def get_router_stats():
    if snmp_worker:
        return snmp_worker.metrics
    return {"error": "SNMP Worker not running"}


# Imports for System Tray
import threading
from PIL import Image, ImageDraw
import pystray
import webbrowser

# --- SYSTEM TRAY ICON SETUP ---
def create_image(width, height, color1, color2):
    # Generate a simple icon (e.g. invalid color split or just a solid color)
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image

def on_quit(icon, item):
    icon.stop()
    # Force kill process eventually if threads hang, but icon.stop() usually enough for pystray loop
    # We might need to kill the uvicorn server or just let the process die
    os._exit(0)

def open_dashboard(icon=None, item=None):
    webbrowser.open("http://localhost:8001")

def run_uvicorn():
    try:
        import uvicorn
        # Listen on all interfaces
        # log_config=None prevents uvicorn from trying to configure logging again
        uvicorn.run(app, host="0.0.0.0", port=8001, log_config=None)
    except Exception as e:
        import traceback
        with open("crash_startup.txt", "w") as f:
            f.write(f"Startup Error at {datetime.datetime.now()}:\n")
            f.write(traceback.format_exc())

if __name__ == "__main__":
    # 1. Start API Server in separate thread
    api_thread = threading.Thread(target=run_uvicorn, daemon=True)
    api_thread.start()

    # 2. Open Browser immediately
    # Give it a slight delay to ensure server started (optional, but 1s is safe)
    def delayed_open():
        time.sleep(2)
        open_dashboard()
    
    threading.Thread(target=delayed_open, daemon=True).start()

    # 3. Create and run System Tray Icon (Blocking in Main Thread)
    try:
        icon_image = create_image(64, 64, 'blue', 'white')
        icon = pystray.Icon("ControlRedCasaPro", icon_image, "Control Red Casa Pro", menu=pystray.Menu(
            pystray.MenuItem("Abrir Dashboard", open_dashboard, default=True),
            pystray.MenuItem("Salir", on_quit)
        ))
        icon.run()
    except Exception as e:
        # Fallback if GUI fails
        with open("crash_gui.txt", "w") as f:
            f.write(f"GUI Error: {e}")
        # If GUI fails, keep main thread alive for API
        while True:
            time.sleep(1)


