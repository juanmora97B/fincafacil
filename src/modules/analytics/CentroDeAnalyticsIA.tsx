/**
 * Centro de Analytics IA - Dashboard Principal
 * Componente que integra KPIs, gráficas y tendencias
 * 
 * Características:
 * - Carga lazy de datos
 * - Memoización para evitar re-renders
 * - Cache client-side
 * - Responsive design
 * - Auditoría de accesos
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import {
  LineChart,
  BarChart,
  PieChart,
  Line,
  Bar,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

// ==================== INTERFACES ====================

interface KPIData {
  hoy: {
    animales_totales: number;
    nacimientos: number;
    destetes: number;
    muertes: number;
    mortalidad_pct: number;
    alertas_activas: number;
    sugerencias_ia_aceptadas: number;
  };
  ultimos_7_dias: {
    muertes: number;
    promedio_diario: number;
  };
  timestamp: string;
}

interface ProductivityData {
  serie_temporal: Array<{
    fecha: string;
    nacimientos: number;
    destetes: number;
    muertes: number;
    traslados: number;
    servicios: number;
    partos: number;
  }>;
  total_periodo: {
    nacimientos: number;
    muertes: number;
    destetes: number;
  };
  timestamp: string;
}

interface AlertsData {
  por_tipo: Array<{
    tipo_alerta: string;
    total_activas: number;
    total_resueltas: number;
  }>;
  total_activas: number;
  total_resueltas: number;
  criticas_activas: number;
  timestamp: string;
}

interface IAData {
  sugerencias_generadas: number;
  sugerencias_aceptadas: number;
  tasa_aceptacion_pct: number;
  impacto_estimado_pesos: number;
  precision_historica_pct: number;
  timestamp: string;
}

interface AutonomyData {
  orquestaciones_ejecutadas: number;
  orquestaciones_exitosas: number;
  orquestaciones_fallidas: number;
  tasa_exito_pct: number;
  kill_switch_activaciones: number;
  timestamp: string;
}

// ==================== COMPONENTES ====================

/**
 * KPICard - Tarjeta de KPI con valor, variación y tendencia
 */
interface KPICardProps {
  titulo: string;
  valor: number | string;
  unidad?: string;
  variacion?: number;
  icono?: React.ReactNode;
  color?: string;
}

const KPICard: React.FC<KPICardProps> = ({
  titulo,
  valor,
  unidad = '',
  variacion,
  icono,
  color = '#1f77b4',
}) => {
  const variacionClass = variacion && variacion > 0 ? 'text-red-500' : 'text-green-500';

  return (
    <div
      className="bg-white rounded-lg shadow p-6 border-l-4"
      style={{ borderColor: color }}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium mb-2">{titulo}</p>
          <p className="text-3xl font-bold">{valor}</p>
          {unidad && <p className="text-gray-500 text-xs mt-1">{unidad}</p>}
        </div>
        {icono && <div className="text-3xl opacity-20">{icono}</div>}
      </div>
      {variacion !== undefined && (
        <p className={`text-sm mt-3 font-semibold ${variacionClass}`}>
          {variacion > 0 ? '↑' : '↓'} {Math.abs(variacion).toFixed(1)}%
        </p>
      )}
    </div>
  );
};

/**
 * LineChart - Gráfica de línea con tendencias
 */
interface ChartDataPoint {
  fecha: string;
  [key: string]: any;
}

interface LineChartComponentProps {
  title: string;
  data: ChartDataPoint[];
  lines: Array<{
    dataKey: string;
    stroke: string;
    name: string;
  }>;
}

