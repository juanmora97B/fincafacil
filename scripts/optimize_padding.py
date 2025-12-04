"""
Script para optimizar el padding en todos los módulos
Reduce márgenes excesivos y maximiza el espacio útil
"""

import os
import re
from pathlib import Path

# Directorio base de módulos
MODULES_DIR = Path(__file__).parent.parent / "modules"

# Patrones a optimizar
OPTIMIZATIONS = [
    # Reducir padding de títulos
    (r'titulo\.pack\(pady=\(10, 5\)\)', 'titulo.pack(pady=(5, 3))'),
    (r'titulo\.pack\(pady=\(10, 10\)\)', 'titulo.pack(pady=(5, 5))'),
    (r'titulo\.pack\(pady=10\)', 'titulo.pack(pady=5)'),
    
    # Optimizar notebook padding
    (r'self\.notebook\.pack\(fill="both", expand=True, padx=10, pady=\(5, 10\)\)', 
     'self.notebook.pack(fill="both", expand=True, padx=5, pady=(3, 5))'),
    (r'self\.notebook\.pack\(fill="both", expand=True, padx=10, pady=10\)', 
     'self.notebook.pack(fill="both", expand=True, padx=5, pady=5)'),
    
    # Optimizar main_frame padding
    (r'main_frame\.pack\(fill="both", expand=True, padx=20, pady=10\)',
     'main_frame.pack(fill="both", expand=True, padx=10, pady=5)'),
    (r'main_frame\.pack\(fill="both", expand=True, padx=10, pady=10\)',
     'main_frame.pack(fill="both", expand=True, padx=5, pady=5)'),
    
    # Optimizar scrollable frames
    (r'main = ctk\.CTkScrollableFrame\(.*?\)\s+main\.pack\(fill="both", expand=True, padx=20, pady=10\)',
     lambda m: m.group(0).replace('padx=20, pady=10', 'padx=10, pady=5')),
    
    # Reducir pady en labels
    (r'\.pack\(pady=\(0, 15\)\)', '.pack(pady=(0, 10))'),
    (r'\.pack\(pady=\(0, 20\)\)', '.pack(pady=(0, 10))'),
    (r'\.pack\(pady=15\)', '.pack(pady=10)'),
    (r'\.pack\(pady=20\)', '.pack(pady=10)'),
]

def optimize_file(file_path):
    """Optimiza un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        for pattern, replacement in OPTIMIZATIONS:
            if callable(replacement):
                # Si es una función, usarla directamente
                new_content = re.sub(pattern, replacement, content)
            else:
                # Si es una cadena, reemplazar directamente
                new_content = content.replace(pattern, replacement)
            
            if new_content != content:
                changes += 1
                content = new_content
        
        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes
        
        return 0
    
    except Exception as e:
        print(f"⚠️  Error procesando {file_path}: {e}")
        return 0

def main():
    """Función principal"""
    print("=" * 70)
    print("OPTIMIZACIÓN DE PADDING EN MÓDULOS")
    print("=" * 70)
    print()
    
    # Módulos a optimizar
    modules_to_optimize = [
        "dashboard/dashboard_main.py",
        "animales/__init__.py",
        "reproduccion/reproduccion_main.py",
        "salud/salud_main.py",
        "potreros/potreros_main.py",
        "tratamientos/tratamientos_main.py",
        "ventas/ventas_main.py",
        "insumos/insumos_main.py",
        "reportes/reportes_main.py",
        "nomina/nomina_main.py",
        "configuracion/__main__.py",
        "ajustes/ajustes_main.py",
    ]
    
    total_changes = 0
    optimized_files = 0
    
    for module_path in modules_to_optimize:
        full_path = MODULES_DIR / module_path
        
        if not full_path.exists():
            print(f"⚠️  No encontrado: {module_path}")
            continue
        
        print(f"📝 Optimizando: {module_path}...", end=" ")
        changes = optimize_file(full_path)
        
        if changes > 0:
            print(f"✅ {changes} cambios aplicados")
            optimized_files += 1
            total_changes += changes
        else:
            print("⏭️  Sin cambios necesarios")
    
    print()
    print("=" * 70)
    print(f"✅ OPTIMIZACIÓN COMPLETADA")
    print(f"   Archivos procesados: {len(modules_to_optimize)}")
    print(f"   Archivos modificados: {optimized_files}")
    print(f"   Total de cambios: {total_changes}")
    print("=" * 70)

if __name__ == "__main__":
    main()
