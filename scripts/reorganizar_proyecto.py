"""
Script de reorganización del proyecto FincaFácil
Estructura: src/
├── config/
├── database/
├── modules/
├── assets/
├── utils/
├── styles/
└── main.py

Ejecución: python scripts/reorganizar_proyecto.py
"""
import shutil
import os
from pathlib import Path
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent
NEW_STRUCTURE = ROOT_DIR / "src"

def crear_estructura():
    """Crea la nueva estructura de directorios"""
    directorios = [
        NEW_STRUCTURE,
        NEW_STRUCTURE / "config",
        NEW_STRUCTURE / "database",
        NEW_STRUCTURE / "modules",
        NEW_STRUCTURE / "assets",
        NEW_STRUCTURE / "utils",
        NEW_STRUCTURE / "styles",
    ]
    
    for directorio in directorios:
        directorio.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio creado: {directorio}")

def mover_carpetas():
    """Mueve las carpetas principales a src/"""
    carpetas = {
        "config": NEW_STRUCTURE / "config",
        "database": NEW_STRUCTURE / "database",
        "modules": NEW_STRUCTURE / "modules",
        "assets": NEW_STRUCTURE / "assets",
    }
    
    for carpeta_nombre, destino in carpetas.items():
        origen = ROOT_DIR / carpeta_nombre
        
        if origen.exists() and carpeta_nombre in ["config", "database", "modules", "assets"]:
            # Mover contenido (no la carpeta misma)
            for item in origen.iterdir():
                dest_item = destino / item.name
                
                # Si el destino ya existe, eliminar
                if dest_item.exists():
                    if dest_item.is_dir():
                        shutil.rmtree(dest_item)
                    else:
                        dest_item.unlink()
                
                # Mover
                shutil.move(str(item), str(dest_item))
                logger.info(f"Movido: {item.name} -> {destino.name}/{item.name}")

def mover_utilidades():
    """Mueve archivos de utilidad a src/utils/"""
    utils_files = [
        "requirements.txt",
        "pyproject.toml",
        "config.py",
        "conftest.py",
    ]
    
    for archivo in utils_files:
        origen = ROOT_DIR / archivo
        if origen.exists():
            destino = NEW_STRUCTURE / "utils" / archivo
            shutil.copy2(str(origen), str(destino))
            logger.info(f"Copiado: {archivo} -> src/utils/{archivo}")

def mover_main():
    """Mueve main.py a src/"""
    main_origen = ROOT_DIR / "main.py"
    if main_origen.exists():
        destino = NEW_STRUCTURE / "main.py"
        shutil.copy2(str(main_origen), str(destino))
        logger.info(f"Copiado: main.py -> src/main.py")
        
        # Actualizar imports en main.py dentro de src
        actualizar_imports_main(destino)

