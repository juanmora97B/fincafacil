import os
import sys
from typing import List, Dict
import random

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(ROOT, "..", "src"))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from infraestructura.configuracion.configuracion_service import ConfiguracionService  # type: ignore

roles = ["Vaquero", "Operario", "Supervisor", "Veterinario", "Administrador"]


def log(msg: str) -> None:
    print(msg)


def main() -> None:
    log("[SEED] Trabajadores - inicio")
    svc = ConfiguracionService()

    fincas = svc.listar_fincas_para_combo_lotes()
    if not fincas:
        log("✖ No hay fincas activas; ejecute seed_configuracion primero")
        return

    empleados_seed = [
        ("TRAB001", "1001001001", "Carlos", "Gómez", "Vaquero"),
        ("TRAB002", "1001001002", "María", "López", "Operario"),
        ("TRAB003", "1001001003", "Juan", "Pérez", "Supervisor"),
        ("TRAB004", "1001001004", "Ana", "Ramírez", "Veterinario"),
        ("TRAB005", "1001001005", "Luis", "Martínez", "Administrador"),
        ("TRAB006", "1001001006", "Sofía", "Hernández", "Operario"),
        ("TRAB007", "1001001007", "Diego", "Castro", "Vaquero"),
        ("TRAB008", "1001001008", "Elena", "Torres", "Auxiliar"),
    ]

    for codigo, doc, nombres, apellidos, cargo in empleados_seed:
        try:
            if svc.existe_codigo_empleado(codigo) or svc.existe_empleado_por_documento(doc):
                log(f"↪ Empleado existente: {codigo} - {doc}")
                continue
            finca = random.choice(fincas)
            fid_val = finca.get("id")
            if fid_val is None:
                raise ValueError("ID de finca faltante para empleado")
            svc.crear_empleado(
                codigo=codigo,
                numero_identificacion=doc,
                nombres=nombres,
                apellidos=apellidos,
                cargo=cargo,
                id_finca=int(fid_val),
                estado="Activo",
            )
            log(f"✔ Empleado creado: {codigo} - {nombres} {apellidos} ({cargo}) en {finca.get('nombre')}")
        except Exception as e:
            log(f"✖ Error empleado {codigo}: {e}")

    log("[SEED] Trabajadores - completado")


if __name__ == "__main__":
    main()
