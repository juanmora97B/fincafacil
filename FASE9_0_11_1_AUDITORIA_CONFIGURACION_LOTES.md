# FASE 9.0.11.1 — AUDITORÍA CONFIGURACIÓN LOTES

**Fecha:** 2025-12-21  
**Módulo:** Configuración · Lotes  
**Archivo:** `src/modules/configuracion/lotes.py`  
**Líneas:** 387  
**Complejidad:** 🟡 Media (relación FK con finca, soft delete crítico)

---

## 1. RESUMEN EJECUTIVO

Auditoría del módulo **Lotes** (configuración de lotes ganaderos por finca) para identificar violaciones de fronteras arquitectónicas y riesgos de gobernanza.

**Hallazgos críticos:**
- ❌ **DELETE físico** (línea 281) → Pérdida de historial
- ⚠️ **Estados divergentes** ('Activo' vs 'Activa') → Inconsistencia
- ⚠️ **Relación FK finca_id** → Requiere validación estricta
- ❌ **4 get_connection()** → SQL directo en UI
- ❌ **11 cursor.execute()** → Lógica de negocio en UI
- ❌ **3 conn.commit()** → Transacciones en UI

**Recomendación:** Migración COMPLETE (incluye criterio y descripción, son campos simples sin complejidad adicional).

---

## 2. VIOLACIONES DE FRONTERAS

### 2.1. SQL Directo en UI

| Método | Línea | Violación | Query |
|--------|-------|-----------|-------|
| `cargar_fincas_combobox()` | 118-120 | get_connection + execute | `SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'` |
| `guardar_lote()` | 154-188 | get_connection + execute + commit | `INSERT INTO lote` / `UPDATE lote` |
| `cargar_lotes()` | 204-224 | get_connection + execute | `SELECT l.*, f.nombre FROM lote l LEFT JOIN finca f` |
| `eliminar_lote()` | 279-282 | get_connection + execute + commit | **DELETE FROM lote WHERE id = ?** |
| `importar_excel()` | 334-378 | get_connection + execute + commit | `INSERT INTO lote` (bulk) |

**Total violaciones:**
- get_connection(): 4 instancias
- cursor.execute(): 11 queries
- conn.commit(): 3 instancias
- DELETE físico: 1 instancia (CRÍTICO)

---

### 2.2. DELETE Físico (RIESGO CRÍTICO)

**Ubicación:** Línea 281
```python
def eliminar_lote(self):
    # ...
    cursor.execute("DELETE FROM lote WHERE id = ?", (lote_id,))
    conn.commit()
```

**Problema:**
- ❌ Pérdida permanente de historial
- ❌ Imposible auditoría de lotes eliminados
- ❌ No se puede restaurar si fue error de usuario
- ❌ Rompe integridad referencial si lote tiene registros relacionados

**Solución requerida:**
- ✅ Soft delete: `UPDATE lote SET estado='Inactivo' WHERE id=?`
- ✅ Preservar historial completo
- ✅ Posibilitar auditorías y reportes históricos

---

### 2.3. Estados Divergentes (RIESGO MEDIO)

**Inconsistencias detectadas:**

**Línea 120:** `WHERE estado = 'Activa' OR estado = 'Activo'`  
**Línea 213:** `WHERE l.estado = 'Activo' OR l.estado = 'Activa'`  
**Línea 182:** `INSERT ... VALUES (..., 'Activo', ...)`  
**Línea 347:** `WHERE ... AND (estado='Activo' OR estado='Activa')`

**Problema:**
- ⚠️ Fincas usan 2 variantes: 'Activa' y 'Activo'
- ⚠️ Lotes siempre insertan 'Activo'
- ⚠️ Queries deben considerar ambas variantes

**Causa raíz:**
- Tabla `finca` no tiene constraint CHECK de estados
- Diferentes módulos insertaron con variantes distintas
- Sin Service centralizado para normalizar

**Solución requerida:**
- ✅ Service normaliza estado a 'Activo' solamente
- ✅ Repository asume 'Activo'/'Inactivo' únicamente
- ✅ Migración futura: `UPDATE finca SET estado='Activo' WHERE estado='Activa'`

---

### 2.4. Validaciones en UI (RIESGO BAJO)

