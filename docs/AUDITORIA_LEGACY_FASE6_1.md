# AUDITORÍA DE CÓDIGO LEGACY - FASE 6.1

**Fecha:** 17 de diciembre de 2025  
**Proyecto:** FincaFácil v2.0 — ERP Ganadero  
**Alcance:** Auditoría pasiva de shims, wrappers y APIs legacy  
**Tipo:** Solo análisis. Sin cambios de código.

---

## Resumen ejecutivo

### Hallazgos principales
- **NO existe carpeta `/legacy` dedicada** en el proyecto
- El código legacy está **distribuido** en módulos activos mediante:
  - Comentarios `# DEPRECATED`, `# Legacy fallback`, `# compatibilidad`
  - Funciones/clases wrapper sobre APIs modernas
  - Aliases para backward compatibility
  - Tablas BD temporales legacy (eliminadas en runtime)

### Estado actual del legacy
- **Nivel de legacy:** MEDIO-BAJO (controlado y documentado)
- **Patrón dominante:** Wrappers con fallback + comentarios explícitos
- **Riesgo de ruptura:** BAJO (consumidores activos usan ambas APIs)
- **Deuda técnica:** BAJA (legacy bien aislado, con propósito claro)

### Clasificación global
| Categoría | Elementos | Estado | Acción recomendada |
|-----------|-----------|--------|-------------------|
| **API pública activa** | 26+ consumidores | Producción | NO TOCAR |
| **Wrappers transitivos** | 4 elementos | Compatibilidad | MANTENER (corto plazo) |
| **Legacy muerto** | 0 detectados | N/A | N/A |
| **Comentarios históricos** | ~69 marcas | Documentación | REVISAR (bajo impacto) |

---

## Tabla de inventario legacy

### 1. Sistema de Base de Datos (`database/`)

#### 1.1. `database/__init__.py`

**Propósito:** Punto de entrada unificado para acceso a BD; mantiene compatibilidad con sistema antiguo

**Exports legacy:**
```python
# Sistema legacy (comentario línea 84)
"get_db_connection",          # Función antigua
"verificar_base_datos",
"inicializar_base_datos", 
"ejecutar_consulta",
"obtener_tablas",
"asegurar_esquema_minimo",
"asegurar_esquema_completo",

# Aliases para compatibilidad (línea 92)
"check_database_exists",      # Alias de verificar_base_datos
"init_database",              # Alias de inicializar_base_datos
"get_table_info",             # Alias de obtener_tablas
"DB_PATH",                    # Variable lazy (línea 32)
```

**Exports modernos (NO legacy):**
```python
"get_connection",             # Context manager nuevo
"db",                         # DatabaseManager instance
"DatabaseManager",            # Clase moderna
```

**Consumidores activos:**
- **Forma antigua (`from database import db`):** 26 archivos
  - `salud_main.py`, `reportes_profesional.py`, `reportes_main.py`
  - `potreros_main.py`, `nomina_main.py`, `insumos_main.py`
  - `herramientas_main.py`, `tipo_explotacion.py`, `sectores.py`
  - `razas.py`, `proveedores.py`, `procedencia.py`, `potreros.py`
  - `motivos_venta.py`, `lotes.py`, `fincas.py`, `empleados.py` (fallback)
  - `diagnosticos.py`, `destino_venta.py`, `condiciones_corporales.py`
  - `causa_muerte.py`, `calidad_animal.py`, `importar_excel.py`
  - `bitacora_reubicaciones.py`, `bitacora_comentarios.py`, `actualizacion_inventario.py`

- **Forma moderna (`from database.database import get_db_connection`):** 19 archivos
  - `ventas_main.py`, `validators.py`, `sistema_alertas.py`
  - `notificaciones.py`, `importador_excel.py`, `dashboard_main.py`
  - `empleados.py` (try-except mixto), `animales/__init__.py`
  - `ventana_graficas.py`, `reubicacion.py`, `realizar_inventario.py`
  - `modal_reubicar_animal.py`, `modal_editar_animal.py`, `inventario_v2.py`
  - `ficha_animal.py`, `bitacora_historial_reubicaciones.py`
  - `bitacora_comentarios.py`, `ajustes_main.py` (src + modules)

**Tipo:** API pública dual (moderna + legacy)

**Clasificación:** ✅ **ACTIVO** — Ambas APIs en uso simultáneo

**Riesgo si se elimina:** 🔴 **CRÍTICO** — 26 módulos dependen de API antigua; breaking changes masivos

---

