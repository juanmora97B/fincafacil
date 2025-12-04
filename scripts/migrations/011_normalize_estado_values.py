"""
Migration 011: Normaliza valores de estado generales (Activa->Activo, Operativa->Activo)
Mantiene estados de dominios especializados (servicio, pago, etc.). Idempotente.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_connection

GENERAL_TABLES = [
    'finca','herramienta','animal','potrero','lote','grupo','insumo','procedencia','vendedor'
]
MAPPING = {
    'Activa': 'Activo',
    'Operativa': 'Activo',
    'activa': 'Activo',
    'operativa': 'Activo'
}

def run():
    with get_connection() as conn:
        cur = conn.cursor()
        print('=== Migration 011: Normalizar estado ===')
        for table in GENERAL_TABLES:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cur.fetchone():
                continue
            for src, dst in MAPPING.items():
                try:
                    cur.execute(f"UPDATE {table} SET estado=? WHERE estado=?", (dst, src))
                except Exception as e:
                    print(f"  ⚠️ No se pudo actualizar {table}.{src}: {e}")
        conn.commit()
        print('✔ Normalización aplicada (si había valores).')
        print('=== Migration 011 completada ===')

if __name__ == '__main__':
    run()
