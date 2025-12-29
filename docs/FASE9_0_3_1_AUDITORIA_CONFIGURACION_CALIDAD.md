# 📊 FASE 9.0.3.1 — Auditoría Pasiva: Catálogo Calidad Animal

**Estado:** ✅ AUDITORÍA COMPLETADA  
**Fecha:** 2025-12-19  
**Dominio:** Configuración  
**Catálogo:** Calidad Animal  
**Archivo:** `src/modules/configuracion/calidad_animal.py`

---

## 📋 Resumen Ejecutivo

### Objetivo
Auditoría pasiva (sin modificar código) del catálogo Calidad Animal para identificar violaciones de frontera UI → BD y riesgos de migración a gobernanza.

### Resultado
✅ **Auditoría completada**
- 4 violaciones críticas de frontera identificadas
- 4 queries SQL embebidas en UI
- 2 commit() directos desde UI
- 1 estado hardcoded (edit vs new)
- 3 flujos principales mapeados

---

## 🔍 Inventario Detallado

### Archivo Analizado
**Ruta:** `src/modules/configuracion/calidad_animal.py`  
**Tamaño:** 350 líneas  
**Tipo:** `ctk.CTkFrame` (CustomTkinter)

### Estructura de Clases
```
CalidadAnimalFrame (ctk.CTkFrame)
├── __init__()
├── crear_widgets()
├── guardar_calidad()         ← VIOLACIÓN 1
├── cargar_calidades()        ← VIOLACIÓN 2
├── editar_calidad()
├── eliminar_calidad()        ← VIOLACIÓN 3
├── limpiar_formulario()
├── importar_excel()          ← VIOLACIÓN 4
└── mostrar_menu_contextual()
```

---

## 🚨 VIOLACIONES DETECTADAS (CRÍTICAS)

### 1️⃣ VIOLACIÓN: SQL INSERT/UPDATE en guardar_calidad() (Línea 114–133)

**Ubicación:** Método `guardar_calidad()`

**Código:**
```python
def guardar_calidad(self):
    codigo = self.entry_codigo.get().strip()
    descripcion = self.entry_descripcion.get().strip()
    comentario = self.text_comentario.get("1.0", "end-1c").strip()
    
    if not codigo or not descripcion:
        messagebox.showerror("Error", "Los campos Código y Descripción son obligatorios")
        return

    try:
        with db.get_connection() as conn:                              # ← get_connection #1
            cursor = conn.cursor()
            if self.entry_codigo.cget("state") == "disabled":         # ← Estado hardcoded: detección de edit vs insert
                cursor.execute("""                                     # ← execute #1
                    UPDATE calidad_animal 
                    SET descripcion = ?, comentario = ?
                    WHERE codigo = ?
                """, (descripcion, comentario, codigo))
                messagebox.showinfo("Éxito", "Calidad animal actualizada")
            else:
                cursor.execute("""                                     # ← execute #2
                    INSERT INTO calidad_animal (codigo, descripcion, comentario)
                    VALUES (?, ?, ?)
                """, (codigo, descripcion, comentario))
                messagebox.showinfo("Éxito", "Calidad animal guardada")
            
            conn.commit()                                              # ← commit #1
            
        self.limpiar_formulario()
        self.cargar_calidades()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Ya existe una calidad con ese código")
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar: {str(e)}")
```

**Análisis:**
- **Tipo:** INSERT + UPDATE en mismo método
- **SQL Embebido:** 2 queries (INSERT, UPDATE)
- **Violaciones:**
  - ✗ `db.get_connection()` directo desde UI
  - ✗ `cursor.execute()` 2 veces
  - ✗ `conn.commit()` desde UI
- **Estado Hardcoded:** Usa `entry_codigo.cget("state") == "disabled"` para determinar si es edición o creación
  - Riesgo: Acoplamiento con widget state
  - Mejor: Pasar `es_edicion: bool` desde service

**Impacto:** Alto — lógica de persistencia mezclada con lógica de UI

