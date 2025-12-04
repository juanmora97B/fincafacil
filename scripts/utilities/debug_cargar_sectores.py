"""Script para verificar exactamente qué muestra la consulta de cargar_sectores."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

print("=== EJECUTANDO LA MISMA CONSULTA QUE USA cargar_sectores() ===\n")

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.id, f.nombre as finca, s.codigo, s.nombre, 
               COALESCE(s.comentario, s.descripcion, '') as comentario 
        FROM sector s
        LEFT JOIN finca f ON s.finca_id = f.id
        WHERE s.estado = 'Activo' OR s.estado = 'Activa'
    """)
    
    print("Resultados:")
    print("-" * 80)
    for fila in cursor.fetchall():
        print(f"ID: {fila[0]}")
        print(f"Finca: {fila[1]}")
        print(f"Código: {fila[2]}")
        print(f"Nombre: {fila[3]}")
        print(f"Comentario: {fila[4]}")
        print("-" * 80)
    
    print("\n=== VERIFICACIÓN DIRECTA DE SC001 ===\n")
    cursor.execute("""
        SELECT s.id, s.codigo, s.nombre, s.finca_id, f.id as finca_real_id, f.nombre as finca_nombre
        FROM sector s
        LEFT JOIN finca f ON s.finca_id = f.id
        WHERE s.codigo = 'SC001'
    """)
    
    resultado = cursor.fetchone()
    if resultado:
        print(f"Sector ID: {resultado[0]}")
        print(f"Código: {resultado[1]}")
        print(f"Nombre: {resultado[2]}")
        print(f"finca_id en sector: {resultado[3]}")
        print(f"finca ID real: {resultado[4]}")
        print(f"Nombre de finca: {resultado[5]}")
    
    print(f"\n=== RUTA DE LA BASE DE DATOS ===")
    cursor.execute("PRAGMA database_list")
    for db_info in cursor.fetchall():
        print(f"Database: {db_info[1]}, File: {db_info[2]}")
