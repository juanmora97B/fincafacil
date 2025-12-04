"""Script para verificar si el sector tiene finca_id asignado."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

print("=== VERIFICACIÓN DE SECTOR SC001 ===\n")

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Verificar sector
    cursor.execute("SELECT id, codigo, nombre, finca_id FROM sector WHERE codigo = ?", ('SC001',))
    sector = cursor.fetchone()
    
    if sector:
        print(f"Sector encontrado:")
        print(f"  ID: {sector[0]}")
        print(f"  Código: {sector[1]}")
        print(f"  Nombre: {sector[2]}")
        print(f"  finca_id: {sector[3]}")
    else:
        print("No se encontró el sector SC001")
    
    print("\n=== FINCAS DISPONIBLES ===\n")
    cursor.execute("SELECT id, codigo, nombre FROM finca WHERE estado = 'Activo'")
    fincas = cursor.fetchall()
    
    for finca in fincas:
        print(f"ID: {finca[0]}, Código: {finca[1]}, Nombre: {finca[2]}")
    
    print("\n=== BÚSQUEDA DE 'Finca El Prado' ===\n")
    cursor.execute("SELECT id FROM finca WHERE nombre = ? AND estado = 'Activo'", ('Finca El Prado',))
    finca_prado = cursor.fetchone()
    
    if finca_prado:
        print(f"Finca encontrada con ID: {finca_prado[0]}")
    else:
        print("No se encontró una finca con nombre 'Finca El Prado'")
        print("\nIntentando búsqueda con LIKE...")
        cursor.execute("SELECT id, nombre FROM finca WHERE nombre LIKE '%prado%' AND estado = 'Activo'")
        similares = cursor.fetchall()
        if similares:
            print("Fincas similares encontradas:")
            for f in similares:
                print(f"  ID: {f[0]}, Nombre: {f[1]}")
