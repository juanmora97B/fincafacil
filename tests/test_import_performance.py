import importlib
import sys
import time
from pathlib import Path

# Lista de módulos clave a medir. Se pueden añadir más si se expanden los reportes.
TARGET_MODULES = [
    'main',
    'modules.reportes.reportes_main',
    'modules.ventas.ventas_main',
    'modules.reproduccion.reproduccion_main',
    'modules.animales.inventario',
]

# Umbral de tiempo máximo por import (segundos) alineado a requisito (1.5s)
MAX_SECONDS_PER_IMPORT = 1.5

def timed_import(module_name: str):
    # Forzar recarga limpia para una medición más honesta
    if module_name in sys.modules:
        del sys.modules[module_name]
    start = time.perf_counter()
    mod = importlib.import_module(module_name)
    elapsed = time.perf_counter() - start
    return mod, elapsed

def test_import_performance():
    slow = []
    for name in TARGET_MODULES:
        try:
            _, t = timed_import(name)
        except Exception as e:
            raise AssertionError(f'Fallo importando {name}: {e}')
        if t > MAX_SECONDS_PER_IMPORT:
            slow.append((name, t))
    assert not slow, f'Módulos lentos al importar (> {MAX_SECONDS_PER_IMPORT:.1f}s): ' + ', '.join(f'{n}={s:.2f}s' for n, s in slow)