---

### 2️⃣ VIOLACIÓN: SQL SELECT en cargar_calidades() (Línea 135–149)

**Ubicación:** Método `cargar_calidades()`

**Código:**
```python
def cargar_calidades(self):
    for item in self.tabla.get_children():
        self.tabla.delete(item)

    try:
        with db.get_connection() as conn:                    # ← get_connection #2
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, descripcion, comentario FROM calidad_animal")  # ← execute #3
            for calidad in cursor.fetchall():
                # Convertir explícitamente a strings
                valores = (
                    str(calidad[0]) if calidad[0] is not None else "",
                    str(calidad[1]) if calidad[1] is not None else "",
                    str(calidad[2]) if calidad[2] is not None else ""
                )
                self.tabla.insert("", "end", values=valores)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
```

**Análisis:**
- **Tipo:** SELECT + Render en Treeview
- **SQL Embebido:** 1 query (SELECT)
- **Violaciones:**
  - ✗ `db.get_connection()` directo desde UI
  - ✗ `cursor.execute()` 1 vez
  - ✗ Conversión de tipos en UI (líneas 145–149)
- **Conversión Explícita:** UI conoce que puede haber NULL, maneja conversión a strings
  - Debería: Service devolver `List[Dict[str, str]]` normalizado

**Impacto:** Medio — Lectura embebida en UI, renderizado acoplado

---

### 3️⃣ VIOLACIÓN: SQL DELETE en eliminar_calidad() (Línea 176–189)

**Ubicación:** Método `eliminar_calidad()`

**Código:**
```python
def eliminar_calidad(self):
    selected = self.tabla.selection()
    if not selected:
        messagebox.showwarning("Advertencia", "Seleccione una calidad para eliminar")
        return

    codigo = self.tabla.item(selected[0])["values"][0]
    if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la calidad '{codigo}'?\n\nEsta acción no se puede deshacer."):
        return

    try:
        with db.get_connection() as conn:                    # ← get_connection #3
            cursor = conn.cursor()
            cursor.execute("DELETE FROM calidad_animal WHERE codigo = ?", (codigo,))  # ← execute #4
            conn.commit()                                    # ← commit #2
        messagebox.showinfo("Éxito", "Calidad eliminada correctamente.")
        self.cargar_calidades()
    except Exception as e:
        messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
```

**Análisis:**
- **Tipo:** DELETE
- **SQL Embebido:** 1 query (DELETE)
- **Violaciones:**
  - ✗ `db.get_connection()` directo desde UI
  - ✗ `cursor.execute()` 1 vez
  - ✗ `conn.commit()` desde UI
- **Flujo:** UI captura ID directamente desde tabla (valores[0])
  - Debería: Pasar código a service, service elimina

**Impacto:** Alto — Eliminación sin mediación de servicio

---

### 4️⃣ VIOLACIÓN: SQL INSERT en importar_excel() (Línea 192–230)

**Ubicación:** Método `importar_excel()`

**Código:**
```python
def importar_excel(self):
    file_path = filedialog.askopenfilename(
        title="Seleccionar Excel",
        filetypes=[("Excel", "*.xlsx;*.xls")]
    )
    if not file_path:
        return

    try:
        registros, errores_parse = parse_excel_to_dicts(file_path)
        
        if errores_parse:
            messagebox.showerror("Error", "\n".join(errores_parse))
            return
        
        if not registros:
            messagebox.showinfo("Importar", "No se encontraron filas para importar.")
            return
        
        importados = 0
        errores = []
        
        with db.get_connection() as conn:                    # ← get_connection #4
            cursor = conn.cursor()
            for idx, reg in enumerate(registros, start=2):
                try:
                    cursor.execute("""                       # ← execute #5
                        INSERT INTO calidad_animal (codigo, descripcion, comentario)
                        VALUES (?, ?, ?)
                    """, (
                        str(reg.get('codigo', '')).strip(),
                        str(reg.get('descripcion', '')).strip(),
                        str(reg.get('comentario', '')).strip()
                    ))
                    importados += 1
                except sqlite3.IntegrityError:
                    errores.append(f"Fila {idx}: código duplicado")
                except Exception as e:
                    errores.append(f"Fila {idx}: {e}")
            conn.commit()                                    # ← commit #3
        
        mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
        if errores:
            mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
        
        messagebox.showinfo("Importación", mensaje)
        self.cargar_calidades()
    except Exception as e:
        messagebox.showerror("Error", f"Error en importación: {str(e)}")
```

