@echo off
:: Importante: Cambiar al directorio donde esta este archivo
cd /d "%~dp0"

title INSTALANDO DEPENDECIAS NUEVAS...
color 0B
echo.
echo ===============================================
echo   ACTUALIZANDO CONTROL-RED-CASA (DASHBOARD)
echo ===============================================
echo.
echo [1/2] Instalando libreria de "Arrastrar y Soltar" (react-grid-layout)...
cd frontend
call npm install
cd ..
echo [OK] Libreria instalada correcta.
echo.
echo [2/2] Reiniciando Sistema...
echo.
echo Por favor, cierre la ventana anterior de "INICIAR.bat" si sigue abierta.
timeout /t 3
start INICIAR.bat
exit
