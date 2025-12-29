# 🔍 FASE 8.5.1 — AUDITORÍA PASIVA DOMINIO SALUD

**Fecha:** 19 de diciembre de 2025  
**Fase:** FASE 8.5.1 — Auditoría sin modificar código  
**Objetivo:** Mapear estado real del dominio Salud antes de migración

---

## 📊 RESUMEN EJECUTIVO

### HALLAZGOS CRÍTICOS

- ✅ **1 archivo UI identificado**: salud_main.py (1016 líneas)
- 🟥 **60+ violaciones UI→BD** contadas
- 🟧 **Complejidad media-alta**: diagnósticos + tratamientos + alertas
- 🟨 **Patrón similar a Reproducción** (importa desde database.db)

---

## 📁 INVENTARIO DE ARCHIVOS

### ARCHIVOS DEL DOMINIO SALUD

| Archivo | Líneas | Tipo | Responsabilidad |
|---------|--------|------|-----------------|
| `src/modules/salud/salud_main.py` | 1016 | UI | Formularios diagnósticos + tratamientos |
| `src/modules/salud/__init__.py` | 1 | Export | Exporta SaludModule |

**Total archivos:** 2  
**Total líneas UI:** 1016

---

## 🔴 CONTEO DE VIOLACIONES

### ACCESOS DIRECTOS A BD

| Tipo de Violación | Cantidad | Líneas Ejemplo |
|-------------------|----------|----------------|
| `db.get_connection()` | 15 | L178, L222, L243, L270, L292, L313, L340, L375, L405, L442, L500, L771, L836, L890, L955 |
| `cursor.execute()` (SELECT) | 25+ | L224, L246, L272, L294, L316, L342, L407, L839, L893, L957 |
| `cursor.execute()` (INSERT) | 6 | L182, L197, L377, L801 |
| `cursor.execute()` (UPDATE) | 2 | L503 |
| `cursor.execute()` (CREATE TABLE) | 2 | L182, L775 (inicialización) |
| `conn.commit()` | 4 | L215, L395, L508, L822 |
| **TOTAL** | **60+** | Distribuidas en 1016 líneas |

---

## 🧩 FLUJOS CRÍTICOS IDENTIFICADOS

### 1️⃣ REGISTRO DE DIAGNÓSTICO

**Archivo:** salud_main.py  
**Método:** `guardar_diagnostico()` (L364-395)  
**Complejidad:** Media

**SQL Embebido:**
```python
# Línea 377
cur.execute("SELECT id FROM animal WHERE id = ?", (animal_id,))

# Línea 383
cur.execute("""
    INSERT INTO diagnostico_evento (animal_id, fecha, tipo, detalle, 
                                   severidad, estado, observaciones)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (...))

# Línea 395
conn.commit()
```

**Violaciones:** 3 (1 SELECT + 1 INSERT + 1 commit)  
**Riesgo:** Medio (validaciones en UI)

---

### 2️⃣ REGISTRO DE TRATAMIENTO

**Archivo:** salud_main.py  
**Método:** `guardar_tratamiento()` (L756-822)  
**Complejidad:** Alta

**SQL Embebido:**
```python
# Línea 775 - CREATE TABLE inline (!!!)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tratamiento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_animal INTEGER NOT NULL,
        ...
    )
""")

# Línea 794
cursor.execute("SELECT id FROM animal WHERE id = ? AND estado = 'Activo'", (animal_id,))

# Línea 801
cursor.execute("""
    INSERT INTO tratamiento (
        id_animal, fecha_inicio, tipo_tratamiento, producto, 
        dosis, veterinario, comentario, fecha_proxima
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (...))

# Línea 822
conn.commit()
```

**Violaciones:** 4 (1 CREATE + 1 SELECT + 1 INSERT + 1 commit)  
**Riesgo:** Alto (CREATE TABLE en runtime, transacción manual)

---

### 3️⃣ CARGAR HISTORIAL DE DIAGNÓSTICOS

**Archivo:** salud_main.py  
**Método:** `cargar_historial()` (L400-429)  
**Complejidad:** Media

