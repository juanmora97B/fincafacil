import sqlite3

conn = sqlite3.connect('database/database.db')
cursor = conn.cursor()

print("=" * 80)
print("ESQUEMA DE LA TABLA 'insumo'")
print("=" * 80)

cursor.execute("PRAGMA table_info(insumo)")
columns = cursor.fetchall()

for col in columns:
    cid, name, dtype, notnull, default, pk = col
    print(f"{name:25s} | {dtype:15s} | PK={pk} | NotNull={notnull}")

print("\n" + "=" * 80)
print("CAMPOS NUMÉRICOS CRÍTICOS:")
print("=" * 80)

for col in columns:
    name, dtype = col[1], col[2]
    if name in ['precio_unitario', 'stock_minimo', 'stock_actual', 'stock_bodega']:
        print(f"  {name:25s} → {dtype:15s}")

conn.close()
