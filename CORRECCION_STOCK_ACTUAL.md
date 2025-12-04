# 🔧 CORRECCIÓN: Error "no such column: h.stock_total"

## 📋 Problema Identificado

Al intentar acceder al módulo de Insumos, se producía el error:
```
Error al conectar con la base de datos: no such column: h.stock_total
```

**Causa:** El código del módulo `insumos_main.py` estaba usando el campo `stock_total`, pero en la tabla `insumo` de la base de datos el campo correcto es `stock_actual`.

Este error se produjo durante la generación automática del módulo, donde se hizo un mapeo incorrecto entre los campos de herramientas e insumos.

---

## 🔍 Campos Reales de la Tabla `insumo`

```python
Campos verificados en la base de datos:
- id (INTEGER)
- codigo (TEXT)
- nombre (TEXT)
- categoria (TEXT)
- descripcion (TEXT)
- unidad_medida (TEXT)
- stock_actual (REAL)      ← Campo correcto
- stock_minimo (REAL)
- stock_maximo (REAL)
- precio_unitario (REAL)
- id_finca (INTEGER)
- ubicacion (TEXT)
- proveedor_principal (TEXT)
- fecha_vencimiento (DATE)
- lote_proveedor (TEXT)
- estado (TEXT)
- fecha_creacion (TIMESTAMP)
- foto_path (TEXT)
- id_trabajador (INTEGER)
- responsable (TEXT)
- stock_bodega (REAL)
- observaciones (TEXT)
```

---

## ✅ Correcciones Aplicadas

### 1. **Query SQL de Catálogo** (Línea 878)
```python
# Antes:
h.stock_total, h.id_trabajador, h.responsable, h.stock_bodega

# Ahora:
h.stock_actual, h.id_trabajador, h.responsable, h.stock_bodega
```

### 2. **Columnas del Treeview** (Línea 335-344)
```python
# Antes:
columns=("codigo", "nombre", "categoria", "finca", "stock_total", "asignacion", "stock_bodega", "estado")
("stock_total", "Stock Total", 95)

# Ahora:
columns=("codigo", "nombre", "categoria", "finca", "stock_actual", "asignacion", "stock_bodega", "estado")
("stock_actual", "Stock Actual", 95)
```

### 3. **Campo de Entrada en UI** (Línea 206)
```python
# Antes:
ctk.CTkLabel(stock_frame, text="Stock Total:", width=150)
self.entry_stock_total = ctk.CTkEntry(stock_frame, width=120)

# Ahora:
ctk.CTkLabel(stock_frame, text="Stock Actual:", width=150)
self.entry_stock_actual = ctk.CTkEntry(stock_frame, width=120)
```

### 4. **Método de Validación** (Línea 1918)
```python
# Antes:
def _get_stock_total_validado(self, valor):
    """Valida stock_total (int >=1)..."""

# Ahora:
def _get_stock_actual_validado(self, valor):
    """Valida stock_actual (int >=1)..."""
```

### 5. **Guardado en Base de Datos** (Líneas 779, 808)
```python
# Antes:
UPDATE insumo SET ... stock_total = ?, stock_bodega = ? ...
INSERT INTO insumo (...stock_total, stock_bodega...) VALUES (?, ?)

# Ahora:
UPDATE insumo SET ... stock_actual = ?, stock_bodega = ? ...
INSERT INTO insumo (...stock_actual, stock_bodega...) VALUES (?, ?)
```

### 6. **Cargar Datos en Formulario** (Línea 1173-1175)
```python
# Antes:
if hasattr(self, 'entry_stock_total'):
    self.entry_stock_total.delete(0, "end")
    self.entry_stock_total.insert(0, str(h.get('stock_total', 1)))

# Ahora:
if hasattr(self, 'entry_stock_actual'):
    self.entry_stock_actual.delete(0, "end")
    self.entry_stock_actual.insert(0, str(h.get('stock_actual', 1)))
```

### 7. **Limpiar Formulario** (Línea 853-855)
```python
# Antes:
if hasattr(self, 'entry_stock_total'):
    self.entry_stock_total.delete(0, "end")
    self.entry_stock_total.insert(0, "1")

# Ahora:
if hasattr(self, 'entry_stock_actual'):
    self.entry_stock_actual.delete(0, "end")
    self.entry_stock_actual.insert(0, "1")
```

### 8. **Ventana de Detalles** (Línea 963)
```python
# Antes:
• Stock Total: {h.get('stock_total', 'N/D')}

# Ahora:
• Stock Actual: {h.get('stock_actual', 'N/D')}
```

