"""
FASE 11: Simulation Service
Motor de simulación "¿Qué pasaría si...?" para probar recomendaciones sin riesgo.
Permite a usuarios explorar escenarios hipotéticos y ver resultados predichos.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Sequence, SupportsFloat
from datetime import datetime, timedelta
from enum import Enum
import random
import statistics
import logging


# ============================================================================
#                           DATACLASSES Y ENUMS
# ============================================================================

class TipoEscenario(Enum):
    """Tipos de escenarios de simulación disponibles"""
    INCREMENTO_PRODUCCION = "incremento_produccion"
    REDUCCION_COSTOS = "reduccion_costos"
    CAMBIO_ALIMENTACION = "cambio_alimentacion"
    MEJORA_SALUD = "mejora_salud"
    CAMBIO_ESTACION = "cambio_estacion"
    PERSONALIZADO = "personalizado"


@dataclass
class ParametroSimulacion:
    """Parámetro ajustable en una simulación"""
    nombre: str
    valor_actual: float
    valor_simulado: float
    unidad: str
    descripcion: str
    
    def porcentaje_cambio(self) -> float:
        """Calcula el porcentaje de cambio entre actual y simulado"""
        if self.valor_actual == 0:
            return 0.0
        return ((self.valor_simulado - self.valor_actual) / self.valor_actual) * 100


@dataclass
class ResultadoSimulacion:
    """Resultado proyectado de una métrica bajo el escenario"""
    metrica_nombre: str
    valor_actual: float
    valor_proyectado: float
    desviacion_pct: float
    confianza_pct: int
    tendencia: str  # "mejora", "empeora", "sin_cambio"
    impacto_negocio: str  # "positivo", "negativo", "neutral"
    
    def impacto_numerico(self) -> float:
        """Calcula el impacto numérico absoluto"""
        return self.valor_proyectado - self.valor_actual


@dataclass
class ReporteSimulacion:
    """Reporte completo de una simulación"""
    tipo_escenario: str
    nombre_escenario: str
    descripcion_escenario: str
    parametros: List[ParametroSimulacion]
    resultados: List[ResultadoSimulacion]
    resumen_ejecutivo: str
    riesgo_implementacion: str  # "bajo", "medio", "alto"
    roi_estimado_pct: float  # Return on Investment %
    periodo_amortizacion_dias: Optional[int]
    recomendacion_final: str
    fecha_generacion: str
    validez_dias: int  # Cuántos días es válida esta simulación


# ============================================================================
#                        SIMULATION SERVICE
# ============================================================================

class SimulationService:
    """
    Servicio de simulación para explorar escenarios "¿Qué pasaría si...?"
    Permite probar recomendaciones de FASE 10 sin riesgo real.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SimulationService")
        self.escenarios_ejecutados = []
        self._inicializar_plantillas_escenarios()
    
    def _inicializar_plantillas_escenarios(self):
        """Inicializa plantillas predefinidas de escenarios"""
        self.plantillas = {
            TipoEscenario.INCREMENTO_PRODUCCION: {
                "nombre": "Incremento de Producción",
                "descripcion": "Simula el impacto de aumentar la producción diaria",
                "parametros_afectados": ["produccion_total", "costos_incrementales", "necesidad_alimento"],
                "factores_multiplicadores": {
                    "produccion_total": 1.0,  # Sin cambio directo
                    "costos_incrementales": 0.3,  # Aumentan costos 30% por unidad
                    "necesidad_alimento": 0.25,  # +25% necesidad de alimento
                    "ingresos": 0.95  # Ingresos aumentan casi 1:1 (95%)
                }
            },
            TipoEscenario.REDUCCION_COSTOS: {
                "nombre": "Reducción de Costos",
                "descripcion": "Simula el impacto de reducir costos operacionales",
                "parametros_afectados": ["costos_totales", "margen_utilidad", "productividad"],
                "factores_multiplicadores": {
                    "costos_totales": 1.0,  # Sin cambio directo
                    "margen_utilidad": 0.15,  # Mejora margen 15%
                    "productividad": 0.05,  # Riesgo: reduce productividad 5%
                    "calidad": -0.02  # Pequeño riesgo de reducción de calidad
                }
            },
            TipoEscenario.CAMBIO_ALIMENTACION: {
                "nombre": "Cambio en Alimentación",
                "descripcion": "Simula efecto de cambiar composición de alimento",
                "parametros_afectados": ["costos_alimento", "produccion_total", "salud_animales"],
                "factores_multiplicadores": {
                    "costos_alimento": 1.0,
                    "produccion_total": 0.10,  # +10% producción
                    "salud_animales": 0.15,  # +15% en indicadores salud
                    "adaptacion_dias": 14  # Tiempo adaptación
                }
            },
            TipoEscenario.MEJORA_SALUD: {
                "nombre": "Mejora en Salud Animal",
                "descripcion": "Simula impacto de mejorar protocolos sanitarios",
                "parametros_afectados": ["tasa_mortalidad", "produccion_total", "costos_salud"],
                "factores_multiplicadores": {
                    "tasa_mortalidad": -0.30,  # -30% mortalidad
                    "produccion_total": 0.08,  # +8% producción
                    "costos_salud": 0.20,  # +20% costos salud inicial
                    "ahorro_largo_plazo": 0.15  # -15% costos a largo plazo
                }
            }
        }
    
    def simular_incremento_produccion(self, 
                                     produccion_actual: float,
                                     incremento_pct: float,
                                     datos_historicos: Sequence[SupportsFloat]) -> ReporteSimulacion:
        """
        Simula el impacto de incrementar la producción.
        
        Args:
            produccion_actual: Producción diaria actual (litros)
            incremento_pct: Porcentaje de incremento esperado (10, 15, 20, etc)
            datos_historicos: Datos históricos para validación
        
        Returns:
            ReporteSimulacion con proyecciones
        """
        nombre_escenario = f"Incremento {incremento_pct}% en Producción"
        
        # Calcular valores simulados
        produccion_simulada = produccion_actual * (1 + incremento_pct / 100)
        
        # Estimar impactos secundarios
        plantilla = self.plantillas[TipoEscenario.INCREMENTO_PRODUCCION]
        factores = plantilla["factores_multiplicadores"]
        
        # Calcular costo incremental estimado (30% por unidad adicional)
        unidades_adicionales = produccion_simulada - produccion_actual
        costo_incremental = unidades_adicionales * factores["costos_incrementales"]
        
        # Calcular ingresos adicionales (95% del valor de producción)
        ingresos_adicionales = unidades_adicionales * factores["ingresos"]
        
        # Margen estimado
        margen = ingresos_adicionales - costo_incremental
        roi = (margen / costo_incremental * 100) if costo_incremental > 0 else 100
        
        # Construir parámetros
        parametros = [
            ParametroSimulacion(
                nombre="Producción Diaria",
                valor_actual=produccion_actual,
                valor_simulado=produccion_simulada,
                unidad="litros",
                descripcion="Producción de leche diaria total"
            ),
            ParametroSimulacion(
                nombre="Costos Incrementales",
                valor_actual=0,
                valor_simulado=costo_incremental,
                unidad="USD",
                descripcion="Costos adicionales por producción extra"
            ),
            ParametroSimulacion(
                nombre="Ingresos Adicionales",
                valor_actual=0,
                valor_simulado=ingresos_adicionales,
                unidad="USD",
                descripcion="Ingresos por producción adicional"
            )
        ]
        
        # Construir resultados
        resultados = [
            ResultadoSimulacion(
                metrica_nombre="Producción Diaria",
                valor_actual=produccion_actual,
                valor_proyectado=produccion_simulada,
                desviacion_pct=incremento_pct,
                confianza_pct=85,
                tendencia="mejora",
                impacto_negocio="positivo"
            ),
            ResultadoSimulacion(
                metrica_nombre="Margen Operativo",
                valor_actual=100,  # Base
                valor_proyectado=100 + (roi * 0.1),  # Estimado
                desviacion_pct=roi * 0.1,
                confianza_pct=75,
                tendencia="mejora",
                impacto_negocio="positivo"
            ),
            ResultadoSimulacion(
                metrica_nombre="Necesidad Alimento",
                valor_actual=100,
                valor_proyectado=100 + (incremento_pct * factores["necesidad_alimento"]),
                desviacion_pct=incremento_pct * factores["necesidad_alimento"],
                confianza_pct=80,
                tendencia="empeora",
                impacto_negocio="negativo"
            )
        ]
        
        # Resumen ejecutivo
        resumen = f"""
        Escenario: {nombre_escenario}
        
        Si incrementas la producción en {incremento_pct}%:
        • Producción: {produccion_actual:.0f}L → {produccion_simulada:.0f}L (+{unidades_adicionales:.0f}L)
        • Ingresos adicionales: ${ingresos_adicionales:.2f}
        • Costos incrementales: ${costo_incremental:.2f}
        • Margen neto: ${margen:.2f}
        • ROI estimado: {roi:.1f}%
        
        Consideraciones:
        • Requiere capacidad de infraestructura
        • Mayor demanda de alimento y recursos
        • Potencial de amortización: ~{14 + int(incremento_pct/5)} días
        """
        
        # Recomendación
        if roi > 50:
            recomendacion = "✅ ALTAMENTE RECOMENDADO: ROI excelente con implementación gradual"
            riesgo = "bajo"
        elif roi > 20:
            recomendacion = "✅ RECOMENDADO: Buena relación riesgo-beneficio"
            riesgo = "medio"
        else:
            recomendacion = "⚠️ EVALUAR: ROI marginal, validar disponibilidad de recursos"
            riesgo = "medio"
        
        dias_amortizacion = int(30 * (1 - (roi / 100))) if roi > 0 else None
        
        return ReporteSimulacion(
            tipo_escenario="incremento_produccion",
            nombre_escenario=nombre_escenario,
            descripcion_escenario=plantilla["descripcion"],
            parametros=parametros,
            resultados=resultados,
            resumen_ejecutivo=resumen.strip(),
            riesgo_implementacion=riesgo,
            roi_estimado_pct=roi,
            periodo_amortizacion_dias=dias_amortizacion,
            recomendacion_final=recomendacion,
            fecha_generacion=datetime.now().isoformat(),
            validez_dias=30
        )
    
    def simular_reduccion_costos(self,
                                costos_actuales: float,
                                reduccion_pct: float) -> ReporteSimulacion:
        """
        Simula el impacto de reducir costos operacionales.
        
        Args:
            costos_actuales: Costos operacionales actuales (USD)
            reduccion_pct: Porcentaje de reducción (5, 10, 15, etc)
        
        Returns:
            ReporteSimulacion con proyecciones
        """
        nombre_escenario = f"Reducción {reduccion_pct}% en Costos"
        
        costos_simulados = costos_actuales * (1 - reduccion_pct / 100)
        ahorro = costos_actuales - costos_simulados
        
        plantilla = self.plantillas[TipoEscenario.REDUCCION_COSTOS]
        factores = plantilla["factores_multiplicadores"]
        
        # Mejora en margen
        mejora_margen = ahorro * factores["margen_utilidad"]
        
        # Riesgo de caída de productividad
        impacto_productividad = -ahorro * factores["productividad"]
        
        parametros = [
            ParametroSimulacion(
                nombre="Costos Operacionales",
                valor_actual=costos_actuales,
                valor_simulado=costos_simulados,
                unidad="USD",
                descripcion="Costos totales operacionales"
            ),
            ParametroSimulacion(
                nombre="Ahorro Esperado",
                valor_actual=0,
                valor_simulado=ahorro,
                unidad="USD",
                descripcion="Ahorro directo en costos"
            ),
            ParametroSimulacion(
                nombre="Riesgo Productividad",
                valor_actual=0,
                valor_simulado=-impacto_productividad,
                unidad="USD equiv",
                descripcion="Riesgo potencial por caída productiva"
            )
        ]
        
        resultados = [
            ResultadoSimulacion(
                metrica_nombre="Costos Totales",
                valor_actual=costos_actuales,
                valor_proyectado=costos_simulados,
                desviacion_pct=-reduccion_pct,
                confianza_pct=80,
                tendencia="mejora",
                impacto_negocio="positivo"
            ),
            ResultadoSimulacion(
                metrica_nombre="Margen Utilidad",
                valor_actual=100,
                valor_proyectado=100 + mejora_margen,
                desviacion_pct=mejora_margen,
                confianza_pct=75,
                tendencia="mejora",
                impacto_negocio="positivo"
            ),
            ResultadoSimulacion(
                metrica_nombre="Productividad (Riesgo)",
                valor_actual=100,
                valor_proyectado=100 - (reduccion_pct * factores["productividad"]),
                desviacion_pct=-(reduccion_pct * factores["productividad"]),
                confianza_pct=70,
                tendencia="empeora",
                impacto_negocio="negativo"
            )
        ]
        
        resumen = f"""
        Escenario: {nombre_escenario}
        
        Si reduces costos en {reduccion_pct}%:
        • Costos: ${costos_actuales:.2f} → ${costos_simulados:.2f}
        • Ahorro directo: ${ahorro:.2f}
        • Mejora margen: ${mejora_margen:.2f}
        • Riesgo productividad: ${impacto_productividad:.2f}
        • Ganancia neta: ${ahorro - impacto_productividad:.2f}
        
        Advertencias:
        • Riesgo moderado de caída productiva ({reduccion_pct * factores['productividad']:.1f}%)
        • Requiere implementación cuidadosa
        • Validar por sector (insumos vs personal)
        """
        
        ganancia_neta = ahorro - impacto_productividad
        roi = (ganancia_neta / costos_actuales) * 100 if costos_actuales > 0 else 0
        
        if roi > 15:
            recomendacion = "✅ RECOMENDADO: Beneficio neto con manejo cuidadoso"
            riesgo = "bajo"
        else:
            recomendacion = "⚠️ EVALUAR: Margen ajustado, validar riesgos"
            riesgo = "medio"
        
        return ReporteSimulacion(
            tipo_escenario="reduccion_costos",
            nombre_escenario=nombre_escenario,
            descripcion_escenario=plantilla["descripcion"],
            parametros=parametros,
            resultados=resultados,
            resumen_ejecutivo=resumen.strip(),
            riesgo_implementacion=riesgo,
            roi_estimado_pct=roi,
            periodo_amortizacion_dias=30 - int(reduccion_pct),
            recomendacion_final=recomendacion,
            fecha_generacion=datetime.now().isoformat(),
            validez_dias=30
        )
    
    def simular_cambio_alimentacion(self,
                                   produccion_actual: float,
                                   costo_alimento_actual: float,
                                   cambio_tipo: str = "optimizado") -> ReporteSimulacion:
        """
        Simula el impacto de cambiar la alimentación.
        
        Args:
            produccion_actual: Producción actual (litros)
            costo_alimento_actual: Costo actual de alimento (USD)
            cambio_tipo: "optimizado" o "premium"
        
        Returns:
            ReporteSimulacion con proyecciones
        """
        plantilla = self.plantillas[TipoEscenario.CAMBIO_ALIMENTACION]
        
        # Parámetros según tipo de cambio
        if cambio_tipo == "optimizado":
            nombre_escenario = "Cambio a Alimentación Optimizada"
            costo_nuevo = costo_alimento_actual * 0.95  # 5% más barato
            produccion_nueva = produccion_actual * 1.08  # 8% más producción
            salud_mejora = 12  # +12% en salud
        else:  # premium
            nombre_escenario = "Cambio a Alimentación Premium"
            costo_nuevo = costo_alimento_actual * 1.15  # 15% más caro
            produccion_nueva = produccion_actual * 1.12  # 12% más producción
            salud_mejora = 18  # +18% en salud
        
        parametros = [
            ParametroSimulacion(
                nombre="Costo Alimento",
                valor_actual=costo_alimento_actual,
                valor_simulado=costo_nuevo,
                unidad="USD",
                descripcion="Costo diario de alimentación"
            ),
            ParametroSimulacion(
                nombre="Producción",
                valor_actual=produccion_actual,
                valor_simulado=produccion_nueva,
                unidad="litros",
                descripcion="Producción diaria"
            ),
            ParametroSimulacion(
                nombre="Índice Salud",
                valor_actual=100,
                valor_simulado=100 + salud_mejora,
                unidad="puntos",
                descripcion="Indicador general de salud animal"
            )
        ]
        
        # Cálculo de ROI
        ingresos_adicionales = (produccion_nueva - produccion_actual) * 0.95
        costo_neto_cambio = costo_nuevo - costo_alimento_actual
        ganancia = ingresos_adicionales - abs(costo_neto_cambio)
        roi = (ganancia / abs(costo_neto_cambio)) * 100 if costo_neto_cambio != 0 else ingresos_adicionales
        
        resultados = [
            ResultadoSimulacion(
                metrica_nombre="Producción",
                valor_actual=produccion_actual,
                valor_proyectado=produccion_nueva,
                desviacion_pct=(produccion_nueva - produccion_actual) / produccion_actual * 100,
                confianza_pct=78,
                tendencia="mejora",
                impacto_negocio="positivo"
            ),
            ResultadoSimulacion(
                metrica_nombre="Costo Alimento",
                valor_actual=costo_alimento_actual,
                valor_proyectado=costo_nuevo,
                desviacion_pct=(costo_nuevo - costo_alimento_actual) / costo_alimento_actual * 100,
                confianza_pct=82,
                tendencia="mejora" if costo_nuevo < costo_alimento_actual else "empeora",
                impacto_negocio="positivo" if costo_nuevo < costo_alimento_actual else "negativo"
            ),
            ResultadoSimulacion(
                metrica_nombre="Salud Animal",
                valor_actual=100,
                valor_proyectado=100 + salud_mejora,
                desviacion_pct=salud_mejora,
                confianza_pct=76,
                tendencia="mejora",
                impacto_negocio="positivo"
            )
        ]
        
        resumen = f"""
        Escenario: {nombre_escenario}
        
        Impacto estimado:
        • Producción: {produccion_actual:.0f}L → {produccion_nueva:.0f}L (+{(produccion_nueva-produccion_actual):.0f}L)
        • Costo alimento: ${costo_alimento_actual:.2f} → ${costo_nuevo:.2f}
        • Ingresos adicionales: ${ingresos_adicionales:.2f}
        • Ganancia neta: ${ganancia:.2f}
        • ROI: {roi:.1f}%
        
        Beneficios adicionales:
        • Salud animal mejorada (+{salud_mejora}%)
        • Menor tasa de enfermedades
        • Adaptación: ~{14 if cambio_tipo == "optimizado" else 21} días
        """
        
        if roi > 30:
            recomendacion = "✅ ALTAMENTE RECOMENDADO"
            riesgo = "bajo"
        elif roi > 10:
            recomendacion = "✅ RECOMENDADO con período de adaptación"
            riesgo = "bajo"
        else:
            recomendacion = "⚠️ EVALUAR: Monitorear adaptación de animales"
            riesgo = "medio"
        
        return ReporteSimulacion(
            tipo_escenario="cambio_alimentacion",
            nombre_escenario=nombre_escenario,
            descripcion_escenario=plantilla["descripcion"],
            parametros=parametros,
            resultados=resultados,
            resumen_ejecutivo=resumen.strip(),
            riesgo_implementacion=riesgo,
            roi_estimado_pct=roi,
            periodo_amortizacion_dias=14 if cambio_tipo == "optimizado" else 21,
            recomendacion_final=recomendacion,
            fecha_generacion=datetime.now().isoformat(),
            validez_dias=45
        )
    
    def simular_mejora_salud(self,
                            tasa_mortalidad_actual: float,
                            produccion_actual: float,
                            costo_salud_actual: float) -> ReporteSimulacion:
        """
        Simula el impacto de mejorar protocolos sanitarios.
        
        Args:
            tasa_mortalidad_actual: Tasa actual (porcentaje)
            produccion_actual: Producción actual (litros)
            costo_salud_actual: Costo actual de salud (USD)
        
        Returns:
            ReporteSimulacion
        """
        plantilla = self.plantillas[TipoEscenario.MEJORA_SALUD]
        
        # Reducciones esperadas
        tasa_mortalidad_nueva = tasa_mortalidad_actual * 0.70  # -30% mortalidad
        produccion_nueva = produccion_actual * 1.08  # +8% por menos enfermedades
        costo_salud_nuevo = costo_salud_actual * 1.20  # +20% inicial
        
        # Beneficios a largo plazo
        costo_salud_largo_plazo = costo_salud_actual * 0.85  # -15% a LP
        
        parametros = [
            ParametroSimulacion(
                nombre="Tasa Mortalidad",
                valor_actual=tasa_mortalidad_actual,
                valor_simulado=tasa_mortalidad_nueva,
                unidad="%",
                descripcion="Porcentaje de mortalidad animal"
            ),
            ParametroSimulacion(
                nombre="Producción",
                valor_actual=produccion_actual,
                valor_simulado=produccion_nueva,
                unidad="litros",
                descripcion="Producción diaria"
            ),
            ParametroSimulacion(
                nombre="Costo Salud (corto plazo)",
                valor_actual=costo_salud_actual,
                valor_simulado=costo_salud_nuevo,
                unidad="USD",
                descripcion="Inversión en protocolos sanitarios"
            )
        ]
        
        # ROI calculado a 6 meses (período típico de impacto)
        animales_salvados = tasa_mortalidad_actual - tasa_mortalidad_nueva
        ingresos_por_animales = animales_salvados * 0.5 * produccion_nueva  # Proyectado
        ahorro_largo_plazo = costo_salud_actual - costo_salud_largo_plazo
        ganancia_6m = ingresos_por_animales + ahorro_largo_plazo
        roi_6m = (ganancia_6m / (costo_salud_nuevo - costo_salud_actual)) * 100 if costo_salud_nuevo > costo_salud_actual else 100
        
        resultados = [
            ResultadoSimulacion(
                metrica_nombre="Tasa Mortalidad",
                valor_actual=tasa_mortalidad_actual,
                valor_proyectado=tasa_mortalidad_nueva,
                desviacion_pct=-(tasa_mortalidad_actual - tasa_mortalidad_nueva),
                confianza_pct=82,
                tendencia="mejora",
                impacto_negocio="positivo"
            ),
            ResultadoSimulacion(
                metrica_nombre="Producción",
                valor_actual=produccion_actual,
                valor_proyectado=produccion_nueva,
                desviacion_pct=(produccion_nueva - produccion_actual) / produccion_actual * 100,
                confianza_pct=78,
                tendencia="mejora",
                impacto_negocio="positivo"
            ),
            ResultadoSimulacion(
                metrica_nombre="Costo Salud Largo Plazo (6m+)",
                valor_actual=costo_salud_actual,
                valor_proyectado=costo_salud_largo_plazo,
                desviacion_pct=-(costo_salud_actual - costo_salud_largo_plazo) / costo_salud_actual * 100,
                confianza_pct=70,
                tendencia="mejora",
                impacto_negocio="positivo"
            )
        ]
        
        resumen = f"""
        Escenario: Mejora en Protocolos Sanitarios
        
        Proyecciones:
        • Mortalidad: {tasa_mortalidad_actual:.1f}% → {tasa_mortalidad_nueva:.1f}%
        • Producción adicional: +{(produccion_nueva-produccion_actual):.0f}L/día
        • Inversión inicial: +${costo_salud_nuevo - costo_salud_actual:.2f}
        • Ahorro a largo plazo (6m+): ${ahorro_largo_plazo:.2f}/mes
        • ROI en 6 meses: {roi_6m:.1f}%
        
        Beneficios cualitativos:
        • Mejora bienestar animal
        • Reducción de enfermedades contagiosas
        • Mayor confianza del consumidor
        • Mejor reputación de granja
        """
        
        recomendacion = "✅ ALTAMENTE RECOMENDADO: Beneficio directo e indirecto significativo"
        riesgo = "bajo"
        
        return ReporteSimulacion(
            tipo_escenario="mejora_salud",
            nombre_escenario="Mejora en Protocolos Sanitarios",
            descripcion_escenario=plantilla["descripcion"],
            parametros=parametros,
            resultados=resultados,
            resumen_ejecutivo=resumen.strip(),
            riesgo_implementacion=riesgo,
            roi_estimado_pct=roi_6m,
            periodo_amortizacion_dias=180,  # 6 meses
            recomendacion_final=recomendacion,
            fecha_generacion=datetime.now().isoformat(),
            validez_dias=90
        )
    
    def guardar_simulacion(self, reporte: ReporteSimulacion):
        """Guarda la simulación en historial"""
        self.escenarios_ejecutados.append(reporte)
        self.logger.info(f"Simulación guardada: {reporte.nombre_escenario}")
    
    def obtener_historial_simulaciones(self) -> List[ReporteSimulacion]:
        """Retorna el historial de simulaciones ejecutadas"""
        return self.escenarios_ejecutados


# ============================================================================
#                        SINGLETON PATTERN
# ============================================================================

_simulation_service_instance = None


def get_simulation_service() -> SimulationService:
    """
    Obtiene la instancia única del servicio de simulación.
    Implementa el patrón Singleton.
    
    Returns:
        SimulationService: Instancia única del servicio
    """
    global _simulation_service_instance
    if _simulation_service_instance is None:
        _simulation_service_instance = SimulationService()
    return _simulation_service_instance
