"""Script para verificar estructura de tablas de insumos"""
import sys
sys.path.insert(0, '.')
from database.database import get_db_connection

print("=" * 70)
print("ESTRUCTURA DE TABLAS DE INSUMOS")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Tabla insumo
    print("\n📦 Tabla INSUMO:")
    print("-" * 70)
    cur.execute('PRAGMA table_info(insumo)')
    cols = cur.fetchall()
    for c in cols:
        print(f"  • {c[1]:30} {c[2]:15}")
    
    cur.execute("SELECT COUNT(*) FROM insumo")
    count = cur.fetchone()[0]
    print(f"\n  Total registros: {count}")
    
    # Tablas relacionadas
    print("\n📋 Tablas relacionadas con insumos:")
    print("-" * 70)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%insumo%'")
    tablas = cur.fetchall()
    for t in tablas:
        print(f"  • {t[0]}")
        
        # Ver estructura
        cur.execute(f'PRAGMA table_info({t[0]})')
        cols = cur.fetchall()
        if len(cols) > 0:
            for c in cols[:5]:  # Primeras 5 columnas
                print(f"      - {c[1]} ({c[2]})")
            if len(cols) > 5:
                print(f"      ... y {len(cols)-5} columnas más")
        
        cur.execute(f"SELECT COUNT(*) FROM {t[0]}")
        count = cur.fetchone()[0]
        print(f"      Total: {count} registros\n")
    
    print("=" * 70)
