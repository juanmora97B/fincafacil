import sqlite3

conn = sqlite3.connect('database/fincafacil.db')
cursor = conn.cursor()

print("=" * 80)
print("TABLAS EN LA BASE DE DATOS")
print("=" * 80)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

for table in tables:
    print(f"  - {table[0]}")

# Buscar tablas que contengan 'insumo'
print("\n" + "=" * 80)
print("TABLAS RELACIONADAS CON INSUMOS:")
print("=" * 80)

insumo_tables = [t[0] for t in tables if 'insumo' in t[0].lower()]
for table in insumo_tables:
    print(f"\n▶ {table}")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        name, dtype = col[1], col[2]
        print(f"    {name:25s} → {dtype:15s}")

conn.close()
