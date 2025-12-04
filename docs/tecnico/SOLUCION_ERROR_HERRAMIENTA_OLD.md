# Corrección de Error: "no such table: main.herramienta_old"

**Fecha**: 25 de noviembre de 2025  
**Módulo**: Herramientas - Mantenimiento  
**Estado**: ✅ RESUELTO

---

## 📋 Descripción del Problema

### Error Reportado
Al intentar registrar un mantenimiento en el módulo de Herramientas, aparecía el siguiente error:

```
Error: no se pudo guardar el mantenimiento: no such table: main.herramienta_old
```

### Síntomas
- ❌ No se podían registrar nuevos mantenimientos
- ❌ Error de tabla inexistente `herramienta_old`
- ✅ El resto de funcionalidades del módulo funcionaban correctamente

---

## 🔍 Análisis del Problema

### Causa Raíz

El problema fue causado por un **bug en las migraciones de base de datos** (específicamente migraciones 008 y 018):

1. **Migración 003** (original):
   - Creó tabla `mantenimiento_herramienta` correctamente
   - FK: `FOREIGN KEY (herramienta_id) REFERENCES herramienta(id)`

2. **Migración 008** (problema):
   ```python
   # Renombra herramienta a herramienta_old
   ALTER TABLE herramienta RENAME TO herramienta_old;
   
   # Crea nueva tabla herramienta
   CREATE TABLE herramienta (...);
   
   # Copia datos
   INSERT INTO herramienta SELECT ... FROM herramienta_old;
   
   # Elimina tabla temporal
   DROP TABLE herramienta_old;
   ```
   
   **PROBLEMA**: Al renombrar la tabla, SQLite automáticamente actualiza las FK de tablas dependientes para que apunten a `herramienta_old`. Cuando se elimina `herramienta_old`, las FK quedan apuntando a una tabla inexistente.

3. **Script normalizar_y_migrar.py** (también afectado):
   - Recreó la tabla `herramienta` para agregar CHECK constraint
   - No actualizó las FK de tablas dependientes
   - Dejó `mantenimiento_herramienta` con FK inválida

### Estado Encontrado

```sql
-- ANTES (INCORRECTO)
CREATE TABLE mantenimiento_herramienta (
    ...
    FOREIGN KEY (herramienta_id) REFERENCES "herramienta_old" (id) ON DELETE CASCADE
    --                                      ^^^^^^^^^^^^^^^^^ tabla inexistente
);
```

### Impacto
- **Severidad**: Alta (funcionalidad principal bloqueada)
- **Alcance**: Solo registro de mantenimientos
- **Datos**: No se perdieron datos (1 registro existente preservado)

---

## ✅ Solución Implementada

### 1. Diagnóstico y Detección

Creados scripts de verificación:

**verificar_tablas_bd.py**
- Lista todas las tablas en la BD
- Detecta tablas temporales residuales
- Verifica existencia de `herramienta` y `mantenimiento_herramienta`

**verificar_triggers_fks.py**
- Analiza foreign keys de todas las tablas
- Detecta referencias a tablas inexistentes
- Muestra el CREATE TABLE completo

**Resultado del diagnóstico:**
```
✅ Tabla 'herramienta' existe
✅ Tabla 'herramienta_old' NO existe (correcto)
⚠️  FK en mantenimiento_herramienta: herramienta_id → herramienta_old
```

### 2. Corrección Aplicada

**Script: corregir_fk_mantenimiento.py**

