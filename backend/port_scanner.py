"""
port_scanner.py - Escáner de puertos para dispositivos de red
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# Puertos comunes y sus servicios
COMMON_PORTS = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "HTTP Proxy",
    8443: "HTTPS Alt",
    27017: "MongoDB"
}

def scan_port(ip: str, port: int, timeout: float = 1.0) -> Tuple[int, bool, str]:
    """
    Escanea un puerto específico en una IP
    
    Args:
        ip: Dirección IP a escanear
        port: Puerto a escanear
        timeout: Timeout en segundos
        
    Returns:
        Tupla (puerto, está_abierto, servicio)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        is_open = (result == 0)
        service = COMMON_PORTS.get(port, "Unknown")
        
        return (port, is_open, service)
    except socket.error as e:
        logger.debug(f"Error scanning {ip}:{port} - {e}")
        return (port, False, "Error")
    except Exception as e:
        logger.error(f"Unexpected error scanning {ip}:{port} - {e}")
        return (port, False, "Error")

def scan_ports_range(ip: str, start_port: int, end_port: int, timeout: float = 1.0, max_workers: int = 50) -> List[Dict]:
    """
    Escanea un rango de puertos en una IP
    
    Args:
        ip: Dirección IP a escanear
        start_port: Puerto inicial
        end_port: Puerto final
        timeout: Timeout por puerto
        max_workers: Número máximo de threads concurrentes
        
    Returns:
        Lista de diccionarios con información de puertos abiertos
    """
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scan_port, ip, port, timeout): port 
            for port in range(start_port, end_port + 1)
        }
        
        for future in as_completed(futures):
            port, is_open, service = future.result()
            if is_open:
                open_ports.append({
                    'port': port,
                    'service': service,
                    'state': 'open'
                })
                logger.info(f"Port {port} is open on {ip} ({service})")
    
    return sorted(open_ports, key=lambda x: x['port'])

def scan_common_ports(ip: str, timeout: float = 1.0) -> List[Dict]:
    """
    Escanea solo los puertos comunes en una IP
    
    Args:
        ip: Dirección IP a escanear
        timeout: Timeout por puerto
        
    Returns:
        Lista de diccionarios con información de puertos abiertos
    """
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(scan_port, ip, port, timeout): port 
            for port in COMMON_PORTS.keys()
        }
        
        for future in as_completed(futures):
            port, is_open, service = future.result()
            if is_open:
                open_ports.append({
                    'port': port,
                    'service': service,
                    'state': 'open'
                })
                logger.info(f"Port {port} is open on {ip} ({service})")
    
    return sorted(open_ports, key=lambda x: x['port'])

def scan_custom_ports(ip: str, ports: List[int], timeout: float = 1.0) -> List[Dict]:
    """
    Escanea puertos personalizados en una IP
    
    Args:
        ip: Dirección IP a escanear
        ports: Lista de puertos a escanear
        timeout: Timeout por puerto
        
    Returns:
        Lista de diccionarios con información de puertos abiertos
    """
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=min(len(ports), 50)) as executor:
        futures = {
            executor.submit(scan_port, ip, port, timeout): port 
            for port in ports
        }
        
        for future in as_completed(futures):
            port, is_open, service = future.result()
            if is_open:
                open_ports.append({
                    'port': port,
                    'service': service,
                    'state': 'open'
                })
                logger.info(f"Port {port} is open on {ip} ({service})")
    
    return sorted(open_ports, key=lambda x: x['port'])

def scan_multiple_ips(ips: List[str], scan_type: str = 'common', 
                     custom_ports: List[int] = None, 
                     port_range: Tuple[int, int] = None,
                     timeout: float = 1.0) -> Dict[str, List[Dict]]:
    """
    Escanea múltiples IPs
    
    Args:
        ips: Lista de IPs a escanear
        scan_type: 'common', 'range', o 'custom'
        custom_ports: Lista de puertos personalizados (si scan_type='custom')
        port_range: Tupla (inicio, fin) de rango de puertos (si scan_type='range')
        timeout: Timeout por puerto
        
    Returns:
        Diccionario {ip: [puertos_abiertos]}
    """
    results = {}
    
    for ip in ips:
        logger.info(f"Scanning {ip}...")
        
        if scan_type == 'common':
            results[ip] = scan_common_ports(ip, timeout)
        elif scan_type == 'range' and port_range:
            results[ip] = scan_ports_range(ip, port_range[0], port_range[1], timeout)
        elif scan_type == 'custom' and custom_ports:
            results[ip] = scan_custom_ports(ip, custom_ports, timeout)
        else:
            results[ip] = []
            
    return results
