# FASE 37: Analytics BI para FincaFácil

## 🎯 Objetivo
Convertir datos operacionales en información ejecutiva y accionable mediante read models, jobs de agregación y dashboards profesionales.

## 🏗️ Arquitectura CQRS

```
┌─────────────────────────────────────────────────────────────┐
│                    DATOS OPERACIONALES                      │
│  (animal, servicio, diagnostico, tratamiento, evento, etc.) │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │   JOBS DE AGREGACIÓN (Hora)    │
    ├────────────────────────────────┤
    │ BuildProductivityAnalytics     │
    │ BuildAlertAnalytics            │
    │ BuildIAAnalytics               │
    │ BuildAutonomyAnalytics         │
    └────────────┬───────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │   READ MODELS (Agregadas)      │
    ├────────────────────────────────┤
    │ analytics_productividad        │
    │ analytics_alertas              │
    │ analytics_ia                   │
    │ analytics_autonomia            │
    │ analytics_orquestacion         │
    │ analytics_comparativos         │
    └────────────┬───────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │   API REST (/api/v1/analytics) │
    │   Cache (300-900s)             │
    │   Rate Limit                   │
    └────────────┬───────────────────┘
                 │
                 ▼
    ┌────────────────────────────────┐
    │   DASHBOARDS (React)           │
    │ CentroDeAnalyticsIA.tsx        │
    │ KPIs, Gráficas, Tendencias     │
    └────────────────────────────────┘
```

## 📊 Read Models Diseño

### 1. `analytics_productividad`
```sql
CREATE TABLE analytics_productividad (
  id INTEGER PRIMARY KEY,
  empresa_id INTEGER NOT NULL,
  fecha DATE NOT NULL,
  lote_id INTEGER,
  sector_id INTEGER,
  animales_totales INTEGER DEFAULT 0,
  nacimientos INTEGER DEFAULT 0,
  destetes INTEGER DEFAULT 0,
  muertes INTEGER DEFAULT 0,
  traslados INTEGER DEFAULT 0,
  servicios INTEGER DEFAULT 0,
  partos INTEGER DEFAULT 0,
  mortalidad_pct REAL DEFAULT 0.0,
  natalidad_pct REAL DEFAULT 0.0,
  peso_promedio REAL,
  refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(empresa_id, fecha, lote_id, sector_id),
  FOREIGN KEY (empresa_id) REFERENCES empresa(id),
  INDEX idx_empresa_fecha (empresa_id, fecha)
);
```

### 2. `analytics_alertas`
```sql
CREATE TABLE analytics_alertas (
  id INTEGER PRIMARY KEY,
  empresa_id INTEGER NOT NULL,
  fecha DATE NOT NULL,
  tipo_alerta TEXT,  -- 'Sanitaria', 'Nutricional', 'Reproductiva', 'Operacional'
  total_activas INTEGER DEFAULT 0,
  total_resueltas INTEGER DEFAULT 0,
  criticas_activas INTEGER DEFAULT 0,
  tiempo_promedio_resolucion INTEGER,  -- minutos
  refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(empresa_id, fecha, tipo_alerta),
  FOREIGN KEY (empresa_id) REFERENCES empresa(id),
  INDEX idx_empresa_fecha (empresa_id, fecha)
);
```

### 3. `analytics_ia`
```sql
CREATE TABLE analytics_ia (
  id INTEGER PRIMARY KEY,
  empresa_id INTEGER NOT NULL,
  fecha DATE NOT NULL,
  sugerencias_generadas INTEGER DEFAULT 0,
  sugerencias_aceptadas INTEGER DEFAULT 0,
  sugerencias_rechazadas INTEGER DEFAULT 0,
  tasa_aceptacion_pct REAL DEFAULT 0.0,
  impacto_estimado_pesos REAL DEFAULT 0.0,
  precision_historica_pct REAL DEFAULT 0.0,
  modelo_version TEXT,
  refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(empresa_id, fecha),
  FOREIGN KEY (empresa_id) REFERENCES empresa(id),
  INDEX idx_empresa_fecha (empresa_id, fecha)
);
```

