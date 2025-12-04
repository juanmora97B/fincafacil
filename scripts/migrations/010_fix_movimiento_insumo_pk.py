"""
Migración 010: Corregir PRIMARY KEY en tabla movimiento_insumo
================================================================

Problema:
- La tabla movimiento_insumo tiene columna 'id' pero sin PRIMARY KEY AUTOINCREMENT
- Esto causa que los registros tengan id = NULL
- No se pueden eliminar registros correctamente del historial

Solución:
- Recrear tabla con PRIMARY KEY AUTOINCREMENT correcto
- Migrar datos existentes
- Asignar IDs secuenciales a registros con id NULL
"""

import sqlite3
import sys
from pathlib import Path

# Agregar directorio raíz al path
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

DB_PATH = BASE_DIR / "database" / "fincafacil.db"

def aplicar_migracion():
    """Aplica la migración 010"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("🔧 Aplicando migración 010: Corregir PRIMARY KEY en movimiento_insumo")
        print("=" * 70)
        
        # 1. Verificar estructura actual
        cursor.execute("SELECT COUNT(*) FROM movimiento_insumo WHERE id IS NULL")
        count_null = cursor.fetchone()[0]
        print(f"\n📊 Registros con ID NULL encontrados: {count_null}")
        
        cursor.execute("SELECT COUNT(*) FROM movimiento_insumo")
        total_registros = cursor.fetchone()[0]
        print(f"📊 Total de registros en tabla: {total_registros}")
        
        # 2. Renombrar tabla actual
        print("\n🔄 Paso 1: Renombrando tabla actual...")
        cursor.execute("ALTER TABLE movimiento_insumo RENAME TO movimiento_insumo_old")
        
        # 3. Crear nueva tabla con PRIMARY KEY correcto
        print("🔄 Paso 2: Creando nueva tabla con PRIMARY KEY AUTOINCREMENT...")
        cursor.execute("""
            CREATE TABLE movimiento_insumo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insumo_id INTEGER NOT NULL,
                tipo_movimiento TEXT NOT NULL CHECK(tipo_movimiento IN ('Entrada', 'Salida', 'Ajuste')),
                cantidad REAL NOT NULL,
                motivo TEXT,
                referencia TEXT,
                animal_id INTEGER,
                potrero_id INTEGER,
                usuario TEXT,
                costo_unitario REAL,
                costo_total REAL,
                observaciones TEXT,
                fecha_movimiento DATE NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (insumo_id) REFERENCES insumo (id) ON DELETE CASCADE,
                FOREIGN KEY (animal_id) REFERENCES animal (id) ON DELETE SET NULL,
                FOREIGN KEY (potrero_id) REFERENCES potrero (id) ON DELETE SET NULL
            )
        """)
        
        # 4. Migrar datos con IDs nuevos (autoincrement asigna IDs automáticamente)
        print("🔄 Paso 3: Migrando datos existentes...")
        cursor.execute("""
            INSERT INTO movimiento_insumo (
                insumo_id, tipo_movimiento, cantidad, motivo, referencia,
                animal_id, potrero_id, usuario, costo_unitario, costo_total,
                observaciones, fecha_movimiento, fecha_registro
            )
            SELECT 
                insumo_id, tipo_movimiento, cantidad, motivo, referencia,
                animal_id, potrero_id, usuario, costo_unitario, costo_total,
                observaciones, fecha_movimiento, fecha_registro
            FROM movimiento_insumo_old
            ORDER BY fecha_registro ASC
        """)
        
        migrados = cursor.rowcount
        print(f"  ✅ {migrados} registros migrados con IDs nuevos")
        
        # 5. Eliminar tabla antigua
        print("🔄 Paso 4: Eliminando tabla antigua...")
        cursor.execute("DROP TABLE movimiento_insumo_old")
        
        # 6. Verificar resultado
        print("\n🔍 Verificando resultado:")
        cursor.execute("SELECT COUNT(*) FROM movimiento_insumo WHERE id IS NULL")
        count_null_after = cursor.fetchone()[0]
        print(f"  Registros con ID NULL: {count_null_after}")
        
        cursor.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM movimiento_insumo")
        min_id, max_id, total = cursor.fetchone()
        print(f"  ID mínimo: {min_id}")
        print(f"  ID máximo: {max_id}")
        print(f"  Total registros: {total}")
        
        # Commit
        conn.commit()
        
        print("\n" + "=" * 70)
        print("✅ MIGRACIÓN 010 COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print("\nResumen:")
        print(f"  • Tabla movimiento_insumo recreada con PRIMARY KEY AUTOINCREMENT")
        print(f"  • {migrados} registros migrados con IDs válidos")
        print(f"  • {count_null} registros con ID NULL corregidos")
        print(f"  • Rango de IDs: {min_id} - {max_id}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Error en migración 010: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("MIGRACIÓN 010: Corregir PRIMARY KEY en movimiento_insumo")
    print("=" * 70)
    
    if not DB_PATH.exists():
        print(f"❌ Base de datos no encontrada: {DB_PATH}")
        sys.exit(1)
    
    # Advertencia
    print("\n⚠️  ADVERTENCIA:")
    print("Esta migración recreará la tabla movimiento_insumo.")
    print("Todos los movimientos recibirán nuevos IDs secuenciales.")
    print("Se recomienda hacer backup de la base de datos antes de continuar.")
    print()
    
    respuesta = input("¿Desea continuar? (s/n): ")
    if respuesta.lower() != 's':
        print("Migración cancelada por el usuario.")
        sys.exit(0)
    
    exito = aplicar_migracion()
    sys.exit(0 if exito else 1)
