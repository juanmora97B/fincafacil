"""
Configuración de PyInstaller para FincaFácil
Crea un ejecutable profesional standalone
"""
import PyInstaller.__main__
import os
import sys
from pathlib import Path

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
SPEC_FILE = PROJECT_ROOT / "FincaFacil.spec"

# Configuración
ENTRY_POINT = str(SRC_DIR / "main.py")
ICON_PATH = str(SRC_DIR / "assets" / "Logo.ico")
HIDDEN_IMPORTS = [
    "customtkinter",
    "PIL",
    "reportlab",
    "openpyxl",
    "tkcalendar",
    "matplotlib",
    "numpy",
    "markdown",
    "sqlite3",
    "tkinter",
]

# Archivos a incluir
DATA_FILES = [
    (str(SRC_DIR / "assets"), "assets"),
    (str(SRC_DIR / "database"), "database"),
    (str(SRC_DIR / "config"), "config"),
    (str(SRC_DIR / "modules"), "modules"),
    (str(SRC_DIR / "utils" / "requirements.txt"), "."),
]

def generar_spec():
    """Genera el archivo .spec para PyInstaller"""
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Spec file for FincaFácil

a = Analysis(
    ['{ENTRY_POINT}'],
    pathex=[],
    binaries=[],
    datas={repr([str(f) if isinstance(f, tuple) else f for f in DATA_FILES])},
    hiddenimports={repr(HIDDEN_IMPORTS)},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FincaFacil',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{ICON_PATH}',
)
'''
    
    with open(SPEC_FILE, 'w') as f:
        f.write(spec_content)
    
    print(f"✓ Archivo .spec generado: {SPEC_FILE}")
    return str(SPEC_FILE)

def compilar_exe():
    """Compila el ejecutable usando PyInstaller"""
    
    print("\n" + "="*60)
    print("COMPILANDO FINCAFÁCIL CON PYINSTALLER")
    print("="*60)
    
    args = [
        ENTRY_POINT,
        '--name=FincaFacil',
        '--onefile',
        f'--icon={ICON_PATH}',
        '--windowed',
        '--noconfirm',
    ]
    
    # Agregar hidden imports
    for imp in HIDDEN_IMPORTS:
        args.append(f'--hidden-import={imp}')
    
    # Agregar datos
    for source, dest in DATA_FILES:
        args.append(f'--add-data={source}{os.pathsep}{dest}')
    
    # Especificar output
    args.append(f'--distpath={DIST_DIR}')
    args.append(f'--buildpath={BUILD_DIR}')
    args.append(f'--specpath={PROJECT_ROOT}')
    
    print(f"\nComandos PyInstaller:")
    for arg in args[:5]:
        print(f"  {arg}")
    print("  ...")
    
    print(f"\nCompilando...")
    try:
        PyInstaller.__main__.run(args)
        print("\n✓ Compilación completada exitosamente")
        return True
    except Exception as e:
        print(f"\n✗ Error en compilación: {e}")
        return False

def crear_build_bat():
    """Crea un archivo .bat para compilar fácilmente"""
    
    bat_content = f'''@echo off
REM Build script para FincaFácil
REM Compila el ejecutable con PyInstaller

echo ============================================
echo COMPILANDO FINCAFÁCIL
echo ============================================

cd /d {PROJECT_ROOT}

REM Instalar PyInstaller si no está disponible
echo Verificando dependencias...
pip install pyinstaller -q

REM Generar .spec
echo Generando configuración...
python scripts\build_pyinstaller.py --spec

REM Compilar
echo Compilando ejecutable...
pyinstaller --onefile --windowed --icon=src\\assets\\Logo.ico --distpath=dist --buildpath=build --name=FincaFacil src\\main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo ✓ COMPILACIÓN EXITOSA
    echo ============================================
    echo.
    echo Ejecutable generado: dist\\FincaFacil.exe
    echo.
    pause
) else (
    echo.
    echo ============================================
    echo ✗ ERROR EN COMPILACIÓN
    echo ============================================
    echo.
    pause
    exit /b 1
)
'''
    
    bat_path = PROJECT_ROOT / "build_exe.bat"
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print(f"✓ Script build_exe.bat creado: {bat_path}")
    return str(bat_path)

def crear_este_script_mejorado():
    """Crea la versión mejorada de este script"""
    # Este script ya es bueno, solo documentamos
    pass

def main():
    """Flujo principal"""
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--spec':
        # Solo generar .spec
        generar_spec()
    else:
        # Flujo completo: generar .spec + compilar + crear .bat
        print("Preparando compilación de FincaFácil...\n")
        
        # 1. Generar .spec
        generar_spec()
        
        # 2. Compilar
        exito = compilar_exe()
        
        if exito:
            # 3. Crear script .bat
            crear_build_bat()
            
            print("\n" + "="*60)
            print("PROCESO COMPLETADO")
            print("="*60)
            print(f"\nEjecutable: {DIST_DIR / 'FincaFacil.exe'}")
            print(f"Para futuras compilaciones: build_exe.bat")
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
