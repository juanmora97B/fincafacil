"""Simple migrations runner.
Executes numbered migration scripts in order.
Usage: python scripts/run_migrations.py
"""
import pathlib
import importlib.util

def discover_migrations():
    mig_dir = pathlib.Path(__file__).parent / 'migrations'
    scripts = []
    for p in mig_dir.glob('*.py'):
        name = p.stem
        # Aceptar prefijo numérico inicial (con posibles sufijos alfanuméricos: 008B, 010, etc.)
        # Extraer solo dígitos consecutivos desde inicio
        prefix = ''
        for ch in name:
            if ch.isdigit():
                prefix += ch
            else:
                break
        if prefix:
            # Excluir migración obsoleta que causa conflictos (008_allow_delete_finca reemplazada por 008B/008C/008D)
            if name != '008_allow_delete_finca':
                scripts.append((int(prefix), p))
    # Ordenar por número y luego por nombre completo para estabilidad
    scripts.sort(key=lambda t: (t[0], t[1].name))
    # Devolver solo Path
    scripts = [t[1] for t in scripts]
    return scripts

def _load_module_from_path(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def run_all():
    for script_path in discover_migrations():
        print(f'➡️ Running migration {script_path.stem} ...')
        mod = _load_module_from_path(script_path)
        if hasattr(mod, 'run'):
            mod.run()
        print(f'✔️ Finished {script_path.stem}')

if __name__ == '__main__':
    run_all()
    print('🎉 All migrations executed.')
