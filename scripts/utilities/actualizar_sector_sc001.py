"""Script para actualizar el sector SC001 con la finca correcta."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

print("=== ACTUALIZANDO SECTOR SC001 ===\n")

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Buscar finca "finca el prado" (case insensitive)
    cursor.execute("SELECT id, nombre FROM finca WHERE LOWER(nombre) = LOWER(?) AND estado = 'Activo'", ('Finca El Prado',))
    finca = cursor.fetchone()
    
    if finca:
        finca_id = finca[0]
        finca_nombre = finca[1]
        print(f"Finca encontrada: ID={finca_id}, Nombre={finca_nombre}")
        
        # Actualizar sector
        cursor.execute("UPDATE sector SET finca_id = ? WHERE codigo = ?", (finca_id, 'SC001'))
        conn.commit()
        
        print(f"\n✓ Sector SC001 actualizado con finca_id={finca_id}")
        
        # Verificar
        cursor.execute("""
            SELECT s.codigo, s.nombre, f.nombre as finca_nombre
            FROM sector s
            LEFT JOIN finca f ON s.finca_id = f.id
            WHERE s.codigo = ?
        """, ('SC001',))
        resultado = cursor.fetchone()
        
        print(f"\nVerificación:")
        print(f"  Código: {resultado[0]}")
        print(f"  Nombre: {resultado[1]}")
        print(f"  Finca: {resultado[2]}")
    else:
        print("No se encontró la finca")
