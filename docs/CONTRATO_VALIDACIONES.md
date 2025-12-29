# CONTRATO DE VALIDACIONES - FincaFácil v2.0

**Fecha:** 17 de Diciembre de 2025  
**Proyecto:** FincaFácil v2.0  
**Versión:** 1.0  
**Status:** Congelado hasta FASE 5

---

## 📋 FUENTE DE VERDAD OFICIAL

**Módulo único de verdad:** `modules.utils.validators`

Todas las validaciones de negocio se definen en:
- `src/modules/utils/validators.py`

**Responsabilidades:**
- Validaciones con acceso a BD
- Validaciones de dominio (animales, fincas)
- Instancias globales singleton (`validator`, `animal_validator`)

---

## 🔐 CONTRATO DE FIRMAS

### Clase: `FincaFacilValidator` (fuente oficial)

#### Método: `validar_email(email: str) -> Tuple[bool, str]`

**Entrada:**
- `email` (str): Dirección de correo a validar

**Salida:**
- `Tuple[bool, str]`: (es_válido, mensaje_error_o_éxito)

**Comportamiento:**
- Email vacío: retorna `(True, "Email opcional")`
- Email inválido: retorna `(False, "Formato de email inválido")`
- Email válido: retorna `(True, "Email válido")`

**Patrón:** `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

---

#### Método: `validar_telefono(telefono: str) -> Tuple[bool, str]`

**Entrada:**
- `telefono` (str): Número de teléfono a validar

**Salida:**
- `Tuple[bool, str]`: (es_válido, mensaje_error_o_éxito)

**Comportamiento:**
- Teléfono vacío: retorna `(True, "Teléfono opcional")`
- Teléfono inválido: retorna `(False, "Formato de teléfono inválido")`
- Teléfono válido: retorna `(True, "Teléfono válido")`

**Patrón:** `^[\d\s\+\-\(\)]{7,15}$`

---

#### Método: `validar_fecha(fecha_str: str, fecha_min: str = None, fecha_max: str = None) -> Tuple[bool, str]`

**Entrada:**
- `fecha_str` (str): Fecha en formato YYYY-MM-DD
- `fecha_min` (str, optional): Fecha mínima permitida
- `fecha_max` (str, optional): Fecha máxima permitida

**Salida:**
- `Tuple[bool, str]`: (es_válido, mensaje_error_o_éxito)

**Comportamiento:**
- Fecha vacía: retorna `(True, "Fecha opcional")`
- Formato inválido: retorna `(False, "Formato de fecha inválido. Use YYYY-MM-DD")`
- Fecha futura: retorna `(False, "La fecha no puede ser futura")`
- Fecha válida: retorna `(True, "Fecha válida")`

**Formato:** `%Y-%m-%d`

---

#### Método: `validar_peso(peso, tipo: str = "cualquiera") -> Tuple[bool, str]`

**Entrada:**
- `peso` (float): Peso en kg
- `tipo` (str): "ternero" | "adulto" | "cualquiera"

**Salida:**
- `Tuple[bool, str]`: (es_válido, mensaje_error_o_éxito)

**Rangos:**
- ternero: 10-200 kg
- adulto: 200-1500 kg
- cualquiera: 1-2000 kg

---

#### Método: `validar_arete(arete: str, animal_id: int = None) -> Tuple[bool, str]`

**Entrada:**
- `arete` (str): Código de arete
- `animal_id` (int, optional): ID del animal (para actualizaciones)

**Salida:**
- `Tuple[bool, str]`: (es_válido, mensaje_error_o_éxito)

**Comportamiento:**
- Valida unicidad en BD
- Excluye animal_id en actualizaciones
- Acceso a BD: `get_db_connection()`

---

#### Método: `validar_codigo_unico(codigo: str, tabla: str, campo: str = 'codigo', registro_id: int = None) -> Tuple[bool, str]`

**Entrada:**
- `codigo` (str): Código a validar
- `tabla` (str): Nombre de tabla BD
- `campo` (str): Nombre del campo
- `registro_id` (int, optional): ID para excluir en actualización

**Salida:**
- `Tuple[bool, str]`: (es_válido, mensaje_error_o_éxito)

**Comportamiento:**
- Valida unicidad en tabla específica
- Acceso a BD requerido

---

#### Método: `validar_valor_monetario(valor: float, minimo: float = 0, maximo: float = 100000000) -> Tuple[bool, str]`

**Entrada:**
- `valor` (float): Cantidad a validar
- `minimo` (float): Mínimo permitido
- `maximo` (float): Máximo permitido

**Salida:**
- `Tuple[bool, str]`: (es_válido, mensaje_error_o_éxito)

---

### Clase: `Validador` (en `validaciones.py` - WRAPPER)

#### Método: `validar_email(valor: str, nombre_campo: str = "Email", permitir_vacio: bool = False) -> Tuple[bool, str, str]`

**Entrada:**
- `valor` (str): Email a validar
- `nombre_campo` (str): Nombre del campo para mensajes
- `permitir_vacio` (bool): Si se permite vacío

**Salida:**
- `Tuple[bool, str, str]`: (es_válido, valor_limpio, mensaje_error)

**DEPRECATED:** Wrapper a `validators.FincaFacilValidator.validar_email`

**Comportamiento:**
- Si `permitir_vacio=True` y vacío: retorna `(True, "", "")`
- Delegua a `validators.validator.validar_email()` si disponible
- Fallback: validación local con mismo patrón

---

#### Método: `validar_telefono(valor: str, nombre_campo: str = "Teléfono", permitir_vacio: bool = False) -> Tuple[bool, str, str]`

**DEPRECATED:** Wrapper a `validators.FincaFacilValidator.validar_telefono`

**Salida:** `Tuple[bool, str, str]`: (es_válido, valor_limpio, mensaje_error)

---

### Instancias Globales

```python
validator = FincaFacilValidator()              # Instancia singleton
animal_validator = AnimalValidator()           # Especialización para animales
```

**Uso correcto:**
```python
from modules.utils.validators import validator, animal_validator

