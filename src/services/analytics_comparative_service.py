"""
=============================================================================
ANALYTICS COMPARATIVE SERVICE - FASE 2 BI/Analytics
=============================================================================

Responsabilidad:
    Comparar períodos: mes vs mes, trimestre vs trimestre, año vs año
    Genera análisis de variación con explicaciones

Casos soportados:
    1. Mes actual vs mes anterior
    2. Trimestre actual vs trimestre anterior
    3. Año actual vs año anterior

Salida:
    - Valor actual
    - Valor anterior
    - Variación absoluta
    - Variación porcentual
    - Cambio categorizado: MEJORA/EMPEORA/ESTABLE

Regla CRÍTICA:
    ⚠️ NUNCA leer tablas operativas
    ✅ SOLO leer bi_snapshots_mensual

Auditoría:
    - CONSULTA_ANALITICA: tipo=COMPARATIVO
    - Qué períodos se comparan
    - Duracion de query

Autor: Arquitecto BI Senior
Versión: 2.0 - Analytics Phase
"""

from typing import Dict, Optional, Any, Literal
from datetime import datetime, date
from dataclasses import dataclass, asdict
import json
import logging
from enum import Enum

from src.database.database import get_db_connection
from src.services.analytics_cache_service import get_analytics_cache
from src.core.audit_service import log_event

logger = logging.getLogger("AnalyticsComparative")


class ComparativeType(Enum):
    """Tipos de comparación soportados."""
    MONTH_VS_MONTH = "mes_vs_mes"
    QUARTER_VS_QUARTER = "trim_vs_trim"
    YEAR_VS_YEAR = "año_vs_año"


class ComparisonCategory(Enum):
    """Categoría de cambio."""
    MEJORA = "MEJORA"  # Positivo
    EMPEORA = "EMPEORA"  # Negativo
    ESTABLE = "ESTABLE"  # Sin cambio significativo


