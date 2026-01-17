@echo off
echo ========================================
echo Control Red Casa Pro - Launcher
echo ========================================
echo.

:: Cambiar al directorio donde está el script
cd /d "%~dp0"

:: Verificar que existen los directorios
if not exist "backend" (
    echo [ERROR] No se encuentra el directorio backend
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] No se encuentra el directorio frontend
    pause
    exit /b 1
)

echo Iniciando Backend...
start "Control Red Casa - Backend" cmd /k "cd /d "%~dp0backend" && python main.py || py main.py"

timeout /t 3 /nobreak >nul

echo Iniciando Frontend...
start "Control Red Casa - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo Sistema iniciado!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Las ventanas se abriran automaticamente.
echo Presiona Ctrl+C en cada ventana para detener.
echo.
pause
