import React from 'react';
import { GripVertical } from 'lucide-react';

const DashboardWidget = ({ title, children, style, className, isEditMode, ...props }) => {
    return (
        <div
            style={{
                width: '100%',
                height: '100%',
                background: 'var(--card-bg)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.75rem',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                transition: 'border-color 0.2s',
                ...style
            }}
            className={`${className} ${isEditMode ? 'widget-editable' : ''}`}
            {...props}
        >
            {/* Header */}
            <div style={{
                padding: '0.75rem 1rem',
                borderBottom: '1px solid var(--border-color)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'rgba(255,255,255,0.02)'
            }}>
                <h3 style={{ margin: 0, fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    {title}
                </h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {isEditMode && props.onRemove && (
                        <button
                            onClick={(e) => { e.stopPropagation(); props.onRemove(); }}
                            style={{
                                cursor: 'pointer',
                                padding: '0.25rem',
                                borderRadius: '0.25rem',
                                background: 'rgba(239, 68, 68, 0.2)',
                                border: 'none',
                                color: '#ef4444',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                            title="Ocultar Widget"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                        </button>
                    )}
                    {isEditMode && (
                        <div className="drag-handle" style={{ cursor: 'grab', padding: '0.25rem', borderRadius: '0.25rem', background: 'rgba(255,255,255,0.1)' }}>
                            <GripVertical size={16} />
                        </div>
                    )}
                </div>
            </div>

            {/* Content */}
            <div style={{ flex: 1, overflow: 'auto', position: 'relative' }}>
                {children}
            </div>
        </div>
    );
};

export default DashboardWidget;
