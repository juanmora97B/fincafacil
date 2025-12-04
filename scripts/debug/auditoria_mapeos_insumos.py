"""
Script de auditoría y corrección de mapeos de campos en FincaFácil
===================================================================

PROBLEMA IDENTIFICADO EN MÓDULO INSUMOS - MOVIMIENTOS:

1. DEFINICIÓN DE COLUMNAS (línea 580):
   columns=("id", "fecha", "insumo", "tipo", "estado", "costo", "realizado_por", "proximo")
   
2. CONSULTA SQL (línea 1476):
   SELECT m.id, m.fecha_movimiento, h.codigo || ' - ' || h.nombre,
          m.tipo_movimiento, m.cantidad, m.usuario, m.referencia, m.observaciones
   
3. INSERCIÓN DE VALORES (línea 1502):
   values=(row[0], row[1], row[2], estado_display, cantidad_fmt, row[5] or "N/A", row[6] or "N/A")
   
MAPEO ACTUAL (INCORRECTO):
┌─────────────────┬──────────────┬────────────────────────┐
│ Columna Tabla   │ Valor        │ Origen SQL (row[N])    │
├─────────────────┼──────────────┼────────────────────────┤
│ id              │ row[0]       │ m.id                   │ ✓
│ fecha           │ row[1]       │ m.fecha_movimiento     │ ✓
│ insumo          │ row[2]       │ h.codigo || nombre     │ ✓
│ tipo            │ estado_display│ m.tipo_movimiento     │ ✓
│ estado          │ cantidad_fmt │ m.cantidad             │ ❌ INCORRECTO
│ costo           │ row[5]       │ m.usuario              │ ❌ INCORRECTO
│ realizado_por   │ row[6]       │ m.referencia           │ ❌ INCORRECTO
│ proximo         │ (falta)      │ m.observaciones        │ ❌ INCORRECTO
└─────────────────┴──────────────┴────────────────────────┘

MAPEO CORRECTO ESPERADO:
┌─────────────────┬────────────────────┬──────────────────────────┐
│ Columna Tabla   │ Valor              │ Origen SQL               │
├─────────────────┼────────────────────┼──────────────────────────┤
│ id              │ row[0]             │ m.id                     │
│ fecha           │ row[1]             │ m.fecha_movimiento       │
│ insumo          │ row[2]             │ h.codigo || nombre       │
│ tipo            │ estado_display     │ m.tipo_movimiento        │
│ cantidad        │ cantidad_fmt       │ m.cantidad               │
│ precio          │ precio_fmt         │ m.costo_total o costo_unitario│
│ realizado_por   │ row[X]             │ m.usuario (responsable)  │
│ finca           │ row[Y]             │ m.referencia (finca_destino)│
└─────────────────┴────────────────────┴──────────────────────────┘

CORRECCIONES NECESARIAS:
=========================

1. Renombrar columnas del Treeview:
   - "estado" → "cantidad"
   - "costo" → "precio"
   - "proximo" → "finca"

2. Actualizar consulta SQL para incluir precios:
   SELECT m.id, m.fecha_movimiento, h.codigo || ' - ' || h.nombre,
          m.tipo_movimiento, m.cantidad, m.costo_total, m.costo_unitario,
          m.usuario, m.referencia, m.observaciones

3. Reorganizar inserción de valores:
   values=(row[0], row[1], row[2], tipo_display, 
           cantidad_fmt, precio_fmt, usuario, finca_destino)

VALIDACIONES A AGREGAR:
========================

1. En guardar_mantenimiento:
   - Validar que responsable (entry_realizado_por) sea texto
   - Validar que precio_unitario sea numérico
   - Calcular precio_total = cantidad * precio_unitario
   - Mapear correctamente:
     * responsable → campo 'usuario'
     * precio_unitario → campo 'costo_unitario'
     * precio_total → campo 'costo_total'
     * destino_finca → campo 'referencia'

2. En cargar_mantenimientos:
   - Formatear precio: "N/A" si NULL, sino formato monetario
   - Mostrar usuario en columna "Realizado Por"
   - Mostrar referencia en columna "Finca Destino"

"""

import sqlite3
from pathlib import Path

DB_PATH = Path("c:/Users/lenovo/Desktop/FincaFacil/database/fincafacil.db")

print("=" * 80)
print("AUDITORÍA DE MAPEOS - MÓDULO INSUMOS")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Verificar estructura de movimiento_insumo
print("\n1. Estructura de tabla movimiento_insumo:")
print("-" * 80)
cursor.execute("PRAGMA table_info(movimiento_insumo)")
for col in cursor.fetchall():
    print(f"  {col[1]:<20} {col[2]:<15} {'NULL' if col[3] == 0 else 'NOT NULL':<10}")

# Verificar datos actuales
print("\n2. Muestra de datos actuales:")
print("-" * 80)
cursor.execute("""
    SELECT m.id, m.tipo_movimiento, m.cantidad, m.costo_unitario, m.costo_total,
           m.usuario, m.referencia, m.motivo
    FROM movimiento_insumo m
    LIMIT 5
""")

