"""
Paquete de base de datos de FincaFácil

API pública:
- get_connection: Context manager para conexiones
- db: Instancia global de DatabaseManager
- DatabaseManager: Manager para operaciones comunes
"""

from __future__ import annotations
import logging
from typing import List
from pathlib import Path

# Importar desde los módulos correctos (modernos)
from .connection import get_connection, db, DatabaseManager

# Importar también desde database.py (compatibilidad ampliada)
from .database import (
    get_db_connection,
    verificar_base_datos,
    inicializar_base_datos,
    ejecutar_consulta,
    obtener_tablas,
    asegurar_esquema_minimo,
    asegurar_esquema_completo,
    get_db_path_safe,
)

# Lazy DB_PATH for backwards compatibility
DB_PATH: Path | None = None

def _lazy_db_path() -> Path:
    global DB_PATH
    if DB_PATH is None:
        DB_PATH = get_db_path_safe()
    return DB_PATH

# Alias para compatibilidad
check_database_exists = verificar_base_datos
init_database = inicializar_base_datos
get_table_info = obtener_tablas

log = logging.getLogger("FincaFacil.database")
log.info("Database module cargado correctamente")

# API pública exportada
__all__ = [
    # Nuevo sistema
    "get_connection",
    "db",
    "DatabaseManager",
    # Sistema legacy (compatibilidad)
    "get_db_connection",
    "verificar_base_datos",
    "inicializar_base_datos", 
    "ejecutar_consulta",
    "obtener_tablas",
    "asegurar_esquema_minimo",
    "asegurar_esquema_completo",
    # Aliases para compatibilidad
    "check_database_exists",
    "init_database", 
    "get_table_info",
    "DB_PATH",
]

# Ejecutar solo cuando se corre el módulo directamente
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    log = logging.getLogger("FincaFacil.database.__main__")

    log.info("Paquete `database` ejecutado como script. Comprobando estado de la BD...")
    try:
        exists = verificar_base_datos()
        log.info("Base de datos existe y es válida: %s", exists)
        
        if not exists:
            log.info("Inicializando base de datos...")
            if inicializar_base_datos():
                log.info("Base de datos inicializada correctamente")
            else:
                log.error("Error inicializando base de datos")
        
        tables = obtener_tablas()
        log.info("Tablas detectadas: %d", len(tables))
        for t in tables:
            log.info(" - %s", t)
            
    except Exception as e:
        log.error("Error verificando BD: %s", e)