```python
# 1. Respaldar datos existentes
SELECT * FROM mantenimiento_herramienta

# 2. Eliminar tabla con FK incorrecta
DROP TABLE mantenimiento_herramienta

# 3. Recrear tabla con FK correcta
CREATE TABLE mantenimiento_herramienta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    herramienta_id INTEGER NOT NULL,
    tipo_mantenimiento TEXT,
    fecha_mantenimiento DATE NOT NULL,
    descripcion TEXT,
    costo REAL,
    proveedor_servicio TEXT,
    proximo_mantenimiento DATE,
    realizado_por TEXT,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_actual TEXT DEFAULT 'Activo' 
        CHECK(estado_actual IN ('Activo', 'Completado')),
    estado_previo_herramienta TEXT,
    fecha_completado DATE,
    FOREIGN KEY (herramienta_id) REFERENCES herramienta(id) ON DELETE CASCADE
    --                                      ^^^^^^^^^^^ tabla correcta
)

# 4. Restaurar datos
INSERT INTO mantenimiento_herramienta VALUES (...)

# 5. Recrear índices
CREATE INDEX idx_mant_estado ON mantenimiento_herramienta(...)
```

### 3. Verificación

**Script: probar_registro_mantenimiento.py**

Prueba completa:
1. ✅ Selecciona una herramienta existente
2. ✅ Registra un mantenimiento de prueba
3. ✅ Verifica con JOIN que se puede consultar
4. ✅ Elimina el registro de prueba

**Resultado:**
```
✅ PRUEBA EXITOSA
La tabla mantenimiento_herramienta funciona correctamente.
El error 'no such table: main.herramienta_old' ha sido resuelto.
```

---

## 📊 Estado Final

### Tabla Corregida

```sql
-- DESPUÉS (CORRECTO)
CREATE TABLE mantenimiento_herramienta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    herramienta_id INTEGER NOT NULL,
    tipo_mantenimiento TEXT,
    fecha_mantenimiento DATE NOT NULL,
    descripcion TEXT,
    costo REAL,
    proveedor_servicio TEXT,
    proximo_mantenimiento DATE,
    realizado_por TEXT,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_actual TEXT DEFAULT 'Activo' 
        CHECK(estado_actual IN ('Activo', 'Completado')),
    estado_previo_herramienta TEXT,
    fecha_completado DATE,
    FOREIGN KEY (herramienta_id) REFERENCES herramienta(id) ON DELETE CASCADE
    --                                      ^^^^^^^^^^^ ✅ correcto
);

CREATE INDEX idx_mant_estado 
ON mantenimiento_herramienta(estado_actual, herramienta_id);
```

### Verificación de FK

```bash
$ python verificar_triggers_fks.py

FOREIGN KEYS EN MANTENIMIENTO_HERRAMIENTA
======================================================================
✅ Foreign keys encontradas:
  • Columna: herramienta_id → Tabla: herramienta

✅ No hay referencias a herramienta_old en la definición
```

### Funcionalidad

✅ Registro de mantenimientos: **OPERATIVO**  
✅ Consultas con JOIN: **OPERATIVAS**  
✅ Eliminación en cascada: **CONFIGURADA**  
✅ Historial de mantenimientos: **FUNCIONAL**  

---

## 🛠️ Archivos Creados/Modificados

### Scripts de Corrección
```
✅ corregir_fk_mantenimiento.py         (corrección principal)
✅ verificar_y_corregir_mant.py         (verificación y corrección automática)
✅ scripts/migrations/019_fix_mantenimiento_fk.py  (migración correctiva)
```

### Scripts de Verificación
```
✅ verificar_tablas_bd.py               (estado de tablas)
✅ verificar_triggers_fks.py            (análisis de FK)
✅ probar_registro_mantenimiento.py    (prueba funcional)
✅ verificar_mantenimiento.bat          (script batch de verificación)
```

### Documentación
```
✅ SOLUCION_ERROR_HERRAMIENTA_OLD.md   (este documento)
```

---

## 🚀 Instrucciones para Usuarios

### Verificar que el Problema Está Resuelto

**Opción 1 - Desde Windows:**
```bash
verificar_mantenimiento.bat
```

**Opción 2 - Desde Python:**
```bash
python verificar_triggers_fks.py
python probar_registro_mantenimiento.py
```

**Resultado Esperado:**
```
✅ Foreign key: herramienta_id → herramienta
✅ PRUEBA EXITOSA
```

### Usar el Módulo de Mantenimiento

