import sqlite3
import os

DB_FILE = "network_monitor.db"

print(f"--- DIAGNOSTICO DE BASE DE DATOS ---")
print(f"Archivo: {os.path.abspath(DB_FILE)}")

if not os.path.exists(DB_FILE):
    print("ERROR: El archivo de base de datos no existe.")
    exit(1)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

try:
    # 1. Contar dispositivos
    cursor.execute("SELECT COUNT(*) FROM devices")
    count = cursor.fetchone()[0]
    print(f"\n[DEVICES] Total encontrados en DB: {count}")
    
    if count > 0:
        cursor.execute("SELECT hostname, ip FROM devices LIMIT 5")
        rows = cursor.fetchall()
        print("Muestra de dispositivos:")
        for r in rows:
            print(f" - {r[0]} ({r[1]})")

    # 2. Verificar columnas de 'alerts'
    print(f"\n[ALERTS] Verificando columnas...")
    cursor.execute("PRAGMA table_info(alerts)")
    columns = cursor.fetchall()
    col_names = [c[1] for c in columns]
    print(f"Columnas encontradas: {col_names}")
    
    if 'alert_metadata' in col_names:
        print("✅ Columna 'alert_metadata' EXISTE (Nueva estructura)")
    else:
        print("❌ Columna 'alert_metadata' NO EXISTE")

    if 'metadata' in col_names:
        print("⚠️ Columna 'metadata' EXISTE (Antigua estructura)")
        
    if 'alert_metadata' not in col_names and 'metadata' in col_names:
        print("\n[DIAGNOSTICO] ¡Tienes la base de datos ANTIGUA!")
        print("La actualizacion no se aplico correctamente.")
        print("El codigo espera 'alert_metadata' pero la DB tiene 'metadata'.")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
finally:
    conn.close()
    print("\n--- FIN DIAGNOSTICO ---")
    input("Presiona Enter para cerrar...")
