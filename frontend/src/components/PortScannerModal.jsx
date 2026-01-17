import React, { useState } from 'react';
import axios from 'axios';
import { X, Wifi, Search, Play, Loader } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const COMMON_PORT_RANGES = [
    { name: 'Puertos Comunes', value: 'common', description: 'HTTP, HTTPS, SSH, FTP, etc.' },
    { name: 'Rango Completo (1-1024)', value: 'range_1024', start: 1, end: 1024 },
    { name: 'Rango Extendido (1-10000)', value: 'range_10000', start: 1, end: 10000 },
    { name: 'Personalizado', value: 'custom', description: 'Especifica puertos o rango' }
];

/**
 * Modal de escaneo de puertos
 */
const PortScannerModal = ({ devices, onClose, onScanComplete }) => {
    const [selectedDevices, setSelectedDevices] = useState([]);
    const [scanType, setScanType] = useState('common');
    const [customPorts, setCustomPorts] = useState('');
    const [portRangeStart, setPortRangeStart] = useState('1');
    const [portRangeEnd, setPortRangeEnd] = useState('1024');
    const [scanning, setScanning] = useState(false);
    const [results, setResults] = useState(null);

    const handleDeviceToggle = (deviceIp) => {
        setSelectedDevices(prev =>
            prev.includes(deviceIp)
                ? prev.filter(ip => ip !== deviceIp)
                : [...prev, deviceIp]
        );
    };

    const handleSelectAll = () => {
        if (selectedDevices.length === devices.length) {
            setSelectedDevices([]);
        } else {
            setSelectedDevices(devices.map(d => d.ip));
        }
    };

    const handleScan = async () => {
        if (selectedDevices.length === 0) {
            alert('Selecciona al menos un dispositivo');
            return;
        }

        setScanning(true);
        setResults(null);

        try {
            let requestData = {
                ips: selectedDevices,
                scan_type: scanType,
                timeout: 1.0
            };

            if (scanType === 'range_1024') {
                requestData.scan_type = 'range';
                requestData.port_range_start = 1;
                requestData.port_range_end = 1024;
            } else if (scanType === 'range_10000') {
                requestData.scan_type = 'range';
                requestData.port_range_start = 1;
                requestData.port_range_end = 10000;
            } else if (scanType === 'custom') {
                // Parsear puertos personalizados
                const portsStr = customPorts.trim();

                // Si contiene un guión, es un rango
                if (portsStr.includes('-')) {
                    const [start, end] = portsStr.split('-').map(p => parseInt(p.trim()));
                    requestData.scan_type = 'range';
                    requestData.port_range_start = start;
                    requestData.port_range_end = end;
                } else {
                    // Lista de puertos separados por comas
                    const ports = portsStr.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p));
                    requestData.scan_type = 'custom';
                    requestData.custom_ports = ports;
                }
            }

            const response = await axios.post(`${API_BASE}/scan/ports`, requestData);
            setResults(response.data);

            if (onScanComplete) {
                onScanComplete(response.data);
            }
        } catch (error) {
            console.error('Error scanning ports:', error);
            alert('Error al escanear puertos: ' + (error.response?.data?.message || error.message));
        } finally {
            setScanning(false);
        }
    };

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
                maxWidth: '900px',
                width: '100%',
                maxHeight: '90vh',
                overflow: 'auto',
                position: 'relative'
            }}>
                {/* Header */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '2rem',
                    paddingBottom: '1rem',
                    borderBottom: '1px solid var(--border-color)'
                }}>
                    <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <Search size={24} color="var(--accent-color)" />
                        Escáner de Puertos
                    </h2>
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

                {!results ? (
                    <>
                        {/* Selección de dispositivos */}
                        <div style={{ marginBottom: '2rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                <h3>Seleccionar Dispositivos</h3>
                                <button
                                    onClick={handleSelectAll}
                                    style={{
                                        padding: '0.5rem 1rem',
                                        background: 'var(--card-bg)',
                                        border: '1px solid var(--border-color)',
                                        borderRadius: '0.5rem',
                                        color: 'white',
                                        cursor: 'pointer',
                                        fontSize: '0.875rem'
                                    }}
                                >
                                    {selectedDevices.length === devices.length ? 'Deseleccionar Todos' : 'Seleccionar Todos'}
                                </button>
                            </div>

                            <div style={{
                                maxHeight: '200px',
                                overflow: 'auto',
                                background: 'rgba(255,255,255,0.02)',
                                borderRadius: '0.75rem',
                                padding: '1rem'
                            }}>
                                {devices.map(device => (
                                    <label
                                        key={device.ip}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.75rem',
                                            padding: '0.75rem',
                                            cursor: 'pointer',
                                            borderRadius: '0.5rem',
                                            marginBottom: '0.5rem',
                                            background: selectedDevices.includes(device.ip) ? 'rgba(59, 130, 246, 0.1)' : 'transparent'
                                        }}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={selectedDevices.includes(device.ip)}
                                            onChange={() => handleDeviceToggle(device.ip)}
                                            style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                                        />
                                        <Wifi size={16} color={device.status === 'Online' ? 'var(--success)' : 'var(--text-secondary)'} />
                                        <span>{device.alias || device.hostname || 'Desconocido'}</span>
                                        <code style={{ marginLeft: 'auto', fontSize: '0.875rem' }}>{device.ip}</code>
                                    </label>
                                ))}
                            </div>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                                {selectedDevices.length} dispositivo(s) seleccionado(s)
                            </div>
                        </div>

                        {/* Tipo de escaneo */}
                        <div style={{ marginBottom: '2rem' }}>
                            <h3 style={{ marginBottom: '1rem' }}>Tipo de Escaneo</h3>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                {COMMON_PORT_RANGES.map(range => (
                                    <label
                                        key={range.value}
                                        style={{
                                            display: 'flex',
                                            flexDirection: 'column',
                                            padding: '1rem',
                                            background: scanType === range.value ? 'rgba(59, 130, 246, 0.1)' : 'rgba(255,255,255,0.02)',
                                            border: `1px solid ${scanType === range.value ? 'var(--accent-color)' : 'var(--border-color)'}`,
                                            borderRadius: '0.75rem',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s'
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                            <input
                                                type="radio"
                                                name="scanType"
                                                value={range.value}
                                                checked={scanType === range.value}
                                                onChange={(e) => setScanType(e.target.value)}
                                                style={{ cursor: 'pointer' }}
                                            />
                                            <span style={{ fontWeight: 500 }}>{range.name}</span>
                                        </div>
                                        {range.description && (
                                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginLeft: '1.5rem' }}>
                                                {range.description}
                                            </div>
                                        )}
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Puertos personalizados */}
                        {scanType === 'custom' && (
                            <div style={{ marginBottom: '2rem' }}>
                                <h3 style={{ marginBottom: '0.5rem' }}>Puertos Personalizados</h3>
                                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                                    Ingresa puertos separados por comas (ej: 80,443,8080) o un rango (ej: 1-1000)
                                </p>
                                <input
                                    type="text"
                                    value={customPorts}
                                    onChange={(e) => setCustomPorts(e.target.value)}
                                    placeholder="80,443,8080 o 1-1000"
                                    style={{
                                        width: '100%',
                                        padding: '0.75rem',
                                        background: 'rgba(255,255,255,0.05)',
                                        border: '1px solid var(--border-color)',
                                        borderRadius: '0.5rem',
                                        color: 'white',
                                        fontSize: '1rem'
                                    }}
                                />
                            </div>
                        )}

                        {/* Botón de escaneo */}
                        <button
                            onClick={handleScan}
                            disabled={scanning || selectedDevices.length === 0}
                            style={{
                                width: '100%',
                                padding: '1rem',
                                background: scanning ? 'var(--border-color)' : 'var(--accent-color)',
                                border: 'none',
                                borderRadius: '0.75rem',
                                color: 'white',
                                fontSize: '1rem',
                                fontWeight: 600,
                                cursor: scanning ? 'not-allowed' : 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '0.75rem'
                            }}
                        >
                            {scanning ? (
                                <>
                                    <Loader size={20} style={{ animation: 'spin 1s linear infinite' }} />
                                    Escaneando...
                                </>
                            ) : (
                                <>
                                    <Play size={20} />
                                    Iniciar Escaneo
                                </>
                            )}
                        </button>
                    </>
                ) : (
                    /* Resultados */
                    <div>
                        <div style={{
                            padding: '1rem',
                            background: 'rgba(16, 185, 129, 0.1)',
                            border: '1px solid rgba(16, 185, 129, 0.3)',
                            borderRadius: '0.75rem',
                            marginBottom: '2rem'
                        }}>
                            <h3 style={{ color: 'var(--success)', marginBottom: '0.5rem' }}>✓ Escaneo Completado</h3>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                {results.total_ips} dispositivo(s) escaneado(s) • {results.total_open_ports} puerto(s) abierto(s)
                            </div>
                        </div>

                        {Object.entries(results.results).map(([ip, ports]) => {
                            const device = devices.find(d => d.ip === ip);
                            return (
                                <div key={ip} style={{
                                    marginBottom: '1.5rem',
                                    background: 'rgba(255,255,255,0.02)',
                                    borderRadius: '0.75rem',
                                    padding: '1rem'
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                                        <Wifi size={18} color="var(--success)" />
                                        <span style={{ fontWeight: 600 }}>{device?.alias || device?.hostname || 'Desconocido'}</span>
                                        <code style={{ marginLeft: 'auto' }}>{ip}</code>
                                    </div>

                                    {ports.length > 0 ? (
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.5rem' }}>
                                            {ports.map(port => (
                                                <div key={port.port} style={{
                                                    padding: '0.75rem',
                                                    background: 'rgba(16, 185, 129, 0.1)',
                                                    border: '1px solid rgba(16, 185, 129, 0.3)',
                                                    borderRadius: '0.5rem',
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center'
                                                }}>
                                                    <span style={{ fontWeight: 600, color: 'var(--success)' }}>{port.port}</span>
                                                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{port.service}</span>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                                            No se encontraron puertos abiertos
                                        </div>
                                    )}
                                </div>
                            );
                        })}

                        <button
                            onClick={() => setResults(null)}
                            style={{
                                width: '100%',
                                padding: '1rem',
                                background: 'var(--card-bg)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '0.75rem',
                                color: 'white',
                                fontSize: '1rem',
                                fontWeight: 600,
                                cursor: 'pointer'
                            }}
                        >
                            Nuevo Escaneo
                        </button>
                    </div>
                )}

                <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
            </div>
        </div>
    );
};

export default PortScannerModal;
