@echo off
title PROBAR DISPOSITIVOS
color 0E

echo ========================================
echo   DIAGNOSTICO API DISPOSITIVOS
echo ========================================
echo.

echo [1/3] Probando conectividad con API...
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] No se puede conectar al backend (http://127.0.0.1:8000)
    echo Asegurate de que el backend este corriendo.
    pause
    exit /b
)
echo [OK] Backend reachable.
echo.

echo [2/3] Consultando endpoint /devices...
curl -v http://127.0.0.1:8000/devices > response_devices.json 2> curl_error.log

if %errorLevel% neq 0 (
    echo [ERROR] Fallo la peticion a /devices
    type curl_error.log
    pause
    exit /b
)
echo [OK] Respuesta recibida.
echo.

echo [3/3] Analizando respuesta...
powershell -Command "try { $json = Get-Content response_devices.json | ConvertFrom-Json; Write-Host 'Dispositivos encontrados:' $json.Count; if($json.Count -gt 0) { Write-Host 'Primer dispositivo:'; $json[0] | Format-List } } catch { Write-Host '[ERROR] JSON invalido o vacio' -ForegroundColor Red; Get-Content response_devices.json }"

echo.
echo ========================================
echo   FIN DEL DIAGNOSTICO
echo ========================================
pause
