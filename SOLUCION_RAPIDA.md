# 🚀 Guía de Inicio Rápido

## Problema Actual: No se detectan dispositivos

**Causa:** El backend NO está corriendo

## Solución en 3 pasos:

### Paso 1: Ejecutar Backend como ADMINISTRADOR ⚠️

**Opción A - Usando el script BAT (RECOMENDADO):**
```
1. Navegar a: c:\Users\admin\Desktop\plugins\control-red-casa\backend
2. Buscar archivo: INICIAR_BACKEND.bat
3. Clic DERECHO sobre el archivo
4. Seleccionar "Ejecutar como administrador"
```

**Opción B - Desde PowerShell con privilegios:**
```powershell
# Abrir PowerShell como Administrador, luego:
cd c:\Users\admin\Desktop\plugins\control-red-casa\backend
python main.py
```

### Paso 2: Verificar que funciona

Abrir navegador y visitar: http://localhost:8000/docs

Deberías ver la documentación de la API (Swagger UI).

Probar endpoint `/devices` - Debería mostrar lista de dispositivos (puede estar vacía al principio, se llenan en ~60 segundos).

### Paso 3: Iniciar Frontend

**Nueva terminal** (SIN admin necesario):
```powershell
cd c:\Users\admin\Desktop\plugins\control-red-casa\frontend
npm run dev
```

Abrir navegador: http://localhost:5173

## ¿Por qué como administrador?

El escaneo ARP (usado para detectar dispositivos) requiere permisos de administrador en Windows.

**Sin admin:**  
- ❌ Scapy no puede enviar paquetes ARP  
- ❌ No se detectan dispositivos  
- ❌ La lista queda vacía

**Con admin:**  
- ✅ Scapy funciona correctamente  
- ✅ Escanea la red cada 60 segundos  
- ✅ Detecta dispositivos automáticamente

## Configuración Detectada

✅ **Red detectada:** 192.168.50.0/24  
✅ **Tu IP:** 192.168.50.109  
✅ **Interface:** Wi-Fi  
✅ **Scapy:** Instalado  
✅ **Npcap:** Funcionando  

Todo está listo, solo falta iniciar el backend con permisos.

## Si sigue sin funcionar

1. **Revisar el log:**
   ```powershell
   cd c:\Users\admin\Desktop\plugins\control-red-casa\backend
   Get-Content backend.log -Tail 20
   ```

2. **Escaneo manual de prueba:**
   Ejecutar (como admin):
   ```powershell
   cd c:\Users\admin\Desktop\plugins\control-red-casa\backend
   python diagnostico_red.py
   ```

3. **Reinstalar dependencias:**
   ```powershell
   cd c:\Users\admin\Desktop\plugins\control-red-casa\backend
   pip install -r requirements.txt --upgrade
   ```

## Archivos creados para ayudarte

- 📄 `INICIAR_BACKEND.bat` - Script para arrancar backend fácilmente
- 📄 `diagnostico_red.py` - Diagnóstico de red y permisos
- 📄 Este archivo - Guía rápida

## Próximos pasos después de arrancar

Una vez que ambos (backend + frontend) estén corriendo:

1. Esperar ~60 segundos (primer escaneo de red)
2. Ver dispositivos aparecer en el dashboard
3. Los nuevos dispositivos mostrarán notificación
4. Puedes editar nombres/alias haciendo clic en el ícono de lápiz
