import sys, os
sys.path.append(os.path.abspath('.'))
from database import get_connection

with get_connection() as conn:
    cur = conn.cursor()
    cur.execute('SELECT id, codigo, nombre, propietario, ubicacion FROM finca ORDER BY id')
    rows = cur.fetchall()
    print('ID | codigo | nombre | propietario | ubicacion')
    for r in rows:
        try:
            print(f"{r['id']} | {r['codigo']} | {r['nombre']} | {r['propietario']} | {r['ubicacion']}")
        except Exception:
            print(r)
