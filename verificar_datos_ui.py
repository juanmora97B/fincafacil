import sqlite3

conn = sqlite3.connect('database/fincafacil.db')
cursor = conn.cursor()

print("=" * 80)
print("VERIFICACIÓN DE DATOS CARGADOS")
print("=" * 80)

# Verificar fincas
cursor.execute("SELECT id, nombre, estado FROM finca")
fincas = cursor.fetchall()
print(f"\n🏢 FINCAS TOTALES EN BD: {len(fincas)}")
for f in fincas:
    print(f"   ID: {f[0]:3d} | Nombre: {f[1]:30s} | Estado: {f[2]}")

# Filtrar según criterio del código
excluir = {'eliminada', 'eliminado', 'inactiva', 'inactivo'}
fincas_activas = [f for f in fincas if (f[2] or '').lower() not in excluir]
print(f"\n✅ FINCAS QUE DEBERÍAN MOSTRARSE: {len(fincas_activas)}")
for f in fincas_activas:
    print(f"   - {f[1]}")

# Verificar razas
cursor.execute("SELECT id, nombre, estado FROM raza")
razas = cursor.fetchall()
print(f"\n🐄 RAZAS TOTALES EN BD: {len(razas)}")

# Filtrar según criterio del código
razas_activas = [r for r in razas if (r[2] or '').lower() not in ('inactiva', 'eliminada')]
print(f"\n✅ RAZAS QUE DEBERÍAN MOSTRARSE: {len(razas_activas)}")
for i, r in enumerate(razas_activas[:15], 1):
    print(f"   {i:2d}. {r[1]}")
if len(razas_activas) > 15:
    print(f"   ... y {len(razas_activas) - 15} más")

conn.close()
