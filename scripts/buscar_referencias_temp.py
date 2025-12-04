import sqlite3
c = sqlite3.connect('database/fincafacil.db')
cur = c.cursor()
cur.execute("SELECT type, name, sql FROM sqlite_master WHERE sql LIKE '%animal_legacy_temp%'")
r = cur.fetchall()
print('\nReferencias a animal_legacy_temp:')
if r:
    for tipo, nombre, sql in r:
        print(f'\n{tipo.upper()}: {nombre}')
        print(sql)
        print('-' * 80)
else:
    print('✓ No hay referencias a animal_legacy_temp')

# Verificar si la tabla existe
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animal_legacy_temp'")
if cur.fetchone():
    print('\n⚠️ La tabla animal_legacy_temp EXISTE')
else:
    print('\n✓ La tabla animal_legacy_temp NO existe (correctamente eliminada)')

c.close()
