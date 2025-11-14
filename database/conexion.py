"""
MÓDULO DE COMPATIBILIDAD - Redirige a la base de datos unificada
Mantiene compatibilidad con todos los módulos existentes
"""

import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("FincaFacil.Compat")

try:
    # Importar desde la base de datos unificada
    from .conexion_unified import (
        get_db_connection,
        init_database,
        check_database_exists,
        db,
        DatabaseManager
    )
    
    log.info("✅ Usando base de datos unificada")
    
except ImportError as e:
    log.error(f"❌ Error importando base de datos unificada: {e}")
    
    # Fallback básico para evitar errores críticos
    import sqlite3
    import os
    from pathlib import Path
    from contextlib import contextmanager
    
    class FallbackConfig:
        BASE_DIR = Path(__file__).parent.parent
        DB_PATH = BASE_DIR / "database" / "fincafacil.db"
    
    config = FallbackConfig()
    
    @contextmanager
    def get_db_connection():
        conn = sqlite3.connect(config.DB_PATH)
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database():
        log.warning("⚠️ Usando fallback - inicializar manualmente la BD unificada")
    
    def check_database_exists():
        return os.path.exists(config.DB_PATH)
    
    class DatabaseManager:
        def __init__(self, db_path=None):
            self.db_path = db_path or config.DB_PATH
        
        def get_connection(self):
            return sqlite3.connect(self.db_path)
        
        def ensure_database(self):
            init_database()
    
    db = DatabaseManager()

# Exportar para compatibilidad
__all__ = [
    'get_db_connection', 
    'init_database', 
    'check_database_exists', 
    'db', 
    'DatabaseManager'
]

# Mensaje de confirmación
if __name__ == "__main__":
    print("🔧 Módulo de compatibilidad cargado correctamente")
    print("📁 Redirigiendo a: database.conexion_unified")