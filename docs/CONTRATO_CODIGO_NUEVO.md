# CONTRATO DE CÓDIGO NUEVO

**Proyecto:** FincaFácil v2.0 — ERP Ganadero  
**Fecha de emisión:** 18 de diciembre de 2025  
**Versión:** 1.0  
**Estado:** EN VIGOR

---

## 1. Propósito del contrato

Este documento define las reglas **obligatorias** para **TODO código nuevo** escrito a partir de esta fecha en el proyecto FincaFácil v2.0.

### Por qué existe este contrato

- 🔴 **Problema que previene:** Reintroducción accidental de legacy después de FASES 1-6
- 🔴 **Problema que previene:** Creación de nuevos wrappers, aliases o compatibilidades innecesarias
- 🔴 **Problema que previene:** Violación de contratos públicos congelados
- 🔴 **Problema que previene:** Deuda técnica nueva por falta de lineamientos claros

### Relación con contratos existentes

Este contrato **complementa** y **refuerza**:

| Documento | Relación | Autoridad |
|-----------|----------|-----------|
| `CONTRATO_VALIDACIONES.md` | Especifica APIs de validaciones a usar | FUENTE DE VERDAD |
| `CONTRATO_LEGACY.md` | Define qué es legacy y qué NO usar | NO TOCAR |
| `AUDITORIA_EXPORTS_UTILS_FASE5_3.md` | Documental sobre estado actual de exports | REFERENCIA |

**Jerarquía de autoridad:**
1. Contrato de Validaciones (APIs permitidas)
2. Contrato de Código Nuevo (cómo escribir)
3. Contrato de Legacy (qué evitar)
4. Auditorías (referencia histórica)

---

## 2. Reglas FUNDAMENTALES (NO NEGOCIABLES)

Estas reglas son de cumplimiento **obligatorio**. Violaciones son causa de rechazo en code review.

### 2.1 Validaciones

| Regla | Clasificación | Detalle |
|-------|----------------|--------|
| **DEBE usar `modules.utils.validators`** | 🔴 OBLIGATORIO | Todas las validaciones nuevas van aquí |
| **NO DEBE importar `modules.utils.validaciones`** | 🔴 PROHIBIDO | Es legacy. Usar `validators.py` en su lugar |
| **NO DEBE crear wrappers de validación** | 🔴 PROHIBIDO | Usar APIs existentes sin delegación |
| **DEBE respetar firmas congeladas** | 🔴 OBLIGATORIO | Las firmas en `CONTRATO_VALIDACIONES.md` no cambian |

**Violación típica:**
```python
# ❌ MALO
from modules.utils.validaciones import validar_email
resultado = validar_email(email)

# ✅ CORRECTO
from modules.utils.validators import validator
es_valido, mensaje = validator.validar_email(email)
```

---

### 2.2 Base de Datos

| Regla | Clasificación | Detalle |
|-------|----------------|--------|
| **DEBE usar `from database import db`** | 🟢 PERMITIDO | API moderna y estable |
| **DEBE usar `from database import get_connection`** | 🟢 PERMITIDO | Context manager moderno |
| **NO DEBE usar `from database import get_db_connection`** | 🟡 LEGACY | Solo si código existente lo requiere |
| **NO DEBE crear nuevas funciones de conexión** | 🔴 PROHIBIDO | Usar `db` o `get_connection()` |

**Violación típica:**
```python
# ❌ MALO
from database.database import get_db_connection
with get_db_connection() as conn:
    ...

# ✅ CORRECTO
from database import get_connection
with get_connection() as conn:
    ...
```

---

### 2.3 Logging

| Regla | Clasificación | Detalle |
|-------|----------------|--------|
| **DEBE usar `modules.utils.logger.Logger`** | 🟢 PERMITIDO | API oficial de logging |
| **DEBE usar `get_logger(name)` helper** | 🟢 PERMITIDO | Factory oficial |
| **NO DEBE crear instancias custom de logging** | 🔴 PROHIBIDO | Usar factory centralizada |
| **NO DEBE usar `log = logging.getLogger(__name__)`** | 🟡 LEGACY | Incompatible con arquitectura |

**Violación típica:**
```python
# ❌ MALO
import logging
logger = logging.getLogger(__name__)

# ✅ CORRECTO
from modules.utils.logger import get_logger
logger = get_logger(__name__)
```

---

### 2.4 Importaciones

