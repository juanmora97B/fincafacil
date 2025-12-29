"""
=============================================================================
GUÍA DE INTEGRACIÓN - FASE 2 ANALYTICS ENGINES
=============================================================================

Ejemplos de uso de los 3 motores analíticos en tu aplicación.
"""

from typing import Optional

# ============================================================================
# EJEMPLO 1: CALCULAR TENDENCIA DE PRODUCCIÓN ÚLTIMA SEMANA
# ============================================================================

from src.services.analytics_trends_service import get_analytics_trends_service, TrendPeriod

def mostrar_tendencia_produccion():
    """Mostrar gráfico de tendencia de producción."""
    
    service = get_analytics_trends_service()
    
    # Calcular tendencia del último mes
    resultado = service.calcular_tendencia(
        metrica="produccion_total",
        periodo=TrendPeriod.MONTHLY,
        usuario_id=1  # Usuario actual
    )
    
    # El resultado contiene:
    # - puntos: lista de TrendPoint con fecha, valor, promedio_movil, variacion_pct
    # - tendencia_general: "ASCENDENTE", "DESCENDENTE", "ESTABLE"
    # - variacion_total_pct: cambio total en el período
    
    print(f"Métrica: {resultado.metrica}")
    print(f"Período: {resultado.periodo}")
    print(f"Tendencia general: {resultado.tendencia_general}")
    print(f"Variación: {resultado.variacion_total_pct:.2f}%")
    print(f"Puntos: {len(resultado.puntos)}")
    
    # Iterar sobre puntos para graficar
    for punto in resultado.puntos:
        print(f"  {punto.fecha}: {punto.valor:.2f} (MA: {punto.promedio_movil:.2f}, Var: {punto.variacion_pct:.2f}%)")
    
    return resultado


# ============================================================================
# EJEMPLO 2: COMPARAR MES ACTUAL CON MES ANTERIOR
# ============================================================================

from src.services.analytics_comparative_service import get_analytics_comparative_service

def mostrar_comparacion_mensual():
    """Mostrar variación mes a mes."""
    
    service = get_analytics_comparative_service()
    
    # Comparar mes actual vs mes anterior (auto-detecta)
    resultado = service.comparar_mes_vs_mes(
        metrica="produccion_total",
        usuario_id=1
    )
    
    # El resultado contiene:
    # - periodo_actual, periodo_anterior
    # - valor_actual, valor_anterior
    # - variacion_absoluta, variacion_pct
    # - categoria: "MEJORA", "EMPEORA", "ESTABLE"
    
    print(f"\n{resultado.metrica}")
    print(f"Período actual: {resultado.periodo_actual} → {resultado.valor_actual:.2f}")
    print(f"Período anterior: {resultado.periodo_anterior} → {resultado.valor_anterior:.2f}")
    print(f"Variación: {resultado.variacion_pct:+.2f}% ({resultado.variacion_absoluta:+.2f})")
    print(f"Categoría: {resultado.categoria}")
    
    # Colorear en UI según categoría
    if resultado.categoria == "MEJORA":
        print("🟢 Mejora detectada")
    elif resultado.categoria == "EMPEORA":
        print("🔴 Empeora detectada")
    else:
        print("🟡 Sin cambios significativos")
    
    return resultado


# ============================================================================
# EJEMPLO 3: COMPARAR TRIMESTRE CON TRIMESTRE
# ============================================================================

def mostrar_comparacion_trimestral():
    """Comparar trimestre a trimestre."""
    
    service = get_analytics_comparative_service()
    
    # Trimestre actual vs trimestre anterior
    resultado = service.comparar_trimestre_vs_trimestre(
        metrica="costo_total",
        usuario_id=1
    )
    
    print(f"\nComparación trimestral - {resultado.metrica}")
    print(f"Trimestre actual ({resultado.periodo_actual}): ${resultado.valor_actual:,.2f}")
    print(f"Trimestre anterior ({resultado.periodo_anterior}): ${resultado.valor_anterior:,.2f}")
    print(f"Cambio: {resultado.variacion_pct:+.2f}%")


# ============================================================================
# EJEMPLO 4: COMPARAR AÑO CON AÑO
# ============================================================================

def mostrar_comparacion_anual():
    """Comparar año a año."""
    
    service = get_analytics_comparative_service()
    
    resultado = service.comparar_año_vs_año(
        metrica="ingreso_total",
        usuario_id=1
    )
    
    print(f"\nComparación anual - {resultado.metrica}")
    print(f"Año {resultado.periodo_actual}: ${resultado.valor_actual:,.2f}")
    print(f"Año {resultado.periodo_anterior}: ${resultado.valor_anterior:,.2f}")
    print(f"Crecimiento: {resultado.variacion_pct:+.2f}%")


# ============================================================================
# EJEMPLO 5: GENERAR INSIGHTS AUTOMÁTICOS
# ============================================================================

