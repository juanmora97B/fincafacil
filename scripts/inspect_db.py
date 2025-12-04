"""Herramienta rápida para ver qué datos hay en la base de datos.
Uso:
  python scripts/inspect_db.py                -> listado de tablas y conteos
  python scripts/inspect_db.py --full         -> muestra hasta 200 filas por tabla
  python scripts/inspect_db.py --table animal -> muestra todas (<=200) o últimas 50 filas de 'animal'
  python scripts/inspect_db.py --search texto -> busca 'texto' en campos tipo texto y muestra coincidencias
Opciones combinables: --table y --full
"""
from __future__ import annotations
import argparse, json, re, sys, os
from typing import Any, Dict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

MAX_FULL = 200
SAMPLE = 50

def list_tables(cur):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [r[0] for r in cur.fetchall()]

def table_info(cur, name):
    cur.execute(f"PRAGMA table_info({name})")
    return [c[1] for c in cur.fetchall()]

def dump_table(cur, name, full=False):
    cols = table_info(cur, name)
    cur.execute(f"SELECT COUNT(*) FROM {name}")
    count = cur.fetchone()[0]
    if full or count <= MAX_FULL:
        cur.execute(f"SELECT * FROM {name}")
        rows = cur.fetchall()
        data = [dict(zip(cols, r)) for r in rows]
    else:
        cur.execute(f"SELECT * FROM {name} ORDER BY ROWID DESC LIMIT {SAMPLE}")
        rows = cur.fetchall()
        data = {"sample_last": [dict(zip(cols, r)) for r in rows], "note": f"Mostrando últimas {SAMPLE} de {count}"}
    return {"columns": cols, "count": count, "data": data}

def search_text(cur, text: str, tables):
    pattern = f"%{text}%"
    results = {}
    for t in tables:
        cols = table_info(cur, t)
        # Construir lista de columnas texto
        cur.execute(f"PRAGMA table_info({t})")
        text_cols = [c[1] for c in cur.fetchall() if c[2] and ('CHAR' in c[2].upper() or 'TEXT' in c[2].upper())]
        if not text_cols:
            continue
        where_parts = [f"{c} LIKE ?" for c in text_cols]
        sql = f"SELECT * FROM {t} WHERE {' OR '.join(where_parts)} LIMIT 100"
        cur.execute(sql, [pattern]*len(text_cols))
        rows = cur.fetchall()
        if rows:
            results[t] = {"columns": cols, "matches": [dict(zip(cols, r)) for r in rows]}
    return results

def main():
    ap = argparse.ArgumentParser(description="Inspección rápida de la BD")
    ap.add_argument('--full', action='store_true', help='Mostrar tablas completas (hasta 200 filas)')
    ap.add_argument('--table', help='Nombre de tabla específica a volcar')
    ap.add_argument('--search', help='Texto a buscar en columnas texto')
    args = ap.parse_args()

    with get_connection() as conn:
        cur = conn.cursor()
        tables = list_tables(cur)
        if args.search:
            data = search_text(cur, args.search, tables)
            print(json.dumps({"search": args.search, "results": data}, ensure_ascii=False, indent=2))
            return
        if args.table:
            if args.table not in tables:
                print(f"Tabla '{args.table}' no existe. Disponible: {', '.join(tables)}")
                return
            info = dump_table(cur, args.table, full=args.full)
            print(json.dumps({args.table: info}, ensure_ascii=False, indent=2))
            return
        # listado general
        snapshot = {}
        for t in tables:
            snapshot[t] = dump_table(cur, t, full=args.full)
        # Minimizar salida si no full: remover data cuando count>0
        if not args.full:
            for t, v in snapshot.items():
                # Para visión rápida remueve datos salvo sample
                if isinstance(v['data'], list) and v['count']>0:
                    v['data'] = f"{v['count']} filas (usar --table {t} para ver detalle)"
            
        print(json.dumps({"tables": snapshot}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
