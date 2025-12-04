"""Script para limpiar TODOS los datos de la base de datos.
USO (Windows CMD):
    python scripts\\purge_all_data.py

ADVERTENCIA: Esta acción eliminará TODOS LOS DATOS de todas las tablas.
- Se mantendrá la estructura (tablas, columnas, índices)
- Se eliminarán todos los registros
- NO HAY FORMA DE RECUPERAR LOS DATOS después de ejecutar este script

Acciones:
 1. Muestra conteo de registros en cada tabla
 2. Pide confirmación TRIPLE (escribe ELIMINAR TODO) antes de proceder
 3. Elimina todos los registros de todas las tablas de datos
 4. Respeta migration_history para mantener estado de migraciones
 5. Muestra resumen final

Recomendación: Haz un respaldo de la base de datos antes de ejecutar.
"""
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'fincafacil.db')

# Orden de eliminación (respetando foreign keys)
TABLES_TO_PURGE = [
    # Dependientes primero
    'pago_nomina',
    'movimiento_inventario',
    'detalle_venta',
    'entrada_producto',
    'salida_producto',
    'peso_leche',
    'produccion_leche',
    'tratamiento_animal',
    'registro_salud',
    'evento_reproductivo',
    'mantenimiento',
    'animal',
    'herramienta',
    'insumo',
    'producto_venta',
    'lote',
    'empleado',
    'potrero',
    'sector',
    'finca',
    'usuario',
    # No tocar: migration_history (mantener estado de migraciones)
]

def get_table_counts(cursor):
    """Obtiene conteo de registros por tabla"""
    counts = {}
    for table in TABLES_TO_PURGE:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            counts[table] = None  # Tabla no existe
    return counts

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encontró base de datos en: {DB_PATH}")
        return

    print("=" * 70)
    print("⚠️  PURGA TOTAL DE BASE DE DATOS ⚠️")
    print("=" * 70)
    print(f"→ Base de datos: {DB_PATH}")
    print()

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        
        # Mostrar conteos actuales
        print("📊 CONTEO ACTUAL DE REGISTROS:")
        print("-" * 70)
        counts = get_table_counts(cur)
        total_records = 0
        for table, count in counts.items():
            if count is not None and count > 0:
                print(f"  {table:30} {count:>6} registros")
                total_records += count
            elif count == 0:
                print(f"  {table:30}      0 registros (vacía)")
        
        print("-" * 70)
        print(f"  {'TOTAL':30} {total_records:>6} registros")
        print()

        if total_records == 0:
            print("✅ La base de datos ya está vacía. No hay nada que eliminar.")
            return

        # Confirmación triple
        print("⚠️  ADVERTENCIA: Esta acción es IRREVERSIBLE")
        print("⚠️  Se eliminarán TODOS los datos de la aplicación")
        print()
        
        confirm1 = input("¿Estás seguro? Escribe 'SI' para continuar: ").strip().upper()
        if confirm1 != 'SI':
            print("❌ Operación cancelada.")
            return

        confirm2 = input("¿Realmente deseas eliminar TODO? Escribe 'CONFIRMO': ").strip().upper()
        if confirm2 != 'CONFIRMO':
            print("❌ Operación cancelada.")
            return

        confirm3 = input("Última confirmación. Escribe 'ELIMINAR TODO': ").strip().upper()
        if confirm3 != 'ELIMINAR TODO':
            print("❌ Operación cancelada.")
            return

        print()
        print("🔥 Iniciando purga total...")
        print()

        # Deshabilitar foreign keys temporalmente para evitar conflictos
        cur.execute("PRAGMA foreign_keys = OFF")
        
        deleted_counts = {}
        for table in TABLES_TO_PURGE:
            if counts[table] is not None and counts[table] > 0:
                try:
                    cur.execute(f"DELETE FROM {table}")
                    deleted_counts[table] = counts[table]
                    print(f"  ✓ {table}: {counts[table]} registros eliminados")
                except Exception as e:
                    print(f"  ✗ {table}: Error - {e}")
        
        # Re-habilitar foreign keys
        cur.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()

        # Verificar resultado
        print()
        print("=" * 70)
        print("📊 VERIFICACIÓN FINAL:")
        print("-" * 70)
        final_counts = get_table_counts(cur)
        remaining = 0
        for table, count in final_counts.items():
            if count and count > 0:
                print(f"  ⚠️  {table}: {count} registros restantes")
                remaining += count
        
        if remaining == 0:
            print("  ✅ Todas las tablas están vacías")
        
        print("-" * 70)
        print()
        print(f"✅ Purga completada: {sum(deleted_counts.values())} registros eliminados")
        print()
        print("🔄 Ahora puedes empezar a registrar información nueva desde la aplicación.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error durante la purga: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
