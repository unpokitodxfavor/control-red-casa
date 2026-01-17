@echo off
:: ============================================
:: CONTROL-RED-CASA - Instalador Automático
:: Instala todas las dependencias
:: ============================================

title Control-Red-Casa - Instalador
color 0B

echo.
echo ========================================
echo   INSTALADOR - CONTROL-RED-CASA
echo ========================================
echo.
echo Este instalador configurara todo automaticamente
echo.
pause

:: Verificar Python
echo.
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python no esta instalado
    echo.
    echo Por favor instala Python 3.8 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marca la opcion "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% encontrado
echo.

:: Verificar Node.js
echo [2/6] Verificando Node.js...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js no esta instalado
    echo.
    echo Por favor instala Node.js LTS desde:
    echo https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% encontrado
echo.

:: Instalar dependencias de Python
echo [3/6] Instalando dependencias de Python...
echo Esto puede tardar varios minutos...
cd backend
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ERROR] Error instalando dependencias de Python
    pause
    exit /b 1
)
cd ..
echo [OK] Dependencias de Python instaladas
echo.

:: Instalar dependencias de Node.js
echo [4/6] Instalando dependencias de Node.js...
echo Esto puede tardar varios minutos...
cd frontend
call npm install
if %errorLevel% neq 0 (
    echo [ERROR] Error instalando dependencias de Node.js
    pause
    exit /b 1
)
cd ..
echo [OK] Dependencias de Node.js instaladas
echo.

:: Crear base de datos
echo [5/6] Creando base de datos...
cd backend
python -c "from database import init_db; init_db()" >nul 2>&1
cd ..
echo [OK] Base de datos creada
echo.

:: Crear acceso directo en el escritorio
echo [6/6] Creando acceso directo...
set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop

:: Crear VBS para acceso directo
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\Control-Red-Casa.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%INICIAR.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Control-Red-Casa Network Monitor" >> CreateShortcut.vbs
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,13" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo [OK] Acceso directo creado en el escritorio
echo.

echo ========================================
echo   INSTALACION COMPLETADA
echo ========================================
echo.
echo El sistema esta listo para usar!
echo.
echo OPCIONES PARA INICIAR:
echo 1. Doble clic en "Control-Red-Casa" en el escritorio
echo 2. Ejecutar INICIAR.bat (como administrador)
echo.
echo IMPORTANTE:
echo - Siempre ejecuta como ADMINISTRADOR
echo - Para detener: ejecuta DETENER.bat
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul

exit /b 0
