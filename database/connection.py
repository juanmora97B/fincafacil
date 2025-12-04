"""
Sistema moderno de conexión a base de datos para FincaFácil

Este módulo proporciona:
- get_connection(): Context manager para conexiones
- DatabaseManager: Clase para operaciones comunes
- db: Instancia global del DatabaseManager
"""

from __future__ import annotations
import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Iterator
from contextlib import contextmanager

# Importar las funciones existentes del sistema legacy
from .database import get_db_connection, DB_PATH

logger = logging.getLogger(__name__)


@contextmanager
def get_connection(db_path: Optional[str] = None) -> Iterator[sqlite3.Connection]:
    """
    Context manager moderno para obtener conexión a BD.
    
    Uso:
        from database import get_connection
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM animal")
    
    Args:
        db_path: Ruta opcional a la base de datos
        
    Yields:
        sqlite3.Connection: Conexión configurada a la BD
    """
    # Delegar al sistema existente
    with get_db_connection(db_path or DB_PATH) as conn:
        yield conn


class DatabaseManager:
    """
    Manager centralizado para operaciones comunes en la base de datos.
    
    Proporciona métodos de alto nivel para:
    - Consultas SELECT
    - Inserciones, actualizaciones, eliminaciones
    - Transacciones
    - Verificaciones de tabla
    
    Ejemplo:
        db = DatabaseManager()
        animales = db.execute_query("SELECT * FROM animal WHERE finca_id = ?", (1,))
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa el DatabaseManager.
        
        Args:
            db_path: Ruta opcional a la base de datos
        """
        self.db_path = db_path or DB_PATH
        self.logger = logging.getLogger(f"{__name__}.DatabaseManager")
    
    @contextmanager
    def _get_conn(self) -> Iterator[sqlite3.Connection]:
        """Context manager interno para conexiones."""
        with get_connection(self.db_path) as conn:
            yield conn
    
    def execute_query(
        self,
        query: str,
        params: tuple = None,
        fetch_one: bool = False,
        fetch_all: bool = True
    ) -> Any:
        """
        Ejecuta una consulta SELECT.
        
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
            fetch_one: Si True, retorna un registro
            fetch_all: Si True, retorna todos los registros (default)
            
        Returns:
            Registros como diccionarios o None
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                if fetch_one:
                    row = cursor.fetchone()
                    return dict(row) if row else None
                elif fetch_all:
                    return [dict(row) for row in cursor.fetchall()]
                else:
                    return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Error ejecutando query: {query} - {e}")
            raise
    
    def execute_one(
        self,
        query: str,
        params: tuple = None
    ) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta que retorna un solo registro.
        
        Args:
            query: Consulta SQL
            params: Parámetros
            
        Returns:
            Registro como diccionario o None
        """
        return self.execute_query(query, params, fetch_one=True, fetch_all=False)
    
    def execute_update(
        self,
        query: str,
        params: tuple = None
    ) -> int:
        """
        Ejecuta una operación INSERT, UPDATE o DELETE.
        
        Args:
            query: Consulta SQL
            params: Parámetros
            
        Returns:
            Número de filas afectadas
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            self.logger.error(f"Error ejecutando update: {query} - {e}")
            raise
    
    def execute_many(
        self,
        query: str,
        params_list: List[tuple]
    ) -> int:
        """
        Ejecuta múltiples operaciones INSERT/UPDATE/DELETE.
        
        Args:
            query: Consulta SQL
            params_list: Lista de tuplas de parámetros
            
        Returns:
            Número total de filas afectadas
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            self.logger.error(f"Error ejecutando many: {query} - {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica si una tabla existe en la BD.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            True si la tabla existe
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,)
                )
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"Error verificando tabla {table_name}: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Obtiene información sobre las columnas de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Lista de diccionarios con info de columnas
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                return [
                    {
                        'cid': col[0],
                        'name': col[1],
                        'type': col[2],
                        'notnull': col[3],
                        'dflt_value': col[4],
                        'pk': col[5]
                    }
                    for col in columns
                ]
        except sqlite3.Error as e:
            self.logger.error(f"Error obteniendo info de {table_name}: {e}")
            return []
    
    def backup(self, backup_path: str) -> bool:
        """
        Realiza un backup de la base de datos.
        
        Args:
            backup_path: Ruta donde guardar el backup
            
        Returns:
            True si fue exitoso
        """
        try:
            with self._get_conn() as conn:
                backup_conn = sqlite3.connect(backup_path)
                conn.backup(backup_conn)
                backup_conn.close()
                self.logger.info(f"Backup realizado en: {backup_path}")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error realizando backup: {e}")
            return False
    
    def vacuum(self) -> bool:
        """
        Optimiza la base de datos (libera espacio).
        
        Returns:
            True si fue exitoso
        """
        try:
            with self._get_conn() as conn:
                conn.execute("VACUUM")
                self.logger.info("Base de datos optimizada")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error en VACUUM: {e}")
            return False
    
    @contextmanager
    def transaction(self):
        """
        Context manager para transacciones.
        
        Uso:
            with db.transaction():
                db.execute_update("UPDATE animal SET peso = ?", (100,))
                db.execute_update("INSERT INTO log VALUES (...)")
        
        Yields:
            None (usa execute_update dentro del contexto)
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Error en transacción: {e}")
            raise
        finally:
            if conn:
                conn.close()


# Instancia global
db = DatabaseManager()


__all__ = [
    "get_connection",
    "DatabaseManager",
    "db",
]
