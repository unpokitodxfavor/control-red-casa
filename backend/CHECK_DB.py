from database import engine, Config, SessionLocal
from sqlalchemy import inspect

try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")

    if "config" in tables:
        print("✅ Config table exists.")
        
        # Try to insert
        try:
            db = SessionLocal()
            print("Attempting to write to config...")
            db.merge(Config(key='test_key', value='test_value', category='TEST'))
            db.commit()
            print("✅ Write successful")
            db.close()
        except Exception as e:
            print(f"❌ Write failed: {e}")
    else:
        print("❌ Config table MISSING.")
except Exception as e:
    print(f"❌ Error inspecting DB: {e}")
