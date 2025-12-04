import sqlite3

conn = sqlite3.connect('database/fincafacil.db')
cursor = conn.cursor()

# Listar todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("TABLAS EN LA BASE DE DATOS:")
print("-" * 40)
for table in tables:
    print(f"  {table[0]}")

print(f"\nTotal: {len(tables)} tablas")

# Verificar si existe procedencia
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='procedencia'")
if cursor.fetchone():
    print("\nLa tabla 'procedencia' EXISTE")
    cursor.execute("PRAGMA table_info(procedencia)")
    columns = cursor.fetchall()
    print("Columnas:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("\nLa tabla 'procedencia' NO EXISTE")

conn.close()
