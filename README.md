# 🛡️ Control-Red-Casa - Network Monitor

<div align="center">

![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Sistema profesional de monitoreo de red con Dashboard Personalizable y Alertas Telegram**

[Características](#-características) • [Instalación](#-instalación-rápida) • [Uso](#-uso) • [Telegram](#-telegram) • [Dashboard](#-dashboard-personalizable)

</div>

---

## 📋 Descripción

**Control-Red-Casa** es un sistema de monitoreo de red avanzado (tipo PRTG) diseñado para uso doméstico o pequeña empresa. Detecta intrusos automáticamente, te avisa al móvil vía Telegram y te permite organizar tu visibilidad con un Dashboard totalmente personalizable (Drag & Drop).

### ✨ Características Principales (v2.2.0)

- ⚡ **Core Asíncrono** - Escaneo masivo sin bloqueo de interfaz.
- 📱 **Alertas Telegram** - Notificaciones instantáneas al móvil (Intrusos/Offline).
- 🎨 **Dashboard Personalizable** - Mueve, redimensiona y organiza tus widgets.
- 🔍 **Detección Automática** - Escaneo ARP/mDNS continuo.
- 🗺️ **Mapa de Red** - Visualización de topología (ahora como Widget embebido).
- 🔐 **Escáner de Puertos** - Análisis de seguridad bajo demanda.
- 📈 **Métricas** - Latencia y estado en tiempo real.
- 🌓 **Tema Claro/Oscuro** - Elegancia visual.


---

## 📦 Versión Portable (.EXE)

Esta versión permite ejecutar el programa sin instalar Python ni Node.js.

### Requisitos Previos
- **Instalar [Npcap](https://npcap.com/)** (Necesario para el escáner de red).
  - *Importante: Durante la instalación, marca "Install Npcap in WinPcap API-compatible Mode".*

### Cómo Iniciar
1. Navega a `backend/dist/`.
2. Ejecuta **`ControlRedCasaPro.exe`** (Click derecho -> **Ejecutar como administrador**).
3. Se abrirá una consola negra (Back-end) y tu navegador web (Front-end).

> **Nota**: No cierres la ventana negra, es el servidor funcionando.

---

## 🚀 Instalación Rápida

### Requisitos
- **Windows 10/11**
- **Python 3.8+**
- **Node.js 18+**

### Pasos
1. **Descargar** el repositorio.
2. Ejecutar **`INSTALAR.bat`** (Click derecho -> Administrador).
   - *Esto instalará todas las dependencias de Python y Node.js.*
3. Ejecutar **`INICIAR.bat`** (Click derecho -> Administrador).

> **Nota**: Si tienes problemas con librerías faltantes (pantalla roja), usa `FIX_DASHBOARD.bat`.

---

## 🎮 Uso

1. **Frontend**: Abre automáticamente en `http://localhost:5173`
2. **Backend**: Corre en segundo plano en `http://127.0.0.1:8001`

### Scripts Útiles
| Archivo | Función |
|---------|---------|
| `INICIAR.bat` | Arranca todo el sistema. |
| `DETENER.bat` | Para todos los procesos. |
| `FIX_DASHBOARD.bat` | Repara dependencias y reinicia. |
| `FORCE_RESET.bat` | Borra base de datos y reinicia de fábrica. |

---

## 📱 Telegram

Configura tus alertas para recibir avisos en el móvil:
1. Ve a **Configuración** en el menú.
2. Introduce tu `Bot Token` y `Chat ID`.
3. Dale a **"Probar Conexión"**.
4. ¡Listo! Recibirás avisos de *Nuevo Dispositivo* o *Dispositivo Offline*.

## 🎨 Dashboard Personalizable (NUEVO)

La versión 2.2.0 introduce un sistema de Grilla interactiva:
1. Pulsa **"Personalizar Dashboard"** (arriba derecha).
2. **Arrastra** los widgets donde quieras.
3. **Redimensiona** desde la esquina inferior derecha.
4. Pulsa **"Guardar Cambios"** para persistir tu diseño.

**Widgets Disponibles:**
- 📊 **Estadísticas**: Resumen global.
- 📱 **Dispositivos Recientes**: Listado rápido.
- ⚠️ **Alertas**: Notificaciones recientes (sustituye al mapa antiguo).
- 🗺️ **Mapa Mini**: Versión compacta del mapa de red.

---

## 🏗️ Estructura del Proyecto

```
/
├── backend/            # API FastAPI + SQLAlchemy + Scapy
├── frontend/           # React + Vite + Recharts + React-Grid-Layout
├── innecesario/        # Archivos antiguos/backup
├── INICIAR.bat         # Launcher
└── README.md           # Documentación
```

---

## 🤝 Contribuir
Proyecto de código abierto. ¡Las PRs son bienvenidas!

## 📄 Licencia
MIT
