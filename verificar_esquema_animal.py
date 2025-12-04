import sqlite3

conn = sqlite3.connect('database/fincafacil.db')
cursor = conn.cursor()

print("=" * 80)
print("ESQUEMA DE LA TABLA 'animal'")
print("=" * 80)

cursor.execute("PRAGMA table_info(animal)")
columns = cursor.fetchall()

for col in columns:
    cid, name, dtype, notnull, default, pk = col
    print(f"{name:25s} | {dtype:15s} | PK={pk} | NotNull={notnull}")

print("\n" + "=" * 80)
print("COLUMNAS RELACIONADAS CON UBICACIÓN:")
print("=" * 80)

ubicacion_cols = ['id_finca', 'id_potrero', 'id_lote', 'lote_id', 'id_sector', 'sector_id', 'id_grupo', 'grupo_id']
for col in columns:
    name = col[1]
    if any(term in name.lower() for term in ['finca', 'potrero', 'lote', 'sector', 'grupo']):
        print(f"  {name:25s} → {col[2]:15s}")

conn.close()