**Análisis:**
- **Tipo:** INSERT bulk (loop sobre registros)
- **SQL Embebido:** 1 query template (INSERT múltiple)
- **Violaciones:**
  - ✗ `db.get_connection()` directo desde UI
  - ✗ `cursor.execute()` en loop (1 vez per row)
  - ✗ `conn.commit()` desde UI
- **Lógica de Negocio en UI:** 
  - Parseo de Excel (OK, delegado a `parse_excel_to_dicts`)
  - Inserción bulk (✗ debería ser service)
  - Conteo de importados/errores (✗ debería ser service)

**Impacto:** Muy Alto — Bulk insert sin mediación, lógica de importación en UI

---

## 📊 CONTEO DE VIOLACIONES

| Tipo | Cantidad | Métodos Afectados |
|------|----------|-------------------|
| `get_db_connection()` | 4 | guardar, cargar, eliminar, importar |
| `cursor.execute()` | 5 | 2×guardar, 1×cargar, 1×eliminar, 1×importar |
| `conn.commit()` | 3 | guardar, eliminar, importar |
| **TOTAL** | **12 violaciones** | **4 métodos** |

---

## 🔨 VALIDACIONES EN UI

### 1. Validación: Campos Obligatorios (Línea 108–111)

**Ubicación:** `guardar_calidad()`

```python
if not codigo or not descripcion:
    messagebox.showerror("Error", "Los campos Código y Descripción son obligatorios")
    return
```

**Tipo:** Validación UI simple (presencia)

**Riesgo:** 
- ✓ Aceptable: Es una validación UX (feedback inmediato)
- ✓ No rompe si eliminamos: Service puede revalidar

**Decisión:** Mantener en UI + revalidar en service

---

### 2. Validación: Integridad de Código (Línea 130–131, 224–225)

**Ubicación:** `guardar_calidad()`, `importar_excel()`

```python
except sqlite3.IntegrityError:
    messagebox.showerror("Error", "Ya existe una calidad con ese código")
```

**Tipo:** Validación de negocio (uniqueness)

**Riesgo:**
- ✓ Aceptable: Solo captura excepción
- ✓ No rompe si eliminamos: Service puede validar antes

**Decisión:** Mover validación a service (proactiva) + mantener try/except como fallback (defensiva)

---

## 🎯 FLUJOS IDENTIFICADOS

### Flujo 1: Listado de Calidades (Lectura)

**Ruta:** `cargar_calidades()` → `db.get_connection()` → `cursor.execute(SELECT)` → Treeview.insert()

```
┌────────────────┐
│ __init__()     │
├────────────────┤
│ crear_widgets()│
│ cargar_..()    │ ← Línea 16
└────────────────┘
        ↓
   (ON LOAD)
        ↓
┌─────────────────────────────────┐
│ cargar_calidades()              │
├─────────────────────────────────┤
│ 1. Limpiar tabla                │
│ 2. db.get_connection()          │
│ 3. cursor.execute(SELECT)       │ ← VIOLACIÓN
│ 4. Para cada fila:              │
│    - Normalizar tipos (str)     │
│    - tabla.insert()             │
└─────────────────────────────────┘
```

**Riesgo:** Medio — Lectura simple, pero UI acoplada a SELECT

**Migración:** `service.listar_calidades()` → retorna `List[Dict[str, str]]` (ya normalizado)

---

### Flujo 2: Crear/Editar Calidad (Escritura)

