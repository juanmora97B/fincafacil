"""Exporta tablas a CSV o JSON.
Uso:
  python scripts/export_tables.py --tables finca,animal --format csv
  python scripts/export_tables.py --all --format json
  python scripts/export_tables.py --tables origen --where "estado='Activo'" --limit 100
Por defecto escribe en carpeta 'exports/'.
"""
from __future__ import annotations
import argparse, csv, json, os, datetime
from typing import List
from database.database import get_db_connection

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')

def list_tables(cur):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [r[0] for r in cur.fetchall()]

def fetch(cur, table, where=None, limit=None):
    cur.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cur.fetchall()]
    sql = f"SELECT * FROM {table}"
    if where:
        sql += f" WHERE {where}"
    if limit:
        sql += f" LIMIT {int(limit)}"
    cur.execute(sql)
    rows = cur.fetchall()
    return cols, [dict(zip(cols, r)) for r in rows]

def export_csv(path, cols, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def export_json(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

def main():
    ap = argparse.ArgumentParser(description="Exporta tablas a CSV/JSON")
    ap.add_argument('--tables', help='Lista de tablas separadas por coma')
    ap.add_argument('--all', action='store_true', help='Exportar todas las tablas')
    ap.add_argument('--format', choices=['csv','json'], default='csv')
    ap.add_argument('--where', help='Filtro WHERE SQL simple (ej. estado="Activo")')
    ap.add_argument('--limit', help='Límite de filas')
    ap.add_argument('--prefix', help='Prefijo de archivo (default timestamp)')
    args = ap.parse_args()

    os.makedirs(EXPORT_DIR, exist_ok=True)
    ts = args.prefix or datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    with get_db_connection() as conn:
        cur = conn.cursor()
        available = list_tables(cur)
        if args.all:
            tables = available
        elif args.tables:
            requested = [t.strip() for t in args.tables.split(',') if t.strip()]
            missing = [t for t in requested if t not in available]
            if missing:
                print(f"Tablas inexistentes: {', '.join(missing)}")
                return
            tables = requested
        else:
            print("Debe usar --tables o --all")
            return
        for t in tables:
            cols, rows = fetch(cur, t, where=args.where, limit=args.limit)
            filename = f"{ts}_{t}.{args.format}"
            path = os.path.join(EXPORT_DIR, filename)
            if args.format == 'csv':
                export_csv(path, cols, rows)
            else:
                export_json(path, rows)
            print(f"Exportado {t} -> {path} ({len(rows)} filas)")

if __name__ == '__main__':
    main()
