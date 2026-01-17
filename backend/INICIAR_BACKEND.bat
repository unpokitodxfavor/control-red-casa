@echo off
REM ====================================================
REM Script simple para iniciar el backend
REM ====================================================

echo ========================================
echo Control Red Casa - Backend
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo [ERROR] No se encuentra main.py
    echo Este script debe ejecutarse desde la carpeta backend
    pause
    exit /b 1
)

echo [INFO] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python no encontrado
    echo Por favor instala Python desde python.org
    pause
    exit /b 1
)

echo [OK] Python encontrado:
python --version
echo.

echo [INFO] Verificando puerto 8000...
REM Buscar y cerrar proceso en puerto 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo [WARNING] Puerto 8000 en uso. Liberando...
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 1 /nobreak >nul
)
echo [OK] Puerto 8000 disponible
echo.

echo [INFO] Iniciando backend...
echo [INFO] El backend se ejecutara en http://localhost:8000
echo [INFO] Presiona Ctrl+C para detener
echo.
echo ========================================
echo.

REM Iniciar el backend
python main.py

pause
