import React, { useEffect, useRef, useState } from 'react';
import { X, Wifi, WifiOff, Router, Smartphone, Laptop, Printer, Server } from 'lucide-react';

/**
 * Mapa de Red Interactivo
 * Visualiza la topología de red con nodos y conexiones
 */
const NetworkMap = ({ devices, onClose }) => {
    const canvasRef = useRef(null);
    const [nodes, setNodes] = useState([]);
    const [selectedNode, setSelectedNode] = useState(null);
    const [hoveredNode, setHoveredNode] = useState(null);

    // Inicializar nodos con posiciones
    useEffect(() => {
        if (!devices || devices.length === 0) return;

        const canvas = canvasRef.current;
        if (!canvas) return;

        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(canvas.width, canvas.height) / 3;

        // Crear nodo central (router/gateway)
        const gateway = {
            id: 'gateway',
            label: 'Router',
            ip: devices[0]?.ip?.split('.').slice(0, 3).join('.') + '.1',
            type: 'gateway',
            x: centerX,
            y: centerY,
            vx: 0,
            vy: 0,
            online: true
        };

        // Crear nodos para cada dispositivo
        const deviceNodes = devices.map((device, index) => {
            const angle = (index / devices.length) * 2 * Math.PI;
            return {
                id: device.id,
                label: device.alias || device.hostname || `Device ${index + 1}`,
                ip: device.ip,
                mac: device.mac,
                vendor: device.vendor,
                type: getDeviceType(device),
                online: device.status === 'Online',
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle),
                vx: 0,
                vy: 0,
                device: device
            };
        });

        setNodes([gateway, ...deviceNodes]);
    }, [devices]);

    // Función para determinar el tipo de dispositivo
    const getDeviceType = (device) => {
        const vendor = (device.vendor || '').toLowerCase();
        const hostname = (device.hostname || '').toLowerCase();

        if (vendor.includes('apple') || vendor.includes('samsung') || hostname.includes('phone')) return 'phone';
        if (vendor.includes('hp') || vendor.includes('canon') || vendor.includes('printer')) return 'printer';
        if (hostname.includes('server') || vendor.includes('dell') || vendor.includes('hp enterprise')) return 'server';
        return 'laptop';
    };

    // Obtener icono según tipo
    const getIcon = (type) => {
        switch (type) {
            case 'gateway': return Router;
            case 'phone': return Smartphone;
            case 'printer': return Printer;
            case 'server': return Server;
            default: return Laptop;
        }
    };

    // Animación de física simple
    useEffect(() => {
        if (nodes.length === 0) return;

        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let animationId;

        const animate = () => {
            // Limpiar canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Dibujar conexiones
            nodes.forEach((node, i) => {
                if (i === 0) return; // Skip gateway

                const gateway = nodes[0];

                ctx.beginPath();
                ctx.moveTo(gateway.x, gateway.y);
                ctx.lineTo(node.x, node.y);
                ctx.strokeStyle = node.online ? 'rgba(59, 130, 246, 0.3)' : 'rgba(239, 68, 68, 0.2)';
                ctx.lineWidth = hoveredNode === node.id || selectedNode === node.id ? 3 : 1;
                ctx.stroke();
            });

            // Dibujar nodos
            nodes.forEach(node => {
                const isHovered = hoveredNode === node.id;
                const isSelected = selectedNode === node.id;
                const nodeRadius = node.id === 'gateway' ? 30 : 25;

                // Sombra
                if (isHovered || isSelected) {
                    ctx.shadowColor = node.online ? 'rgba(59, 130, 246, 0.5)' : 'rgba(239, 68, 68, 0.5)';
                    ctx.shadowBlur = 20;
                }

                // Círculo del nodo
                ctx.beginPath();
                ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI);
                ctx.fillStyle = node.online
                    ? (node.id === 'gateway' ? '#3b82f6' : '#10b981')
                    : '#ef4444';
                ctx.fill();

                // Borde
                ctx.strokeStyle = isHovered || isSelected ? '#ffffff' : 'rgba(255, 255, 255, 0.3)';
                ctx.lineWidth = isHovered || isSelected ? 3 : 2;
                ctx.stroke();

                ctx.shadowBlur = 0;

                // Etiqueta
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 12px Inter, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(node.label, node.x, node.y + nodeRadius + 20);

                // IP
                ctx.font = '10px Inter, sans-serif';
                ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                ctx.fillText(node.ip, node.x, node.y + nodeRadius + 35);
            });

            animationId = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
        };
    }, [nodes, hoveredNode, selectedNode]);

    // Manejar clicks en el canvas
    const handleCanvasClick = (e) => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Buscar nodo clickeado
        const clickedNode = nodes.find(node => {
            const dx = x - node.x;
            const dy = y - node.y;
            const nodeRadius = node.id === 'gateway' ? 30 : 25;
            return Math.sqrt(dx * dx + dy * dy) <= nodeRadius;
        });

        setSelectedNode(clickedNode ? clickedNode.id : null);
    };

    // Manejar hover
    const handleCanvasMove = (e) => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const hoveredNode = nodes.find(node => {
            const dx = x - node.x;
            const dy = y - node.y;
            const nodeRadius = node.id === 'gateway' ? 30 : 25;
            return Math.sqrt(dx * dx + dy * dy) <= nodeRadius;
        });

        setHoveredNode(hoveredNode ? hoveredNode.id : null);
        canvas.style.cursor = hoveredNode ? 'pointer' : 'default';
    };

    const selectedNodeData = nodes.find(n => n.id === selectedNode);

    return (
        <div style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000,
            backdropFilter: 'blur(4px)',
            padding: '2rem'
        }}>
            <div className="stat-card" style={{
                maxWidth: '1200px',
                width: '100%',
                height: '80vh',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column'
            }}>
                {/* Header */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '1.5rem',
                    paddingBottom: '1rem',
                    borderBottom: '1px solid var(--border-color)'
                }}>
                    <div>
                        <h2 style={{ marginBottom: '0.5rem' }}>Mapa de Red Interactivo</h2>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            {devices.length} dispositivos conectados
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: 'var(--text-secondary)',
                            cursor: 'pointer',
                            padding: '0.5rem'
                        }}
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* Canvas */}
                <div style={{ flex: 1, position: 'relative', background: 'rgba(0,0,0,0.2)', borderRadius: '1rem', overflow: 'hidden' }}>
                    <canvas
                        ref={canvasRef}
                        width={1000}
                        height={600}
                        onClick={handleCanvasClick}
                        onMouseMove={handleCanvasMove}
                        style={{ width: '100%', height: '100%' }}
                    />

                    {/* Leyenda */}
                    <div style={{
                        position: 'absolute',
                        top: '1rem',
                        right: '1rem',
                        background: 'rgba(0,0,0,0.7)',
                        padding: '1rem',
                        borderRadius: '0.75rem',
                        border: '1px solid var(--border-color)'
                    }}>
                        <h4 style={{ marginBottom: '0.75rem', fontSize: '0.875rem' }}>Leyenda</h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.75rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#3b82f6' }}></div>
                                <span>Router/Gateway</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#10b981' }}></div>
                                <span>Online</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ef4444' }}></div>
                                <span>Offline</span>
                            </div>
                        </div>
                    </div>

                    {/* Info del nodo seleccionado */}
                    {selectedNodeData && selectedNodeData.device && (
                        <div style={{
                            position: 'absolute',
                            bottom: '1rem',
                            left: '1rem',
                            background: 'rgba(0,0,0,0.9)',
                            padding: '1.5rem',
                            borderRadius: '0.75rem',
                            border: '1px solid var(--border-color)',
                            minWidth: '300px'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                                {selectedNodeData.online ? <Wifi size={20} color="var(--success)" /> : <WifiOff size={20} color="var(--danger)" />}
                                <h3 style={{ margin: 0 }}>{selectedNodeData.label}</h3>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
                                <div><strong>IP:</strong> <code>{selectedNodeData.ip}</code></div>
                                <div><strong>MAC:</strong> <code>{selectedNodeData.mac}</code></div>
                                <div><strong>Fabricante:</strong> {selectedNodeData.vendor || 'Desconocido'}</div>
                                <div><strong>Estado:</strong> <span style={{ color: selectedNodeData.online ? 'var(--success)' : 'var(--danger)' }}>
                                    {selectedNodeData.online ? 'Online' : 'Offline'}
                                </span></div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Instrucciones */}
                <div style={{
                    marginTop: '1rem',
                    padding: '1rem',
                    background: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    borderRadius: '0.75rem',
                    fontSize: '0.875rem',
                    color: 'var(--text-secondary)'
                }}>
                    <strong style={{ color: 'var(--accent-color)' }}>💡 Instrucciones:</strong> Haz clic en un nodo para ver sus detalles. Pasa el mouse sobre los nodos para resaltarlos.
                </div>
            </div>
        </div>
    );
};

export default NetworkMap;
