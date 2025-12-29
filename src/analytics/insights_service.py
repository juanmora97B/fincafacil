from __future__ import annotations
from typing import List
from datetime import date, timedelta
from src.analytics.analytics_models import Insight, TrendSeries
from src.analytics.analytics_service import calcular_kpis_financieros, calcular_kpis_productivos, get_monthly_production
from src.core.audit_service import log_event

# Rule-based insights (no ML)

def generar_insights(periodo: str, usuario: str | None = None) -> List[Insight]:
    fin = []
    fk = calcular_kpis_financieros(periodo, usuario=None)
    pk = calcular_kpis_productivos(periodo, usuario=None)

    # ⚠ Producción ↓ 2 meses seguidos
    hoy = date.today()
    inicio = (hoy.replace(day=1) - timedelta(days=30 * (2))).replace(day=1)
    pts = get_monthly_production(inicio.isoformat(), hoy.isoformat())
    if len(pts) >= 3:
        last3 = [v for _, v in pts[-3:]]
        if last3[2] < last3[1] < last3[0]:
            pct = ((last3[2] - last3[0]) / last3[0] * 100) if last3[0] else 0
            fin.append(Insight(
                nivel="ALTO",
                categoria="Producción",
                mensaje=f"Producción cayó {pct:.1f}% en los últimos 2 meses",
                recomendacion="Revisar alimentación y sanidad",
            ))

    # ⚠ Costos ↑ >15% sin aumento de ingresos
    if fk.costos_totales > 0 and fk.ingresos_totales > 0:
        # Comparar contra período anterior (mes anterior)
        from src.analytics.analytics_service import comparativo_periodos
        hoy_str = hoy.strftime('%Y-%m')
        prev = (hoy - timedelta(days=30)).strftime('%Y-%m')
        comp_cost = comparativo_periodos("costos_totales", hoy_str, prev)
        comp_ing = comparativo_periodos("ingresos_totales", hoy_str, prev)
        if comp_cost.variacion_pct and comp_cost.variacion_pct > 15 and (not comp_ing.variacion_pct or comp_ing.variacion_pct <= 0):
            fin.append(Insight(
                nivel="ALTO",
                categoria="Finanzas",
                mensaje=f"Costos subieron {comp_cost.variacion_pct:.1f}% sin aumento de ingresos",
                recomendacion="Revisar compras e insumos, renegociar proveedores",
            ))

    # ⚠ Margen negativo recurrente
    if fk.margen_bruto < 0:
        fin.append(Insight(
            nivel="ALTO",
            categoria="Finanzas",
            mensaje="Margen bruto negativo en el período",
            recomendacion="Ajustar costos o incrementar ingresos",
        ))

    # ⚠ Animal con baja producción persistente
    # Reglas simples: producción promedio por animal bajo cierto umbral
    if pk.produccion_promedio_por_animal is not None and pk.produccion_promedio_por_animal < 2.0:
        fin.append(Insight(
            nivel="MEDIO",
            categoria="Producción",
            mensaje="Producción promedio por animal < 2 L/día",
            recomendacion="Monitorear animales de baja producción",
        ))

    # ⚠ Tratamientos repetidos en mismo animal (placeholder - sin costo)
    # Se puede ampliar en Fase 6 con detalle por animal

    log_event(usuario=usuario, modulo="analytics", accion="CONSULTA_ANALITICA", entidad="insights", resultado="OK")
    return fin
