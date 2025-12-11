#!/usr/bin/env python
"""
Launcher para FincaFácil
Ejecuta src/main.py
"""
import sys
from pathlib import Path
import os

# Cambiar al directorio src
src_dir = Path(__file__).parent / "src"
os.chdir(src_dir)

# Agregar src al path
sys.path.insert(0, str(src_dir))

# Importar y ejecutar main
if __name__ == "__main__":
    from main import main
    main()
