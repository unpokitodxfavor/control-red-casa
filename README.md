# 🛡️ Control-Red-Casa - Network Monitor

<div align="center">

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Sistema de monitoreo de red completo con interfaz web moderna**

[Características](#-características) • [Instalación](#-instalación-rápida) • [Uso](#-uso) • [Documentación](#-documentación)

</div>

---

## 📋 Descripción

**Control-Red-Casa** es un sistema de monitoreo de red tipo PRTG diseñado para redes domésticas y pequeñas empresas. Detecta automáticamente dispositivos en tu red, monitorea su estado, escanea puertos y proporciona una interfaz web moderna para gestionar todo.

### ✨ Características Principales

- 🔍 **Detección Automática** - Escaneo ARP y mDNS de dispositivos
- 📊 **Dashboard Interactivo** - Visualización en tiempo real
- 🗺️ **Mapa de Red** - Topología visual interactiva
- 🔐 **Escáner de Puertos** - Análisis de seguridad
- 📈 **Métricas Detalladas** - Latencia, packet loss, uptime
- 🎨 **Tema Claro/Oscuro** - Interfaz personalizable
- 📥 **Exportación** - CSV y JSON
- 🔔 **Alertas** - Notificaciones de nuevos dispositivos
- 🔒 **Autorización** - Control de dispositivos permitidos

---

## 🚀 Instalación Rápida

### Requisitos Previos

- **Python 3.8+** - [Descargar](https://www.python.org/downloads/)
- **Node.js 18+** - [Descargar](https://nodejs.org/)
- **Windows 10/11** (con permisos de administrador)

### Instalación en 3 Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/unpokitodxfavor/control-red-casa.git
cd control-red-casa

# 2. Ejecutar instalador (como administrador)
INSTALAR.bat

# 3. Iniciar sistema (como administrador)
INICIAR.bat
```

O simplemente:
1. Descarga el repositorio
2. Click derecho en `INSTALAR.bat` → "Ejecutar como administrador"
3. Espera 5-10 minutos
4. ¡Listo!

---

## 🎮 Uso

### Iniciar el Sistema

**Opción 1: Acceso Directo** (Recomendado)
- Doble clic en el acceso directo del escritorio: `Control-Red-Casa`

**Opción 2: Script**
- Click derecho en `INICIAR.bat` → "Ejecutar como administrador"

**Opción 3: Ejecutable** (Opcional)
- Ejecuta `CREAR_EXE.ps1` para crear `Control-Red-Casa.exe`
- Doble clic en el ejecutable

### Acceder a la Aplicación

Una vez iniciado:
- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **Documentación API**: http://127.0.0.1:8000/docs

### Detener el Sistema

```bash
DETENER.bat
```

---

## 📊 Funcionalidades

### 1. Dashboard
- Resumen de dispositivos (total, online, nuevos)
- Lista de dispositivos recientes
- Filtros por estado (Online/Offline)
- Búsqueda en tiempo real

### 2. Gestión de Dispositivos
- **Ordenamiento** - Por IP, nombre, MAC, fabricante, fecha
- **Vista Detallada** - Métricas, gráficos, sensores
- **Edición de Alias** - Renombra dispositivos
- **Autorización** - Marca dispositivos permitidos/bloqueados

### 3. Escáner de Puertos
- **Puertos Comunes** - HTTP, HTTPS, SSH, FTP, etc.
- **Rangos Personalizados** - 1-1024, 1-10000
- **Puertos Específicos** - Define manualmente
- **Selección Múltiple** - Escanea varios dispositivos a la vez

### 4. Mapa de Red Interactivo
- Visualización de topología
- Nodos clicables con detalles
- Router central + dispositivos
- Estados visuales (online/offline)

### 5. Exportación de Datos
- **CSV** - Compatible con Excel
- **JSON** - Para programación
- Incluye todos los campos

### 6. Alertas
- Notificaciones de nuevos dispositivos
- Modal con detalles
- Historial de alertas

### 7. Configuración
- Actualización automática (15s - 5min)
- Notificaciones activables
- Tema claro/oscuro

---

## 🏗️ Arquitectura

```
control-red-casa/
│
├── backend/                 # Servidor Python (FastAPI)
│   ├── main.py             # API principal
│   ├── scanner.py          # Escaneo ARP/mDNS
│   ├── port_scanner.py     # Escaneo de puertos
│   ├── database.py         # SQLAlchemy ORM
│   ├── websocket_manager.py# WebSocket
│   └── requirements.txt    # Dependencias Python
│
├── frontend/               # Cliente React
│   ├── src/
│   │   ├── App.jsx        # Componente principal
│   │   ├── components/    # Componentes
│   │   │   ├── DeviceDetailView.jsx
│   │   │   ├── PortScannerModal.jsx
│   │   │   ├── NetworkMap.jsx
│   │   │   └── Charts.jsx
│   │   └── index.css      # Estilos
│   └── package.json       # Dependencias Node.js
│
├── INSTALAR.bat           # Instalador automático
├── INICIAR.bat            # Launcher principal
├── DETENER.bat            # Detener sistema
├── CREAR_EXE.ps1          # Crear ejecutable
└── README.md              # Este archivo
```

---

## 🔧 Tecnologías

### Backend
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para base de datos
- **Scapy** - Escaneo de red (ARP)
- **Zeroconf** - Descubrimiento mDNS
- **Uvicorn** - Servidor ASGI
- **WebSockets** - Comunicación en tiempo real

### Frontend
- **React 18** - Librería UI
- **Vite** - Build tool
- **Axios** - Cliente HTTP
- **Lucide React** - Iconos
- **Recharts** - Gráficos

---

## 📚 Documentación

### Guías de Usuario
- [Instalación Detallada](README_INSTALACION.md)
- [Ordenamiento de Tabla](docs/ordenamiento_tabla.md)
- [Escáner de Puertos](docs/escaner_puertos.md)
- [Tema y Mapa de Red](docs/tema_y_mapa_red.md)
- [Resumen Completo](docs/resumen_final_completo.md)

### Solución de Problemas
- [Puerto 8000 Ocupado](SOLUCION_PUERTO_8000.md)
- [No se Detectan Dispositivos](SOLUCION_NO_DISPOSITIVOS.md)
- [Guía Definitiva Admin](guia_definitiva_admin.md)

---

## 🔐 Permisos de Administrador

**¿Por qué se necesitan?**

El sistema requiere permisos de administrador para:
- Escaneo ARP de la red (Scapy)
- Detección de dispositivos
- Acceso a interfaces de red
- Escaneo de puertos

**Siempre ejecuta como administrador** para que funcione correctamente.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Si quieres mejorar el proyecto:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📝 Roadmap

### Próximas Funcionalidades
- [ ] WebSocket en tiempo real
- [ ] Grupos de dispositivos
- [ ] Alertas personalizadas
- [ ] Historial de conexiones
- [ ] Drag & drop en mapa
- [ ] Exportar mapa como imagen
- [ ] Soporte para Linux/macOS
- [ ] API REST completa
- [ ] Autenticación de usuarios

---

## 🐛 Reportar Problemas

Si encuentras un bug o tienes una sugerencia:
1. Abre un [Issue](https://github.com/unpokitodxfavor/control-red-casa/issues)
2. Describe el problema detalladamente
3. Incluye logs si es posible

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 👨‍💻 Autor

**unpokitodxfavor**
- GitHub: [@unpokitodxfavor](https://github.com/unpokitodxfavor)

---

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [React](https://react.dev/) - Librería UI
- [Scapy](https://scapy.net/) - Escaneo de red
- [Lucide](https://lucide.dev/) - Iconos

---

## 📊 Estadísticas

- **Líneas de código**: ~2000+
- **Componentes**: 8
- **Endpoints API**: 17
- **Funcionalidades**: 8 principales
- **Versión**: 3.0.0

---

<div align="center">

**⭐ Si te gusta el proyecto, dale una estrella! ⭐**

[Reportar Bug](https://github.com/unpokitodxfavor/control-red-casa/issues) • [Solicitar Funcionalidad](https://github.com/unpokitodxfavor/control-red-casa/issues) • [Documentación](README_INSTALACION.md)

</div>
