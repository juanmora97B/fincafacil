import os, sqlite3
from datetime import datetime
from utils.metadata import build_meta_note, parse_meta

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'fincafacil.db')

def get_conn():
    return sqlite3.connect(DB_PATH)

def _comentarios_supported():
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comentario'")
            return cur.fetchone() is not None
    except Exception:
        return False


def test_inventario_comment_metadata_build_and_parse():
    # Pure metadata build/parse validation for inventario comment type
    resumen = "Peso actualizado correctamente"
    meta = {"codigo": "ANM001", "finca": "Principal", "fecha": "2025-11-24", "contexto": "inventario"}
    note = build_meta_note("comentario_inventario", resumen, meta)
    h, m = parse_meta(note)
    assert h.startswith("Peso"), "Human text truncated incorrectly"
    assert m is not None and m.get("tipo") == "comentario_inventario" and m.get("contexto") == "inventario"


def test_inventario_comment_metadata_db_roundtrip():
    if not _comentarios_supported():
        return  # skip gracefully
    resumen = "Actualización inventario: condición OK"
    meta = {"codigo": "ANMTEST", "finca": "Secundaria", "fecha": datetime.now().strftime('%Y-%m-%d'), "contexto": "inventario"}
    note = build_meta_note("comentario_inventario", resumen, meta)
    with get_conn() as conn:
        cur = conn.cursor()
        # Insert dummy animal if not exists
        cur.execute("CREATE TABLE IF NOT EXISTS animal (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE)")
        cur.execute("INSERT OR IGNORE INTO animal (codigo) VALUES (?)", (meta["codigo"],))
        cur.execute("SELECT id FROM animal WHERE codigo=?", (meta["codigo"],))
        animal_id = cur.fetchone()[0]
        cur.execute("CREATE TABLE IF NOT EXISTS comentario (id INTEGER PRIMARY KEY AUTOINCREMENT, id_animal INTEGER, fecha TEXT, autor TEXT, nota TEXT)")
        cur.execute("INSERT INTO comentario (id_animal, fecha, autor, nota) VALUES (?,?,?,?)", (animal_id, meta["fecha"], "Test", note))
        conn.commit()
        cur.execute("SELECT nota FROM comentario WHERE id_animal=? ORDER BY id DESC LIMIT 1", (animal_id,))
        stored = cur.fetchone()[0]
    h2, m2 = parse_meta(stored)
    assert m2 is not None and m2.get("tipo") == "comentario_inventario" and m2.get("codigo") == meta["codigo"]