1. **Abrir FincaFacil**
2. **Ir a Herramientas → Mantenimiento**
3. **Seleccionar una herramienta**
4. **Llenar formulario de mantenimiento**
5. **Click en "Guardar Mantenimiento"**

**Resultado:**
- ✅ Se guarda sin errores
- ✅ Aparece en el historial
- ✅ El estado de la herramienta se actualiza

---

## 🔧 Solución de Problemas

### Si el Error Persiste

1. **Verificar estado de tablas:**
   ```bash
   python verificar_tablas_bd.py
   ```

2. **Verificar foreign keys:**
   ```bash
   python verificar_triggers_fks.py
   ```

3. **Si FK sigue apuntando a herramienta_old:**
   ```bash
   python corregir_fk_mantenimiento.py
   ```

4. **Verificar corrección:**
   ```bash
   python probar_registro_mantenimiento.py
   ```

### Errores Comunes

**Error: "FOREIGN KEY constraint failed"**
- **Causa**: Intentando registrar mantenimiento para herramienta inexistente
- **Solución**: Verificar que la herramienta existe en la tabla `herramienta`

**Error: "table mantenimiento_herramienta already exists"**
- **Causa**: Tabla no fue eliminada antes de recrear
- **Solución**: Agregar `DROP TABLE IF EXISTS` antes de `CREATE TABLE`

---

## 📚 Lecciones Aprendidas

### Para Futuras Migraciones

1. **Al recrear una tabla con FK:**
   ```python
   # CORRECTO: Actualizar todas las tablas dependientes
   
   # Paso 1: Crear tabla temporal SIN FK
   CREATE TABLE tabla_dependiente_new (...) -- sin FK
   
   # Paso 2: Copiar datos
   INSERT INTO tabla_dependiente_new SELECT * FROM tabla_dependiente
   
   # Paso 3: Eliminar tabla vieja
   DROP TABLE tabla_dependiente
   
   # Paso 4: Recrear tabla principal
   ALTER TABLE tabla_principal RENAME TO tabla_principal_new
   
   # Paso 5: Recrear tabla dependiente CON FK correcta
   CREATE TABLE tabla_dependiente (...) -- con FK a tabla_principal_new
   INSERT INTO tabla_dependiente SELECT * FROM tabla_dependiente_new
   DROP TABLE tabla_dependiente_new
   ```

2. **Siempre verificar FK después de migraciones:**
   ```python
   cur.execute("PRAGMA foreign_key_list(tabla)")
   fks = cur.fetchall()
   for fk in fks:
       tabla_ref = fk[2]
       # Verificar que tabla_ref existe
   ```

3. **Crear scripts de verificación:**
   - Verificar integridad de FK antes de commit
   - Probar operaciones básicas después de migración
   - Mantener respaldo de datos antes de cambios estructurales

---

## ✨ Conclusión

### Problema Resuelto ✅

El error "no such table: main.herramienta_old" ha sido completamente resuelto mediante:

1. **Identificación**: Detección de FK inválida en `mantenimiento_herramienta`
2. **Corrección**: Recreación de tabla con FK correcta
3. **Verificación**: Pruebas funcionales exitosas
4. **Documentación**: Scripts y guías para prevenir recurrencia

### Estado del Sistema

- ✅ Base de datos: **CORRECTA**
- ✅ Foreign keys: **VÁLIDAS**
- ✅ Registro de mantenimientos: **FUNCIONAL**
- ✅ Consultas y reportes: **OPERATIVOS**

### Recomendaciones

1. ✅ Ejecutar `verificar_mantenimiento.bat` periódicamente
2. ✅ Mantener respaldos antes de aplicar migraciones
3. ✅ Revisar FK después de modificaciones estructurales
4. ✅ Usar la migración 019 en nuevas instalaciones

---

**Documentado por**: GitHub Copilot  
**Fecha de corrección**: 25 de noviembre de 2025  
**Estado**: ✅ RESUELTO Y VERIFICADO

---
