"""
Script para verificar los datos del mantenimiento y corregir el FK
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database.database import get_db_connection

print("=" * 70)
print("ANÁLISIS DE DATOS DE MANTENIMIENTO")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Verificar si la tabla existe
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mantenimiento_herramienta'")
    if not cur.fetchone():
        print("\n⚠️  Tabla mantenimiento_herramienta no existe")
        print("   Recreando tabla vacía...")
        
        cur.execute("""
            CREATE TABLE mantenimiento_herramienta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                herramienta_id INTEGER NOT NULL,
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
                estado_previo_herramienta TEXT,
                fecha_completado DATE,
                FOREIGN KEY (herramienta_id) REFERENCES herramienta(id) ON DELETE CASCADE
            )
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mant_estado 
            ON mantenimiento_herramienta(estado_actual, herramienta_id)
        """)
        
        conn.commit()
        
        print("   ✅ Tabla creada correctamente con FK → herramienta")
        print("\n" + "=" * 70)
        print("CORRECCIÓN COMPLETADA")
        print("=" * 70)
        print("\nLa tabla está lista para recibir registros de mantenimiento.")
        print("El error 'herramienta_old' ha sido corregido.")
        print("=" * 70)
        
    else:
        print("\n✅ Tabla mantenimiento_herramienta existe")
        
        # Verificar FK
        cur.execute("PRAGMA foreign_key_list(mantenimiento_herramienta)")
        fks = cur.fetchall()
        if fks:
            print(f"   FK actual: {fks[0][3]} → {fks[0][2]}")
            if fks[0][2] == 'herramienta':
                print("   ✅ FK correcta")
            else:
                print("   ❌ FK incorrecta, necesita corrección")
