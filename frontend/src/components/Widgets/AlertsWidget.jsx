import React from 'react';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';

const AlertsWidget = ({ alerts = [] }) => {
    const recentAlerts = alerts.slice(0, 10);

    const getIcon = (type) => {
        if (type === 'NEW_DEVICE') return <AlertCircle size={16} className="text-accent" />;
        if (type === 'DEVICE_OFFLINE') return <Info size={16} className="text-danger" />;
        return <Info size={16} className="text-secondary" />;
    };

    return (
        <div className="no-scrollbar" style={{ overflow: 'auto', height: '100%', padding: '0.5rem' }}>
            {recentAlerts.length === 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)', opacity: 0.7 }}>
                    <CheckCircle size={32} style={{ marginBottom: '0.5rem' }} />
                    <p>Sin alertas recientes</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {recentAlerts.map(alert => (
                        <div key={alert.id} style={{
                            background: 'rgba(255,255,255,0.03)',
                            borderRadius: '0.5rem',
                            padding: '0.75rem',
                            display: 'flex',
                            gap: '0.75rem',
                            alignItems: 'start',
                            borderLeft: `3px solid ${alert.type === 'NEW_DEVICE' ? 'var(--accent-color)' : 'var(--danger)'}`
                        }}>
                            <div style={{ marginTop: '2px' }}>
                                {getIcon(alert.type)}
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                    <strong style={{ fontSize: '0.8rem' }}>{alert.type}</strong>
                                    <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                                        {new Date(alert.timestamp).toLocaleTimeString()}
                                    </span>
                                </div>
                                <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                                    {alert.message}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AlertsWidget;
