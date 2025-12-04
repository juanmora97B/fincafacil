import sqlite3

DB_PATH = 'database/fincafacil.db'

def listar_razas(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nombre, descripcion, estado
        FROM raza
        ORDER BY LOWER(nombre)
    """)
    rows = cur.fetchall()
    print("\n" + "="*80)
    print("RAZAS (catálogo guardado)")
    print("="*80)
    print(f"Total: {len(rows)}\n")
    print(f"{'ID':<5} {'Nombre':<28} {'Estado':<10}  Descripción")
    print("-"*80)
    for r in rows:
        rid, nombre, desc, estado = r
        print(f"{rid:<5} {nombre:<28} {estado:<10}  {desc or ''}")

def listar_procedencias(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, codigo, tipo_procedencia, descripcion, ubicacion, estado
        FROM procedencia
        ORDER BY codigo
    """)
    rows = cur.fetchall()
    print("\n" + "="*80)
    print("PROCEDENCIAS (catálogo guardado)")
    print("="*80)
    print(f"Total: {len(rows)}\n")
    print(f"{'ID':<5} {'Codigo':<10} {'Tipo':<18} {'Estado':<10}  Descripción / Ubicación")
    print("-"*100)
    for p in rows:
        pid, codigo, tipo, desc, ubic, estado = p
        print(f"{pid:<5} {codigo:<10} {tipo or '':<18} {estado:<10}  {desc or ''} / {ubic or ''}")

if __name__ == '__main__':
    conn = sqlite3.connect(DB_PATH)
    try:
        listar_razas(conn)
        listar_procedencias(conn)
    finally:
        conn.close()
