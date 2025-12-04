"""
Migration 010: Añade columna id_finca y FK (SET NULL) a tablas vendedor y procedencia
Idempotente: solo modifica si las columnas no existen.
"""
import sys, os, sqlite3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database.database import get_db_connection

TABLES = [
    ('vendedor', 'id_finca'),
    ('procedencia', 'id_finca'),
]

FK_REF = 'finca'

def column_exists(cur, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == column for r in cur.fetchall())

def fk_has_on_delete_set_null(cur, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA foreign_key_list({table})")
    for fk in cur.fetchall():
        if fk[3] == column:
            if len(fk) > 6 and fk[6] == 'SET NULL':
                return True
    return False

def rebuild_with_fk(cur, table: str, new_column: str):
    print(f"  ↻ Reescribiendo tabla '{table}' para agregar columna {new_column} y FK...")
    cur.execute(f"PRAGMA table_info({table})")
    cols = cur.fetchall()
    col_defs = []
    for c in cols:
        name, tipo, notnull, default, pk = c[1], c[2], c[3], c[4], c[5]
        nn = ' NOT NULL' if notnull else ''
        df = f" DEFAULT {default}" if default is not None else ''
        pk_def = ' PRIMARY KEY AUTOINCREMENT' if pk and name == 'id' else ''
        col_defs.append(f"{name} {tipo}{pk_def}{nn}{df}")

    # Añadir nueva columna al final si no existe
    if not column_exists(cur, table, new_column):
        col_defs.append(f"{new_column} INTEGER")

    # Recuperar FKs existentes (excepto la nueva) para replicarlas
    cur.execute(f"PRAGMA foreign_key_list({table})")
    old_fks = cur.fetchall()
    fk_defs = []
    for fk in old_fks:
        col_name = fk[3]
        ref_table = fk[2]
        ref_col = fk[4]
        on_delete = fk[6] if len(fk) > 6 else 'NO ACTION'
        fk_defs.append(f"FOREIGN KEY ({col_name}) REFERENCES {ref_table} ({ref_col}) ON DELETE {on_delete}")

    # Agregar nueva FK
    fk_defs.append(f"FOREIGN KEY ({new_column}) REFERENCES {FK_REF} (id) ON DELETE SET NULL")

    cur.execute("PRAGMA foreign_keys = OFF;")
    cur.execute(f"ALTER TABLE {table} RENAME TO {table}_backup;")
    create_sql = f"CREATE TABLE {table} ({', '.join(col_defs + fk_defs)});"
    cur.execute(create_sql)
    # Preparar columnas para INSERT (las antiguas + nueva vacía si procede)
    old_col_names = [c[1] for c in cols]
    select_cols = ', '.join(old_col_names)
    insert_cols = ', '.join(old_col_names + ([new_column] if new_column not in old_col_names else []))
    if new_column not in old_col_names:
        cur.execute(f"INSERT INTO {table} ({insert_cols}) SELECT {select_cols}, NULL FROM {table}_backup;")
    else:
        cur.execute(f"INSERT INTO {table} ({insert_cols}) SELECT {select_cols} FROM {table}_backup;")
    cur.execute(f"DROP TABLE {table}_backup;")
    cur.execute("PRAGMA foreign_keys = ON;")

    # Índice para rendimiento
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_{new_column} ON {table} ({new_column});")


def run():
    with get_db_connection() as conn:
        cur = conn.cursor()
        print("=== Migration 010: Añadir id_finca a vendedor y procedencia ===")
        changed = False
        # Verificar existencia de tabla finca
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finca'")
        if not cur.fetchone():
            print("⚠️ Tabla 'finca' no existe; abortando migración.")
            return

        for table, column in TABLES:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cur.fetchone():
                print(f"⚠️ Tabla '{table}' no existe; saltando.")
                continue
            needs_rebuild = False
            if not column_exists(cur, table, column):
                needs_rebuild = True
            else:
                # Si columna existe pero FK no tiene ON DELETE SET NULL, reconstruir también
                if not fk_has_on_delete_set_null(cur, table, column):
                    needs_rebuild = True
            if needs_rebuild:
                rebuild_with_fk(cur, table, column)
                changed = True
            else:
                # Asegurar índice
                cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table} ({column});")
        conn.commit()
        if changed:
            print("✔ Cambios aplicados correctamente.")
        else:
            print("✔ No se requirieron cambios; estructura ya consistente.")
        print("=== Migration 010 completada ===")

if __name__ == '__main__':
    run()
