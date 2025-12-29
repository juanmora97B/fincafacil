# FRONTERAS DEL SISTEMA (BOUNDARIES & DEPENDENCY RULES)

**Proyecto:** FincaFácil v2.0 — ERP Ganadero  
**Fecha de emisión:** 18 de diciembre de 2025  
**Versión:** 1.0  
**Estado:** EN VIGOR (Fase 7.2)

---

## 1. Propósito de las fronteras

- **Por qué ahora:** Tras Fases 1–7.1 se consolidaron contratos de validaciones, legacy y código nuevo. Este documento define las **líneas de dependencia** para evitar regresiones arquitectónicas en producción.
- **Problemas que previene:** Dependencias circulares, imports transversales, acoplamiento UI↔BD↔Utils, uso accidental de legacy en código nuevo.
- **Relación con contratos existentes:**
  - Refuerza las reglas de [docs/CONTRATO_CODIGO_NUEVO.md](docs/CONTRATO_CODIGO_NUEVO.md) sobre imports permitidos.
  - Se alinea con el congelamiento descrito en [docs/CONTRATO_LEGACY.md](docs/CONTRATO_LEGACY.md) (no se abren nuevas dependencias al legacy).
  - Complementa la autoridad de [docs/CONTRATO_VALIDACIONES.md](docs/CONTRATO_VALIDACIONES.md) para mantener las validaciones en la zona correcta (Utils técnica).

---

## 2. Zonas del sistema (obligatorio)

| Zona | Descripción | Ejemplos (no exhaustivos) |
|------|-------------|---------------------------|
| **UI** | Vistas y presentación. Sin conocimiento de persistencia. | Pantallas, formularios, widgets CustomTkinter, controladores de eventos UI |
| **Dominio** | Lógica de negocio, casos de uso, reglas, validaciones de reglas. | Casos de uso de animales, inventario, cálculos de negocio |
| **Infraestructura** | Persistencia y operaciones IO. | Base de datos, repositorios, acceso a ficheros/Excel/PDF, red |
| **Utils** | Helpers técnicos compartidos y agnósticos al negocio. | Logging, validaciones técnicas (validators.py), formateos, utilidades puras |

---

## 3. Matriz de dependencias (quién puede importar a quién)

- Interpretación: Filas = zona que importa. Columnas = zona importada.
- Leyenda: ✅ Permitido, ⚠️ Permitido con condiciones estrictas, ❌ Prohibido.

| Zona que importa → | UI | Dominio | Infra | Utils |
|--------------------|----|---------|-------|-------|
| **UI** | ✅ | ✅ | ❌ | ⚠️ |
| **Dominio** | ❌ | ✅ | ⚠️ | ✅ |
| **Infra** | ❌ | ❌ | ✅ | ✅ |
| **Utils** | ❌ | ❌ | ❌ | ✅ |

**Condiciones asociadas a ⚠️:**
- UI → Utils: Solo para utilidades puras y logging oficial; prohibido usar Utils como fachada hacia BD o negocio.
- Dominio → Infra: Únicamente a través de contratos explícitos (repositorios/puertos definidos). Prohibido llamar `get_connection()` o `db` desde UI; Dominio puede usar infraestructura mediante abstracciones claras sin mezclar lógica de presentación.

---

## 4. Reglas de imports (NO negociables)

1. **UI NO DEBE importar Infraestructura directamente.**
2. **Dominio NO DEBE importar UI.**
3. **Utils NO DEBE importar Dominio ni UI ni Infraestructura.**
4. **Ningún módulo nuevo DEBE importar legacy** salvo excepciones aprobadas según [docs/CONTRATO_LEGACY.md](docs/CONTRATO_LEGACY.md).
5. **Imports deben ser directos y explícitos; NO usar re-exports para cruzar fronteras.**
6. **Validaciones técnicas DEBEN venir de `modules.utils.validators`; NO usar `modules.utils.validaciones` en código nuevo.**
7. **Acceso a BD DEBE hacerse desde Infra o mediante servicios de Dominio que delegan en Infra; UI no toca BD.**

**Ejemplos (CORRECTO vs INCORRECTO)**