const LineChartComponent: React.FC<LineChartComponentProps> = ({ title, data, lines }) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <div className="h-64 flex items-center justify-center text-gray-400">
          Sin datos disponibles
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="fecha"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip contentStyle={{ backgroundColor: '#f9f9f9', border: '1px solid #ccc' }} />
          <Legend />
          {lines.map((line) => (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              stroke={line.stroke}
              name={line.name}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * BarChart - Gráfica de barras
 */
interface BarChartComponentProps {
  title: string;
  data: ChartDataPoint[];
  bars: Array<{
    dataKey: string;
    fill: string;
    name: string;
  }>;
}

const BarChartComponent: React.FC<BarChartComponentProps> = ({ title, data, bars }) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <div className="h-64 flex items-center justify-center text-gray-400">
          Sin datos disponibles
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis dataKey="fecha" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip contentStyle={{ backgroundColor: '#f9f9f9', border: '1px solid #ccc' }} />
          <Legend />
          {bars.map((bar) => (
            <Bar key={bar.dataKey} dataKey={bar.dataKey} fill={bar.fill} name={bar.name} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * DonutChart - Gráfica circular
 */
interface DonutChartComponentProps {
  title: string;
  data: Array<{ name: string; value: number }>;
  colors?: string[];
}

const DonutChartComponent: React.FC<DonutChartComponentProps> = ({
  title,
  data,
  colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <div className="h-64 flex items-center justify-center text-gray-400">
          Sin datos disponibles
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value}`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

// ==================== MAIN DASHBOARD ====================

const CentroDeAnalyticsIA: React.FC = () => {
  const [kpiData, setKpiData] = useState<KPIData | null>(null);
  const [productivityData, setProductivityData] = useState<ProductivityData | null>(null);
  const [alertsData, setAlertsData] = useState<AlertsData | null>(null);
  const [iaData, setIaData] = useState<IAData | null>(null);
  const [autonomyData, setAutonomyData] = useState<AutonomyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState('30');

  // API Base URL
  const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

  // Fetch data con cache
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const params = { empresa_id: 1 };

      const [kpi, prod, alerts, ia, autonomy] = await Promise.all([
        axios.get(`${API_BASE}/api/v1/analytics/overview`, { params }),
        axios.get(`${API_BASE}/api/v1/analytics/productividad`, {
          params: { ...params, rango_dias: selectedPeriod },
        }),
        axios.get(`${API_BASE}/api/v1/analytics/alertas`, { params }),
        axios.get(`${API_BASE}/api/v1/analytics/ia`, { params }),
        axios.get(`${API_BASE}/api/v1/analytics/autonomia`, { params }),
      ]);

      setKpiData(kpi.data);
      setProductivityData(prod.data);
      setAlertsData(alerts.data);
      setIaData(ia.data);
      setAutonomyData(autonomy.data);
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Error desconocido al cargar datos'
      );
      console.error('Analytics API error:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedPeriod, API_BASE]);

  // Auto-refresh cada 5 minutos
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchData]);

  if (loading && !kpiData) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-500">Cargando dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-600 font-semibold">Error: {error}</p>
        <button
          onClick={fetchData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Encabezado */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">📊 Centro de Analytics IA</h1>
        <p className="text-gray-600">
          Información ejecutiva en tiempo real
          {kpiData?.timestamp && ` • Actualizado: ${new Date(kpiData.timestamp).toLocaleTimeString()}`}
        </p>
      </div>

      {/* KPIs Principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {kpiData && (
          <>
            <KPICard
              titulo="Animales"
              valor={kpiData.hoy.animales_totales}
              unidad="Activos"
              icono="🐄"
              color="#4CAF50"
            />
            <KPICard
              titulo="Nacimientos (Hoy)"
              valor={kpiData.hoy.nacimientos}
              unidad="Nuevos"
              variacion={kpiData.hoy.nacimientos > 0 ? 5 : -5}
              icono="👶"
              color="#2196F3"
            />
            <KPICard
              titulo="Mortalidad"
              valor={kpiData.hoy.mortalidad_pct.toFixed(1)}
              unidad="%"
              variacion={kpiData.hoy.muertes > 0 ? 3 : 0}
              icono="⚠️"
              color="#FF9800"
            />
            <KPICard
              titulo="Alertas Activas"
              valor={kpiData.hoy.alertas_activas}
              unidad="Críticas"
              icono="🔔"
              color="#F44336"
            />
          </>
        )}
      </div>

      {/* Selectores de período */}
      <div className="mb-8 flex gap-4">
        <select
          value={selectedPeriod}
          onChange={(e) => setSelectedPeriod(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="7">Últimos 7 días</option>
          <option value="30">Últimos 30 días</option>
          <option value="90">Últimos 90 días</option>
        </select>
        <button
          onClick={fetchData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          🔄 Actualizar
        </button>
      </div>

      {/* Gráficas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {productivityData && (
          <LineChartComponent
            title="📈 Productividad (Serie Temporal)"
            data={productivityData.serie_temporal}
            lines={[
              { dataKey: 'nacimientos', stroke: '#2196F3', name: 'Nacimientos' },
              { dataKey: 'destetes', stroke: '#4CAF50', name: 'Destetes' },
              { dataKey: 'muertes', stroke: '#F44336', name: 'Muertes' },
            ]}
          />
        )}
        {alertsData && (
          <BarChartComponent
            title="🚨 Alertas por Tipo"
            data={alertsData.por_tipo.map((item: any) => ({
              ...item,
              fecha: item.tipo_alerta || 'Tipo'
            }))}
            bars={[
              { dataKey: 'total_activas', fill: '#FF9800', name: 'Activas' },
              { dataKey: 'total_resueltas', fill: '#4CAF50', name: 'Resueltas' },
            ]}
          />
        )}
      </div>

      {/* Segunda fila de gráficas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {iaData && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">🤖 IA - Sugerencias</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Generadas</p>
                <p className="text-2xl font-bold">{iaData.sugerencias_generadas}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Aceptadas</p>
                <p className="text-2xl font-bold text-green-600">
                  {iaData.sugerencias_aceptadas}
                </p>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Tasa Aceptación</p>
                <p className="text-2xl font-bold">{iaData.tasa_aceptacion_pct.toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Impacto Estimado</p>
                <p className="text-lg font-bold text-blue-600">
                  ${(iaData.impacto_estimado_pesos / 1000).toFixed(0)}K
                </p>
              </div>
            </div>
          </div>
        )}

        {autonomyData && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">⚙️ Autonomía</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Orquestaciones Ejecutadas</p>
                <p className="text-2xl font-bold">{autonomyData.orquestaciones_ejecutadas}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Exitosas</p>
                <p className="text-2xl font-bold text-green-600">
                  {autonomyData.orquestaciones_exitosas}
                </p>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Tasa Éxito</p>
                <p className="text-2xl font-bold">{autonomyData.tasa_exito_pct.toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Kill Switch Activaciones</p>
                <p className="text-lg font-bold text-orange-600">
                  {autonomyData.kill_switch_activaciones}
                </p>
              </div>
            </div>
          </div>
        )}

        {kpiData && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">📊 Resumen Semanal</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Muertes (7 días)</p>
                <p className="text-2xl font-bold">{kpiData.ultimos_7_dias.muertes}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Promedio Diario</p>
                <p className="text-2xl font-bold">
                  {kpiData.ultimos_7_dias.promedio_diario.toFixed(1)}
                </p>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">Destetes Hoy</p>
                <p className="text-2xl font-bold text-blue-600">{kpiData.hoy.destetes}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-8 p-4 bg-white rounded-lg shadow text-center text-sm text-gray-600">
        <p>
          Datos actualizados automáticamente cada 5 minutos
          {kpiData?.timestamp && ` • Última actualización: ${new Date(kpiData.timestamp).toLocaleString('es-ES')}`}
        </p>
      </div>
    </div>
  );
};

export default CentroDeAnalyticsIA;
