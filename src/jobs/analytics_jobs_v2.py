"""Trabajos (Jobs) para agregación de analytics - VERSION 2.

Ejecutan consultas reales sobre datos operacionales y escriben en read models.
Diseñados para ejecutarse con APScheduler (hourly).
Cada job es idempotente: puede ejecutarse múltiples veces sin efectos secundarios.

QUERIES REALES conectadas a:
- animal (nacimiento, destete, muerte)
- evento (Reproductivo, Sanitario)
- movimiento (traslados)
- alerta (activas, resueltas, críticas)
- sugerencia_ia (generadas, aceptadas, confianza)
- orquestacion (ejecutadas, exitosas, fallidas)
- killswitch_log (activaciones)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

from src.infraestructura.analytics.analytics_service import AnalyticsService
from src.database.database import ejecutar_consulta


logger = logging.getLogger(__name__)


class BuildProductivityAnalyticsJob:
    """Agrega datos de productividad (nacimientos, destetes, muertes, etc.)"""

    def __init__(self, service: AnalyticsService):
        self.service = service

    def ejecutar(self, empresa_id: int, fecha: Optional[str] = None) -> Dict:
        """
        Construir analítica de productividad.
        
        Args:
            empresa_id: ID de empresa
            fecha: Fecha a procesar (YYYY-MM-DD). Si no se proporciona, usa hoy.
        
        Returns:
            Diccionario con resultados de agregación
        """
        fecha = fecha or datetime.now().strftime("%Y-%m-%d")
        
        try:
            # ==================== QUERIES REALES ====================
            
            # Nacimientos (eventos de tipo nacimiento registrados en la fecha)
            nacimientos_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM evento
                WHERE empresa_id = ? 
                  AND tipo_evento = 'Reproductivo'
                  AND descripcion LIKE '%nacimiento%'
                  AND DATE(fecha_evento) = ?
                """,
                (empresa_id, fecha),
            )
            nacimientos = nacimientos_result[0]['total'] if nacimientos_result else 0
            
            # Destetes (animales con fecha_destete = fecha)
            destetes_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM animal
                WHERE empresa_id = ? 
                  AND DATE(fecha_destete) = ?
                """,
                (empresa_id, fecha),
            )
            destetes = destetes_result[0]['total'] if destetes_result else 0
            
            # Muertes (animales con fecha_muerte = fecha)
            muertes_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM animal
                WHERE empresa_id = ? 
                  AND DATE(fecha_muerte) = ?
                """,
                (empresa_id, fecha),
            )
            muertes = muertes_result[0]['total'] if muertes_result else 0
            
            # Traslados (movimientos de tipo 'Traslado' en la fecha)
            traslados_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM movimiento m
                JOIN animal a ON m.animal_id = a.id
                WHERE a.empresa_id = ? 
                  AND m.tipo_movimiento = 'Traslado'
                  AND DATE(m.fecha_movimiento) = ?
                """,
                (empresa_id, fecha),
            )
            traslados = traslados_result[0]['total'] if traslados_result else 0
            
            # Servicios (evento de tipo Reproductivo con 'servicio')
            servicios_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM evento
                WHERE empresa_id = ? 
                  AND tipo_evento = 'Reproductivo'
                  AND descripcion LIKE '%servicio%'
                  AND DATE(fecha_evento) = ?
                """,
                (empresa_id, fecha),
            )
            servicios = servicios_result[0]['total'] if servicios_result else 0
            
            # Partos (eventos con tipo 'parto')
            partos_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM evento
                WHERE empresa_id = ? 
                  AND tipo_evento = 'Reproductivo'
                  AND descripcion LIKE '%parto%'
                  AND DATE(fecha_evento) = ?
                """,
                (empresa_id, fecha),
            )
            partos = partos_result[0]['total'] if partos_result else 0
            
            # Registrar en read model
            self.service.registrar_productividad(
                empresa_id=empresa_id,
                fecha=fecha,
                data={
                    'nacimientos': nacimientos,
                    'destetes': destetes,
                    'muertes': muertes,
                    'traslados': traslados,
                    'servicios': servicios,
                    'partos': partos,
                    'animales_totales': 0,  # Será calculado por repo
                    'lote_id': None,
                    'sector_id': None,
                }
            )
            
            logger.info(
                f"✓ Productividad agregada: {fecha} empresa={empresa_id} "
                f"nacimientos={nacimientos} destetes={destetes} muertes={muertes}"
            )
            
            return {
                "status": "success",
                "fecha": fecha,
                "nacimientos": nacimientos,
                "destetes": destetes,
                "muertes": muertes,
            }
        except Exception as e:
            logger.error(f"✗ Error en BuildProductivityAnalyticsJob: {e}", exc_info=True)
            return {"status": "error", "mensaje": str(e)}


class BuildAlertAnalyticsJob:
    """Agrega datos de alertas (activas, resueltas, por tipo)"""

    def __init__(self, service: AnalyticsService):
        self.service = service

    def ejecutar(self, empresa_id: int, fecha: Optional[str] = None) -> Dict:
        """Construir analítica de alertas."""
        fecha = fecha or datetime.now().strftime("%Y-%m-%d")
        
        try:
            # ==================== QUERIES REALES ====================
            
            # Alertas activas (estado = 'Activa')
            activas_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM alerta
                WHERE empresa_id = ? 
                  AND estado = 'Activa'
                """,
                (empresa_id,),
            )
            alertas_activas = activas_result[0]['total'] if activas_result else 0
            
            # Alertas resueltas en la fecha
            resueltas_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM alerta
                WHERE empresa_id = ? 
                  AND estado = 'Resuelta'
                  AND DATE(fecha_resolucion) = ?
                """,
                (empresa_id, fecha),
            )
            alertas_resueltas = resueltas_result[0]['total'] if resueltas_result else 0
            
            # Alertas críticas activas (prioridad = 'Crítica')
            criticas_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM alerta
                WHERE empresa_id = ? 
                  AND estado = 'Activa'
                  AND prioridad = 'Crítica'
                """,
                (empresa_id,),
            )
            alertas_criticas = criticas_result[0]['total'] if criticas_result else 0
            
            # Registrar en read model
            self.service.registrar_alerta(
                empresa_id=empresa_id,
                fecha=fecha,
                data={
                    'total_activas': alertas_activas,
                    'total_resueltas': alertas_resueltas,
                    'criticas_activas': alertas_criticas,
                    'sanitarias_activas': 0,
                    'reproductivas_activas': 0,
                    'zootecnicas_activas': 0,
                }
            )
            
            logger.info(
                f"✓ Alertas agregadas: {fecha} empresa={empresa_id} "
                f"activas={alertas_activas} resueltas={alertas_resueltas}"
            )
            
            return {
                "status": "success",
                "fecha": fecha,
                "activas": alertas_activas,
                "resueltas": alertas_resueltas,
            }
        except Exception as e:
            logger.error(f"✗ Error en BuildAlertAnalyticsJob: {e}", exc_info=True)
            return {"status": "error", "mensaje": str(e)}