**Ruta:** `guardar_calidad()` → Detecta edit vs insert por widget state → `db.get_connection()` → `cursor.execute(INSERT/UPDATE)`

```
┌──────────────────────────┐
│ editar_calidad()         │
├──────────────────────────┤
│ 1. tabla.selection()     │
│ 2. Obtiene valores       │
│ 3. Popula entrada        │
│ 4. entry_codigo.disable()│ ← ESTADO HARDCODED
└──────────────────────────┘
        ↓
┌──────────────────────────────────┐
│ guardar_calidad()                │
├──────────────────────────────────┤
│ 1. Lee codigo, desc, comentario  │
│ 2. IF entry_codigo.disabled:     │ ← DETECCIÓN (ACÓ)
│    - cursor.execute(UPDATE)      │ ← VIOLACIÓN
│    ELSE:                         │
│    - cursor.execute(INSERT)      │ ← VIOLACIÓN
│ 3. conn.commit()                 │ ← VIOLACIÓN
│ 4. Reload tabla                  │
└──────────────────────────────────┘
```

**Riesgo:** Muy Alto — Lógica de persistencia en UI, detección acoplada a widget state

**Migración:** 
- `service.crear_calidad(codigo, desc, comentario)` → si codigo existe: error
- `service.actualizar_calidad(codigo, desc, comentario)` → si no existe: error
- Service maneja duplicados, UI solo hace commit

---

### Flujo 3: Eliminar Calidad (Escritura)

**Ruta:** UI muestra confirm → `db.get_connection()` → `cursor.execute(DELETE)`

```
┌─────────────────────────────────────┐
│ eliminar_calidad()                  │
├─────────────────────────────────────┤
│ 1. tabla.selection()                │
│ 2. messagebox.askyesno()            │
│ 3. db.get_connection()              │ ← VIOLACIÓN
│ 4. cursor.execute(DELETE)           │ ← VIOLACIÓN
│ 5. conn.commit()                    │ ← VIOLACIÓN
│ 6. Reload tabla                     │
└─────────────────────────────────────┘
```

**Riesgo:** Alto — Eliminación directa sin mediación

**Migración:** `service.eliminar_calidad(codigo)` → maneja DELETE + revalidación

---

### Flujo 4: Importar desde Excel (Escritura Bulk)

**Ruta:** Diálogo archivo → `parse_excel_to_dicts()` → Loop INSERT → `conn.commit()`

```
┌──────────────────────────────────────┐
│ importar_excel()                     │
├──────────────────────────────────────┤
│ 1. filedialog.askopenfilename()      │
│ 2. parse_excel_to_dicts(file)        │ ← OK (utilidad)
│ 3. db.get_connection()               │ ← VIOLACIÓN
│ 4. Para cada registro:               │
│    - cursor.execute(INSERT)          │ ← VIOLACIÓN (bulk)
│    - Captura IntegrityError          │
│ 5. conn.commit()                     │ ← VIOLACIÓN
│ 6. Reload tabla                      │
└──────────────────────────────────────┘
```

**Riesgo:** Muy Alto — Bulk insert sin control, lógica de importación en UI

**Migración:** 
- `service.importar_calidades(List[Dict])` → retorna `(importados: int, errores: List[str])`
- UI maneja diálogo + parseo, service maneja inserción

---

## 📋 QUERIES IDENTIFICADAS

### Query 1: Listar Calidades (Lectura)

**Ubicación:** `cargar_calidades()`, línea 138

```sql
SELECT codigo, descripcion, comentario 
FROM calidad_animal
```

**Destino:** Repository: `listar_calidades() → List[Dict[str, str]]`

**Columnnas:** 3 (codigo, descripcion, comentario)

**Riesgo:** Bajo (lectura simple)

---

### Query 2: Insertar Calidad (Escritura)

**Ubicación:** `guardar_calidad()`, línea 122

```sql
INSERT INTO calidad_animal (codigo, descripcion, comentario)
VALUES (?, ?, ?)
```

