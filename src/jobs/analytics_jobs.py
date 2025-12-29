"""
Agregaciones para Analytics - Jobs que construyen read models
Se ejecutan cada hora y nocturno para recálculos históricos
"""
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BuildProductivityAnalyticsJob:
    """Job que agrega datos de productividad: nacimientos, destetes, muertes, traslados."""
    
    def __init__(self, analytics_service):
        self.analytics = analytics_service
        self.animal_svc = None
        self.config_svc = None
    
    def ejecutar(self, empresa_id: int = 1, fecha: Optional[str] = None) -> None:
        """Ejecuta agregación de productividad."""
        if not fecha:
            fecha = datetime.now().date().isoformat()
        
        logger.info(f"[ProductivityJob] Iniciando para {fecha}...")
        
        try:
            # Contar eventos del día por lote/sector
            nacimientos = 10  # Mock: conectar con animal_service cuando esté disponible
            destetes = 5
            muertes = 2
            traslados = 8
            servicios = 3
            partos = 1
            
            # Registrar agregación
            self.analytics.registrar_productividad(empresa_id, fecha, {
                'lote_id': None,
                'sector_id': None,
                'animales_totales': 245,
                'nacimientos': nacimientos,
                'destetes': destetes,
                'muertes': muertes,
                'traslados': traslados,
                'servicios': servicios,
                'partos': partos,
                'mortalidad_pct': (muertes / 245 * 100) if 245 > 0 else 0,
                'natalidad_pct': (nacimientos / 245 * 100) if 245 > 0 else 0,
            })
            
            logger.info(f"[ProductivityJob] Completado: {nacimientos} nac, {muertes} muertes, {traslados} trasl")
        except Exception as e:
            logger.error(f"[ProductivityJob] Error: {e}")
            raise


class BuildAlertAnalyticsJob:
    """Job que agrega datos de alertas: conteos y tiempos de resolución."""
    
    def __init__(self, analytics_service):
        self.analytics = analytics_service
    
    def ejecutar(self, empresa_id: int = 1, fecha: Optional[str] = None) -> None:
        """Ejecuta agregación de alertas."""
        if not fecha:
            fecha = datetime.now().date().isoformat()
        
        logger.info(f"[AlertJob] Iniciando para {fecha}...")
        
        try:
            tipos = ['Sanitaria', 'Nutricional', 'Reproductiva', 'Operacional']
            
            for tipo in tipos:
                # Mock: conectar con servicio de alertas
                total_activas = 3
                total_resueltas = 8
                criticas = 1
                tiempo_promedio = 120  # minutos
                
                self.analytics.registrar_alerta(empresa_id, fecha, {
                    'tipo_alerta': tipo,
                    'total_activas': total_activas,
                    'total_resueltas': total_resueltas,
                    'criticas_activas': criticas,
                    'tiempo_promedio_resolucion': tiempo_promedio,
                })
            
            logger.info(f"[AlertJob] Completado: {len(tipos)} tipos procesados")
        except Exception as e:
            logger.error(f"[AlertJob] Error: {e}")
            raise


class BuildIAAnalyticsJob:
    """Job que agrega datos de IA: sugerencias aceptadas, impacto, precisión."""
    
    def __init__(self, analytics_service):
        self.analytics = analytics_service
    
    def ejecutar(self, empresa_id: int = 1, fecha: Optional[str] = None) -> None:
        """Ejecuta agregación de IA."""
        if not fecha:
            fecha = datetime.now().date().isoformat()
        
        logger.info(f"[IAJob] Iniciando para {fecha}...")
        
        try:
            # Mock: conectar con servicio de IA
            sugerencias_gen = 15
            aceptadas = 10
            rechazadas = 5
            
            self.analytics.registrar_ia(empresa_id, fecha, {
                'sugerencias_generadas': sugerencias_gen,
                'sugerencias_aceptadas': aceptadas,
                'sugerencias_rechazadas': rechazadas,
                'tasa_aceptacion_pct': (aceptadas / sugerencias_gen * 100) if sugerencias_gen > 0 else 0,
                'impacto_estimado_pesos': 125000.0,  # Estimado
                'precision_historica_pct': 87.5,
                'modelo_version': 'v2.1',
            })
            
            logger.info(f"[IAJob] Completado: {aceptadas} de {sugerencias_gen} aceptadas")
        except Exception as e:
            logger.error(f"[IAJob] Error: {e}")
            raise


class BuildAutonomyAnalyticsJob:
    """Job que agrega datos de autonomía: orquestaciones, rollbacks, kill switch."""
    
    def __init__(self, analytics_service):
        self.analytics = analytics_service
    
    def ejecutar(self, empresa_id: int = 1, fecha: Optional[str] = None) -> None:
        """Ejecuta agregación de autonomía."""
        if not fecha:
            fecha = datetime.now().date().isoformat()
        
        logger.info(f"[AutonomyJob] Iniciando para {fecha}...")
        
        try:
            # Mock: conectar con servicio de orquestación
            ejecutadas = 12
            exitosas = 11
            fallidas = 1
            rollbacks = 0
            kill_switch = 0
            
            self.analytics.registrar_autonomia(empresa_id, fecha, {
                'orquestaciones_ejecutadas': ejecutadas,
                'orquestaciones_exitosas': exitosas,
                'orquestaciones_fallidas': fallidas,
                'rollbacks_activados': rollbacks,
                'autonomia_estado': 'ON',
                'kill_switch_activaciones': kill_switch,
            })
            
            logger.info(f"[AutonomyJob] Completado: {exitosas}/{ejecutadas} exitosas")
        except Exception as e:
            logger.error(f"[AutonomyJob] Error: {e}")
            raise


# Scheduler configuration (para usar con APScheduler)
JOBS_CONFIG = [
    {
        'id': 'build_productivity_analytics',
        'trigger': 'cron',
        'hour': '*/1',  # Cada hora
        'minute': '0',
        'job_class': BuildProductivityAnalyticsJob,
        'args': [],
    },
    {
        'id': 'build_alert_analytics',
        'trigger': 'cron',
        'hour': '*/1',
        'minute': '15',
        'job_class': BuildAlertAnalyticsJob,
        'args': [],
    },
    {
        'id': 'build_ia_analytics',
        'trigger': 'cron',
        'hour': '*/1',
        'minute': '30',
        'job_class': BuildIAAnalyticsJob,
        'args': [],
    },
    {
        'id': 'build_autonomy_analytics',
        'trigger': 'cron',
        'hour': '*/1',
        'minute': '45',
        'job_class': BuildAutonomyAnalyticsJob,
        'args': [],
    },
]
