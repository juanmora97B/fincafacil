import sqlite3
from pathlib import Path

DB = Path('database/fincafacil.db')
if not DB.exists():
    print('ERROR: database/fincafacil.db not found')
    exit(1)

conn = sqlite3.connect(str(DB))
c = conn.cursor()

def print_table_info(table):
    print('\n-----', table, '-----')
    try:
        c.execute(f"PRAGMA table_info({table})")
        cols = c.fetchall()
        if not cols:
            print('  (no existe o no tiene columnas)')
            return
        for col in cols:
            print('  ', col)
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        print('  filas:', count)
        c.execute(f"SELECT * FROM {table} LIMIT 5")
        rows = c.fetchall()
        for r in rows:
            print('   ', r)
    except Exception as e:
        print('  ERROR leyendo', table, e)

print_table_info('vendedores')
print_table_info('vendedor')

# Mostrar claves primarias o índices
print('\n----- índices -----')
for t in ('vendedores','vendedor'):
    try:
        c.execute(f"PRAGMA index_list({t})")
        print('\nindex_list', t, c.fetchall())
    except Exception as e:
        print(' index_list error', t, e)

conn.close()
