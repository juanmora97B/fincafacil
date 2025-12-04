import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'database/fincafacil.db'

def fmt(n):
    return n if n is not None else 'N/A'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("="*100)
print("AUDITORIA DE IMPORTACIÓN DE ANIMALES")
print("="*100)

# Totales actuales
cur.execute("SELECT COUNT(*) FROM animal")
total = cur.fetchone()[0]
print(f"Total animales en BD: {total}")

# Animales por estado
cur.execute("SELECT estado, COUNT(*) FROM animal GROUP BY estado")
estados = cur.fetchall()
print("Estados:")
for estado, cnt in estados:
    print(f"  - {fmt(estado)}: {cnt}")

# Por finca
cur.execute("""
SELECT f.nombre, COUNT(a.id)
FROM animal a
LEFT JOIN finca f ON f.id = a.id_finca
GROUP BY f.id
ORDER BY COUNT(a.id) DESC
""")
print("\nPor finca:")
for nombre, cnt in cur.fetchall():
    print(f"  - {fmt(nombre)}: {cnt}")

# Animales con problemas de asignación
cur.execute("SELECT COUNT(*) FROM animal WHERE id_finca IS NULL")
sin_finca = cur.fetchone()[0]
print(f"\nAnimales SIN finca asignada: {sin_finca}")
if sin_finca:
    cur.execute("SELECT id, codigo, nombre, sexo, raza_id, estado FROM animal WHERE id_finca IS NULL ORDER BY id DESC LIMIT 20")
    rows = cur.fetchall()
    print("  Últimos 20 sin finca:")
    for r in rows:
        print("   ", r)

# Duplicados por codigo (muestra códigos repetidos)
cur.execute("""
SELECT codigo, COUNT(*) c
FROM animal
GROUP BY codigo
HAVING c > 1
ORDER BY c DESC
""")
id_dups = cur.fetchall()
print(f"\nCódigos de animales duplicados: {len(id_dups)}")
for codigo, c in id_dups:
    print(f"  - {codigo}: {c} veces")

# Últimos importados (muestra los 20 más recientes)
cur.execute("""
SELECT id, codigo, nombre, sexo, raza_id, id_finca, estado, fecha_creacion
FROM animal
ORDER BY id DESC
LIMIT 20
""")
rows = cur.fetchall()
print("\nÚltimos 20 registros de animales:")
for r in rows:
    print("  ", r)

# Verificación de mapeos sensibles a mayúsculas en raza/finca
print("\nVerificación de mapeo case-insensitive (existencias en catálogo):")
cur.execute("SELECT LOWER(TRIM(nombre)) FROM raza")
razas_norm = set(x[0] for x in cur.fetchall())
cur.execute("SELECT LOWER(TRIM(nombre)) FROM finca")
fincas_norm = set(x[0] for x in cur.fetchall())
print(f"  Razas en catálogo (normalizadas): {len(razas_norm)}")
print(f"  Fincas en catálogo (normalizadas): {len(fincas_norm)}")

# Animales con raza_id sin referencia válida
cur.execute("""
SELECT COUNT(*) FROM animal a
LEFT JOIN raza r ON r.id = a.raza_id
WHERE a.raza_id IS NOT NULL AND r.id IS NULL
""")
no_cat_raza = cur.fetchone()[0]
print(f"\nAnimales con raza_id sin referencia en catálogo: {no_cat_raza}")

# Animales con finca no encontrada (si se guarda nombre de finca aparte)
# Generalmente es por id_finca NULL, ya contado arriba.

print("\nSugerencias automáticas:")
if sin_finca:
    print("  - Hay animales sin finca: revisar mapeo de finca en importación y usar búsqueda case-insensitive.")
if id_dups:
    print("  - Hay códigos duplicados: la importación pudo saltar filas por UNIQUE (animal.codigo).")
if no_cat_raza:
    print("  - Hay razas no catalogadas: agregar al catálogo o normalizar nombres en el Excel.")
if total == 0:
    print("  - No hay animales: verificar que se está usando database/fincafacil.db y no otra BD.")

conn.close()
