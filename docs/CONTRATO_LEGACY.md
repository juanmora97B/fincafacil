# CONTRATO DE CÓDIGO LEGACY

**Proyecto:** FincaFácil v2.0 — ERP Ganadero  
**Fecha de emisión:** 17 de diciembre de 2025  
**Versión:** 1.0  
**Estado:** CONGELADO Y DOCUMENTADO

---

## 1. Propósito del contrato

Este documento define formalmente el **código legacy** del proyecto FincaFácil, estableciendo:

- **Qué se considera legacy** en este proyecto
- **Por qué se congela** el código legacy identificado
- **Qué problema evita** este contrato

### Qué se considera "legacy"

En FincaFácil v2.0, se clasifica como **código legacy** a:

1. **APIs públicas antiguas** con consumidores activos en producción que fueron reemplazadas por APIs modernas, pero se mantienen por compatibilidad hacia atrás.

2. **Wrappers transitivos** que delegan a sistemas legacy para proporcionar interfaces modernas sin romper código existente.

3. **Funciones de compatibilidad** (aliases, re-exports, fallbacks) mantenidas para evitar breaking changes.

4. **Código de limpieza runtime** que auto-sanea bases de datos antiguas durante la inicialización.

5. **Comentarios documentales** que marcan explícitamente secciones legacy mediante `# DEPRECATED`, `# Legacy fallback`, `# compatibilidad`.

### Por qué se congela

El código legacy identificado en FASE 6.1 se **congela** (no se elimina ni refactoriza) porque:

- ✅ **45+ módulos** dependen activamente de APIs legacy
- ✅ **No bloquea** la evolución del sistema ni nuevas funcionalidades
- ✅ **Proporciona compatibilidad** sin complejidad arquitectónica excesiva
- ✅ **Está bien aislado** y documentado con propósito claro
- ✅ **Eliminar legacy** tendría **costo > beneficio**

### Qué problema evita

Este contrato evita:

- 🔴 **Refactors accidentales** de código legacy crítico
- 🔴 **Breaking changes** no planificados en producción
- 🔴 **Pérdida de compatibilidad** con instalaciones antiguas
- 🔴 **Confusión** sobre qué código es legacy vs moderno
- 🔴 **Deuda técnica oculta** sin inventario formal

---

## 2. Definición de Legacy

El código legacy en FincaFácil se clasifica en **tres categorías**:

### 🔴 Legacy ACTIVO (NO TOCAR)

**Definición:** APIs críticas en producción con consumidores activos. Son la **columna vertebral** del sistema actual.

**Características:**
- Consumidas por 10+ módulos
- Infraestructura crítica (BD, logging, validaciones)
- Eliminación causaría colapso masivo del sistema

**Regla:** ❌ **PROHIBIDO modificar, eliminar o refactorizar sin aprobación arquitectónica formal.**

---

### ⚠️ Legacy TRANSITIVO (WRAPPERS)

**Definición:** Código que actúa como puente entre APIs modernas y legacy, delegando ejecución a sistemas antiguos.

**Características:**
- Wrappers sobre funciones legacy
- Context managers modernos que llaman a BD antigua
- Métodos deprecated activos usados internamente

**Regla:** ✅ Permitido mantener indefinidamente. ⚠️ Eliminar solo con plan de migración gradual aprobado.

---

### 🟢 Legacy CONGELADO (COMPATIBILIDAD)

**Definición:** Código sin consumidores activos, mantenido únicamente como red de seguridad (fallbacks, aliases, re-exports).

**Características:**
- 0 consumidores detectados en auditoría
- Protege contra importaciones futuras
- Costo de mantenimiento cercano a cero

**Regla:** ✅ Permitido mantener indefinidamente. 🟡 Candidato a eliminación futura de bajo riesgo (no urgente).

---

## 3. Inventario oficial de APIs Legacy

### Sistema de Base de Datos

