"""
Dominio Configuración - Infraestructura Gobernada
FASE 9.0.3 - Encapsulación Inicial (Catálogo Calidad Animal)

Exporta: ConfiguracionRepository, ConfiguracionService
"""

from .configuracion_service import ConfiguracionService
from .configuracion_repository import ConfiguracionRepository

__all__ = ["ConfiguracionService", "ConfiguracionRepository"]
