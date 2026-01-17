# 🚀 Control-Red-Casa - Guía de Instalación y Uso

## 📋 Requisitos Previos

Antes de instalar, necesitas:

1. **Python 3.8 o superior**
   - Descarga: https://www.python.org/downloads/
   - ⚠️ **IMPORTANTE**: Marca la opción "Add Python to PATH" durante la instalación

2. **Node.js LTS**
   - Descarga: https://nodejs.org/
   - Instala la versión LTS (recomendada)

---

## 🎯 Instalación Rápida (3 Pasos)

### Paso 1: Instalar Requisitos
1. Instala **Python** (si no lo tienes)
2. Instala **Node.js** (si no lo tienes)

### Paso 2: Ejecutar Instalador
1. **Click derecho** en `INSTALAR.bat`
2. Selecciona **"Ejecutar como administrador"**
3. Espera a que termine (puede tardar 5-10 minutos)

### Paso 3: ¡Listo!
- Se creará un acceso directo en tu escritorio: **Control-Red-Casa**
- Doble clic para iniciar el sistema

---

## 🎮 Uso Diario

### Opción 1: Acceso Directo (Más Fácil)
1. **Doble clic** en el icono del escritorio: **Control-Red-Casa**
2. Acepta el UAC (permisos de administrador)
3. Espera 10 segundos
4. El navegador se abrirá automáticamente

### Opción 2: Script Manual
1. **Click derecho** en `INICIAR.bat`
2. Selecciona **"Ejecutar como administrador"**
3. Espera a que se abra el navegador

### Detener el Sistema
1. Ejecuta `DETENER.bat` (como administrador)
2. O cierra las ventanas de backend y frontend

---

## 💻 Crear Ejecutable (.exe)

Si quieres un archivo `.exe` para ejecutar más fácilmente:

### Método 1: Automático (Recomendado)
1. **Click derecho** en `CREAR_EXE.ps1`
2. Selecciona **"Ejecutar con PowerShell"**
3. Si aparece error de permisos, ejecuta primero:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
4. Se creará `Control-Red-Casa.exe`

### Método 2: Manual
Usa directamente `INICIAR.bat` (no necesitas .exe)

---

## 📁 Estructura de Archivos

```
control-red-casa/
│
├── INSTALAR.bat          ← Instalador (ejecutar PRIMERO)
├── INICIAR.bat           ← Iniciar sistema
├── DETENER.bat           ← Detener sistema
├── CREAR_EXE.ps1         ← Crear ejecutable (opcional)
│
├── backend/              ← Servidor Python
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
└── frontend/             ← Interfaz web
    ├── src/
    ├── package.json
    └── ...
```

---

## 🔧 Solución de Problemas

### Problema: "Python no está instalado"
**Solución**:
1. Instala Python desde https://www.python.org/downloads/
2. **IMPORTANTE**: Marca "Add Python to PATH"
3. Reinicia la terminal
4. Ejecuta `INSTALAR.bat` de nuevo

### Problema: "Node.js no está instalado"
**Solución**:
1. Instala Node.js desde https://nodejs.org/
2. Reinicia la terminal
3. Ejecuta `INSTALAR.bat` de nuevo

### Problema: "Puerto 8000 ya está en uso"
**Solución**:
1. Ejecuta `DETENER.bat`
2. O ejecuta manualmente:
   ```cmd
   cd backend
   kill_port_8000.bat
   ```

### Problema: "No se detectan dispositivos"
**Solución**:
1. **Ejecuta como ADMINISTRADOR** (muy importante)
2. El escaneo ARP requiere permisos elevados

### Problema: "Error al crear .exe"
**Solución**:
1. Abre PowerShell como administrador
2. Ejecuta:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   Install-Module -Name ps2exe -Scope CurrentUser -Force
   ```
3. Ejecuta `CREAR_EXE.ps1` de nuevo

---

## 🎯 Acceso a la Aplicación

Una vez iniciado el sistema:

- **Frontend (Interfaz Web)**: http://localhost:5173
- **Backend (API)**: http://127.0.0.1:8000
- **Documentación API**: http://127.0.0.1:8000/docs

---

## 📊 Funcionalidades Disponibles

✅ **Ordenamiento de Tabla** - Ordena por cualquier columna
✅ **Vista Detallada** - Métricas y gráficos de dispositivos
✅ **Exportación** - CSV y JSON
✅ **Autorización** - Marca dispositivos autorizados/bloqueados
✅ **Re-identificación** - Actualiza dispositivos desconocidos
✅ **Escáner de Puertos** - Escanea puertos en dispositivos
✅ **Tema Claro/Oscuro** - Toggle de tema con persistencia
✅ **Mapa de Red Interactivo** - Visualización de topología

---

## 🔐 Permisos de Administrador

**¿Por qué se necesitan?**

El sistema requiere permisos de administrador para:
- Escaneo ARP de la red (Scapy)
- Detección de dispositivos
- Acceso a interfaces de red

**Siempre ejecuta como administrador** para que funcione correctamente.

---

## 📞 Resumen Rápido

### Primera Vez
```
1. Instala Python y Node.js
2. Ejecuta INSTALAR.bat (como admin)
3. Espera a que termine
4. ¡Listo!
```

### Uso Diario
```
1. Doble clic en acceso directo del escritorio
   O ejecuta INICIAR.bat (como admin)
2. Espera 10 segundos
3. Usa la aplicación en el navegador
4. Para detener: ejecuta DETENER.bat
```

### Crear .exe (Opcional)
```
1. Ejecuta CREAR_EXE.ps1
2. Usa Control-Red-Casa.exe
```

---

## 🎉 ¡Listo para Usar!

Tu sistema de monitoreo de red está completamente configurado.

**¿Necesitas ayuda?** Revisa la documentación en la carpeta `docs/`

---

**Versión**: 3.0.0
**Última actualización**: 17 de Enero de 2026
