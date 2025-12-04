"""
Excepciones personalizadas para FincaFacil
"""

class FincaFacilError(Exception):
    """Excepción base para FincaFacil"""
    pass

class ValidationError(FincaFacilError):
    """Error de validación de datos"""
    pass

class DatabaseError(FincaFacilError):
    """Error en operaciones de base de datos"""
    pass

class ConfigError(FincaFacilError):
    """Error de configuración"""
    pass

class ImportError_(FincaFacilError):
    """Error en importaciones de datos"""
    pass
