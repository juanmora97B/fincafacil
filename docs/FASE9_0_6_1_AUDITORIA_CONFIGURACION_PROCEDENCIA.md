# FASE 9.0.6 — PASO 1: Auditoría Pasiva · Configuración · Procedencia

**Estado:** ✅ Completada  
**Fecha:** 2025-12-19  
**Archivo auditado:** `src/modules/configuracion/procedencia.py`

---

## 📊 Hallazgos Cuantitativos

### Violaciones de Frontera UI → BD
- **get_connection:** 5 instancias
  - Línea ~127 (guardar_procedencia: INSERT/UPDATE)
  - Línea ~171 (cargar_procedencias: SELECT activos)
  - Línea ~185 (editar_procedencia: SELECT por código)
  - Línea ~212 (eliminar_procedencia: DELETE)
  - Línea ~248 (importar_excel: SELECT COUNT + INSERT por fila)

- **cursor.execute:** 8 queries SQL directas
  - UPDATE procedencia (edición)
  - INSERT procedencia (alta)
  - SELECT ... WHERE estado='Activo' (listado)
  - SELECT ... WHERE codigo=? (detalle para edición)
  - DELETE FROM procedencia (eliminación HARD, no soft)
  - SELECT COUNT duplicados (importación)
  - INSERT bulk (importación)

- **conn.commit:** 4 instancias
  - guardar_procedencia (línea ~159)
  - eliminar_procedencia (línea ~215)
  - importar_excel (línea ~286)

### Estados y Tipos Hardcoded
- **Estados:** "Activo" (usado en INSERT y SELECT)
- **Tipos Procedencia (combo):** 
  - "Granja", "Centro Acopio", "Importación", "Producción Interna", "Otros"

---

## 🗺️ Mapa CRUD Detectado

### ✅ Listado (READ)
```python
# cargar_procedencias() - Línea ~171
SELECT codigo, descripcion, tipo_procedencia, ubicacion, comentario 
FROM procedencia 
WHERE estado = 'Activo'
```

### ✅ Alta (CREATE)
```python
# guardar_procedencia() - Línea ~146 (INSERT branch)
INSERT INTO procedencia (codigo, descripcion, tipo_procedencia, ubicacion, comentario, estado)
VALUES (?, ?, ?, ?, ?, 'Activo')
```

### ✅ Edición (UPDATE)
```python
# guardar_procedencia() - Línea ~136 (UPDATE branch)
# + editar_procedencia() - Línea ~185 (carga datos para form)
UPDATE procedencia 
SET descripcion = ?, tipo_procedencia = ?, ubicacion = ?, comentario = ?
WHERE codigo = ?

# Carga de datos para edición:
SELECT codigo, descripcion, tipo_procedencia, ubicacion, comentario 
FROM procedencia WHERE codigo = ?
```

### ⚠️ Eliminación (DELETE HARD)
```python
# eliminar_procedencia() - Línea ~214
DELETE FROM procedencia WHERE codigo = ?
```

**⚠️ RIESGO CRÍTICO:** Elimina físicamente el registro. Otros catálogos usan soft delete (estado='Inactivo').

### ✅ Importación (BULK CREATE)
```python
# importar_excel() - Línea ~248+
# Por cada fila:
SELECT COUNT(*) FROM procedencia WHERE codigo = ?  # Validar duplicado
INSERT INTO procedencia (...) VALUES (?, ?, ?, ?, ?, ?)  # Inserción
```

---

## 🚨 Riesgos Identificados

### 1. DELETE sin Soft Delete (CRÍTICO)
**Problema:**  
- `eliminar_procedencia()` usa `DELETE FROM procedencia WHERE codigo = ?`
- No respeta patrón soft-delete usado en otros catálogos (Causa de Muerte, Diagnósticos)

**Impacto:**  
- Pérdida irreversible de datos
- Inconsistencia con arquitectura de otros catálogos
- Imposibilidad de auditoría histórica

**Mitigación:**  
- Cambiar a `UPDATE procedencia SET estado = 'Inactivo' WHERE codigo = ?`
- Mantener mensaje UX ("eliminada") pero hacer soft delete en backend

---

### 2. SQL Embebido en Handlers (ALTO)
**Problema:**  
- 5 métodos UI con SQL directo
- Conocimiento de estructura de tablas en capa de presentación

**Impacto:**  
- Cambios de esquema requieren modificar UI
- Testing imposible sin BD real
- Violación de arquitectura por capas

**Mitigación:**  
- Migrar todo SQL a `ConfiguracionRepository`
- UI solo llama `ConfiguracionService`

