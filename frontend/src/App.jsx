import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DeviceDetailView from './components/DeviceDetailView';
import PortScannerModal from './components/PortScannerModal';
import DeviceDetectionList from './components/DeviceDetectionList';
import AlertsPanel from './components/AlertsPanel';
import AlertNotification from './components/AlertNotification';
import TelegramSettings from './components/TelegramSettings';
import DashboardGrid from './components/Dashboard/DashboardGrid';
import {
  Activity,
  Shield,
  Settings,
  Smartphone,
  Laptop,
  Printer,
  Wifi,
  AlertCircle,
  Bell,
  Search,
  Filter,
  X,
  Target,
  Edit2,
  Check,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Download,
  Upload,
  Lock,
  Unlock,
  Eye,
  Scan,
  Sun,
  Moon,
  Network
} from 'lucide-react';

import { API_BASE } from './config';

function App() {
  const [devices, setDevices] = useState([]);
  const [stats, setStats] = useState({ total: 0, online: 0, new_today: 0 });
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // 'all', 'online', 'offline'
  const [newDeviceAlert, setNewDeviceAlert] = useState(null);
  const [editingMac, setEditingMac] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [sortField, setSortField] = useState(null); // 'ip', 'hostname', 'mac', 'vendor', 'last_seen'
  const [sortDirection, setSortDirection] = useState('asc'); // 'asc' or 'desc'
  const [selectedDevice, setSelectedDevice] = useState(null); // Para vista detallada
  const [showPortScanner, setShowPortScanner] = useState(false); // Para modal de escaneo de puertos
  const [showNetworkMap, setShowNetworkMap] = useState(false); // Para mapa de red
  const [showAlertsPanel, setShowAlertsPanel] = useState(false); // Para panel de alertas
  const [activeAlerts, setActiveAlerts] = useState([]); // Alertas activas
  const [alertNotifications, setAlertNotifications] = useState([]); // Notificaciones toast
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('netguard-theme');
    return saved || 'dark';
  });
  const [config, setConfig] = useState(() => {
    const saved = localStorage.getItem('netguard-config');
    return saved ? JSON.parse(saved) : {
      autoRefresh: true,
      refreshInterval: 30,
      showNotifications: true,
      soundAlerts: false
    };
  });

  // Aplicar tema al documento
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('netguard-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const fetchData = async () => {
    try {
      const [devRes, statRes, alertRes] = await Promise.all([
        axios.get(`${API_BASE}/devices`),
        axios.get(`${API_BASE}/status`),
        axios.get(`${API_BASE}/alerts`)
      ]);

      // Detection of new device for Modal (using MAC comparison)
      if (devices.length > 0) {
        const existingMacs = new Set(devices.map(d => d.mac));
        const newlyFound = devRes.data.find(d => !existingMacs.has(d.mac));
        if (newlyFound) {
          setNewDeviceAlert(newlyFound);
        }
      }

      setDevices(Array.isArray(devRes.data) ? devRes.data : []);
      setStats(statRes.data || { total: 0, online: 0, new_today: 0 });
      setAlerts(Array.isArray(alertRes.data) ? alertRes.data : []);
    } catch (err) {
      console.error('Failed to fetch data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    if (config.autoRefresh) {
      const interval = setInterval(fetchData, config.refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [config.autoRefresh, config.refreshInterval]);

  // Polling de alertas activas
  useEffect(() => {
    const fetchActiveAlerts = async () => {
      try {
        const response = await axios.get(`${API_BASE}/alerts/active`);
        const newAlerts = response.data.alerts || [];

        // Detectar nuevas alertas para mostrar notificación
        if (config.showNotifications) {
          newAlerts.forEach(alert => {
            const isNew = !activeAlerts.find(a => a.id === alert.id);
            if (isNew && alert.level !== 'DEBUG') {
              // Añadir notificación toast
              setAlertNotifications(prev => [...prev, alert]);
            }
          });
        }

        setActiveAlerts(newAlerts);
      } catch (error) {
        console.error('Error fetching active alerts:', error);
      }
    };

    fetchActiveAlerts();
    const interval = setInterval(fetchActiveAlerts, 10000); // Cada 10 segundos
    return () => clearInterval(interval);
  }, [config.showNotifications, activeAlerts.length]);

  const acknowledgeAlert = async (alertId) => {
    try {
      await axios.post(`${API_BASE}/alerts/${alertId}/acknowledge?user=admin`);
      // Remover de notificaciones
      setAlertNotifications(prev => prev.filter(a => a.id !== alertId));
      // Actualizar alertas activas
      setActiveAlerts(prev => prev.filter(a => a.id !== alertId));
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const removeNotification = (alertId) => {
    setAlertNotifications(prev => prev.filter(a => a.id !== alertId));
  };

  const handleUpdateAlias = async (mac, newAlias) => {
    try {
      await axios.put(`${API_BASE}/devices/${mac}/alias`, { alias: newAlias });
      setEditingMac(null);
      fetchData(); // Refresh list
    } catch (err) {
      console.error('Failed to update alias', err);
    }
  };

  const handleToggleAuthorization = async (deviceId, currentStatus) => {
    try {
      await axios.put(`${API_BASE}/devices/${deviceId}`, {
        is_authorized: !currentStatus
      });
      fetchData();
    } catch (err) {
      console.error('Failed to toggle authorization', err);
    }
  };

  const handleReidentifyDevices = async () => {
    try {
      const response = await axios.post(`${API_BASE}/devices/reidentify`);
      alert(response.data.message);
      fetchData();
    } catch (err) {
      console.error('Failed to reidentify devices', err);
    }
  };

  const exportToCSV = () => {
    const headers = ['Estado', 'Nombre', 'IP', 'MAC', 'Fabricante', 'Tipo', 'Última Vez'];
    const rows = filteredDevices.map(d => [
      d.status,
      d.alias || d.hostname || 'Desconocido',
      d.ip,
      d.mac,
      d.vendor || 'Desconocido',
      d.device_type || 'Unknown',
      new Date(d.last_seen).toLocaleString()
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `dispositivos_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const exportToJSON = () => {
    const data = filteredDevices.map(d => ({
      status: d.status,
      nombre: d.alias || d.hostname || 'Desconocido',
      ip: d.ip,
      mac: d.mac,
      fabricante: d.vendor || 'Desconocido',
      tipo: d.device_type || 'Unknown',
      ultima_vez: d.last_seen,
      autorizado: d.is_authorized
    }));

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `dispositivos_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  };

  const getDeviceIcon = (vendor) => {
    const v = vendor.toLowerCase();
    if (v.includes('apple') || v.includes('sumsung') || v.includes('mobile')) return <Smartphone size={18} />;
    if (v.includes('hp') || v.includes('canon') || v.includes('printer')) return <Printer size={18} />;
    return <Laptop size={18} />;
  };

  const handleSort = (field) => {
    if (sortField === field) {
      // Toggle direction if clicking same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to ascending
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const parseIP = (ip) => {
    // Convert IP to number for proper sorting (e.g., 192.168.1.10 comes before 192.168.1.100)
    if (!ip) return 0;
    const parts = ip.split('.').map(Number);
    return (parts[0] * 16777216) + (parts[1] * 65536) + (parts[2] * 256) + parts[3];
  };

  const filteredDevices = devices
    .filter(d => {
      const matchesSearch = d.hostname?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        d.ip?.includes(searchTerm) ||
        d.mac?.includes(searchTerm.toLowerCase());

      const matchesStatus = statusFilter === 'all' ||
        (statusFilter === 'online' && d.status.toLowerCase() === 'online') ||
        (statusFilter === 'offline' && d.status.toLowerCase() === 'offline');

      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      if (!sortField) return 0;

      let aVal, bVal;

      switch (sortField) {
        case 'ip':
          aVal = parseIP(a.ip);
          bVal = parseIP(b.ip);
          break;
        case 'hostname':
          aVal = (a.alias || a.hostname || 'zzz').toLowerCase();
          bVal = (b.alias || b.hostname || 'zzz').toLowerCase();
          break;
        case 'mac':
          aVal = (a.mac || '').toLowerCase();
          bVal = (b.mac || '').toLowerCase();
          break;
        case 'vendor':
          aVal = (a.vendor || 'zzz').toLowerCase();
          bVal = (b.vendor || 'zzz').toLowerCase();
          break;
        case 'last_seen':
          aVal = new Date(a.last_seen).getTime();
          bVal = new Date(b.last_seen).getTime();
          break;
        case 'status':
          aVal = a.status.toLowerCase();
          bVal = b.status.toLowerCase();
          break;
        default:
          return 0;
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="logo">
          <Shield size={28} />
          <span>control-red-casa</span>
        </div>

        <nav className="nav-links">
          <div
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <Activity size={20} /> Dashboard
          </div>
          <div
            className={`nav-item ${activeTab === 'devices' ? 'active' : ''}`}
            onClick={() => setActiveTab('devices')}
          >
            <Wifi size={20} /> Dispositivos
          </div>
          <div
            className="nav-item"
            onClick={() => setShowAlertsPanel(true)}
            style={{ cursor: 'pointer', position: 'relative' }}
          >
            <Bell size={20} /> Alertas
            {activeAlerts.length > 0 && (
              <span style={{
                position: 'absolute',
                top: '0.5rem',
                right: '0.5rem',
                background: '#ef4444',
                color: 'white',
                borderRadius: '50%',
                width: '20px',
                height: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.75rem',
                fontWeight: 'bold'
              }}>
                {activeAlerts.length}
              </span>
            )}
          </div>
          <div
            className="nav-item"
            onClick={() => setShowNetworkMap(true)}
            style={{ cursor: 'pointer' }}
          >
            <Activity size={20} /> Detección Reciente
          </div>
          <div
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <Settings size={20} /> Configuración
          </div>
        </nav>

        {/* Theme Toggle */}
        <div style={{ marginTop: 'auto', paddingTop: '2rem', borderTop: '1px solid var(--border-color)' }}>
          <button
            onClick={toggleTheme}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--border-color)',
              borderRadius: '0.75rem',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              transition: 'all 0.2s',
              fontSize: '0.875rem',
              fontWeight: 500
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'}
          >
            {theme === 'dark' ? (
              <>
                <Sun size={18} />
                Tema Claro
              </>
            ) : (
              <>
                <Moon size={18} />
                Tema Oscuro
              </>
            )}
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h1>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            {(activeTab === 'dashboard' || activeTab === 'devices') && (
              <div style={{ display: 'flex', gap: '0.5rem', background: 'var(--card-bg)', borderRadius: '0.75rem', padding: '0.25rem', border: '1px solid var(--border-color)' }}>
                <button
                  onClick={() => setStatusFilter('all')}
                  style={{
                    background: statusFilter === 'all' ? 'var(--accent-color)' : 'transparent',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.5rem',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    transition: 'all 0.2s'
                  }}
                >
                  Todos
                </button>
                <button
                  onClick={() => setStatusFilter('online')}
                  style={{
                    background: statusFilter === 'online' ? 'var(--success)' : 'transparent',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.5rem',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    transition: 'all 0.2s'
                  }}
                >
                  Online
                </button>
                <button
                  onClick={() => setStatusFilter('offline')}
                  style={{
                    background: statusFilter === 'offline' ? 'var(--danger)' : 'transparent',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.5rem',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    transition: 'all 0.2s'
                  }}
                >
                  Offline
                </button>
              </div>
            )}
            {activeTab === 'devices' && (
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={exportToCSV}
                  title="Exportar a CSV"
                  style={{
                    background: 'var(--card-bg)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '0.75rem',
                    padding: '0.75rem',
                    color: 'white',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <Download size={18} />
                  CSV
                </button>
                <button
                  onClick={exportToJSON}
                  title="Exportar a JSON"
                  style={{
                    background: 'var(--card-bg)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '0.75rem',
                    padding: '0.75rem',
                    color: 'white',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <Download size={18} />
                  JSON
                </button>
                <button
                  onClick={handleReidentifyDevices}
                  title="Re-identificar dispositivos desconocidos"
                  style={{
                    background: 'var(--card-bg)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '0.75rem',
                    padding: '0.75rem',
                    color: 'white',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <Upload size={18} />
                  Re-identificar
                </button>
                <button
                  onClick={() => setShowPortScanner(true)}
                  title="Escanear puertos"
                  style={{
                    background: 'var(--accent-color)',
                    border: 'none',
                    borderRadius: '0.75rem',
                    padding: '0.75rem',
                    color: 'white',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontWeight: 600
                  }}
                >
                  <Scan size={18} />
                  Escanear Puertos
                </button>
              </div>
            )}
            <div style={{ position: 'relative' }}>
              <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
              <input
                type="text"
                placeholder="Buscar dispositivo..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  background: 'var(--card-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '0.75rem',
                  padding: '0.75rem 1rem 0.75rem 2.5rem',
                  color: 'white',
                  width: '300px'
                }}
              />
            </div>
          </div>
        </header>

        {/* Modal Alert */}
        {newDeviceAlert && config.showNotifications && (
          <div style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(4px)'
          }}>
            <div className="stat-card" style={{ maxWidth: '400px', width: '90%', padding: '2rem', position: 'relative', border: '2px solid var(--accent-color)' }}>
              <button
                onClick={() => setNewDeviceAlert(null)}
                style={{ position: 'absolute', right: '1rem', top: '1rem', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
              <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                <div style={{ background: 'rgba(59, 130, 246, 0.2)', padding: '1rem', borderRadius: '50%', width: 'fit-content', margin: '0 auto 1rem' }}>
                  <Target size={40} color="var(--accent-color)" />
                </div>
                <h2 style={{ color: 'var(--accent-color)' }}>¡Nuevo Dispositivo!</h2>
                <p style={{ color: 'var(--text-secondary)' }}>Se ha detectado un nuevo intruso o equipo en tu red.</p>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <div><strong>Nombre:</strong> {newDeviceAlert.hostname || 'Desconocido'}</div>
                <div><strong>IP:</strong> {newDeviceAlert.ip}</div>
                <div><strong>Fabricante:</strong> {newDeviceAlert.vendor}</div>
              </div>
              <button
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '1.5rem' }}
                onClick={() => setNewDeviceAlert(null)}
              >
                Entendido
              </button>
            </div>
          </div>
        )}

        {(activeTab === 'dashboard' || activeTab === 'devices') && (
          <>
            {activeTab === 'dashboard' && (
              <DashboardGrid
                devices={devices}
                stats={stats}
                alerts={alerts}
                onNavigate={setActiveTab}
              />
            )}

            {activeTab === 'devices' && (
              <section className="table-container">
                <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>
                    {activeTab === 'dashboard' ? 'Dispositivos Recientes' : 'Inventario de Red'}
                  </h3>
                  <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    Mostrando {activeTab === 'dashboard' ? Math.min(10, filteredDevices.length) : filteredDevices.length} de {filteredDevices.length} dispositivos
                    {statusFilter !== 'all' && ` (filtro: ${statusFilter})`}
                  </div>
                </div>
                <table>
                  <thead>
                    <tr>
                      <th
                        onClick={() => handleSort('status')}
                        style={{ cursor: 'pointer', userSelect: 'none' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          Estado
                          {sortField === 'status' ? (
                            sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                          ) : (
                            <ArrowUpDown size={14} style={{ opacity: 0.3 }} />
                          )}
                        </div>
                      </th>
                      <th
                        onClick={() => handleSort('hostname')}
                        style={{ cursor: 'pointer', userSelect: 'none' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          Nombre / Hostname
                          {sortField === 'hostname' ? (
                            sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                          ) : (
                            <ArrowUpDown size={14} style={{ opacity: 0.3 }} />
                          )}
                        </div>
                      </th>
                      <th
                        onClick={() => handleSort('ip')}
                        style={{ cursor: 'pointer', userSelect: 'none' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          Dirección IP
                          {sortField === 'ip' ? (
                            sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                          ) : (
                            <ArrowUpDown size={14} style={{ opacity: 0.3 }} />
                          )}
                        </div>
                      </th>
                      <th
                        onClick={() => handleSort('mac')}
                        style={{ cursor: 'pointer', userSelect: 'none' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          Dirección MAC
                          {sortField === 'mac' ? (
                            sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                          ) : (
                            <ArrowUpDown size={14} style={{ opacity: 0.3 }} />
                          )}
                        </div>
                      </th>
                      <th
                        onClick={() => handleSort('vendor')}
                        style={{ cursor: 'pointer', userSelect: 'none' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          Fabricante
                          {sortField === 'vendor' ? (
                            sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                          ) : (
                            <ArrowUpDown size={14} style={{ opacity: 0.3 }} />
                          )}
                        </div>
                      </th>
                      <th
                        onClick={() => handleSort('last_seen')}
                        style={{ cursor: 'pointer', userSelect: 'none' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          Visto por última vez
                          {sortField === 'last_seen' ? (
                            sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                          ) : (
                            <ArrowUpDown size={14} style={{ opacity: 0.3 }} />
                          )}
                        </div>
                      </th>
                      <th style={{ textAlign: 'center' }}>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(activeTab === 'dashboard' ? filteredDevices.slice(0, 10) : filteredDevices).map(dev => (
                      <tr key={dev.id}>
                        <td>
                          <span className={`badge badge-${dev.status.toLowerCase()}`}>
                            {dev.status}
                          </span>
                        </td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            {getDeviceIcon(dev.vendor || '')}
                            {editingMac === dev.mac ? (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <input
                                  className="edit-input"
                                  value={editValue}
                                  onChange={(e) => setEditValue(e.target.value)}
                                  autoFocus
                                  onKeyDown={(e) => e.key === 'Enter' && handleUpdateAlias(dev.mac, editValue)}
                                />
                                <Check
                                  size={16}
                                  style={{ cursor: 'pointer', color: 'var(--success)' }}
                                  onClick={() => handleUpdateAlias(dev.mac, editValue)}
                                />
                              </div>
                            ) : (
                              <>
                                <span style={{ cursor: 'default' }}>{dev.alias || dev.hostname || 'Desconocido'}</span>
                                <Edit2
                                  size={14}
                                  style={{ cursor: 'pointer', opacity: 0.5, marginLeft: '0.25rem' }}
                                  onClick={() => {
                                    setEditingMac(dev.mac);
                                    setEditValue(dev.alias || dev.hostname || '');
                                  }}
                                />
                              </>
                            )}
                          </div>
                        </td>
                        <td><code>{dev.ip}</code></td>
                        <td><code>{dev.mac}</code></td>
                        <td>{dev.vendor || 'Desconocido'}</td>
                        <td>{new Date(dev.last_seen).toLocaleString()}</td>
                        <td>
                          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                            <button
                              onClick={() => setSelectedDevice(dev)}
                              title="Ver detalles"
                              style={{
                                background: 'var(--accent-color)',
                                border: 'none',
                                borderRadius: '0.5rem',
                                padding: '0.5rem',
                                color: 'white',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center'
                              }}
                            >
                              <Eye size={16} />
                            </button>
                            <button
                              onClick={() => handleToggleAuthorization(dev.id, dev.is_authorized)}
                              title={dev.is_authorized ? 'Bloquear dispositivo' : 'Autorizar dispositivo'}
                              style={{
                                background: dev.is_authorized ? 'var(--danger)' : 'var(--success)',
                                border: 'none',
                                borderRadius: '0.5rem',
                                padding: '0.5rem',
                                color: 'white',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center'
                              }}
                            >
                              {dev.is_authorized ? <Lock size={16} /> : <Unlock size={16} />}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            )}
          </>
        )}

        {activeTab === 'alerts' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {alerts.map(alert => (
              <div key={alert.id} className="stat-card" style={{ flexDirection: 'row', alignItems: 'center', gap: '1.5rem' }}>
                <div style={{
                  background: alert.type === 'NEW_DEVICE' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  padding: '1rem',
                  borderRadius: '1rem',
                  color: alert.type === 'NEW_DEVICE' ? 'var(--accent-color)' : 'var(--danger)'
                }}>
                  <AlertCircle size={24} />
                </div>
                <div>
                  <h4 style={{ marginBottom: '0.25rem' }}>{alert.type}</h4>
                  <p style={{ color: 'var(--text-secondary)' }}>{alert.message}</p>
                  <small style={{ color: 'var(--text-secondary)', opacity: 0.6 }}>
                    {new Date(alert.timestamp).toLocaleString()}
                  </small>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'settings' && (
          <div style={{ maxWidth: '800px' }}>
            <div className="stat-card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Activity size={24} color="var(--accent-color)" />
                Actualización Automática
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>Activar actualización automática</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      Actualiza la lista de dispositivos automáticamente
                    </div>
                  </div>
                  <label style={{ position: 'relative', display: 'inline-block', width: '52px', height: '28px' }}>
                    <input
                      type="checkbox"
                      checked={config.autoRefresh}
                      onChange={(e) => {
                        const newConfig = { ...config, autoRefresh: e.target.checked };
                        setConfig(newConfig);
                        localStorage.setItem('netguard-config', JSON.stringify(newConfig));
                      }}
                      style={{ opacity: 0, width: 0, height: 0 }}
                    />
                    <span style={{
                      position: 'absolute',
                      cursor: 'pointer',
                      top: 0, left: 0, right: 0, bottom: 0,
                      background: config.autoRefresh ? 'var(--success)' : 'var(--border-color)',
                      transition: '0.3s',
                      borderRadius: '28px'
                    }}>
                      <span style={{
                        position: 'absolute',
                        content: '',
                        height: '20px',
                        width: '20px',
                        left: config.autoRefresh ? '28px' : '4px',
                        bottom: '4px',
                        background: 'white',
                        transition: '0.3s',
                        borderRadius: '50%'
                      }}></span>
                    </span>
                  </label>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>Intervalo de actualización</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      Cada cuántos segundos se actualizan los datos
                    </div>
                  </div>
                  <select
                    value={config.refreshInterval}
                    onChange={(e) => {
                      const newConfig = { ...config, refreshInterval: parseInt(e.target.value) };
                      setConfig(newConfig);
                      localStorage.setItem('netguard-config', JSON.stringify(newConfig));
                    }}
                    style={{
                      background: 'var(--card-bg)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '0.5rem',
                      padding: '0.5rem 1rem',
                      color: 'white',
                      cursor: 'pointer'
                    }}
                  >
                    <option value="15">15 segundos</option>
                    <option value="30">30 segundos</option>
                    <option value="60">1 minuto</option>
                    <option value="120">2 minutos</option>
                    <option value="300">5 minutos</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="stat-card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Bell size={24} color="var(--accent-color)" />
                Notificaciones
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>Mostrar notificaciones</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      Muestra alertas cuando se detectan nuevos dispositivos
                    </div>
                  </div>
                  <label style={{ position: 'relative', display: 'inline-block', width: '52px', height: '28px' }}>
                    <input
                      type="checkbox"
                      checked={config.showNotifications}
                      onChange={(e) => {
                        const newConfig = { ...config, showNotifications: e.target.checked };
                        setConfig(newConfig);
                        localStorage.setItem('netguard-config', JSON.stringify(newConfig));
                      }}
                      style={{ opacity: 0, width: 0, height: 0 }}
                    />
                    <span style={{
                      position: 'absolute',
                      cursor: 'pointer',
                      top: 0, left: 0, right: 0, bottom: 0,
                      background: config.showNotifications ? 'var(--success)' : 'var(--border-color)',
                      transition: '0.3s',
                      borderRadius: '28px'
                    }}>
                      <span style={{
                        position: 'absolute',
                        content: '',
                        height: '20px',
                        width: '20px',
                        left: config.showNotifications ? '28px' : '4px',
                        bottom: '4px',
                        background: 'white',
                        transition: '0.3s',
                        borderRadius: '50%'
                      }}></span>
                    </span>
                  </label>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>Alertas sonoras</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      Reproduce un sonido cuando hay nuevas alertas
                    </div>
                  </div>
                  <label style={{ position: 'relative', display: 'inline-block', width: '52px', height: '28px' }}>
                    <input
                      type="checkbox"
                      checked={config.soundAlerts}
                      onChange={(e) => {
                        const newConfig = { ...config, soundAlerts: e.target.checked };
                        setConfig(newConfig);
                        localStorage.setItem('netguard-config', JSON.stringify(newConfig));
                      }}
                      style={{ opacity: 0, width: 0, height: 0 }}
                    />
                    <span style={{
                      position: 'absolute',
                      cursor: 'pointer',
                      top: 0, left: 0, right: 0, bottom: 0,
                      background: config.soundAlerts ? 'var(--success)' : 'var(--border-color)',
                      transition: '0.3s',
                      borderRadius: '28px'
                    }}>
                      <span style={{
                        position: 'absolute',
                        content: '',
                        height: '20px',
                        width: '20px',
                        left: config.soundAlerts ? '28px' : '4px',
                        bottom: '4px',
                        background: 'white',
                        transition: '0.3s',
                        borderRadius: '50%'
                      }}></span>
                    </span>
                  </label>
                </div>
              </div>
            </div>

            <TelegramSettings />

            <div className="stat-card">
              <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Shield size={24} color="var(--accent-color)" />
                Información del Sistema
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '0.75rem' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>VERSION</div>
                  <div style={{ fontSize: '1.125rem', fontWeight: 600 }}>2.1.0</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '0.75rem' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>ESTADO</div>
                  <div style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--success)' }}>Activo</div>
                </div>
              </div>

              <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '0.75rem', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                  <strong style={{ color: 'var(--accent-color)' }}>control-red-casa</strong> es un sistema de monitoreo de red que te permite
                  visualizar todos los dispositivos conectados a tu red local, identificarlos y recibir alertas de nuevas conexiones.
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Device Detail Modal */}
      {selectedDevice && (
        <DeviceDetailView
          device={selectedDevice}
          onClose={() => setSelectedDevice(null)}
        />
      )}
      {/* Port Scanner Modal */}
      {showPortScanner && (
        <PortScannerModal
          devices={devices.filter(d => d.status === 'Online')}
          onClose={() => setShowPortScanner(false)}
          onScanComplete={(results) => {
            console.log('Scan completed:', results);
            // Opcional: actualizar datos después del escaneo
            fetchData();
          }}
        />
      )}
      {/* Device Detection List (Replacement for Network Map) */}
      {showNetworkMap && (
        <DeviceDetectionList
          devices={devices}
          onClose={() => setShowNetworkMap(false)}
        />
      )}
      {/* Alerts Panel */}
      {showAlertsPanel && (
        <AlertsPanel
          onClose={() => setShowAlertsPanel(false)}
        />
      )}
      {/* Alert Notifications (Toasts) */}
      {alertNotifications.map((alert, index) => (
        <div
          key={alert.id || index}
          style={{
            position: 'fixed',
            top: `${2 + index * 6}rem`,
            right: '2rem',
            zIndex: 9999
          }}
        >
          <AlertNotification
            alert={alert}
            onClose={() => removeNotification(alert.id)}
            onAcknowledge={acknowledgeAlert}
            autoClose={true}
          />
        </div>
      ))}
    </div>
  );
}

export default App;
