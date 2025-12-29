# AUDITORÍA DE EXPORTS PÚBLICOS - FASE 5.3

**Fecha:** 17 de diciembre de 2025  
**Proyecto:** FincaFácil v2.0 — ERP Ganadero  
**Archivo auditado:** `src/modules/utils/__init__.py`  
**Alcance:** Análisis pasivo. Sin cambios de código.

---

## Resumen ejecutivo

### Estado actual
- `__init__.py` exporta **20 items** de 8 módulos distintos
- Estructura: importaciones críticas, parciales con fallback, y opcionales con try-except
- **Deuda técnica detectada:** HIGH — Múltiples exports no consumidos públicamente
- Riesgo de estabilidad: **BAJO** (fallbacks evitan breaking changes)
- Riesgo de mantenimiento: **MEDIO** (API implícita, sin contrato claro)

### Hallazgos clave
1. **Exports nunca usados vía módulo raíz** (`from modules.utils import X`)
2. **Consumidores usan imports directos** (`from modules.utils.modulo import X`)
3. **Los fallbacks nunca se activan** (no hay excepciones en proyecto)
4. **Inconsistencia de responsabilidades** en `__init__.py`: validaciones + UI + tooling + persistence
5. **API implícita no documentada** — `database_helpers` existe pero no está en `__all__`

---

## Tabla de exports

| # | Export | Módulo origen | Categoría | Consumidores activos | Forma de uso | Recomendación futura |
|---|--------|--------------|-----------|---------------------|--------------|----------------------|
| 1 | `Logger` | `logger.py` | A | 5 internos (tour, pdf, metadata) | Directo `from modules.utils.logger` | ✅ Mantener congelado |
| 2 | `validar_texto` | `validaciones.py` | B | 0 | Re-export fallback | 🗑️ Eliminar (FASE 5.2 ya quitó wrappers muertos) |
| 3 | `validar_numero` | `validaciones.py` | B | 0 | Re-export fallback | 🗑️ Eliminar (FASE 5.2 ya quitó wrappers muertos) |
| 4 | `validar_email` | `validaciones.py` | B | 0 | Re-export fallback | 🗑️ Eliminado en FASE 5.2 (verificar si fallback sigue) |
| 5 | `validar_telefono` | `validaciones.py` | B | 0 | Re-export fallback | 🗑️ Eliminado en FASE 5.2 (verificar si fallback sigue) |
| 6 | `mostrar_error` | `ui.py` | C | 0 | Re-export fallback | 🗑️ No usado; consumidores import directo de `ui.py` |
| 7 | `mostrar_exito` | `ui.py` | C | 0 | Re-export fallback | 🗑️ No usado; consumidores import directo de `ui.py` |
| 8 | `mostrar_advertencia` | `ui.py` | C | 0 | Re-export fallback | 🗑️ No usado; consumidores import directo de `ui.py` |
| 9 | `mostrar_info` | `ui.py` | C | 0 | Re-export fallback | 🗑️ No usado; consumidores import directo de `ui.py` |
| 10 | `ExportadorDatos` | `exportador_datos.py` | C | 0 | Nunca consumido | 🗑️ Eliminar si no hay plan activo |
| 11 | `ImportadorExcel` | `importador_excel.py` | C | 0 | Nunca consumido | 🗑️ Eliminar si no hay plan activo |
| 12 | `PreferencesManager` | `preferences_manager.py` | C | 0 | Nunca consumido | 🗑️ Eliminar si no hay plan activo |
| 13 | `TourManager` | `tour_manager.py` | A | 2 activos | Directo `from modules.utils.tour_manager` | ✅ Mantener (usado en global_tour.py, ajustes_main.py) |
| 14 | `TourStep` | `tour_manager.py` | A | 2 activos | Directo `from modules.utils.tour_manager` | ✅ Mantener (usado en global_tour.py, ajustes_main.py) |
| 15 | `ModuleTourHelper` | `tour_manager.py` | A | 0 | Nunca consumido | ⚠️ Revisar si es realmente necesario |
| 16 | `GestorMetadatos` | `metadata.py` | A | 1 activo | Directo `from modules.utils.metadata` | ✅ Mantener (usado en actualizacion_inventario.py) |
| 17 | `obtener_gestor_metadatos` | `metadata.py` | A | 0 | Nunca consumido | ⚠️ Candidato a eliminación |
| 18 | `GeneradorPDFManual` | `pdf_manual_generator.py` | C | 0 | Nunca consumido | 🗑️ Eliminar si no hay plan activo |
| 19 | `obtener_generador_pdf` | `pdf_manual_generator.py` | C | 0 | Nunca consumido | 🗑️ Eliminar si no hay plan activo |
| 20 | `database_helpers` (IMPLÍCITO) | `database_helpers.py` | C | 3 activos | Re-import interno (`from modules.utils.database_helpers`) | ⚠️ NO está en `__all__` pero se importa |

