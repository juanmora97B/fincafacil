"""Verificar potreros en la base de datos."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    print("=== TODOS LOS POTREROS ===\n")
    cursor.execute("""
        SELECT p.id, p.codigo, p.nombre, p.id_finca, p.id_sector, p.estado,
               f.nombre as finca_nombre, s.nombre as sector_nombre
        FROM potrero p
        LEFT JOIN finca f ON p.id_finca = f.id
        LEFT JOIN sector s ON p.id_sector = s.id
        ORDER BY p.id DESC
        LIMIT 20
    """)
    
    potreros = cursor.fetchall()
    
    if potreros:
        print(f"Total registros encontrados: {len(potreros)}\n")
        for p in potreros:
            print(f"ID: {p[0]}")
            print(f"  Código: {p[1]}")
            print(f"  Nombre: {p[2]}")
            print(f"  id_finca: {p[3]} → {p[6]}")
            print(f"  id_sector: {p[4]} → {p[7]}")
            print(f"  Estado: {p[5]}")
            print("-" * 50)
    else:
        print("No hay potreros en la base de datos")
    
    print("\n=== POTREROS ACTIVOS (los que muestra la app) ===\n")
    cursor.execute("""
        SELECT p.id, p.codigo, p.nombre, f.nombre as finca, s.nombre as sector
        FROM potrero p
        LEFT JOIN finca f ON p.id_finca = f.id
        LEFT JOIN sector s ON p.id_sector = s.id
        WHERE p.estado = 'Activo'
    """)
    
    activos = cursor.fetchall()
    
    if activos:
        print(f"Total activos: {len(activos)}\n")
        for p in activos:
            print(f"ID: {p[0]}, Código: {p[1]}, Nombre: {p[2]}, Finca: {p[3]}, Sector: {p[4]}")
    else:
        print("No hay potreros activos")
