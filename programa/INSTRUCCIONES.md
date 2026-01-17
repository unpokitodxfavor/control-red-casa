# 🎯 INSTRUCCIONES DE USO - Control Red Casa

## ✅ ¿Qué hay en esta carpeta?

Esta carpeta contiene **ÚNICAMENTE** los archivos necesarios para que la aplicación funcione.

**Total de archivos:** 32 archivos (6.41 MB)

### ❌ NO incluye:
- node_modules/ (se instala automáticamente)
- venv/ (se crea automáticamente)
- __pycache__/ (se genera automáticamente)
- Archivos de backup
- Logs
- Código fuente de desarrollo

## 🚀 PASOS PARA INSTALAR Y EJECUTAR

### 1️⃣ Primera vez - Instalación

Ejecuta UNO de estos scripts (elige el que prefieras):

**Opción A - PowerShell (Recomendado):**
```powershell
Click derecho en "setup_netguard.ps1" → "Ejecutar con PowerShell"
```

**Opción B - Batch:**
```cmd
Doble click en "setup.bat"
```

Esto instalará:
- ✅ Dependencias Python (desde requirements.txt)
- ✅ Dependencias Node.js (desde package.json)
- ✅ Configuración automática

### 2️⃣ Ejecutar la aplicación

Después de la instalación, ejecuta:

```cmd
Doble click en "run_app.bat"
```

Esto iniciará:
- 🔹 Backend (FastAPI) en http://localhost:8000
- 🔹 Frontend (React) en http://localhost:5173

### 3️⃣ Acceder a la aplicación

Abre tu navegador en:
- **Aplicación:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

## 📋 Archivos Principales

### Backend (Python)
| Archivo | Descripción |
|---------|-------------|
| `main.py` | Servidor principal FastAPI |
| `database.py` | Gestión de base de datos |
| `scanner.py` | Escaneo de red (ARP) |
| `sensors.py` | Sensores de monitoreo |
| `metrics_worker.py` | Recolección de métricas |
| `websocket_manager.py` | WebSocket tiempo real |
| `oui_db.py` | Base de datos fabricantes |
| `oui.txt` | 30K+ fabricantes MAC |
| `requirements.txt` | Dependencias Python |

### Frontend (React)
| Archivo | Descripción |
|---------|-------------|
| `src/App.jsx` | Aplicación principal |
| `src/components/` | Componentes UI |
| `src/hooks/useWebSocket.js` | Hook WebSocket |
| `package.json` | Dependencias Node.js |
| `vite.config.js` | Configuración Vite |

### Scripts de Inicio
| Archivo | Descripción |
|---------|-------------|
| `setup.bat` | Instalación automática |
| `setup_netguard.ps1` | Instalación PowerShell |
| `run_app.bat` | Ejecutar aplicación |
| `start_manual.bat` | Inicio manual |

## ⚙️ Requisitos del Sistema

- **Python 3.8+** → [Descargar](https://www.python.org/downloads/)
- **Node.js 16+** → [Descargar](https://nodejs.org/)
- **Permisos de Administrador** (para escaneo de red)

## 🔧 Solución de Problemas

### "Python no encontrado"
```powershell
# Verifica que Python esté en el PATH
python --version

# Si no funciona, reinstala Python marcando "Add to PATH"
```

### "npm no encontrado"
```powershell
# Verifica que Node.js esté instalado
node --version
npm --version

# Si no funciona, reinstala Node.js
```

### Puerto ocupado
Si el puerto 8000 o 5173 está ocupado:
1. Cierra otras aplicaciones que usen esos puertos
2. O modifica los puertos en `backend/main.py` y `frontend/vite.config.js`

## 📞 Funcionalidades

✅ Detección automática de dispositivos en la red
✅ Monitoreo en tiempo real (WebSocket)
✅ Gráficos de métricas (latencia, disponibilidad)
✅ Identificación de fabricantes (30K+ OUI)
✅ Filtros por estado (online/offline)
✅ Sensores automáticos por dispositivo

## 🎉 ¡Listo!

Una vez ejecutado `run_app.bat`, la aplicación estará funcionando y detectará automáticamente los dispositivos en tu red.
