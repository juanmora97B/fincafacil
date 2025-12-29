"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    SERVICIO CENTRAL DE REPORTES                          ║
║                         FASE 3 - FincaFácil                              ║
╚══════════════════════════════════════════════════════════════════════════╝

Propósito:
    Orquestador central que coordina la generación de reportes operativos,
    delegando a servicios especializados y proporcionando una API unificada.

Responsabilidades:
    - Coordinar reportes de animales, reproducción, producción y finanzas
    - Validar parámetros de entrada (fechas, formatos)
    - Manejo centralizado de errores
    - Logging de operaciones de reporte

Autor: Arquitecto Senior - Fase 3
Fecha: Diciembre 2025
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import logging

from src.reports.reporte_animales import ReporteAnimales
from src.reports.reporte_reproduccion import ReporteReproduccion
from src.reports.reporte_produccion import ReporteProduccion
from src.reports.reporte_finanzas import ReporteFinanzas


class ReportesService:
    """
    Servicio central de reportes - Orquestador FASE 3.
    
    Principios:
        - No genera vistas HTML/PDF directamente
        - Retorna datos estructurados (dict/list)
        - Reutilizable por UI, exportadores y auditorías
        - Valida parámetros y maneja errores
    """
    
    TIPOS_REPORTE = [
        'animales',
        'reproduccion',
        'produccion',
        'finanzas',
        'completo'  # Todos los reportes
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Instanciar generadores específicos
        self.reporte_animales = ReporteAnimales()
        self.reporte_reproduccion = ReporteReproduccion()
        self.reporte_produccion = ReporteProduccion()
        self.reporte_finanzas = ReporteFinanzas()
        
        self.logger.info("✓ ReportesService inicializado")
    
    # ═══════════════════════════════════════════════════════════════════════
    #                      MÉTODOS PÚBLICOS - API
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_reporte(self, tipo: str, fecha_inicio: Optional[date] = None,
                       fecha_fin: Optional[date] = None, 
                       filtros: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Genera un reporte específico.
        
        Args:
            tipo: Tipo de reporte ('animales', 'reproduccion', 'produccion', 'finanzas', 'completo')
            fecha_inicio: Fecha inicial del período (opcional, último mes por defecto)
            fecha_fin: Fecha final del período (opcional, hoy por defecto)
            filtros: Filtros adicionales específicos del reporte
        
        Returns:
            Diccionario con estructura:
            {
                'tipo': str,
                'periodo': {'inicio': str, 'fin': str},
                'generado_en': str (ISO),
                'datos': Dict | List,
                'totales': Dict (opcional),
                'metadatos': Dict (opcional)
            }
        
        Raises:
            ValueError: Si el tipo de reporte no es válido
        """
        # Validar tipo
        if tipo not in self.TIPOS_REPORTE:
            raise ValueError(
                f"Tipo de reporte inválido: '{tipo}'. "
                f"Tipos válidos: {', '.join(self.TIPOS_REPORTE)}"
            )
        
        # Normalizar fechas
        fecha_inicio, fecha_fin = self._normalizar_fechas(fecha_inicio, fecha_fin)
        
        # Logging
        self.logger.info(
            f"Generando reporte: {tipo} "
            f"(periodo: {fecha_inicio} → {fecha_fin})"
        )
        
        # Generar según tipo
        if tipo == 'completo':
            return self._generar_reporte_completo(fecha_inicio, fecha_fin, filtros)
        
        # Delegar a generador específico
        generadores = {
            'animales': self.reporte_animales.generar,
            'reproduccion': self.reporte_reproduccion.generar,
            'produccion': self.reporte_produccion.generar,
            'finanzas': self.reporte_finanzas.generar
        }
        
        try:
            datos = generadores[tipo](fecha_inicio, fecha_fin, filtros or {})
            
            return {
                'tipo': tipo,
                'periodo': {
                    'inicio': fecha_inicio.isoformat(),
                    'fin': fecha_fin.isoformat()
                },
                'generado_en': datetime.now().isoformat(),
                'datos': datos.get('datos', {}),
                'totales': datos.get('totales', {}),
                'metadatos': datos.get('metadatos', {})
            }
        
        except Exception as e:
            self.logger.error(f"Error generando reporte {tipo}: {e}", exc_info=True)
            raise
    
    def obtener_resumen_rapido(self) -> Dict[str, Any]:
        """
        Genera un resumen ejecutivo rápido (última semana).
        
        Ideal para dashboard principal o notificaciones.
        
        Returns:
            Diccionario con métricas clave de todas las áreas
        """
        hoy = date.today()
        hace_7_dias = hoy - timedelta(days=7)
        
        try:
            # Obtener datos mínimos de cada área
            animales = self.reporte_animales.obtener_inventario_actual()
            produccion = self.reporte_produccion.obtener_ultimos_dias(7)
            finanzas = self.reporte_finanzas.obtener_kpis_rapidos(hace_7_dias, hoy)
            
            return {
                'periodo': f"Últimos 7 días ({hace_7_dias} → {hoy})",
                'generado_en': datetime.now().isoformat(),
                'resumen': {
                    'animales': {
                        'total_activos': animales.get('total_activos', 0),
                        'gestantes': animales.get('gestantes', 0)
                    },
                    'produccion': {
                        'litros_semana': produccion.get('total_litros', 0),
                        'promedio_diario': produccion.get('promedio_diario', 0)
                    },
                    'finanzas': {
                        'ingresos': finanzas.get('ingresos_totales', 0),
                        'margen_porcentaje': finanzas.get('margen_porcentaje', 0)
                    }
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error generando resumen rápido: {e}")
            return {'error': str(e)}
    
    def validar_periodo(self, fecha_inicio: date, fecha_fin: date) -> bool:
        """
        Valida que un período sea coherente.
        
        Args:
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
        
        Returns:
            True si el período es válido
        
        Raises:
            ValueError: Si el período es inválido
        """
        if fecha_inicio > fecha_fin:
            raise ValueError(
                f"Fecha inicial ({fecha_inicio}) no puede ser mayor "
                f"que fecha final ({fecha_fin})"
            )
        
        if fecha_fin > date.today():
            raise ValueError(
                f"Fecha final ({fecha_fin}) no puede ser futura"
            )
        
        # Advertencia si el período es muy largo (más de 1 año)
        dias = (fecha_fin - fecha_inicio).days
        if dias > 365:
            self.logger.warning(
                f"Período muy extenso: {dias} días. "
                "El reporte puede tardar."
            )
        
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    #                      MÉTODOS PRIVADOS - UTILIDADES
    # ═══════════════════════════════════════════════════════════════════════
    
    def _normalizar_fechas(self, fecha_inicio: Optional[date], 
                          fecha_fin: Optional[date]) -> tuple[date, date]:
        """
        Normaliza y valida fechas de entrada.
        
        Returns:
            Tupla (fecha_inicio, fecha_fin) normalizadas
        """
        if fecha_fin is None:
            fecha_fin = date.today()
        
        if fecha_inicio is None:
            # Por defecto: último mes
            fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Validar coherencia
        self.validar_periodo(fecha_inicio, fecha_fin)
        
        return fecha_inicio, fecha_fin
    
    def _generar_reporte_completo(self, fecha_inicio: date, fecha_fin: date,
                                 filtros: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera un reporte completo con todas las secciones.
        
        Returns:
            Diccionario con todas las secciones de reportes
        """
        self.logger.info("Generando reporte completo (todas las secciones)...")
        
        try:
            reportes = {
                'animales': self.reporte_animales.generar(fecha_inicio, fecha_fin, filtros or {}),
                'reproduccion': self.reporte_reproduccion.generar(fecha_inicio, fecha_fin, filtros or {}),
                'produccion': self.reporte_produccion.generar(fecha_inicio, fecha_fin, filtros or {}),
                'finanzas': self.reporte_finanzas.generar(fecha_inicio, fecha_fin, filtros or {})
            }
            
            return {
                'tipo': 'completo',
                'periodo': {
                    'inicio': fecha_inicio.isoformat(),
                    'fin': fecha_fin.isoformat()
                },
                'generado_en': datetime.now().isoformat(),
                'secciones': reportes,
                'metadatos': {
                    'secciones_incluidas': list(reportes.keys()),
                    'total_secciones': len(reportes)
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error generando reporte completo: {e}", exc_info=True)
            raise


# Singleton global
reportes_service = ReportesService()
