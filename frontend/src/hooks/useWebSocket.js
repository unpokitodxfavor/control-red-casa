import { useState, useEffect } from 'react';
import io from 'socket.io-client';

const SOCKET_URL = 'ws://127.0.0.1:8000/ws';

/**
 * Hook para gestionar la conexión WebSocket
 */
export const useWebSocket = () => {
    const [socket, setSocket] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        // Crear conexión WebSocket nativa (no socket.io)
        const ws = new WebSocket(SOCKET_URL);

        ws.onopen = () => {
            console.log('✅ WebSocket conectado');
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('📨 Mensaje recibido:', data);
                setMessages(prev => [...prev, data]);
            } catch (err) {
                console.error('Error parseando mensaje WebSocket:', err);
            }
        };

        ws.onerror = (error) => {
            console.error('❌ Error WebSocket:', error);
        };

        ws.onclose = () => {
            console.log('🔌 WebSocket desconectado');
            setIsConnected(false);

            // Intentar reconectar después de 5 segundos
            setTimeout(() => {
                console.log('🔄 Intentando reconectar...');
                window.location.reload(); // Simple reconnect strategy
            }, 5000);
        };

        setSocket(ws);

        return () => {
            ws.close();
        };
    }, []);

    return { socket, isConnected, messages };
};

/**
 * Hook para escuchar eventos específicos de WebSocket
 */
export const useWebSocketEvent = (eventType, callback) => {
    const { messages } = useWebSocket();

    useEffect(() => {
        const matchingMessages = messages.filter(msg => msg.type === eventType);
        if (matchingMessages.length > 0) {
            matchingMessages.forEach(msg => callback(msg.data));
        }
    }, [messages, eventType, callback]);
};
