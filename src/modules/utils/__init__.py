"""Módulo de utilidades para FincaFácil."""

# API pública estable (Categoría A)
from modules.utils.logger import Logger

# API Legacy / Compatibilidad (Categoría B)
# Mantenida para backward compatibility; consumidores usan import directo
try:
    from modules.utils.validaciones import (  # type: ignore[attr-defined]
        validar_texto, validar_numero  # type: ignore[attr-defined]
    )
except ImportError:
    def validar_texto(*args, **kwargs): return (True, None, "")  # type: ignore[return-value]
    def validar_numero(*args, **kwargs): return (True, None, "")  # type: ignore[return-value]
    def validar_email(*args, **kwargs): return (True, None, "")
    def validar_telefono(*args, **kwargs): return (True, None, "")

# API pública estable (Categoría A)
try:
    from modules.utils.tour_manager import TourManager, TourStep, ModuleTourHelper
except ImportError:
    TourManager = None
    TourStep = None
    ModuleTourHelper = None

try:
    from modules.utils.metadata import GestorMetadatos, obtener_gestor_metadatos
except ImportError:
    GestorMetadatos = None
    obtener_gestor_metadatos = None

__all__ = [
    'Logger',
    'validar_texto',
    'validar_numero',
    'TourManager',
    'TourStep',
    'ModuleTourHelper',
    'GestorMetadatos',
    'obtener_gestor_metadatos',
]
