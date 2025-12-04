"""
Migration 012: Consolidar procedencia y vendedor en tabla 'origen'.
Crea tabla origen y la llena con registros de procedencia (tipo='procedencia') y vendedor (tipo='vendedor').
Agrega columna origen_id a animal (sin FK formal por simplicidad idempotente) y asigna origen_id basado en id_vendedor.
NOTA: Para una FK estricta se requiere reconstruir tabla animal; se deja para una migración futura si se desea.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_connection

def run():
    with get_connection() as conn:
        cur = conn.cursor()
        print('=== Migration 012: Consolidar origen ===')
        # Crear tabla origen si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS origen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_finca INTEGER,
                tipo TEXT NOT NULL, -- 'procedencia' | 'vendedor'
                codigo TEXT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                estado TEXT DEFAULT 'Activo',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Índices básicos
        cur.execute("CREATE INDEX IF NOT EXISTS idx_origen_tipo ON origen (tipo)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_origen_finca ON origen (id_finca)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_origen_nombre ON origen (nombre)")

        # Poblar desde procedencia
        cur.execute("SELECT id, id_finca, codigo, descripcion, comentario, estado FROM procedencia")
        procedencias = cur.fetchall()
        inserted_proc = 0
        for r in procedencias:
            pid, finca_id, codigo, descripcion, comentario, estado = r
            # Verificar existencia previa
            cur.execute("SELECT 1 FROM origen WHERE tipo='procedencia' AND nombre=?", (descripcion,))
            if cur.fetchone():
                continue
            cur.execute("INSERT INTO origen (id_finca, tipo, codigo, nombre, descripcion, estado) VALUES (?,?,?,?,?,?)",
                        (finca_id, 'procedencia', codigo, descripcion, comentario, estado))
            inserted_proc += 1

        # Poblar desde vendedor
        cur.execute("SELECT id, id_finca, nombre, estado FROM vendedor")
        vendedores = cur.fetchall()
        inserted_vend = 0
        for r in vendedores:
            vid, finca_id, nombre, estado = r
            cur.execute("SELECT 1 FROM origen WHERE tipo='vendedor' AND nombre=?", (nombre,))
            if cur.fetchone():
                continue
            codigo = f'VEND-{vid}'
            cur.execute("INSERT INTO origen (id_finca, tipo, codigo, nombre, descripcion, estado) VALUES (?,?,?,?,?,?)",
                        (finca_id, 'vendedor', codigo, nombre, None, estado))
            inserted_vend += 1

        # Agregar columna origen_id a animal si no existe
        cur.execute("PRAGMA table_info(animal)")
        cols = [c[1] for c in cur.fetchall()]
        if 'origen_id' not in cols:
            print('↻ Agregando columna origen_id a animal ...')
            cur.execute("ALTER TABLE animal ADD COLUMN origen_id INTEGER")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_origen ON animal (origen_id)")
        # Asignar origen_id para filas con id_vendedor
        cur.execute("UPDATE animal SET origen_id = NULL WHERE origen_id IS NOT NULL")
        cur.execute("""
            UPDATE animal SET origen_id = (
                SELECT o.id FROM origen o 
                JOIN vendedor v ON v.id = animal.id_vendedor
                WHERE o.tipo='vendedor' AND o.nombre = v.nombre
            ) WHERE id_vendedor IS NOT NULL
        """)

        conn.commit()
        print(f'✔ Procedencias insertadas: {inserted_proc}, Vendedores insertados: {inserted_vend}')
        print('=== Migration 012 completada ===')

if __name__ == '__main__':
    run()