**Destino:** Repository: `crear_calidad(codigo, desc, comentario) → None`

**Validaciones Necesarias:**
- ✗ Código no vacío (UI lo hace, service revalida)
- ✗ Código único (DB lo garantiza con PK, service puede prevalidar con `existe_calidad()`)
- ✗ Descripción no vacía (UI lo hace, service revalida)

**Riesgo:** Medio (sin transacción, sin rollback)

---

### Query 3: Actualizar Calidad (Escritura)

**Ubicación:** `guardar_calidad()`, línea 119

```sql
UPDATE calidad_animal 
SET descripcion = ?, comentario = ?
WHERE codigo = ?
```

**Destino:** Repository: `actualizar_calidad(codigo, desc, comentario) → None`

**Validaciones Necesarias:**
- ✗ Código existe (service debe validar antes)
- ✗ Descripción no vacía (UI lo hace, service revalida)

**Riesgo:** Medio (sin verificar affected_rows)

---

### Query 4: Eliminar Calidad (Escritura)

**Ubicación:** `eliminar_calidad()`, línea 181

```sql
DELETE FROM calidad_animal 
WHERE codigo = ?
```

**Destino:** Repository: `eliminar_calidad(codigo) → None`

**Validaciones Necesarias:**
- ✗ Código existe (service debe validar antes)
- ✗ No hay FK dependencias (asumir no para este catálogo)

**Riesgo:** Alto (soft delete? cascade? unclear)

---

### Query 5: Validar Código (Lectura)

**Ubicación:** Implícita (via `sqlite3.IntegrityError`)

```sql
-- No existe en código, pero debería:
SELECT COUNT(*) FROM calidad_animal WHERE codigo = ?
```

**Destino:** Repository: `existe_calidad(codigo) → bool`

**Riesgo:** Bajo (validación preventiva)

---

### Query 6: Insertar Bulk (Escritura)

**Ubicación:** `importar_excel()`, línea 212

```sql
INSERT INTO calidad_animal (codigo, descripcion, comentario)
VALUES (?, ?, ?)  -- Ejecutada en loop
```

**Destino:** Repository: `insertar_calidad_bulk(List[Dict]) → Tuple[int, List[str]]`

**Batching:** Actualmente sin transacción explícita (cada INSERT = 1 transacción)
- Debería: Service agrupar en transacción o usar BEGIN...COMMIT

**Riesgo:** Muy Alto (no atomic, no rollback on partial failure)

---

## 🏗️ ESTRUCTURA DE TABLA (Inferida)

```sql
CREATE TABLE calidad_animal (
    codigo TEXT PRIMARY KEY,
    descripcion TEXT NOT NULL,
    comentario TEXT
);
```

**Observaciones:**
- ✓ No hay ID numérico (código es PK)
- ✓ No hay estado/activo flag
- ✓ No hay timestamps
- ✓ No hay FK a otras tablas
- ✓ Muy simple (bueno para migración)

---

## ⚠️ RIESGOS IDENTIFICADOS

### Riesgo 1: Detección de Edit vs Insert por Widget State (ALTO)

**Problema:** Línea 118

```python
if self.entry_codigo.cget("state") == "disabled":  # ← Acoplamiento
```

**Por Qué es Riesgo:**
- ✗ UI state determina lógica de negocio
- ✗ Si alguien olvida deshabilitar, hace INSERT duplicado
- ✗ Difícil de testear (requiere widget mock)

**Mitigación:** 
- Service recibe `crear_calidad()` o `actualizar_calidad()` (métodos separados)
- UI llama a uno u otro, sin condicional

---

### Riesgo 2: SQL Directo en UI (ALTO)

**Problema:** 4 métodos con `cursor.execute()`

**Por Qué es Riesgo:**
- ✗ Cambios en esquema requieren modificar UI
- ✗ No testeable (requiere DB real)
- ✗ Difícil rastrear todas las queries

