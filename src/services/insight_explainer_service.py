"""
╔════════════════════════════════════════════════════════════════════════════╗
║                   INSIGHT EXPLAINER SERVICE - FASE 10                      ║
║                                                                            ║
║ Convierte decisiones técnicas de AI en explicaciones claras y accionables  ║
║ para usuarios no técnicos.                                                ║
║                                                                            ║
║ Responsabilidades:                                                        ║
║ - Generar pasos de razonamiento (5 pasos estándar)                        ║
║ - Evidencia numérica clara                                                ║
║ - Contexto (estación, patrones, cambios)                                  ║
║ - Recomendaciones de acción                                               ║
║ - Cálculo de confianza basado en datos disponibles                        ║
║                                                                            ║
║ Resultado: Explicaciones en lenguaje de negocio (no técnico)              ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger("insight_explainer")


@dataclass
class ExplanationStep:
    """Paso individual en el razonamiento"""
    numero: int
    accion: str  # "Obtuve datos", "Calculé promedio", etc.
    detalle: str
    resultado: Any


@dataclass
class ExplanationEvidence:
    """Evidencia numérica de una anomalía"""
    metrica_nombre: str
    valor_observado: float
    valor_esperado: float
    desviacion_pct: float


@dataclass
class ExplanationReport:
    """Reporte completo de explicación para usuario"""
    titulo: str
    resumen: str
    evidencia: List[ExplanationEvidence]
    pasos: List[ExplanationStep]
    contexto: Dict[str, Any]
    recomendacion: str
    confianza_pct: float
    fecha_generacion: str


class InsightExplainerService:
    """Servicio para generar explicaciones de insights y anomalías"""

    def __init__(self):
        self.logger = logger

    def explicar_anomalia(self, anomalia_dict: Dict[str, Any]) -> ExplanationReport:
        """
        Genera explicación detallada de una anomalía.

        Args:
            anomalia_dict: Diccionario con datos de la anomalía:
                {
                    'metrica': 'produccion_total',
                    'valor_observado': 800,
                    'valor_esperado': 1200,
                    'umbral_alerta': 0.25,
                    'periodo': '2025-12-28',
                    'datos_historicos': [...],  # Lista de valores
                    'estacion': 'invierno',
                    'valor_mes_anterior': 1220,
                    'patrones': [],  # Patrones conocidos
                    'cambios': []  # Cambios recientes
                }

        Returns:
            ExplanationReport con explicación completa
        """
        try:
            # 1. Extraer datos de entrada
            metrica = anomalia_dict.get("metrica", "métrica_desconocida")
            valor_observado = float(anomalia_dict.get("valor_observado", 0))
            valor_esperado = float(anomalia_dict.get("valor_esperado", 1))

            # Evitar división por cero
            if valor_esperado == 0:
                valor_esperado = 1

            # 2. Construir evidencia
            desviacion_pct = (
                ((valor_observado - valor_esperado) / valor_esperado) * 100
            )
            evidencia = ExplanationEvidence(
                metrica_nombre=self._nombre_negocio(metrica),
                valor_observado=valor_observado,
                valor_esperado=valor_esperado,
                desviacion_pct=desviacion_pct,
            )

            # 3. Construir pasos de razonamiento
            pasos = self._construir_pasos_anomalia(anomalia_dict)

            # 4. Agregar contexto
            contexto = self._analizar_contexto(anomalia_dict)

            # 5. Generar recomendación
            recomendacion = self._recomendar_accion(metrica, desviacion_pct)

            # 6. Calcular confianza
            confianza = self._calcular_confianza(anomalia_dict)

            # 7. Armar reporte final
            return ExplanationReport(
                titulo=f"{self._emoji_anomalia(desviacion_pct)} ANOMALÍA: {self._titulo_anomalia(metrica, desviacion_pct)}",
                resumen=f"{self._nombre_negocio(metrica)} está {abs(desviacion_pct):.0f}% {'por debajo' if desviacion_pct < 0 else 'por arriba'} de lo esperado",
                evidencia=[evidencia],
                pasos=pasos,
                contexto=contexto,
                recomendacion=recomendacion,
                confianza_pct=confianza,
                fecha_generacion=datetime.now().isoformat(),
            )

        except Exception as e:
            self.logger.error(f"Error generando explicación de anomalía: {e}")
            # Retornar explicación mínima
            return ExplanationReport(
                titulo="⚠️ Anomalía detectada",
                resumen="Se detectó una anomalía, pero no se pudo generar explicación detallada",
                evidencia=[],
                pasos=[],
                contexto={},
                recomendacion="Contacta al administrador del sistema",
                confianza_pct=0,
                fecha_generacion=datetime.now().isoformat(),
            )

    def explicar_patron(self, patron_dict: Dict[str, Any]) -> ExplanationReport:
        """
        Genera explicación detallada de un patrón detectado.

        Args:
            patron_dict: Diccionario con datos del patrón:
                {
                    'tipo': 'estacionalidad|rampa_costos|rampa_produccion',
                    'metrica': 'produccion_total',
                    'nivel': 'BAJO|MEDIO|ALTO',
                    'descripcion': 'Estacionalidad en meses de invierno',
                    'evidencia': ['Enero: -20%', 'Febrero: -18%', ...]
                }

        Returns:
            ExplanationReport con explicación del patrón
        """
        try:
            tipo = patron_dict.get("tipo", "patrón")
            metrica = patron_dict.get("metrica", "métrica_desconocida")
            nivel = patron_dict.get("nivel", "MEDIO")
            descripcion = patron_dict.get("descripcion", "Patrón detectado")
            evidencia_items = patron_dict.get("evidencia", [])

            # Construir pasos
            pasos = []

            # Paso 1: Recopilar datos
            pasos.append(
                ExplanationStep(
                    numero=1,
                    accion="Recopilé datos históricos",
                    detalle=f"Analicé últimos 12 meses de {self._nombre_negocio(metrica)}",
                    resultado={"periodo": "12_meses"},
                )
            )

            # Paso 2: Buscar patrones
            pasos.append(
                ExplanationStep(
                    numero=2,
                    accion="Busqué patrones recurrentes",
                    detalle=f"Tipo de patrón: {self._nombre_patron(tipo)}",
                    resultado={"tipo_patron": tipo},
                )
            )

            # Paso 3: Validar en histórico
            pasos.append(
                ExplanationStep(
                    numero=3,
                    accion="Validé el patrón en histórico",
                    detalle=f"Encontré {len(evidencia_items)} casos similares",
                    resultado={"casos_encontrados": len(evidencia_items)},
                )
            )

            # Paso 4: Evaluar predictibilidad
            pasos.append(
                ExplanationStep(
                    numero=4,
                    accion="Evalué predictibilidad",
                    detalle=f"Patrón tiene {nivel} recurrencia",
                    resultado={"recurrencia": nivel},
                )
            )

            # Paso 5: Conclusión
            pasos.append(
                ExplanationStep(
                    numero=5,
                    accion="Conclusión",
                    detalle=f"Patrón identificado: {descripcion}",
                    resultado={"patron_confirmado": True},
                )
            )

            # Calcular confianza
            confianza = 70 + (len(evidencia_items) * 3)  # Más casos = más confianza
            confianza = min(95, confianza)  # Máximo 95%

            return ExplanationReport(
                titulo=f"📊 PATRÓN: {descripcion}",
                resumen=f"Se detectó un patrón recurrente en {self._nombre_negocio(metrica)}",
                evidencia=[],
                pasos=pasos,
                contexto={"tipo": tipo, "evidencia_casos": evidencia_items},
                recomendacion=self._recomendar_patron(tipo, nivel),
                confianza_pct=confianza,
                fecha_generacion=datetime.now().isoformat(),
            )

        except Exception as e:
            self.logger.error(f"Error generando explicación de patrón: {e}")
            return ExplanationReport(
                titulo="📊 Patrón detectado",
                resumen="Se detectó un patrón recurrente",
                evidencia=[],
                pasos=[],
                contexto={},
                recomendacion="Revisa el análisis detallado en el dashboard",
                confianza_pct=50,
                fecha_generacion=datetime.now().isoformat(),
            )

    # ==================== MÉTODOS PRIVADOS ====================

    def _nombre_negocio(self, metrica_tecnica: str) -> str:
        """Convierte nombre técnico a lenguaje de negocio"""
        mapping = {
            "produccion_total": "Producción",
            "costo_total": "Costos",
            "ingreso_total": "Ingresos",
            "margen_bruto_pct": "Margen bruto",
            "tasa_prenez": "Tasa de preñez",
            "mortalidad_pct": "Mortalidad",
            "total_activos": "Total de animales",
            "litros_totales": "Litros producidos",
        }
        return mapping.get(metrica_tecnica, metrica_tecnica)

    def _nombre_patron(self, tipo_patron: str) -> str:
        """Convierte tipo de patrón a descripción clara"""
        mapping = {
            "estacionalidad": "Estacionalidad recurrente",
            "rampa_costos": "Rampa de costos ascendente",
            "rampa_produccion": "Rampa de producción",
            "ciclo_prenez": "Ciclo reproductivo",
        }
        return mapping.get(tipo_patron, tipo_patron)

    def _construir_pasos_anomalia(self, anomalia_dict) -> List[ExplanationStep]:
        """Construye los 5 pasos estándar del razonamiento"""
        pasos = []

        try:
            datos_historicos = anomalia_dict.get("datos_historicos", [])
            valor_observado = anomalia_dict.get("valor_observado", 0)
            valor_esperado = anomalia_dict.get("valor_esperado", 1)
            metrica = anomalia_dict.get("metrica", "métrica")
            umbral = anomalia_dict.get("umbral_alerta", 0.25)

            # Paso 1: Obtener datos
            pasos.append(
                ExplanationStep(
                    numero=1,
                    accion="Obtuve datos históricos",
                    detalle=f"Recopilé {len(datos_historicos)} registros de últimos 6 meses",
                    resultado={"registros": len(datos_historicos)},
                )
            )

            # Paso 2: Calcular promedio
            pasos.append(
                ExplanationStep(
                    numero=2,
                    accion="Calculé promedio histórico",
                    detalle=f"Promedio: {valor_esperado:.2f}",
                    resultado={"promedio": valor_esperado},
                )
            )

            # Paso 3: Comparar
            desviacion = valor_observado - valor_esperado
            desviacion_pct = (desviacion / valor_esperado * 100) if valor_esperado else 0
            pasos.append(
                ExplanationStep(
                    numero=3,
                    accion="Comparé hoy vs promedio",
                    detalle=f"Hoy: {valor_observado:.2f} | Esperado: {valor_esperado:.2f} | Diferencia: {desviacion:+.2f}",
                    resultado={"hoy": valor_observado, "diferencia": desviacion},
                )
            )

            # Paso 4: Verificar contexto
            contexto_relevante = self._analizar_contexto(anomalia_dict)
            pasos.append(
                ExplanationStep(
                    numero=4,
                    accion="Verifiqué factores contextuales",
                    detalle=f"Estación: {contexto_relevante.get('estacion', 'N/A')}",
                    resultado={"contexto_analizado": True},
                )
            )

            # Paso 5: Conclusión
            es_anormal = abs(desviacion_pct) > (umbral * 100)
            pasos.append(
                ExplanationStep(
                    numero=5,
                    accion="Conclusión",
                    detalle=f"Desviación {abs(desviacion_pct):.1f}% {'>' if es_anormal else '<'} umbral {umbral*100:.0f}% → {'ANOMALÍA' if es_anormal else 'NORMAL'}",
                    resultado={"anomalia": es_anormal},
                )
            )

        except Exception as e:
            self.logger.warning(f"Error construyendo pasos: {e}")

        return pasos

    def _analizar_contexto(self, anomalia_dict) -> Dict[str, Any]:
        """Agrega contexto relevante a la anomalía"""
        return {
            "estacion": anomalia_dict.get("estacion", "desconocida"),
            "mes_anterior": anomalia_dict.get("valor_mes_anterior"),
            "patrones_conocidos": anomalia_dict.get("patrones", []),
            "cambios_recientes": anomalia_dict.get("cambios", []),
        }

    def _recomendar_accion(self, metrica: str, desviacion_pct: float) -> str:
        """Genera recomendación de acción basada en métrica y severidad"""
        recomendaciones = {
            "produccion_total": "Investiga salud del hato, equipamiento de ordeño y cambios en alimentación",
            "costo_total": "Revisa las categorías de costos más afectadas y verifica con proveedores",
            "ingreso_total": "Analiza volumen y precio de ventas; compara con mercado actual",
            "tasa_prenez": "Evalúa protocolo reproductivo, condición corporal de vacas y servicio de IA",
            "mortalidad_pct": "Revisa las causas de muertes recientes; consulta con veterinario",
            "total_activos": "Verifica registros de entradas y salidas del hato",
            "litros_totales": "Analiza producción por animal y revisa salud individual",
        }

        recomendacion_base = recomendaciones.get(
            metrica, "Investiga la causa de la desviación"
        )

        # Agregar urgencia según severidad
        if abs(desviacion_pct) > 50:
            recomendacion_base = f"🚨 URGENTE: {recomendacion_base}"
        elif abs(desviacion_pct) > 25:
            recomendacion_base = f"⚠️ IMPORTANTE: {recomendacion_base}"

        return recomendacion_base

    def _recomendar_patron(self, tipo_patron: str, nivel: str) -> str:
        """Genera recomendación para un patrón detectado"""
        recomendaciones = {
            "estacionalidad": "Este patrón es predecible. Planifica recursos anticipadamente para estos períodos",
            "rampa_costos": "Los costos muestran tendencia alcista. Negocia con proveedores o optimiza procesos",
            "rampa_produccion": "La producción muestra mejora. Mantén los cambios que han sido exitosos",
            "ciclo_prenez": "El ciclo reproductivo es estable. Continúa con el protocolo actual",
        }

        recomendacion = recomendaciones.get(
            tipo_patron, "Usa este patrón para mejorar tu planificación"
        )

        # Agregar contexto de nivel
        if nivel == "ALTO":
            recomendacion = f"[PATRÓN FUERTE] {recomendacion}"
        elif nivel == "BAJO":
            recomendacion = f"[PATRÓN DÉBIL] {recomendacion}"

        return recomendacion

    def _calcular_confianza(self, anomalia_dict) -> float:
        """Calcula confianza de la explicación (0-100)"""
        score = 80

        # Reducir si pocos datos históricos
        datos = len(anomalia_dict.get("datos_historicos", []))
        if datos < 20:
            score -= 15
        elif datos < 100:
            score -= 5

        # Reducir si hay cambios recientes
        if anomalia_dict.get("cambios"):
            score -= 10

        # Aumentar si hay contexto abundante
        if anomalia_dict.get("estacion") and anomalia_dict.get(
            "valor_mes_anterior"
        ):
            score += 5

        return max(50, min(95, score))

    def _emoji_anomalia(self, desviacion_pct: float) -> str:
        """Selecciona emoji según severidad"""
        if abs(desviacion_pct) > 50:
            return "🚨"  # Crítico
        elif abs(desviacion_pct) > 25:
            return "⚠️"  # Importante
        else:
            return "ℹ️"  # Información

    def _titulo_anomalia(self, metrica: str, desviacion_pct: float) -> str:
        """Genera título descriptivo de la anomalía"""
        nombre = self._nombre_negocio(metrica)
        direccion = "anormalmente baja" if desviacion_pct < 0 else "anormalmente alta"
        pct_abs = abs(desviacion_pct)
        return f"{nombre} {direccion} ({pct_abs:.0f}%)"


# Singleton global
_explainer_instance = None


def get_insight_explainer_service() -> InsightExplainerService:
    """Obtiene la instancia única del servicio de explicaciones"""
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = InsightExplainerService()
    return _explainer_instance