### 4. `analytics_autonomia`
```sql
CREATE TABLE analytics_autonomia (
  id INTEGER PRIMARY KEY,
  empresa_id INTEGER NOT NULL,
  fecha DATE NOT NULL,
  orquestaciones_ejecutadas INTEGER DEFAULT 0,
  orquestaciones_exitosas INTEGER DEFAULT 0,
  orquestaciones_fallidas INTEGER DEFAULT 0,
  rollbacks_activados INTEGER DEFAULT 0,
  autonomia_estado TEXT DEFAULT 'ON',  -- ON, OFF
  kill_switch_activaciones INTEGER DEFAULT 0,
  refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(empresa_id, fecha),
  FOREIGN KEY (empresa_id) REFERENCES empresa(id),
  INDEX idx_empresa_fecha (empresa_id, fecha)
);
```

### 5. `analytics_comparativos`
```sql
CREATE TABLE analytics_comparativos (
  id INTEGER PRIMARY KEY,
  empresa_id INTEGER NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  comparador TEXT,  -- 'hoy_vs_semana_pasada', 'mes_vs_anterior', 'con_sin_ia', 'antes_despues_orquestacion'
  metrica_nombre TEXT,
  valor_actual REAL,
  valor_anterior REAL,
  variacion_pct REAL,
  refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(empresa_id, comparador, fecha_inicio, fecha_fin, metrica_nombre),
  FOREIGN KEY (empresa_id) REFERENCES empresa(id),
  INDEX idx_empresa_comparador (empresa_id, comparador)
);
```

### 6. `analytics_audit`
```sql
CREATE TABLE analytics_audit (
  id INTEGER PRIMARY KEY,
  empresa_id INTEGER NOT NULL,
  usuario_id INTEGER,
  endpoint TEXT,
  metodo TEXT,
  parametros TEXT,  -- JSON
  resultado TEXT,   -- 'SUCCESS', 'DENIED'
  razon TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (empresa_id) REFERENCES empresa(id),
  INDEX idx_empresa_timestamp (empresa_id, timestamp)
);
```

## 🔄 Jobs de Agregación

### Ejecución
- **Horario**: Cada hora (LUN-DOM, 06:00-22:00)
- **Nocturno**: 23:00 (recálculos históricos)
- **Configuración**: `withoutOverlapping`, `onOneServer`

### Tipo de Jobs
1. `BuildProductivityAnalyticsJob` - Nacimientos, destetes, mortalidad, traslados
2. `BuildAlertAnalyticsJob` - Conteos y tiempos de resolución
3. `BuildIAAnalyticsJob` - Sugerencias aceptadas, impacto, precisión
4. `BuildAutonomyAnalyticsJob` - Orquestaciones, rollbacks, kill switch

## 🚀 Endpoints REST (<40ms)

```
GET /api/v1/analytics/overview
  → KPIs principales (hoy, últimos 7 días, últimos 30)
  
GET /api/v1/analytics/productividad?fecha=YYYY-MM-DD&lote_id=123
  → Producción por período, lote, sector
  
GET /api/v1/analytics/alertas?tipo=Sanitaria&fechaDesde=YYYY-MM-DD
  → Alertas activas, resueltas, críticas, tiempo promedio
  
GET /api/v1/analytics/ia?periodo=ultima_semana
  → Sugerencias, aceptación, impacto, precisión
  
GET /api/v1/analytics/autonomia?comparador=antes_despues
  → Orquestaciones, rollbacks, autonomía ON/OFF
```

## 📈 Frontend Dashboards

### CentroDeAnalyticsIA.tsx
- KPIs principales en cards (animales, nacimientos, muertes, mortalidad%)
- Gráfica de línea: Productividad por día (últimos 30)
- Gráfica de barras: Alertas por tipo
- Gráfica de dona: Distribución por sector
- Tablas: Últimos eventos, alertas activas, sugerencias IA

### Componentes Reutilizables
- `KPICard` - Valor + variación %
- `LineChart` - Tendencias temporales
- `BarChart` - Comparativas
- `DonutChart` - Distribuciones
- `AlertTable` - Listados con filtros

## 🔒 Seguridad & Gobernanza

✅ Respeta `empresa_id`
✅ Read-only (sin inserciones/actualizaciones desde API)
✅ Auditoría de accesos en `analytics_audit`
✅ Rate limit: 100 req/min por IP
✅ Cache: 300-900s según tipo
✅ Sin export masivo aún

## ✅ Criterios de Cierre

- [ ] Read models creadas con índices
- [ ] Jobs de agregación funcionando
- [ ] Endpoints REST validados <40ms
- [ ] Dashboards alimentados automáticamente
- [ ] Tendencias con lógica correcta
- [ ] Auditoría de accesos registrada
- [ ] Documentación completa

---

**Status**: EN PROGRESO  
**Última actualización**: 2025-12-25
