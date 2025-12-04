"""Migration 014: Remove legacy 'grupo' table and 'id_grupo' column from animal.
Safe to run multiple times. Performs schema copy without data loss.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / 'database' / 'fincafacil.db'

def table_exists(cur, name: str) -> bool:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None

def column_exists(cur, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())

def recreate_animal_without_id_grupo(cur):
    # Capture existing columns and types (including those added by later migrations)
    cur.execute("PRAGMA table_info(animal)")
    pragma_cols = cur.fetchall()
    if not any(row[1] == 'id_grupo' for row in pragma_cols):
        return False
    # Build create table dynamically excluding id_grupo
    col_defs = []
    for cid, name, col_type, notnull, dflt, pk in pragma_cols:
        if name == 'id_grupo':
            continue
        line = f"{name} {col_type or ''}".strip()
        if pk:
            line += " PRIMARY KEY AUTOINCREMENT" if name == 'id' else " PRIMARY KEY"
        if not pk and notnull:
            line += " NOT NULL"
        if dflt is not None:
            line += f" DEFAULT {dflt}"
        col_defs.append(line)
    # Append foreign keys for known columns present
    fk_lines = []
    fks = [
        ("raza_id", "raza", "id"),
        ("id_finca", "finca", "id"),
        ("id_potrero", "potrero", "id"),
        ("lote_id", "lote", "id"),
        ("id_sector", "sector", "id"),
        ("id_vendedor", "vendedor", "id"),
        ("id_padre", "animal", "id"),
        ("id_madre", "animal", "id")
    ]
    existing_names = {row[1] for row in pragma_cols}
    for col, ref_table, ref_col in fks:
        if col in existing_names and col != 'id_grupo':
            fk_lines.append(f"FOREIGN KEY ({col}) REFERENCES {ref_table} ({ref_col})")
    create_sql = "CREATE TABLE animal_new (\n    " + ",\n    ".join(col_defs + fk_lines) + "\n);"
    cur.execute("DROP TABLE IF EXISTS animal_new")
    cur.execute(create_sql)
    copy_cols = [row[1] for row in pragma_cols if row[1] != 'id_grupo']
    cur.execute(f"INSERT INTO animal_new ({', '.join(copy_cols)}) SELECT {', '.join(copy_cols)} FROM animal")
    cur.execute("DROP TABLE animal")
    cur.execute("ALTER TABLE animal_new RENAME TO animal")
    return True

def ensure_indexes(cur):
    # Ensure id_sector column exists after rebuild (legacy DBs may lack it)
    cur.execute("PRAGMA table_info(animal)")
    cols = {r[1] for r in cur.fetchall()}
    if 'id_sector' not in cols:
        cur.execute("ALTER TABLE animal ADD COLUMN id_sector INTEGER")
    # Recreate needed indexes if missing (sector, lote, finca, codigo)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_codigo ON animal(codigo)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_finca ON animal(id_finca)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_potrero ON animal(id_potrero)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_lote ON animal(lote_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_sector ON animal(id_sector)")

def ensure_trigger(cur):
    cur.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name='trg_animal_update'")
    if not cur.fetchone():
        cur.execute("""
        CREATE TRIGGER trg_animal_update
        AFTER UPDATE ON animal
        BEGIN
            UPDATE animal SET fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;""")

def run():
    if not DB_PATH.exists():
        print("BD no encontrada, migración omitida")
        return
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        changed = False
        # Drop grupo table if exists and empty
        if table_exists(cur, 'grupo'):
            cur.execute("SELECT COUNT(*) FROM grupo")
            if cur.fetchone()[0] == 0:
                cur.execute("DROP TABLE grupo")
                changed = True
                print("Tabla 'grupo' eliminada (vacía)")
        # Remove id_grupo column from animal if present
        if column_exists(cur, 'animal', 'id_grupo'):
            if recreate_animal_without_id_grupo(cur):
                changed = True
                print("Columna id_grupo eliminada de 'animal'")
        ensure_indexes(cur)
        ensure_trigger(cur)
        conn.commit()
    print("Migración 014 completada" if changed else "Migración 014 sin cambios")

if __name__ == '__main__':
    run()
