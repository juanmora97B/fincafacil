"""
Migration 009: Consolidación final de FKs y limpieza de residuos

Objetivos:
- Asegurar que TODAS las tablas que referencian finca usan ON DELETE SET NULL
  (animal, potrero, insumo, herramienta, sector, lote, animal_legacy)
- Eliminar cualquier referencia de FK hacia tablas *_old (movimiento, evento, comentario, mantenimiento_herramienta, servicio, etc.)
- Reconstruir tabla animal con definición limpia (incluyendo FKs auto-referenciadas) si contiene incoherencias
- Limpiar tablas temporales *_old remanentes
- Idempotente: sólo migra cuando detecta necesidad
"""
import sys, os
from typing import List, Tuple
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_connection

FK_FINCA_TABLES = [
    ('animal', 'id_finca'),
    ('potrero', 'id_finca'),
    ('insumo', 'id_finca'),
    ('herramienta', 'id_finca'),
    ('sector', 'finca_id'),
    ('lote', 'finca_id'),
    ('animal_legacy', 'id_finca'),
]

# Tablas que históricamente han tenido referencias a *_old
POTENTIAL_OLD_REF_TABLES = [
    'movimiento', 'evento', 'comentario', 'mantenimiento_herramienta', 'servicio', 'animal',
]

def fetch_fk_list(cur, table: str) -> List[Tuple]:
    cur.execute(f"PRAGMA foreign_key_list({table})")
    return cur.fetchall()

def fetch_columns(cur, table: str) -> List[Tuple]:
    cur.execute(f"PRAGMA table_info({table})")
    return cur.fetchall()

def rebuild_animal(cur):
    """Reconstruye la tabla animal si alguna FK es incoherente (por ejemplo ref a lote_old)."""
    fks = fetch_fk_list(cur, 'animal')
    needs = False
    for fk in fks:
        ref_table = fk[2]
        if ref_table.endswith('_old'):
            needs = True
            break
    # También aseguramos orden y definición limpia
    if not needs:
        # Verificar que lote_id refiera a lote y no a lote_old
        for fk in fks:
            if fk[3] == 'lote_id' and fk[2] != 'lote':
                needs = True
                break
    if not needs:
        return False

    print("  ↻ Reconstruyendo tabla 'animal' (limpieza de FKs)...")
    cur.execute("PRAGMA foreign_keys = OFF;")
    cur.execute("ALTER TABLE animal RENAME TO animal_backup;")
    cur.execute("""
        CREATE TABLE animal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_finca INTEGER,
            codigo TEXT NOT NULL,
            nombre TEXT,
            tipo_ingreso TEXT,
            sexo TEXT,
            raza_id INTEGER,
            id_potrero INTEGER,
            lote_id INTEGER,
            id_grupo INTEGER,
            id_vendedor INTEGER,
            fecha_nacimiento DATE,
            fecha_compra DATE,
            peso_nacimiento REAL,
            peso_compra REAL,
            precio_compra REAL,
            id_padre INTEGER,
            id_madre INTEGER,
            tipo_concepcion TEXT,
            salud TEXT,
            estado TEXT DEFAULT 'Activo',
            inventariado INTEGER DEFAULT 0,
            color TEXT,
            hierro TEXT,
            numero_hierros INTEGER,
            composicion_racial TEXT,
            comentarios TEXT,
            foto_path TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (raza_id) REFERENCES raza (id) ON DELETE SET NULL,
            FOREIGN KEY (id_finca) REFERENCES finca (id) ON DELETE SET NULL,
            FOREIGN KEY (id_potrero) REFERENCES potrero (id) ON DELETE SET NULL,
            FOREIGN KEY (lote_id) REFERENCES lote (id) ON DELETE SET NULL,
            FOREIGN KEY (id_grupo) REFERENCES grupo (id) ON DELETE SET NULL,
            FOREIGN KEY (id_vendedor) REFERENCES vendedor (id) ON DELETE SET NULL,
            FOREIGN KEY (id_padre) REFERENCES animal (id) ON DELETE SET NULL,
            FOREIGN KEY (id_madre) REFERENCES animal (id) ON DELETE SET NULL
        );
    """)
    cur.execute("INSERT INTO animal SELECT * FROM animal_backup;")
    cur.execute("DROP TABLE animal_backup;")
    cur.execute("PRAGMA foreign_keys = ON;")
    return True

def recreate_table_with_corrected_fks(cur, table: str, fk_corrections: dict):
    """Recrea una tabla corrigiendo FKs que referencian tablas *_old.
    fk_corrections: {column_name: new_table_name}
    """
    print(f"  ↻ Corrigiendo referencias *_old en '{table}' ...")
    cols = fetch_columns(cur, table)
    col_defs = []
    for col in cols:
        name = col[1]
        tipo = col[2]
        notnull = " NOT NULL" if col[3] else ""
        default = f" DEFAULT {col[4]}" if col[4] is not None else ""
        pk = " PRIMARY KEY AUTOINCREMENT" if col[5] and name == 'id' else ""
        col_defs.append(f"{name} {tipo}{pk}{notnull}{default}")

    fks = fetch_fk_list(cur, table)
    fk_defs = []
    for fk in fks:
        col_name = fk[3]
        ref_table = fk[2]
        ref_col = fk[4]
        on_delete = fk[6] if len(fk) > 6 else 'NO ACTION'
        if col_name in fk_corrections:
            ref_table = fk_corrections[col_name]
        fk_defs.append(f"FOREIGN KEY ({col_name}) REFERENCES {ref_table} ({ref_col}) ON DELETE {on_delete}")

    cur.execute("PRAGMA foreign_keys = OFF;")
    cur.execute(f"ALTER TABLE {table} RENAME TO {table}_backup;")
    all_defs = col_defs + fk_defs
    create_sql = f"CREATE TABLE {table} ({', '.join(all_defs)});"
    cur.execute(create_sql)
    col_names = [c[1] for c in cols]
    cur.execute(f"INSERT INTO {table} ({', '.join(col_names)}) SELECT {', '.join(col_names)} FROM {table}_backup;")
    cur.execute(f"DROP TABLE {table}_backup;")
    cur.execute("PRAGMA foreign_keys = ON;")

