"""
Script de diagnóstico para identificar problemas de detección de red
"""
import psutil
import socket
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

print("=" * 60)
print("[DIAGNOSTICO DE RED - Control Red Casa]")
print("=" * 60)
print()

# 1. Verificar permisos
print("[1] VERIFICACION DE PERMISOS")
print("-" * 60)
if is_admin():
    print("[OK] Ejecutandose como ADMINISTRADOR")
else:
    print("[ERROR] NO tiene permisos de administrador")
    print("   [WARN] SCAPY FALLARA sin permisos")
    print("   Solucion: Ejecutar como administrador")
print()

# 2. Listar todas las interfaces
print("[2] INTERFACES DE RED DETECTADAS")
print("-" * 60)
addrs = psutil.net_if_addrs()
stats = psutil.net_if_stats()

for iface_name, iface_addrs in addrs.items():
    # Estado
    is_up = stats[iface_name].isup if iface_name in stats else False
    status = "[UP]" if is_up else "[DOWN]"
    
    print(f"\n[Interface] {iface_name}")
    print(f"   Estado: {status}")
    
    # Direcciones
    for addr in iface_addrs:
        if addr.family == socket.AF_INET:  # IPv4
            ip = addr.address
            mask = addr.netmask
            
            # Filtros que usa el código
            is_loopback = ip.startswith("127.")
            is_docker = "172." in ip or "169.254" in ip
            is_virtual = any(x in iface_name for x in ["vEthernet", "WSL", "Docker", "VMware", "VirtualBox"])
            
            print(f"   IPv4: {ip}")
            print(f"   Máscara: {mask}")
            
            # Calcular red
            if mask == "255.255.255.0":
                network = ".".join(ip.split(".")[:-1]) + ".0/24"
                print(f"   Red: {network}")
            
            # Filtros aplicados
            warnings = []
            if is_loopback:
                warnings.append("[WARN] Loopback (excluida)")
            if is_docker:
                warnings.append("[WARN] IP Docker/AutoIP (puede ser excluida)")
            if is_virtual:
                warnings.append("[WARN] Interfaz virtual (puede ser excluida)")
            
            if warnings:
                for w in warnings:
                    print(f"   {w}")
            else:
                print(f"   [OK] CANDIDATA VALIDA")

print()
print("[3] DETECCION AUTOMATICA (Mismo codigo que main.py)")
print("-" * 60)

# Copiar exactamente el código de get_local_network()
try:
    ifaces = sorted(addrs.keys(), key=lambda x: (
        not ("vEthernet" in x or "WSL" in x or "Docker" in x or "VMware" in x or "VirtualBox" in x),
        stats[x].isup if x in stats else False
    ), reverse=True)

    detected_network = None
    
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
                detected_network = base_ip
                print(f"[OK] RED DETECTADA: {base_ip}")
                print(f"   Interface: {iface}")
                print(f"   IP local: {ip}")
                break
        
        if detected_network:
            break
    
    if not detected_network:
        print("[WARN] No se detecto red automaticamente")
        print("   Usando fallback: 192.168.1.0/24")
        detected_network = "192.168.1.0/24"

except Exception as e:
    print(f"[ERROR] ERROR en deteccion: {e}")
    detected_network = "192.168.1.0/24"

print()
print("[4] VERIFICACION DE SCAPY")
print("-" * 60)
try:
    from scapy.all import ARP, Ether, srp
    print("[OK] Scapy instalado correctamente")
    
    if not is_admin():
        print("[WARN] Sin permisos de admin, el escaneo puede fallar")
    
except ImportError as e:
    print(f"[ERROR] Scapy NO esta instalado: {e}")
    print("   Solucion: pip install scapy")
except Exception as e:
    print(f"[ERROR] Error importando Scapy: {e}")

print()
print("[5] VERIFICACION DE NPCAP/WINPCAP")
print("-" * 60)
try:
    from scapy.all import conf
    if conf.use_pcap:
        print("[OK] Usando Npcap/WinPcap")
    else:
        print("[WARN] No se detecto Npcap/WinPcap")
        print("   Puede causar problemas en Windows")
        print("   Descargar: https://npcap.com")
except:
    print("[WARN] No se pudo verificar")

print()
print("[6] RECOMENDACIONES")
print("-" * 60)

issues = []
if not is_admin():
    issues.append("Ejecutar como ADMINISTRADOR")
if detected_network != "192.168.50.0/24":
    issues.append(f"La red detectada ({detected_network}) puede no ser correcta")
    issues.append(f"Tu IP es 192.168.50.109, debería ser 192.168.50.0/24")

if issues:
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
else:
    print("[OK] Todo parece correcto")

print()
print("=" * 60)
print("FIN DEL DIAGNÓSTICO")
print("=" * 60)
