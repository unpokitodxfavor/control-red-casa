# ========================================
# Control Red Casa Pro - Setup PowerShell
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Control Red Casa Pro - Setup Completo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar permisos de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] Este script requiere permisos de administrador" -ForegroundColor Red
    Write-Host "Ejecuta: Right-click -> 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# [1/6] Verificar Python
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Python no esta instalado" -ForegroundColor Red
    Write-Host "Descarga desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# [2/6] Verificar Node.js
Write-Host ""
Write-Host "[2/6] Verificando Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Node.js no esta instalado" -ForegroundColor Red
    Write-Host "Descarga desde: https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# [3/6] Verificar pip
Write-Host ""
Write-Host "[3/6] Verificando pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "[OK] pip instalado" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] pip no esta disponible" -ForegroundColor Red
    exit 1
}

# [4/6] Instalar dependencias Backend
Write-Host ""
Write-Host "[4/6] Instalando dependencias del Backend..." -ForegroundColor Yellow
Set-Location backend

# Backup del main.py original
if (Test-Path "main.py") {
    if (-not (Test-Path "main_backup.py")) {
        Write-Host "Creando backup de main.py..." -ForegroundColor Cyan
        Copy-Item "main.py" "main_backup.py"
    }
}

# Activar main_extended.py si existe
if (Test-Path "main_extended.py") {
    Write-Host "Activando version extendida..." -ForegroundColor Cyan
    Copy-Item "main_extended.py" "main.py" -Force
    Write-Host "[OK] main_extended.py activado como main.py" -ForegroundColor Green
}

Write-Host "Instalando paquetes Python..." -ForegroundColor Cyan
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dependencias Backend instaladas" -ForegroundColor Green
}
else {
    Write-Host "[WARNING] Algunas dependencias fallaron, pero continuamos..." -ForegroundColor Yellow
}

Set-Location ..

# [5/6] Instalar dependencias Frontend
Write-Host ""
Write-Host "[5/6] Instalando dependencias del Frontend..." -ForegroundColor Yellow
Set-Location frontend

Write-Host "Ejecutando npm install..." -ForegroundColor Cyan
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dependencias Frontend instaladas" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Error instalando dependencias de Node" -ForegroundColor Red
    Set-Location ..
    Read-Host "Presiona Enter para salir"
    exit 1
}

Set-Location ..

# [6/6] Verificar instalacion
Write-Host ""
Write-Host "[6/6] Verificando instalacion..." -ForegroundColor Yellow

$backendOK = Test-Path "backend\main.py"
$frontendOK = Test-Path "frontend\node_modules"
$dbExists = Test-Path "backend\network_monitor.db"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALACION COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  " -NoNewline
if ($backendOK) { Write-Host "[OK]" -ForegroundColor Green } else { Write-Host "[FAIL]" -ForegroundColor Red }
Write-Host "Frontend: " -NoNewline
if ($frontendOK) { Write-Host "[OK]" -ForegroundColor Green } else { Write-Host "[FAIL]" -ForegroundColor Red }
Write-Host ""

if (-not $dbExists) {
    Write-Host "[INFO] La base de datos se creara automaticamente al iniciar" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Para iniciar el sistema:" -ForegroundColor Cyan
Write-Host "  Opcion 1: .\run_app.bat" -ForegroundColor White
Write-Host "  Opcion 2: Manual" -ForegroundColor White
Write-Host "    - Backend:  cd backend && python main.py" -ForegroundColor Gray
Write-Host "    - Frontend: cd frontend && npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "URLs importantes:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

Read-Host "Presiona Enter para salir"
