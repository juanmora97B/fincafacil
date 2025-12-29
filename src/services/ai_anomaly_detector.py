"""
AI Anomaly Detector (FASE 3)

Detecta comportamientos anómalos en métricas clave usando heurísticas y estadística básica.
- Sin ML ni dependencias externas
- Lectura SOLO desde snapshots: bi_snapshots_mensual
- Score 0–100, nivel BAJO/MEDIO/ALTO, explicación textual
- Integración con cache y auditoría
- Generación de alertas (cooldown anti-duplicados)
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json

from src.database.database import get_db_connection
from src.services.analytics_cache_service import get_analytics_cache
from src.services.alert_rules_service import get_alert_rules_service
from src.services.system_metrics_service import get_system_metrics_service
from src.core.audit_service import log_event

logger = logging.getLogger("AiAnomalyDetector")


@dataclass
class AnomalyResult:
    metrica: str
    score: int  # 0–100
    nivel: str  # BAJO | MEDIO | ALTO
    explicacion: str
    valor_actual: float
    promedio_6m: float
    desviacion_std_6m: float
    z_score: float
    fecha: str


class AiAnomalyDetectorService:
    """Servicio de detección de anomalías basado en snapshots."""

    METRICAS_OBJETIVO = [
        "costo_total",
        "ingreso_total",
        "produccion_total",
        "margen_bruto_pct",
        # opcionales si existen en snapshot
        "mortalidad_pct",
    ]

    def __init__(self) -> None:
        self._cache = get_analytics_cache()
        self._alert_rules = get_alert_rules_service()

    def evaluar_anomalias(
        self,
        usuario_id: Optional[int] = None,
        incluir_alertas: bool = True
    ) -> List[AnomalyResult]:
        """
        Evalúa anomalías para métricas objetivo usando últimos 6 meses.
        Returns lista de resultados con score y explicación.
        """
        inicio = datetime.now()
        cache_key = "ai_anomalies_6m"

        cached = self._cache.get_or_calculate(cache_key, lambda: self._compute_all())
        if isinstance(cached, str):
            cached = json.loads(cached)
        resultados = [AnomalyResult(**r) for r in cached]

        # Registrar tiempo de ejecución en métricas
        duracion_ms = (datetime.now() - inicio).total_seconds() * 1000
        metrics_service = get_system_metrics_service()
        metrics_service.registrar_tiempo_ejecucion(
            "detector_anomalias",
            duracion_ms,
            {"resultados": len(resultados)}
        )

        # Auditoría
        if usuario_id is not None:
            log_event(
                usuario=f"usuario_{usuario_id}",
                modulo="AI",
                accion="DETECCION_ANOMALIAS",
                entidad="global",
                resultado="OK",
                mensaje=f"{len(resultados)} anomalías evaluadas en {duracion_ms:.0f}ms"
            )

        # Integración con alertas
        if incluir_alertas:
            alertas = self._convertir_a_alertas(resultados)
            if alertas:
                try:
                    self._alert_rules.guardar_alertas_en_bd(alertas, usuario=f"usuario_{usuario_id or 'Sistema'}")
                except Exception as e:
                    logger.warning(f"No se pudieron guardar alertas de anomalías: {e}")

        return resultados

    # ==================== IMPLEMENTACIÓN PRIVADA ====================

    def _compute_all(self) -> List[Dict[str, Any]]:
        """Calcula anomalías para todas las métricas objetivo."""
        fin = datetime.now()
        inicio = fin - timedelta(days=180)
        snapshots = self._obtener_snapshots_rango(inicio, fin)
        if not snapshots:
            return []

        resultados: List[Dict[str, Any]] = []
        for metrica in self.METRICAS_OBJETIVO:
            res = self._evaluar_metrica(metrica, snapshots)
            if res is not None:
                resultados.append(res)
        return resultados

    def _obtener_snapshots_rango(self, inicio: datetime, fin: datetime) -> List[Dict[str, Any]]:
        """Obtiene snapshots entre fechas (incluye año/mes al filtrar)."""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                # Suponemos columnas: año (int), mes (int), data_json (text)
                cur.execute(
                    """
                    SELECT año, mes, data_json
                    FROM bi_snapshots_mensual
                    WHERE date(año || '-' || printf('%02d', mes) || '-01') BETWEEN ? AND ?
                    ORDER BY año ASC, mes ASC
                    """,
                    (inicio.date(), fin.date()),
                )
                rows = cur.fetchall()
                out: List[Dict[str, Any]] = []
                for año, mes, data_json in rows:
                    try:
                        data = json.loads(data_json)
                        out.append({"año": año, "mes": mes, "data": data})
                    except Exception:
                        continue
                return out
        except Exception as e:
            logger.error(f"Error obteniendo snapshots: {e}")
            return []

    def _extraer_metrica(self, snap: Dict[str, Any], metrica: str) -> Optional[float]:
        """Extrae valor de métrica desde estructura JSON conocida."""
        data = snap.get("data", {})
        try:
            if "resumen_mensual" in data and "kpis" in data["resumen_mensual"]:
                kpis = data["resumen_mensual"]["kpis"]
                if metrica in kpis:
                    return float(kpis[metrica])
            if "kpis" in data and metrica in data["kpis"]:
                return float(data["kpis"][metrica])
            return None
        except Exception:
            return None

    def _evaluar_metrica(self, metrica: str, snaps: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Calcula score y explicación para una métrica contra 6 meses previos."""
        # Tomar últimos 6 y el último como "actual"
        valores: List[Tuple[str, float]] = []
        for s in snaps[-7:]:  # hasta 7 meses para tener 6 previos + actual
            val = self._extraer_metrica(s, metrica)
            if val is not None:
                etiqueta = f"{s['año']}-{s['mes']:02d}"
                valores.append((etiqueta, float(val)))

        if len(valores) < 3:
            return None

        # Separar actual vs históricos (previos 6)
        actual_etq, actual = valores[-1]
        previos = [v for _, v in valores[:-1]][-6:]
        if len(previos) == 0:
            return None

        promedio = sum(previos) / len(previos)
        varianza = sum((v - promedio) ** 2 for v in previos) / len(previos)
        std = varianza ** 0.5

        # z-score del actual
        z = 0.0 if std == 0 else (actual - promedio) / std

        # desviación porcentual
        pct = 0.0 if promedio == 0 else ((actual - promedio) / abs(promedio)) * 100

        # score heurístico 0–100 (combinando magnitud de z y %)
        score_raw = abs(z) * 20 + abs(pct) * 0.5  # ponderación balanceada
        score = max(0, min(100, int(round(score_raw))))

        if score < 30:
            nivel = "BAJO"
        elif score < 60:
            nivel = "MEDIO"
        else:
            nivel = "ALTO"

        direccion = "aumentó" if actual >= promedio else "disminuyó"
        explicacion = (
            f"{metrica.replace('_',' ')} {direccion} {abs(pct):.1f}% respecto al promedio de 6 meses. "
            f"z={z:.2f}, actual={actual:.2f}, promedio={promedio:.2f}"
        )

        return {
            "metrica": metrica,
            "score": score,
            "nivel": nivel,
            "explicacion": explicacion,
            "valor_actual": float(actual),
            "promedio_6m": float(promedio),
            "desviacion_std_6m": float(std),
            "z_score": float(z),
            "fecha": actual_etq,
        }

    def _convertir_a_alertas(self, resultados: List[AnomalyResult]) -> List[Dict[str, Any]]:
        """Convierte anomalías con nivel ALTO/MEDIO a alertas para el sistema."""
        alertas: List[Dict[str, Any]] = []
        for r in resultados:
            if r.nivel in ("ALTO", "MEDIO"):
                prioridad = "alta" if r.nivel == "ALTO" else "media"
                tipo = "anomalia_financiera" if "costo" in r.metrica or "ingreso" in r.metrica or "margen" in r.metrica else "anomalia_productiva"
                alertas.append({
                    "tipo": tipo,
                    "prioridad": prioridad,
                    "titulo": f"Anomalía en {r.metrica}",
                    "descripcion": r.explicacion,
                    "entidad_tipo": "bi_snapshot",
                    "entidad_id": r.fecha,
                    "valor_actual": r.valor_actual,
                    "valor_referencia": r.promedio_6m,
                })
        return alertas


# Singleton
_ai_anomaly_service: Optional[AiAnomalyDetectorService] = None


def get_ai_anomaly_detector_service() -> AiAnomalyDetectorService:
    global _ai_anomaly_service
    if _ai_anomaly_service is None:
        _ai_anomaly_service = AiAnomalyDetectorService()
    return _ai_anomaly_service