es_valido, mensaje = validator.validar_email("test@example.com")
es_valido, errores = animal_validator.validar_animal_completo(datos)
```

---

## 🛑 CONVENCIÓN DE ERRORES

### Formato estándar de retorno

**Validaciones sin BD (genéricas):**
```python
Tuple[bool, str]
(es_valido, mensaje)
# (True, "Descripción de éxito")
# (False, "Error: descripción específica")
```

**Validaciones con contexto (nombre_campo):**
```python
Tuple[bool, str, str]
(es_valido, valor_limpio_u_vacío, mensaje_error)
# (True, "valor_limpio", "")
# (False, "", "nombre_campo no puede estar vacío")
```

### Codes de error implícitos (NO cambiar)

| Situación | Mensaje |
|-----------|---------|
| Campo vacío sin permiso | `"{nombre_campo} no puede estar vacío"` |
| Formato inválido | `"{nombre_campo} no tiene un formato válido"` |
| Rango excedido | `"{nombre_campo} debe estar entre X y Y"` |
| Valor no único | `"El código '{codigo}' ya existe en {tabla}"` |
| BD no disponible | `"(modo prueba - ...)"` |

---

## 🔄 REGLA: `permitir_vacio`

**Aplicable solo en:**
- `Validador.validar_email(..., permitir_vacio=True)`
- `Validador.validar_telefono(..., permitir_vacio=True)`
- `Validador.validar_numerico(..., permitir_vacio=True)`
- Otros métodos de `Validador`

**Comportamiento:**
- `permitir_vacio=True` + campo_vacío → retorna `(True, "", "")`
- `permitir_vacio=False` + campo_vacío → retorna `(False, "", "mensaje")`

**NO aplicable en:**
- `FincaFacilValidator` (métodos estáticos)
- `validator` instance (singleton)

---

## 📍 LISTA DE FUNCIONES DEPRECATED

| Función | Ubicación | Motivo | Reemplazo |
|---------|-----------|--------|-----------|
| `validar_email()` | `validaciones.Validador` | Duplicada en `validators` | `validator.validar_email()` |
| `validar_telefono()` | `validaciones.Validador` | Duplicada en `validators` | `validator.validar_telefono()` |
| `validar_email(email)` | `validaciones` módulo-level | Wrapper legacy | `Validador.validar_email(email)` |
| `validar_telefono(tel)` | `validaciones` módulo-level | Wrapper legacy | `Validador.validar_telefono(tel)` |

**Estado:** Funcionales pero marcadas con `# DEPRECATED` en código. No serán eliminadas hasta FASE 5+.

