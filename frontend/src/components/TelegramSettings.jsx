
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Send, Save, Check, X, Eye, EyeOff } from 'lucide-react';
import { API_BASE } from '../config';

const TelegramSettings = () => {
    const [config, setConfig] = useState({
        enabled: false,
        bot_token: '',
        chat_id: ''
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);
    const [showToken, setShowToken] = useState(false);
    const [message, setMessage] = useState(null);

    useEffect(() => {
        fetchConfig();
    }, []);

    const fetchConfig = async () => {
        try {
            const res = await axios.get(`${API_BASE}/config/telegram`);
            setConfig(res.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching telegram config:", error);
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        setMessage(null);
        try {
            await axios.post(`${API_BASE}/config/telegram`, config);
            setMessage({ type: 'success', text: 'Configuración guardada correctamente' });
            // Refetch to get masked token if needed
            fetchConfig();
        } catch (error) {
            const errorMsg = error.response?.data?.message || error.response?.data?.detail || error.message || 'Error al guardar configuración';
            setMessage({ type: 'error', text: errorMsg });
        } finally {
            setSaving(false);
        }
    };

    const handleTest = async () => {
        setTesting(true);
        setMessage(null);
        try {
            // Fix: Use correct endpoint and send current config
            await axios.post(`${API_BASE}/api/test-telegram`, config);
            setMessage({ type: 'success', text: 'Mensaje de prueba enviado con éxito' });
        } catch (error) {
            const errorMsg = error.response?.data?.message || error.response?.data?.detail || error.message || 'Error enviando mensaje';
            setMessage({ type: 'error', text: errorMsg });
        } finally {
            setTesting(false);
        }
    };

    if (loading) return <div>Cargando configuración...</div>;

    return (
        <div className="stat-card" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Send size={24} color="#229ED9" />
                Integración con Telegram
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {/* Switch Enable */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                        <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>Activar notificaciones</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            Envía alertas a tu chat de Telegram
                        </div>
                    </div>
                    <label style={{ position: 'relative', display: 'inline-block', width: '52px', height: '28px' }}>
                        <input
                            type="checkbox"
                            checked={config.enabled}
                            onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                            style={{ opacity: 0, width: 0, height: 0 }}
                        />
                        <span style={{
                            position: 'absolute',
                            cursor: 'pointer',
                            top: 0, left: 0, right: 0, bottom: 0,
                            background: config.enabled ? '#229ED9' : 'var(--border-color)',
                            transition: '0.3s',
                            borderRadius: '28px'
                        }}>
                            <span style={{
                                position: 'absolute',
                                content: '',
                                height: '20px',
                                width: '20px',
                                left: config.enabled ? '28px' : '4px',
                                bottom: '4px',
                                background: 'white',
                                transition: '0.3s',
                                borderRadius: '50%'
                            }}></span>
                        </span>
                    </label>
                </div>

                {/* Bot Token Input */}
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Bot Token</label>
                    <div style={{ position: 'relative' }}>
                        <input
                            type={showToken ? "text" : "password"}
                            value={config.bot_token}
                            onChange={(e) => setConfig({ ...config, bot_token: e.target.value })}
                            placeholder="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                paddingRight: '2.5rem',
                                background: 'var(--background)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '0.5rem',
                                color: 'var(--text-primary)'
                            }}
                        />
                        <button
                            onClick={() => setShowToken(!showToken)}
                            style={{
                                position: 'absolute',
                                right: '0.5rem',
                                top: '50%',
                                transform: 'translateY(-50%)',
                                background: 'none',
                                border: 'none',
                                color: 'var(--text-secondary)',
                                cursor: 'pointer'
                            }}
                        >
                            {showToken ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                    </div>
                    <small style={{ color: 'var(--text-secondary)', marginTop: '0.25rem', display: 'block' }}>
                        Obtenlo creando un bot con @BotFather
                    </small>
                </div>

                {/* Chat ID Input */}
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Chat ID</label>
                    <input
                        type="text"
                        value={config.chat_id}
                        onChange={(e) => setConfig({ ...config, chat_id: e.target.value })}
                        placeholder="123456789"
                        style={{
                            width: '100%',
                            padding: '0.75rem',
                            background: 'var(--background)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '0.5rem',
                            color: 'var(--text-primary)'
                        }}
                    />
                    <small style={{ color: 'var(--text-secondary)', marginTop: '0.25rem', display: 'block' }}>
                        Tu ID personal o el ID del grupo/canal (busca "get my id" en Telegram)
                    </small>
                </div>

                {/* Notification Options */}
                <div style={{ background: 'var(--background)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--border-color)' }}>
                    <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.875rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Tipos de Alerta
                    </h4>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={config.notify_new_device !== false} // Default true
                                onChange={(e) => setConfig({ ...config, notify_new_device: e.target.checked })}
                            />
                            <span style={{ fontSize: '0.9rem' }}>ℹ️ Nuevos dispositivos detectados</span>
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={config.notify_device_offline !== false} // Default true
                                onChange={(e) => setConfig({ ...config, notify_device_offline: e.target.checked })}
                            />
                            <span style={{ fontSize: '0.9rem' }}>🔴 Dispositivo desconectado (Offline)</span>
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={config.notify_device_online === true} // Default false
                                onChange={(e) => setConfig({ ...config, notify_device_online: e.target.checked })}
                            />
                            <span style={{ fontSize: '0.9rem' }}>🟢 Dispositivo reconectado (Online)</span>
                        </label>
                    </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        style={{
                            flex: 1,
                            padding: '0.75rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.5rem',
                            background: 'var(--accent-color)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '0.5rem',
                            cursor: saving ? 'not-allowed' : 'pointer',
                            opacity: saving ? 0.7 : 1
                        }}
                    >
                        {saving ? 'Guardando...' : <><Save size={18} /> Guardar Configuración</>}
                    </button>

                    <button
                        onClick={handleTest}
                        disabled={testing || !config.enabled}
                        style={{
                            flex: 1,
                            padding: '0.75rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.5rem',
                            background: 'transparent',
                            border: '1px solid var(--border-color)',
                            color: 'var(--text-primary)',
                            borderRadius: '0.5rem',
                            cursor: (testing || !config.enabled) ? 'not-allowed' : 'pointer',
                            opacity: (testing || !config.enabled) ? 0.5 : 1
                        }}
                    >
                        {testing ? 'Enviando...' : <><Send size={18} /> Probar Conexión</>}
                    </button>
                </div>

                {/* Feedback Message */}
                {message && (
                    <div style={{
                        padding: '1rem',
                        borderRadius: '0.5rem',
                        background: message.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        color: message.type === 'success' ? 'var(--success)' : 'var(--danger)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        {message.type === 'success' ? <Check size={18} /> : <X size={18} />}
                        {message.text}
                    </div>
                )}
            </div>
        </div>
    );
};

export default TelegramSettings;