**SQL Embebido:**
```python
# Línea 407 - JOIN complejo
cur.execute("""
    SELECT d.id, d.fecha, a.codigo || ' ' || COALESCE(a.nombre, ''),
           d.tipo, SUBSTR(d.detalle, 1, 50) || CASE WHEN LENGTH(d.detalle) > 50 THEN '...' ELSE '' END,
           d.severidad, d.estado
    FROM diagnostico_evento d
    JOIN animal a ON d.animal_id = a.id
    ORDER BY d.fecha DESC
    LIMIT 100
""")
```

**Violaciones:** 1 SELECT (JOIN + formateo en SQL)  
**Riesgo:** Bajo (solo lectura, pero lógica de presentación en SQL)

---

### 4️⃣ CARGAR TRATAMIENTOS

**Archivo:** salud_main.py  
**Método:** `cargar_tratamientos()` (L824-881)  
**Complejidad:** Media

**SQL Embebido:**
```python
# Línea 839 - JOIN complejo
cursor.execute("""
    SELECT 
        t.id,
        t.fecha_inicio,
        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
        t.tipo_tratamiento,
        t.producto,
        t.dosis,
        t.veterinario,
        t.fecha_proxima,
        t.comentario
    FROM tratamiento t
    JOIN animal a ON t.id_animal = a.id
    WHERE t.estado = 'Activo'
    ORDER BY t.fecha_inicio DESC
    LIMIT 100
""")
```

**Violaciones:** 1 SELECT (JOIN + filtros)  
**Riesgo:** Bajo (solo lectura)

---

### 5️⃣ PRÓXIMOS TRATAMIENTOS

**Archivo:** salud_main.py  
**Método:** `cargar_proximos_tratamientos()` (L883-950)  
**Complejidad:** Media

**SQL Embebido:**
```python
# Línea 893 - JOIN con filtro temporal
cursor.execute("""
    SELECT 
        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
        t.tipo_tratamiento,
        t.producto,
        t.fecha_proxima,
        t.comentario
    FROM tratamiento t
    JOIN animal a ON t.id_animal = a.id
    WHERE t.fecha_proxima IS NOT NULL 
    AND t.fecha_proxima >= date('now')
    AND t.estado = 'Activo'
    ORDER BY t.fecha_proxima ASC
    LIMIT 20
""")
```

**Violaciones:** 1 SELECT (JOIN + filtro temporal con date('now'))  
**Riesgo:** Bajo (solo lectura, lógica de fechas en SQL)

---

### 6️⃣ ACTUALIZAR ESTADO DIAGNÓSTICO

**Archivo:** salud_main.py  
**Método:** `actualizar_estado()` (L488-512)  
**Complejidad:** Baja

**SQL Embebido:**
```python
# Línea 503 (dentro de función anidada)
cur.execute("UPDATE diagnostico_evento SET estado = ? WHERE id = ?", 
           (cb_nuevo.get(), sel[0]))
conn.commit()
```

**Violaciones:** 2 (1 UPDATE + 1 commit)  
**Riesgo:** Medio (UI crea modal con callback que ejecuta SQL)

---

### 7️⃣ VER DETALLE DIAGNÓSTICO

**Archivo:** salud_main.py  
**Método:** `ver_detalle()` (L431-486)  
**Complejidad:** Baja

**SQL Embebido:**
```python
# Línea 442 - JOIN para obtener detalles
cur.execute("""
    SELECT d.fecha, a.codigo || ' ' || COALESCE(a.nombre, ''),
           d.tipo, d.detalle, d.severidad, d.estado, d.observaciones
    FROM diagnostico_evento d
    JOIN animal a ON d.animal_id = a.id
    WHERE d.id = ?
""", (evento_id,))
```

**Violaciones:** 1 SELECT (JOIN)  
**Riesgo:** Bajo (solo lectura)

---

### 8️⃣ CARGAR CATÁLOGOS (FINCAS, ANIMALES)

**Archivo:** salud_main.py  
**Métodos:** `cargar_fincas()`, `cargar_animales()`, `actualizar_animales_por_finca()`, etc.  
**Complejidad:** Baja (repetido 6 veces)