**Validaciones actuales (líneas 137-147):**
```python
if not codigo or not nombre:
    messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
    return

if not finca_nombre or finca_nombre == "Seleccione una finca":
    messagebox.showwarning("Atención", "Debe seleccionar una finca.")
    return

finca_id = self._finca_map.get(finca_nombre)
if not finca_id:
    messagebox.showwarning("Atención", "Finca no válida.")
    return
```

**Problema:**
- ⚠️ Validaciones duplicadas en UI (no reutilizables)
- ⚠️ Excel import tiene su propia validación (línea 356)
- ⚠️ No valida unicidad de código por finca

**Solución:**
- ✅ Mover validaciones a Service
- ✅ Service valida: campos requeridos, finca existente, unicidad código/nombre por finca
- ✅ UI solo captura ValueError y muestra mensaje

---

### 2.5. Normalización Ausente (RIESGO BAJO)

**Código actual:**
```python
codigo = self.entry_codigo.get().strip()  # No normaliza case
nombre = self.entry_nombre.get().strip()  # No normaliza case
```

**Problema:**
- ⚠️ Usuarios pueden crear "LOT001", "lot001", "Lot001" (duplicados lógicos)
- ⚠️ Sin .upper() o .title(), búsquedas son case-sensitive

**Solución:**
- ✅ Service normaliza: `codigo.strip().upper()`, `nombre.strip().title()`
- ✅ Unicidad garantizada independiente de case

---

## 3. ANÁLISIS DE MÉTODOS

### 3.1. cargar_fincas_combobox() — Cargar fincas activas

**SQL actual (línea 120):**
```python
cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
rows = cursor.fetchall()
self._finca_map = {str(r[1]).strip(): int(r[0]) for r in rows}
```

**Problemas:**
- SQL directo en UI
- Estados divergentes hardcoded
- Mapeo manual nombre→id (propenso a errores)

**Solución:**
```python
# Repository
def listar_fincas_activas_para_lotes() -> List[Dict[str, Any]]:
    # SELECT id, codigo, nombre FROM finca WHERE estado='Activo' ORDER BY nombre

# Service
def listar_fincas_para_combo_lotes() -> List[Dict[str, Any]]:
    # Retorna: [{'id': 1, 'codigo': 'F001', 'nombre': 'La Esperanza'}, ...]

# UI
fincas = self.service.listar_fincas_para_combo_lotes()
self.combo_finca.configure(values=[f['nombre'] for f in fincas])
self._finca_map = {f['nombre']: f['id'] for f in fincas}
```

---

### 3.2. guardar_lote() — Crear/Actualizar

**SQL actual (líneas 162-188):**
```python
if self.entry_codigo.cget("state") == "disabled":
    # Modo edición
    cursor.execute("""
        UPDATE lote 
        SET nombre = ?, descripcion = ?, criterio = ?, finca_id = ?
        WHERE id = ?
    """, (...))
else:
    # Modo creación
    cursor.execute("""
        INSERT INTO lote (codigo, nombre, descripcion, criterio, estado, finca_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (..., 'Activo', ...))
conn.commit()
```

**Problemas:**
- SQL directo en UI
- Lógica de edición basada en estado del widget (frágil)
- Sin validación de unicidad (maneja IntegrityError después)
- Estado 'Activo' hardcoded

**Solución:**
```python
# Repository
def crear_lote(codigo, nombre, finca_id, descripcion, criterio, estado) -> None:
    # INSERT INTO lote VALUES (...)

def actualizar_lote(lote_id, nombre, descripcion, criterio, finca_id) -> None:
    # UPDATE lote SET ... WHERE id=?

# Service
def crear_lote(codigo, nombre, finca_id, descripcion='', criterio='Por Peso') -> None:
    # Validaciones:
    # - codigo required
    # - nombre required
    # - finca_id required y existe
    # - unicidad: existe_lote_en_finca(codigo, finca_id) → raise ValueError
    # Normalización: codigo→UPPER, nombre→title
    # Llama: repo.crear_lote(..., estado='Activo')

def actualizar_lote(lote_id, nombre, descripcion, criterio, finca_id) -> None:
    # Valida lote_id existe
    # Normaliza nombre→title
    # Llama: repo.actualizar_lote(...)

# UI
try:
    if self.lote_editando_id:
        self.service.actualizar_lote(self.lote_editando_id, nombre, desc, crit, finca_id)
    else:
        self.service.crear_lote(codigo, nombre, finca_id, desc, crit)
    messagebox.showinfo("Éxito", "Lote guardado")
except ValueError as e:
    messagebox.showerror("Error", str(e))
```

