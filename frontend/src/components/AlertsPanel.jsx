import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    AlertCircle,
    AlertTriangle,
    Info,
    Bug,
    X,
    Check,
    Filter,
    Bell,
    BellOff
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

/**
 * AlertsPanel - Panel principal de alertas
 * Muestra alertas activas y permite reconocerlas
 */
const AlertsPanel = ({ onClose }) => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [levelFilter, setLevelFilter] = useState('all');
    const [showAcknowledged, setShowAcknowledged] = useState(false);

    useEffect(() => {
        fetchAlerts();
        // Actualizar cada 10 segundos
        const interval = setInterval(fetchAlerts, 10000);
        return () => clearInterval(interval);
    }, [levelFilter, showAcknowledged]);

    const fetchAlerts = async () => {
        try {
            const params = {};
            if (levelFilter !== 'all') {
                params.level = levelFilter;
            }
            if (showAcknowledged !== null) {
                params.acknowledged = showAcknowledged;
            }

            const response = await axios.get(`${API_BASE}/alerts`, { params });
            // API returns a list directly, or invalid property access was empty
            if (Array.isArray(response.data)) {
                setAlerts(response.data);
            } else {
                setAlerts(response.data.alerts || []);
            }
            setLoading(false);
        } catch (error) {
            console.error('Error fetching alerts:', error);
            setLoading(false);
        }
    };

    const acknowledgeAlert = async (alertId) => {
        try {
            await axios.post(`${API_BASE}/alerts/${alertId}/acknowledge?user=admin`);
            fetchAlerts();
        } catch (error) {
            console.error('Error acknowledging alert:', error);
        }
    };

    const getLevelIcon = (level) => {
        switch (level?.toLowerCase()) {
            case 'critical':
                return <AlertCircle size={20} color="#ef4444" />;
            case 'warning':
                return <AlertTriangle size={20} color="#f59e0b" />;
            case 'info':
                return <Info size={20} color="#3b82f6" />;
            case 'debug':
                return <Bug size={20} color="#6b7280" />;
            default:
                return <Info size={20} color="#3b82f6" />;
        }
    };

    const getLevelColor = (level) => {
        switch (level?.toLowerCase()) {
            case 'critical':
                return '#ef4444';
            case 'warning':
                return '#f59e0b';
            case 'info':
                return '#3b82f6';
            case 'debug':
                return '#6b7280';
            default:
                return '#3b82f6';
        }
    };

    const formatTimestamp = (timestamp) => {
        if (!timestamp) return 'N/A';
        const date = new Date(timestamp);
        return date.toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const activeAlerts = alerts.filter(a => !a.is_acknowledged);
    const acknowledgedAlerts = alerts.filter(a => a.is_acknowledged);

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000,
            backdropFilter: 'blur(4px)',
            padding: '2rem'
        }}>
            <div className="stat-card" style={{
                maxWidth: '1000px',
                width: '100%',
                maxHeight: '80vh',
                overflow: 'hidden',
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
                        <h2 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Bell size={24} />
                            Alertas del Sistema
                        </h2>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            {activeAlerts.length} activas • {acknowledgedAlerts.length} reconocidas
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

                {/* Filters */}
                <div style={{
                    display: 'flex',
                    gap: '1rem',
                    marginBottom: '1.5rem',
                    flexWrap: 'wrap'
                }}>
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <Filter size={16} />
                        <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Nivel:</span>
                        <select
                            value={levelFilter}
                            onChange={(e) => setLevelFilter(e.target.value)}
                            style={{
                                background: 'var(--card-bg)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '0.5rem',
                                padding: '0.5rem',
                                color: 'var(--text-primary)',
                                cursor: 'pointer'
                            }}
                        >
                            <option value="all">Todas</option>
                            <option value="CRITICAL">Críticas</option>
                            <option value="WARNING">Advertencias</option>
                            <option value="INFO">Información</option>
                            <option value="DEBUG">Debug</option>
                        </select>
                    </div>

                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                        <input
                            type="checkbox"
                            checked={showAcknowledged}
                            onChange={(e) => setShowAcknowledged(e.target.checked)}
                        />
                        <span style={{ fontSize: '0.875rem' }}>Mostrar reconocidas</span>
                    </label>
                </div>

                {/* Alerts List */}
                <div style={{
                    flex: 1,
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.75rem'
                }}>
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                            Cargando alertas...
                        </div>
                    ) : alerts.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                            <BellOff size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
                            <p>No hay alertas</p>
                        </div>
                    ) : (
                        alerts.map(alert => (
                            <div
                                key={alert.id}
                                style={{
                                    background: alert.is_acknowledged ? 'rgba(0,0,0,0.2)' : 'var(--card-bg)',
                                    border: `1px solid ${alert.is_acknowledged ? 'var(--border-color)' : getLevelColor(alert.level)}`,
                                    borderRadius: '0.75rem',
                                    padding: '1rem',
                                    display: 'flex',
                                    gap: '1rem',
                                    alignItems: 'flex-start',
                                    opacity: alert.is_acknowledged ? 0.6 : 1,
                                    transition: 'all 0.2s'
                                }}
                            >
                                {/* Icon */}
                                <div style={{ flexShrink: 0, marginTop: '0.25rem' }}>
                                    {getLevelIcon(alert.level)}
                                </div>

                                {/* Content */}
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem',
                                        marginBottom: '0.5rem'
                                    }}>
                                        <span style={{
                                            fontSize: '0.75rem',
                                            fontWeight: 'bold',
                                            color: getLevelColor(alert.level),
                                            textTransform: 'uppercase',
                                            letterSpacing: '0.05em'
                                        }}>
                                            {alert.level}
                                        </span>
                                        {alert.device_name && (
                                            <>
                                                <span style={{ color: 'var(--text-secondary)' }}>•</span>
                                                <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                                    {alert.device_name}
                                                </span>
                                            </>
                                        )}
                                        {alert.device_ip && (
                                            <>
                                                <span style={{ color: 'var(--text-secondary)' }}>•</span>
                                                <code style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                                    {alert.device_ip}
                                                </code>
                                            </>
                                        )}
                                    </div>

                                    <p style={{
                                        margin: '0 0 0.5rem 0',
                                        fontSize: '0.9375rem',
                                        lineHeight: 1.5
                                    }}>
                                        {alert.message}
                                    </p>

                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '1rem',
                                        fontSize: '0.75rem',
                                        color: 'var(--text-secondary)'
                                    }}>
                                        <span>🕐 {formatTimestamp(alert.timestamp)}</span>
                                        {alert.is_acknowledged && (
                                            <>
                                                <span>•</span>
                                                <span>✓ Reconocida por {alert.acknowledged_by}</span>
                                            </>
                                        )}
                                    </div>
                                </div>

                                {/* Actions */}
                                {!alert.is_acknowledged && (
                                    <button
                                        onClick={() => acknowledgeAlert(alert.id)}
                                        style={{
                                            background: 'var(--accent-color)',
                                            border: 'none',
                                            borderRadius: '0.5rem',
                                            padding: '0.5rem 1rem',
                                            color: 'white',
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.5rem',
                                            fontSize: '0.875rem',
                                            transition: 'background 0.2s'
                                        }}
                                        onMouseOver={(e) => e.currentTarget.style.background = 'var(--accent-hover)'}
                                        onMouseOut={(e) => e.currentTarget.style.background = 'var(--accent-color)'}
                                    >
                                        <Check size={16} />
                                        Reconocer
                                    </button>
                                )}
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                <div style={{
                    marginTop: '1.5rem',
                    paddingTop: '1rem',
                    borderTop: '1px solid var(--border-color)',
                    fontSize: '0.875rem',
                    color: 'var(--text-secondary)',
                    textAlign: 'center'
                }}>
                    Las alertas se actualizan automáticamente cada 10 segundos
                </div>
            </div>
        </div>
    );
};

export default AlertsPanel;