from src.services.analytics_insights_service import get_analytics_insights_service, SeverityLevel

def mostrar_insights():
    """Generar y mostrar insights automáticos."""
    
    service = get_analytics_insights_service()
    
    # Generar insights para toda la finca
    resultado = service.generar_insights(
        finca_id=None,  # None = todas las fincas
        usuario_id=1
    )
    
    print(f"\n{'='*70}")
    print(f"INSIGHTS AUTOMÁTICOS - {resultado.total_insights} total")
    print(f"Críticos: {resultado.insights_criticos}, Warnings: {resultado.insights_warnings}")
    print(f"{'='*70}")
    
    # Agrupar por severidad
    for insight in resultado.insights:
        color = "🔴" if insight.severidad == "CRITICAL" else "🟡" if insight.severidad == "WARNING" else "🔵"
        
        print(f"\n{color} [{insight.severidad}] {insight.titulo}")
        print(f"   Tipo: {insight.tipo}")
        print(f"   Descripción: {insight.descripcion}")
        print(f"   Métrica: {insight.metrica_principal}")
        print(f"   Valor actual: {insight.valor_actual:.2f}, Threshold: {insight.threshold:.2f}")
        
        if insight.acciones_sugeridas:
            print(f"   Acciones sugeridas:")
            for accion in insight.acciones_sugeridas:
                print(f"      • {accion}")
    
    return resultado


# ============================================================================
# EJEMPLO 6: DASHBOARD COMPLETO (TODOS LOS SERVICIOS)
# ============================================================================

def generar_dashboard_completo(finca_id: Optional[int] = None, usuario_id: int = 1):
    """Generar dashboard con datos de los 3 servicios."""
    
    print(f"\n{'='*70}")
    print(f"DASHBOARD ANALÍTICO - FincaFácil BI")
    print(f"{'='*70}")
    
    # [1] Tendencias
    print("\n[1] TENDENCIAS (Último mes)")
    print("-" * 70)
    try:
        tendencias_serv = get_analytics_trends_service()
        trend = tendencias_serv.calcular_tendencia(
            "produccion_total",
            TrendPeriod.MONTHLY,
            usuario_id
        )
        print(f"Producción: {trend.tendencia_general}")
        print(f"  Valor inicial: {trend.valor_inicial:.2f}")
        print(f"  Valor final: {trend.valor_final:.2f}")
        print(f"  Cambio: {trend.variacion_total_pct:+.2f}%")
        print(f"  Puntos datos: {len(trend.puntos)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # [2] Comparativos
    print("\n[2] COMPARATIVOS (Mes vs mes)")
    print("-" * 70)
    try:
        comp_serv = get_analytics_comparative_service()
        
        # Producción
        comp_prod = comp_serv.comparar_mes_vs_mes("produccion_total", usuario_id=usuario_id)
        print(f"Producción: {comp_prod.valor_actual:.2f} ({comp_prod.variacion_pct:+.2f}%) [{comp_prod.categoria}]")
        
        # Costos
        comp_cost = comp_serv.comparar_mes_vs_mes("costo_total", usuario_id=usuario_id)
        print(f"Costos: {comp_cost.valor_actual:.2f} ({comp_cost.variacion_pct:+.2f}%) [{comp_cost.categoria}]")
        
        # Ingresos
        comp_ing = comp_serv.comparar_mes_vs_mes("ingreso_total", usuario_id=usuario_id)
        print(f"Ingresos: {comp_ing.valor_actual:.2f} ({comp_ing.variacion_pct:+.2f}%) [{comp_ing.categoria}]")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # [3] Insights
    print("\n[3] INSIGHTS (Alertas automáticas)")
    print("-" * 70)
    try:
        insights_serv = get_analytics_insights_service()
        result = insights_serv.generar_insights(finca_id, usuario_id)
        
        if result.insights_criticos > 0:
            print(f"🔴 CRÍTICOS: {result.insights_criticos}")
            for insight in result.insights:
                if insight.severidad == "CRITICAL":
                    print(f"   - {insight.titulo}")
        
        if result.insights_warnings > 0:
            print(f"🟡 WARNINGS: {result.insights_warnings}")
            for insight in result.insights:
                if insight.severidad == "WARNING":
                    print(f"   - {insight.titulo}")
        
        if result.total_insights == 0:
            print("✅ Sin alertas - Todo bien")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*70)


# ============================================================================
# EJEMPLO 7: EXPORTAR DATOS A JSON (PARA DASHBOARD FRONTEND)
# ============================================================================

import json
from datetime import datetime

