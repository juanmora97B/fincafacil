from __future__ import annotations
from typing import Tuple, List
from datetime import date
from src.database.database import get_db_connection

# Repository: ONLY aggregated SELECT queries

def ingresos_animales(fecha_inicio: str, fecha_fin: str) -> float:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COALESCE(SUM(precio_total), 0)
            FROM venta
            WHERE DATE(fecha) BETWEEN ? AND ?
            """,
            (fecha_inicio, fecha_fin),
        )
        return float(cur.fetchone()[0])


def ingresos_leche(fecha_inicio: str, fecha_fin: str) -> float:
    # No tabla de ventas de leche explícita; retornar 0 hasta que exista
    return 0.0


def costos_nomina(fecha_inicio: str, fecha_fin: str) -> float:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COALESCE(SUM(total_pagado), 0)
            FROM pago_nomina
            WHERE DATE(fecha_pago) BETWEEN ? AND ?
            """,
            (fecha_inicio, fecha_fin),
        )
        return float(cur.fetchone()[0])


def costos_insumos(fecha_inicio: str, fecha_fin: str) -> float:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COALESCE(SUM(costo_total), 0)
            FROM movimiento_insumo
            WHERE DATE(fecha_movimiento) BETWEEN ? AND ?
            """,
            (fecha_inicio, fecha_fin),
        )
        return float(cur.fetchone()[0])


def produccion_leche_total(fecha_inicio: str, fecha_fin: str) -> float:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COALESCE(SUM(litros_manana + litros_tarde + litros_noche), 0)
            FROM produccion_leche
            WHERE DATE(fecha) BETWEEN ? AND ?
            """,
            (fecha_inicio, fecha_fin),
        )
        return float(cur.fetchone()[0])


def animales_activos() -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM animal WHERE estado IS NULL OR estado NOT IN ('Vendido','Muerto')")
        return int(cur.fetchone()[0])


def mortalidad_periodo(fecha_inicio: str, fecha_fin: str) -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) FROM muerte
            WHERE DATE(fecha) BETWEEN ? AND ?
            """,
            (fecha_inicio, fecha_fin),
        )
        return int(cur.fetchone()[0])


def gestaciones_periodo(fecha_inicio: str, fecha_fin: str) -> Tuple[int, int]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) FROM servicio
            WHERE DATE(fecha_servicio) BETWEEN ? AND ? AND estado = 'Servida'
            """,
            (fecha_inicio, fecha_fin),
        )
        servidas = int(cur.fetchone()[0])
        cur.execute(
            """
            SELECT COUNT(*) FROM servicio
            WHERE DATE(fecha_parto_real) BETWEEN ? AND ? AND estado = 'Parida'
            """,
            (fecha_inicio, fecha_fin),
        )
        paridas = int(cur.fetchone()[0])
        return servidas, paridas


def promedio_intervalo_partos_dias(fecha_inicio: str, fecha_fin: str) -> float | None:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id_hembra, MIN(fecha_parto_real), MAX(fecha_parto_real)
            FROM servicio
            WHERE fecha_parto_real IS NOT NULL
              AND DATE(fecha_parto_real) BETWEEN ? AND ?
            GROUP BY id_hembra
            """,
            (fecha_inicio, fecha_fin),
        )
        rows = cur.fetchall()
        if not rows:
            return None
        import datetime
        diffs = []
        for _, fmin, fmax in rows:
            try:
                dmin = datetime.date.fromisoformat(fmin)
                dmax = datetime.date.fromisoformat(fmax)
                delta = (dmax - dmin).days
                if delta > 0:
                    diffs.append(delta)
            except Exception:
                pass
        return (sum(diffs) / len(diffs)) if diffs else None


def monthly_sum(table: str, column: str, fecha_inicio: str, fecha_fin: str) -> List[Tuple[str, float]]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT strftime('%Y-%m', fecha) AS ym, SUM({column})
            FROM {table}
            WHERE DATE(fecha) BETWEEN ? AND ?
            GROUP BY ym
            ORDER BY ym
            """,
            (fecha_inicio, fecha_fin),
        )
        return [(r[0], float(r[1]) if r[1] else 0) for r in cur.fetchall()]
