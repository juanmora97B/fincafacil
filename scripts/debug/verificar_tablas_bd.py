"""
Script para verificar el estado de tablas en la base de datos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database.database import get_db_connection

print("=" * 70)
print("VERIFICACIÓN DE TABLAS EN BASE DE DATOS")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Listar todas las tablas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tablas = [row[0] for row in cur.fetchall()]
    
    print(f"\n📊 Total de tablas: {len(tablas)}")
    print("-" * 70)
    
    # Buscar tablas temporales (_old, _new)
    tablas_temp = []
    tablas_normales = []
    
    for tabla in tablas:
        if '_old' in tabla or '_new' in tabla:
            tablas_temp.append(tabla)
        else:
            tablas_normales.append(tabla)
    
    print("\n✅ Tablas principales:")
    for t in sorted(tablas_normales):
        if 'herramienta' in t.lower() or 'mantenimiento' in t.lower():
            print(f"  • {t} ⭐")
        else:
            print(f"  • {t}")
    
    if tablas_temp:
        print("\n⚠️  Tablas temporales encontradas:")
        for t in sorted(tablas_temp):
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            count = cur.fetchone()[0]
            print(f"  • {t} ({count} registros)")
    else:
        print("\n✅ No hay tablas temporales")
    
    # Verificar tabla herramienta específicamente
    print("\n" + "=" * 70)
    print("TABLA HERRAMIENTA")
    print("=" * 70)
    
    if 'herramienta' in tablas:
        cur.execute("PRAGMA table_info(herramienta)")
        columnas = cur.fetchall()
        print(f"\n✅ Tabla 'herramienta' existe con {len(columnas)} columnas")
        
        cur.execute("SELECT COUNT(*) FROM herramienta")
        count = cur.fetchone()[0]
        print(f"   Registros: {count}")
    
    if 'herramienta_old' in tablas:
        print("\n⚠️  Tabla 'herramienta_old' existe (debería eliminarse)")
        cur.execute("SELECT COUNT(*) FROM herramienta_old")
        count = cur.fetchone()[0]
        print(f"   Registros: {count}")
    else:
        print("\n✅ Tabla 'herramienta_old' NO existe (correcto)")
    
    # Verificar tabla de mantenimiento
    print("\n" + "=" * 70)
    print("TABLA MANTENIMIENTO")
    print("=" * 70)
    
    if 'mantenimiento_herramienta' in tablas:
        cur.execute("PRAGMA table_info(mantenimiento_herramienta)")
        columnas = cur.fetchall()
        print(f"\n✅ Tabla 'mantenimiento_herramienta' existe con {len(columnas)} columnas:")
        for col in columnas:
            print(f"   • {col[1]} ({col[2]})")
        
        cur.execute("SELECT COUNT(*) FROM mantenimiento_herramienta")
        count = cur.fetchone()[0]
        print(f"\n   Total registros: {count}")
    else:
        print("\n❌ Tabla 'mantenimiento_herramienta' NO existe")
    
    print("\n" + "=" * 70)
