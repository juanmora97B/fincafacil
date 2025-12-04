"""Eliminar TODOS los sectores para poder reimportar con finca correcta."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    print("=== ELIMINANDO TODOS LOS SECTORES ===\n")
    
    cursor.execute("SELECT COUNT(*) FROM sector")
    total = cursor.fetchone()[0]
    
    print(f"Total de sectores en la BD: {total}")
    
    if total > 0:
        cursor.execute("DELETE FROM sector")
        filas_eliminadas = cursor.rowcount
        conn.commit()
        
        print(f"✓ {filas_eliminadas} sector(es) eliminado(s)")
        print("\nAhora reimporta el Excel con el importador corregido.")
    else:
        print("No hay sectores para eliminar.")
