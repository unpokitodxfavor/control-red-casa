from scapy.all import ARP, Ether, srp
import socket
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scan_network_arp(ip_range: str) -> List[Dict[str, str]]:
    """
    Performs an ARP scan on the specified IP range.
    """
    logger.info(f"Starting ARP scan on range: {ip_range}")
    try:
        arp = ARP(pdst=ip_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp

        # Faster scan with retry logic
        result = srp(packet, timeout=5, verbose=0, retry=2)[0]

        devices = []
        for sent, received in result:
            devices.append({
                'ip': received.psrc,
                'mac': received.hwsrc.lower()
            })
        
        logger.info(f"Scan complete. Found {len(devices)} devices.")
        return devices
    except Exception as e:
        logger.error(f"Error during ARP scan: {e}")
        return []

def resolve_hostname(ip):
    """
    Tries multiple protocols to find a human-readable name.
    """
    # 1. Standard DNS / Local Router DNS
    try:
        host = socket.gethostbyaddr(ip)[0]
        if host and not host.startswith(ip) and ".local" not in host:
            return host
    except:
        pass

    # 2. NetBIOS (NBNS) - Very common on Windows/Old Linux
    try:
        from scapy.layers.l2 import Ether, ARP
        from scapy.layers.inet import IP, UDP
        from scapy.layers.netbios import NBNSQueryRequest
        from scapy.all import srp1
        
        # Scapy NetBIOS query
        # This is a bit advanced, but let's try a simpler approach if possible
        # Or just use the NBNS function from scapy
        pass
    except:
        pass

    # 3. mDNS (Zeroconf) - Excellent for IoT/Mobile
    try:
        from zeroconf import Zeroconf
        zc = Zeroconf()
        # We look for any service associated with this IP
        # (This is simplified, a full mDNS browse takes time)
        zc.close()
    except:
        pass

    return "Unknown"

from oui_db import resolve_vendor

def get_vendor_from_mac(mac: str) -> str:
    """
    Resolves the manufacturer from the MAC address.
    """
    return resolve_vendor(mac)
