import React from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/**
 * Componente de gráfico de líneas para métricas temporales
 */
export const MetricLineChart = ({ data, dataKey, color = "#3b82f6", title }) => {
    if (!data || data.length === 0) {
        return (
            <div className="chart-placeholder">
                <p>No hay datos disponibles</p>
            </div>
        );
    }

    return (
        <div className="chart-container">
            {title && <h3 className="chart-title">{title}</h3>}
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                        dataKey="timestamp"
                        stroke="var(--text-secondary)"
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
                        }}
                    />
                    <YAxis stroke="var(--text-secondary)" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'var(--card-bg)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '0.5rem'
                        }}
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                    />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey={dataKey}
                        stroke={color}
                        strokeWidth={2}
                        dot={false}
                        name={dataKey.replace(/_/g, ' ')}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

/**
 * Componente de gráfico de área para bandwidth o tráfico
 */
export const MetricAreaChart = ({ data, dataKey, color = "#10b981", title }) => {
    return (
        <div className="chart-container">
            {title && <h3 className="chart-title">{title}</h3>}
            <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                        dataKey="timestamp"
                        stroke="var(--text-secondary)"
                        tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                    />
                    <YAxis stroke="var(--text-secondary)" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'var(--card-bg)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '0.5rem'
                        }}
                    />
                    <Area
                        type="monotone"
                        dataKey={dataKey}
                        stroke={color}
                        fill={color}
                        fillOpacity={0.3}
                        name={dataKey.replace(/_/g, ' ')}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

/**
 * Componente de gráfico de barras para comparativas
 */
export const MetricBarChart = ({ data, dataKey, color = "#f59e0b", title }) => {
    return (
        <div className="chart-container">
            {title && <h3 className="chart-title">{title}</h3>}
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="name" stroke="var(--text-secondary)" />
                    <YAxis stroke="var(--text-secondary)" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'var(--card-bg)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '0.5rem'
                        }}
                    />
                    <Bar dataKey={dataKey} fill={color} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

/**
 * Mini card con estadística resumida
 */
export const StatCard = ({ label, value, unit, trend, color = "var(--accent-color)" }) => {
    return (
        <div className="stat-mini-card">
            <div className="stat-mini-label">{label}</div>
            <div className="stat-mini-value" style={{ color }}>
                {value}
                {unit && <span className="stat-mini-unit">{unit}</span>}
            </div>
            {trend !== undefined && (
                <div className={`stat-mini-trend ${trend >= 0 ? 'positive' : 'negative'}`}>
                    {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
                </div>
            )}
        </div>
    );
};

/**
 * Gauge circular para métricas tipo porcentaje
 */
export const GaugeChart = ({ value, max = 100, label, color }) => {
    const percentage = ((value || 0) / max) * 100;
    const rotation = (percentage / 100) * 180 - 90;

    const getColor = () => {
        if (color) return color;
        if (percentage < 50) return 'var(--success)';
        if (percentage < 80) return 'var(--warning)';
        return 'var(--danger)';
    };

    return (
        <div className="gauge-container">
            <svg width="200" height="120" viewBox="0 0 200 120">
                <path
                    d="M 20 100 A 80 80 0 0 1 180 100"
                    fill="none"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="15"
                />
                <path
                    d="M 20 100 A 80 80 0 0 1 180 100"
                    fill="none"
                    stroke={getColor()}
                    strokeWidth="15"
                    strokeDasharray={`${(percentage / 100) * 251}, 251`}
                />
                <text x="100" y="90" textAnchor="middle" fill="white" fontSize="32" fontWeight="bold">
                    {(value || 0).toFixed(1)}
                </text>
                <text x="100" y="110" textAnchor="middle" fill="var(--text-secondary)" fontSize="14">
                    {label}
                </text>
            </svg>
        </div>
    );
};
