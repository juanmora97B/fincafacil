# Correcciones de Errores - FincaFacil
**Fecha:** 16 de Noviembre, 2025

## Problemas Identificados y Solucionados

### 1. ❌ Error: "no such table: servicio"
**Problema:** El sistema de notificaciones intentaba consultar una tabla `servicio` que no existía en el esquema de la base de datos.

**Solución:**
- ✅ Creada tabla `servicio` en `database/database.py` con la siguiente estructura:
  - `id` (PRIMARY KEY)
  - `id_hembra` (FK a animal)
  - `id_macho` (FK a animal)
  - `fecha_servicio`
  - `tipo_servicio` (Monta Natural / Inseminación Artificial)
  - `estado` (Servida / Gestante / Vacía / Parida / Aborto)
  - `fecha_parto_estimada`
  - `fecha_parto_real`
  - `observaciones`
  - `fecha_creacion`

- ✅ Creado script de migración: `scripts/migrations/004_add_servicio_table.py`
- ✅ Creado archivo batch: `aplicar_migracion_004.bat`
- ✅ Migración aplicada exitosamente a la base de datos

**Archivos modificados:**
- `database/database.py` (líneas 305-319)
- `scripts/migrations/004_add_servicio_table.py` (nuevo)
- `aplicar_migracion_004.bat` (nuevo)

---

### 2. ❌ Error: "no such column: t.medicamento"
**Problema:** El sistema de notificaciones buscaba la columna `medicamento` en la tabla `tratamiento`, pero la columna se llama `producto`.

**Solución:**
- ✅ Actualizado query en `modules/utils/notificaciones.py` línea 211:
  - Cambiado `t.medicamento` → `t.producto`
- ✅ Actualizada variable en el código (línea 220):
  - Cambiado `medicamento` → `producto`
- ✅ Actualizado diccionario de datos (línea 238):
  - Cambiado clave `'medicamento'` → `'producto'`

**Archivos modificados:**
- `modules/utils/notificaciones.py` (líneas 211, 220, 238)

---

### 3. ❌ Error: "'font' option forbidden, because would be incompatible with scaling"
**Problema:** El widget `CTkTextbox` no soporta configuración de fuentes en tags mediante tuplas cuando el escalado está activo.

**Solución:**
- ✅ Eliminadas todas las configuraciones `font=("Segoe UI", ...)` de los tags
- ✅ Mantenidas solo las configuraciones de `foreground` para colores
- ✅ El sistema ahora usa la fuente predeterminada del widget con colores aplicados

**Archivos modificados:**
- `modules/dashboard/dashboard_main.py` (líneas 586-598)

**Tags afectados:**
- `titulo_alta`, `alta`, `detalle_alta`
- `titulo_media`, `media`, `detalle_media`
- `titulo_baja`, `baja`, `detalle_baja`
- `exito`, `info`, `titulo_info`

---

### 4. ❌ Error: "invalid command name" al cerrar la aplicación
**Problema:** Callbacks programados con `.after()` no se cancelaban al cerrar la ventana, causando errores cuando intentaban ejecutarse después de destruir widgets.

**Solución:**
- ✅ Mejorado método `on_closing()` en `main.py`
- ✅ Agregado código para cancelar todos los callbacks pendientes:
  ```python
  for after_id in self.tk.eval('after info').split():
      try:
          self.after_cancel(after_id)
      except:
          pass
  ```
- ✅ Cambiado `self.destroy()` por `self.quit()` seguido de `self.destroy()` para limpiar correctamente el event loop

**Archivos modificados:**
- `main.py` (líneas 386-396)

---

## Plantillas de Importación Corregidas

### Plantillas Creadas/Corregidas:
1. ✅ `plantilla_animales.xlsx` - Agregado campo "Condición Corporal" y "Comentario"
2. ✅ `plantilla_tipo_explotacion.xlsx` - Agregados campos "Categoría" y "Comentario"
3. ✅ `plantilla_finca.xlsx` - Creada con campos "Nombre" y "Comentario"
4. ✅ `plantilla_sector.xlsx` - Creada con campos "Nombre" y "Comentario"
5. ✅ `plantilla_lote.xlsx` - Creada con campos "Nombre" y "Comentario"
6. ✅ `plantilla_condicion_corporal.xlsx` - Creada con campos "Condición Corporal" y "Comentario"

**Ubicación:** `plantillas de carga/`

---

## Pruebas Realizadas

### ✅ Migración de Base de Datos
```
Creando tabla 'servicio'...
✓ Tabla 'servicio' creada correctamente
✅ Migración completada exitosamente
```

---

## Próximos Pasos Recomendados

1. **Ejecutar la aplicación** para verificar que todos los errores fueron corregidos
2. **Probar el sistema de notificaciones** para verificar que detecta partos y tratamientos
3. **Verificar las plantillas de importación** con datos reales
4. **Crear módulo de gestión de servicios** para aprovechar la nueva tabla `servicio`

---

## Notas Técnicas

- La tabla `servicio` permite gestionar servicios de reproducción (montas e inseminaciones)
- El campo `fecha_parto_estimada` se puede calcular automáticamente sumando 280 días a `fecha_servicio`
- Los estados disponibles permiten seguimiento completo del ciclo reproductivo
- Las correcciones son retrocompatibles y no afectan funcionalidad existente

---

## Resumen de Cambios

| Categoría | Archivos Modificados | Archivos Nuevos |
|-----------|---------------------|-----------------|
| Base de Datos | 1 | 1 |
| Módulos | 2 | 0 |
| Scripts | 0 | 1 |
| Plantillas | 0 | 6 |
| Batch | 0 | 1 |
| **TOTAL** | **3** | **9** |
