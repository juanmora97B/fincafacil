"""
Script para identificar triggers y FKs que referencian tablas legacy
"""
import sqlite3

conn = sqlite3.connect('database/fincafacil.db')
cur = conn.cursor()

print("\n=== TRIGGERS CON REFERENCIAS LEGACY ===")
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND (sql LIKE '%animal_legacy%' OR sql LIKE '%legacy%')")
triggers = cur.fetchall()
if triggers:
    for name, sql in triggers:
        print(f"\n🔴 Trigger: {name}")
        print(sql)
        print("-" * 80)
else:
    print("✅ No hay triggers con referencias legacy")

print("\n\n=== TABLAS LEGACY EXISTENTES ===")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%legacy%'")
tables = cur.fetchall()
if tables:
    for (table,) in tables:
        print(f"🔴 Tabla: {table}")
else:
    print("✅ No hay tablas legacy")

print("\n\n=== INDICES QUE REFERENCIAN LEGACY ===")
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND (sql LIKE '%legacy%' OR name LIKE '%legacy%')")
indices = cur.fetchall()
if indices:
    for name, sql in indices:
        print(f"🔴 Índice: {name}")
        print(f"   {sql}")
else:
    print("✅ No hay índices legacy")

print("\n\n=== VERIFICANDO FOREIGN KEYS EN TABLA ANIMAL ===")
cur.execute("PRAGMA foreign_key_list(animal)")
fks = cur.fetchall()
if fks:
    print("Foreign Keys de animal:")
    for fk in fks:
        print(f"  - id={fk[0]}, seq={fk[1]}, table={fk[2]}, from={fk[3]}, to={fk[4]}, on_update={fk[5]}, on_delete={fk[6]}")
else:
    print("✅ Tabla animal no tiene FKs definidas")

conn.close()
print("\n✅ Análisis completado")
