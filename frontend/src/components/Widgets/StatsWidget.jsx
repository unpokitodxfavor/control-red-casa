import React from 'react';

const StatsWidget = ({ stats }) => {
    return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', padding: '1rem', height: '100%' }}>
            <div className="stat-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '0.5rem' }}>
                <span className="stat-label">Total</span>
                <span className="stat-value">{stats.total || 0}</span>
            </div>
            <div className="stat-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '0.5rem' }}>
                <span className="stat-label">En Línea</span>
                <span className="stat-value" style={{ color: 'var(--success)' }}>{stats.online || 0}</span>
            </div>
            <div className="stat-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '0.5rem' }}>
                <span className="stat-label">Nuevos</span>
                <span className="stat-value" style={{ color: 'var(--accent-color)' }}>{stats.new_today || 0}</span>
            </div>
        </div>
    );
};

export default StatsWidget;
