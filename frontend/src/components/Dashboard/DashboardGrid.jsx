import React, { useState, useEffect, useRef } from 'react';
import GridLayout from 'react-grid-layout';
import axios from 'axios';
import { API_BASE } from '../../config';
import DashboardWidget from './DashboardWidget';
import StatsWidget from '../Widgets/StatsWidget';
import DeviceListWidget from '../Widgets/DeviceListWidget';
import AlertsWidget from '../Widgets/AlertsWidget';
import RouterStatsWidget from '../Widgets/RouterStatsWidget';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { Save, Edit2, X, RotateCcw, Plus } from 'lucide-react';

const ALL_WIDGETS = [
    { id: 'router', title: 'Estado del Router' },
    { id: 'stats', title: 'Estadísticas Generales' },
    { id: 'devices', title: 'Dispositivos Recientes' },
    { id: 'alerts', title: 'Últimas Alertas' }
];

const DEFAULT_LAYOUT = [
    { i: 'router', x: 0, y: 0, w: 12, h: 4 },
    { i: 'stats', x: 0, y: 4, w: 12, h: 3 }, // Taller default
    { i: 'devices', x: 0, y: 7, w: 8, h: 8 }, // Taller default
    { i: 'alerts', x: 8, y: 7, w: 4, h: 8 }   // Taller default
];