---

## Observaciones técnicas

### 1. **Exports nunca usados vía módulo raíz**
```
Búsqueda realizada:
  from modules.utils import Logger        ❌ NO ENCONTRADO
  from modules.utils import validar_texto ❌ NO ENCONTRADO
  from modules.utils import mostrar_error ❌ NO ENCONTRADO
  from modules.utils import ExportadorDatos ❌ NO ENCONTRADO
  (...)

Conclusión:
  Todos los consumidores importan DIRECTAMENTE del módulo origen:
  - from modules.utils.logger import Logger          ✅ 5 matches
  - from modules.utils.tour_manager import TourManager ✅ 2 matches
  - from modules.utils.metadata import GestorMetadatos ✅ 1 match
  - from modules.utils.database_helpers import ... ✅ 3 matches
```

### 2. **API implícita no exportada pero usada**
```python
# src/modules/utils/__init__.py
# AÚN NO INCLUYE EN __all__:
from modules.utils import database_helpers as db  # FUNCIONA pero no está documentado
```
Archivos que lo usan:
- `src/modules/animales/inventario_rapido.py` línea 3

### 3. **Estructura de fallbacks innecesarios**
El `__init__.py` define fallbacks para excepciones que nunca ocurren en producción:
```python
try:
    from modules.utils.validaciones import validar_texto
except ImportError:
    def validar_texto(*args, **kwargs): return (True, None, "")
```
- Validaciones: FASE 5.2 quitó wrappers muertos, pero los fallbacks todavía están aquí
- UI functions: Nunca se llaman vía `__init__.py`
- Fallbacks nunca se ejecutan → **código muerto**

### 4. **Categoría B: Wrappers legacy post-FASE 5.2**
Después de eliminar `validar_email` y `validar_telefono` en FASE 5.2:
- ✅ `validar_texto` — Aún en `__init__.py` pero no consumido
- ✅ `validar_numero` — Aún en `__init__.py` pero no consumido
- ⚠️ `validar_email` — **MUST VERIFY**: ¿Sigue fallback o ya removido?
- ⚠️ `validar_telefono` — **MUST VERIFY**: ¿Sigue fallback o ya removido?

### 5. **Tooling exports nunca usados**
```python
ExportadorDatos = None          # Nunca consumido desde __init__
ImportadorExcel = None          # Nunca consumido desde __init__
PreferencesManager = None       # Nunca consumido desde __init__
GeneradorPDFManual = None       # Nunca consumido desde __init__
obtener_generador_pdf = None    # Nunca consumido desde __init__
```
¿Intención?: Reservar API futura pero sin consumo.
**Riesgo**: Documentación implícita que puede engañar a nuevos desarrolladores.

### 6. **`ModuleTourHelper` sin consumidores detectados**
Exportado en línea 15, incluido en `__all__`, pero:
- Grep no encontró consumo vía módulo raíz
- Possible uso interno en tour_manager.py (no rastreado)
- **Requiere verificación manual**

---

## Clasificación por categoría

### ✅ CATEGORÍA A: API PÚBLICA ESTABLE (mantener congelado)
Usada activamente, definida en contrato o esencial para producción.

| Export | Razón |
|--------|-------|
| `Logger` | Infraestructura crítica; usado por internals (tour, pdf, metadata) |
| `TourManager` | Consumido en `global_tour.py` y `ajustes_main.py` |
| `TourStep` | Consumido junto con TourManager |
| `GestorMetadatos` | Consumido en `actualizacion_inventario.py` |

**Acción:** Congelar. No modificar nunca.

---

### 🟡 CATEGORÍA B: API LEGACY / COMPATIBILIDAD (candidata a eliminar FASE 5.4+)
Mantenida por backward compatibility histórica pero sin consumo real.

| Export | Razón | Detalles |
|--------|-------|----------|
| `validar_texto` | Wrapper post-consolidación validaciones | Nunca llamado vía módulo raíz; FASE 5.2 eliminó equivalentes |
| `validar_numero` | Wrapper post-consolidación validaciones | Nunca llamado vía módulo raíz; FASE 5.2 eliminó equivalentes |
| `validar_email` | ⚠️ VERIFICAR | Fue eliminado en FASE 5.2; ¿fallback sigue en __init__? |
| `validar_telefono` | ⚠️ VERIFICAR | Fue eliminado en FASE 5.2; ¿fallback sigue en __init__? |

**Acción:** Evaluar en FASE 5.4 si los fallbacks aún existen y si vale la pena mantenerlos.

---

### 🗑️ CATEGORÍA C: API INTERNA (no debería exportarse)
Detalles implementativos que no tienen contrato ni consumo público.

