"""Ver todos los sectores y actualizar SC001 activo."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    print("=== TODOS LOS SECTORES ===\n")
    cursor.execute('SELECT id, codigo, nombre, finca_id, estado FROM sector ORDER BY id')
    
    for s in cursor.fetchall():
        print(f"ID:{s[0]}, Código:{s[1]}, Nombre:{s[2]}, finca_id:{s[3]}, Estado:{s[4]}")
    
    print("\n=== BUSCANDO FINCA 'finca el prado' ===\n")
    cursor.execute("SELECT id, nombre FROM finca WHERE LOWER(nombre) LIKE '%prado%' AND estado = 'Activo'")
    finca = cursor.fetchone()
    
    if finca:
        finca_id = finca[0]
        print(f"Finca encontrada: ID={finca_id}, Nombre={finca[1]}")
        
        print("\n=== ACTUALIZANDO SECTOR SC001 ACTIVO ===\n")
        cursor.execute("""
            UPDATE sector 
            SET finca_id = ? 
            WHERE codigo = 'SC001' AND (estado = 'Activo' OR estado = 'Activa')
        """, (finca_id,))
        
        filas_actualizadas = cursor.rowcount
        conn.commit()
        
        print(f"✓ {filas_actualizadas} sector(es) actualizado(s)")
        
        # Verificar
        cursor.execute("""
            SELECT s.id, s.codigo, s.nombre, f.nombre as finca
            FROM sector s
            LEFT JOIN finca f ON s.finca_id = f.id
            WHERE s.codigo = 'SC001' AND (s.estado = 'Activo' OR s.estado = 'Activa')
        """)
        
        print("\nSector actualizado:")
        for r in cursor.fetchall():
            print(f"  ID:{r[0]}, Código:{r[1]}, Nombre:{r[2]}, Finca:{r[3]}")
    else:
        print("No se encontró la finca")