**SQL Embebido (ejemplos):**
```python
# L224 - Fincas
cur.execute("SELECT nombre FROM finca WHERE estado = 'Activo' ORDER BY nombre")

# L246 - Animales por finca
cur.execute("""
    SELECT a.id, a.codigo, a.nombre FROM animal a
    WHERE a.id_finca = (SELECT id FROM finca WHERE nombre = ? AND estado = 'Activo')
    AND a.estado = 'Activo'
    ORDER BY a.codigo
""", (finca_seleccionada,))

# L272 - Todos los animales
cur.execute("""
    SELECT id, codigo, nombre FROM animal 
    WHERE estado = 'Activo'
    ORDER BY codigo
""")
```

**Violaciones:** 12+ SELECTs (catálogos duplicados entre diagnósticos y tratamientos)  
**Riesgo:** Bajo (solo lectura, pero código duplicado)

---

## 📊 CLASIFICACIÓN DE VIOLACIONES

### 🟥 CRÍTICAS (ALTA PRIORIDAD)

| Violación | Ubicación | Motivo |
|-----------|-----------|--------|
| CREATE TABLE en runtime | `guardar_tratamiento()` L775 | Lógica de esquema en UI |
| Transacciones manuales | `guardar_diagnostico()`, `guardar_tratamiento()` | Commit/rollback en UI |
| Validaciones en UI | `guardar_diagnostico()` L377, `guardar_tratamiento()` L794 | SELECT antes de INSERT |
| Formateo en SQL | `cargar_historial()` L407, `cargar_tratamientos()` L839 | Lógica de presentación en SQL |

**Total:** 10+ violaciones críticas

---

### 🟧 LEGACY ACTIVO (MEDIA PRIORIDAD)

| Violación | Ubicación | Motivo |
|-----------|-----------|--------|
| Catálogos duplicados | `cargar_fincas()`, `cargar_fincas_trat()` | Mismo código repetido 2 veces |
| Filtros temporales en SQL | `cargar_proximos_tratamientos()` L893 | date('now') en SQL |
| JOINs con concatenación | Multiple lugares | Formateo de strings en SQL |

**Total:** 20+ violaciones legacy

---

### 🟨 EXCEPCIONES ACEPTABLES (BAJA PRIORIDAD)

| Violación | Ubicación | Motivo |
|-----------|-----------|--------|
| Inicialización de tablas | `_inicializar_tablas()` L176-215 | CREATE TABLE IF NOT EXISTS (bootstrap) |
| Límites de paginación | LIMIT 100 en SELECTs | Aceptable temporalmente |

**Total:** 2-3 excepciones

---

## 🔄 LÓGICA DE NEGOCIO DETECTADA

### CÁLCULOS Y VALIDACIONES EN UI

| Lógica | Ubicación | Debe migrar a Service |
|--------|-----------|----------------------|
| Validación de animal activo | `guardar_diagnostico()` L377 | ✅ SaludService.validar_animal() |
| Validación de animal activo | `guardar_tratamiento()` L794 | ✅ SaludService.validar_animal() |
| Formateo de fecha de registro | Multiple | ✅ SaludService o Repository |
| Truncado de comentarios (50 chars) | `cargar_historial()` L409 | ✅ UI puede mantener, o Service |
| Cálculo de próximos (>= now) | `cargar_proximos_tratamientos()` L898 | ✅ SaludService.listar_proximos() |

---

### REGLAS DE NEGOCIO IMPLÍCITAS

1. **Diagnósticos:**
   - Severidad: "Leve", "Moderada", "Grave"
   - Estado: "Activo", "En Tratamiento", "Recuperado", "Crónico"
   - Tipos: (No hay validación en el código actual)

2. **Tratamientos:**
   - Tipos: "Vacunación", "Desparasitación", "Antibiótico", "Vitaminas", "Minerales", "Cirugía", "Otro"
   - Estado: "Activo" (default)
   - Fecha próxima: Opcional, permite programar recurrencia

3. **Próximos tratamientos:**
   - Solo muestra si `fecha_proxima >= date('now')`
   - Ordenado por `fecha_proxima ASC`
   - Límite de 20 registros

---

## 🎯 ANÁLISIS DE RIESGOS

