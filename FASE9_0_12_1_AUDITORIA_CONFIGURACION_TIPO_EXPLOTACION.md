# 🔍 AUDITORÍA — Configuración · Tipo Explotación (Catálogo #13)

**Fecha:** 2025-12-22  
**Archivo:** `src/modules/configuracion/tipo_explotacion.py`  
**Estado inicial:** Arquitectura violada (SQL directo en UI)  
**Objetivo:** Cerrar Configuración al 100% (13/13)

---

## 1. RESUMEN EJECUTIVO

**Archivo analizado:** tipo_explotacion.py (349 líneas)

### Violaciones críticas detectadas:
- ❌ **7×** `db.get_connection()` — SQL directo en UI
- ❌ **7×** `cursor = conn.cursor()` — Gestión de cursores en presentación
- ❌ **10×** `cursor.execute()` — Queries embebidos
- ❌ **3×** `conn.commit()` — Transacciones en UI
- ❌ **1×** `DELETE FROM tipo_explotacion` — Hard delete (línea 226)
- ❌ **0** uso de `ConfiguracionService` — Bypass total de capa de servicio

**Campos de la tabla:**
```sql
CREATE TABLE tipo_explotacion (
    codigo TEXT PRIMARY KEY,
    descripcion TEXT NOT NULL,
    categoria TEXT,  -- 'Carne', 'Leche', 'Doble Propósito', etc
    comentario TEXT,
    estado TEXT DEFAULT 'Activo'
)
```

**Características del catálogo:**
- ✅ Estados binarios: {'Activo', 'Inactivo'}
- ✅ Sin FKs — Tabla independiente
- ✅ PK simple: código (TEXT)
- ✅ Campo categoría con valores predefinidos
- ✅ CRUD completo con importación Excel
- ✅ Inline editing (campo código disabled en modo edición)

---

## 2. INVENTARIO DE VIOLACIONES

### 2.1 Método: `guardar_tipo_explotacion` (líneas 126-166)
**Tipo de operación:** INSERT + UPDATE (modo dual según estado del campo)

**SQL encontrado:**
```python
# Línea 136-149 (UPDATE cuando código está disabled)
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tipo_explotacion 
        SET descripcion = ?, categoria = ?, comentario = ?
        WHERE codigo = ?
    """, (descripcion, self.combo_categoria.get(), 
          self.text_comentario.get("1.0", "end-1c").strip(), codigo))
    
# Línea 150-159 (INSERT cuando código está enabled)
    cursor.execute("""
        INSERT INTO tipo_explotacion (codigo, descripcion, categoria, comentario, estado)
        VALUES (?, ?, ?, ?, ?)
    """, (codigo, descripcion, self.combo_categoria.get(),
          self.text_comentario.get("1.0", "end-1c").strip(), "Activo"))
    conn.commit()
```

**Violaciones:**
- ❌ 1× `get_connection`
- ❌ 1× `cursor`
- ❌ 2× `execute` (UPDATE + INSERT condicional)
- ❌ 1× `commit`
- ❌ Sin validación de campos requeridos antes de SQL
- ❌ Sin normalización de datos (.strip() manual, sin .upper()/.title())
- ❌ IntegrityError manejado localmente

---

### 2.2 Método: `cargar_tipos_explotacion` (líneas 168-187)
**Tipo de operación:** SELECT (carga de tabla)

**SQL encontrado:**
```python
# Línea 177-179
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT codigo, descripcion, categoria, comentario 
        FROM tipo_explotacion 
        WHERE estado = 'Activo'
    """)
```

**Violaciones:**
- ❌ 1× `get_connection`
- ❌ 1× `cursor`
- ❌ 1× `execute`
- ❌ Filtrado manual por estado en SQL

---

### 2.3 Método: `editar_tipo_explotacion` (líneas 189-216)
**Tipo de operación:** SELECT (carga para edición inline)

**SQL encontrado:**
```python
# Línea 196-199
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT codigo, descripcion, categoria, comentario 
        FROM tipo_explotacion 
        WHERE codigo = ?
    """, (codigo,))
    row = cursor.fetchone()
```

**Violaciones:**
- ❌ 1× `get_connection`
- ❌ 1× `cursor`
- ❌ 1× `execute`
- ❌ Carga directa sin pasar por servicio

