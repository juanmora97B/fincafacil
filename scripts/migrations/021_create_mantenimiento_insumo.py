"""
Migración 021: Crear tabla mantenimiento_insumo
Similar a mantenimiento_herramienta
"""

def run(conn):
    print("➡️ Ejecutando migración 021: Crear tabla mantenimiento_insumo...")
    
    try:
        cur = conn.cursor()
        
        # Verificar si la tabla ya existe
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mantenimiento_insumo'")
        if cur.fetchone():
            print("✅ Tabla mantenimiento_insumo ya existe")
            return
        
        # Crear tabla de mantenimiento de insumos
        cur.execute("""
            CREATE TABLE mantenimiento_insumo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insumo_id INTEGER NOT NULL,
                tipo_mantenimiento TEXT,
                fecha_mantenimiento DATE NOT NULL,
                descripcion TEXT,
                costo REAL,
                proveedor_servicio TEXT,
                proximo_mantenimiento DATE,
                realizado_por TEXT,
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado_actual TEXT DEFAULT 'Activo' 
                    CHECK(estado_actual IN ('Activo', 'Completado')),
                estado_previo_insumo TEXT,
                fecha_completado DATE,
                FOREIGN KEY (insumo_id) REFERENCES insumo(id) ON DELETE CASCADE
            )
        """)
        print("   ✓ Tabla mantenimiento_insumo creada")
        
        # Crear índice
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mant_insumo_estado 
            ON mantenimiento_insumo(estado_actual, insumo_id)
        """)
        print("   ✓ Índice idx_mant_insumo_estado creado")
        
        conn.commit()
        print("✅ Migración 021 completada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error en migración 021: {e}")
        raise

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    from database.database import get_db_connection
    
    with get_db_connection() as conn:
        run(conn)
