"""
Workers para recolección continua de métricas en background.
"""
import asyncio
import logging
import datetime
from typing import List
from database import SessionLocal, Device, Sensor, MetricHistory
from sensors import create_sensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """Recolector de métricas en background"""
    
    def __init__(self):
        self.running = False
        self.tasks = []
    
    async def collect_device_metrics(self, device_id: int, device_ip: str, sensors: List[Sensor]):
        """Recolecta métricas de todos los sensores de un dispositivo"""
        db = SessionLocal()
        try:
            for sensor in sensors:
                if not sensor.enabled:
                    continue
                
                try:
                    # Crear instancia del sensor
                    sensor_instance = create_sensor(
                        sensor.sensor_type,
                        device_ip,
                        sensor.config or {}
                    )
                    
                    # Recolectar métricas
                    metrics = await sensor_instance.collect()
                    
                    # Guardar en base de datos
                    timestamp = datetime.datetime.utcnow()
                    for metric_name, value in metrics.items():
                        metric = MetricHistory(
                            device_id=device_id,
                            sensor_id=sensor.id,
                            metric_name=metric_name,
                            value=value,
                            unit=self._get_unit(metric_name),
                            timestamp=timestamp
                        )
                        db.add(metric)
                    
                    # Actualizar estado del sensor
                    sensor.last_run = timestamp
                    sensor.status = sensor_instance.status
                    
                    db.commit()
                    logger.info(f"Métricas recolectadas para sensor {sensor.name} (device {device_id})")
                    
                except Exception as e:
                    logger.error(f"Error recolectando métricas de sensor {sensor.id}: {e}")
                    db.rollback()
        finally:
            db.close()
    
    def _get_unit(self, metric_name: str) -> str:
        """Determina la unidad de medida según el nombre de la métrica"""
        units = {
            'latency': 'ms',
            'packet_loss': '%',
            'response_time': 'ms',
            'bandwidth': 'Mbps',
            'upload': 'Mbps',
            'download': 'Mbps',
            'cpu': '%',
            'memory': '%',
            'disk': '%',
            'temperature': '°C',
            'count': '#',
            'status_code': '#',
            'available': 'bool'
        }
        
        for key, unit in units.items():
            if key in metric_name.lower():
                return unit
        
        return ''
    
    async def run_collection_loop(self):
        """Loop principal de recolección"""
        logger.info("Iniciando loop de recolección de métricas...")
        
        while self.running:
            db = SessionLocal()
            try:
                # Obtener todos los dispositivos online con sensores activos
                devices = db.query(Device).filter(Device.status == "Online").all()
                
                for device in devices:
                    # Obtener sensores activos del dispositivo
                    sensors = db.query(Sensor).filter(
                        Sensor.device_id == device.id,
                        Sensor.enabled == True
                    ).all()
                    
                    if sensors:
                        # Crear tarea asíncrona para recolectar métricas
                        asyncio.create_task(
                            self.collect_device_metrics(device.id, device.ip, sensors)
                        )
                
            except Exception as e:
                logger.error(f"Error en loop de recolección: {e}")
            finally:
                db.close()
            
            # Esperar antes del próximo ciclo (60 segundos por defecto)
            await asyncio.sleep(60)
    
    async def start(self):
        """Inicia el recolector"""
        self.running = True
        await self.run_collection_loop()
    
    async def stop(self):
        """Para el recolector"""
        self.running = False


# Función helper para auto-crear sensores de ping para todos los dispositivos
def auto_create_ping_sensors():
    """Crea sensores de ping para dispositivos que no los tienen"""
    db = SessionLocal()
    try:
        devices = db.query(Device).all()
        
        for device in devices:
            # Verificar si ya tiene sensor de ping
            existing = db.query(Sensor).filter(
                Sensor.device_id == device.id,
                Sensor.sensor_type == "PING"
            ).first()
            
            if not existing:
                ping_sensor = Sensor(
                    device_id=device.id,
                    name=f"Ping - {device.hostname or device.ip}",
                    sensor_type="PING",
                    config={"ping_count": 4},
                    interval=60,
                    enabled=True
                )
                db.add(ping_sensor)
                logger.info(f"Sensor de ping creado para {device.hostname or device.ip}")
        
        db.commit()
        logger.info("Auto-creación de sensores de ping completada")
        
    except Exception as e:
        logger.error(f"Error en auto_create_ping_sensors: {e}")
        db.rollback()
    finally:
        db.close()
