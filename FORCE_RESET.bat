@echo off
echo ========================================
echo   LIMPIEZA TOTAL DE PROCESOS
echo ========================================
echo.

echo [1/3] Cerrando procesos de Python...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM py.exe >nul 2>&1
echo [OK] Python cerrado

echo [2/3] Cerrando procesos de Node.js...
taskkill /F /IM node.exe >nul 2>&1
echo [OK] Node.js cerrado

echo [3/3] Cerrando otros procesos...
taskkill /F /IM "Control Red Casa Pro.exe" >nul 2>&1
echo [OK] Otros cerrados

echo.
echo ========================================
echo   SISTEMA LIMPIO
echo ========================================
echo.
echo Ahora puedes ejecutar INICIAR.bat sin conflictos.
echo.
pause
