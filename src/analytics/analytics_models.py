from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class FinancialKPIs:
    ingresos_totales: float
    ingresos_animales: float
    ingresos_leche: float
    costos_totales: float
    costos_nomina: float
    costos_insumos: float
    margen_bruto: float
    margen_por_litro: Optional[float]
    costo_por_animal: Optional[float]
    rentabilidad_mensual: Optional[float]

@dataclass
class ProductionKPIs:
    produccion_diaria: float
    produccion_mensual: float
    produccion_promedio_por_animal: Optional[float]
    tasa_gestacion: Optional[float]
    intervalo_promedio_partos_dias: Optional[float]
    mortalidad: int
    rotacion_inventario: Optional[float]

@dataclass
class MonthlyPoint:
    periodo: str  # YYYY-MM
    valor: float

@dataclass
class TrendSeries:
    nombre: str
    puntos: List[MonthlyPoint]

@dataclass
class Comparative:
    periodo_actual: str
    periodo_anterior: str
    valor_actual: float
    valor_anterior: float
    variacion_pct: Optional[float]

@dataclass
class Insight:
    nivel: str  # BAJO | MEDIO | ALTO
    categoria: str  # Producción | Finanzas | Salud
    mensaje: str
    recomendacion: str
    meta: Optional[Dict] = None
