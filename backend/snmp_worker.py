import asyncio
import time
import subprocess
import re
from pysnmp.hlapi.asyncio import *

class SNMPWorker:
    def __init__(self, ip="auto", community="public", interval=5):
        self.ip = ip
        self.community = community
        self.interval = interval
        self.running = False
        self.metrics = {
            "uptime": 0,
            "traffic_in": 0,
            "traffic_out": 0,
            "cpu_load": 0,
            "ram_usage": 0,
            "last_updated": 0,
            "ip_used": "Pending"
        }
        self._prev_traffic = {"in": 0, "out": 0, "time": 0}

    def detect_gateway(self):
        try:
            # Try Windows route command
            output = subprocess.check_output("route print 0.0.0.0", shell=True).decode()
            for line in output.split("\n"):
                if "0.0.0.0" in line and "0.0.0.0" in line:
                    parts = line.split()
                    for part in parts:
                        # Simple regex for IP
                        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", part):
                             if part != "0.0.0.0" and not part.startswith("127"):
                                 print(f"[SNMP] Detected Gateway: {part}")
                                 return part
        except Exception as e:
            print(f"[SNMP] Gateway detection failed: {e}")
        
        return "192.168.1.1" # Fallback

    async def get_oid(self, oid_str):
        target_ip = self.ip
        if target_ip == "auto" or target_ip == "192.168.1.1": # Force detect if default
             target_ip = self.detect_gateway()
             self.ip = target_ip # Cache it
             self.metrics["ip_used"] = target_ip

        try:
            errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                SnmpEngine(),
                CommunityData(self.community, mpModel=1), # v2c
                UdpTransportTarget((target_ip, 161), timeout=1, retries=1),
                ContextData(),
                ObjectType(ObjectIdentity(oid_str))
            )

            if errorIndication:
                print(f"SNMP Error: {errorIndication}")
                return None
            elif errorStatus:
                print(f"SNMP Error Status: {errorStatus}")
                return None
            else:
                for varBind in varBinds:
                    return varBind[1]
        except Exception as e:
            print(f"SNMP Exception {oid_str}: {e}")
            return None

    async def poll(self):
        # OIDs Standard (RFC1213)
        # sysUpTime: .1.3.6.1.2.1.1.3.0
        # ifInOctets (Wan usually index 2 or 5? Asus often uses vlan or eth0): .1.3.6.1.2.1.2.2.1.10.X
        # ifOutOctets: .1.3.6.1.2.1.2.2.1.16.X
        
        # NOTE: Finding the correct interface index (IF-MIB) is tricky without walking.
        # For Asus RT-AC65P, WAN is often eth0 (index 2?).
        # We will try to fetch multiple and see which one has traffic, or default to a common one.
        
        # Let's try index 2 (often eth0/WAN on residential routers)
        if_index = 2 
        
        uptime_val = await self.get_oid('1.3.6.1.2.1.1.3.0')
        in_bytes = await self.get_oid(f'1.3.6.1.2.1.2.2.1.10.{if_index}')
        out_bytes = await self.get_oid(f'1.3.6.1.2.1.2.2.1.16.{if_index}')
        
        # ASUS Specific for CPU/RAM (Might vary, usually Linux MIB .1.3.6.1.4.1.2021...)
        # CPU 1 min load: .1.3.6.1.4.1.2021.10.1.3.1
        # Mem Total: .1.3.6.1.4.1.2021.4.5.0
        # Mem Avail: .1.3.6.1.4.1.2021.4.6.0
        
        load_1min = await self.get_oid('1.3.6.1.4.1.2021.10.1.3.1')
        mem_total = await self.get_oid('1.3.6.1.4.1.2021.4.5.0')
        mem_avail = await self.get_oid('1.3.6.1.4.1.2021.4.6.0')

        now = time.time()
        
        # Calculate rates
        if in_bytes and out_bytes:
            current_in = int(in_bytes)
            current_out = int(out_bytes)
            
            if self._prev_traffic["time"] > 0:
                dt = now - self._prev_traffic["time"]
                if dt > 0:
                    speed_in = (current_in - self._prev_traffic["in"]) * 8 / dt # bits per second
                    speed_out = (current_out - self._prev_traffic["out"]) * 8 / dt
                    
                    self.metrics["traffic_in"] = max(0, round(speed_in, 2))
                    self.metrics["traffic_out"] = max(0, round(speed_out, 2))

            self._prev_traffic = {"in": current_in, "out": current_out, "time": now}

        if uptime_val:
            self.metrics["uptime"] = int(uptime_val) / 100 # timeticks to seconds
            
        if load_1min:
             self.metrics["cpu_load"] = float(load_1min)
             
        if mem_total and mem_avail:
            total = int(mem_total)
            avail = int(mem_avail)
            used = total - avail
            percent = (used / total) * 100 if total > 0 else 0
            self.metrics["ram_usage"] = round(percent, 1)

        self.metrics["last_updated"] = now

    async def start(self):
        self.running = True
        print(f"Iniciando SNMP Worker para {self.ip}...")
        while self.running:
            await self.poll()
            await asyncio.sleep(self.interval)

    def stop(self):
        self.running = False
