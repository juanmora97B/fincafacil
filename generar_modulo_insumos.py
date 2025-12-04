"""
Script para generar módulo de insumos basado en módulo de herramientas
"""
import os
import re

# Leer el archivo de herramientas
herr_path = r"c:\Users\lenovo\Desktop\FincaFacil\modules\herramientas\herramientas_main.py"
insumo_path = r"c:\Users\lenovo\Desktop\FincaFacil\modules\insumos\insumos_main_new.py"

print("=" * 70)
print("GENERANDO MÓDULO DE INSUMOS DESDE HERRAMIENTAS")
print("=" * 70)

with open(herr_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"\n📄 Archivo fuente: {len(content)} caracteres")

# Reemplazos generales
replacements = [
    # Clases y títulos
    ('HerramientasModule', 'InsumosModule'),
    ('herramientas_main', 'insumos_main'),
    
    # Nombres de tablas
    ('herramienta_id', 'insumo_id'),
    ('mantenimiento_herramienta', 'mantenimiento_insumo'),
    ('herramienta', 'insumo'),
    ('Herramientas', 'Insumos'),
    ('herramientas', 'insumos'),
    ('HERRAMIENTAS', 'INSUMOS'),
    
    # Variables y atributos
    ('self.foto_path_actual', 'self.foto_path_actual'),
    ('self.herramienta_editando_id', 'self.insumo_editando_id'),
    
    # Términos específicos  
    ('🔧 Gestión de Herramientas y Equipos', '📦 Gestión de Insumos e Inventario'),
    ('Herramienta', 'Insumo'),
    ('herramienta', 'insumo'),
    ('HERRAMIENTA', 'INSUMO'),
    
    # Campos específicos de herramientas -> insumos
    ('numero_serie', 'lote_proveedor'),
    ('marca', 'proveedor_principal'),
    ('modelo', 'unidad_medida'),
    ('valor_adquisicion', 'precio_unitario'),
    ('vida_util_anos', 'stock_minimo'),
    
    # Mensajes
    ('Maquinaria', 'Medicamento'),
    ('Vehículo', 'Fertilizante'),
    ('Manual', 'Alimento'),
    ('Equipo', 'Semilla'),
]

new_content = content

# Aplicar reemplazos en orden
for old, new in replacements:
    new_content = new_content.replace(old, new)

# Reemplazos específicos con regex
new_content = re.sub(r'cargar_herramientas\(\)', 'cargar_insumos()', new_content)
new_content = re.sub(r'def cargar_herramientas\(self\):', 'def cargar_insumos(self):', new_content)

print(f"✓ {len(replacements)} reemplazos aplicados")
print(f"📄 Archivo resultado: {len(new_content)} caracteres")

# Guardar archivo
with open(insumo_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n✅ Archivo generado: {insumo_path}")
print(f"   Tamaño: {os.path.getsize(insumo_path)} bytes")
print("\n⚠️  IMPORTANTE: Revisar manualmente el archivo generado")
print("   - Verificar nombres de campos de BD")
print("   - Ajustar categorías y valores predeterminados")
print("   - Adaptar mensajes de usuario")
print("=" * 70)