```python
# ✅ CORRECTO (UI -> Dominio)
from dominio.animales.casos_uso import registrar_animal

resultado = registrar_animal(datos_formulario)
```

```python
# ❌ INCORRECTO (UI -> Infra)
from database import get_connection

with get_connection() as conn:
    conn.execute("INSERT INTO animal ...")
```

```python
# ✅ CORRECTO (Dominio -> Infra a través de puerto)
from infraestructura.repositorios import AnimalesRepository

repo = AnimalesRepository()
repo.guardar(animal)
```

```python
# ❌ INCORRECTO (Dominio -> UI)
from ui.formularios import FormularioAnimal  # Prohibido
```

```python
# ✅ CORRECTO (Uso de validaciones técnicas desde Utils)
from modules.utils.validators import validator
es_valido, msg = validator.validar_email(email)
```

```python
# ❌ INCORRECTO (Uso de legacy en código nuevo)
from modules.utils.validaciones import validar_email  # Prohibido
```

---

## 5. Casos especiales permitidos

- **Compatibilidad legacy existente:** Código previo a Fase 7.2 que ya cruza fronteras se mantiene congelado según [docs/CONTRATO_LEGACY.md](docs/CONTRATO_LEGACY.md). No se expande.
- **Integraciones puntuales de dominio con infraestructura:** Solo mediante interfaces definidas (puertos/repositorios). Requiere anotación en el PR y actualización de esta sección si se abre un nuevo puerto.
- **Scripts operativos aislados (one-off):** Deben vivir en carpeta de scripts y no contaminar módulos principales. Requieren nota de excepción en el PR y referencia a este documento.
- **Proceso si se necesita una excepción nueva:**
  1) Abrir **Fase de Excepción** documentada; 2) Actualizar [docs/CONTRATO_CODIGO_NUEVO.md](docs/CONTRATO_CODIGO_NUEVO.md) si aplica; 3) Registrar la excepción aquí con fecha y alcance; 4) Plan de reversión.

---

## 6. Señales de violación de frontera

- Imports cruzados (UI importando Infra, Dominio importando UI, Utils importando cualquier otra zona).
- Acceso directo a BD desde UI (uso de `db` o `get_connection()` en vistas/controladores).
- Uso de Utils como "god module" para esconder lógica de Dominio o Infra.
- Re-exports para acortar rutas que crucen zonas.
- Fallbacks silenciosos que mezclan APIs nuevas y legacy.
- Clases/módulos con responsabilidades mezcladas (UI + lógica de negocio + IO en un mismo archivo).

---

## 7. Gobernanza y enforcement

- **Revisión en PR:** Checklist obligatorio antes de aprobar.
- **Checklist de fronteras:**
  1) ¿Algún import cruza una frontera prohibida según la matriz? (❌ → rechazar)
  2) ¿UI toca BD o Infra directamente? (❌ → rechazar)
  3) ¿Dominio depende de UI? (❌ → rechazar)
  4) ¿Utils importa otra zona? (❌ → rechazar)
  5) ¿Se usa legacy en código nuevo? (❌ → rechazar salvo excepción aprobada)
  6) ¿Se agregaron re-exports para evitar rutas largas? (❌ → rechazar)
  7) ¿Las validaciones técnicas vienen de `modules.utils.validators`? (✅ requerido)
  8) ¿El acceso a BD está encapsulado en Infra/repositorios? (✅ requerido)
- **Pre-commit:** Si se añade tooling, debe verificar la matriz (búsqueda de patrones de import prohibidos) y rechazar commits con violaciones.
- **Trazabilidad:** Cualquier excepción debe quedar registrada en este documento y referenciada en el PR.

---

## 8. Estado final y vigencia

- Este documento es **obligatorio** para todo el equipo a partir del **18/12/2025**.
- No introduce cambios de código; define solo reglas de dependencia.
- Impacto esperado: Reducir acoplamiento, prevenir regresiones, facilitar escalabilidad y onboarding.
- Cualquier cambio a estas fronteras requiere una fase formal y actualización de este documento.

---

**Declaración formal:** Las fronteras aquí descritas son vinculantes y complementan los contratos previos. El incumplimiento es causa de rechazo en revisión de código y deberá ser corregido antes de merge.