| Módulo | API / Función / Clase | Tipo | Consumidores conocidos | Estado |
|--------|----------------------|------|------------------------|--------|
| `database/__init__.py` | `db` (instancia DatabaseManager) | ACTIVO | 26 módulos core | CONGELADO |
| `database.database` | `get_db_connection()` | ACTIVO | 19 módulos core | CONGELADO |
| `database.database` | `verificar_base_datos()` | ACTIVO | Main + inicialización | CONGELADO |
| `database.database` | `inicializar_base_datos()` | ACTIVO | Main + scripts setup | CONGELADO |
| `database.database` | `ejecutar_consulta()` | ACTIVO | Módulos configuración | CONGELADO |
| `database.database` | `obtener_tablas()` | ACTIVO | Scripts diagnóstico | CONGELADO |
| `database.database` | `asegurar_esquema_minimo()` | ACTIVO | Main inicialización | CONGELADO |
| `database.database` | `asegurar_esquema_completo()` | ACTIVO | Main inicialización | CONGELADO |
| `database.__init__.py` | `check_database_exists` (alias) | COMPATIBILIDAD | 0 detectados | CONGELADO |
| `database.__init__.py` | `init_database` (alias) | COMPATIBILIDAD | 0 detectados | CONGELADO |
| `database.__init__.py` | `get_table_info` (alias) | COMPATIBILIDAD | 0 detectados | CONGELADO |
| `database.__init__.py` | `DB_PATH` (variable lazy) | ACTIVO | Connection.py + consumidores | CONGELADO |
| `database.connection` | `get_connection()` context manager | TRANSITIVO | DatabaseManager interno | CONGELADO |
| `database.database` | Limpieza tablas `animal_legacy*` (runtime) | ACTIVO | Auto-ejecutado en init | CONGELADO |
| `database.database` | Limpieza triggers legacy (runtime) | ACTIVO | Auto-ejecutado en init | CONGELADO |

---

### Sistema de Validaciones

| Módulo | API / Función / Clase | Tipo | Consumidores conocidos | Estado |
|--------|----------------------|------|------------------------|--------|
| `modules.utils.validaciones` | `Validador.validar_email()` | TRANSITIVO | `EntryValidado` interno | CONGELADO |
| `modules.utils.validaciones` | `Validador.validar_telefono()` | TRANSITIVO | `EntryValidado` interno | CONGELADO |
| `modules.utils.validaciones` | `validar_texto()` función módulo | COMPATIBILIDAD | 0 externos | CONGELADO |
| `modules.utils.validaciones` | `validar_numero()` función módulo | COMPATIBILIDAD | 0 externos | CONGELADO |
| `modules.utils.__init__` | `validar_texto` (re-export) | COMPATIBILIDAD | 0 (fallback safety) | CONGELADO |
| `modules.utils.__init__` | `validar_numero` (re-export) | COMPATIBILIDAD | 0 (fallback safety) | CONGELADO |
| `modules.utils.__init__` | `validar_email` (re-export) | COMPATIBILIDAD | 0 (fallback safety) | CONGELADO |
| `modules.utils.__init__` | `validar_telefono` (re-export) | COMPATIBILIDAD | 0 (fallback safety) | CONGELADO |

---

### Sistema de Logging

| Módulo | API / Función / Clase | Tipo | Consumidores conocidos | Estado |
|--------|----------------------|------|------------------------|--------|
| `modules.utils.logger` | `_default_logger` (instancia global) | ACTIVO | Infraestructura crítica | CONGELADO |
| `modules.utils.logger` | `get_logger(name)` | ACTIVO | Todos los módulos | CONGELADO |
| `modules.utils.logger` | `log` (alias logger) | ACTIVO | Imports legacy | CONGELADO |
| `modules.utils.logger` | `setup_logger()` | ACTIVO | Scripts inicialización | CONGELADO |

---

### Módulos de Negocio (Lógica de Compatibilidad)

| Módulo | API / Función / Clase | Tipo | Consumidores conocidos | Estado |
|--------|----------------------|------|------------------------|--------|
| `configuracion/empleados.py` | Fallback `from database import db` | ACTIVO | Try-except interno | CONGELADO |
| `animales/registro_animal.py` | Mapeo campos legacy (líneas 669-870) | ACTIVO | Registros históricos | CONGELADO |
| `animales/bitacora_reubicaciones.py` | Regex patrones legacy (líneas 162-184) | ACTIVO | Notas antiguas | CONGELADO |
| `animales/bitacora_comentarios.py` | Alias función (línea 555) | ACTIVO | Integraciones | CONGELADO |
| `main.py` | `sys.path.insert` compatibilidad (línea 38) | ACTIVO | Ejecuciones locales | CONGELADO |
| `main.py` | `asegurar_esquema_minimo()` (línea 736/758) | ACTIVO | BD antiguas | CONGELADO |

---

## 4. Reglas arquitectónicas (OBLIGATORIAS)

Estas reglas son de cumplimiento **obligatorio** para todo desarrollador, arquitecto o mantenedor del proyecto FincaFácil.

