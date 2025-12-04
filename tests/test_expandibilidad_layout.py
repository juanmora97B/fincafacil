import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT / 'modules'

# Buscamos frames scrollables principales con pack(fill="both", expand=True)
FRAME_REGEX = re.compile(r"CTk(ScrollableFrame|Frame)\([^)]*\)")
PACK_REGEX = re.compile(r"pack\([^)]*fill=\"both\"[^)]*expand=True[^)]*\)")

MAX_ALLOWED_PADX = 10


def test_expandibilidad_frames():
    """Verifica que frames principales mantienen expandibilidad y padding horizontal <= MAX_ALLOWED_PADX.
    Simplificación: se analiza línea a línea; si el pack está en la misma línea con padx, evaluamos su valor.
    """
    violations = []
    for py_file in MODULES_DIR.rglob('*.py'):
        if py_file.name.startswith('__'):
            continue
        try:
            lines = py_file.read_text(encoding='utf-8').splitlines()
        except Exception:
            continue
        for line in lines:
            if 'CTkScrollableFrame' in line or 'CTkFrame' in line:
                # Buscar pack en misma línea (simplificado; muchas llamadas están en la misma línea)
                if 'pack(' in line and 'fill="both"' in line and 'expand=True' in line:
                    # Extraer padx si existe
                    m = re.search(r'padx=([0-9]+)', line)
                    if m:
                        val = int(m.group(1))
                        if val > MAX_ALLOWED_PADX:
                            violations.append(f"{py_file.name}: padx={val} -> {line.strip()}")
    assert not violations, 'Frames con padding horizontal excesivo (>10): ' + '; '.join(violations)
