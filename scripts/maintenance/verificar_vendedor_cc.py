import sqlite3

conn = sqlite3.connect('database/fincafacil.db')
cursor = conn.cursor()

print("ESTRUCTURA DE TABLA: vendedor")
print("-" * 60)
cursor.execute("PRAGMA table_info(vendedor)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\n" + "=" * 60)
print("ESTRUCTURA DE TABLA: condicion_corporal")
print("-" * 60)
cursor.execute("PRAGMA table_info(condicion_corporal)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
