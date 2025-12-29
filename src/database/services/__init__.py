"""
Servicios de infraestructura para módulos utils.

Inicializa los servicios de conexión y paths de forma centralizada,
permitiendo inyección de dependencias limpia.
"""

from .connection_service import DbConnectionService, get_db_service, set_db_service
from .path_service import PathService, get_path_service, set_path_service

__all__ = [
    "DbConnectionService",
    "get_db_service",
    "set_db_service",
    "PathService",
    "get_path_service",
    "set_path_service",
]
