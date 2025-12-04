"""Migration utility: add structured [META] block to legacy comentario rows lacking it.

Features:
 * Creates backup table comentario_backup (only once) before modifying.
 * Processes rows in batches (BATCH_SIZE) for memory safety.
 * Skips rows already containing metadata marker.
 * Supports dry-run mode (no updates) and custom database path.
 * Exposes migrate_conn() for testability.

Usage:
    python migrate_add_metadata_to_old_comments.py            # real migration
    python migrate_add_metadata_to_old_comments.py --dry-run  # report counts only

Exit codes: 0 success / 1 error
"""
import os, sqlite3, json, time, sys
from datetime import datetime
from utils.metadata import build_meta_note, META_MARK, parse_meta

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'fincafacil.db')

BATCH_SIZE = 500

def get_conn(db_path: str = DEFAULT_DB_PATH):
    return sqlite3.connect(db_path)

def is_meta(note: str) -> bool:
    return META_MARK in note if note else False

def migrate_conn(conn: sqlite3.Connection, dry_run: bool = False) -> int:
    """Perform migration on provided connection.
    Returns number of rows updated (0 in dry-run)."""
    start = time.time()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comentario'")
    if not cur.fetchone():
        print("comentario table not found. Abort.")
        return 0
    cur.execute("SELECT COUNT(*) FROM comentario WHERE nota NOT LIKE '%[META]%' OR nota IS NULL")
    total = cur.fetchone()[0]
    if total == 0:
        print("No legacy rows to migrate.")
        return 0
    print(f"Legacy rows: {total}")
    if dry_run:
        print("Dry-run: no changes applied.")
        return 0
    # Backup (only create if not exists)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comentario_backup'")
    if not cur.fetchone():
        cur.execute("CREATE TABLE comentario_backup AS SELECT * FROM comentario")
        conn.commit()
        print("Backup table comentario_backup created.")
    cur.execute("SELECT id, id_animal, fecha, autor, nota FROM comentario WHERE nota NOT LIKE '%[META]%' OR nota IS NULL")
    rows = cur.fetchall()
    updated = 0
    for chunk_start in range(0, len(rows), BATCH_SIZE):
        chunk = rows[chunk_start:chunk_start+BATCH_SIZE]
        for (cid, id_animal, fecha, autor, nota) in chunk:
            human = (nota or '').strip() or 'Comentario legado'
            meta = {
                'fecha_original': fecha,
                'autor_original': autor,
                'tipo': 'legacy',
                'migrated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            new_note = build_meta_note('legacy', human[:140], meta)
            cur.execute("UPDATE comentario SET nota=? WHERE id=?", (new_note, cid))
            updated += 1
        conn.commit()
        print(f"Migrated {updated}/{total}")
    print(f"Migration complete in {time.time()-start:.2f}s. Rows updated: {updated}")
    return updated

def migrate(db_path: str = DEFAULT_DB_PATH, dry_run: bool = False) -> int:
    with get_conn(db_path) as conn:
        return migrate_conn(conn, dry_run=dry_run)

if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    path_arg = None
    for a in sys.argv[1:]:
        if a != '--dry-run':
            path_arg = a
    db_path = path_arg if path_arg else DEFAULT_DB_PATH
    try:
        rows = migrate(db_path=db_path, dry_run=dry)
        sys.exit(0)
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
