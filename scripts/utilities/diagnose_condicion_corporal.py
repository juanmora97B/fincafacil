import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_connection, DB_PATH
print(f"DB path: {DB_PATH}")
with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM condicion_corporal")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM condicion_corporal WHERE estado='Activo'")
    activos = cur.fetchone()[0]
    print(f"Total registros condicion_corporal: {total}")
    print(f"Activos visibles (estado='Activo'): {activos}")
    cur.execute("SELECT codigo, descripcion, puntuacion, escala, estado FROM condicion_corporal ORDER BY codigo LIMIT 20")
    rows = cur.fetchall()
    print("Primeros 20 registros:")
    for r in rows:
        print(tuple(r))
    # Mostrar inactivos si existen
    cur.execute("SELECT codigo, estado FROM condicion_corporal WHERE estado!='Activo' LIMIT 10")
    inactivos = cur.fetchall()
    if inactivos:
        print("Registros no activos:")
        for r in inactivos:
            print(tuple(r))
