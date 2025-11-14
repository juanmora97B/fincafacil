"""
Paquete de base de datos de FincaFácil

Este módulo expone la API pública del paquete `database`:
- get_db_connection
- init_database
- check_database_exists
- db
- DatabaseManager
- get_table_info (si está disponible)

Notas:
- No ejecuta lógica ni imprime al importar (solo cuando se ejecuta como script).
- Provee wrappers seguros para llamadas opcionales a funciones que podrían no existir
  en versiones antiguas del módulo unificado.
"""

from __future__ import annotations
import logging
from typing import Callable, List, Optional

log = logging.getLogger("FincaFacil.database")

# Importar desde conexion_unified (se asume que existe)
try:
    from .conexion_unified import (
        get_db_connection,
        init_database,
        check_database_exists,
        db,
        DatabaseManager,
        get_table_info as _get_table_info,
    )
    # indicar que get_table_info existe
    def get_table_info() -> List[str]:
        try:
            return list(_get_table_info())
        except Exception as e:
            log.warning("get_table_info falló al ejecutarse: %s", e)
            return []
except ImportError as exc:
    # Si por alguna razón conexion_unified no está disponible, exponemos fallback mínimo
    # Esto evita que el paquete rompa la importación en casos extremos (p. ej. pruebas)
    log.warning("No se pudo importar database.conexion_unified: %s", exc)

    # Definir fallbacks mínimos
    def get_db_connection():
        raise RuntimeError("database.conexion_unified no disponible")

    def init_database():
        raise RuntimeError("database.conexion_unified no disponible")

    def check_database_exists() -> bool:
        return False

    class DatabaseManager:
        def __init__(self, db_path: Optional[str] = None):
            raise RuntimeError("database.conexion_unified no disponible")

    db = None

    def get_table_info() -> List[str]:
        return []

# API pública exportada
__all__ = [
    "get_db_connection",
    "init_database",
    "check_database_exists",
    "db",
    "DatabaseManager",
    "get_table_info",
]

# Ejecutar solo cuando se corre el módulo directamente (no al importar)
if __name__ == "__main__":
    # Inicializar logging básico si no existe configuración externa
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    log = logging.getLogger("FincaFacil.database.__main__")

    log.info("Paquete `database` ejecutado como script. Comprobando estado de la BD...")
    try:
        exists = check_database_exists()
        log.info("Base de datos existe: %s", exists)
    except Exception as e:
        log.error("Error verificando existencia de BD: %s", e)

    try:
        tables = get_table_info()
        log.info("Tablas detectadas: %d", len(tables))
        for t in tables:
            log.info(" - %s", t)
    except Exception as e:
        log.warning("No se pudo obtener información de tablas: %s", e)

    log.info("Iniciando inicialización de BD...")
    try:
        init_database()
        log.info("Base de datos inicializada")
    except Exception as e:
        log.error("Error inicializando BD: %s", e)