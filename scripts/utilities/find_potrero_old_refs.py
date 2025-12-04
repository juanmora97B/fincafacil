"""
Buscar todas las referencias a potrero_old en foreign keys
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
    
    print("Buscando referencias a potrero_old...\n")
    found = False
    
    for table in tables:
        cur.execute(f"PRAGMA foreign_key_list({table})")
        fks = cur.fetchall()
        
        for fk in fks:
            if fk[2] == 'potrero_old':
                print(f"❌ {table}.{fk[3]} -> potrero_old({fk[4]})")
                found = True
    
    if not found:
        print("✔ No se encontraron referencias a potrero_old")