def ensure_on_delete_set_null(cur, table: str, column: str):
    fks = fetch_fk_list(cur, table)
    needs = False
    for fk in fks:
        if fk[3] == column:
            # fk[6] => on_delete
            if len(fk) <= 6 or fk[6] != 'SET NULL':
                needs = True
            # También si referencia tabla *_old
            if fk[2].endswith('_old'):
                needs = True
            break
    if not needs:
        return False

    print(f"  ↻ Ajustando FK {table}.{column} a ON DELETE SET NULL ...")
    cols = fetch_columns(cur, table)
    col_defs = []
    for col in cols:
        name = col[1]
        tipo = col[2]
        notnull = " NOT NULL" if col[3] else ""
        default = f" DEFAULT {col[4]}" if col[4] is not None else ""
        pk = " PRIMARY KEY AUTOINCREMENT" if col[5] and name == 'id' else ""
        col_defs.append(f"{name} {tipo}{pk}{notnull}{default}")

    fks_defs = []
    for fk in fks:
        col_name = fk[3]
        ref_table = fk[2]
        ref_col = fk[4]
        on_delete = fk[6] if len(fk) > 6 else 'NO ACTION'
        if col_name == column:
            on_delete = 'SET NULL'
        fks_defs.append(f"FOREIGN KEY ({col_name}) REFERENCES {ref_table} ({ref_col}) ON DELETE {on_delete}")

    cur.execute("PRAGMA foreign_keys = OFF;")
    cur.execute(f"ALTER TABLE {table} RENAME TO {table}_backup;")
    create_sql = f"CREATE TABLE {table} ({', '.join(col_defs + fks_defs)});"
    cur.execute(create_sql)
    col_names = [c[1] for c in cols]
    cur.execute(f"INSERT INTO {table} ({', '.join(col_names)}) SELECT {', '.join(col_names)} FROM {table}_backup;")
    cur.execute(f"DROP TABLE {table}_backup;")
    cur.execute("PRAGMA foreign_keys = ON;")
    return True


def cleanup_temp_tables(cur):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_old'")
    leftovers = [r[0] for r in cur.fetchall()]
    for name in leftovers:
        print(f"  🧹 Eliminando tabla temporal residual: {name}")
        cur.execute(f"DROP TABLE IF EXISTS {name};")


def run():
    with get_connection() as conn:
        cur = conn.cursor()
        print("=== Migration 009: Consolidación FKs y limpieza ===")
        changed = False

        # 1. Asegurar FKs ON DELETE SET NULL hacia finca
        print("\n→ Verificando FKs que referencian 'finca' ...")
        for table, column in FK_FINCA_TABLES:
            # Confirmar que la tabla existe
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cur.fetchone():
                continue
            if ensure_on_delete_set_null(cur, table, column):
                changed = True

        # 2. Reconstruir animal si es necesario
        print("\n→ Verificando tabla 'animal' para reconstrucción ...")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animal'")
        if cur.fetchone():
            if rebuild_animal(cur):
                changed = True

        # 3. Buscar referencias a *_old en tablas potenciales
        print("\n→ Buscando FKs que apuntan a tablas *_old ...")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        all_tables = [r[0] for r in cur.fetchall()]

        for table in all_tables:
            fks = fetch_fk_list(cur, table)
            corrections = {}
            for fk in fks:
                col_name = fk[3]
                ref_table = fk[2]
                if ref_table.endswith('_old'):
                    new_name = ref_table[:-4]  # remove _old
                    corrections[col_name] = new_name
            if corrections:
                recreate_table_with_corrected_fks(cur, table, corrections)
                changed = True

        # 4. Limpieza final de tablas temporales
        print("\n→ Limpiando tablas temporales *_old ...")
        cleanup_temp_tables(cur)

        # 5. Verificación resumen
        print("\n→ Resumen final de FKs hacia finca:")
        for table, column in FK_FINCA_TABLES:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cur.fetchone():
                continue
            fks = fetch_fk_list(cur, table)
            for fk in fks:
                if fk[3] == column:
                    on_delete = fk[6] if len(fk) > 6 else 'NO ACTION'
                    status = 'OK' if on_delete == 'SET NULL' else 'WARN'
                    print(f"  {table}.{column} -> {fk[2]}({fk[4]}) ON DELETE {on_delete} [{status}]")

        conn.commit()
        print("\n=== Migration 009 completada ===")
        if changed:
            print("✔ Se aplicaron cambios de consolidación.")
        else:
            print("✔ No se requirieron cambios (estado ya consistente).")

if __name__ == '__main__':
    run()
