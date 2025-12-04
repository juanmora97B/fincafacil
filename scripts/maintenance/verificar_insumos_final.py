"""
Script para verificar que el módulo de insumos se carga correctamente
"""
import sys
sys.path.insert(0, '.')

print("=" * 70)
print("VERIFICACION FINAL DEL MODULO DE INSUMOS")
print("=" * 70)

try:
    # Limpiar cualquier importación previa
    if 'modules.insumos' in sys.modules:
        del sys.modules['modules.insumos']
    if 'modules.insumos.insumos_main' in sys.modules:
        del sys.modules['modules.insumos.insumos_main']
    
    print("\n1. Importando modulo de insumos...")
    from modules.insumos import InsumosModule
    print("   OK - Modulo importado correctamente")
    
    print("\n2. Verificando que la clase existe...")
    print(f"   OK - Clase: {InsumosModule.__name__}")
    
    print("\n3. Probando query SQL...")
    from database.database import get_db_connection
    
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
        
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"   OK - Query ejecutada sin errores ({len(rows)} registros)")
    
    print("\n" + "=" * 70)
    print("VERIFICACION EXITOSA")
    print("=" * 70)
    print("\nEl modulo de insumos esta listo para usar.")
    print("Puedes ejecutar 'python main.py' y acceder al modulo Insumos.")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
