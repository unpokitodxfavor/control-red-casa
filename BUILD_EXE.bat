@echo off
cd /d "%~dp0"
echo ===================================================
echo   CREANDO INSTALADOR / EJECUTABLE PORTABLE
echo ===================================================

echo [paso 1/4] Instalando PyInstaller...
pip install pyinstaller aiofiles uvicorn fastapi sqlalchemy psutil requests scapy pysnmp pyasn1 winotify jinja2 python-multipart pyinstaller

echo [paso 2/4] Construyendo Frontend (React)...
cd frontend
call npm install
call npm run build
cd ..

echo [paso 3/4] Preparando archivos estaticos...
if exist "backend\static" rmdir /s /q "backend\static"
mkdir "backend\static"
xcopy /E /I /Y "frontend\dist" "backend\static"

echo [paso 4/4] Empaquetando EXE con PyInstaller...
cd backend
pyinstaller --name "ControlRedCasaPro" ^
            --onefile ^
            --windowed ^
            --clean ^
            --add-data "static;static" ^
            --hidden-import="uvicorn.logging" ^
            --hidden-import="uvicorn.loops" ^
            --hidden-import="uvicorn.loops.auto" ^
            --hidden-import="uvicorn.protocols" ^
            --hidden-import="uvicorn.protocols.http" ^
            --hidden-import="uvicorn.protocols.http.auto" ^
            --hidden-import="uvicorn.protocols.websockets" ^
            --hidden-import="uvicorn.protocols.websockets.auto" ^
            --hidden-import="uvicorn.lifespan.on" ^
            --hidden-import="engineio.async_drivers.threading" ^
            --hidden-import="pysnmp.smi.mibs" ^
            --hidden-import="pysnmp.smi.mibs.instances" ^
            --collect-all="pysnmp" ^
            server.py

echo.
echo ===================================================
echo   FINALIZADO!
echo ===================================================
echo Tu ejecutable esta listo en: backend\dist\ControlRedCasaPro.exe
echo.
echo COPIA ese archivo .exe al otro ordenador.
echo RECUERDA: En el otro PC debes instalar Npcap (https://npcap.com/)
echo.
pause
