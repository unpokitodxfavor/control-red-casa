@echo off
:: ============================================
:: CONTROL-RED-CASA - Launcher Principal
:: Ejecuta backend y frontend automáticamente
:: ============================================

cd /d "%~dp0"

title Control-Red-Casa - Launcher
color 0A

echo.
echo ========================================
echo   CONTROL-RED-CASA - Network Monitor
echo ========================================
echo.

:: Verificar si estamos en modo administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Este programa requiere permisos de administrador
    echo.
    echo Por favor, ejecuta este archivo como administrador:
    echo 1. Click derecho en INICIAR.bat
    echo 2. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Ejecutando como administrador
echo.

:: Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python no esta instalado
    echo Por favor instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python encontrado
echo.

:: Verificar Node.js
echo [2/5] Verificando Node.js...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js no esta instalado
    echo Por favor instala Node.js desde: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js encontrado
echo.

:: Liberar puertos si están ocupados
echo [3/5] Liberando puertos 8000 y 5173...
cd backend
call kill_port_8000.bat >nul 2>&1
cd ..
echo [OK] Puertos liberados
echo.

:: Iniciar Backend
echo [4/5] Iniciando Backend...
cd backend
start "Backend - Control-Red-Casa" /min cmd /c "python server.py"
cd ..
timeout /t 3 /nobreak >nul
echo [OK] Backend iniciado en puerto 8001
echo.

:: Iniciar Frontend
echo [5/5] Iniciando Frontend...
cd frontend
start "Frontend - Control-Red-Casa" /min cmd /c "npm run dev"
cd ..
timeout /t 5 /nobreak >nul
echo [OK] Frontend iniciado en puerto 5173
echo.

echo ========================================
echo   SISTEMA INICIADO CORRECTAMENTE
echo ========================================
echo.
echo Backend:  http://127.0.0.1:8001
echo Frontend: http://localhost:5173
echo.
echo Abriendo navegador en 3 segundos...
timeout /t 3 /nobreak >nul

:: Abrir navegador
start http://localhost:5173

echo.
echo ========================================
echo   INSTRUCCIONES
echo ========================================
echo.
echo - El sistema esta corriendo en segundo plano
echo - Para DETENER el sistema, ejecuta: DETENER.bat
echo - Para ver logs, revisa las ventanas minimizadas
echo.
echo Presiona cualquier tecla para cerrar este launcher
echo (El sistema seguira corriendo)
pause >nul

exit /b 0
