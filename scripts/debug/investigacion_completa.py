"""
Investigación completa del problema de ComboBox
"""
from database.database import get_db_connection
import sqlite3

print("\n" + "="*80)
print("INVESTIGACIÓN COMPLETA - COMBOBOX FINCAS Y RAZAS")
print("="*80)

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # 1. Verificar tabla raza
    print("\n1️⃣ ESTRUCTURA TABLA RAZA")
    print("-"*80)
    cursor.execute("PRAGMA table_info(raza)")
    cols = cursor.fetchall()
    print("Columnas:", [col[1] for col in cols])
    
    # 2. Todas las razas
    print("\n2️⃣ TODAS LAS RAZAS EN BASE DE DATOS")
    print("-"*80)
    cursor.execute("SELECT id, nombre, estado FROM raza ORDER BY id")
    razas = cursor.fetchall()
    print(f"Total: {len(razas)} razas")
    for i, (id_raza, nombre, estado) in enumerate(razas, 1):
        print(f"{i:2d}. ID:{id_raza:3d} | {nombre:35s} | Estado: {estado}")
    
    # 3. Verificar tabla finca
    print("\n3️⃣ TODAS LAS FINCAS EN BASE DE DATOS")
    print("-"*80)
    cursor.execute("SELECT id, nombre, estado FROM finca ORDER BY id")
    fincas = cursor.fetchall()
    print(f"Total: {len(fincas)} fincas")
    for id_finca, nombre, estado in fincas:
        print(f"ID:{id_finca:3d} | {nombre:35s} | Estado: {estado}")
    
    # 4. Verificar si hay animales con razas compuestas
    print("\n4️⃣ ANIMALES CON CAMPO 'raza' (no raza_id)")
    print("-"*80)
    cursor.execute("PRAGMA table_info(animal)")
    animal_cols = [col[1] for col in cursor.fetchall()]
    print("Columnas de tabla animal:", animal_cols)
    
    if 'raza' in animal_cols:
        print("\n⚠️ La tabla animal tiene columna 'raza' (texto libre)")
        cursor.execute("SELECT id, codigo, raza FROM animal WHERE raza IS NOT NULL LIMIT 10")
        animales_raza = cursor.fetchall()
        print(f"Primeros 10 animales con campo 'raza':")
        for id_animal, codigo, raza in animales_raza:
            print(f"  Animal {codigo}: raza='{raza}'")
    
    if 'raza_id' in animal_cols:
        print("\n✅ La tabla animal tiene columna 'raza_id' (FK a tabla raza)")
        cursor.execute("""
            SELECT a.id, a.codigo, r.nombre 
            FROM animal a 
            LEFT JOIN raza r ON a.raza_id = r.id 
            WHERE a.raza_id IS NOT NULL 
            LIMIT 10
        """)
        animales_raza_id = cursor.fetchall()
        print(f"Primeros 10 animales con raza_id:")
        for id_animal, codigo, raza_nombre in animales_raza_id:
            print(f"  Animal {codigo}: raza='{raza_nombre}'")
    
    # 5. Verificar configuración de app
    print("\n5️⃣ CONFIGURACIÓN DE APLICACIÓN")
    print("-"*80)
    cursor.execute("SELECT clave, valor FROM app_settings")
    settings = cursor.fetchall()
    for clave, valor in settings:
        print(f"  {clave}: {valor}")

print("\n" + "="*80)
print("INVESTIGACIÓN COMPLETADA")
print("="*80)
