"""
Paquete de base de datos de FincaFácil

Este módulo expone la API pública del paquete `database`:
- get_db_connection
- verificar_base_datos (nueva)
- inicializar_base_datos (nueva)
- ejecutar_consulta (nueva)
- obtener_tablas (nueva)
"""

from __future__ import annotations
import logging
from typing import List

log = logging.getLogger("FincaFacil.database")

# Importar desde el módulo unificado database.py
try:
    from .database import (
        get_db_connection,
        verificar_base_datos,
        inicializar_base_datos,
        ejecutar_consulta,
        obtener_tablas
    )
    
    # Alias para compatibilidad
    check_database_exists = verificar_base_datos
    init_database = inicializar_base_datos
    get_table_info = obtener_tablas
    
    # Para compatibilidad con código existente
    class DatabaseManager:
        """Clase de compatibilidad para código existente"""
        def get_connection(self):
            return get_db_connection()
            
        def execute(self, query: str, params: tuple = ()):
            ejecutar_consulta(query, params, fetch=False)
            return True
            
        def fetchall(self, query: str, params: tuple = ()):
            return ejecutar_consulta(query, params, fetch=True) or []
            
        def fetchone(self, query: str, params: tuple = ()):
            result = ejecutar_consulta(query, params, fetch=True)
            return result[0] if result else None
    
    db = DatabaseManager()
    
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
    "get_db_connection",
    "verificar_base_datos",
    "inicializar_base_datos", 
    "ejecutar_consulta",
    "obtener_tablas",
    # Compatibilidad
    "check_database_exists",
    "init_database", 
    "get_table_info",
    "db",
    "DatabaseManager"
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