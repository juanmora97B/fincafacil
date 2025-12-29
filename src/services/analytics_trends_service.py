"""
=============================================================================
ANALYTICS TRENDS SERVICE - FASE 2 BI/Analytics
=============================================================================

Responsabilidad:
    Calcular tendencias temporales desde snapshots mensuales
    Soporta múltiples períodos: 7d, 30d, 3m, 6m, 12m
    Genera JSON listo para gráficas

Flujo:
    1. Consultar analytics_cache primero
    2. Si no existe → Leer snapshots BI
    3. Calcular tendencias: valor, promedio móvil, variación %
    4. Guardar en cache con TTL
    5. Retornar resultados

Regla CRÍTICA:
    ⚠️ NUNCA leer tablas operativas
    ✅ SOLO leer bi_snapshots_mensual
    ✅ USAR analytics_cache para velocidad

Auditoría:
    - CONSULTA_ANALITICA: tipo=TENDENCIA
    - Usuario, timestamp, métrica consultada
    - Duración de query

Autor: Arquitecto BI Senior
Versión: 2.0 - Analytics Phase
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import logging
from enum import Enum

from src.database.database import get_db_connection
from src.services.analytics_cache_service import get_analytics_cache
from src.core.audit_service import log_event

logger = logging.getLogger("AnalyticsTrends")


class TrendPeriod(Enum):
    """Períodos de tiempo soportados."""
    WEEKLY = "7d"
    MONTHLY = "30d"
    QUARTERLY = "3m"
    BIANNUAL = "6m"
    YEARLY = "12m"


@dataclass
class TrendPoint:
    """Punto de datos en una tendencia."""
    fecha: str
    valor: float
    promedio_movil: Optional[float] = None
    variacion_pct: Optional[float] = None


@dataclass
class TrendResult:
    """Resultado completo de un análisis de tendencias."""
    metrica: str
    periodo: str
    puntos: List[TrendPoint]
    tendencia_general: str  # "ASCENDENTE", "DESCENDENTE", "ESTABLE"
    valor_inicial: float
    valor_final: float
    variacion_total_pct: float
    timestamp: str


class AnalyticsTrendsService:
    """Servicio de cálculo de tendencias desde snapshots BI."""

    def __init__(self):
        """Inicializa el servicio de tendencias."""
        self._cache = get_analytics_cache()

    def calcular_tendencia(
        self,
        metrica: str,
        periodo: TrendPeriod = TrendPeriod.MONTHLY,
        usuario_id: Optional[int] = None
    ) -> TrendResult:
        """
        Calcula tendencia para una métrica.

        Args:
            metrica: Nombre de métrica (ej: "produccion_total", "gastos_operativos")
            periodo: Período de análisis (7d, 30d, 3m, 6m, 12m)
            usuario_id: Para auditoría

        Returns:
            TrendResult con puntos, tendencia general, variación

        Proceso:
            1. Consultar cache (clave: f"trend_{metrica}_{periodo.value}")
            2. Si hit → Retornar
            3. Si miss:
               - Leer snapshots BI
               - Calcular puntos y estadísticas
               - Guardar en cache (TTL 3600s para tendencias)
               - Retornar
        """
        # Auditoría
        inicio = datetime.now()

        # 1. Consultar cache
        cache_key = f"trend_{metrica}_{periodo.value}"
        cached = self._cache.get_or_calculate(
            cache_key,
            lambda: self._compute_trend(metrica, periodo)
        )

        # 2. Parsear resultado
        if isinstance(cached, str):
            cached = json.loads(cached)

        resultado = TrendResult(
            metrica=metrica,
            periodo=periodo.value,
            puntos=[TrendPoint(**p) for p in cached["puntos"]],
            tendencia_general=cached["tendencia_general"],
            valor_inicial=cached["valor_inicial"],
            valor_final=cached["valor_final"],
            variacion_total_pct=cached["variacion_total_pct"],
            timestamp=datetime.now().isoformat()
        )

        # 3. Auditoría
        if usuario_id:
            duracion_ms = (datetime.now() - inicio).total_seconds() * 1000
            log_event(
                usuario="usuario_" + str(usuario_id),
                modulo="ANALYTICS",
                accion="CONSULTA_TENDENCIA",
                entidad=f"tendencia_{metrica}_{periodo.value}",
                resultado="OK",
                mensaje=f"Tendencia calculada en {duracion_ms:.0f}ms"
            )

        return resultado

    def _compute_trend(self, metrica: str, periodo: TrendPeriod) -> Dict[str, Any]:
        """
        Calcula tendencia desde snapshots BI.

        Flujo:
            1. Determinar rango de fechas según período
            2. Consultar snapshots en rango
            3. Extraer métrica de JSON
            4. Calcular:
               - Promedio móvil (3 períodos)
               - Variación porcentual
               - Tendencia general
            5. Retornar como dict JSON-serializable
        """
        # 1. Determinar rango
        hoy = datetime.now()
        fecha_inicio = self._calcular_fecha_inicio(hoy, periodo)

        # 2. Consultar snapshots
        snapshots = self._obtener_snapshots_rango(fecha_inicio, hoy)

        if not snapshots:
            # Retornar tendencia vacía
            return {
                "puntos": [],
                "tendencia_general": "SIN_DATOS",
                "valor_inicial": 0,
                "valor_final": 0,
                "variacion_total_pct": 0
            }

        # 3. Extraer métrica
        puntos_brutos = []
        for snapshot in snapshots:
            valor = self._extraer_metrica(snapshot, metrica)
            if valor is not None:
                puntos_brutos.append({
                    "fecha": snapshot["fecha_snapshot"][:10],
                    "valor": float(valor)
                })

        if not puntos_brutos:
            return {
                "puntos": [],
                "tendencia_general": "METRICA_NO_ENCONTRADA",
                "valor_inicial": 0,
                "valor_final": 0,
                "variacion_total_pct": 0
            }

        # 4. Calcular estadísticas
        puntos = self._calcular_estadisticas(puntos_brutos)
        tendencia = self._detectar_tendencia(puntos)
        var_total = self._variacion_porcentual(puntos[0].valor, puntos[-1].valor)

        return {
            "puntos": [asdict(p) for p in puntos],
            "tendencia_general": tendencia,
            "valor_inicial": puntos[0].valor,
            "valor_final": puntos[-1].valor,
            "variacion_total_pct": var_total
        }

    def _calcular_fecha_inicio(self, hoy: datetime, periodo: TrendPeriod) -> datetime:
        """Calcula fecha de inicio según período."""
        if periodo == TrendPeriod.WEEKLY:
            return hoy - timedelta(days=7)
        elif periodo == TrendPeriod.MONTHLY:
            return hoy - timedelta(days=30)
        elif periodo == TrendPeriod.QUARTERLY:
            return hoy - timedelta(days=90)
        elif periodo == TrendPeriod.BIANNUAL:
            return hoy - timedelta(days=180)
        elif periodo == TrendPeriod.YEARLY:
            return hoy - timedelta(days=365)

    def _obtener_snapshots_rango(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Dict[str, Any]]:
        """Consulta snapshots en rango de fechas."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT data_json, fecha_snapshot
                    FROM bi_snapshots_mensual
                    WHERE DATE(fecha_snapshot) >= ? AND DATE(fecha_snapshot) <= ?
                    ORDER BY fecha_snapshot ASC
                """, (fecha_inicio.date(), fecha_fin.date()))

                snapshots = []
                for row in cursor.fetchall():
                    try:
                        data = json.loads(row[0])
                        data["fecha_snapshot"] = row[1]
                        snapshots.append(data)
                    except json.JSONDecodeError:
                        logger.warning(f"No se pudo parsear snapshot: {row}")
                        continue

                return snapshots
        except Exception as e:
            logger.error(f"Error consultando snapshots: {e}")
            return []

    def _extraer_metrica(self, snapshot: Dict[str, Any], metrica: str) -> Optional[float]:
        """Extrae métrica del snapshot JSON."""
        try:
            # Buscar en resumen_mensual.kpis
            if "resumen_mensual" in snapshot and "kpis" in snapshot["resumen_mensual"]:
                kpis = snapshot["resumen_mensual"]["kpis"]
                if metrica in kpis:
                    return float(kpis[metrica])

            # Buscar en kpis root
            if "kpis" in snapshot and metrica in snapshot["kpis"]:
                return float(snapshot["kpis"][metrica])

            return None
        except Exception as e:
            logger.warning(f"Error extrayendo métrica {metrica}: {e}")
            return None

    def _calcular_estadisticas(self, puntos_brutos: List[Dict]) -> List[TrendPoint]:
        """Calcula promedio móvil y variación porcentual."""
        puntos = []

        for i, punto_bruto in enumerate(puntos_brutos):
            # Promedio móvil de 3 períodos
            inicio_ventana = max(0, i - 1)
            fin_ventana = min(len(puntos_brutos), i + 2)
            prom_movil = sum(
                p["valor"] for p in puntos_brutos[inicio_ventana:fin_ventana]
            ) / (fin_ventana - inicio_ventana)

            # Variación porcentual
            var_pct = None
            if i > 0:
                var_pct = self._variacion_porcentual(
                    puntos_brutos[i-1]["valor"],
                    punto_bruto["valor"]
                )

            puntos.append(TrendPoint(
                fecha=punto_bruto["fecha"],
                valor=punto_bruto["valor"],
                promedio_movil=round(prom_movil, 2),
                variacion_pct=round(var_pct, 2) if var_pct else None
            ))

        return puntos

    def _variacion_porcentual(self, valor_anterior: float, valor_actual: float) -> float:
        """Calcula variación porcentual."""
        if valor_anterior == 0:
            return 0 if valor_actual == 0 else 100
        return ((valor_actual - valor_anterior) / abs(valor_anterior)) * 100

    def _detectar_tendencia(self, puntos: List[TrendPoint]) -> str:
        """Detecta tendencia general: ASCENDENTE, DESCENDENTE, ESTABLE."""
        if len(puntos) < 2:
            return "INSUFICIENTES_DATOS"

        variaciones = [
            p.variacion_pct for p in puntos if p.variacion_pct is not None
        ]

        if not variaciones:
            return "ESTABLE"

        promedio_var = sum(variaciones) / len(variaciones)

        if promedio_var > 5:
            return "ASCENDENTE"
        elif promedio_var < -5:
            return "DESCENDENTE"
        else:
            return "ESTABLE"


# Singleton global
_trends_service: Optional[AnalyticsTrendsService] = None


def get_analytics_trends_service() -> AnalyticsTrendsService:
    """Obtiene instancia singleton del servicio de tendencias."""
    global _trends_service
    if _trends_service is None:
        _trends_service = AnalyticsTrendsService()
    return _trends_service
