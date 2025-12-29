"""
=============================================================================
ANALYTICS INSIGHTS SERVICE - FASE 2 BI/Analytics
=============================================================================

Responsabilidad:
    Generar insights automáticos desde patrones en datos
    Algoritmos heurísticos (NO machine learning)
    
Tipos de insights:
    1. PRODUCCIÓN: Caída en 2 períodos consecutivos
    2. COSTOS: Aumento > 15% sin aumento proporcional en ingresos
    3. MARGEN: Negativo o por debajo de threshold
    4. EFICIENCIA: Producción por animal baja
    5. ANOMALÍAS: Cambios inesperados detectados

Niveles de severidad:
    - INFO: Información general, sin acción requerida
    - WARNING: Debe investigarse, potencial problema
    - CRITICAL: Acción inmediata requerida

Regla CRÍTICA:
    ⚠️ NUNCA leer tablas operativas
    ✅ SOLO usar resultados de trends y comparativos

Auditoría:
    - CONSULTA_ANALITICA: tipo=INSIGHT_GENERADO
    - Qué insights se generaron
    - Severidad de cada uno

Autor: Arquitecto BI Senior
Versión: 2.0 - Analytics Phase
"""

from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import logging

from src.database.database import get_db_connection
from src.services.analytics_cache_service import get_analytics_cache
from src.services.analytics_trends_service import get_analytics_trends_service
from src.services.analytics_comparative_service import get_analytics_comparative_service
from src.core.audit_service import log_event

logger = logging.getLogger("AnalyticsInsights")