#### 1.2. `database/connection.py`

**Propósito:** Wrapper moderno sobre sistema legacy; proporciona context manager

**Legacy detectado:**
```python
# Línea 17: Importar las funciones existentes del sistema legacy
from .database import get_db_connection, DB_PATH
```

**Función principal:**
```python
@contextmanager
def get_connection(db_path: Optional[str] = None) -> Iterator[sqlite3.Connection]:
    # Delegar al sistema existente (línea 42)
    with get_db_connection(db_path or DB_PATH) as conn:
        yield conn
```

**Consumidores:** 1 consumidor directo (`connection.py` mismo en documentación; 0 externos directos)

**Tipo:** Shim transitivo (moderno → legacy)

**Clasificación:** ⚠️ **TRANSITIVO** — Wrapper activo que delega a legacy

**Riesgo si se elimina:** 🟡 **MEDIO** — Clase `DatabaseManager` depende de él, pero pocos consumidores externos

---

#### 1.3. `database/database.py`

**Propósito:** Motor principal de BD; maneja tablas legacy en runtime

**Legacy detectado:**
```python
# Líneas 194-216: Limpieza de tablas legacy residuales
legacy_tables = ['animal_legacy', 'animal_legacy_temp']
for legacy_table in legacy_tables:
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (legacy_table,))
    if cur.fetchone():
        cur.execute(f"DROP TABLE IF EXISTS {legacy_table}")
        logger.info(f"Tabla legacy '{legacy_table}' eliminada durante inicialización")

# Línea 209: Eliminar triggers con referencias legacy
cur.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND sql LIKE '%legacy%'")
legacy_triggers = cur.fetchall()
for (trigger_name,) in legacy_triggers:
    cur.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
    logger.info(f"Trigger legacy '{trigger_name}' eliminado")

# Línea 235: Detectar columnas legacy (id_animal, autor, nota)
# Línea 872: Tabla legacy de inventario (opcional - mantener por compatibilidad)
# Línea 1124: Animal (post-normalización: sin columnas legacy 'raza', 'id_raza', 'id_lote')
```

**Tipo:** Código de limpieza runtime (auto-sanea BD antiguas)

**Clasificación:** ✅ **ACTIVO** — Ejecuta limpieza automática al inicializar BD

**Riesgo si se elimina:** 🟢 **BAJO** — Solo afecta a BD antiguas; nuevas instalaciones no tienen tablas legacy

---

### 2. Sistema de Validaciones (`modules/utils/`)

#### 2.1. `validaciones.py`

**Propósito:** Validaciones UI con wrappers sobre `validators.py`

**Legacy detectado:**
```python
# Línea 156: # DEPRECATED: Wrapper to validators.FincaFacilValidator.validar_email
@staticmethod
def validar_email(valor: str, nombre_campo: str = "Email", permitir_vacio: bool = False):
    if _VALIDATOR_AVAILABLE:
        es_valido, mensaje = _validator_instance.validar_email(valor)
        email_limpio = valor.strip().lower() if es_valido else ""
        return es_valido, email_limpio, "" if es_valido else mensaje
    # Fallback manual si validators no disponible
    ...

# Línea 182: # DEPRECATED: Wrapper to validators.FincaFacilValidator.validar_telefono
@staticmethod
def validar_telefono(valor: str, nombre_campo: str = "Teléfono", permitir_vacio: bool = False):
    if _VALIDATOR_AVAILABLE:
        es_valido, mensaje = _validator_instance.validar_telefono(valor)
        telefono_limpio = valor.strip() if es_valido else ""
        return es_valido, telefono_limpio, "" if es_valido else mensaje
    # Fallback manual si validators no disponible
    ...

# Línea 354: Funciones de validación adicionales para compatibilidad
def validar_texto(...): ...
def validar_numero(...): ...
```

**Consumidores:** 0 directos externos (FASE 5.2 eliminó wrappers módulo-level muertos)

**Tipo:** Métodos estáticos deprecated en clase `Validador`

**Clasificación:** ⚠️ **TRANSITIVO** — Usados internamente por `EntryValidado` y `ValidadorFormulario`

**Riesgo si se elimina:** 🟡 **MEDIO** — Widgets UI (`EntryValidado`) dependen de estos métodos

---

#### 2.2. `modules/utils/__init__.py`

**Propósito:** API pública de utils; exporta validaciones legacy

