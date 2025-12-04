"""
Buscar TODAS las referencias a tablas *_old en foreign keys
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database import get_connection

with get_connection() as conn:
    cur = conn.cursor()
    
    # Obtener todas las tablas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cur.fetchall()]
    
    print("=" * 60)
    print("BÚSQUEDA DE REFERENCIAS A TABLAS *_old")
    print("=" * 60)
    
    found = []
    
    for table in tables:
        cur.execute(f"PRAGMA foreign_key_list({table})")
        fks = cur.fetchall()
        
        for fk in fks:
            if fk[2].endswith('_old'):
                found.append({'table': table, 'column': fk[3], 'references': fk[2]})
                print(f"❌ {table}.{fk[3]} -> {fk[2]}({fk[4]})")
    
    print("\n" + "=" * 60)
    
    if found:
        print(f"❌ ENCONTRADAS {len(found)} REFERENCIAS A TABLAS *_old")
        print("\nREQUIERE CORRECCIÓN INMEDIATA")
    else:
        print("✔ NO SE ENCONTRARON REFERENCIAS A TABLAS *_old")
        print("✔ Base de datos limpia y lista para operaciones")
    
    print("=" * 60)
