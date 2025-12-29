#!/usr/bin/env python3
"""
Script para optimizar layout de todos los módulos de configuración
Amplía campos y aprovecha mejor el espacio disponible
"""

import os
import re

CONFIG_MODULES = [
    "lotes.py",
    "potreros.py",
    "razas.py",
    "calidad_animal.py",
    "condiciones_corporales.py",
    "tipo_explotacion.py",
    "motivos_venta.py",
    "destino_venta.py",
    "procedencia.py",
]

BASE_PATH = r"c:\Users\lenovo\Desktop\FincaFacil\modules\configuracion"

def optimize_file(filepath):
    """Optimiza un archivo de configuración para usar mejor el espacio"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. Reducir padding en scroll_container: padx=10, pady=10 -> padx=5, pady=5
    content = re.sub(
        r'scroll_container\.pack\(fill="both", expand=True, padx=10, pady=10\)',
        'scroll_container.pack(fill="both", expand=True, padx=5, pady=5)',
        content
    )
    
    # 2. Aumentar altura de tabla: height=12 -> height=18
    content = re.sub(
        r'height=12\)',
        'height=18)',
        content
    )
    
    # 3. Aumentar altura de combobox/entry: sin especificar -> height=35
    # Para combos sin height explícito
    content = re.sub(
        r'(ctk\.CTkComboBox\([^)]*?)(?:, width=\d+)?(\))',
        r'\1, height=35\2',
        content
    )
    
    # 4. Aumentar altura de botones: sin spec -> height=40
    # Para botones sin height
    content = re.sub(
        r'(ctk\.CTkButton\([^)]*?text="[^"]+")(?:, height=\d+)?(.*?)\)',
        r'\1, height=40\2)',
        content
    )
    
    # 5. Expandir fields en grid: usar weight=1 y sticky="ew"
    content = re.sub(
        r'\.columnconfigure\((\d+)\, weight=0\)',
        r'.columnconfigure(\1, weight=1)',
        content
    )
    
    # 6. Aumentar fuente de botones de acción
    content = re.sub(
        r'font=\("Segoe UI", 12\)',
        'font=("Segoe UI", 12)',
        content,
        count=5
    )
    
    # 7. Cambiar padx en form_frame de 4 a 5
    content = re.sub(
        r'form_frame\.pack\(([^)]*?)padx=4([^)]*?)\)',
        r'form_frame.pack(\1padx=5\2)',
        content
    )
    
    # 8. Tabla: aumentar widths de columnas
    # Reemplazar columnas pequeñas por más grandes
    content = re.sub(
        r'\("codigo", "Código", \d+\)',
        '("codigo", "Código", 120)',
        content
    )
    content = re.sub(
        r'\("nombre", "Nombre", \d+\)',
        '("nombre", "Nombre", 200)',
        content
    )
    content = re.sub(
        r'\("descripcion", "Descripción", \d+\)',
        '("descripcion", "Descripción", 300)',
        content
    )
    content = re.sub(
        r'\("comentario", "Comentario", \d+\)',
        '("comentario", "Comentario", 400)',
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

if __name__ == "__main__":
    for module in CONFIG_MODULES:
        filepath = os.path.join(BASE_PATH, module)
        if os.path.exists(filepath):
            if optimize_file(filepath):
                print(f"✅ Optimizado: {module}")
            else:
                print(f"⏭️  Sin cambios: {module}")
        else:
            print(f"❌ No encontrado: {module}")
    
    print("\n✅ Optimización completada")
