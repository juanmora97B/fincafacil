"""
Verificar estructura completa de tabla animal incluyendo todas las FKs
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database import get_connection

with get_connection() as conn:
    cur = conn.cursor()
    
    print("=" * 60)
    print("ESTRUCTURA DE TABLA ANIMAL")
    print("=" * 60)
    
    print("\nColumnas:")
    cur.execute("PRAGMA table_info(animal)")
    for col in cur.fetchall():
        print(f"  {col[1]} {col[2]}{' NOT NULL' if col[3] else ''}{' PK' if col[5] else ''}")
    
    print("\nForeign Keys:")
    cur.execute("PRAGMA foreign_key_list(animal)")
    fks = cur.fetchall()
    for fk in fks:
        on_delete = fk[6] if len(fk) > 6 else 'NO ACTION'
        print(f"  {fk[3]} -> {fk[2]}({fk[4]}) ON DELETE {on_delete}")
    
    print(f"\nTotal FKs: {len(fks)}")
    
    # Verificar si hay FKs duplicadas o mal configuradas
    print("\n" + "=" * 60)
    print("SQL de creación actual:")
    print("=" * 60)
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='animal'")
    sql = cur.fetchone()[0]
    print(sql)
