# FASE 5 — Analytics Core (Read-Only)

Objetivo: Calcular KPIs operativos y financieros, tendencias y comparativos, sin escribir datos.

## Arquitectura
- UI BI → Services (cálculos) → Repository (SELECT agregados) → SQLite (WAL)
- Prohibido: SQL en UI, escrituras, lógica de negocio en Repository.

## Módulos
- src/analytics/analytics_models.py: dataclasses (FinancialKPIs, ProductionKPIs, TrendSeries, Insight).
- src/analytics/analytics_repository.py: queries agregadas (SUM, COUNT) en tablas reales: `venta`, `pago_nomina`, `movimiento_insumo`, `produccion_leche`, etc.
- src/analytics/analytics_service.py: cálculos y derivaciones KPI (margen, rentabilidad, por litro, por animal).

## KPIs (mínimos)
- Finanzas: ingresos totales (animales), costos totales (nómina + insumos), margen bruto, rentabilidad mensual.
- Producción: producción diaria/mensual, promedio por animal, gestación, intervalo entre partos, mortalidad.

## Read-only
- Todos los métodos usan SELECT.
- Auditoría: `CONSULTA_ANALITICA` en cada cálculo.
