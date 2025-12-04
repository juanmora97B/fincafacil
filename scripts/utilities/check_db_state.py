import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database.database import get_db_connection

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Listar todas las tablas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    print("Tablas actuales:")
    for t in sorted(tables):
        print(f"  - {t}")
    
    # Verificar si existen tablas _old
    old_tables = [t for t in tables if t.endswith('_old')]
    if old_tables:
        print(f"\n⚠ Tablas temporales encontradas: {old_tables}")
    else:
        print("\n✔ No hay tablas temporales")
    
    # Verificar estructura de animal y potrero
    for table in ['animal', 'potrero']:
        if table in tables:
            cur.execute(f"PRAGMA foreign_key_list({table})")
            fks = cur.fetchall()
            print(f"\n{table} - Foreign Keys:")
            for fk in fks:
                print(f"  {fk[3]} -> {fk[2]}({fk[4]}) ON DELETE {fk[6] if len(fk) > 6 else 'NO ACTION'}")