**Mitigación:** 
- Todas las queries → Repository
- UI → Service (sin SQL)

---

### Riesgo 3: No Atomic Bulk Import (ALTO)

**Problema:** Línea 210–217 (loop de INSERTs sin transacción explícita)

**Por Qué es Riesgo:**
- ✗ Si falla en registro 5/10, registros 1–4 quedan insertados (inconsistencia)
- ✗ No hay rollback
- ✗ No hay idempotencia

**Mitigación:** 
- Service.importar_calidades() abre transacción
- Si cualquier INSERT falla, ROLLBACK all
- Retorna (importados, errores) para UI

---

### Riesgo 4: Validaciones Inconsistentes (MEDIO)

**Problema:** 
- Validación "obligatorio" en UI (línea 108)
- Validación "único" en excepción (línea 130)

**Por Qué es Riesgo:**
- ✗ Si UI se salta, DB lo rechaza con mensajes genéricos
- ✗ Service no revalida
- ✗ UX pobre

**Mitigación:** 
- Service revalida TODO (nunca confiar en UI)
- UI muestra errores del service (si es no vacío, si es único, etc.)

---

### Riesgo 5: Conversión de Tipos en UI (BAJO)

**Problema:** Línea 145–149 (conversión NULL → "")

**Por Qué es Riesgo:**
- ✗ Lógica de normalización en UI
- ✗ Si esquema cambia (NULL → default), debe cambiar UI
- ✓ No crítico, pero duplicado

**Mitigación:** 
- Service devuelve `Dict[str, str]` con valores normalizados
- UI solo renderiza

---

## 📝 DECISIONES DE ARQUITECTURA

### Decisión 1: Un Catálogo = Un Método create vs update

**Opción A:** `crear_calidad()`, `actualizar_calidad()` (2 métodos)
- ✓ Claro
- ✓ Sin condicionales
- ✗ Duplicación de validaciones

**Opción B:** `guardar_calidad(codigo, desc, comentario, es_nuevo=True)` (1 método)
- ✓ DRY
- ✗ Condicional en service
- ✗ Menos claro

**Decisión:** **OPCIÓN A** (2 métodos separados, como en Potreros)

---

### Decisión 2: Validación de Código Único

**Opción A:** Service valida antes
```python
if self.existe_calidad(codigo):
    raise ValueError("Código duplicado")
```

**Opción B:** Service atrapa IntegrityError
```python
try:
    self.repo.insertar(...)
except sqlite3.IntegrityError:
    raise ValueError("Código duplicado")
```

**Decisión:** **OPCIÓN A** (proactiva) + **OPCIÓN B** (defensiva fallback)

---

### Decisión 3: Bulk Import Error Handling

**Opción A:** All-or-nothing (transaction ROLLBACK on error)
```python
try:
    BEGIN
    FOR record:
        INSERT
    COMMIT
except:
    ROLLBACK
```

**Opción B:** Partial success (insert what you can, report errors)
```python
FOR record:
    try:
        INSERT
    except:
        errores.append(...)
COMMIT sucessful ones
```

**Decisión:** **OPCIÓN B** (partial success, como importador_excel actual)
- Razón: UI importa desde archivo, algunos datos pueden ser inválidos
- Mejor UX: "Importados 8/10, 2 errores"

---

## 🎯 PREPARACIÓN PARA MIGRACIÓN

### Métodos Repository Necesarios

```python
# Lectura
listar_calidades() → List[Dict[str, str]]
existe_calidad(codigo: str) → bool
obtener_calidad(codigo: str) → Optional[Dict[str, str]]

# Escritura
crear_calidad(codigo: str, descripcion: str, comentario: Optional[str]) → None
actualizar_calidad(codigo: str, descripcion: str, comentario: Optional[str]) → None
eliminar_calidad(codigo: str) → None
insertar_calidad_bulk(List[Dict[str, str]]) → None
```

### Métodos Service Necesarios

