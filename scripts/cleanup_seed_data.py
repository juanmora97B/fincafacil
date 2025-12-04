"""Script de limpieza segura de datos semilla e inactivos.
Modo por defecto (dry-run): solo muestra recomendaciones.
Uso:
  python scripts/cleanup_seed_data.py                 -> análisis y recomendaciones
  python scripts/cleanup_seed_data.py --apply         -> aplica eliminaciones recomendadas
  python scripts/cleanup_seed_data.py --only finca,procedencia  -> limitar categorías
  python scripts/cleanup_seed_data.py --export recomendados.csv  -> exporta listado a CSV
Categorías soportadas: finca, origen, procedencia_vendedor, potrero_lote_grupo, animales_vacios
"""
from __future__ import annotations
import argparse, csv, datetime, sys
from typing import List, Dict, Any
from database import get_connection

CATEGORIES = {"finca", "origen", "procedencia_vendedor", "potrero_lote_grupo", "animales_vacios"}

class Recommendation:
    def __init__(self, category: str, table: str, id_field: str, row_id: Any, reason: str):
        self.category = category
        self.table = table
        self.id_field = id_field
        self.row_id = row_id
        self.reason = reason
    def to_dict(self):
        return {"category": self.category, "table": self.table, "id_field": self.id_field, "row_id": self.row_id, "reason": self.reason}

def fetch_all(cur, sql, params=None):
    cur.execute(sql, params or [])
    return cur.fetchall()

def analyze_fincas(cur) -> List[Recommendation]:
    recs = []
    # Inactivas o eliminadas y sin referencias en animal / insumo / potrero
    cur.execute("""
        SELECT f.id_finca, f.nombre, f.estado,
               (SELECT COUNT(*) FROM animal a WHERE a.id_finca = f.id_finca) as c_animales,
               (SELECT COUNT(*) FROM insumo i WHERE i.id_finca = f.id_finca) as c_insumos,
               (SELECT COUNT(*) FROM potrero p WHERE p.id_finca = f.id_finca) as c_potreros
        FROM finca f
        WHERE LOWER(f.estado) IN ('inactivo','inactiva','eliminado','eliminada')
    """)
    for row in cur.fetchall():
        id_finca, nombre, estado, c_animales, c_insumos, c_potreros = row
        if c_animales == 0 and c_insumos == 0 and c_potreros == 0:
            recs.append(Recommendation("finca", "finca", "id_finca", id_finca, f"Finca '{nombre}' estado={estado} sin referencias"))
    return recs

def analyze_origen(cur) -> List[Recommendation]:
    recs = []
    # Orígenes no referenciados en animal
    cur.execute("""
        SELECT o.id_origen, o.nombre,
               (SELECT COUNT(*) FROM animal a WHERE a.origen_id = o.id_origen) as c_animales
        FROM origen o
    """)
    for row in cur.fetchall():
        id_origen, nombre, c_animales = row
        if c_animales == 0:
            recs.append(Recommendation("origen", "origen", "id_origen", id_origen, f"Origen '{nombre}' sin uso en animales"))
    return recs

def analyze_procedencia_vendedor(cur) -> List[Recommendation]:
    recs = []
    # Si ya consolidamos a origen, estas tablas pueden tener registros semilla sin uso
    for table, id_field in [("procedencia","id_procedencia"),("vendedor","id_vendedor")]:
        cur.execute(f"""
            SELECT t.{id_field}, t.nombre,
                   (SELECT COUNT(*) FROM animal a WHERE a.{id_field} = t.{id_field}) as c_animales
            FROM {table} t
        """)
        for row in cur.fetchall():
            _id, nombre, c_animales = row
            if c_animales == 0:
                recs.append(Recommendation("procedencia_vendedor", table, id_field, _id, f"{table} '{nombre}' sin referencia en animal tras consolidación"))
    return recs

