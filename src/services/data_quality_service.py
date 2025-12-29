"""
╔══════════════════════════════════════════════════════════════════════════╗
║           SERVICIO DE CALIDAD DE DATOS - FASE 8                          ║
╚══════════════════════════════════════════════════════════════════════════╝

Valida la confiabilidad analítica de snapshots y KPIs.

Responsabilidades:
1. Validar integridad de snapshots (KPIs faltantes, valores inválidos)
2. Detectar datos incompletos (faltan días de registro, etc.)
3. Clasificar calidad: ALTA / MEDIA / BAJA
4. Generar reportes de calidad por período
5. Integración con alertas técnicas (no productivas)

Salida tipificada:
{
  "periodo": "2025-01",
  "calidad": "MEDIA",
  "score": 72,
  "problemas": ["Producción sin registros 3 días", "Margen fuera de rango"],
  "kpis_validados": 8,
  "kpis_faltantes": 2
}
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
import json

from src.database.database import get_db_connection
from src.core.audit_service import log_event

logger = logging.getLogger("DataQuality")


@dataclass
class QualityReport:
    periodo: str  # YYYY-MM
    calidad: str  # ALTA | MEDIA | BAJA
    score: int  # 0-100
    problemas: List[str]
    kpis_validados: int
    kpis_faltantes: int
    valor_incompleto: int
    valores_atipicos: int
    fecha_generacion: str


class DataQualityService:
    """Servicio de validación de calidad de datos analíticos."""

    # KPIs esperados en snapshots
    KPIS_REQUERIDOS = [
        "costo_total",
        "ingreso_total",
        "produccion_total",
        "margen_bruto",
        "margen_bruto_pct",
    ]

    # Rangos válidos por métrica (min, max) - ajustables
    RANGOS_VALIDOS = {
        "costo_total": (0, 1_000_000),
        "ingreso_total": (0, 2_000_000),
        "produccion_total": (0, 50_000),  # litros/mes
        "margen_bruto": (-500_000, 1_000_000),
        "margen_bruto_pct": (-100, 100),
        "tasa_prenez": (0, 100),
        "mortalidad_pct": (0, 100),
    }

    def __init__(self) -> None:
        self.logger = logger

    def evaluar_calidad_periodo(
        self,
        año: int,
        mes: int,
        usuario_id: Optional[int] = None
    ) -> QualityReport:
        """
        Evalúa la calidad de datos para un período específico.

        Args:
            año: Año (ej: 2025)
            mes: Mes (1-12)
            usuario_id: ID del usuario para auditoría

        Returns:
            Reporte de calidad estructurado
        """
        periodo_str = f"{año}-{mes:02d}"
        inicio = datetime.now()

        try:
            # Obtener snapshot del período
            snapshot = self._obtener_snapshot(año, mes)
            if not snapshot:
                return QualityReport(
                    periodo=periodo_str,
                    calidad="BAJA",
                    score=0,
                    problemas=["Snapshot no encontrado para el período"],
                    kpis_validados=0,
                    kpis_faltantes=len(self.KPIS_REQUERIDOS),
                    valor_incompleto=0,
                    valores_atipicos=0,
                    fecha_generacion=datetime.now().isoformat(),
                )

            # Validar KPIs
            data = json.loads(snapshot["data_json"]) if isinstance(snapshot["data_json"], str) else snapshot["data_json"]
            kpis = data.get("resumen_mensual", {}).get("kpis", {})

            problemas = []
            validados = 0
            faltantes = 0
            incompleto = 0
            atipicos = 0

            # 1. Verificar KPIs requeridos
            for kpi in self.KPIS_REQUERIDOS:
                if kpi not in kpis:
                    faltantes += 1
                    problemas.append(f"KPI faltante: {kpi}")
                else:
                    validados += 1
                    valor = kpis[kpi]

                    # 2. Validar rango
                    if kpi in self.RANGOS_VALIDOS:
                        min_val, max_val = self.RANGOS_VALIDOS[kpi]
                        if not (min_val <= valor <= max_val):
                            atipicos += 1
                            problemas.append(
                                f"{kpi} fuera de rango: {valor} (esperado {min_val}-{max_val})"
                            )

            # 3. Detectar datos incompletos
            dias_esperados = self._dias_en_mes(año, mes)
            dias_con_datos = self._contar_registros_produccion(año, mes)
            if dias_con_datos < dias_esperados * 0.8:  # < 80% de días
                incompleto = dias_esperados - dias_con_datos
                problemas.append(
                    f"Registros de producción incompletos: {dias_con_datos}/{dias_esperados} días"
                )

            # 4. Detectar inconsistencias lógicas
            if "margen_bruto" in kpis and "ingreso_total" in kpis and "costo_total" in kpis:
                margen_calc = kpis["ingreso_total"] - kpis["costo_total"]
                margen_snapshot = kpis["margen_bruto"]
                if abs(margen_calc - margen_snapshot) > 100:  # Tolerancia 100
                    problemas.append(
                        f"Inconsistencia: margen calculado ({margen_calc}) != snapshot ({margen_snapshot})"
                    )

            # 5. Calcular score de calidad (0-100)
            score = self._calcular_score_calidad(
                validados, faltantes, atipicos, incompleto, len(problemas)
            )

            # 6. Clasificar calidad
            if score >= 85:
                calidad = "ALTA"
            elif score >= 70:
                calidad = "MEDIA"
            else:
                calidad = "BAJA"

            reporte = QualityReport(
                periodo=periodo_str,
                calidad=calidad,
                score=score,
                problemas=problemas,
                kpis_validados=validados,
                kpis_faltantes=faltantes,
                valor_incompleto=incompleto,
                valores_atipicos=atipicos,
                fecha_generacion=datetime.now().isoformat(),
            )

            # Auditoría
            if usuario_id is not None:
                duracion_ms = (datetime.now() - inicio).total_seconds() * 1000
                log_event(
                    usuario=f"usuario_{usuario_id}",
                    modulo="DATA_QUALITY",
                    accion="EVALUAR",
                    entidad=periodo_str,
                    resultado="OK",
                    mensaje=f"Calidad: {calidad} (score {score})",
                )

            self.logger.info(f"Calidad período {periodo_str}: {calidad} (score {score})")
            return reporte

        except Exception as e:
            self.logger.error(f"Error evaluando calidad {periodo_str}: {e}")
            return QualityReport(
                periodo=periodo_str,
                calidad="BAJA",
                score=0,
                problemas=[f"Error durante evaluación: {str(e)}"],
                kpis_validados=0,
                kpis_faltantes=len(self.KPIS_REQUERIDOS),
                valor_incompleto=0,
                valores_atipicos=0,
                fecha_generacion=datetime.now().isoformat(),
            )

    # ==================== PRIVADOS ====================

    def _obtener_snapshot(self, año: int, mes: int) -> Optional[Dict[str, Any]]:
        """Obtiene snapshot del período especificado."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT año, mes, data_json FROM bi_snapshots_mensual WHERE año = ? AND mes = ?",
                    (año, mes),
                )
                row = cursor.fetchone()
                if row:
                    return {"año": row[0], "mes": row[1], "data_json": row[2]}
                return None
        except Exception as e:
            self.logger.warning(f"Error obtener snapshot {año}-{mes}: {e}")
            return None

    def _dias_en_mes(self, año: int, mes: int) -> int:
        """Retorna cantidad de días en el mes."""
        if mes == 12:
            return 31
        import calendar
        return calendar.monthrange(año, mes)[1]

    def _contar_registros_produccion(self, año: int, mes: int) -> int:
        """Cuenta días con registros de producción en el mes."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT COUNT(DISTINCT fecha)
                    FROM produccion_leche
                    WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
                    """,
                    (f"{año:04d}", f"{mes:02d}"),
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def _calcular_score_calidad(
        self,
        validados: int,
        faltantes: int,
        atipicos: int,
        incompleto: int,
        problemas: int,
    ) -> int:
        """Calcula score de calidad (0-100) usando ponderación."""
        total_kpis = validados + faltantes
        if total_kpis == 0:
            return 0

        # Componentes
        cobertura = (validados / total_kpis) * 40  # máx 40 puntos
        consistencia = max(0, 30 - atipicos * 5)  # máx 30, -5 por atípico
        completitud = max(0, 20 - incompleto * 2)  # máx 20, -2 por día faltante
        problemas_score = max(0, 10 - problemas)  # máx 10, -1 por problema

        score = int(cobertura + consistencia + completitud + problemas_score)
        return max(0, min(100, score))


# Singleton
_data_quality_service: Optional[DataQualityService] = None


def get_data_quality_service() -> DataQualityService:
    """Obtiene la instancia singleton del servicio de calidad de datos."""
    global _data_quality_service
    if _data_quality_service is None:
        _data_quality_service = DataQualityService()
    return _data_quality_service
