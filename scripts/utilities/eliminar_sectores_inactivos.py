"""Eliminar completamente los sectores inactivos."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    print("=== SECTORES INACTIVOS ===\n")
    cursor.execute("""
        SELECT id, codigo, nombre
        FROM sector
        WHERE estado = 'Inactivo'
        ORDER BY codigo
    """)
    
    inactivos = cursor.fetchall()
    
    if inactivos:
        for r in inactivos:
            print(f"  ID:{r[0]} - {r[1]} - {r[2]}")
        
        print(f"\nTotal: {len(inactivos)} sectores inactivos")
        print("\nEliminando sectores inactivos...")
        
        cursor.execute("DELETE FROM sector WHERE estado = 'Inactivo'")
        
        filas_eliminadas = cursor.rowcount
        conn.commit()
        
        print(f"✓ {filas_eliminadas} sector(es) eliminado(s)")
        print("\nAhora puedes importar el Excel sin problemas de duplicados.")
    else:
        print("No hay sectores inactivos para eliminar.")