---

### 3.3. cargar_lotes() — Listar activos

**SQL actual (líneas 206-224):**
```python
cursor.execute("""
    SELECT l.id, f.nombre as finca, l.codigo, l.nombre, l.descripcion, 
           COALESCE(l.criterio, 'N/A') as criterio 
    FROM lote l
    LEFT JOIN finca f ON l.finca_id = f.id
    WHERE l.estado = 'Activo' OR l.estado = 'Activa'
""")
```

**Problemas:**
- SQL directo en UI
- Estados divergentes hardcoded
- COALESCE manual (debería ser normalizado en Service)
- LEFT JOIN en UI (lógica de negocio)

**Solución:**
```python
# Repository
def listar_lotes_activos_con_finca() -> List[Dict[str, Any]]:
    # SELECT l.id, l.codigo, l.nombre, l.descripcion, l.criterio, l.finca_id, f.nombre as finca_nombre
    # FROM lote l LEFT JOIN finca f ON l.finca_id = f.id
    # WHERE l.estado='Activo' ORDER BY l.codigo

# Service
def listar_lotes_activos() -> List[Dict[str, Any]]:
    # Normaliza output: criterio=criterio or 'Por Peso', finca_nombre=finca_nombre or 'Sin Finca'
    # Retorna: [{'id': 1, 'codigo': 'LOT001', 'nombre': 'Lote Terneros', ...}, ...]

# UI
lotes = self.service.listar_lotes_activos()
for lote in lotes:
    self.tabla.insert("", "end", values=(
        lote['id'], lote['finca_nombre'], lote['codigo'], 
        lote['nombre'], lote['descripcion'], lote['criterio']
    ))
```

---

### 3.4. eliminar_lote() — CRÍTICO: DELETE físico

**SQL actual (línea 281):**
```python
cursor.execute("DELETE FROM lote WHERE id = ?", (lote_id,))
conn.commit()
```

**Problema CRÍTICO:**
- ❌ Eliminación permanente e irreversible
- ❌ Pérdida de historial
- ❌ No cumple con auditoría de cambios

**Solución (soft delete):**
```python
# Repository
def cambiar_estado_lote(lote_id: int, estado: str) -> None:
    # UPDATE lote SET estado=? WHERE id=?

# Service
def cambiar_estado_lote(lote_id: int, estado: str) -> None:
    # Valida: lote_id existe, estado in ['Activo', 'Inactivo']
    # Llama: repo.cambiar_estado_lote(lote_id, estado)

# UI
try:
    self.service.cambiar_estado_lote(lote_id, 'Inactivo')
    messagebox.showinfo("Éxito", f"Lote '{codigo}' marcado como Inactivo.")
except ValueError as e:
    messagebox.showerror("Error", str(e))
```

---

### 3.5. importar_excel() — Bulk import

**SQL actual (líneas 334-378):**
```python
for idx, fila in enumerate(filas, start=2):
    # Validaciones inline
    codigo = str(fila.get('codigo') or '').strip()
    nombre = str(fila.get('nombre') or '').strip()
    finca_nombre = str(fila.get('finca') or '').strip()
    
    # Resolver finca_id con query
    cursor.execute("SELECT id FROM finca WHERE LOWER(nombre) = LOWER(?) ...", (finca_nombre,))
    
    # Validar duplicado con query
    cursor.execute("SELECT COUNT(*) FROM lote WHERE (codigo = ? OR nombre = ?) AND finca_id = ?", (...))
    
    # Insertar
    cursor.execute("INSERT INTO lote (...) VALUES (...)", (...))

conn.commit()
```

**Problemas:**
- SQL directo en UI (loop de queries)
- Validaciones duplicadas (diferentes a guardar_lote)
- Resolución finca_id manual (debería usar Service)
- Estados divergentes en query finca

**Solución:**
```python
# Service reutiliza crear_lote(), que ya valida todo
# UI simplificado:

for idx, fila in enumerate(filas, start=2):
    codigo = str(fila.get('codigo') or '').strip()
    nombre = str(fila.get('nombre') or '').strip()
    finca_nombre = str(fila.get('finca') or '').strip()
    
    # Resolver finca_id usando Service
    try:
        finca = self.service.obtener_finca_por_nombre(finca_nombre)
        finca_id = finca['id']
    except ValueError:
        errores.append(f"Fila {idx}: finca '{finca_nombre}' no encontrada")
        continue
    
    try:
        self.service.crear_lote(codigo, nombre, finca_id, desc, crit)
        importados += 1
    except ValueError as e:
        errores.append(f"Fila {idx}: {str(e)}")
```