const DashboardGrid = ({ devices, stats, alerts, onNavigate }) => {
    const [isEditMode, setIsEditMode] = useState(false);
    const [showWidgetMenu, setShowWidgetMenu] = useState(false);
    const [visibleWidgets, setVisibleWidgets] = useState(['router', 'stats', 'devices', 'alerts']);
    const [layout, setLayout] = useState(DEFAULT_LAYOUT);

    // Dynamic Width State
    const [width, setWidth] = useState(1280);
    const containerRef = useRef(null);

    // Resize Observer for Full Width
    useEffect(() => {
        if (!containerRef.current) return;

        const observer = new ResizeObserver((entries) => {
            for (let entry of entries) {
                if (entry.contentRect.width > 0) {
                    setWidth(entry.contentRect.width);
                }
            }
        });

        observer.observe(containerRef.current);

        // Initial width set
        if (containerRef.current.offsetWidth > 0) {
            setWidth(containerRef.current.offsetWidth);
        }

        return () => observer.disconnect();
    }, []);

    useEffect(() => {
        loadLayout();
    }, []);

    const loadLayout = async () => {
        try {
            const res = await axios.get(`${API_BASE}/config/dashboard`);
            let loaded = null;

            if (res.data.layout) {
                if (Array.isArray(res.data.layout)) {
                    loaded = res.data.layout;
                } else {
                    loaded = res.data.layout.layout || null;
                    if (res.data.layout.visible_widgets) {
                        setVisibleWidgets(res.data.layout.visible_widgets);
                    }
                }
            }

            // AUTO-UPGRADE LOGIC
            // If the user has an old layout with small widgets, upgrade them automatically.
            if (loaded && loaded.length > 0) {
                const isCorrupted = loaded.some(item => item.w < 2 || item.h < 2);

                if (isCorrupted) {
                    console.warn("Detected corrupted layout. Resetting.");
                    setLayout(DEFAULT_LAYOUT);
                    setVisibleWidgets(['router', 'stats', 'devices', 'alerts']);
                } else {
                    // Upgrade existing items to new minimum heights
                    const upgradedLayout = loaded.map(item => {
                        if (item.i === 'stats' && item.h < 3) return { ...item, h: 3 };
                        if ((item.i === 'devices' || item.i === 'alerts') && item.h < 8) return { ...item, h: 8 };
                        return item;
                    });
                    setLayout(upgradedLayout);
                }
            }
        } catch (error) {
            console.error("Failed to load layout", error);
        }
    };

    const saveLayout = async () => {
        try {
            await axios.post(`${API_BASE}/config/dashboard`, {
                layout: layout,
                visible_widgets: visibleWidgets
            });
            setIsEditMode(false);
            setShowWidgetMenu(false);
        } catch (error) {
            console.error("Failed to save layout", error);
        }
    };

    const onLayoutChange = (newLayout) => {
        setLayout(newLayout);
    };

    const resetLayout = () => {
        setLayout(DEFAULT_LAYOUT);
        setVisibleWidgets(['router', 'stats', 'devices', 'alerts']);
    };

    const toggleWidget = (widgetId) => {
        if (visibleWidgets.includes(widgetId)) {
            setVisibleWidgets(visibleWidgets.filter(id => id !== widgetId));
        } else {
            setVisibleWidgets([...visibleWidgets, widgetId]);
        }
    };

    return (
        <div
            ref={containerRef}
            className="dashboard-grid-container"
            style={{ width: '100%', minHeight: '100vh', paddingBottom: '50px' }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ margin: 0 }}>Dashboard</h2>

                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    {isEditMode && (
                        <div style={{ position: 'relative' }}>
                            <button
                                onClick={() => setShowWidgetMenu(!showWidgetMenu)}
                                className="btn-secondary"
                                style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                            >
                                <Plus size={16} /> Widgets ({visibleWidgets.length}/{ALL_WIDGETS.length})
                            </button>
                            {showWidgetMenu && (
                                <div style={{
                                    position: 'absolute',
                                    top: '100%',
                                    right: 0,
                                    marginTop: '0.5rem',
                                    background: 'var(--card-bg)',
                                    border: '1px solid var(--border-color)',
                                    borderRadius: '0.5rem',
                                    padding: '0.5rem',
                                    zIndex: 100,
                                    minWidth: '200px',
                                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                                }}>
                                    {ALL_WIDGETS.map(w => (
                                        <div
                                            key={w.id}
                                            onClick={() => toggleWidget(w.id)}
                                            style={{
                                                padding: '0.5rem',
                                                cursor: 'pointer',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '0.5rem',
                                                opacity: visibleWidgets.includes(w.id) ? 1 : 0.5
                                            }}
                                        >
                                            <div style={{
                                                width: '16px',
                                                height: '16px',
                                                borderRadius: '4px',
                                                border: '1px solid currentColor',
                                                background: visibleWidgets.includes(w.id) ? 'currentColor' : 'transparent'
                                            }}></div>
                                            <span>{w.title}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {isEditMode ? (
                        <>
                            <button onClick={resetLayout} className="btn-secondary" style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <RotateCcw size={16} /> Reset
                            </button>
                            <button onClick={() => setIsEditMode(false)} className="btn-secondary" style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <X size={16} /> Cancelar
                            </button>
                            <button onClick={saveLayout} className="btn-primary" style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Save size={16} /> Guardar
                            </button>
                        </>
                    ) : (
                        <button onClick={() => setIsEditMode(true)} className="btn-secondary" style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Edit2 size={16} /> Personalizar
                        </button>
                    )}
                </div>
            </div>

            <GridLayout
                className="layout"
                layout={layout}
                cols={12}
                rowHeight={60}
                width={width}
                onLayoutChange={onLayoutChange}
                isDraggable={isEditMode}
                isResizable={isEditMode}
                draggableHandle=".drag-handle"
                margin={[16, 16]}
                useCSSTransforms={true}
            >
                {visibleWidgets.includes('router') && (
                    <div key="router">
                        <DashboardWidget
                            title="Estado del Router (Asus RT-AC65P)"
                            isEditMode={isEditMode}
                            onRemove={() => toggleWidget('router')}
                        >
                            <RouterStatsWidget />
                        </DashboardWidget>
                    </div>
                )}

                {visibleWidgets.includes('stats') && (
                    <div key="stats">
                        <DashboardWidget
                            title="Estadísticas Generales"
                            isEditMode={isEditMode}
                            onRemove={() => toggleWidget('stats')}
                        >
                            <StatsWidget stats={stats} />
                        </DashboardWidget>
                    </div>
                )}

                {visibleWidgets.includes('devices') && (
                    <div key="devices">
                        <DashboardWidget
                            title="Dispositivos Recientes"
                            isEditMode={isEditMode}
                            onRemove={() => toggleWidget('devices')}
                        >
                            <DeviceListWidget devices={devices} onNavigate={onNavigate} />
                        </DashboardWidget>
                    </div>
                )}

                {visibleWidgets.includes('alerts') && (
                    <div key="alerts">
                        <DashboardWidget
                            title="Últimas Alertas"
                            isEditMode={isEditMode}
                            onRemove={() => toggleWidget('alerts')}
                        >
                            <AlertsWidget alerts={alerts} />
                        </DashboardWidget>
                    </div>
                )}
            </GridLayout>

            <style>{`
        .react-grid-item.react-grid-placeholder {
          background: rgba(59, 130, 246, 0.2) !important;
          border-radius: 0.75rem !important;
          opacity: 0.5;
        }
        .widget-editable {
          border: 1px dashed var(--accent-color) !important;
        }
      `}</style>
        </div>
    );
};

export default DashboardGrid;
