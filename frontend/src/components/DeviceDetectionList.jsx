import React, { useState, useEffect } from 'react';
import { X, Clock, Wifi, WifiOff, Smartphone, Laptop, Printer, Server, Search, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

const DeviceDetectionList = ({ devices, onClose }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [sortDirection, setSortDirection] = useState('desc'); // Current session duration (desc = longest first)
    const [currentTime, setCurrentTime] = useState(new Date());

    // Update timer every second to show live "seconds ago"
    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    const getDeviceIcon = (vendor) => {
        const v = (vendor || '').toLowerCase();
        if (v.includes('apple') || v.includes('samsung') || v.includes('mobile')) return <Smartphone size={18} />;
        if (v.includes('hp') || v.includes('canon') || v.includes('printer')) return <Printer size={18} />;
        if (v.includes('server')) return <Server size={18} />;
        return <Laptop size={18} />;
    };

    const calculateDuration = (detectedAt) => {
        if (!detectedAt) return 0;
        const start = new Date(detectedAt);
        const diff = Math.floor((currentTime - start) / 1000);
        return diff > 0 ? diff : 0;
    };

    const formatDuration = (seconds) => {
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${mins}m`;
    };

    const filteredAndSortedDevices = devices
        .filter(d => d.status === 'Online')
        .filter(d => {
            const search = searchTerm.toLowerCase();
            return (
                (d.alias || d.hostname || '').toLowerCase().includes(search) ||
                (d.ip || '').includes(search) ||
                (d.mac || '').toLowerCase().includes(search)
            );
        })
        .sort((a, b) => {
            const durA = calculateDuration(a.detected_at);
            const durB = calculateDuration(b.detected_at);
            return sortDirection === 'asc' ? durA - durB : durB - durA;
        });

    return (
        <div style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000,
            backdropFilter: 'blur(10px)',
            padding: '2rem'
        }}>
            <div className="stat-card" style={{
                maxWidth: '1000px',
                width: '100%',
                maxHeight: '90vh',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                padding: '0',
                overflow: 'hidden',
                border: '1px solid var(--border-color)',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
            }}>
                {/* Header */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '1.5rem 2rem',
                    background: 'rgba(255,255,255,0.03)',
                    borderBottom: '1px solid var(--border-color)'
                }}>
                    <div>
                        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <Clock size={24} color="var(--accent-color)" />
                            Detecciones en Tiempo Real
                        </h2>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: '0.25rem 0 0 0' }}>
                            Dispositivos activos ordenados por tiempo de detección en la sesión actual
                        </p>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                        <div style={{ position: 'relative' }}>
                            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                            <input
                                type="text"
                                placeholder="Filtrar..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                style={{
                                    background: 'rgba(0,0,0,0.2)',
                                    border: '1px solid var(--border-color)',
                                    borderRadius: '0.5rem',
                                    padding: '0.50rem 1rem 0.50rem 2.25rem',
                                    color: 'white',
                                    fontSize: '0.875rem',
                                    width: '200px'
                                }}
                            />
                        </div>
                        <button
                            onClick={onClose}
                            style={{
                                background: 'rgba(255,255,255,0.05)',
                                border: '1px solid var(--border-color)',
                                color: 'var(--text-secondary)',
                                cursor: 'pointer',
                                padding: '0.5rem',
                                borderRadius: '0.5rem',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* List Container */}
                <div style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: '1rem 2rem 2rem 2rem'
                }}>
                    <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 0.75rem' }}>
                        <thead>
                            <tr style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                <th style={{ textAlign: 'left', padding: '0 1rem' }}>Dispositivo</th>
                                <th style={{ textAlign: 'left', padding: '0 1rem' }}>IP / MAC</th>
                                <th
                                    style={{ textAlign: 'center', padding: '0 1rem', cursor: 'pointer', userSelect: 'none' }}
                                    onClick={() => setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                                        Tiempo Detectado
                                        {sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                                    </div>
                                </th>
                                <th style={{ textAlign: 'center', padding: '0 1rem' }}>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredAndSortedDevices.length > 0 ? (
                                filteredAndSortedDevices.map((dev) => {
                                    const duration = calculateDuration(dev.detected_at);
                                    return (
                                        <tr key={dev.id} style={{
                                            background: 'rgba(255,255,255,0.02)',
                                            transition: 'transform 0.2s, background 0.2s',
                                        }}
                                            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                                            onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
                                        >
                                            <td style={{ padding: '1rem', borderRadius: '0.75rem 0 0 0.75rem' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                                    <div style={{
                                                        background: 'rgba(59, 130, 246, 0.1)',
                                                        padding: '0.75rem',
                                                        borderRadius: '0.75rem',
                                                        color: 'var(--accent-color)'
                                                    }}>
                                                        {getDeviceIcon(dev.vendor)}
                                                    </div>
                                                    <div>
                                                        <div style={{ fontWeight: 600 }}>{dev.alias || dev.hostname || 'Desconocido'}</div>
                                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{dev.vendor || 'Fabricante Desconocido'}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td style={{ padding: '1rem' }}>
                                                <div style={{ fontSize: '0.875rem' }}><code>{dev.ip}</code></div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}><code>{dev.mac}</code></div>
                                            </td>
                                            <td style={{ padding: '1rem', textAlign: 'center' }}>
                                                <div style={{
                                                    fontSize: '1.25rem',
                                                    fontWeight: 700,
                                                    color: 'var(--success)',
                                                    fontFamily: 'monospace'
                                                }}>
                                                    {formatDuration(duration)}
                                                </div>
                                                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                                                    en la red actualmente
                                                </div>
                                            </td>
                                            <td style={{ padding: '1rem', textAlign: 'center', borderRadius: '0 0.75rem 0.75rem 0' }}>
                                                <span className="badge badge-online" style={{ padding: '0.5rem 1rem' }}>
                                                    <Wifi size={14} style={{ marginRight: '0.5rem' }} /> Online
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })
                            ) : (
                                <tr>
                                    <td colSpan="4" style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                                            <WifiOff size={48} opacity={0.3} />
                                            {searchTerm ? 'No se encontraron dispositivos con ese criterio' : 'No hay dispositivos detectados actualmente'}
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Footer Info */}
                <div style={{
                    padding: '1rem 2rem',
                    background: 'rgba(59, 130, 246, 0.05)',
                    borderTop: '1px solid var(--border-color)',
                    fontSize: '0.8125rem',
                    color: 'var(--text-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)', boxShadow: '0 0 10px var(--success)' }}></div>
                    Actualizando detecciones en tiempo real. Los dispositivos que se desconectan desaparecen de esta lista.
                </div>
            </div>
        </div>
    );
};

export default DeviceDetectionList;
