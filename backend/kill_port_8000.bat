@echo off
REM ====================================================
REM Script para liberar el puerto 8000
REM ====================================================

echo ========================================
echo Liberando puerto 8000...
echo ========================================
echo.

REM Buscar el proceso que está usando el puerto 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    set PID=%%a
)

if defined PID (
    echo [INFO] Proceso encontrado usando puerto 8000 (PID: %PID%)
    echo [INFO] Cerrando proceso...
    taskkill /F /PID %PID% >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] Puerto 8000 liberado correctamente
    ) else (
        echo [WARNING] No se pudo cerrar el proceso automaticamente
        echo [INFO] Intenta cerrar manualmente el proceso con PID: %PID%
    )
) else (
    echo [INFO] No hay ningun proceso usando el puerto 8000
)

echo.
echo ========================================
echo Proceso completado
echo ========================================
echo.
timeout /t 2 /nobreak >nul
