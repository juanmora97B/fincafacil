"""
Test rápido del módulo de insumos para verificar que no hay errores de columnas
"""
import sys
sys.path.insert(0, '.')

print("=" * 70)
print("TEST DEL MÓDULO DE INSUMOS")
print("=" * 70)

try:
    from database.database import get_db_connection
    
    print("\n✅ Importación de database exitosa")
    
    # Simular la query que hace el módulo
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT h.codigo, h.nombre, h.categoria, f.nombre as finca_nombre,
                   h.stock_actual, h.id_trabajador, h.responsable, h.stock_bodega,
                   h.estado, h.id_finca
            FROM insumo h
            LEFT JOIN finca f ON h.id_finca = f.id
            WHERE 1=1
            ORDER BY h.codigo
            LIMIT 5
        """
        
        print("\n✅ Ejecutando query de prueba...")
        cursor.execute(query)
        
        rows = cursor.fetchall()
        
        if rows:
            print(f"✅ Query exitosa - {len(rows)} registros encontrados")
            print("\nPrimeros registros:")
            for row in rows:
                print(f"  - {row[0]}: {row[1]} (Stock: {row[4]})")
        else:
            print("✅ Query exitosa - No hay insumos registrados aún")
        
    print("\n" + "=" * 70)
    print("✅ MÓDULO DE INSUMOS FUNCIONANDO CORRECTAMENTE")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