### RIESGOS DE MIGRACIÓN

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| CREATE TABLE en UI | 🟥 Alta | Mover a migraciones iniciales |
| Transacciones complejas | 🟧 Media | Orquestar en Service |
| Código duplicado (fincas/animales) | 🟧 Media | Un solo método en Service |
| Formateo de fechas inconsistente | 🟨 Baja | Estandarizar en Repository |
| Límites arbitrarios (100, 20) | 🟨 Baja | Documentar como constantes |

---

### DEPENDENCIAS CRÍTICAS

1. **database.db**:
   - Importa desde `from database import db`
   - Usa `db.get_connection()` (wrapper legacy)
   - Compatible con `ejecutar_consulta()` usado en Animales/Reproducción

2. **Tablas:**
   - `diagnostico_evento` (creada en L182)
   - `tratamiento` (creada en L775)
   - `animal` (FK)
   - `finca` (catálogo)

3. **Módulos UI:**
   - `modules.utils.date_picker` (attach_date_picker)
   - `modules.utils.ui` (get_theme_colors, add_tooltip, style_treeview)
   - `modules.utils.colores` (obtener_colores)

---

## 📐 ARQUITECTURA ACTUAL

### DIAGRAMA DE ACCESOS

```
┌─────────────────────────────────────────┐
│ salud_main.py (UI)                      │
│ ├─ SaludModule (1016 líneas)            │
│ ├─ db.get_connection() [15 VECES]       │
│ ├─ cursor.execute() [35+ VECES]         │
│ ├─ conn.commit() [4 VECES]              │
│ ├─ CREATE TABLE [2 VECES]               │
│ ├─ Validaciones inline                  │
│ ├─ Formateo de datos en SQL             │
│ └─ Cálculos temporales en SQL           │
└─────────────────────────────────────────┘
           ▼ VIOLACIÓN DIRECTA (60+)
┌─────────────────────────────────────────┐
│ database.db (SQLite)                    │
│ ├─ diagnostico_evento                   │
│ ├─ tratamiento                          │
│ ├─ animal                               │
│ └─ finca                                │
└─────────────────────────────────────────┘
```

**Problemas:**
- ❌ UI conoce estructura de tablas
- ❌ UI ejecuta CREATE TABLE
- ❌ UI maneja transacciones
- ❌ UI formatea datos para presentación en SQL
- ❌ UI tiene lógica de validación acoplada

---

## 🛠️ PLAN DE ENCAPSULACIÓN

### FASE 8.5.2 — REPOSITORY

**Métodos a crear en SaludRepository:**

#### Diagnósticos (8 métodos)
- `insertar_diagnostico(animal_id, fecha, tipo, detalle, severidad, estado, obs)`
- `listar_diagnosticos(limite=100)`
- `obtener_diagnostico_por_id(diagnostico_id)`
- `actualizar_estado_diagnostico(diagnostico_id, estado)`
- `contar_diagnosticos()`

#### Tratamientos (10 métodos)
- `insertar_tratamiento(animal_id, fecha, tipo, producto, dosis, vet, comentario, proxima)`
- `listar_tratamientos(limite=100)`
- `listar_proximos_tratamientos(limite=20)`
- `obtener_tratamiento_por_id(tratamiento_id)`
- `contar_tratamientos()`
- `contar_proximos_tratamientos()`

#### Catálogos (4 métodos)
- `listar_fincas_activas()`
- `listar_animales_por_finca(finca_id)`
- `listar_animales_activos()`
- `validar_animal_activo(animal_id)` → bool

**Total:** 22+ métodos en Repository

---

### FASE 8.5.2 — SERVICE

**Métodos a crear en SaludService:**

#### Diagnósticos (5 métodos públicos)
- `registrar_diagnostico(animal_id, fecha, tipo, detalle, severidad, estado, obs)`
  - Valida animal activo
  - Delega insert al repository
- `obtener_historial_diagnosticos(limite=100)`
- `obtener_detalle_diagnostico(diagnostico_id)`
- `actualizar_estado_diagnostico(diagnostico_id, nuevo_estado)`
- `obtener_estadisticas_diagnosticos()` → Dict

#### Tratamientos (6 métodos públicos)
- `registrar_tratamiento(animal_id, fecha, tipo, producto, dosis, vet, comentario, proxima)`
  - Valida animal activo
  - Valida tipo de tratamiento
  - Delega insert al repository
