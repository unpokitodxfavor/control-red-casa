import React, { useState, useEffect } from 'react';
import { X, AlertCircle, AlertTriangle, Info, Bug } from 'lucide-react';

/**
 * AlertNotification - Toast de notificación para alertas
 * Aparece cuando llega una nueva alerta
 */
const AlertNotification = ({ alert, onClose, onAcknowledge, autoClose = true }) => {
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        if (autoClose) {
            const timer = setTimeout(() => {
                handleClose();
            }, 10000); // Auto-cerrar después de 10 segundos

            return () => clearTimeout(timer);
        }
    }, [autoClose]);

    const handleClose = () => {
        setIsVisible(false);
        setTimeout(() => {
            if (onClose) onClose();
        }, 300); // Esperar a que termine la animación
    };

    const handleAcknowledge = () => {
        if (onAcknowledge) {
            onAcknowledge(alert.id);
        }
        handleClose();
    };

    const getLevelIcon = () => {
        switch (alert.level?.toLowerCase()) {
            case 'critical':
                return <AlertCircle size={24} color="#ef4444" />;
            case 'warning':
                return <AlertTriangle size={24} color="#f59e0b" />;
            case 'info':
                return <Info size={24} color="#3b82f6" />;
            case 'debug':
                return <Bug size={24} color="#6b7280" />;
            default:
                return <Info size={24} color="#3b82f6" />;
        }
    };

    const getLevelColor = () => {
        switch (alert.level?.toLowerCase()) {
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

    const getLevelBg = () => {
        switch (alert.level?.toLowerCase()) {
            case 'critical':
                return 'rgba(239, 68, 68, 0.1)';
            case 'warning':
                return 'rgba(245, 158, 11, 0.1)';
            case 'info':
                return 'rgba(59, 130, 246, 0.1)';
            case 'debug':
                return 'rgba(107, 115, 128, 0.1)';
            default:
                return 'rgba(59, 130, 246, 0.1)';
        }
    };

    return (
        <div
            style={{
                position: 'fixed',
                top: '2rem',
                right: isVisible ? '2rem' : '-400px',
                width: '350px',
                background: 'var(--card-bg)',
                backdropFilter: 'var(--glass)',
                border: `2px solid ${getLevelColor()}`,
                borderRadius: '1rem',
                padding: '1rem',
                boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
                zIndex: 9999,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                opacity: isVisible ? 1 : 0
            }}
        >
            {/* Header */}
            <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.75rem',
                marginBottom: '0.75rem'
            }}>
                <div style={{
                    background: getLevelBg(),
                    borderRadius: '0.5rem',
                    padding: '0.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    {getLevelIcon()}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                        fontSize: '0.75rem',
                        fontWeight: 'bold',
                        color: getLevelColor(),
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        marginBottom: '0.25rem'
                    }}>
                        {alert.level} • Nueva Alerta
                    </div>
                    {alert.device_name && (
                        <div style={{
                            fontSize: '0.875rem',
                            color: 'var(--text-secondary)',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                        }}>
                            {alert.device_name}
                            {alert.device_ip && ` (${alert.device_ip})`}
                        </div>
                    )}
                </div>

                <button
                    onClick={handleClose}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        padding: '0.25rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderRadius: '0.25rem',
                        transition: 'background 0.2s'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                    onMouseOut={(e) => e.currentTarget.style.background = 'none'}
                >
                    <X size={18} />
                </button>
            </div>

            {/* Message */}
            <p style={{
                margin: '0 0 1rem 0',
                fontSize: '0.9375rem',
                lineHeight: 1.5,
                color: 'var(--text-primary)'
            }}>
                {alert.message}
            </p>

            {/* Actions */}
            <div style={{
                display: 'flex',
                gap: '0.5rem',
                justifyContent: 'flex-end'
            }}>
                <button
                    onClick={handleClose}
                    style={{
                        background: 'rgba(255,255,255,0.1)',
                        border: 'none',
                        borderRadius: '0.5rem',
                        padding: '0.5rem 1rem',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        transition: 'background 0.2s'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.15)'}
                    onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                >
                    Cerrar
                </button>
                <button
                    onClick={handleAcknowledge}
                    style={{
                        background: getLevelColor(),
                        border: 'none',
                        borderRadius: '0.5rem',
                        padding: '0.5rem 1rem',
                        color: 'white',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        fontWeight: '500',
                        transition: 'opacity 0.2s'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.opacity = '0.9'}
                    onMouseOut={(e) => e.currentTarget.style.opacity = '1'}
                >
                    Reconocer
                </button>
            </div>

            {/* Progress bar (auto-close) */}
            {autoClose && (
                <div style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: '3px',
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: '0 0 1rem 1rem',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        height: '100%',
                        background: getLevelColor(),
                        animation: 'progress 10s linear forwards'
                    }} />
                </div>
            )}

            <style>{`
        @keyframes progress {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
        </div>
    );
};

export default AlertNotification;