### ❌ PROHIBICIONES ABSOLUTAS

1. **❌ NO usar código legacy en nuevas funcionalidades**
   - Todo código nuevo debe usar APIs modernas (`validators.py`, `database.DatabaseManager`)
   - Excepciones requieren aprobación arquitectónica explícita

2. **❌ NO refactorizar código legacy sin fase aprobada**
   - El legacy identificado en FASE 6.1 está congelado
   - Cambios requieren auditoría + plan de migración + aprobación formal

3. **❌ NO eliminar código legacy sin auditoría previa**
   - Incluso aliases con 0 consumidores detectados requieren revisión
   - Eliminar sin análisis puede romper importaciones dinámicas o scripts externos

4. **❌ NO cambiar firmas de funciones legacy en API pública**
   - Firmas congeladas: `get_db_connection(db_path)`, `validar_email(email)`, `get_logger(name)`
   - Cambios de firma = breaking changes críticos

5. **❌ NO mover archivos sin actualizar imports**
   - 45+ archivos tienen imports legacy hardcodeados
   - Mover `database/__init__.py` o `validators.py` requiere migración masiva

---

### ✅ ACCIONES PERMITIDAS

1. **✅ Mantenimiento correctivo**
   - Corregir bugs en código legacy sin cambiar comportamiento
   - Agregar logs para debugging
   - Mejorar mensajes de error

2. **✅ Documentación adicional**
   - Agregar docstrings explicativos
   - Actualizar comentarios sobre propósito legacy
   - Crear guías de migración

3. **✅ Testing de código legacy**
   - Agregar tests unitarios para asegurar estabilidad
   - Validar que fallbacks funcionan correctamente

4. **✅ Código nuevo con APIs modernas**
   - Usar `from modules.utils.validators import validator` (NO `validaciones.py`)
   - Usar `from database import db` o `get_connection()` (ambos soportados)
   - Importar `Logger` directamente, no usar alias legacy

---

## 5. Estrategia de evolución futura (NO AHORA)

Este contrato **NO ejecuta** ninguna de estas opciones. Solo las documenta para referencia futura.

### Opción A: Consolidación gradual de APIs BD

**Descripción:**
1. Crear wrapper unificado `get_connection()` que reemplace ambos sistemas
2. Migrar consumidores de `database.db` → nuevo wrapper (26 archivos)
3. Migrar consumidores de `get_db_connection()` → nuevo wrapper (19 archivos)
4. Deprecar ambos sistemas antiguos con warnings
5. Documentar fecha límite de eliminación (ej: 6 meses)

**Esfuerzo:** ALTO (45 archivos a modificar)  
**Riesgo:** MEDIO (requiere testing exhaustivo)  
**Beneficio:** API unificada, sin duplicación  
**Estado:** NO APROBADO — Requiere fase dedicada (ej: FASE 7.x)

---

### Opción B: Mantener status quo con documentación ✅ (RECOMENDADO ACTUAL)

**Descripción:**
1. Documentar cuáles APIs son legacy en este contrato ✅ (ya ejecutado)
2. Agregar warnings en docstrings de funciones legacy
3. Crear guía de migración para nuevos desarrolladores
4. NO eliminar nada

**Esfuerzo:** BAJO (solo documentación)  
**Riesgo:** CERO  
**Beneficio:** Claridad sin breaking changes  
**Estado:** ✅ ACTIVO — Es el estado actual del proyecto

---

### Opción C: Limpieza quirúrgica de aliases muertos

**Descripción:**
1. Eliminar solo aliases sin consumidores:
   - `check_database_exists`
   - `init_database`
   - `get_table_info`
2. Mantener todo el resto intacto
3. Ejecutar tests completos post-eliminación

**Esfuerzo:** MÍNIMO (3 líneas + actualizar `__all__`)  
**Riesgo:** CERO (sin consumidores detectados)  
**Beneficio:** API más limpia, menos ruido  
**Estado:** CANDIDATO — Puede ejecutarse en FASE futura sin riesgo

---

### Estrategia recomendada

**A corto plazo (próximos 3-6 meses):**
- ✅ Mantener **Opción B** (status quo documentado)
- ⚠️ Evaluar **Opción C** si hay consenso (bajo riesgo, bajo impacto)

**A medio plazo (6-12 meses):**
- ⚠️ Revisar si APIs legacy tienen nuevos consumidores
- ⚠️ Actualizar este contrato si hay cambios arquitectónicos

