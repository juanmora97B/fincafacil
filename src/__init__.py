"""
FincaFacil - Sistema de Gestión Ganadera
Paquete principal del sistema
"""

__version__ = "2.0.0"
__author__ = "FincaFacil Team"

from src.core.exceptions import ValidationError, DatabaseError

__all__ = [
    "ValidationError",
    "DatabaseError",
]
