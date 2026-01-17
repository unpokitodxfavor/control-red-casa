# Iniciar Backend como Administrador
# Este script debe ejecutarse desde PowerShell como administrador

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Control Red Casa - Backend (ADMIN)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Verificar si ya estamos como admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] Este script debe ejecutarse como ADMINISTRADOR" -ForegroundColor Red
    Write-Host ""
    Write-Host "Haz clic derecho en PowerShell y selecciona 'Ejecutar como administrador'" -ForegroundColor Yellow
    Write-Host "Luego ejecuta este script de nuevo" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "[OK] Ejecutando como administrador" -ForegroundColor Green
Write-Host ""

# Verificar puerto 8000
Write-Host "[INFO] Verificando puerto 8000..." -ForegroundColor Yellow
$port = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port) {
    Write-Host "[WARNING] Puerto 8000 en uso. Liberando..." -ForegroundColor Yellow
    Stop-Process -Id $port.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}
Write-Host "[OK] Puerto 8000 disponible" -ForegroundColor Green
Write-Host ""

# Verificar Python
Write-Host "[INFO] Verificando Python..." -ForegroundColor Yellow
$pythonCmd = $null

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
    Write-Host "[OK] Python encontrado" -ForegroundColor Green
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
    Write-Host "[OK] Python encontrado (py launcher)" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python no encontrado" -ForegroundColor Red
    Write-Host "Instala Python desde python.org" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Iniciando Backend" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "[INFO] API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "[INFO] Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

# Iniciar el backend
& $pythonCmd main.py