| Regla | Clasificación | Detalle |
|-------|----------------|--------|
| **NO DEBE crear re-exports innecesarios** | 🔴 PROHIBIDO | Usar imports directos |
| **NO DEBE crear fallbacks sin aprobación** | 🔴 PROHIBIDO | Los fallbacks existen solo para legacy |
| **DEBE usar imports específicos** | 🟢 PERMITIDO | `from X import Y`, no `import X` vago |
| **NO DEBE crear aliases implícitos** | 🔴 PROHIBIDO | Usar nombres claros y directos |

**Violación típica:**
```python
# ❌ MALO
try:
    from new_api import funcion
except ImportError:
    from old_api import funcion  # Fallback no autorizado

# ✅ CORRECTO
from new_api import funcion  # Direct import
```

---

### 2.5 Modificación de contratos públicos

| Regla | Clasificación | Detalle |
|-------|----------------|--------|
| **NO DEBE cambiar firmas de funciones públicas** | 🔴 PROHIBIDO | Breaking changes = FASE aprobada |
| **NO DEBE eliminar parámetros de APIs públicas** | 🔴 PROHIBIDO | Deprecar primero, eliminar después |
| **NO DEBE cambiar retornos de funciones públicas** | 🔴 PROHIBIDO | Mantener compatibilidad |
| **DEBE notificar cambios en `__all__`** | 🟢 OBLIGATORIO | Si afecta exports públicos |

**Violación típica:**
```python
# ❌ MALO - Cambiar firma (breaking change)
# Antes: def validar_email(email: str) -> Tuple[bool, str]
# Ahora: def validar_email(email: str, strict: bool = True) -> bool

# ✅ CORRECTO - Crear nueva función si se necesita comportamiento diferente
def validar_email_strict(email: str) -> bool:
    ...
```

---

## 3. APIs OFICIALES PERMITIDAS

### 3.1 Validaciones

**Módulo oficial:** `modules.utils.validators`

| API | Uso permitido | Retorno | Notas |
|-----|---------------|---------|-------|
| `FincaFacilValidator` (clase) | ✅ Permitido | Instancia | Use instancia global `validator` |
| `validator` (instancia global) | ✅ RECOMENDADO | Métodos | Singleton, use directo |
| `validator.validar_email(email)` | ✅ Permitido | `(bool, str)` | Documentado en CONTRATO_VALIDACIONES |
| `validator.validar_telefono(tel)` | ✅ Permitido | `(bool, str)` | Documentado en CONTRATO_VALIDACIONES |
| `validator.validar_fecha(fecha)` | ✅ Permitido | `(bool, str)` | Documentado en CONTRATO_VALIDACIONES |
| `AnimalValidator` (clase) | ✅ Permitido | Instancia | Use `animal_validator` global |
| `animal_validator` (instancia global) | ✅ RECOMENDADO | Métodos | Singleton, use directo |

**Ejemplo CORRECTO:**
```python
from modules.utils.validators import validator, animal_validator

# Validar email
es_valido, mensaje = validator.validar_email("user@example.com")

# Validar animal
datos_animal = {"arete": "12345", ...}
es_valido, errores = animal_validator.validar_animal_completo(datos_animal)
```

---

### 3.2 Base de Datos

**Módulos oficiales:** `database` (nuevo), `database.database` (legacy)

| API | Uso permitido | Patrón | Notas |
|-----|---------------|--------|-------|
| `from database import db` | ✅ RECOMENDADO | Global instance | Instancia de DatabaseManager |
| `from database import get_connection` | ✅ PERMITIDO | Context manager | Moderno y seguro |
| `db.get_connection()` | ✅ PERMITIDO | Método instancia | Equivalente a `get_connection()` |
| `from database import DatabaseManager` | ✅ PERMITIDO | Clase | Si necesita crear manager custom |
| `from database import get_db_connection` | 🟡 LEGACY | Fallback | Solo si código existente lo requiere |

**Ejemplo CORRECTO:**
```python
from database import db, get_connection

# Opción 1: Instancia global (recomendado)
result = db.obtener_tabla("animales")

# Opción 2: Context manager
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM animal")
```

---

### 3.3 Logging

**Módulo oficial:** `modules.utils.logger`

