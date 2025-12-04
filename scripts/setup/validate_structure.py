"""
Script para validar la nueva estructura del proyecto
FASE 6: Validación
"""

import sys
from pathlib import Path
import importlib.util
from typing import List, Tuple

# Agregar paths
base_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))

def check_directory_structure() -> Tuple[bool, List[str]]:
    """Verifica que exista la estructura correcta"""
    print("🔍 Validando estructura de directorios...")
    
    base = Path(__file__).parent.parent.parent
    required_dirs = [
        "src",
        "src/core",
        "src/database",
        "src/utils",
        "src/modules",
        "src/app",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
        "scripts/dev_tools",
        "scripts/audit",
        "scripts/maintenance",
        "scripts/setup",
    ]
    
    errors = []
    for dir_name in required_dirs:
        dir_path = base / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"  ✅ {dir_name}")
        else:
            print(f"  ❌ {dir_name} (FALTANTE)")
            errors.append(f"Directorio faltante: {dir_name}")
    
    return len(errors) == 0, errors


def check_imports() -> Tuple[bool, List[str]]:
    """Verifica que los imports principales funcionen"""
    print("\n🔍 Validando imports...")
    
    errors = []
    
    # Test 1: Database
    try:
        from database import get_connection, db
        print("  ✅ database.get_connection")
        print("  ✅ database.db")
    except ImportError as e:
        print(f"  ❌ database: {e}")
        errors.append(f"Database import error: {e}")
    
    # Test 2: Validators
    try:
        from src.utils.validators import DataValidator
        print("  ✅ src.utils.validators.DataValidator")
    except ImportError as e:
        print(f"  ❌ validators: {e}")
        errors.append(f"Validators import error: {e}")
    
    # Test 3: Core
    try:
        from src.core.exceptions import ValidationError, DatabaseError
        print("  ✅ src.core.exceptions")
    except ImportError as e:
        print(f"  ❌ core.exceptions: {e}")
        errors.append(f"Core exceptions import error: {e}")
    
    # Test 4: Core constants
    try:
        from src.core.constants import APP_NAME, APP_VERSION
        print("  ✅ src.core.constants")
    except ImportError as e:
        print(f"  ❌ core.constants: {e}")
        errors.append(f"Core constants import error: {e}")
    
    # Test 5: Database connection
    try:
        from database import get_connection
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
        print("  ✅ Conexión a BD funcional")
    except Exception as e:
        print(f"  ❌ Conexión a BD: {e}")
        errors.append(f"Database connection error: {e}")
    
    return len(errors) == 0, errors


def check_key_files() -> Tuple[bool, List[str]]:
    """Verifica que existan archivos clave"""
    print("\n🔍 Validando archivos clave...")
    
    base = Path(__file__).parent.parent.parent
    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "src/__init__.py",
        "src/core/__init__.py",
        "src/core/exceptions.py",
        "src/core/constants.py",
        "src/utils/validators.py",
        "src/database/connection.py",
        "database/database.py",
    ]
    
    errors = []
    for file_name in required_files:
        file_path = base / file_name
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} (FALTANTE)")
            errors.append(f"Archivo faltante: {file_name}")
    
    return len(errors) == 0, errors


def check_no_import_errors() -> Tuple[bool, List[str]]:
    """Verifica que no haya archivos con errores de import"""
    print("\n🔍 Buscando archivos con errores de import...")
    
    base = Path(__file__).parent.parent.parent
    errors = []
    checked = 0
    
    # Archivos críticos a verificar
    critical_files = [
        "main.py",
        "modules/dashboard/dashboard_main.py",
        "modules/ajustes/ajustes_main.py",
    ]
    
    for file_rel in critical_files:
        file_path = base / file_rel
        if not file_path.exists():
            continue
        
        checked += 1
        try:
            # Intentar parsearlo
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            print(f"  ✅ {file_rel}")
        except SyntaxError as e:
            print(f"  ❌ {file_rel}: {e}")
            errors.append(f"Syntax error in {file_rel}: {e}")
        except Exception as e:
            print(f"  ⚠️  {file_rel}: {e}")
    
    return len(errors) == 0, errors


def main():
    """Ejecuta validación completa"""
    print("=" * 70)
    print("  VALIDACIÓN DE ESTRUCTURA - FincaFacil")
    print("=" * 70)
    print()
    
    all_ok = True
    all_errors = []
    
    # Test 1: Estructura
    dirs_ok, dir_errors = check_directory_structure()
    all_ok = all_ok and dirs_ok
    all_errors.extend(dir_errors)
    
    # Test 2: Imports
    imports_ok, import_errors = check_imports()
    all_ok = all_ok and imports_ok
    all_errors.extend(import_errors)
    
    # Test 3: Archivos clave
    files_ok, file_errors = check_key_files()
    all_ok = all_ok and files_ok
    all_errors.extend(file_errors)
    
    # Test 4: Sin errores de import
    syntax_ok, syntax_errors = check_no_import_errors()
    all_ok = all_ok and syntax_ok
    all_errors.extend(syntax_errors)
    
    # Resumen
    print()
    print("=" * 70)
    if all_ok:
        print("✅ VALIDACIÓN EXITOSA - Proyecto listo")
        print("=" * 70)
        return 0
    else:
        print("❌ VALIDACIÓN FALLIDA - Errores encontrados:")
        print("=" * 70)
        for error in all_errors:
            print(f"  • {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
