# 🚀 Guía de Instalación Rápida - Control Red Casa Pro

## Pasos de Instalación

### 1. Backend

```powershell
cd c:\Users\admin\Desktop\plugins\control-red-casa\backend

# Instalar dependencias
pip install -r requirements.txt

# Activar versión extendida (BACKUP PRIMERO)
copy main.py main_backup.py
copy main_extended.py main.py

# Iniciar
python main.py
```

### 2. Frontend

```powershell
cd c:\Users\admin\Desktop\plugins\control-red-casa\frontend

# Instalar nuevas dependencias
npm install

# Iniciar
npm run dev
```

## Verificación

1. Backend: `http://localhost:8000/docs`
2. Frontend: `http://localhost:5173`
3. WebSocket: Debería conectar automáticamente

## Funcionalidades Nuevas

### Gráficos
- Click en cualquier dispositivo para ver métricas históricas
- Gráficos de latencia, packet loss, bandwidth
- Selector de rango temporal (1h, 6h, 12h, 24h, 48h, 1 semana)

### WebSocket
- Actualizaciones en tiempo real automáticas
- Sin necesidad de refrescar manualmente
- Conexión persistente con reconexión automática

### Sensores
- Cada dispositivo tiene sensores auto-creados
- Ping monitoring por defecto
- Activar/desactivar sensores individualmente

## Archivos Importantes

**Backend**:
- `main.py` (ahora extendido)
- `sensors.py`
- `metrics_worker.py`
- `websocket_manager.py`
- `database.py` (expandido)

**Frontend**:
- `components/Charts.jsx`
- `components/DeviceDetailView.jsx`
- `hooks/useWebSocket.js`

## Solución de Problemas

**Error en BD**: 
```powershell
cd backend
del network_monitor.db
python main.py
```

**Dependencias**: 
```powershell
pip install -r requirements.txt
npm install
```

**Puerto ocupado**:
Cambia puerto en `main.py`: `uvicorn.run(app, host="127.0.0.1", port=8001)`
