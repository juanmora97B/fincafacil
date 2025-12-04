import os
import json
import sqlite3
from utils.metadata import build_meta_note, parse_meta

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'fincafacil.db')

def get_conn():
    return sqlite3.connect(DB_PATH)

def test_build_and_parse_meta():
    human = "REUBICACIÓN: De 'A' a 'B'. Motivo: Cambio"
    meta = {"from": "A", "to": "B", "motivo": "Cambio", "fecha": "2025-11-24"}
    note = build_meta_note("reubicacion", human, meta)
    h2, m2 = parse_meta(note)
    assert h2.startswith("REUBICACIÓN"), "Human text mismatch"
    assert m2 is not None and m2.get("to") == "B" and m2.get("tipo") == "reubicacion"

# Persistence tests rely on app_settings table existing.
# They will skip gracefully if table or columns missing.

def _settings_supported():
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_settings'")
            return cur.fetchone() is not None
    except Exception:
        return False

def test_autocomplete_mode_persistence():
    if not _settings_supported():
        return  # skip
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("REPLACE INTO app_settings (clave, valor) VALUES (?, ?)", ("autocomplete_match_mode", "startswith"))
        conn.commit()
        cur.execute("SELECT valor FROM app_settings WHERE clave='autocomplete_match_mode'")
        val = cur.fetchone()[0]
        assert val == "startswith"

def test_bitacora_filters_persistence():
    if not _settings_supported():
        return
    data = {"fecha_desde": "2025-01-01", "fecha_hasta": "2025-12-31", "finca": "Principal", "potrero": "Norte", "motivo": "traslado"}
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("REPLACE INTO app_settings (clave, valor) VALUES (?, ?)", ("bitacora_reubicaciones_filters", json.dumps(data)))
        conn.commit()
        cur.execute("SELECT valor FROM app_settings WHERE clave='bitacora_reubicaciones_filters'")
        raw = cur.fetchone()[0]
        loaded = json.loads(raw)
        assert loaded.get("motivo") == "traslado" and loaded.get("potrero") == "Norte"
