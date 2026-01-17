import requests
import sys
import os

# Cambiar al directorio del script para encontrar la DB correcta
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# INTENTA LEER LA CONFIGURACION DE LA BD
try:
    from database import SessionLocal, Config
    db = SessionLocal()
    token_entry = db.query(Config).filter(Config.key == "telegram_bot_token").first()
    chat_id_entry = db.query(Config).filter(Config.key == "telegram_chat_id").first()
    
    TOKEN = token_entry.value if token_entry else None
    CHAT_ID = chat_id_entry.value if chat_id_entry else None
    db.close()
except:
    TOKEN = None
    CHAT_ID = None

print("\n--- DIAGNOSTICO DE TELEGRAM ---")

if not TOKEN or not CHAT_ID:
    print("No se encontraron credenciales en la base de datos.")
    TOKEN = input("Introduce tu BOT TOKEN: ").strip()
    CHAT_ID = input("Introduce tu CHAT ID: ").strip()
else:
    print(f"Usando Token: {TOKEN[:5]}...{TOKEN[-5:]}")
    print(f"Usando Chat ID: {CHAT_ID}")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# 1. PRUEBA DE TEXTO PLANO
print("\n[1/2] Probando mensaje simple (Texto Plano)...")
try:
    data = {
        "chat_id": CHAT_ID,
        "text": "Hola, esto es una prueba de texto plano desde Control Red Casa."
    }
    resp = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {resp.status_code}")
    print(f"Respuesta: {resp.text}")
    
    if resp.status_code == 200:
        print("✅ MENSAJE SIMPLE ENVIADO CON ÉXITO")
    else:
        print("❌ FALLÓ EL MENSAJE SIMPLE")

except Exception as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")

# 2. PRUEBA DE MARKDOWN (Causante habitual de errores)
print("\n[2/2] Probando mensaje con formato (Markdown)...")
try:
    data = {
        "chat_id": CHAT_ID,
        "text": "*PRUEBA MARKDOWN* \n\n Esto es una prueba con formato.",
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {resp.status_code}")
    print(f"Respuesta: {resp.text}")
    
    if resp.status_code == 200:
        print("✅ MENSAJE MARKDOWN ENVIADO CON ÉXITO")
    else:
        print("❌ FALLÓ EL MENSAJE MARKDOWN (Posible error de formato)")

except Exception as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")

input("\nPresiona ENTER para salir...")
