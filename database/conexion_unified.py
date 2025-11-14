"""
conexion_unified.py
Módulo profesional para manejo centralizado de la base de datos SQLite en FincaFácil.

Incluye:
- Conexión segura y reutilizable
- PRAGMA foreign_keys = ON
- row_factory para acceso tipo diccionario
- DatabaseManager para manejo unificado
- Funciones utilitarias para crear/verificar BD
"""

from __future__ import annotations
import os
import sqlite3
import logging
from typing import Optional, List

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE LOGS
# ---------------------------------------------------------------------
log = logging.getLogger("FincaFacil.database")
if not log.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


# ---------------------------------------------------------------------
# CONFIGURACIÓN DE RUTA DE BASE DE DATOS
# ---------------------------------------------------------------------
def _resolve_database_path() -> str:
    """
    Determina de forma segura dónde debe guardarse la base de datos.
    Compatible con PyInstaller y evita rutas relativas inseguras.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_dir, "fincafacil.db")
    return db_path


DB_PATH = _resolve_database_path()


# ---------------------------------------------------------------------
# FUNCIÓN PRINCIPAL DE CONEXIÓN
# ---------------------------------------------------------------------
def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Retorna una conexión configurada con buenas prácticas."""
    path = db_path or DB_PATH

    try:
        conn = sqlite3.connect(path, timeout=10)
        conn.row_factory = sqlite3.Row

        # Activar integridad referencial
        conn.execute("PRAGMA foreign_keys = ON")

        return conn
    except Exception as e:
        log.error("Error obteniendo conexión a BD: %s", e)
        raise


# ---------------------------------------------------------------------
# CLASE ADMINISTRADORA DE BD
# ---------------------------------------------------------------------
class DatabaseManager:
    """Manejador central de base de datos con caching de conexión."""

    _conn: Optional[sqlite3.Connection] = None

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_PATH

    def get_connection(self) -> sqlite3.Connection:
        if DatabaseManager._conn is None:
            DatabaseManager._conn = get_db_connection(self.db_path)
        return DatabaseManager._conn

    def close_connection(self):
        if DatabaseManager._conn is not None:
            DatabaseManager._conn.close()
            DatabaseManager._conn = None
            log.info("Conexión a BD cerrada correctamente.")

    def execute(self, query: str, params: tuple = ()):
        """Ejecuta una consulta sin retorno."""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            log.error("Error en execute(): %s | Query: %s", e, query)
            return False

    def fetchall(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()
        except Exception as e:
            log.error("Error en fetchall(): %s | Query: %s", e, query)
            return []

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchone()
        except Exception as e:
            log.error("Error en fetchone(): %s | Query: %s", e, query)
            return None


# Instancia global reutilizable
db = DatabaseManager()


# ---------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------
def check_database_exists(path: Optional[str] = None) -> bool:
    """Retorna True si el archivo de BD ya existe."""
    return os.path.exists(path or DB_PATH)


def init_database(schema_sql: Optional[str] = None):
    """
    Inicializa la base de datos si no existe.
    Puede recibir un schema SQL completo.
    """
    if check_database_exists():
        log.info("BD ya existe, no se creará nuevamente.")
        return

    log.info("Creando BD en: %s", DB_PATH)
    conn = get_db_connection()

    if schema_sql:
        try:
            conn.executescript(schema_sql)
            conn.commit()
            log.info("Base de datos creada con schema proporcionado.")
        except Exception as e:
            log.error("Error ejecutando schema inicial: %s", e)
    else:
        log.warning("init_database() llamada sin un schema. BD vacía creada.")

    conn.close()


# ---------------------------------------------------------------------
# MÉTODO PARA CONSULTAR TABLAS EXISTENTES
# ---------------------------------------------------------------------
def get_table_info() -> List[str]:
    """Retorna una lista con los nombres de las tablas en la BD."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        return [row["name"] for row in rows]
    except Exception as e:
        log.error("Error obteniendo tabla de BD: %s", e)
        return []


# ---------------------------------------------------------------------
# EJECUCIÓN DIRECTA DEL MÓDULO (para pruebas)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    log.info("Probando conexión unificada...")
    log.info("Ruta de BD: %s", DB_PATH)

    exists = check_database_exists()
    log.info("¿Existe la BD?: %s", exists)

    tables = get_table_info()
    log.info("Tablas detectadas (%d): %s", len(tables), tables)
