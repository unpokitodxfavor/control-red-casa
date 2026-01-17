@echo off
:: ============================================
:: CONTROL-RED-CASA - Detener Sistema
:: Cierra backend y frontend
:: ============================================

title Control-Red-Casa - Detener
color 0C

echo.
echo ========================================
echo   DETENIENDO CONTROL-RED-CASA
echo ========================================
echo.

:: Matar procesos de Python (backend)
echo [1/3] Deteniendo Backend (Python)...
taskkill /F /IM python.exe /T >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Backend detenido
) else (
    echo [INFO] Backend no estaba corriendo
)
echo.

:: Matar procesos de Node (frontend)
echo [2/3] Deteniendo Frontend (Node.js)...
taskkill /F /IM node.exe /T >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Frontend detenido
) else (
    echo [INFO] Frontend no estaba corriendo
)
echo.

:: Liberar puertos
echo [3/3] Liberando puertos...
cd backend
call kill_port_8000.bat >nul 2>&1
cd ..
echo [OK] Puertos liberados
echo.

echo ========================================
echo   SISTEMA DETENIDO CORRECTAMENTE
echo ========================================
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul

exit /b 0
