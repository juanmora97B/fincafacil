import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_connection

with get_connection() as conn:
    cur = conn.cursor()
    # Limpiar tablas temporales fallidas
    for table in ['animal_old', 'potrero_old', 'insumo_old', 'herramienta_old', 'sector_old']:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"✔ Eliminada tabla temporal: {table}")
        except Exception as e:
            print(f"⚠ No se pudo eliminar {table}: {e}")
    conn.commit()
print("✔ Limpieza completada")