---

## 4. DECISIÓN DE ALCANCE

### ALCANCE RECOMENDADO: **COMPLETE**

**Campos incluidos:**
- ✅ codigo (PK lógica, requerido, único por finca)
- ✅ nombre (requerido)
- ✅ finca_id (FK, requerido, debe existir)
- ✅ descripcion (opcional, texto libre)
- ✅ criterio (opcional, valores: Por Peso, Por Edad, Por Origen, Por Salud, Por Producción, Personalizado)
- ✅ estado ∈ {Activo, Inactivo}

**Justificación:**
- **Criterio y descripción son simples:** No agregan complejidad arquitectónica
- **Sin relaciones complejas:** No hay cascadas a otras tablas
- **UI ya los incluye:** No requiere cambios visuales adicionales
- **Valor de negocio:** Criterio permite agrupar lotes por estrategia ganadera

**Exclusiones:** Ninguna (alcance COMPLETE)

---

## 5. ARQUITECTURA OBJETIVO

### 5.1. Repository (SQL-only)

**Métodos requeridos (8 métodos):**

```python
def listar_fincas_activas_para_lotes() -> List[Dict[str, Any]]:
    # SELECT id, codigo, nombre FROM finca WHERE estado='Activo'

def listar_lotes_activos_con_finca() -> List[Dict[str, Any]]:
    # SELECT l.*, f.nombre FROM lote l LEFT JOIN finca f WHERE l.estado='Activo'

def obtener_lote(lote_id: int) -> Optional[Dict[str, Any]]:
    # SELECT * FROM lote WHERE id=? LIMIT 1

def existe_lote_en_finca(codigo: str, finca_id: int) -> bool:
    # SELECT COUNT(*) FROM lote WHERE codigo=? AND finca_id=?

def crear_lote(codigo, nombre, finca_id, descripcion, criterio, estado) -> None:
    # INSERT INTO lote VALUES (...)

def actualizar_lote(lote_id, nombre, descripcion, criterio, finca_id) -> None:
    # UPDATE lote SET ... WHERE id=?

def cambiar_estado_lote(lote_id: int, estado: str) -> None:
    # UPDATE lote SET estado=? WHERE id=?

def obtener_finca_por_nombre(nombre: str) -> Optional[Dict[str, Any]]:
    # SELECT * FROM finca WHERE LOWER(nombre)=LOWER(?) AND estado='Activo' LIMIT 1
```

---

### 5.2. Service (Validations + Normalización)

**Métodos requeridos (7 métodos):**

```python
def listar_fincas_para_combo_lotes() -> List[Dict[str, Any]]:
    # Llama repo, normaliza nombres (title)

def listar_lotes_activos() -> List[Dict[str, Any]]:
    # Llama repo, normaliza: codigo→UPPER, nombre→title, criterio→default 'Por Peso'

def obtener_lote(lote_id: int) -> Dict[str, Any]:
    # Valida existencia, raises ValueError si no existe
    # Normaliza output

def obtener_finca_por_nombre(nombre: str) -> Dict[str, Any]:
    # Normaliza búsqueda, valida existencia

def crear_lote(codigo, nombre, finca_id, descripcion='', criterio='Por Peso') -> None:
    # Validaciones:
    # - codigo required
    # - nombre required
    # - finca_id required y existe
    # - criterio in valores_validos
    # - unicidad: existe_lote_en_finca(codigo, finca_id) → raise ValueError
    # Normalización: codigo→UPPER, nombre→title
    # Crea con estado='Activo'

def actualizar_lote(lote_id, nombre, descripcion, criterio, finca_id) -> None:
    # Valida lote_id existe, finca_id existe, criterio válido
    # Normaliza nombre→title
    # Actualiza

def cambiar_estado_lote(lote_id: int, estado: str) -> None:
    # Valida: lote_id existe, estado ∈ {Activo, Inactivo}
    # Soft delete
```