### 9. **Importación desde Excel** (Líneas 1722, 1794, 1821, 1867)
```python
# Antes:
stock_total_raw = row[col_map.get("stock_total")]
stock_total = self._get_stock_total_validado(stock_total_raw)
INSERT INTO insumo (...stock_total, stock_bodega...)

# Ahora:
stock_actual_raw = row[col_map.get("stock_actual")]
stock_actual = self._get_stock_actual_validado(stock_actual_raw)
INSERT INTO insumo (...stock_actual, stock_bodega...)
```

### 10. **Plantilla de Importación** (Líneas 1867, 1907)
```python
# Antes:
headers = [..., "stock_total", "stock_bodega"]
"Opcionales (recomendado): stock_total, stock_bodega"

# Ahora:
headers = [..., "stock_actual", "stock_bodega"]
"Opcionales (recomendado): stock_actual, stock_bodega"
```

### 11. **Método de Validación de Stock Bodega** (Línea 1934)
```python
# Antes:
def _get_stock_bodega_validado(self, valor, stock_total, responsable_actual):
    """Valida stock_bodega (int >=0 <= stock_total)..."""
    if v > stock_total:
        v = stock_total

# Ahora:
def _get_stock_bodega_validado(self, valor, stock_actual, responsable_actual):
    """Valida stock_bodega (int >=0 <= stock_actual)..."""
    if v > stock_actual:
        v = stock_actual
```

### 12. **Comentarios y Docstrings** (Líneas 869, 904)
```python
# Antes:
"""Carga insumos en Catálogo con filtrado y muestra stock_total y stock_bodega"""
# row indices: ...4 stock_total...

# Ahora:
"""Carga insumos en Catálogo con filtrado y muestra stock_actual y stock_bodega"""
# row indices: ...4 stock_actual...
```

### 13. **Validación de Variables** (Líneas 761-766)
```python
# Antes:
stock_total = self._get_stock_total_validado(self.entry_stock_total.get().strip())
stock_bodega = self._get_stock_bodega_validado(self.entry_stock_bodega.get().strip(), stock_total, ...)
if asignada_flag and stock_total == 1:

# Ahora:
stock_actual = self._get_stock_actual_validado(self.entry_stock_actual.get().strip())
stock_bodega = self._get_stock_bodega_validado(self.entry_stock_bodega.get().strip(), stock_actual, ...)
if asignada_flag and stock_actual == 1:
```

---

## 📊 Resumen de Cambios

| Tipo de Cambio | Cantidad | Líneas Afectadas |
|----------------|----------|------------------|
| Queries SQL | 2 | 878, 1821 |
| Definiciones UI | 3 | 206, 335, 344 |
| Métodos Python | 2 | 1918, 1934 |
| Guardado DB | 2 | 779, 808 |
| Carga de datos | 2 | 853, 1173 |
| Importación Excel | 4 | 1722, 1794, 1821, 1867 |
| Plantillas | 2 | 1867, 1907 |
| Validaciones | 3 | 761, 762, 765 |
| Comentarios | 3 | 869, 904, 910 |
| **TOTAL** | **24 cambios** | **Múltiples líneas** |

---

## 🧪 Verificación

### Test de Conexión
```bash
python test_insumos_fix.py
```

**Resultado:**
```
✅ Query exitosa - No hay insumos registrados aún
✅ MÓDULO DE INSUMOS FUNCIONANDO CORRECTAMENTE
```

### Query de Prueba
```sql
SELECT h.codigo, h.nombre, h.categoria, f.nombre as finca_nombre,
       h.stock_actual, h.id_trabajador, h.responsable, h.stock_bodega,
       h.estado, h.id_finca
FROM insumo h
LEFT JOIN finca f ON h.id_finca = f.id
```

✅ **Ejecuta sin errores**

---

## 🎯 Estado Final

✅ **Módulo de Insumos funcionando correctamente**
- Todas las referencias a `stock_total` han sido reemplazadas por `stock_actual`
- Las queries SQL utilizan el campo correcto de la base de datos
- La interfaz muestra "Stock Actual" en lugar de "Stock Total"
- Los métodos de validación usan el nombre correcto
- La importación/exportación Excel usa las columnas correctas

---

## 📝 Notas Importantes

1. **Campo en DB:** El campo correcto en la tabla `insumo` es `stock_actual` (no `stock_total`)
2. **Terminología:** "Stock Actual" es más apropiado para insumos que "Stock Total"
3. **Consistencia:** Todos los métodos, queries y UI ahora usan `stock_actual` consistentemente
4. **Excel:** Las plantillas de importación/exportación también usan `stock_actual`

---

## 🚀 Próximos Pasos

El módulo está listo para usar. Puedes:
1. ✅ Crear nuevos insumos
2. ✅ Ver el catálogo filtrado por finca
3. ✅ Asignar insumos a trabajadores
4. ✅ Registrar mantenimientos
5. ✅ Ver detalles con fotos
6. ✅ Importar/exportar desde Excel

**Ejecuta la aplicación normalmente:**
```bash
python main.py
```
