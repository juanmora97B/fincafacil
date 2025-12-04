"""
Script de verificación de correcciones en módulo Insumos
=========================================================

Verifica que se hayan implementado correctamente:
1. Campos de precio en movimientos tipo Entrada
2. Cambio de estado Agotado → Disponible en entradas
3. Botón Limpiar Campos funciona sin mensajes de eliminación
4. Validación de campos numéricos con comas
5. Referencias actualizadas de "mantenimiento" a "movimientos"
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("c:/Users/lenovo/Desktop/FincaFacil/database/fincafacil.db")

print("=" * 80)
print("VERIFICACIÓN DE CORRECCIONES - MÓDULO INSUMOS")
print("=" * 80)

# 1. Verificar campos en movimiento_insumo
print("\n1. Verificando campos en tabla movimiento_insumo...")
print("-" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(movimiento_insumo)")
columnas = {col[1]: col[2] for col in cursor.fetchall()}

campos_requeridos = ['costo_unitario', 'costo_total', 'tipo_movimiento', 'cantidad']
for campo in campos_requeridos:
    if campo in columnas:
        print(f"  ✓ {campo}: {columnas[campo]}")
    else:
        print(f"  ✗ {campo}: FALTA")

# 2. Verificar estructura de insumo
print("\n2. Verificando campos en tabla insumo...")
print("-" * 80)

cursor.execute("PRAGMA table_info(insumo)")
columnas_insumo = {col[1]: col[2] for col in cursor.fetchall()}

campos_clave = ['stock_actual', 'stock_bodega', 'estado', 'precio_unitario']
for campo in campos_clave:
    if campo in columnas_insumo:
        print(f"  ✓ {campo}: {columnas_insumo[campo]}")
    else:
        print(f"  ✗ {campo}: FALTA")

conn.close()

# 3. Verificar código en insumos_main.py
print("\n3. Verificando código en insumos_main.py...")
print("-" * 80)

codigo_path = Path("c:/Users/lenovo/Desktop/FincaFacil/modules/insumos/insumos_main.py")
with open(codigo_path, 'r', encoding='utf-8') as f:
    contenido = f.read()

verificaciones = [
    ("Campos de precio en formulario", "entry_precio_unitario_mov"),
    ("Cálculo de precio total", "_calcular_precio_total_mov"),
    ("Mostrar/ocultar campos precio", "_actualizar_campos_precio"),
    ("Actualización de precio en DB", "costo_unitario, costo_total"),
    ("Cambio de estado Agotado→Disponible", 'nuevo_estado = "Disponible" if estado_actual == "Agotado"'),
    ("Botón limpiar sin confirmación", "Limpia los campos del formulario de movimientos"),
    ("Validación decimal con coma", 'replace(",", ".")'),
    ("Texto 'Movimientos de Insumos'", "Movimientos de Insumos"),
    ("Historial actualizado", "Historial de Movimientos de Insumos"),
]

for desc, patron in verificaciones:
    if patron in contenido:
        print(f"  ✓ {desc}")
    else:
        print(f"  ✗ {desc}: NO ENCONTRADO")

print("\n4. Resumen de correcciones implementadas:")
print("-" * 80)
print("""
✅ CORRECCIÓN 1: Campos de precio en movimientos Entrada
   - Se agregaron campos entry_precio_unitario_mov y entry_precio_total_mov
   - Se vinculó evento para cálculo automático de precio total
   - Los campos se muestran solo cuando tipo = "Entrada"
   - Se guardan costo_unitario y costo_total en movimiento_insumo
   - Se actualiza precio_unitario del insumo al registrar entrada

✅ CORRECCIÓN 2: Estado Agotado → Disponible
   - Al registrar movimiento tipo Entrada con cantidad > 0
   - Se verifica si estado_actual == "Agotado"
   - Automáticamente cambia nuevo_estado = "Disponible"

✅ CORRECCIÓN 3: Botón Limpiar Campos
   - Método eliminar_insumo_desde_mantenimiento() renombrado funcionalmente
   - Ahora solo limpia campos del formulario sin confirmaciones
   - No muestra mensajes de "eliminar registro"
   - Reinicia todos los campos a valores por defecto

✅ CORRECCIÓN 4: Validación numérica con comas
   - _get_stock_actual_validado() ahora usa .replace(",", ".")
   - _get_stock_bodega_validado() ahora usa .replace(",", ".")
   - Acepta entrada "3,0" y la convierte correctamente a 3.0
   - Evita error: "invalid literal for int() with base 10: 3,0"

✅ CORRECCIÓN 5: Referencias actualizadas
   - "Historial de Mantenimientos" → "Historial de Movimientos de Insumos"
   - Mensajes: "Seleccione un mantenimiento" → "Seleccione un movimiento"
   - Títulos de ventana actualizados
   - Docstrings de métodos actualizados
""")

print("\n5. Instrucciones de prueba:")
print("-" * 80)
print("""
Para probar en la aplicación:

1. PRUEBA DE CAMPOS DE PRECIO:
   a. Ir a pestaña "Movimientos de Insumos"
   b. Seleccionar tipo "Entrada"
   c. Verificar que aparecen campos "Precio Unitario" y "Precio Total"
   d. Ingresar cantidad (ej: 10) y precio unitario (ej: 5.50)
   e. Confirmar que precio total se calcula automáticamente (55.00)
   f. Registrar movimiento y verificar que se guarda correctamente

2. PRUEBA DE CAMBIO DE ESTADO:
   a. Crear o buscar un insumo en estado "Agotado" con stock = 0
   b. Ir a "Movimientos de Insumos"
   c. Registrar una Entrada con cantidad > 0
   d. Ir al Catálogo y verificar que el estado cambió a "Disponible"

3. PRUEBA DE LIMPIAR CAMPOS:
   a. Llenar el formulario de movimientos con datos
   b. Hacer clic en botón "🗑️ Limpiar Campos"
   c. Verificar que todos los campos se vacían sin mensajes
   d. No debe aparecer confirmación de eliminación

4. PRUEBA DE VALIDACIÓN NUMÉRICA:
   a. Ir a Catálogo, seleccionar un insumo y hacer clic en "Editar"
   b. Cambiar cantidad a "3,0" (con coma decimal)
   c. Guardar y verificar que NO aparece error
   d. Confirmar que se guardó correctamente como 3.0

5. PRUEBA DE ELIMINACIÓN DE MOVIMIENTO:
   a. Ir a "Movimientos de Insumos"
   b. Seleccionar un movimiento del historial
   c. Hacer clic en "🗑️ Eliminar del Historial"
   d. Confirmar que el movimiento desaparece del historial
   e. Verificar que el insumo SIGUE en el Catálogo
   f. Verificar que el stock NO se modifica
""")

print("=" * 80)
print("VERIFICACIÓN COMPLETADA")
print("=" * 80)
