"""
AI Pattern Detector (FASE 3)

Detecta patrones recurrentes y explicables en KPIs usando snapshots.
- Sin ML
- Lectura SOLO desde bi_snapshots_mensual
- Explicación textual con evidencia
- Integración con cache, auditoría y alertas
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import json

from src.database.database import get_db_connection
from src.services.analytics_cache_service import get_analytics_cache
from src.services.alert_rules_service import get_alert_rules_service
from src.services.system_metrics_service import get_system_metrics_service
from src.core.audit_service import log_event

logger = logging.getLogger("AiPatternDetector")


@dataclass
class PatternInsight:
    tipo: str  # estacionalidad|rampa_costos|rampa_produccion|otros
    metrica: str
    nivel: str  # BAJO|MEDIO|ALTO
    descripcion: str
    evidencia: List[str]
    fecha: str


class AiPatternDetectorService:
    """Servicio de detección de patrones basado en snapshots."""

    METRICAS = ["produccion_total", "costo_total", "ingreso_total", "margen_bruto_pct"]

    def __init__(self) -> None:
        self._cache = get_analytics_cache()
        self._alert_rules = get_alert_rules_service()

    def detectar_patrones(
        self,
        usuario_id: Optional[int] = None,
        incluir_alertas: bool = True
    ) -> List[PatternInsight]:
        inicio = datetime.now()
        cache_key = "ai_patterns_12m"
        cached = self._cache.get_or_calculate(cache_key, lambda: self._compute_patterns())
        if isinstance(cached, str):
            cached = json.loads(cached)
        insights = [PatternInsight(**i) for i in cached]

        if usuario_id is not None:
            duracion_ms = (datetime.now() - inicio).total_seconds() * 1000
            log_event(
                usuario=f"usuario_{usuario_id}",
                modulo="AI",
                accion="DETECCION_PATRONES",
                entidad="global",
                resultado="OK",
                mensaje=f"{len(insights)} patrones detectados en {duracion_ms:.0f}ms"
            )
            # Registrar métrica
            metrics_service = get_system_metrics_service()
            metrics_service.registrar_tiempo_ejecucion(
                "detector_patrones",
                duracion_ms,
                {"resultados": len(insights)}
            )

        if incluir_alertas:
            alertas = self._convertir_a_alertas(insights)
            if alertas:
                try:
                    self._alert_rules.guardar_alertas_en_bd(alertas, usuario=f"usuario_{usuario_id or 'Sistema'}")
                except Exception as e:
                    logger.warning(f"No se pudieron guardar alertas de patrones: {e}")

        return insights

    # ==================== IMPLEMENTACIÓN PRIVADA ====================

    def _compute_patterns(self) -> List[Dict[str, Any]]:
        """Detecta patrones usando últimos 12 meses de snapshots."""
        fin = datetime.now()
        inicio = fin - timedelta(days=365)
        snaps = self._obtener_snapshots_rango(inicio, fin)
        if not snaps:
            return []

        out: List[Dict[str, Any]] = []
        for metrica in self.METRICAS:
            p1 = self._estacionalidad_mes(metrica, snaps)
            if p1:
                out.append(p1)
            p2 = self._rampa_consecutiva(metrica, snaps, tipo="rampa_costos" if metrica == "costo_total" else "rampa_produccion")
            if p2:
                out.append(p2)
        return out

    def _obtener_snapshots_rango(self, inicio: datetime, fin: datetime) -> List[Dict[str, Any]]:
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
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
                snaps: List[Dict[str, Any]] = []
                for año, mes, data_json in rows:
                    try:
                        data = json.loads(data_json)
                        snaps.append({"año": año, "mes": mes, "data": data})
                    except Exception:
                        continue
                return snaps
        except Exception as e:
            logger.error(f"Error obteniendo snapshots: {e}")
            return []

    def _extraer_metrica(self, snap: Dict[str, Any], metrica: str) -> Optional[float]:
        data = snap.get("data", {})
        try:
            kpis = data.get("resumen_mensual", {}).get("kpis", {})
            if metrica in kpis:
                return float(kpis[metrica])
            if "kpis" in data and metrica in data["kpis"]:
                return float(data["kpis"][metrica])
            return None
        except Exception:
            return None

    def _estacionalidad_mes(self, metrica: str, snaps: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detecta si el mes actual está consistentemente por debajo del promedio del mes en años previos."""
        # agrupar por mes
        por_mes: Dict[int, List[float]] = {m: [] for m in range(1, 13)}
        for s in snaps:
            v = self._extraer_metrica(s, metrica)
            if v is not None:
                por_mes[s["mes"]].append(float(v))

        # promedio por mes
        promedios_mes: Dict[int, float] = {m: (sum(vals) / len(vals) if vals else 0.0) for m, vals in por_mes.items()}
        if not promedios_mes:
            return None

        # mes actual
        actual = snaps[-1]
        mes_actual = actual["mes"]
        valor_actual = float(self._extraer_metrica(actual, metrica) or 0.0)
        prom_mes = promedios_mes.get(mes_actual, 0.0)
        if prom_mes <= 0:
            return None

        pct = ((valor_actual - prom_mes) / abs(prom_mes)) * 100
        nivel = "BAJO" if abs(pct) < 10 else ("MEDIO" if abs(pct) < 20 else "ALTO")
        desc = (
            f"{metrica.replace('_',' ')} del mes actual está {('por debajo' if valor_actual < prom_mes else 'por encima')} "
            f"del promedio histórico de este mes ({abs(pct):.1f}%)."
        )
        evidencia = [
            f"Mes {mes_actual:02d}: actual={valor_actual:.2f}, prom_mes={prom_mes:.2f}",
        ]
        return {
            "tipo": "estacionalidad",
            "metrica": metrica,
            "nivel": nivel,
            "descripcion": desc,
            "evidencia": evidencia,
            "fecha": f"{actual['año']}-{actual['mes']:02d}",
        }

    def _rampa_consecutiva(self, metrica: str, snaps: List[Dict[str, Any]], tipo: str) -> Optional[Dict[str, Any]]:
        """Detecta 3 meses consecutivos de aumento (costos) o caída (producción)."""
        vals: List[float] = []
        for s in snaps[-6:]:  # últimos 6 meses
            v = self._extraer_metrica(s, metrica)
            vals.append(float(v or 0))
        if len(vals) < 4:
            return None

        tendencias: List[str] = []
        for i in range(1, len(vals)):
            tendencias.append("up" if vals[i] > vals[i-1] else ("down" if vals[i] < vals[i-1] else "flat"))

        # Regla: 3 en fila
        aumento_3 = any(tendencias[i:i+3] == ["up", "up", "up"] for i in range(len(tendencias)-2))
        caida_3 = any(tendencias[i:i+3] == ["down", "down", "down"] for i in range(len(tendencias)-2))

        if tipo == "rampa_costos" and aumento_3:
            nivel = "ALTO"
            desc = "Costos con aumento consecutivo durante 3 meses. Patrón de rampa detectado."
        elif tipo == "rampa_produccion" and caida_3:
            nivel = "ALTO"
            desc = "Producción con caída consecutiva durante 3 meses. Patrón de rampa detectado."
        else:
            return None

        evidencia = [f"Serie: {', '.join(f'{v:.0f}' for v in vals)}"]
        actual = snaps[-1]
        return {
            "tipo": tipo,
            "metrica": metrica,
            "nivel": nivel,
            "descripcion": desc,
            "evidencia": evidencia,
            "fecha": f"{actual['año']}-{actual['mes']:02d}",
        }

    def _convertir_a_alertas(self, insights: List[PatternInsight]) -> List[Dict[str, Any]]:
        alertas: List[Dict[str, Any]] = []
        for i in insights:
            if i.nivel in ("ALTO", "MEDIO"):
                prioridad = "alta" if i.nivel == "ALTO" else "media"
                alertas.append({
                    "tipo": f"patron_{i.tipo}",
                    "prioridad": prioridad,
                    "titulo": f"Patrón en {i.metrica}",
                    "descripcion": i.descripcion,
                    "entidad_tipo": "bi_snapshot",
                    "entidad_id": i.fecha,
                    "valor_actual": None,
                    "valor_referencia": None,
                })
        return alertas


# Singleton
_ai_pattern_service: Optional[AiPatternDetectorService] = None


def get_ai_pattern_detector_service() -> AiPatternDetectorService:
    global _ai_pattern_service
    if _ai_pattern_service is None:
        _ai_pattern_service = AiPatternDetectorService()
    return _ai_pattern_service
