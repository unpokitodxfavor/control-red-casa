import sqlite3
import os

def patch_db(db_path):
    print(f"--- Patching: {db_path} ---")
    if not os.path.exists(db_path):
        print(f"File not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists first
        cursor.execute("PRAGMA table_info(devices)")
        cols = [c[1] for c in cursor.fetchall()]
        
        if not cols:
            print("Table 'devices' not found in this database.")
        elif 'detected_at' not in cols:
            print("Adding 'detected_at' column to 'devices' table...")
            cursor.execute("ALTER TABLE devices ADD COLUMN detected_at DATETIME")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column 'detected_at' already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error patching database {db_path}: {e}")

if __name__ == "__main__":
    # Target both potential locations
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Dev database
    dev_db = os.path.join(base_dir, 'network_monitor.db')
    patch_db(dev_db)
    
    # 2. Dist database (where the app actually runs from logs)
    dist_db = os.path.join(base_dir, 'dist', 'network_monitor.db')
    patch_db(dist_db)

