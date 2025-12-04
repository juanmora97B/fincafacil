"""Ver FKs de tablas que deben referenciar finca"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from database import get_connection

with get_connection() as conn:
    cur = conn.cursor()
    
    for tabla in ['insumo', 'herramienta', 'sector']:
        print(f"\n{tabla} - Foreign Keys:")
        fks = cur.execute(f'PRAGMA foreign_key_list({tabla})').fetchall()
        if fks:
            for fk in fks:
                accion = fk[6] if len(fk) > 6 else 'NO ACTION'
                print(f"  {fk[3]} -> {fk[2]}({fk[4]}) ON DELETE {accion}")
        else:
            print("  (sin FKs)")
