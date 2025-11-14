"""
Paquete de base de datos - Provee acceso unificado a la BD
"""

from .conexion_unified import (
    get_db_connection,
    init_database,
    check_database_exists,
    db,
    DatabaseManager
)

# Exportar funciones principales
__all__ = [
    'get_db_connection',
    'init_database', 
    'check_database_exists',
    'db',
    'DatabaseManager'
]
"""
Paquete de base de datos - Provee acceso unificado a la BD
"""

try:
    from .conexion_unified import (
        get_db_connection,
        init_database,
        check_database_exists,
        db,
        DatabaseManager,
        get_table_info
    )
except ImportError:
    # Fallback si alguna función no existe
    from .conexion_unified import (
        get_db_connection,
        init_database,
        check_database_exists,
        db,
        DatabaseManager
    )
    
    # Definir get_table_info si no existe
    def get_table_info():
        """Obtiene información de las tablas (fallback)"""
        try:
            from .conexion_unified import get_table_info as gti
            return gti()
        except:
            return []

# Exportar funciones principales
__all__ = [
    'get_db_connection',
    'init_database', 
    'check_database_exists',
    'db',
    'DatabaseManager',
    'get_table_info'
]

# Mensaje de inicialización
if __name__ == "__main__":
    print("✅ Paquete de base de datos cargado correctamente")
    try:
        tables = get_table_info()
        print(f"📊 Tablas disponibles: {len(tables)}")
    except:
        print("📊 Funcionalidad básica cargada")
# Mensaje de inicialización
if __name__ == "__main__":
    print("✅ Paquete de base de datos cargado correctamente")
    print("📊 Tablas disponibles:", len(get_table_info()) if hasattr(get_db_connection, '__wrapped__') else "Funcional")