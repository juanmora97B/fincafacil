# FASE 5 — Dashboard BI (Read-Only)

UI de visualización básica, sin cálculos.

## Módulo
- src/ui/analytics_dashboard.py: CustomTkinter, threading/after, `@safe_ui_call`.

## Contenido
- Tarjetas KPI (ingresos, costos, margen, producción).
- Alertas generadas por insights.
- Selector de período (próximo paso).

## Auditoría
- `VIEW_DASHBOARD` al abrir.