**Legacy detectado:**
```python
# Línea 6-7: API Legacy / Compatibilidad (Categoría B)
# Mantenida para backward compatibility; consumidores usan import directo
try:
    from modules.utils.validaciones import (
        validar_texto, validar_numero, validar_email, validar_telefono
    )
except ImportError:
    def validar_texto(*args, **kwargs): return (True, None, "")
    def validar_numero(*args, **kwargs): return (True, None, "")
    def validar_email(*args, **kwargs): return (True, None, "")
    def validar_telefono(*args, **kwargs): return (True, None, "")
```

**Consumidores:** 0 externos (FASE 5.3 confirmó que nadie usa `from modules.utils import validar_*`)

**Tipo:** Re-exports con fallback

**Clasificación:** 🗑️ **MUERTO** (re-export) pero **MANTENER** (fallback safety)

**Riesgo si se elimina:** 🟢 **BAJO** — No hay consumidores, pero fallbacks protegen contra importaciones futuras

---

#### 2.3. `logger.py`

**Propósito:** Sistema de logging; mantiene API legacy

**Legacy detectado:**
```python
# Línea 100: Logger global para compatibilidad
_default_logger = Logger()

def get_logger(name=None):
    """Obtiene un logger por nombre."""
    if name:
        return Logger(name)
    return _default_logger

# Línea 110: Para compatibilidad con imports anteriores
log = _default_logger.logger

def setup_logger(name="FincaFacil", level=None):
    # Línea 115: Función de compatibilidad que retorna un logger configurado.
    return Logger(name)
```

**Consumidores:** Incontables (logger es infraestructura crítica)

**Tipo:** Funciones helper de compatibilidad

**Clasificación:** ✅ **ACTIVO** — API pública estable

**Riesgo si se elimina:** 🔴 **CRÍTICO** — Rompe sistema de logging en todo el proyecto

---

### 3. Módulos de Negocio

#### 3.1. `configuracion/empleados.py`

**Legacy detectado:**
```python
# Línea 14-16: Unificación de acceso a BD con nuevo módulo central
try:
    from database.database import get_db_connection as get_connection
except ImportError:
    from database import db  # Legacy fallback
    get_connection = db.get_connection  # type: ignore
```

**Tipo:** Try-except con fallback dual

**Clasificación:** ✅ **ACTIVO** — Patrón de migración gradual

**Riesgo si se elimina:** 🟡 **MEDIO** — Único archivo con fallback explícito; otros usan solo una forma

---

#### 3.2. Comentarios legacy en lógica de negocio

**Archivos con marcas `# legacy` / `# compatibilidad`:**
- `animales/registro_animal.py` (líneas 669, 785, 851, 870): Backward compatibility mapeo campos
- `animales/bitacora_reubicaciones.py` (líneas 162-184): Patrón regex para notas legacy
- `animales/bitacora_comentarios.py` (línea 555): Alias función para compatibilidad
- `configuracion/tipo_explotacion.py` (línea 260): Compatibilidad acentos en búsqueda
- `configuracion/destino_venta.py` (línea 290): Compatibilidad mapeo campos
- `main.py` / `src/main.py` (líneas 38, 736/758): sys.path + esquema BD antiguas

**Tipo:** Comentarios documentales + lógica de migración

**Clasificación:** ✅ **ACTIVO** — Código en uso para soportar datos antiguos

**Riesgo si se elimina:** 🟡 **MEDIO** — Pérdida de compatibilidad con registros históricos

---

## Clasificación por tipo

### ✅ ACTIVO — API pública en producción (NO TOCAR)

| Elemento | Ubicación | Consumidores | Razón crítica |
|----------|-----------|--------------|---------------|
| `database.db` (instancia) | `database/__init__.py` | 26 módulos | API principal de acceso a BD |
| `get_db_connection()` | `database.database` | 19 módulos | Contexto de conexión legacy |
| `Logger` + helpers | `modules.utils.logger` | Todos | Infraestructura logging |
| `verificar_base_datos()` | `database.database` | Main + inicialización | Validación BD existente |
| Métodos `Validador.*` | `modules.utils.validaciones` | Widgets UI | Validación formularios |

**Acción:** Mantener congelado. Documentar como API legacy estable.

---

### ⚠️ TRANSITIVO — Wrappers activos sobre legacy (MANTENER corto plazo)

| Elemento | Ubicación | Delegación | Razón |
|----------|-----------|------------|-------|
| `get_connection()` context manager | `database.connection` | → `get_db_connection()` | Wrapper moderno sobre legacy |
| `DatabaseManager.get_connection()` | `database.connection` | → `database.db.get_connection()` | Método instancia sobre global |
| `Validador.validar_email()` | `modules.utils.validaciones` | → `validators.FincaFacilValidator` | Wrapper deprecated activo |
| `Validador.validar_telefono()` | `modules.utils.validaciones` | → `validators.FincaFacilValidator` | Wrapper deprecated activo |

