
import asyncio
import subprocess
import re
import sys
from pysnmp.hlapi.asyncio import *

async def get_oid(ip, oid, community='public'):
    print(f"   Querying {oid} on {ip}...")
    try:
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1), # v2c
            UdpTransportTarget((ip, 161), timeout=2, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        if errorIndication:
            return f"ERROR: {errorIndication}"
        elif errorStatus:
            return f"ERROR: {errorStatus.prettyPrint()}"
        else:
            return varBinds[0][1].prettyPrint()
    except Exception as e:
        return f"EXCEPTION: {e}"

def detect_gateway():
    print("   [1/3] Detecting Gateway via 'route print'...")
    try:
        output = subprocess.check_output("route print 0.0.0.0", shell=True).decode()
        for line in output.split("\n"):
            if "0.0.0.0" in line and "0.0.0.0" in line:
                parts = line.split()
                # Windows route print: Dest Mask Gateway Interface
                # We want the Gateway column (usually index 2)
                # But let's find the first IP that isn't 0.0.0.0
                candidates = []
                for part in parts:
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", part):
                        candidates.append(part)
                
                # Usually: 0.0.0.0 0.0.0.0 GATEWAY INTERFACE
                if len(candidates) >= 4:
                     gw = candidates[2]
                     if gw != "0.0.0.0":
                         return gw
                # Fallback heuristic
                for c in candidates:
                    if c != "0.0.0.0" and not c.startswith("127") and not c.startswith("10.0.0.0"):
                         return c
    except Exception as e:
        print(f"   Error detecting: {e}")
    return None

async def main():
    print("\n=== DIAGNOSTICO DE ROUTER ASUS ===")
    
    # 1. IP
    ip = detect_gateway()
    if not ip:
        print("   [ERROR] Could not detect gateway automatically.")
        ip = input("   Please enter Router IP manually (e.g. 192.168.50.1): ").strip()
    else:
        print(f"   [OK] Gateway Detected: {ip}")

    # 2. Connection Test (Uptime)
    print("\n=== TEST 1: CONEXION BASICA (Uptime) ===")
    uptime_oid = '1.3.6.1.2.1.1.3.0'
    res = await get_oid(ip, uptime_oid)
    print(f"   RESULT: {res}")
    
    if "ERROR" in str(res) or "EXCEPTION" in str(res):
        print("\n   [FATAL] No se pudo conectar con el router.")
        print("   Posibles causas:")
        print("   1. SNMP no esta activado en el router.")
        print("   2. La comunidad no es 'public'.")
        print("   3. El firewall del router bloquea la conexion.")
        return

    # 3. Model Info
    print("\n=== TEST 2: INFORMACION DEL SISTEMA ===")
    descr = await get_oid(ip, '1.3.6.1.2.1.1.1.0')
    print(f"   SYSTEM: {descr}")

    # 4. Traffic Interfaces
    print("\n=== TEST 3: INTERFACES DE RED ===")
    # Look for eth0 or vlan1 usually logic for WAN
    # Just try a few indexes
    for i in range(1, 10):
        name = await get_oid(ip, f'1.3.6.1.2.1.2.2.1.2.{i}')
        if "ERROR" not in str(name) and name != "No Such Instance currently exists at this OID":
            desc = await get_oid(ip, f'1.3.6.1.2.1.2.2.1.2.{i}')
            bytes_in = await get_oid(ip, f'1.3.6.1.2.1.2.2.1.10.{i}')
            print(f"   Interface {i}: {desc} -> InBytes: {bytes_in}")

    print("\n=== DIAGNOSTICO FINALIZADO ===")

if __name__ == "__main__":
    asyncio.run(main())
