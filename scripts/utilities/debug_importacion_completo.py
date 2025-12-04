"""Debug completo del proceso de importación de sectores."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db
from modules.utils.importador_excel import importar_sector_desde_excel

print("=== 1. VERIFICAR FINCAS DISPONIBLES ===\n")
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, codigo, nombre, estado FROM finca ORDER BY id")
    fincas = cursor.fetchall()
    
    for f in fincas:
        print(f"ID:{f[0]}, Código:{f[1]}, Nombre:'{f[2]}', Estado:{f[3]}")

print("\n=== 2. PROBAR BÚSQUEDA DE 'finca el prado' ===\n")
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    test_nombre = "finca el prado"
    print(f"Buscando: '{test_nombre}'")
    
    cursor.execute("SELECT id, nombre FROM finca WHERE LOWER(nombre) = LOWER(?) AND estado = 'Activo'", (test_nombre,))
    resultado = cursor.fetchone()
    
    if resultado:
        print(f"✓ Encontrada: ID={resultado[0]}, Nombre='{resultado[1]}'")
    else:
        print("✗ No encontrada con búsqueda exacta")
        
        # Intentar con LIKE
        cursor.execute("SELECT id, nombre FROM finca WHERE LOWER(nombre) LIKE LOWER(?) AND estado = 'Activo'", (f"%{test_nombre}%",))
        similares = cursor.fetchall()
        if similares:
            print("\nFincas similares encontradas:")
            for s in similares:
                print(f"  ID={s[0]}, Nombre='{s[1]}'")

print("\n=== 3. SIMULAR IMPORTACIÓN DE UN SECTOR ===\n")

# Simular lo que hace el importador
test_finca_nombre = "finca el prado"
print(f"Simulando búsqueda para: '{test_finca_nombre}'")

from database import get_connection

finca_id = None
try:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM finca WHERE LOWER(nombre) = LOWER(?) AND estado = 'Activo' LIMIT 1", (test_finca_nombre,))
        finca_row = cursor.fetchone()
        if finca_row:
            finca_id = finca_row[0]
            print(f"✓ finca_id obtenido: {finca_id}")
        else:
            print("✗ No se obtuvo finca_id")
except Exception as e:
    print(f"✗ Error: {e}")

print(f"\nResultado final: finca_id = {finca_id}")

print("\n=== 4. VERIFICAR ESTRUCTURA TABLA SECTOR ===\n")
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(sector)")
    columnas = cursor.fetchall()
    
    print("Columnas de la tabla 'sector':")
    for col in columnas:
        print(f"  {col[1]} ({col[2]})")
