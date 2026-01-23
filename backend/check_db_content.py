
import sys
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Device, Base  # Assuming database.py is in the same dir

# Setup DB connection
SQLALCHEMY_DATABASE_URL = "sqlite:///C:/Users/admin/Desktop/plugins/control-red-casa/backend/dist/network_monitor.db"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    count = db.query(Device).count()
    print(f"Device count: {count}")
    
    devices = db.query(Device).all()
    if count > 0:
        first = devices[0]
        # Manually create a dict to simulate what we expect (since simple json.dump might fail on objects)
        # However, we want to see if the OBJECTS are populated correctly.
        print(f"Device 1: ID={first.id}, IP={first.ip}, MAC={first.mac}, Hostname={first.hostname}")
        
        # Test serialization (simplified)
        serialized = []
        for d in devices:
            d_dict = {
                "id": d.id,
                "mac": d.mac,
                "ip": d.ip,
                "hostname": d.hostname,
                "vendor": d.vendor,
                "device_type": d.device_type,
                "status": d.status,
                "last_seen": str(d.last_seen) if d.last_seen else None
            }
            serialized.append(d_dict)
            
        print("Serialization successful.")
        print("Sample JSON:")
        print(json.dumps(serialized[:1], indent=2))
        
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