**Patrón inline editing:**
- ✅ Campo código disabled en modo edición (línea 204)
- ✅ Formulario reutilizado (no modal window)

---

### 2.4 Método: `eliminar_tipo_explotacion` (líneas 218-233) ⚠️ CRÍTICO
**Tipo de operación:** DELETE (hard delete)

**SQL encontrado:**
```python
# Línea 225-227
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tipo_explotacion WHERE codigo = ?", (codigo,))
    conn.commit()
```

**VIOLACIÓN CRÍTICA:**
- 🔴 **HARD DELETE** — `DELETE FROM` viola política de soft delete
- ❌ 1× `get_connection`
- ❌ 1× `cursor`
- ❌ 1× `execute`
- ❌ 1× `commit`

**Mensaje UX actual:** "Esta acción no se puede deshacer"

**Corrección requerida:**
```python
# Cambiar a soft delete
service.cambiar_estado_tipo_explotacion(codigo, 'Inactivo')
# Mensaje UX: "Podrá reactivarlo desde la base de datos"
```

---

### 2.5 Método: `importar_excel` (líneas 239-349)
**Tipo de operación:** Bulk INSERT con validaciones

**SQL encontrado:**
```python
# Línea 292-338 (loop de importación)
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    for idx, fila in enumerate(filas, start=2):
        # Línea 307: Verificación de existencia
        cursor.execute("SELECT COUNT(*) FROM tipo_explotacion WHERE codigo = ?", (codigo,))
        
        if cursor.fetchone()[0] > 0:
            errores.append(f"Fila {idx}: ya existe")
            continue
        
        # Línea 312-317: Inserción
        cursor.execute("""
            INSERT INTO tipo_explotacion (codigo, descripcion, categoria, comentario, estado)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo, descripcion, categoria, comentario, estado))
    
    conn.commit()
```

**Violaciones:**
- ❌ 1× `get_connection`
- ❌ 1× `cursor`
- ❌ 2× `execute` por fila (COUNT + INSERT) → **2N queries en loop**
- ❌ 1× `commit` único al final
- ❌ Validación de unicidad vía SELECT COUNT en loop (N+1 problem)

**Complejidad adicional:**
- Normalización de encabezados (variantes: código/codigos/código)
- Inferencia de categoría por palabras clave en comentario
- Compatibilidad con acentos en columnas

---

## 3. ANÁLISIS DE DEPENDENCIAS

### 3.1 Imports actuales
```python
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
import sqlite3  # ← A ELIMINAR
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db  # ← A ELIMINAR
from modules.utils.importador_excel import parse_excel_to_dicts  # ← MANTENER
```

### 3.2 Imports requeridos después de migración
```python
from typing import Optional
from services.configuracion_service import ConfiguracionService
```

### 3.3 Estado tracking requerido
```python
def __init__(self, master):
    super().__init__(master)
    self._service = ConfiguracionService()
    self._tipo_editando_codigo: Optional[str] = None  # Tracking para create vs update
    self.pack(fill="both", expand=True)
    self.crear_widgets()
    self.cargar_tipos_explotacion()
```

---

## 4. RESUMEN DE MÉTRICAS

| Métrica | Valor |
|---------|-------|
| **Líneas totales** | 349 |
| **get_connection** | 7 |
| **cursor.execute** | 10+ (loop en importar) |
| **commits** | 3 |
| **Hard deletes** | 1 🔴 |
| **Métodos afectados** | 4 (guardar, cargar, editar, eliminar, importar) |
| **FKs a validar** | 0 (tabla independiente) |
| **Estados** | 2 ('Activo', 'Inactivo') |
| **PK** | codigo (TEXT) |

---

## 5. PATRÓN DE MIGRACIÓN REQUERIDO

