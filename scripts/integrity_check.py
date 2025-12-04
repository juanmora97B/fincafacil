"""Chequeo de integridad y consistencia referencial extendido.
Uso:
  python scripts/integrity_check.py                 -> reporte completo
  python scripts/integrity_check.py --json          -> salida JSON
  python scripts/integrity_check.py --focus animal  -> analizar solo categoría
Categorías: animal, finca, origen, estructura
"""
from __future__ import annotations
import argparse, json
from typing import Dict, Any
from database.database import get_db_connection

CATEGORIES = {"animal","finca","origen","estructura"}

def check_finca(cur):
    cur.execute("""
        SELECT f.id_finca, f.nombre, f.estado,
               (SELECT COUNT(*) FROM animal a WHERE a.id_finca = f.id_finca) as c_animales,
               (SELECT COUNT(*) FROM potrero p WHERE p.id_finca = f.id_finca) as c_potreros
        FROM finca f
    """)
    rows = cur.fetchall()
    issues = []
    for r in rows:
        id_finca,nombre,estado,c_animales,c_potreros = r
        if estado.lower() in {"inactivo","inactiva","eliminado","eliminada"} and (c_animales>0 or c_potreros>0):
            issues.append({"type":"finca_inactiva_con_referencias","id_finca":id_finca,"nombre":nombre,"estado":estado,"animales":c_animales,"potreros":c_potreros})
    return {"total":len(rows),"issues":issues}

def check_animal(cur):
    issues = []
    # Animales sin finca
    cur.execute("SELECT id_animal, nombre FROM animal WHERE id_finca IS NULL")
    for r in cur.fetchall():
        issues.append({"type":"animal_sin_finca","id_animal":r[0],"nombre":r[1]})
    # Animales con origen inexistente
    cur.execute("SELECT a.id_animal, a.nombre FROM animal a LEFT JOIN origen o ON a.origen_id = o.id_origen WHERE a.origen_id IS NOT NULL AND o.id_origen IS NULL")
    for r in cur.fetchall():
        issues.append({"type":"animal_origen_inexistente","id_animal":r[0],"nombre":r[1]})
    return {"issues":issues}

def check_origen(cur):
    issues = []
    # Orígenes duplicados por nombre
    cur.execute("SELECT nombre, COUNT(*) c FROM origen GROUP BY nombre HAVING c>1")
    for r in cur.fetchall():
        issues.append({"type":"origen_nombre_duplicado","nombre":r[0],"duplicados":r[1]})
    return {"issues":issues}

def check_estructura(cur):
    issues = []
    # Columnas esperadas en animal
    expected_cols = {"id_animal","nombre","id_finca","origen_id"}
    cur.execute("PRAGMA table_info(animal)")
    cols = {c[1] for c in cur.fetchall()}
    faltantes = expected_cols - cols
    if faltantes:
        issues.append({"type":"animal_columnas_faltantes","faltan":sorted(faltantes)})
    return {"issues":issues}

CHECKERS = {
    "finca": check_finca,
    "animal": check_animal,
    "origen": check_origen,
    "estructura": check_estructura,
}

def run_checks(focus=None):
    with get_db_connection() as conn:
        cur = conn.cursor()
        result = {}
        targets = [focus] if focus else sorted(CATEGORIES)
        for cat in targets:
            result[cat] = CHECKERS[cat](cur)
        return result

def main():
    ap = argparse.ArgumentParser(description="Chequeo de integridad referencial y estructura")
    ap.add_argument('--json', action='store_true', help='Salida JSON')
    ap.add_argument('--focus', choices=list(CATEGORIES), help='Analizar solo una categoría')
    args = ap.parse_args()

    data = run_checks(focus=args.focus)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for cat, info in data.items():
            print(f"[{cat}]")
            if 'total' in info:
                print(f" total filas: {info['total']}")
            if info.get('issues'):
                for issue in info['issues']:
                    print(f"  - {issue['type']}: {issue}")
            else:
                print("  sin issues")

if __name__ == '__main__':
    main()