**A largo plazo (12+ meses):**
- ⚠️ Evaluar **Opción A** solo si:
  - Dual API genera confusión real en equipo
  - Nuevos bugs críticos en código legacy
  - Presión de mantenimiento aumenta significativamente

---

## 6. Señales visuales en código (REFERENCIA)

Este contrato **NO aplica** estas señales todavía. Solo documenta su significado para referencia futura.

### Marcadores propuestos

Si en el futuro se decide marcar código legacy explícitamente en archivos `.py`, usar:

```python
# @legacy
# Indica que esta función/clase es código legacy congelado.
# NO modificar sin aprobación arquitectónica.
# Consultar CONTRATO_LEGACY.md antes de cambios.

# @frozen
# Indica que la firma de esta función está congelada.
# Cambiar parámetros o retorno = breaking change crítico.

# @no-new-usage
# Indica que NO se debe usar en código nuevo.
# Solo mantener para compatibilidad con código existente.
```

### Ejemplo de uso (NO aplicar aún):

```python
# @legacy
# @frozen
# @no-new-usage
def get_db_connection(db_path=None):
    """
    Función legacy para conexión a BD.
    
    LEGACY: Usar `from database import db` en código nuevo.
    Esta función se mantiene solo para compatibilidad.
    """
    ...
```

### Cuándo aplicar marcadores

- ⚠️ Solo si el equipo lo decide en fase futura
- ⚠️ Requiere consenso sobre nomenclatura
- ⚠️ Aplicar de forma consistente en todo el proyecto

**Estado actual:** NO aplicado (solo documentado aquí para referencia).

---

## 7. Estado final del proyecto

### Declaración formal

**El código legacy del proyecto FincaFácil v2.0 se considera:**

- ✅ **CONGELADO** — No se eliminará ni refactorizará sin fase aprobada
- ✅ **DOCUMENTADO** — Inventariado formalmente en este contrato
- ✅ **ESTABLE** — No genera bugs críticos ni bloquea evolución
- ✅ **NO BLOQUEANTE** — No impide desarrollo de nuevas funcionalidades

### Conclusión arquitectónica

Este contrato establece que:

1. El legacy actual es **necesario y justificado** (45+ consumidores activos)
2. Eliminar legacy **costaría más** que mantenerlo documentado
3. El proyecto puede **evolucionar libremente** usando APIs modernas en paralelo
4. Los desarrolladores tienen **claridad** sobre qué es legacy y qué no

### Próximos pasos

**Acciones inmediatas (completadas):**
- ✅ Contrato formal creado
- ✅ Inventario de APIs legacy documentado
- ✅ Reglas arquitectónicas definidas

**Acciones futuras (opcionales):**
- ⚠️ Agregar warnings en docstrings de funciones legacy
- ⚠️ Crear guía de migración para nuevos desarrolladores
- ⚠️ Revisar anualmente si hay cambios en consumidores

**Acciones prohibidas:**
- ❌ Refactorizar código legacy sin aprobación
- ❌ Eliminar APIs congeladas sin auditoría
- ❌ Cambiar firmas de funciones legacy

---

## Anexo: Resumen de clasificación

| Categoría | Elementos | Acción permitida |
|-----------|-----------|------------------|
| **ACTIVO (NO TOCAR)** | 15+ APIs críticas | Solo mantenimiento correctivo |
| **TRANSITIVO (WRAPPERS)** | 4 elementos | Mantener indefinidamente |
| **COMPATIBILIDAD (CONGELADO)** | 7 re-exports/aliases | Mantener por safety |
| **RUNTIME CLEANUP** | 2 funciones auto-limpieza | Mantener indefinidamente |

**Total APIs legacy inventariadas:** 28+  
**Total consumidores activos:** 45+ módulos  
**Riesgo de mantener legacy:** BAJO  
**Riesgo de eliminar legacy:** CRÍTICO

---

## Metadata del contrato

- **Fecha de auditoría base:** 17 de diciembre de 2025
- **Documento fuente:** `AUDITORIA_LEGACY_FASE6_1.md`
- **Versión del contrato:** 1.0
- **Próxima revisión recomendada:** Diciembre 2026 (anual)
- **Autor:** Arquitectura FincaFácil
- **Aprobación:** Pendiente (se considera en vigor tras creación)

---

**FIN DEL CONTRATO**

Este documento es la fuente única de verdad sobre código legacy en FincaFácil v2.0.  
Cualquier cambio futuro en código legacy debe actualizar este contrato.
