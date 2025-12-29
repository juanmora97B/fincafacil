# 📊 FASE 9.0.4.1 — Auditoría Pasiva: Catálogo Causa de Muerte

**Estado:** ✅ AUDITORÍA COMPLETADA  
**Fecha:** 2025-12-19  
**Dominio:** Configuración  
**Catálogo:** Causa de Muerte  
**Archivo:** `src/modules/configuracion/causa_muerte.py`

---

## 📋 Resumen Ejecutivo

### Resultado
- 4 métodos con SQL directo en UI
- 4× `get_connection()`; 6× `cursor.execute()`; 3× `commit()`
- Estados hardcoded: "Activo"/"Inactivo"; tipos causa predefinidos
- Flujos mapeados: listado, alta, edición (placeholder), activación/desactivación, importación

---

## 🔍 Inventario de Violaciones

| Método | get_connection | execute | commit | Notas |
|--------|-----------------|---------|--------|-------|
| `guardar_causa()` | 1 | 1 | 1 | INSERT con estado="Activo" hardcoded |
| `cargar_causas()` | 1 | 1 | 0 | SELECT con filtro estado='Activo' |
| `eliminar_causa()` | 1 | 1 | 1 | UPDATE estado='Inactivo' (soft delete) |
| `importar_excel()` | 1 | 3 | 1 | SELECT COUNT, INSERT en loop |
| **TOTAL** | **4** | **6** | **3** | 4 métodos con SQL |

---

## 🧭 Flujos Identificados

### 1. Listado (Lectura)
- `cargar_causas()` → SELECT `codigo, descripcion, tipo_causa, comentario` WHERE `estado='Activo'`

### 2. Alta (Escritura)
- `guardar_causa()` → INSERT `codigo, descripcion, tipo_causa, comentario, estado='Activo'`

### 3. Edición (Escritura)
- `editar_causa()` → Placeholder (solo mensaje)

### 4. Activación/Desactivación (Escritura)
- `eliminar_causa()` → UPDATE `estado='Inactivo'` por `codigo` (soft delete)

### 5. Importación (Bulk)
- `importar_excel()` → SELECT COUNT por `codigo`, INSERT múltiples con campos: `codigo, descripcion, tipo_causa, comentario, estado`

---

## 🧱 Estados y Validaciones en UI
- Estado hardcoded: "Activo" al crear, "Inactivo" al eliminar
- Tipos predefinidos de causa: [Enfermedad, Accidente, Natural, Sacrificio, Otros]
- Validación de obligatorios: código y descripción
- Unicidad: via SELECT COUNT + IntegrityError

---

## 🏗️ Esquema inferido
```sql
CREATE TABLE causa_muerte (
  codigo TEXT PRIMARY KEY,
  descripcion TEXT NOT NULL,
  tipo_causa TEXT,
  comentario TEXT,
  estado TEXT NOT NULL CHECK(estado IN ('Activo','Inactivo'))
);
```

---

## ✅ Conclusión
- Complejidad: Baja
- Riesgo: Bajo-Medio (estados y bulk import)
- Recomendación: Extender `ConfiguracionRepository/Service` y migrar UI conforme patrón Week 3.
