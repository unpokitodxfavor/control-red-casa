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
from alerts import AlertManager, AlertLevel, AlertChannel, AlertCondition

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
    global metrics_collector, alert_manager
    
    init_db()
    start_mdns_listener()

    if not is_admin():
        logger.warning("!!! LA APLICACION NO ESTA CORRIENDO COMO ADMINISTRADOR !!!")
        logger.warning("El escaneo ARP de Scapy probablemente fallará.")
    
    # Auto-crear sensores de ping en background
    # (Lo ejecutamos en un hilo aparte para que no bloquee el inicio de la API)
    threading.Thread(target=auto_create_ping_sensors, daemon=True).start()
    
    # Initialize Alert Manager
    db = SessionLocal()
    alert_manager = AlertManager(db, ALERT_CONFIG)
    alert_manager.load_rules()
    logger.info("✅ Alert Manager initialized")
    
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
                        scan_time=dt.utcnow()
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
# ENDPOINTS DE ALERTAS
# ============================================

@app.get("/alerts")
def get_alerts(
    level: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene lista de alertas"""
    query = db.query(Alert)
    
    if level:
        query = query.filter(Alert.level == level.upper())
    
    if acknowledged is not None:
        query = query.filter(Alert.is_acknowledged == acknowledged)
    
    alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
    
    return {
        "alerts": [
            {
                "id": a.id,
                "level": a.level,
                "condition": a.condition,
                "message": a.message,
                "device_id": a.device_id,
                "device_name": a.device_name,
                "device_ip": a.device_ip,
                "metadata": a.alert_metadata,
                "timestamp": a.timestamp.isoformat(),
                "is_acknowledged": a.is_acknowledged,
                "acknowledged_by": a.acknowledged_by,
                "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None
            }
            for a in alerts
        ],
        "total": len(alerts)
    }

@app.get("/alerts/active")
def get_active_alerts(
    level: Optional[str] = None
):
    """Obtiene alertas activas (no reconocidas) del AlertManager"""
    if not alert_manager:
        return {"alerts": [], "total": 0}
    
    level_enum = None
    if level:
        try:
            level_enum = AlertLevel(level.lower())
        except ValueError:
            pass
    
    alerts = alert_manager.get_active_alerts(level=level_enum)
    
    return {
        "alerts": alerts,
        "total": len(alerts)
    }

@app.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    user: str = "system",
    db: Session = Depends(get_db)
):
    """Marca una alerta como reconocida"""
    # Actualizar en base de datos
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_acknowledged = True
        alert.acknowledged_by = user
        alert.acknowledged_at = datetime.datetime.utcnow()
        db.commit()
    
    # Actualizar en AlertManager
    if alert_manager:
        alert_manager.acknowledge_alert(alert_id, user)
    
    return {"status": "success", "alert_id": alert_id}

@app.get("/alerts/rules")
def get_alert_rules(db: Session = Depends(get_db)):
    """Obtiene lista de reglas de alertas"""
    rules = db.query(AlertRule).all()
    
    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "enabled": r.enabled,
                "device_id": r.device_id,
                "condition": r.condition,
                "level": r.level,
                "channels": r.channels,
                "threshold": r.threshold,
                "throttle_minutes": r.throttle_minutes,
                "escalate_after_minutes": r.escalate_after_minutes,
                "last_triggered": r.last_triggered.isoformat() if r.last_triggered else None,
                "created_at": r.created_at.isoformat()
            }
            for r in rules
        ],
        "total": len(rules)
    }

class AlertRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    enabled: bool = True
    device_id: Optional[int] = None
    condition: str
    level: str = "WARNING"
    channels: List[str] = ["in_app"]
    threshold: Optional[float] = None
    throttle_minutes: int = 5
    escalate_after_minutes: Optional[int] = None

@app.post("/alerts/rules")
def create_alert_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """Crea una nueva regla de alerta"""
    db_rule = AlertRule(
        name=rule.name,
        description=rule.description,
        enabled=rule.enabled,
        device_id=rule.device_id,
        condition=rule.condition,
        level=rule.level,
        channels=rule.channels,
        threshold=rule.threshold,
        throttle_minutes=rule.throttle_minutes,
        escalate_after_minutes=rule.escalate_after_minutes
    )
    
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    # Recargar reglas en AlertManager
    if alert_manager:
        alert_manager.load_rules()
    
    return {"status": "success", "rule_id": db_rule.id}

@app.put("/alerts/rules/{rule_id}")
def update_alert_rule(
    rule_id: int,
    rule: AlertRuleCreate,
    db: Session = Depends(get_db)
):
    """Actualiza una regla de alerta"""
    db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    
    if not db_rule:
        return {"status": "error", "message": "Rule not found"}
    
    db_rule.name = rule.name
    db_rule.description = rule.description
    db_rule.enabled = rule.enabled
    db_rule.device_id = rule.device_id
    db_rule.condition = rule.condition
    db_rule.level = rule.level
    db_rule.channels = rule.channels
    db_rule.threshold = rule.threshold
    db_rule.throttle_minutes = rule.throttle_minutes
    db_rule.escalate_after_minutes = rule.escalate_after_minutes
    
    db.commit()
    
    # Recargar reglas en AlertManager
    if alert_manager:
        alert_manager.load_rules()
    
    return {"status": "success", "rule_id": rule_id}

@app.delete("/alerts/rules/{rule_id}")
def delete_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    """Elimina una regla de alerta"""
    db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    
    if not db_rule:
        return {"status": "error", "message": "Rule not found"}
    
    db.delete(db_rule)
    db.commit()
    
    # Recargar reglas en AlertManager
    if alert_manager:
        alert_manager.load_rules()
    
    return {"status": "success", "rule_id": rule_id}

class TestAlertRequest(BaseModel):
    level: str = "INFO"
    message: str = "Test alert"
    channels: List[str] = ["in_app"]

@app.post("/alerts/test")
def test_alert(request: TestAlertRequest):
    """Envía una alerta de prueba y la guarda en BD"""
    if not alert_manager:
        return {"status": "error", "message": "Alert manager not initialized"}
        
    db = SessionLocal()
    try:
        # 1. Guardar en Base de Datos (Persistencia)
        db_alert = Alert(
            level=request.level.upper(),
            condition="NEW_DEVICE", # Condición genérica para tests
            message=request.message,
            device_name="Test Device",
            device_ip="192.168.1.999",
            alert_metadata={"is_test": True}
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        
        # 2. Enviar Notificación (AlertManager)
        from alerts import Alert as AlertClass
        
        # Convertir DB Alert a Python Alert para el manager
        py_alert = AlertClass(
            level=AlertLevel(request.level.lower()),
            condition=AlertCondition.NEW_DEVICE,
            message=request.message,
            device_name="Test Device",
            device_ip="192.168.1.999",
            alert_metadata={"is_test": True}
        )
        py_alert.id = db_alert.id # Vincular ID
        
        # Enviar por canales especificados
        channels = [AlertChannel(ch) for ch in request.channels]
        alert_manager.send_notification(py_alert, channels)
        
        return {
            "status": "success",
            "message": "Test alert sent and saved",
            "alert_id": db_alert.id,
            "channels": request.channels
        }
    except Exception as e:
        logger.error(f"Error sending test alert: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

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
