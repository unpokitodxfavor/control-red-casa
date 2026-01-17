import React, { useState, useEffect } from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import axios from 'axios';
import { API_BASE } from '../../config';
import DashboardWidget from './DashboardWidget';
import StatsWidget from '../Widgets/StatsWidget';
import DeviceListWidget from '../Widgets/DeviceListWidget';
import AlertsWidget from '../Widgets/AlertsWidget';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { Save, Edit2, X, RotateCcw } from 'lucide-react';

const ResponsiveGridLayout = WidthProvider(Responsive);

const DashboardGrid = ({ devices, stats, alerts, onNavigate }) => {
    const [isEditMode, setIsEditMode] = useState(false);
    const [layouts, setLayouts] = useState({
        lg: [
            { i: 'stats', x: 0, y: 0, w: 12, h: 2 },
            { i: 'devices', x: 0, y: 2, w: 8, h: 8 },
            { i: 'alerts', x: 8, y: 2, w: 4, h: 8 }
        ]
    });

    useEffect(() => {
        loadLayout();
    }, []);

    const loadLayout = async () => {
        try {
            const res = await axios.get(`${API_BASE}/config/dashboard`);
            if (res.data.layout) {
                // Simple logic: If we find 'map' in saved layout, we should probably ignore it or mapped it to 'alerts'
                // For now, let's just use the saved layout. If user had 'map', it will show empty unless we handle it.
                // Better: Check if 'alerts' exists in layout. If not (migration), fallback to default.
                const hasAlerts = res.data.layout.find(item => item.i === 'alerts');
                if (hasAlerts) {
                    setLayouts({ lg: res.data.layout });
                } else {
                    // Fallback / Migration: Use default if no alerts widget found
                    console.log("Migrating layout to include alerts...");
                }
            }
        } catch (error) {
            console.error("Failed to load layout", error);
        }
    };

    const saveLayout = async () => {
        try {
            await axios.post(`${API_BASE}/config/dashboard`, { layout: layouts.lg });
            setIsEditMode(false);
        } catch (error) {
            console.error("Failed to save layout", error);
        }
    };

    const onLayoutChange = (currentLayout, allLayouts) => {
        setLayouts({ lg: currentLayout });
    };

    const resetLayout = () => {
        setLayouts({
            lg: [
                { i: 'stats', x: 0, y: 0, w: 12, h: 2 },
                { i: 'devices', x: 0, y: 2, w: 8, h: 8 },
                { i: 'alerts', x: 8, y: 2, w: 4, h: 8 }
            ]
        });
    };

    return (
        <div className="dashboard-grid-container">
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem', gap: '0.5rem' }}>
                {isEditMode ? (
                    <>
                        <button onClick={resetLayout} className="btn-secondary" style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <RotateCcw size={16} /> Reset
                        </button>
                        <button onClick={() => setIsEditMode(false)} className="btn-secondary" style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <X size={16} /> Cancelar
                        </button>
                        <button onClick={saveLayout} className="btn-primary" style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Save size={16} /> Guardar Cambios
                        </button>
                    </>
                ) : (
                    <button onClick={() => setIsEditMode(true)} className="btn-secondary" style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Edit2 size={16} /> Personalizar Dashboard
                    </button>
                )}
            </div>

            <ResponsiveGridLayout
                className="layout"
                layouts={layouts}
                breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
                cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
                rowHeight={60}
                onLayoutChange={onLayoutChange}
                isDraggable={isEditMode}
                isResizable={isEditMode}
                draggableHandle=".drag-handle"
                margin={[16, 16]}
            >
                <div key="stats">
                    <DashboardWidget title="Estadísticas Generales" isEditMode={isEditMode}>
                        <StatsWidget stats={stats} />
                    </DashboardWidget>
                </div>

                <div key="devices">
                    <DashboardWidget title="Dispositivos Recientes" isEditMode={isEditMode}>
                        <DeviceListWidget devices={devices} onNavigate={onNavigate} />
                    </DashboardWidget>
                </div>

                <div key="alerts">
                    <DashboardWidget title="Últimas Alertas" isEditMode={isEditMode}>
                        <AlertsWidget alerts={alerts} />
                    </DashboardWidget>
                </div>
            </ResponsiveGridLayout>

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
