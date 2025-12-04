"""Pruebas básicas de la capa de base de datos.
Valida que el esquema inicial contenga columnas y objetos críticos.
"""
import sqlite3
from database.database import inicializar_base_datos, get_db_connection


def test_sector_tiene_finca_id():
    inicializar_base_datos()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(sector)")
        cols = [c[1] for c in cur.fetchall()]
    assert "finca_id" in cols, "La tabla sector debe incluir finca_id"


def test_trigger_animal_update_existe():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name='trg_animal_update'")
        trigger = cur.fetchone()
    assert trigger is not None, "Debe existir trigger trg_animal_update"


def test_indice_nomina_compuesto():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_pago_nomina_empleado_periodo'")
        idx = cur.fetchone()
    assert idx is not None, "Debe existir índice compuesto de nómina"
