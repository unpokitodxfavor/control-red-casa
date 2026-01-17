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
        """Ping al dispositivo y recolecta métricas (Non-blocking)"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            count = self.config.get('ping_count', 4)
            
            # Ejecutar ping asíncrono
            process = await asyncio.create_subprocess_exec(
                'ping', param, str(count), self.device_ip,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                # Wait with timeout
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10.0)
                stdout = stdout.decode('utf-8', errors='ignore').lower()
            except asyncio.TimeoutError:
                process.kill()
                raise Exception("Ping timed out")
            
            if process.returncode == 0:
                # Parse latency
                latency = None
                if 'average' in stdout: # Windows
                    for line in stdout.split('\r\n'):
                        if 'average' in line:
                            parts = line.split('=')
                            if len(parts) > 1:
                                try:
                                    latency = float(parts[-1].strip().replace('ms', '').strip())
                                except: pass
                elif 'avg' in stdout: # Linux
                    for line in stdout.split('\n'):
                        if 'rtt' in line or 'avg' in line:
                            try:
                                latency = float(line.split('=')[1].split('/')[1])
                            except: pass
                
                # Parse packet loss
                packet_loss = 0
                for line in stdout.split('\r\n'):
                    if 'loss' in line or 'lost' in line:
                        if '%' in line:
                            parts = line.split('%')[0].split()
                            try:
                                packet_loss = float(parts[-1])
                            except: pass

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
        """Escanea puertos comunes (Non-blocking)"""
        try:
            import socket
            loop = asyncio.get_event_loop()
            
            common_ports = self.config.get('ports', [80, 443, 22, 21, 3389, 8080])
            open_ports = 0
            
            def check_port(ip, port):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                return result == 0

            # Ejecutar checks en paralelo/executor
            futures = [
                loop.run_in_executor(None, check_port, self.device_ip, port)
                for port in common_ports
            ]
            
            results = await asyncio.gather(*futures)
            open_ports = sum(results)
            
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
        """Verifica disponibilidad (Non-blocking)"""
        try:
            import requests
            import time
            loop = asyncio.get_event_loop()
            
            url = self.config.get('url', f'http://{self.device_ip}')
            
            def check_http():
                start = time.time()
                try:
                    resp = requests.get(url, timeout=10, verify=False)
                    elapsed = (time.time() - start) * 1000
                    return elapsed, resp.status_code, 1 if resp.status_code == 200 else 0
                except:
                    return 0, 0, 0
            
            elapsed, status, available = await loop.run_in_executor(None, check_http)
            
            self.status = "OK" if status == 200 else "WARNING"
            return {
                "http_response_time": elapsed,
                "http_status_code": status,
                "http_available": available
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
    """Sensor de ancho de banda (System-wide)"""
    
    async def collect(self) -> Dict[str, float]:
        """Recolecta estadísticas de ancho de banda (Non-blocking call to psutil)"""
        try:
            import psutil
            import time
            loop = asyncio.get_event_loop()
            
            # psutil is fast but let's wrap just in case
            net_io = await loop.run_in_executor(None, psutil.net_io_counters)
            
            if hasattr(self, '_last_bytes_sent'):
                bytes_sent_diff = net_io.bytes_sent - self._last_bytes_sent
                bytes_recv_diff = net_io.bytes_recv - self._last_bytes_recv
                time_diff = (datetime.datetime.now() - self._last_measurement).total_seconds()
                
                upload_mbps = (bytes_sent_diff * 8) / (time_diff * 1_000_000) if time_diff > 0 else 0
                download_mbps = (bytes_recv_diff * 8) / (time_diff * 1_000_000) if time_diff > 0 else 0
            else:
                upload_mbps = 0
                download_mbps = 0
            
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
