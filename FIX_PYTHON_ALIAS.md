# Guía: Deshabilitar Alias de Microsoft Store para Python

## 🔴 Problema
Windows redirige `python` al Microsoft Store en lugar de usar el Python instalado.

## ✅ Solución Rápida (Recomendada)

### Opción 1: Deshabilitar Alias (5 segundos)

1. Presiona **Win + I** (Configuración)
2. Ve a: **Aplicaciones** → **Configuración avanzada de aplicaciones** → **Alias de ejecución de aplicaciones**
3. **DESACTIVA** (OFF):
   - `python.exe`
   - `python3.exe`
   - `py.exe` (si aparece)

4. Cierra y vuelve a abrir CMD

### Opción 2: Usar Script Alternativo

Ejecuta: **`backend\start_backend.bat`**

Este script:
- Busca `py` primero (funciona)
- Busca Python en ubicaciones comunes
- Ignora el alias de Store

---

## 🚀 Inicio del Sistema

Una vez deshabilitado el alias:

```cmd
# Ventana 1 - Backend
cd c:\Users\admin\Desktop\plugins\control-red-casa\backend
python main.py

# Ventana 2 - Frontend
cd c:\Users\admin\Desktop\plugins\control-red-casa\frontend
npm run dev
```

O simplemente ejecuta: `start_manual.bat`

---

## 📝 Verificar que funciona

```cmd
python --version
# Debería mostrar: Python 3.14.2
# NO: "Instalar desde Microsoft Store"
```

---

## ℹ️ ¿Por qué pasa esto?

Windows 10/11 tiene "alias" que redirigen `python` a la Store para "ayudar" a los usuarios a instalarlo. Pero si ya tienes Python instalado, causa este problema.
