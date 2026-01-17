@echo off
REM ====================================================
REM Script para iniciar el backend COMO ADMINISTRADOR
REM ====================================================

echo ========================================
echo Control Red Casa - Backend (ADMIN)
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo [ERROR] No se encuentra main.py
    echo Este script debe ejecutarse desde la carpeta backend
    pause
    exit /b 1
)

echo [INFO] Solicitando permisos de administrador...
echo [INFO] Acepta el UAC cuando aparezca
echo.

REM Ejecutar PowerShell como administrador
powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd \"%cd%\"; Write-Host \"[INFO] Verificando puerto 8000...\" -ForegroundColor Cyan; $port = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue; if ($port) { Write-Host \"[WARNING] Puerto 8000 en uso. Liberando...\" -ForegroundColor Yellow; Stop-Process -Id $port.OwningProcess -Force -ErrorAction SilentlyContinue; Start-Sleep -Seconds 1 }; Write-Host \"[OK] Puerto 8000 disponible\" -ForegroundColor Green; Write-Host \"\"; Write-Host \"========================================\" -ForegroundColor Cyan; Write-Host \"Iniciando Backend como ADMINISTRADOR\" -ForegroundColor Green; Write-Host \"========================================\" -ForegroundColor Cyan; Write-Host \"\"; Write-Host \"[INFO] Backend: http://localhost:8000\" -ForegroundColor Yellow; Write-Host \"[INFO] API Docs: http://localhost:8000/docs\" -ForegroundColor Yellow; Write-Host \"[INFO] Presiona Ctrl+C para detener\" -ForegroundColor Yellow; Write-Host \"\"; python main.py' -Verb RunAs"

echo.
echo [INFO] El backend se esta iniciando en una ventana separada con permisos de administrador
echo [INFO] Si no aparece, verifica que aceptaste el UAC
echo.
pause