class BuildIAAnalyticsJob:
    """Agrega datos de IA (sugerencias, aceptación, precisión)"""

    def __init__(self, service: AnalyticsService):
        self.service = service

    def ejecutar(self, empresa_id: int, fecha: Optional[str] = None) -> Dict:
        """Construir analítica de IA."""
        fecha = fecha or datetime.now().strftime("%Y-%m-%d")
        
        try:
            # ==================== QUERIES REALES ====================
            
            # Sugerencias generadas en la fecha
            generadas_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM sugerencia_ia
                WHERE empresa_id = ? 
                  AND DATE(fecha_creacion) = ?
                """,
                (empresa_id, fecha),
            )
            sugerencias_generadas = generadas_result[0]['total'] if generadas_result else 0
            
            # Sugerencias aceptadas en la fecha
            aceptadas_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM sugerencia_ia
                WHERE empresa_id = ? 
                  AND estado_aceptacion = 'Aceptada'
                  AND DATE(fecha_aceptacion) = ?
                """,
                (empresa_id, fecha),
            )
            sugerencias_aceptadas = aceptadas_result[0]['total'] if aceptadas_result else 0
            
            # Tasa de aceptación (total aceptadas / total generadas)
            tasa_aceptacion = (
                (sugerencias_aceptadas / sugerencias_generadas * 100)
                if sugerencias_generadas > 0
                else 0.0
            )
            
            # Impacto estimado (suma de impacto_estimado_pesos)
            impacto_result = ejecutar_consulta(
                """
                SELECT SUM(COALESCE(impacto_estimado_pesos, 0)) as total
                FROM sugerencia_ia
                WHERE empresa_id = ? 
                  AND estado_aceptacion = 'Aceptada'
                  AND DATE(fecha_aceptacion) = ?
                """,
                (empresa_id, fecha),
            )
            impacto_estimado = (
                float(impacto_result[0]['total']) if impacto_result and impacto_result[0]['total'] else 0.0
            )
            
            # Precisión histórica (promedio de confianza de sugerencias aceptadas)
            precision_result = ejecutar_consulta(
                """
                SELECT AVG(COALESCE(nivel_confianza, 0)) as promedio
                FROM sugerencia_ia
                WHERE empresa_id = ? 
                  AND estado_aceptacion = 'Aceptada'
                """,
                (empresa_id,),
            )
            precision = (
                float(precision_result[0]['promedio']) if precision_result and precision_result[0]['promedio'] else 0.0
            )
            
            # Registrar en read model
            self.service.registrar_ia(
                empresa_id=empresa_id,
                fecha=fecha,
                data={
                    'sugerencias_generadas': sugerencias_generadas,
                    'sugerencias_aceptadas': sugerencias_aceptadas,
                    'tasa_aceptacion_pct': tasa_aceptacion,
                    'impacto_estimado_pesos': impacto_estimado,
                    'precision_historica_pct': precision,
                    'modelo_version': '1.0',
                }
            )
            
            logger.info(
                f"✓ IA agregada: {fecha} empresa={empresa_id} "
                f"sugerencias={sugerencias_generadas} aceptadas={sugerencias_aceptadas} "
                f"precision={precision:.1f}%"
            )
            
            return {
                "status": "success",
                "fecha": fecha,
                "sugerencias": sugerencias_generadas,
                "aceptadas": sugerencias_aceptadas,
                "precision": precision,
            }
        except Exception as e:
            logger.error(f"✗ Error en BuildIAAnalyticsJob: {e}", exc_info=True)
            return {"status": "error", "mensaje": str(e)}