**Acción:** Mantener por ahora. Evaluar migración gradual en FASE futura (no urgente).

---

### 🗑️ MUERTO — Sin consumidores pero mantenido por safety (REVISAR futuro)

| Elemento | Ubicación | Consumidores | Razón de mantener |
|----------|-----------|--------------|-------------------|
| `validar_texto` (re-export) | `modules.utils.__init__` | 0 | Fallback safety (FASE 5.3) |
| `validar_numero` (re-export) | `modules.utils.__init__` | 0 | Fallback safety (FASE 5.3) |
| `validar_email` (re-export) | `modules.utils.__init__` | 0 | Fallback safety (FASE 5.3) |
| `validar_telefono` (re-export) | `modules.utils.__init__` | 0 | Fallback safety (FASE 5.3) |

**Acción:** Mantener fallbacks. No hay urgencia de eliminar (FASE 5.4 ya limpió exports públicos).

---

### 🏗️ RUNTIME CLEANUP — Código de limpieza automática (MANTENER)

| Elemento | Ubicación | Propósito |
|----------|-----------|-----------|
| Limpieza tablas `animal_legacy*` | `database.database:194-216` | Drop tables legacy al inicializar |
| Limpieza triggers legacy | `database.database:209-213` | Drop triggers con SQL LIKE '%legacy%' |
| Detección columnas legacy | `database.database:235, 1124` | Comentarios sobre esquema antiguo |

**Acción:** Mantener indefinidamente. Protege contra BD antiguas sin romper nuevas instalaciones.

---

## Observaciones técnicas

### 1. **Patrón dominante: Dual API con fallback**
```python
# Patrón repetido en 3+ archivos:
try:
    from nuevo_modulo import funcion_moderna
except ImportError:
    from legacy_modulo import funcion_antigua  # Legacy fallback
    funcion_moderna = funcion_antigua
```
- ✅ **Ventaja:** Migración gradual sin breaking changes
- ⚠️ **Riesgo:** Mantiene duplicación de APIs indefinidamente
- 🎯 **Recomendación:** Documentar cuándo se eliminará fallback

### 2. **No hay carpeta `/legacy` dedicada**
- Todo el legacy está **inline** en módulos activos
- Comentarios explícitos marcan secciones legacy
- ✅ **Ventaja:** Código legacy visible y documentado
- ⚠️ **Riesgo:** Dificulta identificación de deuda técnica global

### 3. **Aliases para backward compatibility**
```python
# database/__init__.py línea 92
check_database_exists = verificar_base_datos
init_database = inicializar_base_datos
get_table_info = obtener_tablas
```
- ✅ Sin consumidores detectados (grep no encontró usos)
- 🎯 **Candidatos a eliminación futura** (muy bajo riesgo)

### 4. **Comentarios legacy sin código asociado**
- `plantillas_carga.py:35` — Comentario sobre compatibilidad archivos antiguos
- `icons.py:6, 109` — Comentario sobre parámetros legacy
- `configuracion/*` — Múltiples comentarios sobre mapeo campos

- ✅ **Son documentación histórica útil**
- 🎯 No requieren acción (mantener)

### 5. **Sistema de limpieza BD runtime es defensivo**
```python
# database.database:194-216
# Elimina tablas 'animal_legacy' automáticamente
# NO afecta a instalaciones nuevas (tablas no existen)
# SÍ protege migraciones de BD antiguas
```
- ✅ **Diseño robusto y seguro**
- 🎯 Mantener indefinidamente (costo: 0, beneficio: alto)

---

## Riesgos potenciales

### 🔴 RIESGO CRÍTICO — Eliminar API pública activa

| Elemento en riesgo | Impacto | Archivos afectados |
|-------------------|---------|-------------------|
| `database.db` | Breaking change masivo | 26 módulos core |
| `get_db_connection()` | Breaking change alto | 19 módulos core |
| `Logger` + helpers | Colapso sistema logging | Todos |

**Mitigación:** NO TOCAR estos elementos bajo ninguna circunstancia sin plan de migración masiva.

---

### 🟡 RIESGO MEDIO — Eliminar wrappers transitivos