| API | Uso permitido | Patrón | Notas |
|-----|---------------|--------|-------|
| `Logger` (clase) | ✅ PERMITIDO | Instancia | Crear instance con `Logger(name)` |
| `get_logger(name)` | ✅ RECOMENDADO | Factory | Obtener logger configurado |
| `Logger().error/info/debug/warning` | ✅ PERMITIDO | Métodos | Métodos estándar |
| `setup_logger(name)` | ✅ PERMITIDO | Helper | Inicialización custom |

**Ejemplo CORRECTO:**
```python
from modules.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Iniciando módulo animales")
logger.error("No se pudo cargar finca", exc_info=True)
logger.debug(f"Animal ID: {animal_id}")
```

---

### 3.4 UI y Helpers

**Módulo oficial:** `modules.utils.ui`

| API | Uso permitido | Nota |
|-----|---------------|------|
| `add_tooltip(widget, text)` | ✅ PERMITIDO | Helper de UI |
| `get_theme_colors()` | ✅ PERMITIDO | Retorna colores del tema |
| `style_treeview(treeview)` | ✅ PERMITIDO | Estilizar treeview |
| Componentes CustomTkinter nativos | ✅ PERMITIDO | `ctk.CTkFrame`, `ctk.CTkLabel`, etc. |

**NO PERMITIDO:**
- ❌ `from modules.utils.validaciones import Validador` (UI legacy)
- ❌ Crear componentes wrapper personalizados sin aprobación

---

## 4. Reglas de Imports

### 4.1 Formato de imports permitidos

```python
# ✅ CORRECTO - Imports específicos
from modules.utils.validators import validator, animal_validator
from modules.utils.logger import get_logger
from database import db, get_connection

# ✅ CORRECTO - Import de módulo si se usa namespace
from modules.utils import database_helpers
result = database_helpers.normalizar_texto("TEXTO")

# ❌ INCORRECTO - Import vago de módulo sin usar namespace
import modules.utils.validators  # Use validator, animal_validator en su lugar

# ❌ INCORRECTO - Star imports
from modules.utils.validators import *

# ❌ INCORRECTO - Legacy fallbacks
try:
    from new_module import X
except ImportError:
    from old_module import X  # NO permitido en código nuevo
```

---

### 4.2 Imports de módulos internos

**PERMITIDO:**
```python
# Usar importaciones internas dentro del módulo
from database import db
from modules.utils.validators import validator
from modules.utils.logger import get_logger
```

**NO PERMITIDO:**
```python
# No crear helpers que wrappean imports internos
def get_logger_wrapper():
    from modules.utils.logger import get_logger
    return get_logger(__name__)  # ❌ Innecesario
```

---

### 4.3 Estructura de imports en archivo nuevo

**Orden recomendado:**
```python
# 1. Imports estándar Python
import os
import sys
from datetime import datetime
from typing import Optional, Dict

# 2. Imports de terceros
import customtkinter as ctk

# 3. Imports de FincaFácil (internos)
from modules.utils.validators import validator
from modules.utils.logger import get_logger
from database import db, get_connection

# 4. Imports locales de módulo
from .submodulo import Helper

logger = get_logger(__name__)
```

---

## 5. Patrón de desarrollo aprobado

### 5.1 Dónde va la lógica nueva

| Tipo de lógica | Ubicación | Ejemplo |
|---|---|---|
| Validación de datos | `modules.utils.validators` | `FincaFacilValidator.validar_arete()` |
| Acceso a BD | `database/` | Consultas raw o DatabaseManager |
| Logging | `modules.utils.logger` | Get logger y log eventos |
| UI componentes | Módulo específico (`animales/`, `configuracion/`, etc.) | Frames, widgets |
| Lógica negocio | Módulo específico | Cálculos, transformaciones |
| Utilidades genéricas | `modules.utils/` | Funciones helper reutilizables |

---

### 5.2 Cómo extender funcionalidad existente

**Opción A: Extender clase existente (PREFERIDO)**
```python
# Si la clase está en modules.utils.validators

class FincaFacilValidator:
    # Métodos existentes...
    
    def validar_arete_unico(self, arete: str, animal_id: Optional[int] = None) -> Tuple[bool, str]:
        """Nuevo método que extiende sin romper API"""
        # Implementación...
```

**Opción B: Crear clase nueva especializada (SI NECESARIO)**
```python
# Si es lógica completamente nueva en modules.utils.validators

class ReporteValidator:
    """Validaciones específicas para reportes"""
    
    def validar_rango_fechas(self, fecha_ini, fecha_fin) -> Tuple[bool, str]:
        ...
```

