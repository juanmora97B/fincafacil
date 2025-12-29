"""
Analytics Service - Lógica de negocio para analytics
Orquesta cálculos, agregaciones y normalización de datos
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .analytics_repository import AnalyticsRepository


class AnalyticsService:
    """Service para lógica de BI y analytics."""

    def __init__(self):
        self._repo = AnalyticsRepository()
        self._repo.crear_tablas_si_no_existen()

    # ==================== GETTERS ====================
    
    def obtener_overview(self, empresa_id: int) -> Dict[str, Any]:
        """Obtiene KPIs principales de hoy y últimos 7/30 días."""
        hoy = datetime.now().date().isoformat()
        hace_7 = (datetime.now().date() - timedelta(days=7)).isoformat()
        hace_30 = (datetime.now().date() - timedelta(days=30)).isoformat()
        
        # Hoy
        prod_hoy = self._repo.obtener_productividad(empresa_id, hoy)
        animales_totales = sum(p.get('animales_totales', 0) for p in prod_hoy)
        nacimientos = sum(p.get('nacimientos', 0) for p in prod_hoy)
        destetes = sum(p.get('destetes', 0) for p in prod_hoy)
        muertes = sum(p.get('muertes', 0) for p in prod_hoy)
        
        # Últimas alertas
        alertas_hoy = self._repo.obtener_alertas(empresa_id, hoy)
        alertas_activas = sum(a.get('total_activas', 0) for a in alertas_hoy)
        
        # IA
        ia_hoy = self._repo.obtener_ia(empresa_id, hoy)
        sugerencias_aceptadas = ia_hoy.get('sugerencias_aceptadas', 0) if ia_hoy else 0
        
        # Rango (últimos 7 días)
        prod_7 = self._repo.obtener_productividad_rango(empresa_id, hace_7, hoy)
        mortalidad_7d = sum(p.get('muertes', 0) for p in prod_7)
        
        return {
            'hoy': {
                'animales_totales': animales_totales,
                'nacimientos': nacimientos,
                'destetes': destetes,
                'muertes': muertes,
                'mortalidad_pct': (muertes / animales_totales * 100) if animales_totales > 0 else 0,
                'alertas_activas': alertas_activas,
                'sugerencias_ia_aceptadas': sugerencias_aceptadas,
            },
            'ultimos_7_dias': {
                'muertes': mortalidad_7d,
                'promedio_diario': mortalidad_7d / 7,
            },
            'timestamp': datetime.now().isoformat(),
        }

    def obtener_productividad(
        self, 
        empresa_id: int, 
        fecha: Optional[str] = None, 
        lote_id: Optional[int] = None,
        rango_dias: int = 30
    ) -> Dict[str, Any]:
        """Obtiene datos de productividad agregados."""
        if not fecha:
            fecha = datetime.now().date().isoformat()
        
        fecha_inicio = (datetime.fromisoformat(fecha) - timedelta(days=rango_dias)).date().isoformat()
        
        datos = self._repo.obtener_productividad_rango(empresa_id, fecha_inicio, fecha)
        
        if lote_id:
            datos = [d for d in datos if d.get('lote_id') == lote_id]
        
        # Agregación por día
        por_dia = {}
        for d in datos:
            f = d.get('fecha')
            if f not in por_dia:
                por_dia[f] = {
                    'fecha': f,
                    'nacimientos': 0,
                    'destetes': 0,
                    'muertes': 0,
                    'traslados': 0,
                    'servicios': 0,
                    'partos': 0,
                    'mortalidad_pct': 0.0,
                }
            por_dia[f]['nacimientos'] += d.get('nacimientos', 0)
            por_dia[f]['destetes'] += d.get('destetes', 0)
            por_dia[f]['muertes'] += d.get('muertes', 0)
            por_dia[f]['traslados'] += d.get('traslados', 0)
            por_dia[f]['servicios'] += d.get('servicios', 0)
            por_dia[f]['partos'] += d.get('partos', 0)
        
        return {
            'serie_temporal': sorted(por_dia.values(), key=lambda x: x['fecha']),
            'total_periodo': {
                'nacimientos': sum(d.get('nacimientos', 0) for d in datos),
                'muertes': sum(d.get('muertes', 0) for d in datos),
                'destetes': sum(d.get('destetes', 0) for d in datos),
            },
            'timestamp': datetime.now().isoformat(),
        }

    def obtener_alertas(self, empresa_id: int, fecha: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene datos de alertas."""
        if not fecha:
            fecha = datetime.now().date().isoformat()
        
        alertas = self._repo.obtener_alertas(empresa_id, fecha)
        
        return {
            'por_tipo': [dict(a) for a in alertas],
            'total_activas': sum(a.get('total_activas', 0) for a in alertas),
            'total_resueltas': sum(a.get('total_resueltas', 0) for a in alertas),
            'criticas_activas': sum(a.get('criticas_activas', 0) for a in alertas),
            'tiempo_promedio_resolucion': sum(
                a.get('tiempo_promedio_resolucion', 0) for a in alertas if a.get('tiempo_promedio_resolucion')
            ) / len([a for a in alertas if a.get('tiempo_promedio_resolucion')]) if alertas else 0,
            'timestamp': datetime.now().isoformat(),
        }

    def obtener_ia(self, empresa_id: int, fecha: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene datos de IA."""
        if not fecha:
            fecha = datetime.now().date().isoformat()
        
        data = self._repo.obtener_ia(empresa_id, fecha)
        
        if not data:
            return {
                'sugerencias_generadas': 0,
                'sugerencias_aceptadas': 0,
                'tasa_aceptacion_pct': 0.0,
                'impacto_estimado_pesos': 0.0,
                'precision_historica_pct': 0.0,
                'timestamp': datetime.now().isoformat(),
            }
        
        return {
            'sugerencias_generadas': data.get('sugerencias_generadas', 0),
            'sugerencias_aceptadas': data.get('sugerencias_aceptadas', 0),
            'sugerencias_rechazadas': data.get('sugerencias_rechazadas', 0),
            'tasa_aceptacion_pct': data.get('tasa_aceptacion_pct', 0.0),
            'impacto_estimado_pesos': data.get('impacto_estimado_pesos', 0.0),
            'precision_historica_pct': data.get('precision_historica_pct', 0.0),
            'modelo_version': data.get('modelo_version'),
            'timestamp': datetime.now().isoformat(),
        }

    def obtener_autonomia(self, empresa_id: int, fecha: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene datos de autonomía."""
        if not fecha:
            fecha = datetime.now().date().isoformat()
        
        data = self._repo.obtener_autonomia(empresa_id, fecha)
        
        if not data:
            return {
                'orquestaciones_ejecutadas': 0,
                'orquestaciones_exitosas': 0,
                'orquestaciones_fallidas': 0,
                'rollbacks_activados': 0,
                'autonomia_estado': 'ON',
                'kill_switch_activaciones': 0,
                'timestamp': datetime.now().isoformat(),
            }
        
        return {
            'orquestaciones_ejecutadas': data.get('orquestaciones_ejecutadas', 0),
            'orquestaciones_exitosas': data.get('orquestaciones_exitosas', 0),
            'orquestaciones_fallidas': data.get('orquestaciones_fallidas', 0),
            'rollbacks_activados': data.get('rollbacks_activados', 0),
            'autonomia_estado': data.get('autonomia_estado', 'ON'),
            'kill_switch_activaciones': data.get('kill_switch_activaciones', 0),
            'tasa_exito_pct': (
                data.get('orquestaciones_exitosas', 0) / data.get('orquestaciones_ejecutadas', 1) * 100
                if data.get('orquestaciones_ejecutadas', 0) > 0 else 0
            ),
            'timestamp': datetime.now().isoformat(),
        }

    # ==================== SETTERS (para Jobs) ====================
    
    def registrar_productividad(self, empresa_id: int, fecha: str, data: Dict[str, Any]) -> None:
        """Registra (o actualiza) datos de productividad."""
        data['empresa_id'] = empresa_id
        data['fecha'] = fecha
        self._repo.insertar_productividad(data)

    def registrar_alerta(self, empresa_id: int, fecha: str, data: Dict[str, Any]) -> None:
        """Registra (o actualiza) datos de alertas."""
        data['empresa_id'] = empresa_id
        data['fecha'] = fecha
        self._repo.insertar_alerta(data)

    def registrar_ia(self, empresa_id: int, fecha: str, data: Dict[str, Any]) -> None:
        """Registra (o actualiza) datos de IA."""
        data['empresa_id'] = empresa_id
        data['fecha'] = fecha
        self._repo.insertar_ia(data)

    def registrar_autonomia(self, empresa_id: int, fecha: str, data: Dict[str, Any]) -> None:
        """Registra (o actualiza) datos de autonomía."""
        data['empresa_id'] = empresa_id
        data['fecha'] = fecha
        self._repo.insertar_autonomia(data)

    # ==================== AUDITORÍA ====================
    
    def registrar_acceso_analytics(self, empresa_id: int, usuario_id: Optional[int], 
                                  endpoint: str, parametros: str = "", resultado: str = "SUCCESS") -> None:
        """Registra acceso a endpoints de analytics."""
        self._repo.registrar_acceso({
            'empresa_id': empresa_id,
            'usuario_id': usuario_id,
            'endpoint': endpoint,
            'metodo': 'GET',
            'parametros': parametros,
            'resultado': resultado,
        })
