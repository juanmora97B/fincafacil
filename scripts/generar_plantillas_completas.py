#!/usr/bin/env python3
"""
Script para generar todas las plantillas Excel de carga de datos.

Genera plantillas para todos los módulos de FincaFácil en la carpeta 'plantillas de carga'.
"""
import sys
import os
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.utils.plantillas_carga import FRIENDLY_NAMES, create_workbook_for_module


def generar_todas_plantillas():
    """Genera todas las plantillas Excel en la carpeta 'plantillas de carga'"""
    
    # Crear carpeta si no existe
    output_dir = Path("plantillas de carga")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    generadas = []
    errores = []
    
    print("[*] Generando plantillas Excel...")
    print("[*] Carpeta de salida: " + str(output_dir.resolve()) + "\n")
    
    for friendly_name, module_key in FRIENDLY_NAMES:
        try:
            # Crear workbook
            wb = create_workbook_for_module(module_key)
            
            # Nombre archivo amigable
            filename = f"plantilla_{module_key}.xlsx"
            filepath = output_dir / filename
            
            # Guardar
            wb.save(filepath)
            generadas.append(filename)
            print("[OK] " + friendly_name.ljust(40) + " -> " + filename)
            
        except Exception as e:
            error_msg = f"{friendly_name} ({module_key}): {e}"
            errores.append(error_msg)
            print("[ERROR] " + error_msg)
    
    # Resumen
    print("\n" + "="*60)
    print("[OK] Plantillas generadas: " + str(len(generadas)) + "/" + str(len(FRIENDLY_NAMES)))
    if errores:
        print("[WARNING] Errores: " + str(len(errores)))
        for err in errores:
            print("   - " + err)
    print("="*60)
    
    return len(generadas) == len(FRIENDLY_NAMES)


if __name__ == "__main__":
    success = generar_todas_plantillas()
    sys.exit(0 if success else 1)
