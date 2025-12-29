"""
Sistema de Colores para Módulos
Proporciona acceso a los colores del sistema en cada módulo
"""

from typing import Tuple

MODULO_COLORES = {
    "dashboard": ("#0F6CBD", "#3FA9F5"),
    "animales": ("#2E7D32", "#52C41A"),
    "reproduccion": ("#C2185B", "#F06292"),
    "salud": ("#C62828", "#EF5350"),
    "potreros": ("#2F7D32", "#5FB760"),
    "tratamientos": ("#7B1FA2", "#AE7AE7"),
    "ventas": ("#EF6C00", "#FF9800"),
    "insumos": ("#0277BD", "#29B6F6"),
    "herramientas": ("#4E585F", "#90A4AE"),
    "reportes": ("#5E35B1", "#9575CD"),
    "nomina": ("#00695C", "#26A69A"),
    "empleados": ("#00838F", "#00ACC1"),
    "configuracion": ("#455A64", "#90A4AE"),
    "ajustes": ("#37474F", "#78909C"),
    "leche": ("#F57F17", "#FBC02D"),
}

def obtener_colores(modulo: str) -> Tuple[str, str]:
    """
    Obtiene el par de colores (primario, hover) para un módulo
    
    Args:
        modulo: Nombre del módulo (ej: 'dashboard', 'animales')
    
    Returns:
        Tupla (color_primario, color_hover)
    
    Ejemplo:
        >>> color_bg, color_hover = obtener_colores('salud')
        >>> # color_bg = '#C62828', color_hover = '#EF5350'
    """
    return MODULO_COLORES.get(modulo, ("#1976D2", "#2196F3"))

def obtener_color_primario(modulo: str) -> str:
    """Obtiene solo el color primario de un módulo"""
    color_bg, _ = obtener_colores(modulo)
    return color_bg

def obtener_color_hover(modulo: str) -> str:
    """Obtiene solo el color hover de un módulo"""
    _, color_hover = obtener_colores(modulo)
    return color_hover
