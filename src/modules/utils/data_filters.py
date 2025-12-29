"""Utilities for finca-scoped data retrieval.

Functions centralize the pattern of detecting foreign key column names
(id_finca vs finca_id) and returning filtered lists.

REFACTOR FASE 7.5: Usa inyección de DbConnectionService en lugar de acceso directo a BD.
"""
from typing import List, Tuple, Dict, Optional
import sqlite3
from database.services import get_db_service

FK_CANDIDATES = ["id_finca", "finca_id"]

def _detect_fk(cursor: sqlite3.Cursor, table: str) -> Optional[str]:
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cursor.fetchall()]
        for cand in FK_CANDIDATES:
            if cand in cols:
                return cand
    except Exception:
        return None
    return None

def fetch_by_finca(table: str, finca_id: int, order_col: str = "nombre", extra_where: str = "") -> List[Tuple[int,str]]:
    """Return (id, nombre) rows for table limited by finca_id if FK detected; fallback to all."""
    db_service = get_db_service()
    with db_service.connection() as conn:
        cur = conn.cursor()
        fk = _detect_fk(cur, table)
        where_fk = f"{fk} = ?" if fk else "1=1"
        where_extra = f" AND {extra_where}" if extra_where else ""
        sql = f"SELECT id, nombre FROM {table} WHERE {where_fk}{where_extra} ORDER BY {order_col}"
        params = (finca_id,) if fk else ()
        cur.execute(sql, params)
        return cur.fetchall()

def fetch_animals_for_parents(finca_id: int) -> Dict[str,List[Tuple[int,str,str]]]:
    """Return dict with 'madres' and 'padres' filtered by finca if possible."""
    db_service = get_db_service()
    with db_service.connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, codigo, nombre FROM animal WHERE estado='Activo' AND sexo='Hembra' AND id_finca=?", (finca_id,))
            madres = cur.fetchall()
            cur.execute("SELECT id, codigo, nombre FROM animal WHERE estado='Activo' AND sexo='Macho' AND id_finca=?", (finca_id,))
            padres = cur.fetchall()
        except Exception:
            madres, padres = [], []
    return {"madres": madres, "padres": padres}

__all__ = ["fetch_by_finca", "fetch_animals_for_parents"]