| Elemento en riesgo | Impacto | Consecuencia |
|-------------------|---------|--------------|
| `Validador.validar_email()` | Widgets UI rompen | `EntryValidado` necesita refactor |
| `DatabaseManager.get_connection()` | Código moderno rompe | Consumidores de `db.get_connection()` |
| Fallback `empleados.py` | Importación falla | Solo afecta a 1 archivo |

**Mitigación:** Requiere migración coordinada de consumidores antes de eliminar.

---

### 🟢 RIESGO BAJO — Eliminar aliases sin consumidores

| Elemento en riesgo | Impacto | Justificación |
|-------------------|---------|---------------|
| `check_database_exists` | Ninguno | 0 consumidores detectados |
| `init_database` | Ninguno | 0 consumidores detectados |
| `get_table_info` | Ninguno | 0 consumidores detectados |
| Re-exports `validar_*` en `__init__.py` | Ninguno | FASE 5.3 confirmó 0 consumidores |

**Mitigación:** Eliminar en FASE futura (no urgente); mantener por safety.

---

## Recomendaciones preliminares

### 🎯 FASE 6.2 (Futuro — NO ahora)

#### Opción A: Consolidación gradual de APIs BD
1. Crear wrapper unificado `get_connection()` que reemplace ambos sistemas
2. Migrar consumidores de `database.db` → nuevo wrapper (26 archivos)
3. Migrar consumidores de `get_db_connection()` → nuevo wrapper (19 archivos)
4. Deprecar ambos sistemas antiguos
5. Documentar fecha límite de eliminación

**Esfuerzo:** ALTO (45 archivos a modificar)  
**Riesgo:** MEDIO (requiere testing exhaustivo)  
**Beneficio:** API unificada, sin duplicación

---

#### Opción B: Mantener status quo con documentación

1. Documentar cuáles APIs son legacy en `CONTRATO_*.md`
2. Agregar warnings en docstrings de funciones legacy
3. Crear guía de migración para nuevos desarrolladores
4. NO eliminar nada

**Esfuerzo:** BAJO (solo documentación)  
**Riesgo:** CERO  
**Beneficio:** Claridad sin breaking changes

---

#### Opción C: Limpieza quirúrgica de aliases muertos

1. Eliminar solo aliases sin consumidores:
   - `check_database_exists`
   - `init_database`
   - `get_table_info`
2. Mantener todo el resto intacto

**Esfuerzo:** MÍNIMO (3 líneas + actualizar `__all__`)  
**Riesgo:** CERO (sin consumidores)  
**Beneficio:** API más limpia, menos ruido

---

### 🚫 NO HACER (Destructivo / Alto riesgo)

- ❌ Eliminar `database.db` o `get_db_connection()` sin migración masiva
- ❌ Remover sistema de limpieza runtime de tablas legacy
- ❌ Borrar métodos `Validador.validar_*` sin refactor de widgets UI
- ❌ Cambiar firmas de funciones legacy en API pública
- ❌ Mover archivos sin actualizar imports (45+ archivos afectados)

---

## Conclusión

### Estado del proyecto: ✅ SALUDABLE

- **Legacy controlado:** Bien documentado con comentarios explícitos
- **Patrón coherente:** Dual API + fallbacks en puntos críticos
- **Deuda técnica:** BAJA (legacy tiene propósito claro y activo)
- **Riesgo de mantenimiento:** BAJO (código legacy aislado y testeable)

### Recomendación arquitectónica: MANTENER

**Por qué:**
1. El legacy actual **no impide evolución del sistema**
2. Los wrappers proporcionan **compatibilidad sin complejidad**
3. La limpieza runtime de BD es **defensiva y necesaria**
4. El costo de eliminar legacy > beneficio obtenido

**Acción inmediata:**
- ✅ Documentar APIs legacy en contratos existentes
- ✅ Agregar warnings en docstrings (opcional)
- ❌ NO eliminar código en FASE 6.2 sin aprobación explícita

**Siguiente paso:**
- Si se desea limpieza: Ejecutar **Opción C** (aliases muertos) en FASE 6.2
- Si se desea unificación: Planificar **Opción A** (migración gradual) en FASE 7.x
- Si se desea estabilidad: Ejecutar **Opción B** (documentar y mantener)

---

**FASE 6.1 COMPLETADA** ✅  
**Cambios realizados:** NINGUNO (solo análisis pasivo)  
**Archivos modificados:** 0  
**Breaking changes:** 0  
**Riesgo introducido:** CERO

Siguiente paso: Revisar este documento y definir estrategia para FASE 6.2 (si aplica).
