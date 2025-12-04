"""
Verificación final: Confirmar que todas las FKs de finca permiten eliminación
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database import get_connection

print("=" * 60)
print("VERIFICACIÓN FINAL DE FOREIGN KEYS PARA FINCA")
print("=" * 60)

with get_connection() as conn:
    cur = conn.cursor()
    
    # Obtener todas las tablas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cur.fetchall()]
    
    print("\nTablas que referencian 'finca':\n")
    
    tables_referencing_finca = []
    
    for table in tables:
        cur.execute(f"PRAGMA foreign_key_list({table})")
        fks = cur.fetchall()
        
        for fk in fks:
            if fk[2] == 'finca':  # tabla referenciada
                on_delete = fk[6] if len(fk) > 6 else 'NO ACTION'
                status = "✔" if on_delete == "SET NULL" else "❌"
                print(f"{status} {table}.{fk[3]} -> finca({fk[4]}) | ON DELETE {on_delete}")
                tables_referencing_finca.append({
                    'table': table,
                    'column': fk[3],
                    'on_delete': on_delete,
                    'ok': on_delete == "SET NULL"
                })
    
    print("\n" + "=" * 60)
    
    all_ok = all(t['ok'] for t in tables_referencing_finca)
    
    if all_ok:
        print("✔ TODAS LAS FOREIGN KEYS ESTÁN CORRECTAMENTE CONFIGURADAS")
        print("✔ Las fincas ahora se pueden eliminar sin problemas")
        print(f"\nTablas afectadas: {len(tables_referencing_finca)}")
    else:
        print("❌ ALGUNAS FOREIGN KEYS AÚN NECESITAN CORRECCIÓN")
        problematic = [t for t in tables_referencing_finca if not t['ok']]
        print(f"\nTablas con problemas: {len(problematic)}")
        for t in problematic:
            print(f"  - {t['table']}.{t['column']}: ON DELETE {t['on_delete']}")
    
    print("=" * 60)
