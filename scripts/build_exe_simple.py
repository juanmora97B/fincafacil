"""
Build script para compilar FincaFácil a ejecutable standalone
Uso: python build_exe_simple.py
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"

def main():
    print("\n" + "="*60)
    print("COMPILANDO FINCAFÁCIL CON PYINSTALLER")
    print("="*60 + "\n")
    
    # Comando PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--noconfirm",
        f"--icon={SRC_DIR / 'assets' / 'Logo.ico'}",
        f"--distpath={DIST_DIR}",
        f"--buildpath={PROJECT_ROOT / 'build'}",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=reportlab",
        "--hidden-import=openpyxl",
        "--hidden-import=tkcalendar",
        "--hidden-import=matplotlib",
        "--hidden-import=numpy",
        "--hidden-import=markdown",
        f"--add-data={SRC_DIR / 'assets'}{';' if sys.platform == 'win32' else ':'}assets",
        f"--add-data={SRC_DIR / 'database'}{';' if sys.platform == 'win32' else ':'}database",
        f"--add-data={SRC_DIR / 'config'}{';' if sys.platform == 'win32' else ':'}config",
        f"--add-data={SRC_DIR / 'modules'}{';' if sys.platform == 'win32' else ':'}modules",
        str(SRC_DIR / "main.py")
    ]
    
    print(f"Ejecutando: {' '.join(cmd[:5])} ...\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        
        exe_path = DIST_DIR / "FincaFacil.exe"
        
        if exe_path.exists():
            print("\n" + "="*60)
            print("✓ COMPILACIÓN EXITOSA")
            print("="*60)
            print(f"\nEjecutable generado: {exe_path}")
            print(f"Tamaño: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            print("\nPuedes ejecutar el programa:")
            print(f"  {exe_path}")
        else:
            print("\n✗ El ejecutable no fue generado")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error en compilación: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
