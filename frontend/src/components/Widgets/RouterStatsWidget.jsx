import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Wifi, Cpu, Activity, Clock } from 'lucide-react';
import axios from 'axios';
import { API_BASE } from '../../config';

const RouterStatsWidget = () => {
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await axios.get(`${API_BASE}/api/router/stats`);
                if (res.data && !res.data.error) {
                    setStats(res.data);

                    setHistory(prev => {
                        const now = new Date();
                        const timeStr = now.toLocaleTimeString();

                        const newItem = {
                            time: timeStr,
                            in: res.data.traffic_in / 1024 / 1024, // Mbps (aprox)
                            out: res.data.traffic_out / 1024 / 1024
                        };

                        const newHistory = [...prev, newItem];
                        if (newHistory.length > 20) newHistory.shift();
                        return newHistory;
                    });
                }
            } catch (error) {
                console.error("Error fetching router stats", error);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 5000);

        return () => clearInterval(interval);
    }, []);

    if (!stats) return <div style={{ padding: '1rem', color: 'gray' }}>Cargando datos del router...</div>;

    const formatUptime = (seconds) => {
        const days = Math.floor(seconds / (3600 * 24));
        const hours = Math.floor(seconds % (3600 * 24) / 3600);
        return `${days}d ${hours}h`;
    };

    return (
        <div style={{ padding: '0.5rem', height: '100%', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* KPI Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Cpu size={20} className="text-accent" />
                    <div>
                        <div style={{ fontSize: '0.7rem', color: 'gray' }}>CPU Load</div>
                        <div style={{ fontWeight: 'bold' }}>{stats.cpu_load.toFixed(2)}</div>
                    </div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Activity size={20} className="text-success" />
                    <div>
                        <div style={{ fontSize: '0.7rem', color: 'gray' }}>RAM Usage</div>
                        <div style={{ fontWeight: 'bold' }}>{stats.ram_usage}%</div>
                    </div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Wifi size={20} style={{ color: '#f59e0b' }} />
                    <div>
                        <div style={{ fontSize: '0.7rem', color: 'gray' }}>Traffic (In)</div>
                        <div style={{ fontWeight: 'bold' }}>{(stats.traffic_in / 1024 / 1024).toFixed(2)} Mbps</div>
                    </div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Clock size={20} style={{ opacity: 0.5 }} />
                    <div>
                        <div style={{ fontSize: '0.7rem', color: 'gray' }}>Uptime</div>
                        <div style={{ fontWeight: 'bold' }}>{formatUptime(stats.uptime)}</div>
                    </div>
                </div>
            </div>

            {/* Chart */}
            <div style={{ flex: 1, minHeight: 0 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={history}>
                        <defs>
                            <linearGradient id="colorIn" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorOut" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />
                        <XAxis dataKey="time" hide />
                        <YAxis hide />
                        <Tooltip
                            contentStyle={{ background: '#1f2937', borderColor: '#374151' }}
                            itemStyle={{ fontSize: '0.8rem' }}
                        />
                        <Area type="monotone" dataKey="in" stroke="#3b82f6" fillOpacity={1} fill="url(#colorIn)" />
                        <Area type="monotone" dataKey="out" stroke="#10b981" fillOpacity={1} fill="url(#colorOut)" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default RouterStatsWidget;
