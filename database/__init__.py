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
from contextlib import contextmanager

# Importar desde los módulos correctos
try:
    # Nuevo sistema de conexión (módulo connection.py)
    from .connection import get_connection, db, DatabaseManager
    
    # Importar también desde database.py (ya existente) para compatibilidad
    from .database import (
        get_db_connection,
        verificar_base_datos,
        inicializar_base_datos,
        ejecutar_consulta,
        obtener_tablas,
        asegurar_esquema_minimo,
        asegurar_esquema_completo,
        DB_PATH
    )
    
    # Alias para compatibilidad
    check_database_exists = verificar_base_datos
    init_database = inicializar_base_datos
    get_table_info = obtener_tablas
    
    log = logging.getLogger("FincaFacil.database")
    log.info("Database module cargado correctamente")
    
except ImportError as exc:
    # Fallback mínimo si el módulo no está disponible
    log.error("No se pudo importar database.database: %s", exc)

    def get_db_connection():
        raise RuntimeError("database.database no disponible")

    def verificar_base_datos() -> bool:
        return False

    def inicializar_base_datos() -> bool:
        return False

    def ejecutar_consulta(query: str, parametros: tuple = None, fetch: bool = False):
        raise RuntimeError("database.database no disponible")

    def obtener_tablas() -> List[str]:
        return []

    # Aliases
    check_database_exists = verificar_base_datos
    init_database = inicializar_base_datos
    get_table_info = obtener_tablas
    
    class DatabaseManager:
        def __init__(self):
            raise RuntimeError("database.database no disponible")
    
    db = None

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