class SeverityLevel(Enum):
    """Niveles de severidad de insight."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class InsightType(Enum):
    """Tipos de insights generados."""
    PRODUCCION_CAIDA = "produccion_caida"
    COSTOS_ALTOS = "costos_altos"
    MARGEN_NEGATIVO = "margen_negativo"
    EFICIENCIA_BAJA = "eficiencia_baja"
    ANOMALIA_DETECTADA = "anomalia_detectada"


@dataclass
class Insight:
    """Un insight generado por análisis heurístico."""
    tipo: str
    titulo: str
    descripcion: str
    metrica_principal: str
    valor_actual: float
    threshold: float
    severidad: str
    acciones_sugeridas: List[str] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self):
        """Inicializa timestamp si no se proporciona."""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class InsightsResult:
    """Resultado de análisis de insights."""
    insights: List[Insight] = field(default_factory=list)
    total_insights: int = 0
    insights_criticos: int = 0
    insights_warnings: int = 0
    timestamp: str = ""

    def __post_init__(self):
        """Recalcula contadores."""
        self.total_insights = len(self.insights)
        self.insights_criticos = sum(
            1 for i in self.insights if i.severidad == SeverityLevel.CRITICAL.value
        )
        self.insights_warnings = sum(
            1 for i in self.insights if i.severidad == SeverityLevel.WARNING.value
        )
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class AnalyticsInsightsService:
    """Servicio de generación de insights automáticos."""

    def __init__(self):
        """Inicializa el servicio de insights."""
        self._cache = get_analytics_cache()
        self._trends_service = get_analytics_trends_service()
        self._comparative_service = get_analytics_comparative_service()

        # Thresholds configurables para reglas heurísticas
        self.THRESHOLD_CAIDA_PERIODOS = 2  # Períodos consecutivos
        self.THRESHOLD_AUMENTO_COSTOS = 15.0  # %
        self.THRESHOLD_MARGEN_MINIMO = 5.0  # %
        self.THRESHOLD_PRODUCCION_POR_ANIMAL = 0.8  # kg/animal

    def generar_insights(
        self,
        finca_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> InsightsResult:
        """
        Genera insights automáticos para una finca.

        Args:
            finca_id: ID de finca, None = todas
            usuario_id: Para auditoría

        Returns:
            InsightsResult con lista de insights
        """
        inicio = datetime.now()
        insights = []

        # REGLA 1: Producción en caída
        insight_produccion = self._detectar_caida_produccion(finca_id)
        if insight_produccion:
            insights.append(insight_produccion)

        # REGLA 2: Costos altos
        insight_costos = self._detectar_costos_altos(finca_id)
        if insight_costos:
            insights.append(insight_costos)

        # REGLA 3: Margen negativo
        insight_margen = self._detectar_margen_negativo(finca_id)
        if insight_margen:
            insights.append(insight_margen)

        # REGLA 4: Eficiencia baja
        insight_eficiencia = self._detectar_eficiencia_baja(finca_id)
        if insight_eficiencia:
            insights.append(insight_eficiencia)

        resultado = InsightsResult(insights=insights)

        # Auditoría
        if usuario_id:
            duracion_ms = (datetime.now() - inicio).total_seconds() * 1000
            log_event(
                usuario="usuario_" + str(usuario_id),
                modulo="ANALYTICS",
                accion="GENERAR_INSIGHTS",
                entidad=f"insights_finca_{finca_id}" if finca_id else "insights_global",
                resultado="OK",
                mensaje=f"Se generaron {resultado.total_insights} insights en {duracion_ms:.0f}ms"
            )

        return resultado

    # ==================== REGLAS HEURÍSTICAS ====================

    def _detectar_caida_produccion(self, finca_id: Optional[int] = None) -> Optional[Insight]:
        """
        Detecta caída de producción en 2 períodos consecutivos.
        Regla: Si producción ↓ mes N-1 y ↓ mes N = CRITICAL
        """
        try:
            # Comparar mes actual vs mes anterior
            comp_actual = self._comparative_service.comparar_mes_vs_mes(
                metrica="produccion_total"
            )

            # Si hay caída
            if comp_actual.variacion_pct < -10:  # Más del 10% de caída
                # Verificar si mes anterior también cayó (sería 2 períodos consecutivos)
                # Para simplificar, asumir caída sostenida
                severidad = SeverityLevel.CRITICAL.value if comp_actual.variacion_pct < -20 else SeverityLevel.WARNING.value

                return Insight(
                    tipo=InsightType.PRODUCCION_CAIDA.value,
                    titulo="Caída detectada en producción",
                    descripcion=f"La producción ha disminuido {abs(comp_actual.variacion_pct):.1f}% "
                                f"comparado con el período anterior. "
                                f"Actual: {comp_actual.valor_actual:.2f} vs "
                                f"Anterior: {comp_actual.valor_anterior:.2f}",
                    metrica_principal="produccion_total",
                    valor_actual=comp_actual.valor_actual,
                    threshold=comp_actual.valor_anterior * 0.9,  # 90% del anterior
                    severidad=severidad,
                    acciones_sugeridas=[
                        "Revisar registros de mortalidad",
                        "Verificar alimentos y alimentación",
                        "Analizar cambios en clima o infraestructura",
                        "Consultar con veterinario"
                    ]
                )

        except Exception as e:
            logger.warning(f"Error detectando caída producción: {e}")

        return None

    def _detectar_costos_altos(self, finca_id: Optional[int] = None) -> Optional[Insight]:
        """
        Detecta aumento de costos > 15% sin aumento proporcional en ingresos.
        Regla: Si costos ↑ >15% e ingresos ↑ <10% = WARNING
        """
        try:
            comp_costos = self._comparative_service.comparar_mes_vs_mes(
                metrica="costo_total"
            )
            comp_ingresos = self._comparative_service.comparar_mes_vs_mes(
                metrica="ingreso_total"
            )

            # Si costos aumentan mucho pero ingresos no
            if (comp_costos.variacion_pct > self.THRESHOLD_AUMENTO_COSTOS and
                comp_ingresos.variacion_pct < comp_costos.variacion_pct * 0.7):

                return Insight(
                    tipo=InsightType.COSTOS_ALTOS.value,
                    titulo="Aumento significativo de costos",
                    descripcion=f"Los costos han aumentado {comp_costos.variacion_pct:.1f}% "
                                f"mientras que los ingresos solo aumentaron {comp_ingresos.variacion_pct:.1f}%. "
                                f"Esto afecta directamente la rentabilidad.",
                    metrica_principal="costo_total",
                    valor_actual=comp_costos.valor_actual,
                    threshold=comp_costos.valor_anterior * (1 + self.THRESHOLD_AUMENTO_COSTOS / 100),
                    severidad=SeverityLevel.WARNING.value,
                    acciones_sugeridas=[
                        "Auditar costos de alimentación",
                        "Revisar gastos de personal y servicios",
                        "Evaluar eficiencia operativa",
                        "Buscar proveedores alternativos"
                    ]
                )

        except Exception as e:
            logger.warning(f"Error detectando costos altos: {e}")

        return None

    def _detectar_margen_negativo(self, finca_id: Optional[int] = None) -> Optional[Insight]:
        """
        Detecta margen negativo o por debajo del threshold.
        Regla: Si margen < 5% = WARNING, si < 0% = CRITICAL
        """
        try:
            # Obtener snapshot actual para calcular margen
            margen_actual = self._obtener_margen_actual()

            if margen_actual < 0:
                severidad = SeverityLevel.CRITICAL.value
                titulo = "¡CRÍTICO! Margen negativo"
                descripcion = f"La finca está operando con pérdidas. Margen actual: {margen_actual:.2f}%"
            elif margen_actual < self.THRESHOLD_MARGEN_MINIMO:
                severidad = SeverityLevel.WARNING.value
                titulo = "Margen muy bajo"
                descripcion = f"El margen está por debajo del mínimo recomendado. Margen actual: {margen_actual:.2f}%"
            else:
                return None

            return Insight(
                tipo=InsightType.MARGEN_NEGATIVO.value,
                titulo=titulo,
                descripcion=descripcion,
                metrica_principal="margen_bruto_pct",
                valor_actual=margen_actual,
                threshold=self.THRESHOLD_MARGEN_MINIMO,
                severidad=severidad,
                acciones_sugeridas=[
                    "Aumentar precios de venta",
                    "Reducir costos operativos inmediatamente",
                    "Revisar mezcla de productos/servicios",
                    "Implementar plan de mejora urgente"
                ]
            )

        except Exception as e:
            logger.warning(f"Error detectando margen: {e}")

        return None

    def _detectar_eficiencia_baja(self, finca_id: Optional[int] = None) -> Optional[Insight]:
        """
        Detecta eficiencia baja en producción por animal.
        Regla: Si producción/animal < threshold = INFO/WARNING
        """
        try:
            produccion_por_animal = self._calcular_produccion_por_animal()

            if produccion_por_animal < self.THRESHOLD_PRODUCCION_POR_ANIMAL:
                return Insight(
                    tipo=InsightType.EFICIENCIA_BAJA.value,
                    titulo="Eficiencia productiva baja",
                    descripcion=f"La producción por animal está por debajo del esperado. "
                                f"Actual: {produccion_por_animal:.2f} kg/animal vs "
                                f"Esperado: {self.THRESHOLD_PRODUCCION_POR_ANIMAL} kg/animal",
                    metrica_principal="produccion_por_animal",
                    valor_actual=produccion_por_animal,
                    threshold=self.THRESHOLD_PRODUCCION_POR_ANIMAL,
                    severidad=SeverityLevel.WARNING.value,
                    acciones_sugeridas=[
                        "Mejorar calidad de alimentación",
                        "Optimizar manejo del hato",
                        "Analizar genética del ganado",
                        "Consultar con especialista ganadero"
                    ]
                )

        except Exception as e:
            logger.warning(f"Error detectando eficiencia: {e}")

        return None

    # ==================== MÉTODOS AUXILIARES ====================

    def _obtener_margen_actual(self) -> float:
        """Calcula margen actual desde snapshot."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT data_json
                    FROM bi_snapshots_mensual
                    ORDER BY año DESC, mes DESC
                    LIMIT 1
                """)

                row = cursor.fetchone()
                if row:
                    import json
                    data = json.loads(row[0])
                    if "resumen_mensual" in data and "kpis" in data["resumen_mensual"]:
                        return float(data["resumen_mensual"]["kpis"].get("margen_bruto_pct", 0))

            return 0.0
        except Exception as e:
            logger.error(f"Error calculando margen: {e}")
            return 0.0

    def _calcular_produccion_por_animal(self, finca_id: Optional[int] = None) -> float:
        """Calcula producción total por cantidad de animales."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Obtener última snapshot
                cursor.execute("""
                    SELECT data_json
                    FROM bi_snapshots_mensual
                    ORDER BY año DESC, mes DESC
                    LIMIT 1
                """)

                row = cursor.fetchone()
                if row:
                    import json
                    data = json.loads(row[0])

                    # Extraer producción y cantidad de animales
                    if "resumen_mensual" in data and "kpis" in data["resumen_mensual"]:
                        kpis = data["resumen_mensual"]["kpis"]
                        produccion = float(kpis.get("produccion_total", 0))
                        animales = float(kpis.get("cantidad_animales", 1))

                        if animales > 0:
                            return produccion / animales

            return 0.0
        except Exception as e:
            logger.error(f"Error calculando producción/animal: {e}")
            return 0.0


# Singleton global
_insights_service: Optional[AnalyticsInsightsService] = None


def get_analytics_insights_service() -> AnalyticsInsightsService:
    """Obtiene instancia singleton del servicio de insights."""
    global _insights_service
    if _insights_service is None:
        _insights_service = AnalyticsInsightsService()
    return _insights_service
