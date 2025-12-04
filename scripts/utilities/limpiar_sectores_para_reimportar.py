"""Eliminar sectores actuales para poder reimportar con fincas correctas."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    print("=== SECTORES ACTUALES ===\n")
    cursor.execute("""
        SELECT s.codigo, s.nombre, f.nombre as finca
        FROM sector s
        LEFT JOIN finca f ON s.finca_id = f.id
        WHERE s.estado = 'Activo' OR s.estado = 'Activa'
        ORDER BY s.codigo
    """)
    
    for r in cursor.fetchall():
        print(f"  {r[0]} - {r[1]} → Finca: {r[2]}")
    
    print("\n¿Desea marcar todos estos sectores como Inactivos? (s/n): ", end="")
    respuesta = input().lower()
    
    if respuesta == 's':
        cursor.execute("""
            UPDATE sector 
            SET estado = 'Inactivo'
            WHERE estado = 'Activo' OR estado = 'Activa'
        """)
        
        filas_actualizadas = cursor.rowcount
        conn.commit()
        
        print(f"\n✓ {filas_actualizadas} sector(es) marcado(s) como Inactivo")
        print("\nAhora puedes importar el Excel con las fincas correctas para cada sector.")
    else:
        print("\nOperación cancelada.")