- `obtener_historial_tratamientos(limite=100)`
- `obtener_proximos_tratamientos(limite=20)`
- `obtener_detalle_tratamiento(tratamiento_id)`
- `obtener_estadisticas_tratamientos()` → Dict

#### Catálogos (3 métodos públicos)
- `cargar_fincas()` → List[Dict]
- `cargar_animales_por_finca(finca_id)` → List[Dict]
- `cargar_animales()` → List[Dict]

**Total:** 14+ métodos públicos en Service

---

## 📄 MÉTRICAS DE LA AUDITORÍA

### CÓDIGO ACTUAL

| Métrica | Valor |
|---------|-------|
| Archivos UI | 1 |
| Líneas UI | 1016 |
| Violaciones UI→BD | 60+ |
| db.get_connection() | 15 |
| cursor.execute() | 35+ |
| conn.commit() | 4 |
| CREATE TABLE inline | 2 |
| Métodos a migrar | 15+ |

---

### COMPLEJIDAD

| Componente | Complejidad | Motivo |
|------------|-------------|--------|
| Diagnósticos | Media | Validaciones + formateo en SQL |
| Tratamientos | Alta | CREATE TABLE + transacciones + validaciones |
| Próximos tratamientos | Media | Filtros temporales en SQL |
| Catálogos | Baja | SELECTs simples (pero duplicados) |
| **OVERALL** | **Media-Alta** | Similar a Reproducción |

---

## 🚦 SEMÁFORO DE MIGRACIÓN

### ✅ FACTORES A FAVOR

- ✅ Patrón ya validado en Animales y Reproducción
- ✅ Usa `db.get_connection()` (compatible con `ejecutar_consulta()`)
- ✅ No tiene modales complejos (solo formularios inline)
- ✅ Lógica de negocio simple (validaciones básicas)
- ✅ No hay cálculos complejos de fechas (solo date('now'))

---

### ⚠️ FACTORES DE RIESGO

- ⚠️ CREATE TABLE en runtime (debe moverse a migraciones)
- ⚠️ Código duplicado (fincas/animales en diagnósticos y tratamientos)
- ⚠️ Formateo de datos en SQL (presentación acoplada)
- ⚠️ Límites arbitrarios no documentados (100, 20)

---

### 🔴 BLOQUEADORES POTENCIALES

- 🔴 Ninguno identificado (arquitectura migrable)

---

## 🎯 ESTRATEGIA DE MIGRACIÓN

### ORDEN RECOMENDADO (FASE 8.5.3)

1. **Catálogos (bajo riesgo):**
   - `cargar_fincas()`
   - `cargar_animales()`
   - `actualizar_animales_por_finca()`
   - Elimina duplicación

2. **Consultas de lectura (bajo riesgo):**
   - `cargar_historial()`
   - `cargar_tratamientos()`
   - `cargar_proximos_tratamientos()`
   - `ver_detalle()`

3. **Escritura simple (medio riesgo):**
   - `actualizar_estado()`

4. **Escritura compleja (riesgo controlado):**
   - `guardar_diagnostico()`
   - `guardar_tratamiento()`
   - Elimina CREATE TABLE inline

---

## 📚 CONCLUSIÓN

### ESTADO ACTUAL

> **"El dominio Salud tiene 60+ violaciones UI→BD distribuidas en 1016 líneas.**  
> **Patrón similar a Reproducción pero con complejidad media-alta.**  
> **CREATE TABLE en runtime es el mayor riesgo.**  
> **Migración viable siguiendo el patrón validado."**

---

### READINESS PARA FASE 8.5.2

| Criterio | Estado |
|----------|--------|
| Inventario completo | ✅ |
| Violaciones contadas | ✅ 60+ |
| Flujos identificados | ✅ 8 flujos críticos |
| Riesgos mapeados | ✅ CREATE TABLE inline |
| Estrategia definida | ✅ Catálogos → Lectura → Escritura |
| Bloqueadores | ❌ Ninguno |

**Listo para FASE 8.5.2 — Crear infraestructura.**

---

**Documento generado por:** GitHub Copilot  
**Fase:** FASE 8.5.1 — Auditoría Pasiva  
**Próximo paso:** FASE 8.5.2 — Crear SaludRepository + SaludService sin tocar UI
