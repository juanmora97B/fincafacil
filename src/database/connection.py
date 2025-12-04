"""
Sistema de conexión unificado a base de datos
Consolidación de database/database.py con un enfoque moderno
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURACIÓN
# ============================================

BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "database" / "fincafacil.db"
DB_TIMEOUT = 30
DB_JOURNAL_MODE = "WAL"
DB_PRAGMA_FOREIGN_KEYS = True


# ============================================
# CONTEXT MANAGER
# ============================================

@contextmanager
def get_connection(db_path: Optional[str] = None):
    """
    Context manager para obtener conexión a la base de datos
    
    Uso:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
    
    Args:
        db_path: Ruta opcional a la BD (default: fincafacil.db)
        
    Yields:
        sqlite3.Connection: Conexión configurada
        
    Raises:
        sqlite3.Error: Si hay error en la conexión
    """
    path = db_path or DB_PATH
    conn = None
    try:
        # Asegurar que existe el directorio
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        
        # Conectar con configuración optimizada
        conn = sqlite3.connect(str(path), timeout=DB_TIMEOUT)
        conn.row_factory = sqlite3.Row  # Acceso por columna
        conn.execute(f"PRAGMA foreign_keys = {'ON' if DB_PRAGMA_FOREIGN_KEYS else 'OFF'}")
        conn.execute(f"PRAGMA journal_mode = {DB_JOURNAL_MODE}")
        
        logger.debug(f"Conexión establecida a {path}")
        yield conn
        conn.commit()
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error de base de datos: {e}")
        raise
    finally:
        if conn:
            try:
                conn.close()
                logger.debug("Conexión cerrada")
            except Exception:
                pass


# ============================================
# CLASE MANAGER
# ============================================

class DatabaseManager:
    """Manager de base de datos para operaciones comunes"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa el manager
        
        Args:
            db_path: Ruta opcional a la BD
        """
        self.db_path = db_path or DB_PATH
    
    # ======== QUERY EXECUTION ========
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Ejecuta una query SELECT y retorna resultados
        
        Args:
            query: Query SQL
            params: Parámetros para la query
            
        Returns:
            List[Dict]: Lista de resultados como diccionarios
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Ejecuta una query y retorna un solo resultado"""
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Ejecuta INSERT/UPDATE/DELETE
        
        Returns:
            int: Número de filas afectadas
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Ejecuta múltiples inserts/updates
        
        Args:
            query: Query SQL
            params_list: Lista de tuplas de parámetros
            
        Returns:
            int: Número total de filas afectadas
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    # ======== TABLE OPERATIONS ========
    
    def table_exists(self, table_name: str) -> bool:
        """Verifica si existe una tabla"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        return self.execute_one(query, (table_name,)) is not None
    
    def get_tables(self) -> List[str]:
        """Obtiene lista de todas las tablas"""
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        rows = self.execute_query(query)
        return [row['name'] for row in rows]
    
    def get_table_info(self, table_name: str) -> List[Dict]:
        """Obtiene información de columnas de una tabla"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
    
    def get_table_count(self, table_name: str) -> int:
        """Cuenta registros en una tabla"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_one(query)
        return result['count'] if result else 0
    
    # ======== BACKUP/RESTORE ========
    
    def backup(self, backup_path: Optional[str] = None) -> bool:
        """
        Crea backup de la BD
        
        Args:
            backup_path: Ruta de destino (default: database/backup_TIMESTAMP.db)
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.db_path.parent / f"backup_{timestamp}.db"
            
            with get_connection(self.db_path) as source_conn:
                with get_connection(backup_path) as dest_conn:
                    source_conn.backup(dest_conn)
            
            logger.info(f"Backup creado: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False
    
    # ======== VACUUM/OPTIMIZE ========
    
    def vacuum(self) -> bool:
        """Optimiza la BD (VACUUM)"""
        try:
            with get_connection(self.db_path) as conn:
                conn.execute("VACUUM")
            logger.info("BD optimizada")
            return True
        except Exception as e:
            logger.error(f"Error optimizando BD: {e}")
            return False
    
    # ======== TRANSACTION ========
    
    @contextmanager
    def transaction(self):
        """
        Context manager para transacciones
        
        Uso:
            with db.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        with get_connection(self.db_path) as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise


# ============================================
# INSTANCIA GLOBAL
# ============================================

db = DatabaseManager()


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def check_database_exists(path: Optional[str] = None) -> bool:
    """Verifica si existe el archivo de BD"""
    db_path = Path(path or DB_PATH)
    return db_path.exists() and db_path.is_file()


def get_database_size(path: Optional[str] = None) -> int:
    """Obtiene tamaño de la BD en bytes"""
    db_path = Path(path or DB_PATH)
    if db_path.exists():
        return db_path.stat().st_size
    return 0


def get_database_modified_time(path: Optional[str] = None) -> Optional[datetime]:
    """Obtiene fecha de última modificación"""
    db_path = Path(path or DB_PATH)
    if db_path.exists():
        mtime = db_path.stat().st_mtime
        return datetime.fromtimestamp(mtime)
    return None
