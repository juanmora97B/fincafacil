"""
Script de limpieza automática de tablas legacy (sin confirmación)
"""
import sqlite3
from pathlib import Path

db_path = Path("database/fincafacil.db")
if not db_path.exists():
    print("❌ No se encuentra la base de datos")
    exit(1)

try:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    print("🔧 Limpiando tablas legacy...")
    
    # Verificar que animal tiene datos
    cur.execute("SELECT COUNT(*) FROM animal")
    count = cur.fetchone()[0]
    print(f"✓ Tabla 'animal' tiene {count} registros")
    
    if count == 0:
        print("⚠️ Tabla animal vacía, abortando por seguridad")
        exit(1)
    
    # Eliminar tablas legacy
    for table in ['animal_legacy', 'animal_legacy_temp']:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"✓ Tabla '{table}' eliminada")
    
    # Eliminar triggers con referencias legacy
    cur.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND sql LIKE '%legacy%'")
    for (trigger_name,) in cur.fetchall():
        cur.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
        print(f"✓ Trigger '{trigger_name}' eliminado")
    
    conn.commit()
    print("\n✅ Limpieza completada exitosamente")
    
    # Verificar
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%legacy%'")
    remaining = cur.fetchall()
    if remaining:
        print(f"⚠️ Tablas legacy restantes: {[r[0] for r in remaining]}")
    else:
        print("✓ No quedan tablas legacy")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
