from database import SessionLocal, Device
import os

print(f"Current Working Directory: {os.getcwd()}")
print(f"DB File exists: {os.path.exists('network_monitor.db')}")

try:
    db = SessionLocal()
    count = db.query(Device).count()
    devices = db.query(Device).all()
    print(f"\n[DB DEBUG] Total Devices: {count}")
    for d in devices:
        print(f" - ID: {d.id} | IP: {d.ip} | Vendor: {d.vendor} | Status: {d.status}")
    db.close()
    print("\n[SUCCESS] Database read successfully.")
except Exception as e:
    print(f"\n[ERROR] {e}")
