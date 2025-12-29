# FASE 5 — Resumen Ejecutivo

Estado: Core analítico y UI BI inicial completos (read-only).

- KPIs coherentes: ingresos (animales), costos (nómina+insumos), margen.
- Tendencias: producción mensual agregada por 12 meses.
- Insights: reglas de caídas de producción, costos vs ingresos, margen negativo.
- Exportación: CSV, Excel, PDF para analítica, con auditoría `EXPORT_ANALYTICS`.
- Auditoría BI: `CONSULTA_ANALITICA`, `VIEW_DASHBOARD` activas.

Próximos pasos:
- Completar ingresos de leche si se habilita registro de ventas de leche.
- Añadir comparativos adicionales y selector de período en UI.
- Preparar datasets limpios para FASE 6 (ML).
