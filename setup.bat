@echo off
echo ========================================
echo Control Red Casa Pro - Setup Completo
echo ========================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Este script requiere permisos de administrador
    echo Por favor, ejecutalo como administrador
    pause
    exit /b 1
)

echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python no esta instalado
    echo Por favor instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python instalado

echo.
echo [2/5] Verificando Node.js...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js no esta instalado
    echo Por favor instala Node.js desde https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js instalado

echo.
echo [3/5] Instalando dependencias del Backend...
cd backend

:: Backup del main.py original
if exist main.py (
    if not exist main_backup.py (
        echo Creando backup de main.py...
        copy main.py main_backup.py >nul
    )
)

:: Activar main_extended.py
if exist main_extended.py (
    echo Activando version extendida...
    copy /Y main_extended.py main.py >nul
)

:: Instalar dependencias Python
echo Instalando paquetes Python...
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [WARNING] Algunas dependencias fallaron, pero continuamos...
)
echo [OK] Dependencias Backend instaladas

cd ..

echo.
echo [4/5] Instalando dependencias del Frontend...
cd frontend
call npm install
if %errorLevel% neq 0 (
    echo [ERROR] Error instalando dependencias de Node
    pause
    exit /b 1
)
echo [OK] Dependencias Frontend instaladas

cd ..

echo.
echo [5/5] Configuracion completada!
echo.
echo ========================================
echo INSTALACION COMPLETADA EXITOSAMENTE
echo ========================================
echo.
echo Para iniciar el sistema:
echo   1. Backend:  cd backend ^&^& python main.py
echo   2. Frontend: cd frontend ^&^& npm run dev
echo.
echo O usa run_app.bat para iniciar ambos automaticamente
echo.
pause
