import React from 'react';
import { Smartphone, Laptop, Printer, Eye } from 'lucide-react';

const DeviceListWidget = ({ devices = [], onNavigate }) => {
    const recentDevices = devices.slice(0, 10); // Limit to 10 for widget

    const getDeviceIcon = (vendor) => {
        const v = (vendor || '').toLowerCase();
        if (v.includes('apple') || v.includes('sumsung') || v.includes('mobile')) return <Smartphone size={16} />;
        if (v.includes('hp') || v.includes('canon') || v.includes('printer')) return <Printer size={16} />;
        return <Laptop size={16} />;
    };

    return (
        <div style={{ overflow: 'auto', height: '100%' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                <thead style={{ position: 'sticky', top: 0, background: 'var(--card-bg)', zIndex: 1 }}>
                    <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border-color)' }}>
                        <th style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>E</th>
                        <th style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>Dispositivo</th>
                        <th style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>IP</th>
                        <th style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}></th>
                    </tr>
                </thead>
                <tbody>
                    {recentDevices.map(dev => (
                        <tr key={dev.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                            <td style={{ padding: '0.5rem 0.75rem' }}>
                                <span style={{
                                    display: 'inline-block',
                                    width: '8px',
                                    height: '8px',
                                    borderRadius: '50%',
                                    background: dev.status === 'Online' ? 'var(--success)' : 'var(--danger)'
                                }} />
                            </td>
                            <td style={{ padding: '0.5rem 0.75rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    {getDeviceIcon(dev.vendor)}
                                    <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '120px' }}>
                                        {dev.alias || dev.hostname || 'Unknown'}
                                    </span>
                                </div>
                            </td>
                            <td style={{ padding: '0.5rem 0.75rem', fontFamily: 'monospace' }}>{dev.ip}</td>
                            <td style={{ padding: '0.5rem 0.75rem', textAlign: 'right' }}>
                                <button
                                    onClick={() => onNavigate && onNavigate('devices')}
                                    style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
                                >
                                    <Eye size={14} />
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default DeviceListWidget;
