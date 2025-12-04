"""Script para verificar el estado de la tabla mantenimiento_herramienta y aplicar migración 017"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import get_db_connection

print("=" * 60)
print("VERIFICACIÓN DE TABLA mantenimiento_herramienta")
print("=" * 60)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Verificar columnas actuales
    cur.execute('PRAGMA table_info(mantenimiento_herramienta)')
    columnas = cur.fetchall()
    
    print("\nColumnas actuales:")
    print("-" * 60)
    for col in columnas:
        print(f"{col[1]:30} {col[2]:15} {'NOT NULL' if col[3] else ''}")
    
    columnas_nombres = [col[1] for col in columnas]
    
    # Verificar si necesita migración 017
    necesita_017 = 'estado_actual' not in columnas_nombres
    
    print("\n" + "=" * 60)
    if necesita_017:
        print("⚠️  MIGRACIÓN 017 NECESARIA")
        print("=" * 60)
        print("\nFaltan las siguientes columnas:")
        print("  • estado_actual")
        print("  • estado_previo_herramienta")
        print("  • fecha_completado")
        
        # Aplicar migración 017
        print("\n🔧 Aplicando migración 017...")
        try:
            # Agregar estado_actual
            cur.execute("""
                ALTER TABLE mantenimiento_herramienta 
                ADD COLUMN estado_actual TEXT DEFAULT 'Activo' 
                CHECK(estado_actual IN ('Activo', 'Completado'))
            """)
            print("✓ Campo estado_actual agregado")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("✓ Campo estado_actual ya existe")
            else:
                print(f"✗ Error: {e}")
        
        try:
            # Agregar estado_previo_herramienta
            cur.execute("""
                ALTER TABLE mantenimiento_herramienta 
                ADD COLUMN estado_previo_herramienta TEXT
            """)
            print("✓ Campo estado_previo_herramienta agregado")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("✓ Campo estado_previo_herramienta ya existe")
            else:
                print(f"✗ Error: {e}")
        
        try:
            # Agregar fecha_completado
            cur.execute("""
                ALTER TABLE mantenimiento_herramienta 
                ADD COLUMN fecha_completado DATE
            """)
            print("✓ Campo fecha_completado agregado")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("✓ Campo fecha_completado ya existe")
            else:
                print(f"✗ Error: {e}")
        
        try:
            # Crear índice
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_mant_estado 
                ON mantenimiento_herramienta(estado_actual, herramienta_id)
            """)
            print("✓ Índice idx_mant_estado creado")
        except Exception as e:
            print(f"⚠️  Error creando índice: {e}")
        
        conn.commit()
        print("\n✅ Migración 017 completada exitosamente")
    else:
        print("✅ MIGRACIÓN 017 YA APLICADA")
        print("=" * 60)
        print("\nLa tabla ya tiene las columnas necesarias:")
        print("  ✓ estado_actual")
        print("  ✓ estado_previo_herramienta") if 'estado_previo_herramienta' in columnas_nombres else print("  ✗ estado_previo_herramienta")
        print("  ✓ fecha_completado") if 'fecha_completado' in columnas_nombres else print("  ✗ fecha_completado")
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60)
