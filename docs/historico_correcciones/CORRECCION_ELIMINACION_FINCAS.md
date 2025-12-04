# Corrección de Eliminación de Fincas

## Problema Reportado
Usuario experimentaba dos errores al intentar eliminar fincas en el módulo de configuración:
1. **"No se encontró la finca seleccionada"** - Error en la lógica de selección/ID
2. **"FOREIGN KEY constraint failed"** - Restricciones de integridad referencial bloqueaban la eliminación

## Análisis del Problema

### FK Constraints Encontradas
Al investigar la base de datos, se identificaron 7 tablas que referencian `finca` con `ON DELETE NO ACTION` (comportamiento predeterminado de SQLite):

1. `animal.id_finca`
2. `potrero.id_finca`
3. `insumo.id_finca`
4. `herramienta.id_finca`
5. `sector.finca_id`
6. `lote.finca_id`
7. `animal_legacy.id_finca`

### Complicaciones Durante Migración
- **Referencias residuales**: Tablas `animal_legacy` y `movimiento_insumo` tenían FKs que apuntaban a la tabla temporal `potrero_old` de migraciones previas
- **Auto-referencias en animal**: La tabla `animal` tiene FKs auto-referenciadas (id_madre, id_padre) que causaban "foreign key mismatch" durante recreación
- **Migraciones parciales**: Múltiples intentos de migración dejaron tablas `_old` y estados inconsistentes

## Solución Implementada

### 1. Scripts de Diagnóstico
**`scripts/utilities/check_db_state.py`**
- Lista todas las tablas en la BD
- Muestra FKs de tablas específicas con sus acciones ON DELETE
- Detecta tablas temporales residuales

**`scripts/utilities/find_potrero_old_refs.py`**
- Busca referencias a tablas temporales `*_old`
- Identificó referencias incorrectas en `animal_legacy` y `movimiento_insumo`

**`scripts/utilities/verify_finca_fks.py`**
- Verificación completa de todas las FKs que referencian `finca`
- Muestra estado de cada FK (✔ correcto / ❌ necesita fix)
- Reporte final con estadísticas

### 2. Scripts de Corrección
**`scripts/utilities/fix_animal_potrero_fk.py`**
- Corrige FK `animal.id_potrero` que apuntaba a `potrero_old` en lugar de `potrero`
- Usa `PRAGMA foreign_keys = OFF` para manejar auto-referencias
- Patrón: RENAME TO _temp → CREATE nueva → INSERT → DROP temp

**`scripts/utilities/fix_all_potrero_old_refs.py`**
- Corrige FKs residuales en `animal_legacy` y `movimiento_insumo`
- Actualiza referencias de `potrero_old` a `potrero`

**`scripts/utilities/cleanup_temp_tables.py`**
- Elimina tablas temporales `*_old` de migraciones fallidas
- Usado preventivamente antes de nuevas migraciones

### 3. Migraciones de Schema
**`scripts/migrations/008_allow_delete_finca.py`** (Parcialmente exitosa)
- Migró `animal` correctamente
- Falló en tablas subsecuentes por errores de sintaxis y referencias a `potrero_old`

**`scripts/migrations/008B_complete_finca_fk_fix.py`** (No completada)
- Incluía lógica para verificar estado actual de FKs antes de migrar
- Falló debido a referencias residuales no resueltas

**`scripts/migrations/008C_fix_sector_fk.py`** ✔
- Migración específica para `sector.finca_id`
- Cambió ON DELETE de NO ACTION a SET NULL
- Ejecutada exitosamente

**`scripts/migrations/008D_fix_lote_fk.py`** ✔
- Migración específica para `lote.finca_id`
- Última tabla pendiente de corrección
- Ejecutada exitosamente

### 4. Actualización del Código de Aplicación
**`modules/configuracion/fincas.py` - Método `eliminar_finca()`**

**ANTES:**
```python
# Código complejo con cascadas manuales
cursor.execute("SELECT id FROM finca WHERE codigo = ?", (codigo,))
row = cursor.fetchone()
finca_id = row[0] if isinstance(row, tuple) else row[0]

# Eliminación manual de potreros
cursor.execute("DELETE FROM potrero WHERE id_finca = ?", (finca_id,))

# Comentarios indicando tablas no eliminadas por seguridad
cursor.execute("DELETE FROM finca WHERE codigo = ?", (codigo,))
```