**PROHIBIDO: Crear wrapper**
```python
# ❌ NO HACER
class MiValidador:
    def __init__(self):
        self.validator = validator  # Wrapper innecesario
    
    def validar_algo(self, value):
        return self.validator.validar_email(value)
```

---

### 5.3 Cuándo crear nuevas clases vs reutilizar

| Situación | Acción | Ejemplo |
|-----------|--------|---------|
| Lógica que reutiliza 80%+ código existente | Extender clase | `FincaFacilValidator` → agregar método |
| Lógica completamente nueva pero del mismo dominio | Crear clase nueva | `ReporteValidator` en mismo módulo |
| Lógica que combina múltiples módulos | Crear clase composición | Combina `validator` + `db` + `logger` |
| Lógica de UI que reutiliza patrones | Crear función helper | `style_treeview()` |

---

## 6. Señales de violación del contrato

Estas señales indican que el código **viola este contrato** y será rechazado en code review:

### 6.1 Red flags de validación

```python
# 🚩 RED FLAG: Usar validaciones de modules.utils.validaciones
from modules.utils.validaciones import validar_email
es_valido, msg = validar_email(email)

# 🚩 RED FLAG: Crear wrapper de validación
class MiValidador:
    def validar(self, value):
        return validator.validar_email(value)

# 🚩 RED FLAG: Modificar firma de validador público
# Antes: validator.validar_email(email) -> (bool, str)
# Ahora: validator.validar_email(email, strict=True) -> bool

# 🚩 RED FLAG: Crear nueva instancia en lugar de usar global
def procesar():
    v = FincaFacilValidator()  # ❌ Use validator (global)
    return v.validar_email(email)
```

---

### 6.2 Red flags de BD

```python
# 🚩 RED FLAG: Crear nueva función de conexión
def mi_get_connection():
    return get_db_connection()  # Wrapper innecesario

# 🚩 RED FLAG: No usar context manager
conn = get_connection()
try:
    ...
finally:
    conn.close()  # ❌ Use with statement

# 🚩 RED FLAG: Importar get_db_connection en código nuevo
from database.database import get_db_connection  # ❌ Use db
```

---

### 6.3 Red flags de imports

```python
# 🚩 RED FLAG: Star imports
from modules.utils.validators import *

# 🚩 RED FLAG: Crear aliases innecesarios
from modules.utils.validators import validator as v

# 🚩 RED FLAG: Re-exports en __init__.py nuevo
# modules/mi_modulo/__init__.py
from .helpers import helper_function  # Si no se usa, eliminar

# 🚩 RED FLAG: Fallbacks en código nuevo
try:
    from new_api import X
except ImportError:
    from old_api import X
```

---

### 6.4 Red flags de API pública

```python
# 🚩 RED FLAG: Cambiar firma de función pública
# Antes: def validar_email(email: str) -> Tuple[bool, str]
# Ahora: def validar_email(email: str, **kwargs) -> bool

# 🚩 RED FLAG: Eliminar parámetro sin deprecación
# Antes: def func(a, b, c)
# Ahora: def func(a, b)  # ❌ Breaking change

# 🚩 RED FLAG: Crear clase que hereda de API congelada sin necesidad
class MiValidador(FincaFacilValidator):
    pass  # No agrega funcionalidad
```

---

## 7. Proceso de excepción

Si el código nuevo **necesita violar este contrato**, seguir este proceso:

### 7.1 Situaciones que pueden ameritar excepción

- ✅ Integración con sistema externo que requiere API diferente
- ✅ Optimización crítica que requiere patrón diferente
- ✅ Bugfix urgente que requiere cambio temporal
- ❌ Falta de comprensión del contrato (NO es excepción)
- ❌ Preferencia personal del desarrollador (NO es excepción)

### 7.2 Proceso de aprobación

```
1. Documentar violación
   ├─ Archivo: modules/mi_modulo/nuevo_codigo.py
   ├─ Razón: "Optimización crítica requiere fallback de BD"
   ├─ Duración propuesta: 2 sprints (hasta FASE 8)
   └─ Plan de remediación: "Migrar a nueva API en FASE 8"

2. Crear issue con etiqueta: [CONTRATO-EXCEPTION]
   └─ Link a este contrato

3. Obtener aprobación de:
   ├─ Arquitecto senior
   ├─ Tech lead del módulo
   └─ Auditor de código

4. Documentar excepción en código
   ├─ # EXCEPTION: CONTRATO_CODIGO_NUEVO
   ├─ # Razón: ...
   ├─ # Autorizado por: [nombre]
   ├─ # Válido hasta: [fecha]
   └─ # Remediación: [plan]

5. Actualizar este contrato
   └─ Agregar excepción a sección de excepciones activas

6. Code review con excepción
   └─ Rechazo automático sin etiqueta [CONTRATO-EXCEPTION]
```