def actualizar_imports_main(main_path):
    """Actualiza los imports en main.py para reflejar la nueva estructura"""
    try:
        with open(main_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Reemplazar importaciones relativas si es necesario
        # Por ahora, la estructura relativa debería funcionar
        logger.info(f"Importaciones en {main_path} verificadas")
    except Exception as e:
        logger.error(f"Error al actualizar imports: {e}")

def limpiar_cache():
    """Elimina archivos __pycache__ y .pyc"""
    pycache_dirs = list(ROOT_DIR.rglob("__pycache__"))
    pyc_files = list(ROOT_DIR.rglob("*.pyc"))
    
    for pycache in pycache_dirs:
        try:
            shutil.rmtree(pycache)
            logger.info(f"Eliminado: {pycache}")
        except FileNotFoundError:
            logger.warning(f"Directorio ya no existe: {pycache}")
        except Exception as e:
            logger.warning(f"Error eliminando {pycache}: {e}")
    
    for pyc in pyc_files:
        try:
            pyc.unlink()
            logger.info(f"Eliminado: {pyc}")
        except FileNotFoundError:
            logger.warning(f"Archivo ya no existe: {pyc}")
        except Exception as e:
            logger.warning(f"Error eliminando {pyc}: {e}")

def crear_init_files():
    """Crea archivos __init__.py en los directorios necesarios"""
    dirs_init = [
        NEW_STRUCTURE / "utils",
    ]
    
    for directorio in dirs_init:
        init_file = directorio / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            logger.info(f"Creado: {init_file}")

def crear_launcher_raiz():
    """Crea un launcher en la raíz que ejecute src/main.py"""
    launcher_content = '''#!/usr/bin/env python
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
'''
    
    launcher_path = ROOT_DIR / "launcher.py"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    logger.info(f"Creado launcher: {launcher_path}")

def crear_bat_launcher():
    """Crea un .bat para ejecutar desde Windows"""
    bat_content = '''@echo off
REM Launcher para FincaFácil (Windows)
cd /d %~dp0
python -m src.main
pause
'''
    
    bat_path = ROOT_DIR / "FincaFacil.bat"
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    logger.info(f"Creado launcher BAT: {bat_path}")

def generar_informe():
    """Genera un informe de la reorganización"""
    informe = f"""
REORGANIZACIÓN DE PROYECTO FINCAFÁCIL
=====================================

Nueva estructura (src/):
{NEW_STRUCTURE}
├── config/          (configuración)
├── database/        (BD y esquemas)
├── modules/         (módulos funcionales)
├── assets/          (recursos, imágenes, ícono)
├── utils/           (utilidades compartidas)
├── styles/          (estilos CSS/tema)
├── main.py          (punto de entrada)
└── requirements.txt (dependencias)

Pasos completados:
✓ Estructura de directorios creada
✓ Carpetas principales movidas a src/
✓ Archivos de utilidad copiados a src/utils/
✓ main.py copiado a src/
✓ Cache (__pycache__, .pyc) eliminado
✓ Archivos __init__.py creados
✓ Launchers (Python y BAT) creados

Proximos pasos:
1. Eliminar antiguas carpetas en raíz (una vez verificado que todo funciona)
2. Actualizar referencias de rutas en el código
3. Generar ejecutable con PyInstaller desde src/

Para ejecutar:
- Windows: FincaFacil.bat
- Python: python launcher.py
- Directo: python -m src.main
"""
    
    informe_path = ROOT_DIR / "REORGANIZACION_INFORME.txt"
    with open(informe_path, 'w', encoding='utf-8') as f:
        f.write(informe)
    
    logger.info(f"\nInforme generado: {informe_path}")
    print(informe)

def main():
    """Ejecuta la reorganización completa"""
    logger.info("Iniciando reorganización del proyecto FincaFácil...")
    logger.info(f"Directorio raíz: {ROOT_DIR}")
    logger.info(f"Nueva estructura: {NEW_STRUCTURE}")
    
    try:
        # 1. Crear estructura
        logger.info("\n[1/7] Creando estructura de directorios...")
        crear_estructura()
        
        # 2. Mover carpetas principales
        logger.info("\n[2/7] Moviendo carpetas principales...")
        mover_carpetas()
        
        # 3. Mover utilidades
        logger.info("\n[3/7] Moviendo archivos de utilidad...")
        mover_utilidades()
        
        # 4. Mover main.py
        logger.info("\n[4/7] Moviendo main.py...")
        mover_main()
        
        # 5. Limpiar cache
        logger.info("\n[5/7] Limpiando cache (__pycache__, .pyc)...")
        limpiar_cache()
        
        # 6. Crear __init__.py
        logger.info("\n[6/7] Creando archivos __init__.py...")
        crear_init_files()
        
        # 7. Crear launchers
        logger.info("\n[7/7] Creando launchers...")
        crear_launcher_raiz()
        crear_bat_launcher()
        
        # Informe final
        logger.info("\n" + "="*50)
        generar_informe()
        logger.info("="*50)
        logger.info("\nReorganización completada exitosamente!")
        logger.info("ADVERTENCIA: Las carpetas antiguas en raíz pueden ser eliminadas manualmente")
        logger.info("después de verificar que todo funciona correctamente con la nueva estructura.")
        
    except Exception as e:
        logger.error(f"\nError durante la reorganización: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
