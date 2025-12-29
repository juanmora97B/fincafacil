"""
Servicio de acceso a paths y rutas de configuración para módulos utils.

Encapsula get_db_path_safe() de infraestructura, permitiendo que utils
consulte rutas sin dependencia directa a database.

Patrón: Inyección de dependencias.
"""
from pathlib import Path
from typing import Optional


class PathService:
    """Servicio que encapsula acceso a paths de configuración."""
    
    def __init__(self, get_db_path_callable=None):
        """
        Args:
            get_db_path_callable: Función que retorna path seguro de BD.
                                 Ej: database.database.get_db_path_safe
        """
        if get_db_path_callable is None:
            # Fallback para backward compatibility
            from database.database import get_db_path_safe
            get_db_path_callable = get_db_path_safe
        
        self._get_db_path = get_db_path_callable
    
    def get_db_path(self) -> str:
        """Retorna path seguro de BD."""
        return str(self._get_db_path())


# Singleton para backward compatibility
_default_service = None


def get_path_service() -> PathService:
    """Factory para obtener servicio singleton."""
    global _default_service
    if _default_service is None:
        _default_service = PathService()
    return _default_service


def set_path_service(service: PathService) -> None:
    """Permite inyectar servicio custom (testing, etc)."""
    global _default_service
    _default_service = service
