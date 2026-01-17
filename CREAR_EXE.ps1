# ============================================
# CONTROL-RED-CASA - Crear Ejecutable
# Convierte el launcher en un .exe
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CREAR EJECUTABLE - CONTROL-RED-CASA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si ps2exe está instalado
Write-Host "[1/4] Verificando ps2exe..." -ForegroundColor Yellow
$ps2exeInstalled = Get-Module -ListAvailable -Name ps2exe

if (-not $ps2exeInstalled) {
    Write-Host "[INFO] ps2exe no esta instalado. Instalando..." -ForegroundColor Yellow
    try {
        Install-Module -Name ps2exe -Scope CurrentUser -Force -AllowClobber
        Write-Host "[OK] ps2exe instalado correctamente" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] No se pudo instalar ps2exe" -ForegroundColor Red
        Write-Host "Ejecuta manualmente: Install-Module -Name ps2exe" -ForegroundColor Yellow
        pause
        exit 1
    }
}
else {
    Write-Host "[OK] ps2exe ya esta instalado" -ForegroundColor Green
}
Write-Host ""

# Crear script PowerShell principal
Write-Host "[2/4] Creando script PowerShell..." -ForegroundColor Yellow

$psScript = @'
# Control-Red-Casa Launcher
Add-Type -AssemblyName System.Windows.Forms

# Verificar permisos de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    [System.Windows.Forms.MessageBox]::Show(
        "Este programa requiere permisos de administrador.`n`nPor favor, ejecuta como administrador.",
        "Control-Red-Casa - Error",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    exit 1
}

# Obtener directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Verificar Python
$pythonVersion = & python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    [System.Windows.Forms.MessageBox]::Show(
        "Python no esta instalado.`n`nPor favor instala Python desde: https://www.python.org/downloads/",
        "Control-Red-Casa - Error",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    exit 1
}

# Verificar Node.js
$nodeVersion = & node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    [System.Windows.Forms.MessageBox]::Show(
        "Node.js no esta instalado.`n`nPor favor instala Node.js desde: https://nodejs.org/",
        "Control-Red-Casa - Error",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    exit 1
}

# Liberar puertos
Set-Location "$scriptDir\backend"
& .\kill_port_8000.bat | Out-Null
Set-Location $scriptDir

# Iniciar Backend
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd `"$scriptDir\backend`" && python main.py" -WindowStyle Minimized

# Esperar 3 segundos
Start-Sleep -Seconds 3

# Iniciar Frontend
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd `"$scriptDir\frontend`" && npm run dev" -WindowStyle Minimized

# Esperar 5 segundos
Start-Sleep -Seconds 5

# Abrir navegador
Start-Process "http://localhost:5173"

# Mostrar mensaje de éxito
[System.Windows.Forms.MessageBox]::Show(
    "Sistema iniciado correctamente!`n`nBackend: http://127.0.0.1:8000`nFrontend: http://localhost:5173`n`nPara detener el sistema, ejecuta DETENER.bat",
    "Control-Red-Casa - Iniciado",
    [System.Windows.Forms.MessageBoxButtons]::OK,
    [System.Windows.Forms.MessageBoxIcon]::Information
)
'@

$psScript | Out-File -FilePath ".\Control-Red-Casa-Launcher.ps1" -Encoding UTF8
Write-Host "[OK] Script PowerShell creado" -ForegroundColor Green
Write-Host ""

# Compilar a EXE
Write-Host "[3/4] Compilando a ejecutable (.exe)..." -ForegroundColor Yellow
Write-Host "Esto puede tardar un momento..." -ForegroundColor Yellow

try {
    Import-Module ps2exe
    
    Invoke-PS2EXE `
        -inputFile ".\Control-Red-Casa-Launcher.ps1" `
        -outputFile ".\Control-Red-Casa.exe" `
        -title "Control-Red-Casa Network Monitor" `
        -description "Sistema de Monitoreo de Red" `
        -company "Control-Red-Casa" `
        -product "Network Monitor" `
        -version "3.0.0" `
        -requireAdmin `
        -noConsole `
        -noError
    
    Write-Host "[OK] Ejecutable creado: Control-Red-Casa.exe" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Error al compilar: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternativa: Usa INICIAR.bat directamente" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host ""

# Limpiar archivo temporal
Write-Host "[4/4] Limpiando archivos temporales..." -ForegroundColor Yellow
Remove-Item ".\Control-Red-Casa-Launcher.ps1" -ErrorAction SilentlyContinue
Write-Host "[OK] Limpieza completada" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EJECUTABLE CREADO CORRECTAMENTE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Archivo creado: Control-Red-Casa.exe" -ForegroundColor Green
Write-Host ""
Write-Host "COMO USAR:" -ForegroundColor Yellow
Write-Host "1. Doble clic en Control-Red-Casa.exe" -ForegroundColor White
Write-Host "2. Acepta el UAC (permisos de administrador)" -ForegroundColor White
Write-Host "3. El sistema se iniciara automaticamente" -ForegroundColor White
Write-Host ""
Write-Host "Para detener: ejecuta DETENER.bat" -ForegroundColor Yellow
Write-Host ""

pause
