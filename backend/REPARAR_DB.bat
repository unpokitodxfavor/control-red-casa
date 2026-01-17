@echo off
cd /d "%~dp0"
title REPARAR BASE DE DATOS
color 0E

echo ==========================================
echo   REPARAR BASE DE DATOS (Solucion Rapida)
echo ==========================================
echo.

echo [1/3] Cerrando procesos de Python (Backend)...
taskkill /F /IM python.exe /T 2>nul
echo [OK] Procesos cerrados.
echo.

echo [2/3] Eliminando base de datos antigua...
if exist network_monitor.db (
    del network_monitor.db
    echo [OK] Base de datos eliminada.
) else (
    echo [INFO] No habia base de datos previa.
)
echo.

echo [3/3] Creando nueva base de datos...
python -c "from database import init_db; init_db()"

if %errorlevel% equ 0 (
    echo.
    echo [EXITO] Base de datos actualizada correctamente!
    echo.
    echo ------------------------------------------
    echo   AHORA PUEDES INICIAR EL SISTEMA:
    echo ------------------------------------------
    echo   1. En esta ventana escribe: python main.py
    echo   2. En otra ventana/terminal: cd ../frontend ^& npm run dev
    echo.
) else (
    echo.
    echo [ERROR] Hubo un problema creando la base de datos.
    echo Verifica el error de arriba.
)

pause
