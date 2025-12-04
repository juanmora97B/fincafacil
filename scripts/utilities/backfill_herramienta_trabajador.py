"""
Backfill: asigna id_trabajador en herramientas usando el texto de 'responsable'.
- Busca empleados activos cuyo nombre completo (nombres + apellidos) coincida (normalizado)
- No toca registros donde responsable es NULL o 'Bodega'
- Reporta coincidencias múltiples o no encontradas
"""
import sys
from pathlib import Path
import unicodedata

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import get_connection


def _normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    s = ' '.join(s.split())
    return s


def main():
    total = 0
    asignados = 0
    no_encontrados = []
    ambiguos = []

    with get_connection() as conn:
        cur = conn.cursor()
        # Cargar mapa de empleados activos normalizados
        cur.execute("""
            SELECT rowid, nombres, apellidos
            FROM empleado
            WHERE estado_actual = 'Activo' OR estado_actual IS NULL OR estado_actual = ''
        """)
        empleados = cur.fetchall()
        nombre_map = {}
        for row in empleados:
            rid = row[0]
            nombres = row[1] or ""
            apellidos = row[2] or ""
            full = f"{nombres} {apellidos}".strip()
            key = _normalize_text(full)
            if key:
                nombre_map.setdefault(key, []).append(rid)

        # Herramientas con responsable textual y sin id_trabajador
        cur.execute(
            """
            SELECT id, codigo, nombre, responsable
            FROM herramienta
            WHERE (id_trabajador IS NULL OR id_trabajador = '')
              AND responsable IS NOT NULL
              AND TRIM(LOWER(responsable)) <> 'bodega'
            """
        )
        herramientas = cur.fetchall()
        total = len(herramientas)

        for h in herramientas:
            hid, codigo, nombre, resp = h
            key = _normalize_text(resp)
            if not key:
                continue
            if key in nombre_map:
                ids = nombre_map[key]
                if len(ids) == 1:
                    cur.execute("UPDATE herramienta SET id_trabajador = ? WHERE id = ?", (ids[0], hid))
                    asignados += 1
                else:
                    ambiguos.append((codigo, nombre, resp, ids))
            else:
                no_encontrados.append((codigo, nombre, resp))

        conn.commit()

    print("\n========== Backfill id_trabajador en herramienta ==========")
    print(f"Total candidatas: {total}")
    print(f"Asignadas: {asignados}")
    if ambiguos:
        print(f"Ambiguas: {len(ambiguos)} (requiere intervención)")
        for (codigo, nombre, resp, ids) in ambiguos[:10]:
            print(f" - {codigo} - {nombre} : '{resp}' -> multiples empleados {ids}")
        if len(ambiguos) > 10:
            print(f"   ... y {len(ambiguos)-10} más")
    if no_encontrados:
        print(f"No encontradas: {len(no_encontrados)}")
        for (codigo, nombre, resp) in no_encontrados[:10]:
            print(f" - {codigo} - {nombre} : '{resp}'")
        if len(no_encontrados) > 10:
            print(f"   ... y {len(no_encontrados)-10} más")
    print("==========================================================\n")


if __name__ == '__main__':
    main()
