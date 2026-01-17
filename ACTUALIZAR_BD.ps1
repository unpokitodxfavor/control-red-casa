# ============================================
# ACTUALIZAR BASE DE DATOS - Sistema de Alertas
# Recrea la base de datos con las nuevas tablas
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ACTUALIZAR BASE DE DATOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "C:\Users\admin\Desktop\plugins\control-red-casa\backend"
$dbPath = "$backendPath\network_monitor.db"

# Verificar si existe la base de datos
if (Test-Path $dbPath) {
    Write-Host "[INFO] Base de datos existente encontrada" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPCIONES:" -ForegroundColor Yellow
    Write-Host "1. Eliminar y recrear (RECOMENDADO para testing)" -ForegroundColor White
    Write-Host "   - Pierdes todos los datos actuales" -ForegroundColor Gray
    Write-Host "   - Base de datos limpia con nuevas tablas" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Mantener datos (NO RECOMENDADO)" -ForegroundColor White
    Write-Host "   - Puede causar errores si las tablas cambiaron" -ForegroundColor Gray
    Write-Host "   - Necesitarás migración manual" -ForegroundColor Gray
    Write-Host ""
    
    $choice = Read-Host "Selecciona opción (1 o 2)"
    
    if ($choice -eq "1") {
        Write-Host ""
        Write-Host "[1/3] Creando backup..." -ForegroundColor Yellow
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = "$backendPath\network_monitor_backup_$timestamp.db"
        Copy-Item $dbPath $backupPath
        Write-Host "[OK] Backup creado: network_monitor_backup_$timestamp.db" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "[2/3] Eliminando base de datos antigua..." -ForegroundColor Yellow
        Remove-Item $dbPath -Force
        Write-Host "[OK] Base de datos eliminada" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "[3/3] Creando nueva base de datos..." -ForegroundColor Yellow
        Set-Location $backendPath
        python -c "from database import init_db; init_db()"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Base de datos creada con éxito" -ForegroundColor Green
        }
        else {
            Write-Host "[ERROR] Error al crear la base de datos" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host ""
        Write-Host "[INFO] Manteniendo base de datos existente" -ForegroundColor Yellow
        Write-Host "[WARNING] Pueden ocurrir errores si las tablas cambiaron" -ForegroundColor Yellow
    }
}
else {
    Write-Host "[INFO] No existe base de datos previa" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[1/1] Creando base de datos..." -ForegroundColor Yellow
    Set-Location $backendPath
    python -c "from database import init_db; init_db()"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Base de datos creada con éxito" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Error al crear la base de datos" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ACTUALIZACIÓN COMPLETADA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "1. Inicia el backend: cd backend && python main.py" -ForegroundColor White
Write-Host "2. Inicia el frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "3. Abre http://localhost:5173" -ForegroundColor White
Write-Host "4. Prueba las alertas con PROBAR_ALERTAS.bat" -ForegroundColor White
Write-Host ""

pause