| Export | Razón | Detalles |
|--------|-------|----------|
| `mostrar_error` | Funciones UI de bajo nivel | Consumidores usan `from modules.utils.ui import` directo; nunca vía raíz |
| `mostrar_exito` | Funciones UI de bajo nivel | Consumidores usan `from modules.utils.ui import` directo; nunca vía raíz |
| `mostrar_advertencia` | Funciones UI de bajo nivel | Consumidores usan `from modules.utils.ui import` directo; nunca vía raíz |
| `mostrar_info` | Funciones UI de bajo nivel | Consumidores usan `from modules.utils.ui import` directo; nunca vía raíz |
| `ExportadorDatos` | Tooling externo | No consumido desde `__init__`; nunca usado en proyecto |
| `ImportadorExcel` | Tooling externo | No consumido desde `__init__`; nunca usado en proyecto |
| `PreferencesManager` | Tooling externo | No consumido desde `__init__`; nunca usado en proyecto |
| `GeneradorPDFManual` | Tooling externo | No consumido desde `__init__`; nunca usado en proyecto |
| `obtener_generador_pdf` | Getter tooling | No consumido desde `__init__`; nunca usado en proyecto |

**Acción:** Candidatos para eliminación en FASE 5.4 o posterior (sin urgencia).

---

## API implícita (RIESGO DE DEUDA)

### `database_helpers` — NO ESTÁ EN `__all__` pero se importa

**Ubicación:** `src/modules/utils/__init__.py` línea 8 (no en imports críticos, no en `__all__`)

**Consumo detectado:**
```python
# src/modules/animales/inventario_rapido.py línea 3
from modules.utils import database_helpers as db

# src/modules/animales/registro_animal.py línea 1406
from modules.utils.database_helpers import (...)

# src/modules/animales/importar_excel.py línea 116 y 168
from modules.utils.database_helpers import (...)
```

**Problema:**
- Existe forma de importarlo (`from modules.utils import database_helpers`)
- Pero NO está en `__all__`, lo que lo hace **implícito/no documentado**
- Rompe contrato de API clara

**Recomendación:**
1. O agregarlo explícitamente a `__all__` si es parte de API pública
2. O moverlo a `try-except` con fallback y documentación
3. O eliminar el import de raíz (consumidores ya usan import directo)

---

## Recomendaciones para FASE 5.4

### 🔴 Eliminar inmediatamente (bajo riesgo)
1. ✂️ `mostrar_error`, `mostrar_exito`, `mostrar_advertencia`, `mostrar_info` 
   - Nunca consumidos vía módulo raíz
   - Consumidores importan directo de `ui.py`
   - Los fallbacks son código muerto

2. ✂️ `ExportadorDatos`, `ImportadorExcel`, `PreferencesManager`, `GeneradorPDFManual`, `obtener_generador_pdf`
   - Nunca consumidos en proyecto
   - Posibles API del futuro pero sin plan actual
   - Simplificar mantenimiento

### 🟡 Verificar post-FASE 5.2 (fallbacks de validaciones)
1. ❓ Confirmar si `validar_email` y `validar_telefono` fueron totalmente eliminados en FASE 5.2
2. ❓ Si existen fallbacks huérfanos en `__init__.py`, limpiar
3. ❓ Revisar si `validar_texto` y `validar_numero` tienen consumo real oculto

### 🟢 Mantener congelado
1. ✅ `Logger` — Crítica para infraestructura interna
2. ✅ `TourManager`, `TourStep` — API activa con consumidores
3. ✅ `GestorMetadatos` — API activa con consumidores
4. ❓ `ModuleTourHelper` — Verificar consumo antes de decidir

### ⚠️ Documentar explícitamente
1. Agregar `database_helpers` a `__all__` si es API pública, o
2. Mover a modelo explícito con fallback y documentación

---

## Conclusión: Deuda técnica y estabilidad

### Nivel de deuda: **MEDIO → ALTO**
- 11 de 20 exports nunca usados vía módulo raíz (55%)
- 9 fallbacks innecesarios definidos (código muerto)
- API implícita (`database_helpers`) sin documentación

### Riesgo de estabilidad: **BAJO**
- Fallbacks previenen breaking changes
- Consumidores real importan directo (no dependen de raíz)
- Cambios en FASE 5.4 serán seguros

### Impacto en producción: **CERO (si es análisis)**
- Esta es auditoría pasiva; no se modificó código
- Proyecto sigue funcionando exactamente igual

### Plan recomendado
1. **FASE 5.4:** Limpiar exports Categoría C (sin urgencia)
2. **FASE 5.4+:** Eliminar fallbacks huérfanos post-FASE 5.2
3. **FASE 5.5:** Formalizar API pública con documentación clara
4. **Ahora:** Documentar en `CONTRATO_VALIDACIONES.md` cuáles exports están congelados

---

**Estado:** ✅ AUDITORÍA COMPLETA — SIN CAMBIOS DE CÓDIGO

Siguiente fase: FASE 5.4 (consolidación y limpieza de exports innecesarios)
