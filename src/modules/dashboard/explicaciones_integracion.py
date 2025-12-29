"""
Integración FASE 10 con Dashboard
Genera automáticamente explicaciones para anomalías y patrones detectados.
"""

from typing import Dict, Optional, Any
from src.services.insight_explainer_service import get_insight_explainer_service
import json
from datetime import datetime


class ExplicacionesCache:
    """Cache simple para explicaciones generadas (evita regenerar)"""
    def __init__(self):
        self.explicaciones = {}
    
    def get(self, alerta_id: str) -> Optional[Dict]:
        return self.explicaciones.get(alerta_id)
    
    def set(self, alerta_id: str, explicacion: Dict):
        self.explicaciones[alerta_id] = explicacion
    
    def clear(self):
        self.explicaciones.clear()


# Instancia global del cache
_explicaciones_cache = ExplicacionesCache()


def obtener_explicacion_para_alerta(alerta_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Genera una explicación para una alerta de anomalía o patrón.
    
    Args:
        alerta_dict: Diccionario con datos de la alerta:
            - id: str (identificador único)
            - tipo: str ("anomalia_productiva", "anomalia_financiera", "patron_*")
            - metrica: str (nombre de la métrica)
            - valor_observado: float
            - valor_esperado: float
            - periodo: str (YYYY-MM-DD)
            - datos_historicos: list de valores numéricos
            - estacion: str (opcional)
            - cambios: list (cambios recientes)
            - patrones: dict (patrones detectados)
    
    Returns:
        Dict con ExplanationReport o None si falla
    """
    try:
        alerta_id = alerta_dict.get("id")
        
        # Verificar cache primero
        if alerta_id:
            cached = _explicaciones_cache.get(alerta_id)
            if cached:
                return cached
        
        explainer = get_insight_explainer_service()
        tipo_alerta = alerta_dict.get("tipo", "")
        
        # Determinar si es anomalía o patrón
        if tipo_alerta.startswith("anomalia"):
            explicacion_obj = explainer.explicar_anomalia(alerta_dict)
        elif tipo_alerta.startswith("patron"):
            explicacion_obj = explainer.explicar_patron(alerta_dict)
        else:
            return None
        
        # Convertir objeto a dict
        explicacion_dict = {
            "titulo": explicacion_obj.titulo,
            "resumen": explicacion_obj.resumen,
            "evidencia": [
                {
                    "metrica_nombre": e.metrica_nombre,
                    "valor_observado": e.valor_observado,
                    "valor_esperado": e.valor_esperado,
                    "desviacion_pct": e.desviacion_pct
                }
                for e in explicacion_obj.evidencia
            ] if isinstance(explicacion_obj.evidencia, list) else [explicacion_obj.evidencia],
            "pasos": [
                {
                    "numero": p.numero,
                    "accion": p.accion,
                    "detalle": p.detalle,
                    "resultado": p.resultado
                }
                for p in explicacion_obj.pasos
            ],
            "contexto": explicacion_obj.contexto,
            "recomendacion": explicacion_obj.recomendacion,
            "confianza_pct": explicacion_obj.confianza_pct,
            "fecha_generacion": explicacion_obj.fecha_generacion
        }
        
        # Guardar en cache si tiene ID
        if alerta_id:
            _explicaciones_cache.set(alerta_id, explicacion_dict)
        
        return explicacion_dict
        
    except Exception as e:
        print(f"Error generando explicación para alerta: {e}")
        return None


def limpiar_cache_explicaciones():
    """Limpia el cache de explicaciones"""
    _explicaciones_cache.clear()


def formato_para_ui(explicacion_dict: Dict) -> str:
    """
    Formatea una explicación para mostrar en la UI.
    Retorna texto legible para mostrar en logs o debugging.
    
    Args:
        explicacion_dict: Dict con la explicación
    
    Returns:
        String formateado para mostrar
    """
    if not explicacion_dict:
        return "Sin explicación disponible"
    
    lineas = [
        f"\n{'='*70}",
        f"EXPLICACIÓN: {explicacion_dict.get('titulo', 'N/A')}",
        f"{'='*70}",
        f"\n📋 RESUMEN: {explicacion_dict.get('resumen', 'N/A')}",
        f"\n🎯 CONFIANZA: {explicacion_dict.get('confianza_pct', 'N/A')}%",
    ]
    
    # Agregar pasos
    pasos = explicacion_dict.get('pasos', [])
    if pasos:
        lineas.append(f"\n🔍 PASOS DE RAZONAMIENTO ({len(pasos)} pasos):")
        for paso in pasos:
            if isinstance(paso, dict):
                lineas.append(f"   Paso {paso.get('numero', '?')}: {paso.get('accion', 'N/A')}")
                if paso.get('detalle'):
                    lineas.append(f"   → {paso.get('detalle', '')}")
    
    # Recomendación
    recomendacion = explicacion_dict.get('recomendacion', '')
    if recomendacion:
        lineas.append(f"\n✅ RECOMENDACIÓN: {recomendacion}")
    
    lineas.append(f"\n{'='*70}\n")
    
    return "\n".join(lineas)
