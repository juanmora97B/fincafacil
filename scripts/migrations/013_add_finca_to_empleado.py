"""
Migración 013: Agregar id_finca a tabla empleado
Objetivo: Vincular empleados a una finca específica para separación de nómina
"""
import sqlite3
from pathlib import Path

def apply_migration(conn):
    cursor = conn.cursor()
    
    print("Iniciando migración 013: Agregar id_finca a empleado...")
    
    # 1. Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(empleado)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'id_finca' in columns:
        print("  ⚠️ La columna id_finca ya existe en empleado. Migración omitida.")
        return
    
    # 2. Obtener finca por defecto
    cursor.execute("SELECT id FROM finca WHERE estado NOT IN ('Inactivo', 'Eliminado') LIMIT 1")
    default_finca_row = cursor.fetchone()
    if not default_finca_row:
        print("  ⚠️ No hay finca activa. Creando finca por defecto...")
        cursor.execute("""
            INSERT INTO finca (codigo, nombre, estado) 
            VALUES ('DEFAULT', 'Finca Principal', 'Activo')
        """)
        conn.commit()
        cursor.execute("SELECT id FROM finca WHERE codigo = 'DEFAULT'")
        default_finca_row = cursor.fetchone()
    
    default_finca_id = default_finca_row[0]
    print(f"  → Finca por defecto: ID {default_finca_id}")
    
    # 3. Agregar columna id_finca
    print("  → Agregando columna id_finca a empleado...")
    cursor.execute(f"""
        ALTER TABLE empleado 
        ADD COLUMN id_finca INTEGER DEFAULT {default_finca_id}
    """)
    
    # 4. Actualizar registros existentes NULL
    cursor.execute(f"""
        UPDATE empleado 
        SET id_finca = {default_finca_id} 
        WHERE id_finca IS NULL
    """)
    rows_updated = cursor.rowcount
    print(f"  → Actualizados {rows_updated} empleados con finca por defecto")
    
    # 5. Crear índice para mejorar consultas
    print("  → Creando índice idx_empleado_finca...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_empleado_finca 
        ON empleado(id_finca)
    """)
    
    # 6. Nota: SQLite no permite ALTER TABLE ADD CONSTRAINT en columnas existentes
    # La FK se validará en código
    print("  ℹ️ Nota: FK empleado.id_finca → finca.id se valida en código (limitación SQLite)")
    
    conn.commit()
    print("✅ Migración 013 completada exitosamente")

def rollback_migration(conn):
    """Rollback no trivial en SQLite (requiere recrear tabla)"""
    print("⚠️ Rollback de migración 013:")
    print("  → SQLite no soporta DROP COLUMN directamente")
    print("  → Se requiere recrear tabla sin id_finca manualmente si es necesario")

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from database import get_connection
    
    with get_connection() as conn:
        apply_migration(conn)
