import os
from pathlib import Path

# Directorio raíz del proyecto (este archivo está en tests/)
ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT / 'modules'

# Patrones simples a detectar. Centrados en layouts expansibles que antes tenían padx=20.
PATTERN = 'padx=20'

# Whitelist opcional si algún archivo debe conservar padding amplio por diseño (vacía por ahora)
WHITELIST = set()


def test_no_residual_large_padding():
    """Falla si existe alguna línea con fill="both" expand=True y padding horizontal 20.
    Estrictamente buscamos coincidencia conjunta en una misma línea para evitar falsos positivos.
    """
    offending = []
    for py_file in MODULES_DIR.rglob('*.py'):
        if py_file.name.startswith('__'):
            continue
        rel = py_file.relative_to(ROOT).as_posix()
        if rel in WHITELIST:
            continue
        try:
            for line in py_file.read_text(encoding='utf-8').splitlines():
                l = line.replace(' ', '')  # normalizar espacios para patrones compactos
                if 'fill="both"' in l and 'expand=True' in l and 'padx=20' in l:
                    offending.append(rel)
                    break
        except Exception:
            continue
    assert not offending, 'Archivos con padding expansible residual (fill="both" expand=True padx=20): ' + ', '.join(offending)
