import requests
import sys

URL = "http://127.0.0.1:8001/test_connection"

print(f"Probando conexión a {URL}...")

try:
    response = requests.get(URL, timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("[EXITO] El Backend esta FUNCIONANDO y RESPONDIENDO.")
        print("Respuesta:", response.json())
        print("\nCONCLUSION: El problema es el NAVEGADOR o FIREWALL.")
    else:
        print(f"[ERROR] El servidor respondió con error: {response.status_code}")
except Exception as e:
    print(f"[FALLO] No se pudo conectar: {e}")
    print("\nCONCLUSION: El Backend NO esta corriendo o falló al iniciar.")
    print("Verifica la ventana negra del backend para ver errores.")