**Reglas de normalización:**
- `codigo`: `.strip().upper()`
- `nombre`: `.strip().title()`
- `descripcion`: `.strip()` (opcional)
- `criterio`: valores permitidos = ['Por Peso', 'Por Edad', 'Por Origen', 'Por Salud', 'Por Producción', 'Personalizado']
- `estado`: solo 'Activo' o 'Inactivo'

**Reglas de validación:**
- Campos requeridos: codigo, nombre, finca_id
- Unicidad: codigo único por finca (no global)
- Existencia: finca_id debe existir en tabla finca con estado='Activo'
- Criterio: debe estar en lista de valores válidos
- Estados: solo 'Activo' o 'Inactivo'

---

### 5.3. UI (Orchestration-only)

**Cambios requeridos:**

**Eliminar:**
- `import sqlite3`
- `from database import db`
- `db.get_connection()` (4 instancias)
- `cursor.execute()` (11 instancias)
- `conn.commit()` (3 instancias)
- `DELETE FROM lote` (1 instancia)

**Agregar:**
- `from infraestructura.configuracion import ConfiguracionService`
- `self.service = ConfiguracionService()`
- `self.lote_editando_id: Optional[int] = None`

**Refactorizar métodos:**
- `cargar_fincas_combobox()` → `service.listar_fincas_para_combo_lotes()`
- `guardar_lote()` → `service.crear_lote()` or `actualizar_lote()`
- `cargar_lotes()` → `service.listar_lotes_activos()`
- `editar_lote()` → `service.obtener_lote()` + cargar a form
- `eliminar_lote()` → `service.cambiar_estado_lote(lote_id, 'Inactivo')`
- `importar_excel()` → loop `service.crear_lote()`

---

## 6. RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|--------|-----------|
| DELETE físico rompe historial | 🔴 Actual | Crítico | Implementar soft delete obligatorio |
| Estados divergentes causan bugs | 🟡 Media | Medio | Service normaliza a 'Activo'/'Inactivo' únicamente |
| Unicidad no validada (duplicados) | 🟡 Media | Medio | Service valida existe_lote_en_finca() |
| FK finca_id inválido | 🟢 Baja | Bajo | Service valida finca existe antes de crear |
| Regresión UX (combo fincas roto) | 🟢 Baja | Medio | Mantener _finca_map en UI, testing manual |

---

## 7. MÉTRICAS ESTIMADAS

| Métrica | Antes | Después | Delta |
|---------|-------|---------|-------|
| Líneas totales | 387 | ~220 | -167 (-43%) |
| get_connection() | 4 | 0 | -4 ✅ |
| cursor.execute() | 11 | 0 | -11 ✅ |
| conn.commit() | 3 | 0 | -3 ✅ |
| DELETE físico | 1 | 0 | -1 ✅ |
| Soft delete | 0 | 1 | +1 ✅ |
| Métodos repository | 0 | 8 | +8 |
| Métodos service | 0 | 7 | +7 |

---

## 8. CRITERIOS DE ÉXITO

### Validación técnica:
- ✅ Pylance: 0 errors
- ✅ Grep SQL: 0 matches en `lotes.py`
- ✅ Auditor: exit 0 (sin violaciones)

### Validación funcional:
- ✅ CRUD completo funcional vía Service
- ✅ Soft delete implementado (UPDATE estado='Inactivo')
- ✅ UX intacta (formulario, tabla, combo fincas, importar Excel)
- ✅ Normalización automática (UPPER/title)
- ✅ Validaciones centralizadas (uniqueness, FK, required)

### Validación de gobernanza:
- ✅ 0 SQL en UI
- ✅ 0 validaciones en UI
- ✅ 0 normalizaciones en UI
- ✅ Estados estrictos (solo 'Activo'/'Inactivo')
- ✅ Historial preservado (soft delete)

---

## 9. PRÓXIMOS PASOS (PASO 2-7)

1. **PASO 2:** Extender `configuracion_repository.py` con 8 métodos SQL-only
2. **PASO 3:** Extender `configuracion_service.py` con 7 métodos con validaciones
3. **PASO 4:** Migrar `lotes.py` a service-only (eliminar SQL)
4. **PASO 5:** Validación técnica (Pylance, grep, auditor)
5. **PASO 6:** Documentar migración en `FASE9_0_11_2_MIGRACION_CONFIGURACION_LOTES.md`
6. **PASO 7:** Actualizar `FASE9_0_LOG.md` (11/13 = 85%)

---

**FIN DE AUDITORÍA**
