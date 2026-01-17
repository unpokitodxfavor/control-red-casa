# ⚡ INICIO RÁPIDO - Control Red Casa Pro

## 🚀 Instalación en 3 Clics

### 1️⃣ Instalar (Solo la primera vez)

**Opción A - Batch File (Recomendado)**:
1. Click derecho en `setup.bat`
2. Selecciona **"Ejecutar como administrador"**
3. Espera a que termine (3-5 minutos)

**Opción B - PowerShell**:
1. Click derecho en `setup_netguard.ps1`
2. Selecciona **"Run with PowerShell"**
3. Si pregunta, acepta ejecutar como administrador

### 2️⃣ Ejecutar

**Doble click** en `run_app.bat`

### 3️⃣ Abrir

Abre tu navegador en: **http://localhost:5173**

---

## ⚠️ Importante

- **Setup requiere permisos de administrador** (para instalar dependencias)
- **Run_app.bat NO requiere administrador**
- Solo necesitas ejecutar setup **una vez**

---

## 🔧 Lo que hace el Setup

```
✅ Verifica Python y Node.js
✅ Crea backup de main.py → main_backup.py
✅ Activa main_extended.py → main.py
✅ pip install -r requirements.txt (Backend)
✅ npm install (Frontend)
```

---

## 📊 Después del Setup

```cmd
run_app.bat  ← Click aquí para iniciar
```

Se abrirán 2 ventanas:
- 🐍 Backend (Python) - http://localhost:8000
- ⚛️ Frontend (React) - http://localhost:5173

---

## ❓ Problemas Comunes

**"Python no encontrado"**
→ Instala desde https://www.python.org/downloads/

**"Node no encontrado"**
→ Instala desde https://nodejs.org/

**"Permisos denegados"**
→ Click derecho → Ejecutar como administrador

**"Puerto ocupado"**
→ Cierra otras apps que usen puerto 8000 o 5173