print(f"  {'ID':<5} {'Tipo':<10} {'Cant':<8} {'P.Unit':<10} {'P.Total':<10} {'Usuario':<15} {'Ref':<15}")
print(f"  {'-'*5} {'-'*10} {'-'*8} {'-'*10} {'-'*10} {'-'*15} {'-'*15}")
for row in cursor.fetchall():
    print(f"  {row[0]:<5} {row[1]:<10} {row[2]:<8.2f} {row[3] or 'N/A':<10} {row[4] or 'N/A':<10} {row[5] or 'N/A':<15} {row[6] or 'N/A':<15}")

conn.close()

print("\n" + "=" * 80)
print("CORRECCIONES REQUERIDAS")
print("=" * 80)

correcciones = """
ARCHIVO: modules/insumos/insumos_main.py

CAMBIO 1: Renombrar columnas del Treeview (línea ~580)
------------------------------------------------------
ANTES:
columns=("id", "fecha", "insumo", "tipo", "estado", "costo", "realizado_por", "proximo")

DESPUÉS:
columns=("id", "fecha", "insumo", "tipo", "cantidad", "precio", "realizado_por", "finca")


CAMBIO 2: Actualizar encabezados (línea ~585-593)
--------------------------------------------------
ANTES:
("estado", "Estado", 100),
("costo", "Costo", 90),
("realizado_por", "Realizado Por", 140),
("proximo", "Próximo", 90)

DESPUÉS:
("cantidad", "Cantidad", 100),
("precio", "Precio", 90),
("realizado_por", "Realizado Por", 140),
("finca", "Finca Destino", 120)


CAMBIO 3: Actualizar consulta SQL (línea ~1476)
------------------------------------------------
ANTES:
SELECT m.id, m.fecha_movimiento, h.codigo || ' - ' || h.nombre,
       m.tipo_movimiento, m.cantidad, m.usuario, m.referencia, m.observaciones

DESPUÉS:
SELECT m.id, m.fecha_movimiento, h.codigo || ' - ' || h.nombre,
       m.tipo_movimiento, m.cantidad, 
       COALESCE(m.costo_total, m.costo_unitario * m.cantidad, 0) as precio,
       m.usuario, m.referencia


CAMBIO 4: Reorganizar inserción de valores (línea ~1502)
---------------------------------------------------------
ANTES:
values=(row[0], row[1], row[2], estado_display, cantidad_fmt, row[5] or "N/A", row[6] or "N/A")

DESPUÉS:
cantidad_fmt = f"{row[4]:,.2f}" if row[4] is not None else "N/A"
precio_fmt = f"${row[5]:,.2f}" if row[5] and row[5] > 0 else "N/A"
usuario = row[6] or "N/A"
finca_destino = row[7] or "N/A"

values=(row[0], row[1], row[2], estado_display, cantidad_fmt, precio_fmt, usuario, finca_destino)


CAMBIO 5: Validar tipos en guardar_mantenimiento
-------------------------------------------------
Agregar validación:

# Validar que responsable sea texto (no numérico)
if responsable and responsable.replace('.','').replace(',','').isdigit():
    messagebox.showerror("Error", "Responsable debe ser un nombre, no un número")
    return

# Validar que precio sea numérico
if tipo_mov == "Entrada" and precio_unit_txt:
    try:
        costo_unitario = float(precio_unit_txt)
        if costo_unitario < 0:
            raise ValueError("Precio no puede ser negativo")
    except ValueError as e:
        messagebox.showerror("Error", f"Precio unitario inválido: {e}")
        return
"""

print(correcciones)

print("\n" + "=" * 80)
print("MATRIZ DE MAPEO FINAL")
print("=" * 80)

matriz = """
FORMULARIO → BASE DE DATOS → LISTADO
=====================================

Campo Formulario          Campo Entry             Campo BD              Columna Listado
-------------------       -------------------     -----------------     -------------------
Cantidad                  entry_costo_mant        cantidad              Cantidad
Responsable               entry_realizado_por     usuario               Realizado Por
Precio Unitario           entry_precio_unitario_mov  costo_unitario     Precio (calculado)
Precio Total              entry_precio_total_mov  costo_total           Precio (calculado)
Finca Destino             entry_proveedor_mant    referencia            Finca Destino
Motivo                    entry_proximo_mant      motivo                (no se muestra)
Observaciones             text_desc_mant          observaciones         (no se muestra)
Tipo Movimiento           combo_tipo_mant         tipo_movimiento       Tipo
Fecha                     entry_fecha_mant        fecha_movimiento      Fecha
Insumo                    combo_insumo_mant       insumo_id             Insumo (con nombre)

NOTAS:
- "Cantidad" usa entry_costo_mant (nombre confuso del entry, debería ser entry_cantidad)
- "Finca Destino" usa entry_proveedor_mant (nombre confuso, debería ser entry_finca_destino)
- "Motivo" usa entry_proximo_mant (nombre confuso, debería ser entry_motivo)
- Precio en listado muestra costo_total o costo_unitario * cantidad
"""

print(matriz)

print("\nPRÓXIMOS PASOS:")
print("1. Aplicar los 5 cambios listados arriba")
print("2. Renombrar variables de entry para mayor claridad (opcional pero recomendado)")
print("3. Crear pruebas unitarias que validen el mapeo correcto")
print("4. Auditar módulos Herramientas y Animales con el mismo criterio")
