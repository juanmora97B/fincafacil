"""
FASE 16: VALUE METRICS SERVICE
Cuantificación del valor económico del sistema FincaFácil

Responsabilidades:
- Calcular ahorro económico por prevención de problemas
- Calcular ROI de implementación de FASES 8-15
- Valorar impacto de BI y Analytics (FASE 37)
- Valorar reducción de riesgo operativo (FASE 14)
- Generar reportes PDF ejecutivos
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json


class TipoValor(Enum):
    """Tipos de valor económico generado"""
    AHORRO_DIRECTO = "ahorro_directo"              # $ ahorrados directamente
    COSTO_EVITADO = "costo_evitado"                # $ que se habrían gastado
    INGRESO_ADICIONAL = "ingreso_adicional"        # $ ganados por mejora
    REDUCCION_RIESGO = "reduccion_riesgo"          # Valor de riesgo mitigado
    EFICIENCIA_OPERATIVA = "eficiencia_operativa"  # Horas ahorradas
    MEJORA_CALIDAD = "mejora_calidad"              # Valor de mejor calidad


class CategoriaImpacto(Enum):
    """Categorías de impacto del sistema"""
    DATA_QUALITY = "data_quality"        # FASE 8
    OBSERVABILITY = "observability"      # FASE 9
    EXPLAINABILITY = "explainability"    # FASE 10
    SIMULATION = "simulation"            # FASE 11
    UX_GUARDRAILS = "ux_guardrails"      # FASE 13
    RISK_MANAGEMENT = "risk_management"  # FASE 14
    INCIDENT_MGMT = "incident_mgmt"      # FASE 15
    BI_ANALYTICS = "bi_analytics"        # FASE 37


@dataclass
class ItemValor:
    """Ítem individual de valor generado"""
    descripcion: str
    tipo_valor: TipoValor
    categoria: CategoriaImpacto
    monto_cop: float  # Pesos colombianos
    fecha: datetime = field(default_factory=datetime.now)
    evidencia: Optional[str] = None
    recurrente: bool = False  # Si se repite mensualmente
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "descripcion": self.descripcion,
            "tipo_valor": self.tipo_valor.value,
            "categoria": self.categoria.value,
            "monto_cop": self.monto_cop,
            "fecha": self.fecha.isoformat(),
            "evidencia": self.evidencia,
            "recurrente": self.recurrente
        }


@dataclass
class ROICalculation:
    """Cálculo de retorno de inversión"""
    inversion_inicial: float  # Costo de desarrollo/implementación
    beneficio_total: float    # Suma de todo el valor generado
    roi_porcentaje: float     # (Beneficio - Inversión) / Inversión * 100
    payback_meses: float      # Meses para recuperar inversión
    vnp: float                # Valor Neto Presente (con tasa descuento)
    tir: Optional[float] = None  # Tasa Interna de Retorno
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "inversion_inicial": self.inversion_inicial,
            "beneficio_total": self.beneficio_total,
            "beneficio_neto": self.beneficio_total - self.inversion_inicial,
            "roi_porcentaje": round(self.roi_porcentaje, 2),
            "payback_meses": round(self.payback_meses, 2),
            "vnp": round(self.vnp, 2),
            "tir": round(self.tir, 2) if self.tir else None
        }


@dataclass
class ReporteEjecutivo:
    """Reporte ejecutivo de valor generado"""
    periodo_inicio: datetime
    periodo_fin: datetime
    valor_total_generado: float
    roi: ROICalculation
    top_5_impactos: List[ItemValor]
    distribucion_por_categoria: Dict[str, float]
    tendencia_mensual: List[Dict[str, Any]]
    recomendaciones: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "periodo": {
                "inicio": self.periodo_inicio.isoformat(),
                "fin": self.periodo_fin.isoformat(),
                "dias": (self.periodo_fin - self.periodo_inicio).days
            },
            "valor_total_generado": self.valor_total_generado,
            "roi": self.roi.to_dict(),
            "top_5_impactos": [item.to_dict() for item in self.top_5_impactos],
            "distribucion_por_categoria": self.distribucion_por_categoria,
            "tendencia_mensual": self.tendencia_mensual,
            "recomendaciones": self.recomendaciones
        }


class ValueMetricsService:
    """
    Servicio de métricas de valor económico
    """
    
    def __init__(self):
        self.items_valor: List[ItemValor] = []
        self.parametros_economicos = {
            "precio_litro_leche": 1500,  # COP por litro
            "costo_hora_operador": 15000,  # COP por hora
            "costo_hora_veterinario": 80000,  # COP por hora
            "tasa_descuento_anual": 0.12,  # 12% para VNP
            "costo_incidente_critico": 500000,  # COP por incidente crítico
            "costo_incidente_alto": 200000,  # COP por incidente alto
            "costo_incidente_medio": 50000,  # COP por incidente medio
        }
    
    def registrar_valor(self, item: ItemValor) -> None:
        """Registra un ítem de valor generado"""
        self.items_valor.append(item)
    
    def calcular_valor_data_quality(
        self,
        registros_corregidos: int,
        tiempo_ahorrado_horas: float,
        decisiones_mejoradas: int
    ) -> float:
        """
        Calcula valor de FASE 8: Data Quality
        
        Args:
            registros_corregidos: Cantidad de registros con errores detectados/corregidos
            tiempo_ahorrado_horas: Horas ahorradas vs corrección manual
            decisiones_mejoradas: Decisiones mejoradas por data de calidad
            
        Returns:
            Valor total en COP
        """
        # Valor de tiempo ahorrado
        valor_tiempo = tiempo_ahorrado_horas * self.parametros_economicos["costo_hora_operador"]
        
        # Valor de decisiones mejoradas (estimado conservador: $50k por decisión)
        valor_decisiones = decisiones_mejoradas * 50000
        
        # Valor de prevención de errores costosos
        # Cada 100 registros malos evitan 1 incidente alto
        incidentes_evitados = registros_corregidos // 100
        valor_prevencion = incidentes_evitados * self.parametros_economicos["costo_incidente_alto"]
        
        valor_total = valor_tiempo + valor_decisiones + valor_prevencion
        
        # Registrar item
        self.registrar_valor(ItemValor(
            descripcion=f"Data Quality: {registros_corregidos} registros corregidos, {tiempo_ahorrado_horas:.1f}h ahorradas",
            tipo_valor=TipoValor.AHORRO_DIRECTO,
            categoria=CategoriaImpacto.DATA_QUALITY,
            monto_cop=valor_total,
            evidencia=f"Registros: {registros_corregidos}, Decisiones: {decisiones_mejoradas}",
            recurrente=True
        ))
        
        return valor_total
    
    def calcular_valor_observability(
        self,
        incidentes_detectados_temprano: int,
        tiempo_resolucion_reducido_horas: float
    ) -> float:
        """
        Calcula valor de FASE 9: Observability
        
        Args:
            incidentes_detectados_temprano: Incidentes detectados antes de ser críticos
            tiempo_resolucion_reducido_horas: Reducción en tiempo de diagnóstico
            
        Returns:
            Valor total en COP
        """
        # Valor de detección temprana (evita escalamiento a crítico)
        # Crítico cuesta 2.5x más que detectarlo temprano
        valor_deteccion = incidentes_detectados_temprano * (
            self.parametros_economicos["costo_incidente_critico"] - 
            self.parametros_economicos["costo_incidente_medio"]
        )
        
        # Valor de tiempo ahorrado en diagnóstico
        valor_tiempo = tiempo_resolucion_reducido_horas * self.parametros_economicos["costo_hora_operador"]
        
        valor_total = valor_deteccion + valor_tiempo
        
        self.registrar_valor(ItemValor(
            descripcion=f"Observability: {incidentes_detectados_temprano} incidentes detectados temprano",
            tipo_valor=TipoValor.COSTO_EVITADO,
            categoria=CategoriaImpacto.OBSERVABILITY,
            monto_cop=valor_total,
            evidencia=f"Reducción tiempo diagnóstico: {tiempo_resolucion_reducido_horas:.1f}h",
            recurrente=True
        ))
        
        return valor_total
    
    def calcular_valor_explainability(
        self,
        decisiones_explicadas: int,
        confianza_mejorada: float  # 0-1
    ) -> float:
        """
        Calcula valor de FASE 10: Explainability
        
        Args:
            decisiones_explicadas: Cantidad de decisiones con explicación 5-pasos
            confianza_mejorada: Mejora en confianza del sistema (0-1)
            
        Returns:
            Valor total en COP
        """
        # Valor de adopción mejorada (confianza = uso = valor)
        # Cada 10% de confianza adicional = 5% más de uso efectivo
        valor_adopcion = confianza_mejorada * 0.5 * 1000000  # $1M base de beneficio mensual
        
        # Valor de reducción de overrides (usuarios confían más, ignoran menos)
        # Cada decisión explicada reduce 0.1 overrides riesgosos
        overrides_evitados = decisiones_explicadas * 0.1
        valor_overrides = overrides_evitados * 30000  # $30k por override evitado
        
        valor_total = valor_adopcion + valor_overrides
        
        self.registrar_valor(ItemValor(
            descripcion=f"Explainability: {decisiones_explicadas} decisiones explicadas, +{confianza_mejorada*100:.0f}% confianza",
            tipo_valor=TipoValor.MEJORA_CALIDAD,
            categoria=CategoriaImpacto.EXPLAINABILITY,
            monto_cop=valor_total,
            evidencia=f"Mejora confianza: {confianza_mejorada*100:.1f}%",
            recurrente=True
        ))
        
        return valor_total
    
    def calcular_valor_simulation(
        self,
        escenarios_simulados: int,
        decisiones_optimizadas: int,
        roi_promedio_mejora: float  # Mejora de ROI por simulación
    ) -> float:
        """
        Calcula valor de FASE 11: Simulation
        
        Args:
            escenarios_simulados: Cantidad de escenarios simulados
            decisiones_optimizadas: Decisiones mejoradas por simulación
            roi_promedio_mejora: ROI promedio de mejora (ej: 0.15 = 15% mejor)
            
        Returns:
            Valor total en COP
        """
        # Valor base de optimización de decisiones
        # Cada decisión optimizada vale $100k en promedio
        valor_optimizacion = decisiones_optimizadas * 100000
        
        # Valor de ROI mejorado (sobre base de $5M de operación mensual)
        base_operacion = 5000000
        valor_roi_mejorado = base_operacion * roi_promedio_mejora
        
        valor_total = valor_optimizacion + valor_roi_mejorado
        
        self.registrar_valor(ItemValor(
            descripcion=f"Simulation: {escenarios_simulados} escenarios, {decisiones_optimizadas} decisiones optimizadas",
            tipo_valor=TipoValor.INGRESO_ADICIONAL,
            categoria=CategoriaImpacto.SIMULATION,
            monto_cop=valor_total,
            evidencia=f"ROI mejora: +{roi_promedio_mejora*100:.1f}%",
            recurrente=False  # Simulaciones son one-time
        ))
        
        return valor_total
    
    def calcular_valor_ux_guardrails(
        self,
        errores_prevenidos: int,
        tiempo_capacitacion_reducido_horas: float
    ) -> float:
        """
        Calcula valor de FASE 13: UX Guardrails
        
        Args:
            errores_prevenidos: Errores de usuario prevenidos por guardrails
            tiempo_capacitacion_reducido_horas: Tiempo de capacitación ahorrado
            
        Returns:
            Valor total en COP
        """
        # Valor de errores prevenidos
        # Cada error prevenido evita 30 min de corrección
        valor_errores = errores_prevenidos * 0.5 * self.parametros_economicos["costo_hora_operador"]
        
        # Valor de capacitación reducida
        valor_capacitacion = tiempo_capacitacion_reducido_horas * self.parametros_economicos["costo_hora_operador"]
        
        # Valor de adopción mejorada (UX amigable = mayor uso)
        # Guardrails aumentan adopción en 20% estimado
        valor_adopcion = 200000  # $200k mensuales por mayor adopción
        
        valor_total = valor_errores + valor_capacitacion + valor_adopcion
        
        self.registrar_valor(ItemValor(
            descripcion=f"UX Guardrails: {errores_prevenidos} errores prevenidos, {tiempo_capacitacion_reducido_horas:.1f}h capacitación reducida",
            tipo_valor=TipoValor.EFICIENCIA_OPERATIVA,
            categoria=CategoriaImpacto.UX_GUARDRAILS,
            monto_cop=valor_total,
            recurrente=True
        ))
        
        return valor_total
    
    def calcular_valor_risk_management(
        self,
        usuarios_alto_riesgo_identificados: int,
        incidentes_prevenidos: int,
        patrones_detectados: int
    ) -> float:
        """
        Calcula valor de FASE 14: Risk Management
        
        Args:
            usuarios_alto_riesgo_identificados: Usuarios con score >60 identificados
            incidentes_prevenidos: Incidentes prevenidos por detección temprana
            patrones_detectados: Patrones peligrosos detectados
            
        Returns:
            Valor total en COP
        """
        # Valor de incidentes prevenidos
        valor_incidentes = incidentes_prevenidos * self.parametros_economicos["costo_incidente_alto"]
        
        # Valor de usuarios reentrenados antes de causar problema
        # Cada usuario alto riesgo corregido evita $150k en incidentes futuros
        valor_reentrenamiento = usuarios_alto_riesgo_identificados * 150000
        
        # Valor de patrones detectados (inteligencia operativa)
        valor_patrones = patrones_detectados * 50000
        
        valor_total = valor_incidentes + valor_reentrenamiento + valor_patrones
        
        self.registrar_valor(ItemValor(
            descripcion=f"Risk Management: {incidentes_prevenidos} incidentes prevenidos, {usuarios_alto_riesgo_identificados} usuarios identificados",
            tipo_valor=TipoValor.REDUCCION_RIESGO,
            categoria=CategoriaImpacto.RISK_MANAGEMENT,
            monto_cop=valor_total,
            evidencia=f"Patrones detectados: {patrones_detectados}",
            recurrente=True
        ))
        
        return valor_total
    
    def calcular_valor_incident_management(
        self,
        incidentes_resueltos_sin_soporte: int,
        tiempo_resolucion_promedio_min: float,
        kb_consultas: int
    ) -> float:
        """
        Calcula valor de FASE 15: Incident Management
        
        Args:
            incidentes_resueltos_sin_soporte: Incidentes resueltos sin soporte externo
            tiempo_resolucion_promedio_min: Tiempo promedio de resolución
            kb_consultas: Consultas a Knowledge Base
            
        Returns:
            Valor total en COP
        """
        # Valor de independencia de soporte
        # Cada incidente resuelto sin soporte ahorra $100k (costo técnico externo)
        valor_soporte = incidentes_resueltos_sin_soporte * 100000
        
        # Valor de tiempo de resolución reducido
        # Antes: 4 horas promedio, Después: tiempo_resolucion_promedio_min
        horas_ahorradas_por_incidente = max(0, 4 - tiempo_resolucion_promedio_min / 60)
        valor_tiempo = incidentes_resueltos_sin_soporte * horas_ahorradas_por_incidente * self.parametros_economicos["costo_hora_operador"]
        
        # Valor de KB como activo (cada consulta vale $5k en conocimiento acumulado)
        valor_kb = kb_consultas * 5000
        
        valor_total = valor_soporte + valor_tiempo + valor_kb
        
        self.registrar_valor(ItemValor(
            descripcion=f"Incident Mgmt: {incidentes_resueltos_sin_soporte} incidentes resueltos internamente, {kb_consultas} consultas KB",
            tipo_valor=TipoValor.AHORRO_DIRECTO,
            categoria=CategoriaImpacto.INCIDENT_MGMT,
            monto_cop=valor_total,
            evidencia=f"Tiempo resolución: {tiempo_resolucion_promedio_min:.0f} min",
            recurrente=True
        ))
        
        return valor_total
    
    def calcular_valor_bi_analytics(
        self,
        insights_generados: int,
        decisiones_data_driven: int,
        mejora_eficiencia_operativa: float  # 0-1, ej: 0.15 = 15% mejora
    ) -> float:
        """
        Calcula valor de FASE 37: BI & Analytics
        
        Args:
            insights_generados: Cantidad de insights generados por BI
            decisiones_data_driven: Decisiones basadas en datos
            mejora_eficiencia_operativa: Mejora en eficiencia operativa (0-1)
            
        Returns:
            Valor total en COP
        """
        # Valor de insights (cada insight vale $80k en promedio)
        valor_insights = insights_generados * 80000
        
        # Valor de decisiones data-driven (reducen error en 30%)
        # Cada decisión vale $120k vs decisión sin datos
        valor_decisiones = decisiones_data_driven * 120000
        
        # Valor de mejora de eficiencia operativa
        # Base operacional: $10M mensuales
        base_operacion = 10000000
        valor_eficiencia = base_operacion * mejora_eficiencia_operativa
        
        valor_total = valor_insights + valor_decisiones + valor_eficiencia
        
        self.registrar_valor(ItemValor(
            descripcion=f"BI & Analytics: {insights_generados} insights, {decisiones_data_driven} decisiones data-driven",
            tipo_valor=TipoValor.INGRESO_ADICIONAL,
            categoria=CategoriaImpacto.BI_ANALYTICS,
            monto_cop=valor_total,
            evidencia=f"Mejora eficiencia: +{mejora_eficiencia_operativa*100:.1f}%",
            recurrente=True
        ))
        
        return valor_total
    
    def calcular_roi(
        self,
        inversion_inicial: float,
        meses_proyectados: int = 12
    ) -> ROICalculation:
        """
        Calcula ROI del sistema completo
        
        Args:
            inversion_inicial: Costo de desarrollo/implementación
            meses_proyectados: Meses para proyección
            
        Returns:
            Cálculo de ROI completo
        """
        # Calcular beneficio total (incluyendo recurrentes proyectados)
        beneficio_total = 0
        beneficio_mensual_recurrente = 0
        
        for item in self.items_valor:
            if item.recurrente:
                beneficio_mensual_recurrente += item.monto_cop
            else:
                beneficio_total += item.monto_cop
        
        # Proyectar beneficio recurrente
        beneficio_total += beneficio_mensual_recurrente * meses_proyectados
        
        # Calcular ROI
        roi_porcentaje = ((beneficio_total - inversion_inicial) / inversion_inicial) * 100
        
        # Calcular Payback (meses para recuperar inversión)
        if beneficio_mensual_recurrente > 0:
            payback_meses = inversion_inicial / beneficio_mensual_recurrente
        else:
            payback_meses = float('inf')
        
        # Calcular VNP (Valor Neto Presente)
        tasa_mensual = self.parametros_economicos["tasa_descuento_anual"] / 12
        vnp = -inversion_inicial
        for mes in range(1, meses_proyectados + 1):
            vnp += beneficio_mensual_recurrente / ((1 + tasa_mensual) ** mes)
        
        return ROICalculation(
            inversion_inicial=inversion_inicial,
            beneficio_total=beneficio_total,
            roi_porcentaje=roi_porcentaje,
            payback_meses=payback_meses,
            vnp=vnp
        )
    
    def obtener_top_impactos(self, n: int = 5) -> List[ItemValor]:
        """Obtiene top N items de mayor valor"""
        return sorted(self.items_valor, key=lambda x: x.monto_cop, reverse=True)[:n]
    
    def obtener_distribucion_por_categoria(self) -> Dict[str, float]:
        """Obtiene distribución de valor por categoría"""
        distribucion = {}
        for item in self.items_valor:
            categoria = item.categoria.value
            distribucion[categoria] = distribucion.get(categoria, 0) + item.monto_cop
        return distribucion
    
    def obtener_tendencia_mensual(self, meses: int = 6) -> List[Dict[str, Any]]:
        """Obtiene tendencia de valor generado por mes"""
        # Agrupar por mes
        tendencia = {}
        for item in self.items_valor:
            mes_key = item.fecha.strftime("%Y-%m")
            if mes_key not in tendencia:
                tendencia[mes_key] = {
                    "mes": mes_key,
                    "valor_total": 0,
                    "items": 0
                }
            tendencia[mes_key]["valor_total"] += item.monto_cop
            tendencia[mes_key]["items"] += 1
        
        # Ordenar por mes
        return sorted(tendencia.values(), key=lambda x: x["mes"])[-meses:]
    
    def generar_reporte_ejecutivo(
        self,
        inversion_inicial: float,
        periodo_meses: int = 6
    ) -> ReporteEjecutivo:
        """
        Genera reporte ejecutivo completo de valor
        
        Args:
            inversion_inicial: Inversión inicial en el sistema
            periodo_meses: Período de análisis en meses
            
        Returns:
            Reporte ejecutivo completo
        """
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=periodo_meses * 30)
        
        # Filtrar items del período
        items_periodo = [
            item for item in self.items_valor
            if fecha_inicio <= item.fecha <= fecha_fin
        ]
        
        valor_total = sum(item.monto_cop for item in items_periodo)
        
        roi = self.calcular_roi(inversion_inicial, periodo_meses)
        top_5 = self.obtener_top_impactos(5)
        distribucion = self.obtener_distribucion_por_categoria()
        tendencia = self.obtener_tendencia_mensual(periodo_meses)
        
        # Generar recomendaciones
        recomendaciones = []
        
        if roi.roi_porcentaje > 200:
            recomendaciones.append("ROI excelente (>200%). Considerar expansión a otras áreas.")
        elif roi.roi_porcentaje > 100:
            recomendaciones.append("ROI muy bueno (>100%). Sistema justifica inversión.")
        elif roi.roi_porcentaje > 50:
            recomendaciones.append("ROI positivo. Monitorear y optimizar áreas de menor impacto.")
        else:
            recomendaciones.append("ROI bajo. Revisar implementación y adopción del sistema.")
        
        if roi.payback_meses < 6:
            recomendaciones.append(f"Payback excelente ({roi.payback_meses:.1f} meses). Recuperación rápida.")
        elif roi.payback_meses < 12:
            recomendaciones.append(f"Payback bueno ({roi.payback_meses:.1f} meses). Dentro de estándar.")
        
        # Identificar categoría de mayor impacto
        max_categoria = max(distribucion.items(), key=lambda x: x[1])
        recomendaciones.append(f"Mayor impacto en {max_categoria[0]}: ${max_categoria[1]:,.0f}. Priorizar esta área.")
        
        return ReporteEjecutivo(
            periodo_inicio=fecha_inicio,
            periodo_fin=fecha_fin,
            valor_total_generado=valor_total,
            roi=roi,
            top_5_impactos=top_5,
            distribucion_por_categoria=distribucion,
            tendencia_mensual=tendencia,
            recomendaciones=recomendaciones
        )
    
    def exportar_reporte_json(self, filepath: str, inversion_inicial: float) -> None:
        """Exporta reporte ejecutivo a JSON"""
        reporte = self.generar_reporte_ejecutivo(inversion_inicial)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reporte.to_dict(), f, indent=2, ensure_ascii=False)


# Singleton instance
_value_metrics_service = None

def get_value_metrics_service() -> ValueMetricsService:
    """Obtiene la instancia singleton del servicio de métricas de valor"""
    global _value_metrics_service
    if _value_metrics_service is None:
        _value_metrics_service = ValueMetricsService()
    return _value_metrics_service
