import re
import sqlite3
from pathlib import Path
from database.database import get_db_connection

LEGACY_RE = re.compile(r"REUBICACIÓN: De '([^']*)' a '([^']*)'\.")
META_RE = re.compile(r"\[META\](\{.*\})", re.DOTALL)

DB_PATH = Path(__file__).parent.parent / "database" / "fincafacil.db"


def parse_reubicacion_from_comment(text: str):
    """
    Returns dict with keys: from_potrero, to_potrero, motivo, autor
    or None if not a reubicacion.
    """
    if not text:
        return None
    m_meta = META_RE.search(text)
    if m_meta:
        try:
            import json
            meta = json.loads(m_meta.group(1))
            if meta.get("tipo") == "reubicacion":
                return {
                    "from_potrero": meta.get("from") or "-",
                    "to_potrero": meta.get("to") or "-",
                    "motivo": meta.get("motivo") or "",
                    "autor": meta.get("autor") or ""
                }
        except Exception:
            pass
    m_leg = LEGACY_RE.search(text)
    if m_leg:
        return {
            "from_potrero": m_leg.group(1) or "-",
            "to_potrero": m_leg.group(2) or "-",
            "motivo": text.split("\n")[0],
            "autor": ""
        }
    return None


def migrate(limit: int | None = None):
    with get_db_connection(str(DB_PATH)) as conn:
        cur = conn.cursor()
        # Ensure table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reubicacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                from_potrero TEXT,
                to_potrero TEXT,
                motivo TEXT,
                autor TEXT,
                FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
            )
        """)
        # Fetch candidate comments
        sql = (
            "SELECT id, animal_id, fecha, comentario FROM comentario "
            "WHERE comentario LIKE '%reubicación%' OR comentario LIKE '%Reubicación%' OR comentario LIKE '%potrero%' OR comentario LIKE '%traslado%' "
            "ORDER BY fecha DESC"
        )
        if limit:
            sql += f" LIMIT {int(limit)}"
        cur.execute(sql)
        rows = cur.fetchall()
        inserted = 0
        for r in rows:
            cid = r[0]
            aid = r[1]
            fecha = r[2]
            texto = r[3]
            data = parse_reubicacion_from_comment(texto)
            if not data:
                continue
            # Deduping: avoid inserting duplicates for the same animal/fecha/from/to
            cur.execute(
                "SELECT 1 FROM reubicacion WHERE animal_id=? AND fecha=? AND COALESCE(from_potrero,'')=? AND COALESCE(to_potrero,'')=?",
                (aid, fecha, str(data["from_potrero"] or ""), str(data["to_potrero"] or ""))
            )
            if cur.fetchone():
                continue
            cur.execute(
                "INSERT INTO reubicacion (animal_id, fecha, from_potrero, to_potrero, motivo, autor) VALUES (?,?,?,?,?,?)",
                (aid, fecha, data["from_potrero"], data["to_potrero"], data["motivo"], data["autor"])
            )
            inserted += 1
        conn.commit()
        print(f"Migración completada. Reubicaciones insertadas: {inserted}")


if __name__ == "__main__":
    import sys
    lim = None
    if len(sys.argv) > 1:
        try:
            lim = int(sys.argv[1])
        except Exception:
            pass
    migrate(limit=lim)
