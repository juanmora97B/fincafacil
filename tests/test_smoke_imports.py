"""Smoke test: importa todos los módulos *_main.py para asegurar que no hay errores de importación.
No ejecuta bucles de GUI ni mainloop; solo verifica que cada módulo carga sin lanzar excepción.
"""
import importlib
import pathlib
import sys

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent / "modules"

# Excluir potencialmente scripts o módulos que disparen procesos largos al importar
EXCLUDE_CONTAINS = {
    # Agrega patrones si algún módulo requiere entorno externo intenso
}

def _es_main_py(path: pathlib.Path) -> bool:
    return path.name.endswith("_main.py")

def _ruta_a_modulo(path: pathlib.Path) -> str:
    # path relativo a carpeta 'modules'
    rel = path.relative_to(BASE_DIR)
    parts = ["modules"] + list(rel.with_suffix("").parts)
    return ".".join(parts)

def test_import_all_main_modules():
    assert BASE_DIR.exists(), f"Directorio modules no encontrado: {BASE_DIR}"
    fallos = []
    for p in BASE_DIR.rglob("*_main.py"):
        if any(substr in str(p) for substr in EXCLUDE_CONTAINS):
            continue
        modulo = _ruta_a_modulo(p)
        try:
            importlib.import_module(modulo)
        except Exception as e:
            fallos.append((modulo, repr(e)))
    assert not fallos, f"Fallos al importar módulos: {fallos}"  
