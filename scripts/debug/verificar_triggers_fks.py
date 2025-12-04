"""
Script para verificar triggers y foreign keys en la base de datos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database.database import get_db_connection

print("=" * 70)
print("VERIFICACIÓN DE TRIGGERS Y FOREIGN KEYS")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Buscar triggers
    cur.execute("""
        SELECT name, tbl_name, sql 
        FROM sqlite_master 
        WHERE type='trigger' 
        ORDER BY tbl_name, name
    """)
    triggers = cur.fetchall()
    
    print(f"\n📋 Triggers encontrados: {len(triggers)}")
    print("-" * 70)
    
    triggers_herramienta = []
    triggers_mantenimiento = []
    triggers_otros = []
    
    for nombre, tabla, sql in triggers:
        if 'herramienta' in nombre.lower() or 'herramienta' in tabla.lower():
            triggers_herramienta.append((nombre, tabla, sql))
        elif 'mantenimiento' in nombre.lower() or 'mantenimiento' in tabla.lower():
            triggers_mantenimiento.append((nombre, tabla, sql))
        else:
            triggers_otros.append((nombre, tabla, sql))
    
    if triggers_herramienta:
        print("\n🔧 Triggers relacionados con HERRAMIENTA:")
        for nombre, tabla, sql in triggers_herramienta:
            print(f"\n  • {nombre} (tabla: {tabla})")
            if 'herramienta_old' in sql:
                print("    ⚠️  REFERENCIA A herramienta_old ENCONTRADA")
                print(f"    SQL: {sql[:200]}...")
            else:
                print(f"    SQL: {sql[:100]}...")
    
    if triggers_mantenimiento:
        print("\n🔧 Triggers relacionados con MANTENIMIENTO:")
        for nombre, tabla, sql in triggers_mantenimiento:
            print(f"\n  • {nombre} (tabla: {tabla})")
            if 'herramienta_old' in sql:
                print("    ⚠️  REFERENCIA A herramienta_old ENCONTRADA")
                print(f"    SQL: {sql[:200]}...")
            else:
                print(f"    SQL: {sql[:100]}...")
    
    # Buscar foreign keys
    print("\n" + "=" * 70)
    print("FOREIGN KEYS EN MANTENIMIENTO_HERRAMIENTA")
    print("=" * 70)
    
    cur.execute("PRAGMA foreign_key_list(mantenimiento_herramienta)")
    fks = cur.fetchall()
    
    if fks:
        print("\n✅ Foreign keys encontradas:")
        for fk in fks:
            print(f"  • Columna: {fk[3]} → Tabla: {fk[2]}")
            if fk[2] == 'herramienta_old':
                print("    ⚠️  ERROR: Apunta a herramienta_old (tabla inexistente)")
    else:
        print("\n⚠️  No hay foreign keys definidas")
    
    # Verificar el CREATE TABLE de mantenimiento_herramienta
    print("\n" + "=" * 70)
    print("CREATE TABLE DE mantenimiento_herramienta")
    print("=" * 70)
    
    cur.execute("""
        SELECT sql 
        FROM sqlite_master 
        WHERE type='table' AND name='mantenimiento_herramienta'
    """)
    create_sql = cur.fetchone()
    if create_sql:
        sql_text = create_sql[0]
        print(f"\n{sql_text}")
        
        if 'herramienta_old' in sql_text:
            print("\n⚠️  ERROR: La definición de la tabla contiene referencia a herramienta_old")
        else:
            print("\n✅ No hay referencias a herramienta_old en la definición")
    
    print("\n" + "=" * 70)
