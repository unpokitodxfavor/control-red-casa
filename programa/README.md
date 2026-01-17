# Control Red Casa - Archivos del Programa

Esta carpeta contiene **SOLO** los archivos esenciales para que la aplicación funcione.

## 📁 Contenido

### Backend
- **main.py** - Servidor principal FastAPI
- **database.py** - Gestión de base de datos SQLite
- **scanner.py** - Escaneo de red (ARP/Scapy)
- **sensors.py** - Sensores de monitoreo
- **metrics_worker.py** - Recolección de métricas
- **websocket_manager.py** - WebSocket en tiempo real
- **oui_db.py** - Base de datos de fabricantes
- **diagnostico_red.py** - Diagnóstico de red
- **oui.txt** - Base de datos OUI (30K+ fabricantes)
- **requirements.txt** - Dependencias Python
- Scripts de inicio (.bat y .ps1)

### Frontend
- **src/** - Código fuente React
  - App.jsx - Aplicación principal
  - components/ - Componentes UI
  - hooks/ - Custom hooks (WebSocket)
- **package.json** - Dependencias Node.js
- **vite.config.js** - Configuración Vite
- **index.html** - HTML principal

### Raíz
- **setup.bat** - Instalación automática
- **setup_netguard.ps1** - Instalación PowerShell
- **run_app.bat** - Ejecutar aplicación
- **start_manual.bat** - Inicio manual

## 🚀 Instalación

1. Ejecuta `setup.bat` o `setup_netguard.ps1`
2. Ejecuta `run_app.bat`
3. Abre http://localhost:5173

## ⚠️ Archivos NO incluidos

- ❌ node_modules/ (se instala con `npm install`)
- ❌ venv/ (se crea automáticamente)
- ❌ __pycache__/ (se genera automáticamente)
- ❌ Archivos de backup
- ❌ Logs
- ❌ Documentación extensa
- ❌ Archivos de desarrollo

## 📦 Requisitos

- Python 3.8+
- Node.js 16+
- Permisos de administrador (para escaneo de red)
