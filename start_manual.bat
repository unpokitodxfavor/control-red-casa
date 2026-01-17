@echo off
echo ========================================
echo Control Red Casa Pro - Inicio Manual
echo ========================================
echo.
echo Este script es una alternativa si run_app.bat falla.
echo.

cd /d "%~dp0"

echo [1/2] Iniciando Backend en puerto 8000...
echo.
cd backend
start cmd /k "title Backend - Control Red Casa && python main.py || py main.py"
cd ..

timeout /t 3 /nobreak

echo [2/2] Iniciando Frontend en puerto 5173...
echo.
cd frontend  
start cmd /k "title Frontend - Control Red Casa && npm run dev"
cd ..

echo.
echo ========================================
echo LISTO - Abre tu navegador en:
echo http://localhost:5173
echo ========================================
echo.
pause
