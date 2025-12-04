"""
Script para actualizar imports a la nueva estructura
FASE 5: Actualizar todos los imports
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patrones de reemplazo de imports
IMPORT_REPLACEMENTS = [
    # Database
    (r'from database\.database import get_db_connection', 'from database import get_connection'),
    (r'from database import db\b', 'from database import db'),
    (r'import database\.database', 'from database import db'),
    
    # Utils - Validadores
    (r'from modules\.utils\.validaciones import', 'from src.utils.validators import'),
    (r'from modules\.utils\.validators import', 'from src.utils.validators import'),
    (r'from modules\.utils import validaciones', 'from src.utils import validators'),
    (r'from modules\.utils import validators', 'from src.utils import validators'),
    
    # Utils - Logger
    (r'from modules\.utils\.logger import setup_logger, get_logger', 'from modules.utils.logger import setup_logger, get_logger'),
    (r'from modules\.utils\.logger import get_logger', 'from modules.utils.logger import setup_logger'),
    
    # Core
    (r'from src\.core\.exceptions import', 'from src.core.exceptions import'),
    
    # Database connection context
    (r'with get_db_connection\(\) as conn:', 'with get_connection() as conn:'),
    (r'with get_db_connection\(.*?\) as conn:', 'with get_connection() as conn:'),
]

# Archivos a ignorar
IGNORE_PATTERNS = [
    '__pycache__',
    '.venv',
    'venv',
    '.git',
    'dist',
    'build',
    '.pytest_cache',
    '.pyc',
]


def should_process(file_path: Path) -> bool:
    """Verifica si el archivo debe ser procesado"""
    path_str = str(file_path)
    
    # Ignorar ciertos patrones
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return False
    
    # Solo archivos .py
    return file_path.suffix == '.py'


def update_file(filepath: Path) -> Tuple[bool, List[str]]:
    """
    Actualiza imports en un archivo
    
    Returns:
        (actualizado: bool, cambios: List[str])
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        cambios = []
        
        # Aplicar reemplazos
        for pattern, replacement in IMPORT_REPLACEMENTS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                cambios.append(f"  ✓ {pattern} → {replacement}")
                content = new_content
        
        # Si hubo cambios, guardar
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True, cambios
        
        return False, []
        
    except Exception as e:
        print(f"❌ Error en {filepath}: {e}")
        return False, [f"ERROR: {e}"]


def main():
    """Ejecuta actualización de imports"""
    base_dir = Path(__file__).parent.parent
    
    print("=" * 70)
    print("  ACTUALIZACIÓN DE IMPORTS - FincaFacil")
    print("=" * 70)
    print()
    
    updated_files = []
    skipped_files = 0
    errors = []
    
    # Encontrar todos los archivos .py
    py_files = list(base_dir.rglob("*.py"))
    print(f"📁 Encontrados {len(py_files)} archivos Python")
    print()
    
    for idx, py_file in enumerate(py_files, 1):
        # Mostrar progreso
        if idx % 10 == 0:
            print(f"  Procesando: {idx}/{len(py_files)}...", end='\r')
        
        if not should_process(py_file):
            skipped_files += 1
            continue
        
        actualizado, cambios = update_file(py_file)
        
        if actualizado:
            updated_files.append((py_file, cambios))
            print(f"\n✅ {py_file.relative_to(base_dir)}")
            for cambio in cambios:
                print(f"   {cambio}")
    
    # Resumen
    print()
    print("=" * 70)
    print(f"📊 RESUMEN DE ACTUALIZACIÓN")
    print("=" * 70)
    print(f"✅ Archivos actualizados: {len(updated_files)}")
    print(f"⏭️  Archivos sin cambios: {len(py_files) - len(updated_files) - skipped_files}")
    print(f"⏭️  Archivos ignorados: {skipped_files}")
    print()
    
    if updated_files:
        print("📝 ARCHIVOS ACTUALIZADOS:")
        for file_path, cambios in updated_files[:20]:  # Mostrar primeros 20
            print(f"\n  {file_path.relative_to(base_dir)}")
            for cambio in cambios:
                print(f"    {cambio}")
        
        if len(updated_files) > 20:
            print(f"\n  ... y {len(updated_files) - 20} archivos más")
    
    print()
    print("=" * 70)
    print("✅ ACTUALIZACIÓN DE IMPORTS COMPLETADA")
    print("=" * 70)
    
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
