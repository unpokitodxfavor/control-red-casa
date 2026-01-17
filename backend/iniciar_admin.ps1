# Script para iniciar el backend con privilegios de administrador
# Mostrará el diálogo UAC de Windows

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptPath "main.py"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Control Red Casa - Inicio con Admin" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Buscando Python..." -ForegroundColor Yellow

# Intentar encontrar Python
$pythonCmd = $null

# Opción 1: py launcher
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
    Write-Host "[OK] Encontrado: py launcher" -ForegroundColor Green
}
# Opción 2: python directo
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
    Write-Host "[OK] Encontrado: python" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] No se encontro Python" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instala Python desde python.org" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "[INFO] Solicitando permisos de administrador..." -ForegroundColor Yellow
Write-Host "[INFO] Aparecerá el diálogo UAC - Haz clic en 'Sí'" -ForegroundColor Yellow
Write-Host ""

# Iniciar como administrador (mostrará UAC)
Start-Process -FilePath $pythonCmd -ArgumentList $pythonScript -Verb RunAs -WorkingDirectory $scriptPath

Write-Host "[OK] Backend iniciado en ventana separada" -ForegroundColor Green
Write-Host ""
Write-Host "Para detener el backend, cierra su ventana o presiona Ctrl+C en ella" -ForegroundColor Cyan
Write-Host ""
