import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_connection

CLASIFICACIONES = {"Crítico", "Alerta", "Óptimo", "Observación"}

with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT codigo, estado, caracteristicas FROM condicion_corporal")
    rows = cur.fetchall()
    updated = 0
    for r in rows:
        codigo, estado, caracteristicas = r[0], r[1], r[2]
        if estado and estado not in ("Activo", "Inactivo"):
            # Mover estado previo a caracteristicas
            nuevo_caract = (caracteristicas or "").strip()
            if nuevo_caract:
                nuevo_caract += f" | Clasificación: {estado}"
            else:
                nuevo_caract = f"Clasificación: {estado}"
            cur.execute("UPDATE condicion_corporal SET caracteristicas = ?, estado = 'Activo' WHERE codigo = ?", (nuevo_caract, codigo))
            updated += 1
    conn.commit()
print(f"Registros actualizados: {updated}")
