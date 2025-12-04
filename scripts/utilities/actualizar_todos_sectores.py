"""Actualizar todos los sectores activos con la finca 'finca el prado'."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Buscar la finca
    cursor.execute("SELECT id, nombre FROM finca WHERE LOWER(nombre) LIKE '%prado%' AND estado = 'Activo'")
    finca = cursor.fetchone()
    
    if not finca:
        print("❌ No se encontró la finca 'finca el prado'")
        exit(1)
    
    finca_id = finca[0]
    finca_nombre = finca[1]
    
    print(f"Finca encontrada: ID={finca_id}, Nombre='{finca_nombre}'")
    print("\n=== ACTUALIZANDO TODOS LOS SECTORES ACTIVOS ===\n")
    
    # Actualizar TODOS los sectores activos
    cursor.execute("""
        UPDATE sector 
        SET finca_id = ? 
        WHERE (estado = 'Activo' OR estado = 'Activa')
    """, (finca_id,))
    
    filas_actualizadas = cursor.rowcount
    conn.commit()
    
    print(f"✓ {filas_actualizadas} sector(es) actualizado(s) con finca_id={finca_id}")
    
    # Verificar resultado
    print("\n=== SECTORES ACTUALIZADOS ===\n")
    cursor.execute("""
        SELECT s.codigo, s.nombre, f.nombre as finca
        FROM sector s
        LEFT JOIN finca f ON s.finca_id = f.id
        WHERE s.estado = 'Activo' OR s.estado = 'Activa'
        ORDER BY s.codigo
    """)
    
    for r in cursor.fetchall():
        print(f"  {r[0]} - {r[1]} → Finca: {r[2]}")