class BuildAutonomyAnalyticsJob:
    """Agrega datos de autonomía (orquestaciones, rollbacks, kill switch)"""

    def __init__(self, service: AnalyticsService):
        self.service = service

    def ejecutar(self, empresa_id: int, fecha: Optional[str] = None) -> Dict:
        """Construir analítica de autonomía."""
        fecha = fecha or datetime.now().strftime("%Y-%m-%d")
        
        try:
            # ==================== QUERIES REALES ====================
            
            # Orquestaciones ejecutadas en la fecha
            ejecutadas_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM orquestacion
                WHERE empresa_id = ? 
                  AND DATE(fecha_ejecucion) = ?
                """,
                (empresa_id, fecha),
            )
            orquestaciones_ejecutadas = ejecutadas_result[0]['total'] if ejecutadas_result else 0
            
            # Orquestaciones exitosas (estado = 'Exitosa')
            exitosas_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM orquestacion
                WHERE empresa_id = ? 
                  AND estado_ejecucion = 'Exitosa'
                  AND DATE(fecha_ejecucion) = ?
                """,
                (empresa_id, fecha),
            )
            orquestaciones_exitosas = exitosas_result[0]['total'] if exitosas_result else 0
            
            # Orquestaciones fallidas
            orquestaciones_fallidas = orquestaciones_ejecutadas - orquestaciones_exitosas
            
            # Tasa de éxito
            tasa_exito = (
                (orquestaciones_exitosas / orquestaciones_ejecutadas * 100)
                if orquestaciones_ejecutadas > 0
                else 0.0
            )
            
            # Kill switch activaciones en la fecha
            killswitch_result = ejecutar_consulta(
                """
                SELECT COUNT(*) as total
                FROM killswitch_log
                WHERE empresa_id = ? 
                  AND DATE(fecha_activacion) = ?
                """,
                (empresa_id, fecha),
            )
            kill_switch_activaciones = killswitch_result[0]['total'] if killswitch_result else 0
            
            # Registrar en read model
            self.service.registrar_autonomia(
                empresa_id=empresa_id,
                fecha=fecha,
                data={
                    'orquestaciones_ejecutadas': orquestaciones_ejecutadas,
                    'orquestaciones_exitosas': orquestaciones_exitosas,
                    'orquestaciones_fallidas': orquestaciones_fallidas,
                    'rollbacks_activados': 0,
                    'autonomia_estado': 'ON',
                    'tasa_exito_pct': tasa_exito,
                    'kill_switch_activaciones': kill_switch_activaciones,
                }
            )
            
            logger.info(
                f"✓ Autonomía agregada: {fecha} empresa={empresa_id} "
                f"orquestaciones={orquestaciones_ejecutadas} éxito={tasa_exito:.1f}%"
            )
            
            return {
                "status": "success",
                "fecha": fecha,
                "orquestaciones": orquestaciones_ejecutadas,
                "tasa_exito": tasa_exito,
            }
        except Exception as e:
            logger.error(f"✗ Error en BuildAutonomyAnalyticsJob: {e}", exc_info=True)
            return {"status": "error", "mensaje": str(e)}


# ==================== JOBS CONFIGURATION ====================

JOBS_CONFIG = {
    "BuildProductivityAnalyticsJob": {
        "class": BuildProductivityAnalyticsJob,
        "trigger": "cron",
        "hour": "*",
        "minute": "0",  # Cada hora en :00
        "second": 0,
    },
    "BuildAlertAnalyticsJob": {
        "class": BuildAlertAnalyticsJob,
        "trigger": "cron",
        "hour": "*",
        "minute": "15",  # Cada hora en :15
        "second": 0,
    },
    "BuildIAAnalyticsJob": {
        "class": BuildIAAnalyticsJob,
        "trigger": "cron",
        "hour": "*",
        "minute": "30",  # Cada hora en :30
        "second": 0,
    },
    "BuildAutonomyAnalyticsJob": {
        "class": BuildAutonomyAnalyticsJob,
        "trigger": "cron",
        "hour": "*",
        "minute": "45",  # Cada hora en :45
        "second": 0,
    },
}