def analyze_potrero_lote_grupo(cur) -> List[Recommendation]:
    recs = []
    # Potreros, lotes, grupos sin animales
    specs = [
        ("potrero","id_potrero"),
        ("lote","id_lote"),
        ("grupo","id_grupo")
    ]
    for table, id_field in specs:
        cur.execute(f"""
            SELECT t.{id_field}, t.nombre,
                   (SELECT COUNT(*) FROM animal a WHERE a.{id_field} = t.{id_field}) as c_animales
            FROM {table} t
        """)
        for row in cur.fetchall():
            _id, nombre, c_animales = row
            if c_animales == 0:
                recs.append(Recommendation("potrero_lote_grupo", table, id_field, _id, f"{table} '{nombre}' sin animales asociados"))
    return recs

def analyze_animales_vacios(cur) -> List[Recommendation]:
    recs = []
    # Animales sin finca y sin eventos (si existieran) => candidatos a limpieza (raro al inicio)
    cur.execute("""
        SELECT a.id_animal, a.nombre, a.id_finca
        FROM animal a
        WHERE a.id_finca IS NULL
    """)
    for row in cur.fetchall():
        id_animal, nombre, id_finca = row
        recs.append(Recommendation("animales_vacios", "animal", "id_animal", id_animal, f"Animal '{nombre}' sin finca asignada"))
    return recs

ANALYZERS = {
    "finca": analyze_fincas,
    "origen": analyze_origen,
    "procedencia_vendedor": analyze_procedencia_vendedor,
    "potrero_lote_grupo": analyze_potrero_lote_grupo,
    "animales_vacios": analyze_animales_vacios,
}

def apply_deletions(cur, recs: List[Recommendation]):
    # Orden por seguridad: animales -> referencias -> finca
    order_priority = {"animales_vacios":1, "potrero_lote_grupo":2, "procedencia_vendedor":3, "origen":4, "finca":5}
    for r in sorted(recs, key=lambda x: order_priority.get(x.category, 99)):
        sql = f"DELETE FROM {r.table} WHERE {r.id_field} = ?"
        cur.execute(sql, (r.row_id,))

def export_csv(path: str, recs: List[Recommendation]):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=["category","table","id_field","row_id","reason"])
        w.writeheader()
        for r in recs:
            w.writerow(r.to_dict())

def main():
    ap = argparse.ArgumentParser(description="Limpieza segura de datos semilla/inactivos")
    ap.add_argument('--apply', action='store_true', help='Aplica las eliminaciones recomendadas')
    ap.add_argument('--only', help='Lista de categorías separadas por coma')
    ap.add_argument('--export', help='Ruta CSV para exportar recomendaciones')
    args = ap.parse_args()

    selected = CATEGORIES
    if args.only:
        requested = set(s.strip() for s in args.only.split(',') if s.strip())
        invalid = requested - CATEGORIES
        if invalid:
            print(f"Categorías inválidas: {', '.join(invalid)}")
            print(f"Válidas: {', '.join(sorted(CATEGORIES))}")
            sys.exit(1)
        selected = requested

    recommendations: List[Recommendation] = []
    with get_connection() as conn:
        cur = conn.cursor()
        for cat in sorted(selected):
            recs = ANALYZERS[cat](cur)
            recommendations.extend(recs)
        if args.export:
            export_csv(args.export, recommendations)
        print("Resumen recomendaciones:")
        for r in recommendations:
            print(f" - [{r.category}] {r.table}.{r.id_field}={r.row_id}: {r.reason}")
        print(f"Total: {len(recommendations)}")
        if args.apply:
            if not recommendations:
                print("Nada que eliminar.")
                return
            confirm = 'S'
            # Podríamos pedir confirmación, pero para scripting se asume S
            apply_deletions(cur, recommendations)
            conn.commit()
            print("Eliminaciones aplicadas.")
        else:
            print("(Dry-run) No se eliminó nada. Use --apply para ejecutar.")
            if not args.export:
                print("Puede exportar con --export limpieza.csv")

if __name__ == '__main__':
    main()
