"""Script para verificar estado final de las migraciones"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import get_db_connection

print("=" * 70)
print("VERIFICACIÓN FINAL DE MIGRACIONES")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Verificar mantenimiento_herramienta
    print("\n1. Tabla mantenimiento_herramienta:")
    print("-" * 70)
    cur.execute('PRAGMA table_info(mantenimiento_herramienta)')
    cols_mant = [col[1] for col in cur.fetchall()]
    
    tiene_017 = all(c in cols_mant for c in ['estado_actual', 'estado_previo_herramienta', 'fecha_completado'])
    
    if tiene_017:
        print("✅ Migración 017 APLICADA")
        print("   • estado_actual ✓")
        print("   • estado_previo_herramienta ✓")
        print("   • fecha_completado ✓")
    else:
        print("❌ Migración 017 FALTANTE")
        if 'estado_actual' not in cols_mant:
            print("   • estado_actual ✗")
        if 'estado_previo_herramienta' not in cols_mant:
            print("   • estado_previo_herramienta ✗")
        if 'fecha_completado' not in cols_mant:
            print("   • fecha_completado ✗")
    
    # Verificar herramienta
    print("\n2. Tabla herramienta:")
    print("-" * 70)
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='herramienta'")
    create_sql = cur.fetchone()[0]
    
    tiene_018 = 'En Revisión' in create_sql
    
    if tiene_018:
        print("✅ Migración 018 APLICADA")
        print("   • Estado 'En Revisión' disponible en CHECK constraint ✓")
    else:
        print("⚠️  Migración 018 PENDIENTE")
        print("   • Estado 'En Revisión' NO está en CHECK constraint")
    
    # Verificar tablas temporales
    print("\n3. Limpieza:")
    print("-" * 70)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_new' OR name LIKE '%_old'")
    temp_tables = cur.fetchall()
    
    if temp_tables:
        print("⚠️  Tablas temporales encontradas:")
        for (t,) in temp_tables:
            print(f"   • {t}")
    else:
        print("✅ No hay tablas temporales")
    
    # Contar registros
    print("\n4. Datos:")
    print("-" * 70)
    cur.execute("SELECT COUNT(*) FROM herramienta")
    cant_herr = cur.fetchone()[0]
    print(f"   • Herramientas: {cant_herr}")
    
    cur.execute("SELECT COUNT(*) FROM mantenimiento_herramienta")
    cant_mant = cur.fetchone()[0]
    print(f"   • Mantenimientos: {cant_mant}")
    
    if tiene_017:
        cur.execute("SELECT estado_actual, COUNT(*) FROM mantenimiento_herramienta GROUP BY estado_actual")
        estados_mant = cur.fetchall()
        print("   • Estados mantenimiento:")
        for estado, cant in estados_mant:
            print(f"     - {estado or 'NULL'}: {cant}")
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    
    if tiene_017 and tiene_018:
        print("✅ TODAS LAS MIGRACIONES APLICADAS CORRECTAMENTE")
        print("\nEl módulo de mantenimiento ahora tiene:")
        print("  • Seguimiento de estado de mantenimientos (Activo/Completado)")
        print("  • Restauración automática del estado de herramientas")
        print("  • Estado 'En Revisión' disponible para herramientas")
        print("  • Ocultación de mantenimientos completados del historial")
    elif tiene_017 and not tiene_018:
        print("⚠️  Migración 017: ✅ | Migración 018: ⚠️  PENDIENTE")
        print("\nFuncionalidad disponible:")
        print("  ✓ Seguimiento de estado de mantenimientos")
        print("  ✓ Restauración automática del estado de herramientas")
        print("  ✗ Estado 'En Revisión' (se necesita migración 018)")
    else:
        print("❌ MIGRACIONES PENDIENTES")
    
    print("=" * 70)
