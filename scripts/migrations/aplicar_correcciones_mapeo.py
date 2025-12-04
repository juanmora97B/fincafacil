"""
Script de aplicación automática de correcciones de mapeo
=========================================================

Este script aplica las correcciones necesarias en el módulo Insumos
"""

import re
from pathlib import Path

FILE_PATH = Path("c:/Users/lenovo/Desktop/FincaFacil/modules/insumos/insumos_main.py")

print("Leyendo archivo...")
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

# CORRECCIÓN 1: Cambiar columnas del Treeview
print("\n1. Corrigiendo columnas del Treeview...")
content = content.replace(
    'columns=("id", "fecha", "insumo", "tipo", "estado", "costo", "realizado_por", "proximo")',
    'columns=("id", "fecha", "insumo", "tipo", "cantidad", "precio", "realizado_por", "finca")'
)

# CORRECCIÓN 2: Cambiar encabezados de columnas
print("2. Corrigiendo encabezados...")
old_columnas = '''        columnas_mant = [
            ("id", "ID", 50),
            ("fecha", "Fecha", 90),
            ("insumo", "Insumo", 220),
            ("tipo", "Tipo", 110),
            ("estado", "Estado", 100),
            ("costo", "Costo", 90),
            ("realizado_por", "Realizado Por", 140),
            ("proximo", "Próximo", 90)
        ]'''

new_columnas = '''        columnas_mant = [
            ("id", "ID", 50),
            ("fecha", "Fecha", 90),
            ("insumo", "Insumo", 220),
            ("tipo", "Tipo", 110),
            ("cantidad", "Cantidad", 100),
            ("precio", "Precio", 90),
            ("realizado_por", "Realizado Por", 140),
            ("finca", "Finca Destino", 120)
        ]'''

content = content.replace(old_columnas, new_columnas)

# CORRECCIÓN 3: Actualizar consulta SQL
print("3. Corrigiendo consulta SQL...")
old_query = '''                cursor.execute(
                    """
                    SELECT m.id, m.fecha_movimiento, h.codigo || ' - ' || h.nombre,
                           m.tipo_movimiento, m.cantidad, m.usuario, m.referencia, m.observaciones
                    FROM movimiento_insumo m
                    JOIN insumo h ON m.insumo_id = h.id
                    WHERE m.id IS NOT NULL
                    ORDER BY m.fecha_movimiento DESC, m.id DESC
                    LIMIT 100
                    """
                )'''

new_query = '''                cursor.execute(
                    """
                    SELECT m.id, m.fecha_movimiento, h.codigo || ' - ' || h.nombre,
                           m.tipo_movimiento, m.cantidad, 
                           COALESCE(m.costo_total, m.costo_unitario * m.cantidad, 0) as precio,
                           m.usuario, m.referencia
                    FROM movimiento_insumo m
                    JOIN insumo h ON m.insumo_id = h.id
                    WHERE m.id IS NOT NULL
                    ORDER BY m.fecha_movimiento DESC, m.id DESC
                    LIMIT 100
                    """
                )'''

content = content.replace(old_query, new_query)

# CORRECCIÓN 4: Actualizar inserción de valores
print("4. Corrigiendo inserción de valores...")
old_values = '''                    cantidad_fmt = f"{row[4]:,.2f}" if row[4] is not None else "N/A"
                    tipo = row[3]
                    estado_display = "➕ Entrada" if tipo == "Entrada" else ("➖ Salida" if tipo == "Salida" else "⚙️ Ajuste")
                    
                    item_id = self.tabla_mant.insert(
                        "",
                        "end",
                        values=(row[0], row[1], row[2], estado_display, cantidad_fmt, row[5] or "N/A", row[6] or "N/A"),
                    )'''

new_values = '''                    cantidad_fmt = f"{row[4]:,.2f}" if row[4] is not None else "N/A"
                    precio_fmt = f"${row[5]:,.2f}" if row[5] and row[5] > 0 else "N/A"
                    tipo = row[3]
                    tipo_display = "➕ Entrada" if tipo == "Entrada" else ("➖ Salida" if tipo == "Salida" else "⚙️ Ajuste")
                    usuario = row[6] or "N/A"
                    finca_destino = row[7] or "N/A"
                    
                    item_id = self.tabla_mant.insert(
                        "",
                        "end",
                        values=(row[0], row[1], row[2], tipo_display, cantidad_fmt, precio_fmt, usuario, finca_destino),
                    )'''

content = content.replace(old_values, new_values)

# Guardar cambios
if content != original_content:
    print("\nGuardando cambios...")
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Correcciones aplicadas exitosamente!")
    print(f"\nArchivo modificado: {FILE_PATH}")
else:
    print("\n⚠️ No se encontraron cambios para aplicar")

print("\nResumen de cambios:")
print("  1. Columnas del Treeview renombradas: estado→cantidad, costo→precio, proximo→finca")
print("  2. Encabezados actualizados con nombres correctos")
print("  3. Consulta SQL actualizada para incluir precio calculado")
print("  4. Inserción de valores reorganizada para mapeo correcto")