---

### 3. Validaciones en UI (MEDIO)
**Problema:**  
- Validación de campos obligatorios (código/descripción) en UI
- Validación de duplicados en importación (SELECT COUNT inline)

**Impacto:**  
- Lógica duplicada si otro módulo usa procedencias
- Sin validaciones centralizadas

**Mitigación:**  
- Mover validaciones a `ConfiguracionService`

---

### 4. Edición con Estado Disabled (BAJO)
**Problema:**  
- `editar_procedencia()` deshabilita campo código (`state="disabled"`)
- `guardar_procedencia()` detecta modo con `self.entry_codigo.cget("state")`

**Impacto:**  
- Acoplamiento UI: lógica de negocio basada en estado de widget
- Dificulta testing

**Mitigación:**  
- Usar variable de instancia (`self.editando_codigo`) en lugar de estado de widget

---

## 📋 Plan de Migración (Pasos)

### PASO 2: Extender ConfiguracionRepository
Agregar métodos SQL-only:
- `listar_procedencias()` → SELECT activos
- `obtener_procedencia(codigo)` → SELECT por código (para edición)
- `existe_procedencia(codigo)` → validación duplicados
- `crear_procedencia(codigo, descripcion, tipo, ubicacion, comentario, estado)` → INSERT
- `actualizar_procedencia(codigo, descripcion, tipo, ubicacion, comentario)` → UPDATE
- `cambiar_estado_procedencia(codigo, estado)` → soft delete

**Nota:** Reemplazar DELETE por UPDATE estado.

---

### PASO 3: Extender ConfiguracionService
Agregar validaciones y orquestación:
- `listar_procedencias()` → normaliza valores NULL
- `crear_procedencia(...)` → valida:
  - Código/descripción obligatorios
  - No existe duplicado
  - Estado válido (Activo/Inactivo)
- `actualizar_procedencia(...)` → valida:
  - Código existe
  - Descripción obligatoria
- `obtener_procedencia(codigo)` → para edición
- `cambiar_estado_procedencia(codigo, estado)` → soft delete validado

---

### PASO 4: Migrar UI
Refactorizar `procedencia.py`:
- Eliminar `import sqlite3` y `from database import db`
- Agregar `from infraestructura.configuracion import ConfiguracionService, ConfiguracionRepository`
- Inicializar service en `__init__`
- Reemplazar:
  - `guardar_procedencia()` → `service.crear/actualizar_procedencia()`
  - `cargar_procedencias()` → `service.listar_procedencias()`
  - `editar_procedencia()` → `service.obtener_procedencia()`
  - `eliminar_procedencia()` → `service.cambiar_estado_procedencia(..., "Inactivo")`
  - `importar_excel()` → loop con `service.crear_procedencia()` por fila
- Cambiar lógica de edición: usar `self.editando_codigo` en lugar de `entry_codigo.cget("state")`

---

### PASO 5: Validaciones Obligatorias
- [x] Pylance → 0 errores
- [x] Auditor fronteras → Exit 0
- [x] Grep SQL en UI → 0 matches

---

### PASO 6: Documentación
Crear:
- `FASE9_0_6_2_MIGRACION_CONFIGURACION_PROCEDENCIA.md`

Incluir:
- Cambio crítico: DELETE → soft delete
- Mejora: edición con variable de estado
- Métodos repository/service agregados
- Validaciones centralizadas

---

### PASO 7: Actualizar LOG
- Matriz: marcar Procedencia ✅
- Progreso: 6/13 (46%)
- Cronología: 2025-12-19 Week 6
- Siguiente: Motivos de Venta o Destino Venta

---

## 🎯 Dependencias Implícitas

### Tabla BD: `procedencia`
Campos detectados en queries:
- `codigo` (PK, TEXT)
- `descripcion` (TEXT NOT NULL)
- `tipo_procedencia` (TEXT, valores combo)
- `ubicacion` (TEXT nullable)
- `comentario` (TEXT nullable)
- `estado` (TEXT, valores: Activo/Inactivo)

**Nota:** Asumir que tabla existe (creada en migrations anteriores).

---

## ✅ Criterios de Éxito

Al finalizar migración:
- ✅ 0 SQL en UI
- ✅ Soft delete implementado
- ✅ Edición sin acoplamiento a widgets
- ✅ UX preservado (flujos, botones, mensajes)
- ✅ Pylance + Auditor limpios
- ✅ Documentación completa

---

**Próximo paso:** PASO 2 - Extender ConfiguracionRepository con métodos de Procedencia.
