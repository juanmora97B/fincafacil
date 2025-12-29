import os
import sys
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(ROOT, "..", "src"))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from infraestructura.configuracion.configuracion_service import ConfiguracionService  # type: ignore
from infraestructura.animales.animal_service import AnimalService  # type: ignore
from database.database import ejecutar_consulta  # type: ignore


def log(msg: str) -> None:
    print(msg)


def detectar_columna_finca() -> Optional[str]:
    try:
        cols = ejecutar_consulta("PRAGMA table_info(animal)", (), fetch=True) or []
        names = {c.get("name") for c in cols}
        if "finca_id" in names:
            return "finca_id"
        if "id_finca" in names:
            return "id_finca"
        return None
    except Exception:
        return None


def as_int(value: Any) -> int:
    """Convierte a int con validación explícita (evita None)."""
    if value is None:
        raise ValueError("Valor None no convertible a int")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    raise ValueError(f"Tipo no convertible a int: {type(value).__name__}")


def main() -> None:
    log("[SEED] Animales - inicio")
    cfg = ConfiguracionService()
    svc = AnimalService()

    fincas = cfg.listar_fincas_para_combo_lotes()
    lotes = cfg.listar_lotes_activos()
    sectores = cfg.listar_sectores_activos()

    if not fincas or not lotes or not sectores:
        log("✖ Falta configuración base (fincas/lotes/sectores). Ejecute seed_configuracion primero.")
        return

    # Mapear por finca
    lotes_by_finca: Dict[int, List[Dict]] = {}
    for l in lotes:
        fid_val = l.get("finca_id") or l.get("id_finca")
        if fid_val is None:
            # saltar lotes sin referencia de finca
            continue
        fid_int = as_int(fid_val)
        lotes_by_finca.setdefault(fid_int, []).append(l)
    sectores_by_finca: Dict[int, List[Dict]] = {}
    for s in sectores:
        fid_val = s.get("finca_id") or s.get("id_finca")
        if fid_val is None:
            continue
        fid_int = as_int(fid_val)
        sectores_by_finca.setdefault(fid_int, []).append(s)

    finca_col = detectar_columna_finca()

    # Semilla de animales (24-30)
    nombres = [
        "Lucero", "Estrella", "Fuego", "Bruma", "Sol", "Luna", "Rayo", "Nieve",
        "Sombra", "Rocío", "Trueno", "Ceniza", "Cobre", "Perla", "Coral", "Ágata",
        "Pampa", "Selva", "Sierra", "Rio", "Valle", "Monte", "Vega", "Aroma",
    ]

    count_target = 24
    random.shuffle(nombres)

    # Generar fechas de nacimiento realistas (1-8 años)
    def fecha_nacimiento_aleatoria() -> str:
        dias = random.randint(365, 365 * 8)
        d = datetime.today() - timedelta(days=dias)
        return d.strftime("%Y-%m-%d")

    created = 0
    for idx in range(count_target):
        try:
            finca = random.choice(fincas)
            fid = as_int(finca.get("id"))
            lotes_f = lotes_by_finca.get(fid) or []
            sectores_f = sectores_by_finca.get(fid) or []
            if not lotes_f or not sectores_f:
                # saltar si finca no tiene lotes/sectores
                continue
            lote = random.choice(lotes_f)
            sector = random.choice(sectores_f)

            codigo = f"AN{idx+1:04d}"
            sexo = random.choice(["Macho", "Hembra"])  # validado por AnimalService
            nombre = nombres[idx % len(nombres)]
            nacimiento = fecha_nacimiento_aleatoria()

            # Idempotencia: si existe por código, saltar
            if svc.obtener_animal_por_codigo(codigo):
                log(f"↪ Animal existente: {codigo}")
                continue

            data = {
                "codigo": codigo,
                "nombre": nombre,
                "sexo": sexo,
                "fecha_nacimiento": nacimiento,
                "estado": "Activo",
                "lote_id": as_int(lote.get("id")),
                "id_sector": as_int(sector.get("id")),  # campo alterno según esquema
            }
            if finca_col:
                data[finca_col] = fid

            svc.registrar_animal(data)
            created += 1
            log(f"✔ Animal creado: {codigo} - {nombre} ({sexo}) en {finca.get('nombre')}")
        except Exception as e:
            log(f"✖ Error animal índice {idx}: {e}")

    log(f"[SEED] Animales - completado (creados: {created})")


if __name__ == "__main__":
    main()
