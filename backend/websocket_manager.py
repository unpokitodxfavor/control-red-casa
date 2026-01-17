"""
Sistema de WebSockets para comunicación en tiempo real con el frontend.
"""
import json
import logging
from typing import List
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Gestiona las conexiones WebSocket activas"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Acepta una nueva conexión"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nueva conexión WebSocket. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Elimina una conexión"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Conexión WebSocket cerrada. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Envía un mensaje a una conexión específica"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Envía un mensaje a todas las conexiones activas"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error enviando mensaje WebSocket: {e}")
                disconnected.append(connection)
        
        # Limpiar conexiones rotas
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_device_update(self, device_data: dict):
        """Broadcast actualización de dispositivo"""
        await self.broadcast({
            "type": "device_update",
            "data": device_data
        })
    
    async def broadcast_alert(self, alert_data: dict):
        """Broadcast nueva alerta"""
        await self.broadcast({
            "type": "alert_new",
            "data": alert_data
        })
    
    async def broadcast_metric(self, metric_data: dict):
        """Broadcast nueva métrica"""
        await self.broadcast({
            "type": "metric_update",
            "data": metric_data
        })
    
    async def broadcast_status(self, status_data: dict):
        """Broadcast actualización de estado general"""
        await self.broadcast({
            "type": "status_update",
            "data": status_data
        })

# Instancia global del manager
manager = ConnectionManager()
