"""Migration 002: Normalize animal table

Removes duplicated columns: raza(text), id_raza, id_lote
Keeps canonical columns: raza_id (INTEGER), lote_id (INTEGER)
Steps:
1. Inspect current animal schema; abort if already normalized.
2. Build mapping for raza_id: prefer existing raza_id / id_raza; if NULL attempt match by a.raza name.
3. Create new table animal_new with normalized structure.
4. Copy data transforming columns.
5. Drop old animal; rename animal_new -> animal.
6. Re-create indexes referencing updated column names.

Safe re-run: will detect absence of legacy columns and skip.
"""
from datetime import datetime
import sqlite3
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_connection

# Definition of new normalized animal table
NORMALIZED_DDL = """
CREATE TABLE IF NOT EXISTS animal_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_finca INTEGER,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT,
    tipo_ingreso TEXT,
    sexo TEXT,
    raza_id INTEGER, -- canonical FK
    id_potrero INTEGER,
    lote_id INTEGER, -- renamed from id_lote
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
    FOREIGN KEY (raza_id) REFERENCES raza (id),
    FOREIGN KEY (id_finca) REFERENCES finca (id),
    FOREIGN KEY (id_potrero) REFERENCES potrero (id),
    FOREIGN KEY (lote_id) REFERENCES lote (id),
    FOREIGN KEY (id_grupo) REFERENCES grupo (id),
    FOREIGN KEY (id_vendedor) REFERENCES vendedor (id),
    FOREIGN KEY (id_padre) REFERENCES animal (id),
    FOREIGN KEY (id_madre) REFERENCES animal (id)
);
"""

REINDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_animal_codigo ON animal(codigo);",
    "CREATE INDEX IF NOT EXISTS idx_animal_finca ON animal(id_finca);",
    "CREATE INDEX IF NOT EXISTS idx_animal_raza ON animal(raza_id);",
    "CREATE INDEX IF NOT EXISTS idx_animal_lote ON animal(lote_id);",
]

LEGACY_COLUMNS = {"raza", "id_raza", "id_lote"}


def _legacy_columns_present(cur) -> bool:
    cur.execute("PRAGMA table_info(animal)")
    cols = {row[1] for row in cur.fetchall()}
    return bool(LEGACY_COLUMNS & cols)


def _build_temp_raza_mapping(cur):
    """Return dict animal_id -> resolved raza_id"""
    # First fetch name->id mapping from raza
    cur.execute("SELECT id, nombre FROM raza")
    raza_name_to_id = {row[1]: row[0] for row in cur.fetchall() if row[1]}

    mapping = {}
    # Acquire animal raw data for legacy columns
    cur.execute("SELECT id, raza_id, id_raza, raza FROM animal")
    for aid, raza_id, id_raza, raza_name in cur.fetchall():
        resolved = None
        for candidate in (raza_id, id_raza):
            if candidate:
                resolved = candidate
                break
        if not resolved and raza_name:
            resolved = raza_name_to_id.get(raza_name)
        mapping[aid] = resolved
    return mapping


def run():
    with get_connection() as conn:
        cur = conn.cursor()

        # If already normalized skip
        if not _legacy_columns_present(cur):
            print("➖ Migration 002 skipped: animal already normalized")
            return

        print("🔧 Normalizing animal table ...")
        # Build raza mapping
        raza_map = _build_temp_raza_mapping(cur)

        # Create new table
        cur.execute(NORMALIZED_DDL)

        # Copy data transforming columns
        cur.execute("SELECT * FROM animal")
        rows = cur.fetchall()
        cur.execute("PRAGMA table_info(animal)")
        legacy_cols = [c[1] for c in cur.fetchall()]

        # Prepare insert into new table (exclude legacy columns)
        insert_cols = [
            'id','id_finca','codigo','nombre','tipo_ingreso','sexo','raza_id','id_potrero',
            'id_lote','id_grupo','id_vendedor','fecha_nacimiento','fecha_compra','peso_nacimiento',
            'peso_compra','precio_compra','id_padre','id_madre','tipo_concepcion','salud','estado',
            'inventariado','color','hierro','numero_hierros','composicion_racial','comentarios',
            'foto_path','fecha_registro','fecha_creacion','fecha_actualizacion'
        ]
        # Map id_lote -> lote_id in target
        target_cols_sql = ','.join(insert_cols).replace('id_lote','lote_id')
        placeholders = ','.join(['?' for _ in insert_cols])
        insert_sql = f"INSERT INTO animal_new ({target_cols_sql}) VALUES ({placeholders})"

        # Build row mapping indexes
        col_index = {name: idx for idx, name in enumerate(legacy_cols)}

        for row in rows:
            aid = row[col_index['id']]
            raza_id_resolved = raza_map.get(aid)
            # Extract row values sequentially
            values = []
            for col in insert_cols:
                if col == 'raza_id':
                    values.append(raza_id_resolved)
                elif col == 'id_lote':
                    # legacy column name
                    values.append(row[col_index.get('id_lote')])
                else:
                    # Skip legacy-deleted columns gracefully
                    if col in ('raza','id_raza'):
                        values.append(None)
                    else:
                        values.append(row[col_index.get(col)])
            cur.execute(insert_sql, values)

        # Replace table
        cur.execute("ALTER TABLE animal RENAME TO animal_legacy")
        cur.execute("ALTER TABLE animal_new RENAME TO animal")

        # Recreate indexes
        for idx in REINDEX_STATEMENTS:
            cur.execute(idx)

        conn.commit()
        print(f"✅ Migration 002 applied. Migrated {len(rows)} animal rows.")

if __name__ == '__main__':
    run()
