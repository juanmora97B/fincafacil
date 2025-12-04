"""
Migración 005: Agregar campo finca_id a tablas sector y lote
"""
import sqlite3
from pathlib import Path

def migrate(conn: sqlite3.Connection):
    """Ejecuta la migración"""
    cursor = conn.cursor()
    
    print("Agregando campo finca_id a tablas sector y lote...")
    
    # Verificar si la columna finca_id ya existe en la tabla sector
    cursor.execute("PRAGMA table_info(sector)")
    columnas_sector = [col[1] for col in cursor.fetchall()]
    
    if 'finca_id' not in columnas_sector:
        print("  - Agregando finca_id a tabla sector...")
        cursor.execute("""
            ALTER TABLE sector 
            ADD COLUMN finca_id INTEGER 
            REFERENCES finca(id)
        """)
        print("  ✓ Campo finca_id agregado a sector")
    else:
        print("  ✓ Campo finca_id ya existe en sector")
    
    # Verificar si la columna finca_id ya existe en la tabla lote
    cursor.execute("PRAGMA table_info(lote)")
    columnas_lote = [col[1] for col in cursor.fetchall()]
    
    if 'finca_id' not in columnas_lote:
        print("  - Agregando finca_id a tabla lote...")
        cursor.execute("""
            ALTER TABLE lote 
            ADD COLUMN finca_id INTEGER 
            REFERENCES finca(id)
        """)
        print("  ✓ Campo finca_id agregado a lote")
    else:
        print("  ✓ Campo finca_id ya existe en lote")
    
    conn.commit()
    print("✓ Migración 005 completada correctamente")

def rollback(conn: sqlite3.Connection):
    """Revierte la migración
    Nota: SQLite no soporta DROP COLUMN directamente en versiones antiguas,
    por lo que el rollback requeriría recrear las tablas sin la columna.
    """
    print("⚠ Advertencia: El rollback de esta migración requeriría recrear las tablas.")
    print("  No se puede eliminar columnas en SQLite de forma directa.")
    print("  Si necesita revertir, debe hacerlo manualmente o recrear la base de datos.")

if __name__ == "__main__":
    # Para pruebas directas
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from database import db
    
    with db.get_connection() as conn:
        migrate(conn)
