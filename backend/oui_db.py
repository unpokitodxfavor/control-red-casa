import os
import re
import requests
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fallback minimal OUI map for critical vendors
FALLBACK_OUI_MAP = {
    # Google / Nest / Chromecast
    "44:09:b8": "Google", "e8:b0:c5": "Google", "b0:05:94": "Google", "c4:8b:66": "Google",
    "f8:0f:f9": "Google", "60:45:cb": "Google", "00:1a:11": "Google", "d8:16:14": "Google",
    "f0:ef:86": "Google",

    # TP-Link
    "d4:5d:64": "TP-Link", "e8:4e:06": "TP-Link", "10:27:f5": "TP-Link", "7c:61:66": "TP-Link",
    "10:d5:61": "TP-Link", "50:c7:bf": "TP-Link", "f4:f2:6d": "TP-Link", "d8:07:37": "TP-Link",
    "00:21:2f": "TP-Link", "7c:f6:66": "TP-Link", "48:e1:e9": "TP-Link", "10:27:f5": "TP-Link",

    # Apple
    "00:00:0c": "Cisco", "00:03:93": "Apple", "00:05:02": "Apple", "28:cf:e9": "Apple", 
    "d0:03:4b": "Apple", "f8:ff:c2": "Apple",

    # Amazon / Echo
    "08:84:9d": "Amazon", "fc:a6:67": "Amazon", "00:bb:3a": "Amazon",

    # Samsung
    "3c:5a:37": "Samsung", "b2:5f:2f": "Samsung", "46:24:98": "Samsung", "00:07:ab": "Samsung",
    "b2:5f:2f": "Samsung",

    # Sony
    "70:9e:29": "Sony", "00:1d:ba": "Sony",

    # Asus
    "ac:ed:5c": "Asus", "b0:6e:bf": "Asus", "38:d5:47": "Asus", "24:4b:fe": "Asus",
    "00:e0:18": "Asus", "88:d7:f6": "Asus", "d0:17:c2": "Asus", "04:d9:f5": "Asus",
    "00:11:32": "Synology", "b8:27:eb": "Raspberry Pi", "00:e0:4c": "Realtek",
    
    # Shenzhen (común en IoT)
    "80:9f:9b": "Shenzhen Jiawei Technology", "a8:10:87": "Shenzhen Jiawei Technology"
}

# Cache OUI completo en memoria
OUI_DATABASE = {}
OUI_FILE_PATH = Path(__file__).parent / "oui.txt"

def download_oui_database():
    """
    Descarga la base de datos OUI oficial de IEEE.
    """
    logger.info("Descargando base de datos OUI de IEEE...")
    try:
        url = "https://standards-oui.ieee.org/oui/oui.txt"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(OUI_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        logger.info(f"Base de datos OUI descargada exitosamente: {OUI_FILE_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error descargando base de datos OUI: {e}")
        return False

def load_oui_database():
    """
    Carga la base de datos OUI desde el archivo local.
    Formato del archivo:
    00-00-0C   (hex)    Cisco Systems, Inc
    00000C     (base 16) Cisco Systems, Inc
    """
    global OUI_DATABASE
    
    if not OUI_FILE_PATH.exists():
        logger.warning("Archivo OUI no encontrado. Intentando descargar...")
        if not download_oui_database():
            logger.warning("No se pudo descargar. Usando fallback.")
            OUI_DATABASE = FALLBACK_OUI_MAP.copy()
            return
    
    try:
        with open(OUI_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Buscar líneas con formato: 00-00-0C   (hex)    Cisco Systems, Inc
                match = re.match(r'^([0-9A-F]{2})-([0-9A-F]{2})-([0-9A-F]{2})\s+\(hex\)\s+(.+)$', line.strip())
                if match:
                    prefix = f"{match.group(1).lower()}:{match.group(2).lower()}:{match.group(3).lower()}"
                    vendor = match.group(4).strip()
                    OUI_DATABASE[prefix] = vendor
        
        logger.info(f"Base de datos OUI cargada: {len(OUI_DATABASE)} fabricantes")
    except Exception as e:
        logger.error(f"Error cargando base de datos OUI: {e}")
        OUI_DATABASE = FALLBACK_OUI_MAP.copy()

def query_online_api(mac: str) -> str:
    """
    Consulta una API online como respaldo.
    """
    try:
        mac_clean = mac.replace(":", "").replace("-", "")[:6]
        url = f"https://api.macvendors.com/{mac_clean}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    return None

def resolve_vendor(mac: str) -> str:
    """
    Resuelve el fabricante desde la dirección MAC.
    1. Intenta con base de datos local
    2. Intenta con API online
    3. Devuelve "Unknown Vendor"
    """
    if not OUI_DATABASE:
        load_oui_database()
    
    # Normalizar MAC a formato xx:xx:xx
    prefix = mac.lower()[:8].replace("-", ":")
    
    # 1. Búsqueda en base de datos local
    vendor = OUI_DATABASE.get(prefix)
    if vendor:
        return vendor
    
    # 2. Búsqueda en fallback
    vendor = FALLBACK_OUI_MAP.get(prefix)
    if vendor:
        return vendor
    
    # 3. Intentar con API online (solo si no está en cache)
    vendor = query_online_api(mac)
    if vendor:
        # Guardar en cache para futuras consultas
        OUI_DATABASE[prefix] = vendor
        return vendor
    
    return "Unknown Vendor"

# Cargar la base de datos al importar el módulo
load_oui_database()