### Repository (configuracion_repository.py)
```python
# Lectura (4 métodos)
def listar_tipos_explotacion_activos() -> List[Dict]:
    # SELECT * FROM tipo_explotacion WHERE estado='Activo'
    
def obtener_tipo_explotacion(codigo: str) -> Optional[Dict]:
    # SELECT * WHERE codigo=? AND estado='Activo'
    
def existe_codigo_tipo_explotacion(codigo: str) -> bool:
    # SELECT COUNT(*) WHERE codigo=?

# Escritura (3 métodos)
def crear_tipo_explotacion_base(codigo, descripcion, categoria, comentario, estado) -> None:
    # INSERT tipo_explotacion (sin validaciones)
    
def actualizar_tipo_explotacion_base(codigo, descripcion, categoria, comentario) -> None:
    # UPDATE tipo_explotacion WHERE codigo=?
    
def cambiar_estado_tipo_explotacion(codigo: str, estado: str) -> None:
    # UPDATE estado WHERE codigo=?
```

### Service (configuracion_service.py)
```python
# Lectura (3 métodos)
def listar_tipos_explotacion_activos() -> List[Dict]:
    # Normalización: .upper() codigo, .title() descripcion
    
def obtener_tipo_explotacion(codigo: str) -> Dict:
    # Validar existencia → ValueError si no existe
    
# Escritura (4 métodos con validaciones)
def crear_tipo_explotacion(codigo, descripcion, categoria, comentario='') -> None:
    # Validar: campos requeridos, categoría válida, unicidad
    # Normalizar: .strip().upper() codigo, .strip().title() descripcion/categoria
    
def actualizar_tipo_explotacion(codigo, descripcion, categoria, comentario='') -> None:
    # Validar existencia, campos requeridos, categoría válida
    
def cambiar_estado_tipo_explotacion(codigo, estado) -> None:
    # Validar estado ∈ {'Activo', 'Inactivo'}
```

**Categorías válidas:**
```python
CATEGORIAS_VALIDAS = {
    'Carne', 'Leche', 'Doble Propósito', 
    'Reproducción', 'Huevos', 'Otros'
}
```

---

## 6. RIESGOS Y MITIGACIONES

### Riesgo 1: Hard delete existente
**Impacto:** Datos pueden perderse permanentemente  
**Mitigación:** Convertir a soft delete vía `cambiar_estado_tipo_explotacion`  
**Mensaje UX:** "Tipo marcado como inactivo. Podrá reactivarlo desde la base de datos."

### Riesgo 2: Loop N+1 en importar_excel
**Impacto:** Performance degradada con archivos grandes  
**Mitigación:** Usar `service.crear_tipo_explotacion` que valida internamente unicidad sin COUNT extra

### Riesgo 3: Categoría como texto libre
**Impacto:** Inconsistencias ('Carne' vs 'carne' vs 'CARNE')  
**Mitigación:** Validación en servicio con set CATEGORIAS_VALIDAS + normalización .title()

### Riesgo 4: PK como TEXT (codigo)
**Impacto:** Comparaciones case-sensitive  
**Mitigación:** Normalización consistente .upper() en create + búsquedas

---

## 7. PRÓXIMOS PASOS (PLAYBOOK)

✅ **PASO 1 COMPLETADO** — Este documento

**PASO 2:** Repository extension (7 métodos)  
**PASO 3:** Service extension (7 métodos + validaciones)  
**PASO 4:** UI migration (eliminar 7× get_connection, +inline editing tracking)  
**PASO 5:** Validation (Pylance 0, grep 0, auditor 0)  
**PASO 6:** Documentation (FASE9_0_12_2_MIGRACION)  
**PASO 7:** Log update → **13/13 = 100% Configuration** 🎯

---

## 8. DECISIONES DE DISEÑO

### Categorías como catálogo cerrado
**Decisión:** Validar categoría contra set predefinido en lugar de tabla separada  
**Razón:** Solo 6 valores posibles, bajo cambio, evita JOIN innecesario  
**Trade-off:** Si crece a >10 categorías, considerar tabla catalog_categoria

### PK tipo TEXT vs INT autoincrement
**Decisión:** Mantener codigo TEXT como PK (diseño existente)  
**Razón:** Negocio prefiere códigos mnemónicos ('CARNE01', 'LECHE_HOLS')  
**Mitigación:** Normalización .upper() estricta en create/update

### Inline editing sin modal
**Decisión:** Reutilizar formulario principal con estado tracking  
**Razón:** Patrón ya validado en Lotes (-50%) y Sectores (-77%)  
**Implementación:** `_tipo_editando_codigo: Optional[str]` + disable codigo field

---

**FIN DE AUDITORÍA**  
**Próximo:** PASO 2 — Repository extension