```python
# Lectura
listar_calidades() → List[Dict[str, str]]

# Escritura
crear_calidad(codigo: str, descripcion: str, comentario: Optional[str]) → None
    # Valida: código no vacío, no existe
    
actualizar_calidad(codigo: str, descripcion: str, comentario: Optional[str]) → None
    # Valida: código no vacío, existe
    
eliminar_calidad(codigo: str) → None
    # Valida: existe

importar_calidades_bulk(List[Dict]) → Tuple[int, List[str]]
    # Retorna (importados, errores)
    # Maneja IntegrityError, NULL, conversión tipos
```

---

## 📊 IMPACTO DE MIGRACIÓN

### Líneas de Código a Refactorizar

| Componente | Antes | Después | Cambio |
|-----------|-------|---------|--------|
| calidad_animal.py | 350 | 280 | -70 (-20%) |
| configuracion_service.py | 0 | 80 | +80 |
| configuracion_repository.py | 0 | 100 | +100 |
| **Total** | 350 | 460 | +110 (+31%) |

**Nota:** El total aumenta porque separamos capas. UI se reduce, pero aparece lógica centralizada.

### SQL Queries a Mover

| Query | Desde | Hacia |
|-------|-------|-------|
| SELECT calidad_animal | cargar_calidades() | listar_calidades() |
| INSERT calidad_animal | guardar_calidad() | crear_calidad() |
| UPDATE calidad_animal | guardar_calidad() | actualizar_calidad() |
| DELETE calidad_animal | eliminar_calidad() | eliminar_calidad() |
| INSERT bulk (importar) | importar_excel() | importar_calidades_bulk() |
| SELECT COUNT (implicit) | sqlite3.IntegrityError | existe_calidad() |

---

## ✅ PRÓXIMOS PASOS

### FASE 9.0.3.2 — Crear Infraestructura
- [ ] Crear `src/infraestructura/configuracion/configuracion_repository.py` (6 métodos)
- [ ] Crear `src/infraestructura/configuracion/configuracion_service.py` (4 métodos)
- [ ] Crear `src/infraestructura/configuracion/__init__.py`
- [ ] Validar Pylance 0 errores

### FASE 9.0.3.3 — Migración UI
- [ ] Importar service en calidad_animal.py
- [ ] Refactorizar cargar_calidades() → service.listar_calidades()
- [ ] Refactorizar guardar_calidad() → service.crear_calidad() + service.actualizar_calidad()
- [ ] Refactorizar eliminar_calidad() → service.eliminar_calidad()
- [ ] Refactorizar importar_excel() → service.importar_calidades_bulk()
- [ ] Validar Auditor Exit 0

---

## 📖 Referencias

**Patrones Usados:**
- FASE 8.3 (Animales) — Repository + Service + UI
- FASE 8.4 (Reproducción) — Validaciones en service
- FASE 9.0 Week 1 (Potreros) — Lectura gobernada
- FASE 9.0 Week 2 (Ajustes) — Persistencia gobernada

**Archivos Relacionados:**
- [src/modules/configuracion/calidad_animal.py](../src/modules/configuracion/calidad_animal.py) — Código auditado
- FASE9_0_LOG.md — Progreso de FASE 9.0

---

## 🏁 Conclusión Auditoría

**Complejidad:** Muy Baja ✅
- Catálogo simple (3 columnas, sin FK)
- CRUD straightforward
- Sin validaciones complejas

**Riesgo de Migración:** Medio ⚠️
- 4 métodos con SQL directo
- Estado hardcoded (edit vs insert)
- Bulk import sin transacción explícita
- Mitigable con patrón Service

**Confianza:** Alta ✅
- Patrón validado en Potreros + Ajustes
- Riesgos identificados y documentados
- Camino claro a gobernanza

**Recomendación:** Proceder a FASE 9.0.3.2 (Infraestructura)

---

**Autor:** GitHub Copilot  
**Patrón:** Gobernanza Configuración (FASE 9.0.3)  
**Fecha:** 2025-12-19
