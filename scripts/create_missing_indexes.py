"""Create missing indexes to improve query performance on foreign keys and filters.
Run safely multiple times (IF NOT EXISTS)."""
import sqlite3, os
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'fincafacil.db')

INDEXES = [
    ("idx_animal_codigo", "CREATE INDEX IF NOT EXISTS idx_animal_codigo ON animal(codigo)"),
    ("idx_animal_finca", "CREATE INDEX IF NOT EXISTS idx_animal_finca ON animal(id_finca)"),
    ("idx_animal_potrero", "CREATE INDEX IF NOT EXISTS idx_animal_potrero ON animal(id_potrero)"),
    ("idx_animal_lote", "CREATE INDEX IF NOT EXISTS idx_animal_lote ON animal(lote_id)"),
    ("idx_animal_sector", "CREATE INDEX IF NOT EXISTS idx_animal_sector ON animal(id_sector)"),
    ("idx_potrero_finca", "CREATE INDEX IF NOT EXISTS idx_potrero_finca ON potrero(id_finca)"),
    ("idx_lote_finca", "CREATE INDEX IF NOT EXISTS idx_lote_finca ON lote(finca_id)"),
    ("idx_comentario_animal_fecha", "CREATE INDEX IF NOT EXISTS idx_comentario_animal_fecha ON comentario(id_animal, fecha)"),
    ("idx_servicio_hembra", "CREATE INDEX IF NOT EXISTS idx_servicio_hembra ON servicio(id_hembra)"),
    ("idx_servicio_macho", "CREATE INDEX IF NOT EXISTS idx_servicio_macho ON servicio(id_macho)"),
]

OPTIONAL_TABLES = ["comentario", "servicio"]

def table_exists(cur, name):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None

def main():
    if not os.path.exists(DB_PATH):
        print("Database not found:", DB_PATH)
        return
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        applied = 0
        for idx_name, idx_sql in INDEXES:
            # Skip optional if table missing
            target_table = idx_sql.split(' ON ')[1].split('(')[0]
            if target_table in OPTIONAL_TABLES and not table_exists(cur, target_table):
                continue
            try:
                cur.execute(idx_sql)
                applied += 1
            except Exception as e:
                print(f"Failed index {idx_name}: {e}")
        conn.commit()
    print(f"Indexes processed: {applied}")

if __name__ == '__main__':
    main()