@dataclass
class ComparativeResult:
    """Resultado de comparación entre períodos."""
    metrica: str
    tipo_comparacion: str
    periodo_actual: str
    periodo_anterior: str
    valor_actual: float
    valor_anterior: float
    variacion_absoluta: float
    variacion_pct: float
    threshold_estable: float = 5.0  # % para considerar estable
    categoria: str = ""  # MEJORA/EMPEORA/ESTABLE
    timestamp: str = ""

    def __post_init__(self):
        """Calcula categoria después de inicializar."""
        if abs(self.variacion_pct) <= self.threshold_estable:
            self.categoria = ComparisonCategory.ESTABLE.value
        elif self.variacion_pct > 0:
            self.categoria = ComparisonCategory.MEJORA.value
        else:
            self.categoria = ComparisonCategory.EMPEORA.value

        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class AnalyticsComparativeService:
    """Servicio de comparación de períodos desde snapshots BI."""

    def __init__(self):
        """Inicializa el servicio de comparativos."""
        self._cache = get_analytics_cache()

    def comparar_mes_vs_mes(
        self,
        metrica: str,
        mes_actual: Optional[int] = None,
        año_actual: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> ComparativeResult:
        """
        Compara mes actual vs mes anterior.

        Args:
            metrica: Métrica a comparar
            mes_actual: Mes actual (1-12), default = hoy
            año_actual: Año actual, default = hoy
            usuario_id: Para auditoría

        Returns:
            ComparativeResult con variaciones
        """
        inicio = datetime.now()

        # Usar mes/año actual si no se especifica
        hoy = datetime.now().date()
        if mes_actual is None:
            mes_actual = hoy.month
            año_actual = hoy.year
        elif año_actual is None:
            año_actual = hoy.year

        # Consultar cache
        cache_key = f"comp_mes_{metrica}_{año_actual}_{mes_actual}"
        cached = self._cache.get_or_calculate(
            cache_key,
            lambda: self._comparar_meses(metrica, mes_actual, año_actual)
        )

        if isinstance(cached, str):
            cached = json.loads(cached)

        resultado = ComparativeResult(**cached)

        # Auditoría
        if usuario_id:
            duracion_ms = (datetime.now() - inicio).total_seconds() * 1000
            log_event(
                usuario="usuario_" + str(usuario_id),
                modulo="ANALYTICS",
                accion="COMPARATIVO_MES",
                entidad=f"{metrica}_{año_actual}_{mes_actual}",
                resultado="OK",
                mensaje=f"Comparación mes vs mes en {duracion_ms:.0f}ms"
            )

        return resultado

    def comparar_trimestre_vs_trimestre(
        self,
        metrica: str,
        trimestre_actual: Optional[int] = None,
        año_actual: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> ComparativeResult:
        """Compara trimestre actual vs trimestre anterior."""
        inicio = datetime.now()

        hoy = datetime.now().date()
        if trimestre_actual is None:
            trimestre_actual = (hoy.month - 1) // 3 + 1
            año_actual = hoy.year
        elif año_actual is None:
            año_actual = hoy.year

        cache_key = f"comp_trim_{metrica}_{año_actual}_{trimestre_actual}"
        cached = self._cache.get_or_calculate(
            cache_key,
            lambda: self._comparar_trimestres(metrica, trimestre_actual, año_actual)
        )

        if isinstance(cached, str):
            cached = json.loads(cached)

        resultado = ComparativeResult(**cached)

        if usuario_id:
            duracion_ms = (datetime.now() - inicio).total_seconds() * 1000
            log_event(
                usuario="usuario_" + str(usuario_id),
                modulo="ANALYTICS",
                accion="COMPARATIVO_TRIM",
                entidad=f"{metrica}_{año_actual}_Q{trimestre_actual}",
                resultado="OK",
                mensaje=f"Comparación trimestre vs trimestre en {duracion_ms:.0f}ms"
            )

        return resultado

    def comparar_año_vs_año(
        self,
        metrica: str,
        año_actual: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> ComparativeResult:
        """Compara año actual vs año anterior."""
        inicio = datetime.now()

        if año_actual is None:
            año_actual = datetime.now().year

        cache_key = f"comp_año_{metrica}_{año_actual}"
        cached = self._cache.get_or_calculate(
            cache_key,
            lambda: self._comparar_años(metrica, año_actual)
        )

        if isinstance(cached, str):
            cached = json.loads(cached)

        resultado = ComparativeResult(**cached)

        if usuario_id:
            duracion_ms = (datetime.now() - inicio).total_seconds() * 1000
            log_event(
                usuario="usuario_" + str(usuario_id),
                modulo="ANALYTICS",
                accion="COMPARATIVO_AÑO",
                entidad=f"{metrica}_{año_actual}",
                resultado="OK",
                mensaje=f"Comparación año vs año en {duracion_ms:.0f}ms"
            )

        return resultado

    # ==================== IMPLEMENTACIÓN PRIVADA ====================

    def _comparar_meses(self, metrica: str, mes: int, año: int) -> Dict[str, Any]:
        """Implementa comparación mes vs mes."""
        # Snapshot actual
        val_actual = self._obtener_valor_mes(metrica, mes, año)

        # Snapshot anterior
        mes_anterior = mes - 1 if mes > 1 else 12
        año_anterior = año if mes > 1 else año - 1
        val_anterior = self._obtener_valor_mes(metrica, mes_anterior, año_anterior)

        var_abs = val_actual - val_anterior
        var_pct = self._variacion_porcentual(val_anterior, val_actual)

        return asdict(ComparativeResult(
            metrica=metrica,
            tipo_comparacion=ComparativeType.MONTH_VS_MONTH.value,
            periodo_actual=f"{año}-{mes:02d}",
            periodo_anterior=f"{año_anterior}-{mes_anterior:02d}",
            valor_actual=val_actual,
            valor_anterior=val_anterior,
            variacion_absoluta=var_abs,
            variacion_pct=var_pct
        ))

    def _comparar_trimestres(self, metrica: str, trimestre: int, año: int) -> Dict[str, Any]:
        """Implementa comparación trimestre vs trimestre."""
        # Meses del trimestre actual
        meses_actual = self._meses_del_trimestre(trimestre)
        val_actual = self._promedio_meses(metrica, meses_actual, año)

        # Trimestre anterior
        trim_anterior = trimestre - 1 if trimestre > 1 else 4
        año_anterior = año if trimestre > 1 else año - 1
        meses_anterior = self._meses_del_trimestre(trim_anterior)
        val_anterior = self._promedio_meses(metrica, meses_anterior, año_anterior)

        var_abs = val_actual - val_anterior
        var_pct = self._variacion_porcentual(val_anterior, val_actual)

        return asdict(ComparativeResult(
            metrica=metrica,
            tipo_comparacion=ComparativeType.QUARTER_VS_QUARTER.value,
            periodo_actual=f"{año}-Q{trimestre}",
            periodo_anterior=f"{año_anterior}-Q{trim_anterior}",
            valor_actual=val_actual,
            valor_anterior=val_anterior,
            variacion_absoluta=var_abs,
            variacion_pct=var_pct
        ))

    def _comparar_años(self, metrica: str, año: int) -> Dict[str, Any]:
        """Implementa comparación año vs año."""
        # Promedio del año actual
        val_actual = self._promedio_meses(metrica, list(range(1, 13)), año)

        # Promedio del año anterior
        val_anterior = self._promedio_meses(metrica, list(range(1, 13)), año - 1)

        var_abs = val_actual - val_anterior
        var_pct = self._variacion_porcentual(val_anterior, val_actual)

        return asdict(ComparativeResult(
            metrica=metrica,
            tipo_comparacion=ComparativeType.YEAR_VS_YEAR.value,
            periodo_actual=str(año),
            periodo_anterior=str(año - 1),
            valor_actual=val_actual,
            valor_anterior=val_anterior,
            variacion_absoluta=var_abs,
            variacion_pct=var_pct
        ))

    def _obtener_valor_mes(self, metrica: str, mes: int, año: int) -> float:
        """Obtiene valor de métrica para mes específico."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT data_json
                    FROM bi_snapshots_mensual
                    WHERE año = ? AND mes = ?
                    LIMIT 1
                """, (año, mes))

                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    valor = self._extraer_metrica(data, metrica)
                    return float(valor) if valor is not None else 0.0

            return 0.0
        except Exception as e:
            logger.error(f"Error obteniendo valor {mes}/{año}: {e}")
            return 0.0

    def _promedio_meses(self, metrica: str, meses: list, año: int) -> float:
        """Calcula promedio de métrica para varios meses."""
        valores = []
        for mes in meses:
            val = self._obtener_valor_mes(metrica, mes, año)
            if val > 0:
                valores.append(val)

        return sum(valores) / len(valores) if valores else 0.0

    def _extraer_metrica(self, snapshot: Dict[str, Any], metrica: str) -> Optional[float]:
        """Extrae métrica del snapshot JSON."""
        try:
            if "resumen_mensual" in snapshot and "kpis" in snapshot["resumen_mensual"]:
                kpis = snapshot["resumen_mensual"]["kpis"]
                if metrica in kpis:
                    return float(kpis[metrica])

            if "kpis" in snapshot and metrica in snapshot["kpis"]:
                return float(snapshot["kpis"][metrica])

            return None
        except Exception as e:
            logger.warning(f"Error extrayendo {metrica}: {e}")
            return None

    def _variacion_porcentual(self, valor_anterior: float, valor_actual: float) -> float:
        """Calcula variación porcentual."""
        if valor_anterior == 0:
            return 0 if valor_actual == 0 else 100
        return ((valor_actual - valor_anterior) / abs(valor_anterior)) * 100

    @staticmethod
    def _meses_del_trimestre(trimestre: int) -> list:
        """Retorna meses de un trimestre."""
        return [(trimestre - 1) * 3 + i for i in range(1, 4)]


# Singleton global
_comparative_service: Optional[AnalyticsComparativeService] = None


def get_analytics_comparative_service() -> AnalyticsComparativeService:
    """Obtiene instancia singleton del servicio de comparativos."""
    global _comparative_service
    if _comparative_service is None:
        _comparative_service = AnalyticsComparativeService()
    return _comparative_service
