from __future__ import annotations
from typing import Dict, List
from datetime import date, timedelta
from src.analytics.analytics_models import FinancialKPIs, ProductionKPIs, MonthlyPoint, TrendSeries, Comparative
from src.analytics import analytics_repository as repo
from src.core.audit_service import log_event

# Service: Calculates KPIs; repository only queries

def _period_dates(periodo: str) -> tuple[str, str]:
    # 'mes_actual' or 'YYYY-MM' or 'YYYY-MM to YYYY-MM'
    today = date.today()
    if periodo == 'mes_actual':
        inicio = today.replace(day=1)
        fin = today
    elif 'to' in periodo:
        a, b = [p.strip() for p in periodo.split('to')]
        inicio = date.fromisoformat(a + '-01')
        y, m = map(int, b.split('-'))
        fin = date(y, m, 28) + timedelta(days=4)
        fin = fin.replace(day=1) - timedelta(days=1)
    else:
        inicio = date.fromisoformat(periodo + '-01')
        fin = today
    return (inicio.isoformat(), fin.isoformat())


def calcular_kpis_financieros(periodo: str, usuario: str | None = None) -> FinancialKPIs:
    fi, ff = _period_dates(periodo)
    ingresos_anim = repo.ingresos_animales(fi, ff)
    ingresos_lech = repo.ingresos_leche(fi, ff)
    costos_nom = repo.costos_nomina(fi, ff)
    costos_ins = repo.costos_insumos(fi, ff)
    ingresos_tot = ingresos_anim + ingresos_lech
    costos_tot = costos_nom + costos_ins
    margen = ingresos_tot - costos_tot
    litros = repo.produccion_leche_total(fi, ff)
    margen_por_litro = (margen / litros) if litros > 0 else None
    animales = repo.animales_activos()
    costo_por_animal = (costos_tot / animales) if animales > 0 else None
    rentabilidad_mensual = (margen / ingresos_tot * 100) if ingresos_tot > 0 else None

    kpis = FinancialKPIs(
        ingresos_totales=ingresos_tot,
        ingresos_animales=ingresos_anim,
        ingresos_leche=ingresos_lech,
        costos_totales=costos_tot,
        costos_nomina=costos_nom,
        costos_insumos=costos_ins,
        margen_bruto=margen,
        margen_por_litro=margen_por_litro,
        costo_por_animal=costo_por_animal,
        rentabilidad_mensual=rentabilidad_mensual,
    )

    log_event(usuario=usuario, modulo="analytics", accion="CONSULTA_ANALITICA", entidad="kpis_financieros", resultado="OK")
    return kpis


def calcular_kpis_productivos(periodo: str, usuario: str | None = None) -> ProductionKPIs:
    fi, ff = _period_dates(periodo)
    prod_total = repo.produccion_leche_total(fi, ff)
    # Aproximación diaria: promediar sobre días
    di = date.fromisoformat(fi)
    df = date.fromisoformat(ff)
    dias = (df - di).days + 1
    produccion_diaria = prod_total / dias if dias > 0 else 0.0

    # Mensual: si periodo incluye varios meses, usar promedio mensual simple
    produccion_mensual = produccion_diaria * 30

    animales = repo.animales_activos()
    prod_prom_animal = (prod_total / animales) if animales > 0 else None

    servidas, paridas = repo.gestaciones_periodo(fi, ff)
    tasa_gestacion = (paridas / servidas * 100) if servidas > 0 else None

    intervalo_partos = repo.promedio_intervalo_partos_dias(fi, ff)
    mortalidad = repo.mortalidad_periodo(fi, ff)

    # Rotación inventario: ventas / animales
    ventas_animales = repo.ingresos_animales(fi, ff)  # ingreso, no cantidad; estimar por precio promedio futuro
    rotacion = None
    try:
        # Assumption: precio promedio ~ ingresos / N ventas; sin N, dejamos None
        rotacion = None
    except Exception:
        rotacion = None

    kpis = ProductionKPIs(
        produccion_diaria=produccion_diaria,
        produccion_mensual=produccion_mensual,
        produccion_promedio_por_animal=prod_prom_animal,
        tasa_gestacion=tasa_gestacion,
        intervalo_promedio_partos_dias=intervalo_partos,
        mortalidad=mortalidad,
        rotacion_inventario=rotacion,
    )

    log_event(usuario=usuario, modulo="analytics", accion="CONSULTA_ANALITICA", entidad="kpis_productivos", resultado="OK")
    return kpis


def tendencia_mensual_produccion(meses: int = 12, usuario: str | None = None) -> TrendSeries:
    hoy = date.today()
    inicio = (hoy.replace(day=1) - timedelta(days=30 * (meses - 1))).replace(day=1)
    fi, ff = inicio.isoformat(), hoy.isoformat()
    pts = get_monthly_production(fi, ff)
    points = [MonthlyPoint(periodo=p[0], valor=p[1]) for p in pts]
    serie = TrendSeries(nombre="Producción mensual (L)", puntos=points)
    log_event(usuario=usuario, modulo="analytics", accion="CONSULTA_ANALITICA", entidad="tendencia_produccion", resultado="OK")
    return serie

# Helper trends (explicit function to query monthly sums)

def get_monthly_production(fi: str, ff: str):
    pts = repo.monthly_sum("produccion_leche", "litros_manana + litros_tarde + litros_noche", fi, ff)
    return pts


def comparativo_periodos(metric: str, periodo_actual: str, periodo_anterior: str, usuario: str | None = None) -> Comparative:
    fi_a, ff_a = _period_dates(periodo_actual)
    fi_b, ff_b = _period_dates(periodo_anterior)
    if metric == "ingresos_totales":
        va = repo.ingresos_animales(fi_a, ff_a) + repo.ingresos_leche(fi_a, ff_a)
        vb = repo.ingresos_animales(fi_b, ff_b) + repo.ingresos_leche(fi_b, ff_b)
    elif metric == "costos_totales":
        va = repo.costos_nomina(fi_a, ff_a) + repo.costos_insumos(fi_a, ff_a)
        vb = repo.costos_nomina(fi_b, ff_b) + repo.costos_insumos(fi_b, ff_b)
    elif metric == "produccion_total":
        va = repo.produccion_leche_total(fi_a, ff_a)
        vb = repo.produccion_leche_total(fi_b, ff_b)
    else:
        raise ValueError(f"Metric no soportada: {metric}")
    varpct = ((va - vb) / vb * 100) if vb > 0 else None
    comp = Comparative(periodo_actual=periodo_actual, periodo_anterior=periodo_anterior, valor_actual=va, valor_anterior=vb, variacion_pct=varpct)
    log_event(usuario=usuario, modulo="analytics", accion="CONSULTA_ANALITICA", entidad=f"comparativo_{metric}", resultado="OK")
    return comp
