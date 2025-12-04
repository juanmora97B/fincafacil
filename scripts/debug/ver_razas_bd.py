"""
Verificar razas en la base de datos
"""
from database.database import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("RAZAS EN LA BASE DE DATOS")
    print("="*70)
    
    cursor.execute("SELECT id, nombre, estado FROM raza ORDER BY nombre")
    razas = cursor.fetchall()
    
    print(f"\nTotal de razas: {len(razas)}")
    print("\nLista completa:")
    for i, (id_raza, nombre, estado) in enumerate(razas, 1):
        print(f"{i:3d}. ID: {id_raza:3d} | {nombre:35s} | {estado}")
    
    print("\n" + "="*70)
    print("RAZAS ACTIVAS (las que deberían aparecer en el combo)")
    print("="*70)
    
    cursor.execute("SELECT id, nombre FROM raza WHERE estado NOT IN ('Inactiva', 'inactiva', 'Eliminada', 'eliminada') ORDER BY nombre")
    razas_activas = cursor.fetchall()
    
    print(f"\nTotal: {len(razas_activas)}")
    for i, (id_raza, nombre) in enumerate(razas_activas, 1):
        print(f"{i:3d}. {nombre}")