**DESPUÉS:**
```python
# Código simplificado - FKs manejan la integridad
try:
    codigo = self.tabla.item(seleccionado[0])["values"][0]
except (IndexError, KeyError):
    messagebox.showerror("Error", "No se pudo obtener el código...")
    return

cursor.execute("DELETE FROM finca WHERE codigo = ?", (codigo,))

if cursor.rowcount == 0:
    messagebox.showerror("Error", "No se encontró la finca seleccionada.")
    return
```

**Mejoras:**
- Manejo robusto de excepciones al obtener el código de la finca seleccionada
- Eliminación de lógica de cascada manual (ahora manejada por FKs)
- Verificación de `rowcount` para confirmar que se eliminó un registro
- Comentarios explicando que las FKs ON DELETE SET NULL mantienen la integridad

## Patrón de Migración Utilizado

Para cada tabla que necesitaba corrección:

```python
# 1. Deshabilitar FKs (necesario para auto-referencias)
cur.execute("PRAGMA foreign_keys = OFF;")

# 2. Obtener estructura actual
cur.execute("PRAGMA table_info(tabla)")
columns = cur.fetchall()

# 3. Renombrar tabla existente
cur.execute("ALTER TABLE tabla RENAME TO tabla_old;")

# 4. Crear tabla nueva con FK corregida
cur.execute("""
    CREATE TABLE tabla (
        column1 TYPE,
        column2 TYPE,
        ...
        FOREIGN KEY (finca_id) REFERENCES finca (id) ON DELETE SET NULL
    )
""")

# 5. Copiar datos
cur.execute("INSERT INTO tabla SELECT * FROM tabla_old;")

# 6. Eliminar tabla temporal
cur.execute("DROP TABLE tabla_old;")

# 7. Rehabilitar FKs
cur.execute("PRAGMA foreign_keys = ON;")

conn.commit()
```

## Resultado Final

### Estado de FKs (Verificado con `verify_finca_fks.py`)
```
✔ potrero.id_finca -> finca(id) | ON DELETE SET NULL
✔ animal.id_finca -> finca(id) | ON DELETE SET NULL
✔ insumo.id_finca -> finca(id) | ON DELETE SET NULL
✔ animal_legacy.id_finca -> finca(id) | ON DELETE SET NULL
✔ herramienta.id_finca -> finca(id) | ON DELETE SET NULL
✔ sector.finca_id -> finca(id) | ON DELETE SET NULL
✔ lote.finca_id -> finca(id) | ON DELETE SET NULL
```

**7 tablas afectadas** - Todas correctamente configuradas

### Comportamiento Actual
Cuando se elimina una finca:
- Los registros en tablas dependientes **no se eliminan**
- Las columnas FK (`id_finca`, `finca_id`) se establecen en `NULL`
- Los datos históricos se preservan (animales, insumos, herramientas, etc.)
- No se genera error de FOREIGN KEY constraint

### Archivos Modificados
- ✅ `modules/configuracion/fincas.py` - Método eliminar_finca() simplificado
- ✅ 7 tablas migradas con nuevas definiciones FK
- ✅ 9 scripts utilitarios creados para diagnóstico y corrección

## Pruebas Recomendadas

1. **Prueba de eliminación básica**
   - Crear finca de prueba
   - Eliminarla → Debe mostrar "Finca eliminada correctamente"
   
2. **Prueba con dependencias**
   - Crear finca con potrero, animal, insumo asociados
   - Eliminar finca
   - Verificar que registros dependientes tengan `id_finca = NULL`
   - Verificar que registros dependientes sigan existiendo

3. **Prueba de error de selección**
   - Hacer clic en botón eliminar sin seleccionar finca
   - Debe mostrar "Seleccione una finca para eliminar"

## Notas de Mantenimiento

- **ON DELETE SET NULL** es apropiado para estas relaciones porque la finca es información contextual, no propietaria
- Si en el futuro se requiere eliminación en cascada, cambiar `SET NULL` a `CASCADE` en las migraciones
- Siempre ejecutar migraciones con `PRAGMA foreign_keys = OFF/ON` cuando hay auto-referencias
- Las tablas `*_old` deben limpiarse inmediatamente después de migraciones exitosas

## Lecciones Aprendidas

1. **Verificar todas las dependencias antes de migrar**: La tabla `lote` casi se pasa por alto
2. **Buscar referencias a tablas temporales**: `potrero_old` causó múltiples fallas
3. **Descomponer migraciones grandes**: Mejor hacer migraciones específicas por tabla que una masiva
4. **Validación continua**: Scripts de verificación fueron clave para detectar problemas
5. **Deshabilitar FKs temporalmente**: Necesario para manejar auto-referencias en `animal`

---

**Fecha**: 2024
**Versión BD**: Post-migración 008D
**Estado**: ✔ Completado y verificado
