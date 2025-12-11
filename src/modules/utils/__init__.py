"""Módulo de utilidades para FincaFácil."""

# Importaciones críticas (siempre)
from modules.utils.logger import Logger

# Importaciones parciales para evitar errores de importación circular
try:
    from modules.utils.validaciones import (
        validar_texto, validar_numero, validar_email, validar_telefono
    )
except ImportError:
    def validar_texto(*args, **kwargs): return (True, None, "")
    def validar_numero(*args, **kwargs): return (True, None, "")
    def validar_email(*args, **kwargs): return (True, None, "")
    def validar_telefono(*args, **kwargs): return (True, None, "")

try:
    from modules.utils.ui import (
        mostrar_error, mostrar_exito, mostrar_advertencia, mostrar_info
    )
except ImportError:
    def mostrar_error(*args, **kwargs): pass
    def mostrar_exito(*args, **kwargs): pass
    def mostrar_advertencia(*args, **kwargs): pass
    def mostrar_info(*args, **kwargs): pass

# Importaciones opcionales (con try-except)
try:
    from modules.utils.exportador_datos import ExportadorDatos
except ImportError:
    ExportadorDatos = None

try:
    from modules.utils.importador_excel import ImportadorExcel
except ImportError:
    ImportadorExcel = None

try:
    from modules.utils.preferences_manager import PreferencesManager
except ImportError:
    PreferencesManager = None

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

try:
    from modules.utils.pdf_manual_generator import GeneradorPDFManual, obtener_generador_pdf
except ImportError:
    GeneradorPDFManual = None
    obtener_generador_pdf = None

__all__ = [
    'Logger',
    'validar_texto',
    'validar_numero',
    'validar_email',
    'validar_telefono',
    'mostrar_error',
    'mostrar_exito',
    'mostrar_advertencia',
    'mostrar_info',
    'ExportadorDatos',
    'ImportadorExcel',
    'PreferencesManager',
    'TourManager',
    'TourStep',
    'ModuleTourHelper',
    'GestorMetadatos',
    'obtener_gestor_metadatos',
    'GeneradorPDFManual',
    'obtener_generador_pdf',
]
