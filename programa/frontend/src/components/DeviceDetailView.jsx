import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MetricLineChart, MetricAreaChart, StatCard, GaugeChart } from './Charts';
import { X, Activity, TrendingUp, TrendingDown, Wifi, WifiOff } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

/**
 * Vista detallada de un dispositivo con todas sus métricas y gráficos
 */
const DeviceDetailView = ({ device, onClose }) => {
    const [metrics, setMetrics] = useState([]);
    const [summary, setSummary] = useState(null);
    const [sensors, setSensors] = useState([]);
    const [timeRange, setTimeRange] = useState(24); // horas
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (device) {
            fetchDeviceData();
        }
    }, [device, timeRange]);

    const fetchDeviceData = async () => {
        setLoading(true);
        try {
            const [metricsRes, summaryRes, sensorsRes] = await Promise.all([
                axios.get(`${API_BASE}/metrics/device/${device.id}?hours=${timeRange}`),
                axios.get(`${API_BASE}/metrics/summary/${device.id}`),
                axios.get(`${API_BASE}/sensors?device_id=${device.id}`)
            ]);

            setMetrics(metricsRes.data.data || []);
            setSummary(summaryRes.data.summary || []);
            setSensors(sensorsRes.data || []);
        } catch (err) {
            console.error('Error fetching device data:', err);
        } finally {
            setLoading(false);
        }
    };

    const toggleSensor = async (sensorId) => {
        try {
            await axios.put(`${API_BASE}/sensors/${sensorId}/toggle`);
            fetchDeviceData();
        } catch (err) {
            console.error('Error toggling sensor:', err);
        }
    };

    if (!device) return null;

    // Agrupar métricas por tipo
    const metricsByType = metrics.reduce((acc, metric) => {
        if (!acc[metric.metric_name]) {
            acc[metric.metric_name] = [];
        }
        acc[metric.metric_name].push(metric);
        return acc;
    }, {});

    // Obtener métrica de latencia para el gráfico principal
    const latencyData = metricsByType['ping_latency'] || [];
    const packetLossData = metricsByType['ping_packet_loss'] || [];

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
                maxWidth: '1400px',
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
                    <div>
                        <h2 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            {device.status === 'Online' ? <Wifi color="var(--success)" /> : <WifiOff color="var(--danger)" />}
                            {device.alias || device.hostname || device.ip}
                        </h2>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                            {device.ip} • {device.mac} • {device.vendor}
                        </div>
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

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                        <Activity size={48} style={{ animation: 'spin 1s linear infinite' }} />
                        <p style={{ marginTop: '1rem' }}>Cargando métricas...</p>
                    </div>
                ) : (
                    <>
                        {/* Time Range Selector */}
                        <div style={{ marginBottom: '2rem', display: 'flex', gap: '0.5rem' }}>
                            {[1, 6, 12, 24, 48, 168].map(hours => (
                                <button
                                    key={hours}
                                    onClick={() => setTimeRange(hours)}
                                    style={{
                                        padding: '0.5rem 1rem',
                                        background: timeRange === hours ? 'var(--accent-color)' : 'transparent',
                                        border: '1px solid var(--border-color)',
                                        borderRadius: '0.5rem',
                                        color: 'white',
                                        cursor: 'pointer',
                                        fontSize: '0.875rem'
                                    }}
                                >
                                    {hours < 24 ? `${hours}h` : `${hours / 24}d`}
                                </button>
                            ))}
                        </div>

                        {/* Summary Stats */}
                        {summary && summary.length > 0 && (
                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                                gap: '1rem',
                                marginBottom: '2rem'
                            }}>
                                {summary.map((stat, idx) => (
                                    <StatCard
                                        key={idx}
                                        label={stat.metric_name.replace(/_/g, ' ')}
                                        value={stat.avg}
                                        unit={stat.metric_name.includes('latency') ? 'ms' : stat.metric_name.includes('loss') ? '%' : ''}
                                        color={
                                            stat.metric_name.includes('latency') && stat.avg < 50 ? 'var(--success)' :
                                                stat.metric_name.includes('latency') && stat.avg < 100 ? 'var(--warning)' :
                                                    stat.metric_name.includes('latency') ? 'var(--danger)' : 'var(--accent-color)'
                                        }
                                    />
                                ))}
                            </div>
                        )}

                        {/* Main Charts */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
                            {latencyData.length > 0 && (
                                <MetricLineChart
                                    data={latencyData}
                                    dataKey="value"
                                    color="var(--accent-color)"
                                    title="Latencia de Ping (ms)"
                                />
                            )}
                            {packetLossData.length > 0 && (
                                <MetricAreaChart
                                    data={packetLossData}
                                    dataKey="value"
                                    color="var(--danger)"
                                    title="Packet Loss (%)"
                                />
                            )}
                        </div>

                        {/* Otros gráficos */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
                            {Object.entries(metricsByType).map(([metricName, data]) => {
                                if (metricName === 'ping_latency' || metricName === 'ping_packet_loss') return null;
                                return (
                                    <MetricLineChart
                                        key={metricName}
                                        data={data}
                                        dataKey="value"
                                        title={metricName.replace(/_/g, ' ')}
                                    />
                                );
                            })}
                        </div>

                        {/* Sensors List */}
                        {sensors.length > 0 && (
                            <div style={{ marginTop: '2rem' }}>
                                <h3 style={{ marginBottom: '1rem' }}>Sensores Activos</h3>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                    {sensors.map(sensor => (
                                        <div
                                            key={sensor.id}
                                            style={{
                                                background: 'rgba(255,255,255,0.05)',
                                                padding: '1rem',
                                                borderRadius: '0.75rem',
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                alignItems: 'center'
                                            }}
                                        >
                                            <div>
                                                <div style={{ fontWeight: 500 }}>{sensor.name}</div>
                                                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                                    {sensor.sensor_type} • Intervalo: {sensor.interval}s
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => toggleSensor(sensor.id)}
                                                style={{
                                                    padding: '0.5rem 1rem',
                                                    background: sensor.enabled ? 'var(--success)' : 'var(--border-color)',
                                                    border: 'none',
                                                    borderRadius: '0.5rem',
                                                    color: 'white',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                {sensor.enabled ? 'Activo' : 'Inactivo'}
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {metrics.length === 0 && (
                            <div style={{
                                textAlign: 'center',
                                padding: '4rem',
                                color: 'var(--text-secondary)'
                            }}>
                                <Activity size={48} />
                                <p style={{ marginTop: '1rem' }}>No hay métricas disponibles aún</p>
                                <p style={{ fontSize: '0.875rem' }}>Las métricas comenzarán a recolectarse automáticamente</p>
                            </div>
                        )}
                    </>
                )}
            </div>

            <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
};

export default DeviceDetailView;
