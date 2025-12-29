"""
Servicio de acceso a conexión BD para módulos utils.

Encapsula get_db_connection() de infraestructura, proporcionando
una abstracción limpia sin acoplamiento directo a database.

Patrón: Inyección de dependencias. Utils recibe DbConnectionService
en lugar de acceder directo a database.
"""
from contextlib import contextmanager
from typing import Generator, Any


class DbConnectionService:
    """Servicio que encapsula acceso a BD desde utils."""
    
    def __init__(self, get_connection_callable=None):
        """
        Args:
            get_connection_callable: Función que retorna context manager de conexión.
                                    Ej: database.get_connection
        """
        if get_connection_callable is None:
            # Fallback para backward compatibility
            from database import get_connection
            get_connection_callable = get_connection
        
        self._get_connection = get_connection_callable
    
    @contextmanager
    def connection(self) -> Generator[Any, None, None]:
        """Context manager para obtener conexión segura."""
        with self._get_connection() as conn:
            yield conn


# Singleton para backward compatibility
_default_service = None


def get_db_service() -> DbConnectionService:
    """Factory para obtener servicio singleton."""
    global _default_service
    if _default_service is None:
        _default_service = DbConnectionService()
    return _default_service


def set_db_service(service: DbConnectionService) -> None:
    """Permite inyectar servicio custom (testing, etc)."""
    global _default_service
    _default_service = service
