@echo off
cd /d "%~dp0"
title DIAGNOSTICO FINAL Y REPARACION
color 0b
echo ========================================================
echo      REPARACION FINAL - CONTROL RED CASA
echo ========================================================
echo.
echo [INFO] Detectando y reparando librerias SNMP...
python -m pip install --upgrade pip pysnmp pyasn1
echo.
echo [INFO] Reiniciando Backend para aplicar AUTODETECCION de Gateway...
echo.
echo Cerrando todo...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
timeout /t 2 >nul

echo.
echo INICIANDO SISTEMA...
start INICIAR.bat
echo.
echo [OK] El sistema ahora intentara detectar el router (192.168.50.1) automaticamente.
echo Revisa el Dashboard en 1 minuto.
pause
