# FASE 5 — Insights (Reglas)

Generación de insights accionables sin ML.

## Servicio
- src/analytics/insights_service.py: Reglas sobre KPIs y tendencias.

## Reglas incluidas
- Producción ↓ 2 meses seguidos: nivel ALTO, recomendación sanidad/alimentación.
- Costos ↑ >15% sin aumento de ingresos: nivel ALTO, recomendación revisar compras.
- Margen negativo recurrente: nivel ALTO, recomendación ajuste de costos/ingresos.
- Producción promedio por animal baja (<2 L/día): nivel MEDIO.

## Auditoría
- `CONSULTA_ANALITICA` al generar insights.
