import os, sqlite3, tempfile
from datetime import datetime
from scripts.migrate_add_metadata_to_old_comments import migrate_conn
from utils.metadata import parse_meta


def _build_temp_db():
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, 'temp.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Minimal schema
    cur.execute("CREATE TABLE comentario (id INTEGER PRIMARY KEY AUTOINCREMENT, id_animal INTEGER, fecha TEXT, autor TEXT, nota TEXT)")
    # Insert legacy rows (without [META])
    for i in range(3):
        cur.execute("INSERT INTO comentario (id_animal, fecha, autor, nota) VALUES (?,?,?,?)", (100+i, '2025-01-0{}'.format(i+1), 'Tester', f'Nota simple {i}'))
    # Row already migrated-like containing [META] should be ignored
    cur.execute("INSERT INTO comentario (id_animal, fecha, autor, nota) VALUES (?,?,?,?,)")
    conn.commit()
    return conn, db_path


def test_migrate_conn_applies_meta():
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    cur.execute("CREATE TABLE comentario (id INTEGER PRIMARY KEY AUTOINCREMENT, id_animal INTEGER, fecha TEXT, autor TEXT, nota TEXT)")
    cur.execute("INSERT INTO comentario (id_animal, fecha, autor, nota) VALUES (1, '2025-02-01', 'Tester', 'Comentario sin meta')")
    cur.execute("INSERT INTO comentario (id_animal, fecha, autor, nota) VALUES (2, '2025-02-02', 'Tester', 'Otro comentario')")
    conn.commit()
    updated = migrate_conn(conn, dry_run=False)
    assert updated == 2, f"Esperaba 2 filas actualizadas, obtuve {updated}"
    cur.execute("SELECT nota FROM comentario")
    rows = [r[0] for r in cur.fetchall()]
    for note in rows:
        human, meta = parse_meta(note)
        assert meta is not None and meta.get('tipo') == 'legacy'


def test_migrate_conn_dry_run():
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    cur.execute("CREATE TABLE comentario (id INTEGER PRIMARY KEY AUTOINCREMENT, id_animal INTEGER, fecha TEXT, autor TEXT, nota TEXT)")
    cur.execute("INSERT INTO comentario (id_animal, fecha, autor, nota) VALUES (1, '2025-02-01', 'Tester', 'Comentario sin meta')")
    conn.commit()
    updated = migrate_conn(conn, dry_run=True)
    assert updated == 0, "Dry-run no debe modificar filas"
    cur.execute("SELECT nota FROM comentario")
    note = cur.fetchone()[0]
    # Sin cambios
    assert '[META]' not in note
