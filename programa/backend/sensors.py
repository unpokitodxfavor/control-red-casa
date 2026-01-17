"""
Sistema de sensores para monitoreo de red.
Cada sensor es responsable de recolectar métricas específicas.
"""
import logging
import asyncio
import datetime
from typing import Dict, Any, List
from abc import ABC, abstractmethod
import subprocess
import platform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseSensor(ABC):
    """Clase base para todos los sensores"""
    
    def __init__(self, device_ip: str, config: Dict[str, Any] = None):
        self.device_ip = device_ip
        self.config = config or {}
        self.last_run = None
        self.status = "OK"
        
    @abstractmethod
    async def collect(self) -> Dict[str, float]:
        """
        Recolecta métricas y devuelve un diccionario con los valores.
        Ej: {"latency": 45.3, "packet_loss": 0}
        """
        pass
    
    def get_sensor_type(self) -> str:
        return self.__class__.__name__.replace("Sensor", "").upper()


class PingSensor(BaseSensor):
    """Sensor de ping - mide latencia y packet loss"""
    
    async def collect(self) -> Dict[str, float]:
        """Ping al dispositivo y recolecta métricas"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            count = self.config.get('ping_count', 4)
            
            # Ejecutar ping
            command = ['ping', param, str(count), self.device_ip]
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                text=True
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                
                # Parse latency
                latency = None
                if 'average' in output:
                    # Windows format
                    for line in output.split('\n'):
                        if 'average' in line:
                            parts = line.split('=')
                            if len(parts) > 1:
                                avg_part = parts[-1].strip().replace('ms', '').strip()
                                try:
                                    latency = float(avg_part)
                                except ValueError:
                                    pass
                elif 'avg' in output:
                    # Linux format: rtt min/avg/max/mdev = X/Y/Z/W ms
                    for line in output.split('\n'):
                        if 'rtt' in line or 'avg' in line:
                            parts = line.split('=')
                            if len(parts) > 1:
                                stats = parts[1].split('/')
                                if len(stats) >= 2:
                                    try:
                                        latency = float(stats[1].strip())
                                    except ValueError:
                                        pass
                
                # Parse packet loss
                packet_loss = 0
                for line in output.split('\n'):
                    if 'loss' in line or 'lost' in line:
                        # Extract percentage
                        if '%' in line:
                            parts = line.split('%')[0].split()
                            for part in reversed(parts):
                                try:
                                    packet_loss = float(part)
                                    break
                                except ValueError:
                                    continue
                
                self.status = "OK"
                return {
                    "ping_latency": latency if latency is not None else 0,
                    "ping_packet_loss": packet_loss
                }
            else:
                self.status = "ERROR"
                return {"ping_latency": 999, "ping_packet_loss": 100}
                
        except Exception as e:
            logger.error(f"Error en PingSensor para {self.device_ip}: {e}")
            self.status = "ERROR"
            return {"ping_latency": 999, "ping_packet_loss": 100}


class PortScanSensor(BaseSensor):
    """Sensor de escaneo de puertos"""
    
    async def collect(self) -> Dict[str, float]:
        """Escanea puertos comunes"""
        try:
            import socket
            
            common_ports = self.config.get('ports', [80, 443, 22, 21, 3389, 8080])
            open_ports = 0
            
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.device_ip, port))
                sock.close()
                
                if result == 0:
                    open_ports += 1
            
            self.status = "OK"
            return {
                "open_ports_count": open_ports,
                "scanned_ports_count": len(common_ports)
            }
            
        except Exception as e:
            logger.error(f"Error en PortScanSensor para {self.device_ip}: {e}")
            self.status = "ERROR"
            return {"open_ports_count": 0, "scanned_ports_count": 0}


class HTTPSensor(BaseSensor):
    """Sensor de disponibilidad HTTP/HTTPS"""
    
    async def collect(self) -> Dict[str, float]:
        """Verifica disponibilidad y tiempo de respuesta HTTP"""
        try:
            import requests
            import time
            
            url = self.config.get('url', f'http://{self.device_ip}')
            
            start = time.time()
            response = requests.get(url, timeout=10, verify=False)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            
            self.status = "OK" if response.status_code == 200 else "WARNING"
            
            return {
                "http_response_time": elapsed,
                "http_status_code": response.status_code,
                "http_available": 1 if response.status_code == 200 else 0
            }
            
        except Exception as e:
            logger.error(f"Error en HTTPSensor para {self.device_ip}: {e}")
            self.status = "ERROR"
            return {
                "http_response_time": 0,
                "http_status_code": 0,
                "http_available": 0
            }


class BandwidthSensor(BaseSensor):
    """Sensor de ancho de banda (requiere integración con router o herramientas específicas)"""
    
    async def collect(self) -> Dict[str, float]:
        """Recolecta estadísticas de ancho de banda"""
        try:
            import psutil
            
            # Nota: Esto da el ancho de banda total del sistema, no por dispositivo
            # Para por dispositivo necesitaríamos integración con el router
            net_io = psutil.net_io_counters()
            
            # Guardar estado anterior para calcular diferencia
            if hasattr(self, '_last_bytes_sent'):
                bytes_sent_diff = net_io.bytes_sent - self._last_bytes_sent
                bytes_recv_diff = net_io.bytes_recv - self._last_bytes_recv
                time_diff = (datetime.datetime.now() - self._last_measurement).total_seconds()
                
                # Calcular Mbps
                upload_mbps = (bytes_sent_diff * 8) / (time_diff * 1_000_000) if time_diff > 0 else 0
                download_mbps = (bytes_recv_diff * 8) / (time_diff * 1_000_000) if time_diff > 0 else 0
            else:
                upload_mbps = 0
                download_mbps = 0
            
            # Guardar estado actual
            self._last_bytes_sent = net_io.bytes_sent
            self._last_bytes_recv = net_io.bytes_recv
            self._last_measurement = datetime.datetime.now()
            
            self.status = "OK"
            return {
                "bandwidth_upload": upload_mbps,
                "bandwidth_download": download_mbps
            }
            
        except Exception as e:
            logger.error(f"Error en BandwidthSensor: {e}")
            self.status = "ERROR"
            return {"bandwidth_upload": 0, "bandwidth_download": 0}


# Factory para crear sensores
SENSOR_TYPES = {
    'PING': PingSensor,
    'PORT': PortScanSensor,
    'HTTP': HTTPSensor,
    'BANDWIDTH': BandwidthSensor
}

def create_sensor(sensor_type: str, device_ip: str, config: Dict = None) -> BaseSensor:
    """Factory para crear sensores"""
    sensor_class = SENSOR_TYPES.get(sensor_type.upper())
    if not sensor_class:
        raise ValueError(f"Tipo de sensor desconocido: {sensor_type}")
    
    return sensor_class(device_ip, config)
