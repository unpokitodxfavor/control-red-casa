@echo off
REM ====================================================
REM Solución al problema del alias de Microsoft Store
REM ====================================================

echo Buscando Python instalado...

REM Intentar python directo primero
where python >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Encontrado: python
    python --version
    echo.
    echo Iniciando backend con python...
    cd /d "%~dp0"
    python main.py
    pause
    exit /b 0
)

REM Intentar py launcher
where py >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Encontrado: py launcher
    py --version
    echo.
    echo Iniciando backend con py...
    cd /d "%~dp0"
    py main.py
    pause
    exit /b 0
)

REM Buscar Python en ubicaciones comunes
set PYTHON_PATHS=^
C:\Python314\python.exe;^
C:\Python313\python.exe;^
C:\Python312\python.exe;^
C:\Python311\python.exe;^
C:\Python310\python.exe;^
%LOCALAPPDATA%\Programs\Python\Python314\python.exe;^
%LOCALAPPDATA%\Programs\Python\Python313\python.exe;^
%LOCALAPPDATA%\Programs\Python\Python312\python.exe;^
%LOCALAPPDATA%\Programs\Python\Python311\python.exe

for %%p in (%PYTHON_PATHS%) do (
    if exist "%%p" (
        echo [OK] Encontrado: %%p
        "%%p" --version
        echo.
        echo Iniciando backend...
        cd /d "%~dp0"
        "%%p" main.py
        pause
        exit /b 0
    )
)

echo [ERROR] No se encontro Python instalado
echo.
echo Por favor:
echo 1. Abre Configuracion de Windows
echo 2. Ve a: Aplicaciones ^> Configuracion avanzada de aplicaciones ^> Alias de ejecucion de aplicaciones
echo 3. DESACTIVA los alias de "python.exe" y "python3.exe"
echo 4. Instala Python desde python.org si no lo tienes
echo.
pause
