"""
Módulo de infraestructura para el dominio Salud.
Exporta únicamente el Service como punto de entrada público.
"""
from .salud_service import SaludService
from .salud_repository import SaludRepository

__all__ = ['SaludService', 'SaludRepository']
