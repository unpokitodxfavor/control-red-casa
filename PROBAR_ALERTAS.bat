@echo off
:: ============================================
:: PROBAR ALERTAS - Script de Pruebas Rápidas
:: ============================================

title Probar Sistema de Alertas
color 0E

echo.
echo ========================================
echo   PROBAR SISTEMA DE ALERTAS
echo ========================================
echo.

:: Verificar si el backend está corriendo
curl -s http://127.0.0.1:8000/ >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] El backend no esta corriendo
    echo.
    echo Por favor inicia el backend primero:
    echo   cd backend
    echo   python main.py
    echo.
    pause
    exit /b 1
)

echo [OK] Backend esta corriendo
echo.

:menu
echo ========================================
echo   MENU DE PRUEBAS
echo ========================================
echo.
echo 1. Generar alerta INFO
echo 2. Generar alerta WARNING
echo 3. Generar alerta CRITICAL
echo 4. Generar 3 alertas (todas)
echo 5. Ver alertas activas (API)
echo 6. Ver todas las alertas (API)
echo 7. Ver reglas de alertas
echo 8. Salir
echo.
set /p choice="Selecciona una opcion (1-8): "

if "%choice%"=="1" goto info
if "%choice%"=="2" goto warning
if "%choice%"=="3" goto critical
if "%choice%"=="4" goto all
if "%choice%"=="5" goto active
if "%choice%"=="6" goto list
if "%choice%"=="7" goto rules
if "%choice%"=="8" goto end
goto menu

:info
echo.
echo Generando alerta INFO...
curl -X POST http://127.0.0.1:8000/alerts/test -H "Content-Type: application/json" -d "{\"level\": \"INFO\", \"message\": \"Esta es una alerta informativa de prueba\", \"channels\": [\"in_app\"]}"
echo.
echo.
echo [OK] Alerta INFO generada
echo Revisa la aplicacion web - deberia aparecer un toast azul
echo.
pause
goto menu

:warning
echo.
echo Generando alerta WARNING...
curl -X POST http://127.0.0.1:8000/alerts/test -H "Content-Type: application/json" -d "{\"level\": \"WARNING\", \"message\": \"Esta es una alerta de advertencia de prueba\", \"channels\": [\"in_app\"]}"
echo.
echo.
echo [OK] Alerta WARNING generada
echo Revisa la aplicacion web - deberia aparecer un toast naranja
echo.
pause
goto menu

:critical
echo.
echo Generando alerta CRITICAL...
curl -X POST http://127.0.0.1:8000/alerts/test -H "Content-Type: application/json" -d "{\"level\": \"CRITICAL\", \"message\": \"Esta es una alerta critica de prueba\", \"channels\": [\"in_app\"]}"
echo.
echo.
echo [OK] Alerta CRITICAL generada
echo Revisa la aplicacion web - deberia aparecer un toast rojo
echo.
pause
goto menu

:all
echo.
echo Generando 3 alertas...
echo.
echo [1/3] INFO...
curl -X POST http://127.0.0.1:8000/alerts/test -H "Content-Type: application/json" -d "{\"level\": \"INFO\", \"message\": \"Alerta informativa\", \"channels\": [\"in_app\"]}"
timeout /t 1 /nobreak >nul
echo.
echo [2/3] WARNING...
curl -X POST http://127.0.0.1:8000/alerts/test -H "Content-Type: application/json" -d "{\"level\": \"WARNING\", \"message\": \"Alerta de advertencia\", \"channels\": [\"in_app\"]}"
timeout /t 1 /nobreak >nul
echo.
echo [3/3] CRITICAL...
curl -X POST http://127.0.0.1:8000/alerts/test -H "Content-Type: application/json" -d "{\"level\": \"CRITICAL\", \"message\": \"Alerta critica\", \"channels\": [\"in_app\"]}"
echo.
echo.
echo [OK] 3 alertas generadas
echo Revisa la aplicacion web - deberian aparecer 3 toasts apilados
echo El badge deberia mostrar "3"
echo.
pause
goto menu

:active
echo.
echo Consultando alertas activas...
echo.
curl http://127.0.0.1:8000/alerts/active
echo.
echo.
pause
goto menu

:list
echo.
echo Consultando todas las alertas...
echo.
curl http://127.0.0.1:8000/alerts
echo.
echo.
pause
goto menu

:rules
echo.
echo Consultando reglas de alertas...
echo.
curl http://127.0.0.1:8000/alerts/rules
echo.
echo.
pause
goto menu

:end
echo.
echo Saliendo...
exit /b 0
