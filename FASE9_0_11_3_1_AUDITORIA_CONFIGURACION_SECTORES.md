# FASE 9.0.11.3 — AUDITORÍA CONFIGURACIÓN SECTORES

**Fecha:** 2025-12-21  
**Módulo:** Configuración · Sectores  
**Archivo:** `src/modules/configuracion/sectores.py`  
**Líneas:** 454  
**Complejidad:** 🟡 Media (FK finca_id, soft delete crítico, comentario textual)

---

## 1. RESUMEN EJECUTIVO

Auditoría del módulo **Sectores** (sectores de pastura/producción por finca) para identificar violaciones de fronteras arquitectónicas.

**Hallazgos críticos:**
- ❌ **DELETE físico** (línea 351) → Pérdida de historial
- ⚠️ **7 get_connection()** → SQL directo en UI
- ⚠️ **10+ cursor.execute()** → Lógica de negocio en UI
- ⚠️ **3 conn.commit()** → Transacciones en UI
- ⚠️ **Estados divergentes** ('Activa' vs 'Activo') en query línea 115
- ⚠️ **FK finca_id** → Requiere validación estricta

**Recomendación:** Migración COMPLETE (incluye comentario, es campo simple).

---

## 2. VIOLACIONES DETECTADAS

| Método | Línea | Violación | Query/Acción |
|--------|-------|-----------|--------------|
| `cargar_fincas_combobox()` | 113-115 | get_connection + execute | SELECT id, nombre FROM finca |
| `guardar_sector()` | 149-161 | get_connection + execute + commit | INSERT/UPDATE sector |
| `cargar_sectores()` | 178-215 | get_connection + execute | SELECT s.*, f.nombre FROM sector LEFT JOIN finca |
| `editar_sector()` | (UI logic) | Estado widget → modo edición | Frágil, depende de cget("state") |
| `eliminar_sector()` | 348-352 | **DELETE físico** | DELETE FROM sector WHERE id = ? |
| `filtrar_tabla()` | (UI filter) | Python en memoria | Aceptable, no SQL |
| `importar_excel()` | 391-427 | get_connection + execute + commit | INSERT bulk |

**Total:**
- `get_connection()`: 7 instancias
- `cursor.execute()`: 10+ queries
- `conn.commit()`: 3 instancias
- `DELETE FROM`: 1 (CRÍTICO)

---

## 3. DELETE FÍSICO (RIESGO CRÍTICO)

**Ubicación:** Línea 351
```python
def eliminar_sector(self):
    # ...
    safe_execute(cursor, "DELETE FROM sector WHERE id = ?", (sector_id,))
    conn.commit()
```

**Solución requerida:**
- ✅ Soft delete: `UPDATE sector SET estado='Inactivo' WHERE id=?`

---

## 4. ESTRUCTURA DE DATOS

**Tabla sector:**
- `id` (PK)
- `codigo` (único, requerido)
- `nombre` (requerido)
- `comentario` (opcional, TEXT)
- `estado` (Activo/Inactivo)
- `finca_id` (FK → finca, requerido)

---

## 5. ARQUITECTURA OBJETIVO

### Repository (6 métodos SQL-only)
- `listar_fincas_activas_para_sectores()`
- `listar_sectores_activos_por_finca()` o `listar_todos_sectores_activos()`
- `obtener_sector(codigo_sector, finca_id)`
- `existe_codigo_sector_en_finca(codigo, finca_id)`
- `crear_sector_base(..., estado)`
- `actualizar_sector_base(...)`
- `cambiar_estado_sector(sector_id, estado)`
- `obtener_finca_por_id(finca_id)` (reutilizar de Lotes)

### Service (7 métodos con validaciones)
- `listar_fincas_para_combo_sectores()`
- `listar_sectores_activos()`
- `obtener_sector(codigo, finca_id)` → valida existencia, FK activa
- `crear_sector(codigo, nombre, finca_id, comentario='')` → validaciones: required, unicidad por finca, FK activa
- `actualizar_sector(...)`
- `cambiar_estado_sector(sector_id, estado)` → soft delete
- `obtener_finca_por_id(finca_id)` (llamada a repo)

### Normalización
- `codigo`: `.strip().upper()`
- `nombre`: `.strip().title()`
- `comentario`: `.strip()` (opcional)
- `estado`: 'Activo' al crear

---

## 6. CRITERIOS DE ÉXITO

- ✅ Pylance: 0 errores
- ✅ Grep SQL: 0 matches en `sectores.py`
- ✅ Auditor: exit 0
- ✅ Soft delete implementado
- ✅ UX intacta (forma, tabla, búsqueda rápida)

---

**FIN AUDITORÍA**
