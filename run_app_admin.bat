@echo off
echo ========================================
echo Control Red Casa Pro - Launcher ADMIN
echo ========================================
echo.
echo [IMPORTANTE] Este script iniciara el backend como ADMINISTRADOR
echo [IMPORTANTE] Necesario para escanear dispositivos en la red
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

echo [INFO] Solicitando permisos de administrador para el backend...
echo [INFO] Acepta el UAC cuando aparezca
echo.

REM Iniciar backend como administrador usando PowerShell
powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd \"%~dp0backend\"; Write-Host \"========================================\" -ForegroundColor Cyan; Write-Host \"Control Red Casa - Backend (ADMIN)\" -ForegroundColor Green; Write-Host \"========================================\" -ForegroundColor Cyan; Write-Host \"\"; Write-Host \"[INFO] Verificando puerto 8000...\" -ForegroundColor Yellow; $port = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue; if ($port) { Write-Host \"[WARNING] Puerto 8000 en uso. Liberando...\" -ForegroundColor Yellow; Stop-Process -Id $port.OwningProcess -Force -ErrorAction SilentlyContinue; Start-Sleep -Seconds 1 }; Write-Host \"[OK] Puerto 8000 disponible\" -ForegroundColor Green; Write-Host \"\"; Write-Host \"[INFO] Iniciando backend...\" -ForegroundColor Yellow; Write-Host \"[INFO] Backend: http://localhost:8000\" -ForegroundColor Cyan; Write-Host \"[INFO] API Docs: http://localhost:8000/docs\" -ForegroundColor Cyan; Write-Host \"\"; python main.py' -Verb RunAs"

timeout /t 3 /nobreak >nul

echo.
echo Iniciando Frontend (modo normal)...
start "Control Red Casa - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo Sistema iniciado!
echo ========================================
echo.
echo Backend:  http://localhost:8000 (ADMIN)
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo [IMPORTANTE] El backend corre como administrador
echo [IMPORTANTE] Necesario para escanear la red
echo.
echo Presiona Ctrl+C en cada ventana para detener.
echo.
pause
