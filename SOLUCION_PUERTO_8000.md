# 🔧 Solución al Error: Puerto 8000 en Uso

## ❓ ¿Por qué ocurre este error?

El error **WinError 10048** significa que el puerto 8000 ya está siendo utilizado por otro proceso. Esto sucede cuando:

1. **El backend no se cerró correctamente** la última vez que lo ejecutaste
2. **Hay múltiples instancias** del backend corriendo
3. **Cerraste Antigravity** pero el proceso Python siguió ejecutándose en segundo plano

## ✅ Soluciones

### Opción 1: Usar los Scripts Mejorados (RECOMENDADO)

Los scripts de inicio ahora **automáticamente liberan el puerto** antes de iniciar:

```batch
# Para iniciar todo el sistema:
run_app.bat

# Para iniciar solo el backend:
cd backend
INICIAR_BACKEND.bat
```

### Opción 2: Liberar el Puerto Manualmente

Si el error persiste, ejecuta este script:

```batch
cd backend
kill_port_8000.bat
```

### Opción 3: Comando Manual

Abre PowerShell como administrador y ejecuta:

```powershell
# Encontrar el proceso usando el puerto 8000
netstat -ano | findstr :8000

# Cerrar el proceso (reemplaza PID con el número que aparece)
taskkill /F /PID <PID>
```

## 🔍 Cómo Prevenir el Problema

1. **Cierra correctamente el backend**: Usa `Ctrl+C` en la ventana de comandos antes de cerrarla
2. **Usa los scripts de inicio**: Los scripts `run_app.bat` e `INICIAR_BACKEND.bat` ahora limpian automáticamente los puertos
3. **Evita cerrar ventanas bruscamente**: No cierres la ventana con la X, usa `Ctrl+C` primero

## 📋 Diagnóstico Rápido

Para verificar qué está usando el puerto 8000:

```batch
netstat -ano | findstr :8000
```

Esto mostrará algo como:
```
TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    12345
```

El número al final (12345) es el **PID** del proceso.

## 🚀 Inicio Rápido sin Problemas

1. Ejecuta `run_app.bat` desde la carpeta principal
2. El script automáticamente:
   - Verifica si los puertos están en uso
   - Cierra procesos anteriores
   - Inicia backend y frontend limpios

## ⚠️ Si Nada Funciona

Si después de todo esto el error persiste:

1. **Reinicia tu computadora** - Esto cerrará todos los procesos
2. **Verifica que no hay otro software** usando el puerto 8000
3. **Cambia el puerto** en `backend/main.py` (línea 600):
   ```python
   uvicorn.run(app, host="127.0.0.1", port=8001)  # Cambia 8000 a 8001
   ```

## 📞 Resumen

- ✅ **Solución automática**: Los scripts ahora limpian los puertos automáticamente
- ✅ **Script dedicado**: `kill_port_8000.bat` para liberar el puerto manualmente
- ✅ **Prevención**: Cierra siempre con `Ctrl+C` antes de cerrar la ventana