---

## 🔒 APIs CONGELADAS HASTA FASE 5

### Congelado (prohibido modificar hasta FASE 5)

- ✅ Firma completa de `FincaFacilValidator` (todos los métodos)
- ✅ Firma completa de `AnimalValidator`
- ✅ Instancias globales: `validator`, `animal_validator`
- ✅ Tipo de retorno `Tuple[bool, str]` en validators
- ✅ Tipo de retorno `Tuple[bool, str, str]` en validaciones.Validador
- ✅ `ValidadorFormulario` (UI, intacto)
- ✅ `EntryValidado` (widget, intacto)
- ✅ Parámetro `permitir_vacio` en Validador
- ✅ Patrones regex (email, teléfono, etc.)

### Permitido modificar AHORA (FASE 4)

- ✓ Agregar comentarios explicativos (no ejecutables)
- ✓ Agregar documentación interna
- ✓ Crear wrappers siguiendo contrato
- ✓ Actualizar esta documentación

### Prohibido SIEMPRE

- ❌ Cambiar firmas de métodos
- ❌ Cambiar tipos de retorno
- ❌ Mover funciones entre archivos
- ❌ Cambiar lógica de validación
- ❌ Eliminar funciones DEPRECATED sin aviso FASE 5
- ❌ Tocar `__init__.py` (re-exports)

---

## 📌 MIGRACIÓN RECOMENDADA (INFO SOLO)

**De (`validaciones.Validador`):**
```python
es_valido, email, error = Validador.validar_email("test@example.com", permitir_vacio=True)
```

**A (`validators.FincaFacilValidator`):**
```python
es_valido, mensaje = validator.validar_email("test@example.com")
```

**Nota:** Cambio de firma - requiere ajuste en consumidor. Propuesto para FASE 5.

---

## 🧪 PRINCIPIOS DE TESTING

**No tocar en FASE 4, documentado para FASE 5:**

1. Toda validación debe retornar tupla sin excepciones
2. `permitir_vacio=True` nunca debe fallar si campo vacío
3. Errores de BD no deben exponer detalles internos
4. Mensajes deben ser amigables al usuario
5. Fallback sin BD debe funcionar en modo prueba

---

## 📚 REFERENCIAS

- **Fuente oficial:** `src/modules/utils/validators.py`
- **Wrappers:** `src/modules/utils/validaciones.py`
- **Auditoría:** AUDITORIA_VALIDACIONES_FASE1.md
- **Plan:** PROPUESTA_FASE2_CONSOLIDACION_VALIDADORES.md

---

## ✅ CHANGELOG FASE 4

- [x] Documento de contrato creado (CONTRATO_VALIDACIONES.md)
- [x] Fuente de verdad clarificada (validators.py)
- [x] Firmas congeladas documentadas
- [x] APIs permitidas vs prohibidas explicitadas
- [x] DEPRECATED list creada
- [x] Reglas de `permitir_vacio` documentadas

---

**CONTRATO VIGENTE** 🔐

Próximo cambio permitido: FASE 5 (después de revisión y aprobación)