def exportar_dashboard_json(usuario_id: int = 1) -> dict:
    """Exportar todos los datos para fronted/dashboard."""
    
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "usuario_id": usuario_id,
        "trends": {},
        "comparatives": {},
        "insights": {}
    }
    
    try:
        # Trends
        trends_serv = get_analytics_trends_service()
        for periodo in ["WEEKLY", "MONTHLY", "QUARTERLY"]:
            trend = trends_serv.calcular_tendencia(
                "produccion_total",
                getattr(TrendPeriod, periodo),
                usuario_id
            )
            # Convertir a dict
            dashboard_data["trends"][periodo.lower()] = {
                "metrica": trend.metrica,
                "periodo": trend.periodo,
                "tendencia_general": trend.tendencia_general,
                "puntos": [
                    {
                        "fecha": p.fecha,
                        "valor": p.valor,
                        "promedio_movil": p.promedio_movil,
                        "variacion_pct": p.variacion_pct
                    }
                    for p in trend.puntos
                ],
                "variacion_total_pct": trend.variacion_total_pct
            }
    except Exception as e:
        print(f"Error trends: {e}")
    
    try:
        # Comparatives
        comp_serv = get_analytics_comparative_service()
        comp = comp_serv.comparar_mes_vs_mes("produccion_total", usuario_id=usuario_id)
        dashboard_data["comparatives"]["mes_vs_mes"] = {
            "metrica": comp.metrica,
            "periodo_actual": comp.periodo_actual,
            "periodo_anterior": comp.periodo_anterior,
            "valor_actual": comp.valor_actual,
            "valor_anterior": comp.valor_anterior,
            "variacion_pct": comp.variacion_pct,
            "categoria": comp.categoria
        }
    except Exception as e:
        print(f"Error comparatives: {e}")
    
    try:
        # Insights
        insights_serv = get_analytics_insights_service()
        result = insights_serv.generar_insights(usuario_id=usuario_id)
        dashboard_data["insights"] = {
            "total": result.total_insights,
            "criticos": result.insights_criticos,
            "warnings": result.insights_warnings,
            "items": [
                {
                    "tipo": i.tipo,
                    "titulo": i.titulo,
                    "descripcion": i.descripcion,
                    "severidad": i.severidad,
                    "valor_actual": i.valor_actual,
                    "threshold": i.threshold
                }
                for i in result.insights
            ]
        }
    except Exception as e:
        print(f"Error insights: {e}")
    
    return dashboard_data


# ============================================================================
# EJEMPLO 8: USAR EN CONTROLLERS/ROUTES
# ============================================================================

def analytics_api_endpoint(request_type: str, usuario_id: int = 1):
    """
    Endpoint genérico para consultas analíticas.
    
    Uso en Flask/FastAPI:
        GET /api/analytics/trends?metrica=produccion_total&periodo=MONTHLY
        GET /api/analytics/comparatives?type=mes_vs_mes&metrica=produccion_total
        GET /api/analytics/insights
        GET /api/analytics/dashboard
    """
    
    if request_type == "dashboard":
        return exportar_dashboard_json(usuario_id)
    
    elif request_type == "trends":
        serv = get_analytics_trends_service()
        result = serv.calcular_tendencia("produccion_total", TrendPeriod.MONTHLY, usuario_id)
        return {
            "metrica": result.metrica,
            "periodo": result.periodo,
            "puntos": [
                {
                    "fecha": p.fecha,
                    "valor": p.valor,
                    "promedio_movil": p.promedio_movil
                }
                for p in result.puntos
            ]
        }
    
    elif request_type == "insights":
        serv = get_analytics_insights_service()
        result = serv.generar_insights(usuario_id=usuario_id)
        return {
            "total": result.total_insights,
            "criticos": result.insights_criticos,
            "items": [
                {
                    "titulo": i.titulo,
                    "severidad": i.severidad,
                    "acciones": i.acciones_sugeridas
                }
                for i in result.insights
            ]
        }


# ============================================================================
# MAIN - EJECUTAR EJEMPLOS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("EJEMPLOS DE USO - FASE 2 ANALYTICS ENGINES")
    print("="*70)
    
    # Ejecutar los ejemplos
    print("\n[EJEMPLO 1] Mostrar tendencia de producción")
    mostrar_tendencia_produccion()
    
    print("\n[EJEMPLO 2] Mostrar comparación mensual")
    mostrar_comparacion_mensual()
    
    print("\n[EJEMPLO 3] Mostrar comparación trimestral")
    mostrar_comparacion_trimestral()
    
    print("\n[EJEMPLO 4] Mostrar comparación anual")
    mostrar_comparacion_anual()
    
    print("\n[EJEMPLO 5] Mostrar insights")
    mostrar_insights()
    
    print("\n[EJEMPLO 6] Dashboard completo")
    generar_dashboard_completo()
    
    print("\n[EJEMPLO 7] Exportar a JSON")
    dashboard_json = exportar_dashboard_json()
    print(json.dumps(dashboard_json, indent=2, default=str)[:500] + "...")
    
    print("\n" + "="*70)
    print("✅ Todos los ejemplos completados")
    print("="*70)