### 7.3 Excepciones activas

| Archivo | Violación | Autorizado | Válido hasta | Razón |
|---------|-----------|------------|--------------|-------|
| (Ninguno actualmente) | N/A | N/A | N/A | Proyecto en FASE 7.1 |

---

## 8. Estado final del contrato

### 8.1 Declaración de obligatoriedad

**Este contrato es de cumplimiento OBLIGATORIO para:**

- ✅ Todo código nuevo escrito a partir de 18/12/2025
- ✅ Todo code review después de esta fecha
- ✅ Todos los desarrolladores del proyecto
- ✅ Todos los niveles: junior, senior, arquitecto

**Este contrato NO aplica retrospectivamente a:**
- ❌ Código escrito antes de 18/12/2025
- ❌ Legacy identificado en FASES 1-6
- ❌ Código en branches que no se mergen a main

---

### 8.2 Fecha de vigencia

- **Vigencia desde:** 18 de diciembre de 2025
- **Próxima revisión:** 18 de junio de 2026 (6 meses)
- **Actualización:** Cuando hay cambios en contratos base (validaciones, legacy, etc.)

---

### 8.3 Impacto esperado

| Métrica | Antes | Después de contrato |
|---------|-------|-------------------|
| Código nuevo que viola legacy | 30-40% | < 5% |
| Re-exports innecesarios | 10+ | 0-2 |
| Wrappers de compatibilidad | 4+ | 0 |
| Imports específicos vs vagos | 60% | > 95% |
| Deuda técnica nueva | Alto | Bajo |

---

### 8.4 Validación del contrato

**El contrato se considera exitoso si:**
- ✅ Cero violaciones no autorizadas en code review
- ✅ Cero re-exports innecesarios en código nuevo
- ✅ Cero wrappers de compatibilidad nuevos
- ✅ Cero importaciones de legacy en módulos nuevos
- ✅ Todos los imports son específicos y directos

---

## 9. Referencias rápidas

### 9.1 "¿Qué validación debo usar?"

```
¿Necesito validar datos?
  ↓
Usar: from modules.utils.validators import validator
Función: validator.validar_email(), validator.validar_fecha(), etc.
Referencia: CONTRATO_VALIDACIONES.md
```

### 9.2 "¿Cómo accedo a la BD?"

```
¿Necesito conexión a BD?
  ↓
Opción 1 (recomendado): from database import db
Opción 2 (seguro): from database import get_connection
Patrón: with get_connection() as conn: ...
```

### 9.3 "¿Cómo hago logging?"

```
¿Necesito logs?
  ↓
Usar: from modules.utils.logger import get_logger
Código: logger = get_logger(__name__)
Uso: logger.info(), logger.error(), logger.debug()
```

### 9.4 "¿Puedo usar API antigua?"

```
¿Necesito usar API antigua?
  ↓
GENERALMENTE: NO. Usar API moderna equivalente.
EXCEPCIONES: Código existente que lo requiere.
NUNCA en código nuevo sin proceso de excepción.
```

---

## 10. Apéndice: Checklist pre-commit

Antes de hacer push, verificar:

- [ ] No hay `from modules.utils.validaciones import`
- [ ] No hay imports de `database.database.get_db_connection` en código NUEVO
- [ ] No hay star imports (`import *`)
- [ ] No hay wrappers no autorizados
- [ ] No hay re-exports innecesarios en `__init__.py`
- [ ] No hay cambios en firmas públicas
- [ ] Logging usa `get_logger()`
- [ ] BD usa `db` o `get_connection()`
- [ ] Validaciones usan `validator`
- [ ] No hay excepciones sin etiqueta `[CONTRATO-EXCEPTION]`

---

**FIN DEL CONTRATO**

Este documento es la fuente oficial de reglas para todo código nuevo en FincaFácil v2.0.  
En caso de ambigüedad, prevale la interpretación más restrictiva (favor de la estabilidad).

**Contacto para clarificaciones:** Arquitectura FincaFácil  
**Control de cambios:** Actualizar en cada FASE nueva que afecte contratos base
