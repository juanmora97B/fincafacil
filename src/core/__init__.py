"""
Core del sistema FincaFacil - Excepciones y constantes
"""

from src.core.exceptions import ValidationError, DatabaseError, ConfigError

__all__ = [
    "ValidationError",
    "DatabaseError", 
    "ConfigError",
]
