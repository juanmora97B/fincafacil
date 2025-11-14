import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
import logging

# Configuración
class Config:
    BASE_DIR = Path(__file__).parent.parent
    DB_PATH = BASE_DIR / "database" / "fincafacil.db"
    DB_TIMEOUT = 30

config = Config()

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger("FincaFacil.DB")

@contextmanager
def get_db_connection():
    """Context manager para conexiones seguras a la BD"""
    conn = None
    try:
        conn = sqlite3.connect(config.DB_PATH, timeout=config.DB_TIMEOUT)
        conn.row_factory = sqlite3.Row
        log.debug("Conexión a BD establecida")
        yield conn
    except sqlite3.Error as e:
        log.error(f"Error de base de datos: {e}")
        raise
    finally:
        if conn:
            conn.close()
            log.debug("Conexión a BD cerrada")

def recreate_database():
    """Elimina y recrea la base de datos completa"""
    if os.path.exists(config.DB_PATH):
        os.remove(config.DB_PATH)
        log.info("🗑️ Base de datos anterior eliminada")
    
    init_database()
    log.info("🔄 Base de datos recreada exitosamente")            

def init_database():
    """Inicializa la base de datos con el SCHEMA COMPLETO"""
    from database.schema import create_tables
    
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Crear todas las tablas en ORDEN CORRECTO
            tables_created = 0
            for table_name, create_stmt in create_tables.items():
                try:
                    cursor.execute(create_stmt)
                    tables_created += 1
                    log.info(f"✅ Tabla creada: {table_name}")
                except sqlite3.Error as e:
                    log.warning(f"⚠️ Tabla {table_name} ya existe o error: {e}")
            
            conn.commit()
            log.info(f"🎉 Base de datos inicializada. Tablas: {tables_created}")
            
            # Insertar datos básicos DESPUÉS de crear tablas
            insert_basic_data()
            
    except Exception as e:
        log.error(f"❌ Error inicializando BD: {e}")
        raise

def insert_basic_data():
    """Inserta datos básicos esenciales para el sistema"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar estructura de tabla raza antes de insertar
            cursor.execute("PRAGMA table_info(raza)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'codigo' in columns:
                # Razas básicas - solo si existe columna codigo
                razas = [
                    ('HOL', 'Holstein', 'Lechero', 'Ganado lechero especializado'),
                    ('ANG', 'Angus', 'Carne', 'Ganado de carne de alta calidad'),
                    ('BRA', 'Brahman', 'Doble propósito', 'Resistente al clima tropical'),
                    ('GYR', 'Gyr', 'Lechero', 'Ganado lechero tropical'),
                    ('CEB', 'Cebú', 'Carne', 'Ganado resistente')
                ]
                
                for codigo, nombre, tipo, desc in razas:
                    cursor.execute(
                        "INSERT OR IGNORE INTO raza (codigo, nombre, tipo_ganado, descripcion) VALUES (?, ?, ?, ?)",
                        (codigo, nombre, tipo, desc)
                    )
            else:
                # Versión alternativa sin codigo
                razas = [
                    ('Holstein', 'Ganado lechero especializado', 'Lechero'),
                    ('Angus', 'Ganado de carne de alta calidad', 'Carne'),
                    ('Brahman', 'Resistente al clima tropical', 'Doble propósito')
                ]
                
                for nombre, desc, tipo in razas:
                    cursor.execute(
                        "INSERT OR IGNORE INTO raza (nombre, descripcion, tipo_ganado) VALUES (?, ?, ?)",
                        (nombre, desc, tipo)
                    )
            
            # Finca por defecto
            cursor.execute(
                "INSERT OR IGNORE INTO finca (codigo, nombre, propietario, ubicacion) VALUES (?, ?, ?, ?)",
                ('FINCA01', 'Finca Principal', 'Propietario', 'Ubicación Principal')
            )
            
            conn.commit()
            log.info("✅ Datos básicos insertados")
            
    except Exception as e:
        log.error(f"⚠️ Error insertando datos básicos: {e}")

def check_database_exists():
    """Verifica si la base de datos existe y está completa"""
    if not os.path.exists(config.DB_PATH):
        return False
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animal'")
            return cursor.fetchone() is not None
    except:
        return False

def get_table_info():
    """Obtiene información de todas las tablas existentes"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
    except:
        return []

# Compatibilidad con módulos existentes
class DatabaseManager:
    """Wrapper para compatibilidad con código existente"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or config.DB_PATH
        if not check_database_exists():
            init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def ensure_database(self):
        if not check_database_exists():
            init_database()

# Instancia global para compatibilidad
db = DatabaseManager()

if __name__ == "__main__":
    print("🔧 Inicializando base de datos unificada...")
    init_database()
    tables = get_table_info()
    print(f"✅ Base de datos lista. Tablas: {len(tables)}")
    for table in tables:
        print(f"   - {table}")