# 📘 FASE 8.6.2 — Contratos de Service (Diseño, sin cambios de código)

Estado: ✅ Diseño completado (0 líneas modificadas)
Ámbito: `AnimalService`, `ReproduccionService`, `SaludService`
Objetivo: Estandarizar contratos (naming, parámetros, estados, errores) para escalar a 10+ dominios sin romper compatibilidad.

---

## 🧭 Principios de Diseño

- Separación estricta: UI → Service → Repository → BD
- Backward compatibility: ningún método existente se elimina ni cambia firma
- Contratos explícitos: semánticas claras y consistentes por dominio
- Filtros por ID: preferir IDs (enteros) en filtros; evitar nombres (strings)
- Tipado estricto: `int`, `str`, `bool`, `date (YYYY-MM-DD)`; `Dict[str, Any]` solo para payloads complejos
- Validaciones en Service: la UI nunca implementa reglas de negocio
- Errores de dominio: excepciones semánticas en lugar de errores genéricos de BD
- Catálogos dinámicos: sin listas hardcoded en servicios

---

## 📑 Convenciones Oficiales

### A. Contrato de Naming

- `listar_*`: colecciones (posible paginación o límite)
- `obtener_*`: entidad única (por ID)
- `registrar_*`: creación
- `actualizar_*`: modificación parcial/total
- `marcar_*`: cambio de estado discreto (transición de estado)
- `cargar_*`: catálogos (listas de selección)
- `validar_*`: reglas de negocio explicitadas y testeables

### B. Contrato de Parámetros

- IDs: `*_id: int` (obligatorio o `Optional[int]` para filtros globales)
- Fechas: `YYYY-MM-DD` (ISO, `str` documentada)
- Booleans: `bool` (no strings)
- Nombres: evitar en filtros; usarlos solo en payloads descriptivos
- Payloads: `Dict[str, Any]` para creación/actualización con múltiples campos
- Filtros: usar `Optional` para filtros no requeridos (None = sin filtro)

---

## 🏷️ Normalización del Filtro por Finca (Contrato)

### Regla
- Todas las APIs que filtran por finca deben aceptar: `finca_id: Optional[int]`
- Nunca usar: `finca_nombre: str` ni `nombre: str` como filtro

### Convivencia con Legacy (sin romper)
- Mantener métodos actuales que usan nombre (p. ej., `cargar_animales_por_finca(nombre: str)` en Salud)
- Introducir métodos id-based en FASE 8.6.3 (p. ej., `cargar_animales_por_finca_id(finca_id: Optional[int])`)
- UI seguirá llamando métodos legacy; adapters internos del Service mapearán nombre→id sin exponer cambios a UI
- Documentar deprecación suave: preferir variantes con `_id` en nuevo desarrollo

---

## 🗂️ Estados y Catálogos (Contrato)

### Reglas
- Estados y tipos no deben ser listas hardcoded en el Service
- Fuente de verdad: catálogos (tabla dedicada) o enum lógico persistido
- El Service valida contra catálogos; la UI solo consume datos validados

### Interfaces sugeridas (no implementar aún)
- `cargar_estados_diagnostico() -> List[Dict[str, Any]]`
- `cargar_tipos_tratamiento() -> List[Dict[str, Any]]`
- `cargar_estados_servicio_reproduccion() -> List[Dict[str, Any]]`

### Beneficios
- Extensibilidad sin cambios de código
- Consistencia entre dominios
- Testeabilidad y auditoría de datos permitidos

---

## 🚦 Taxonomía de Errores de Dominio (Contrato)

### Clases (a definir en FASE 8.6.3, sin implementación ahora)
- `EntidadNoExisteError`: cuando un ID no referencia una entidad existente
- `EstadoInvalidoError`: cuando un estado enviado no está permitido
- `ViolacionIntegridadError`: cuando una operación viola integridad referencial (FK, unicidad)
- `ParametroInvalidoError`: cuando un parámetro no cumple formato/semántica esperada
- `OperacionNoPermitidaError`: cuando el estado actual bloquea la transición solicitada

### Lineamientos
- Services lanzan errores de dominio; no propagan errores genéricos de BD
- Mensajes consistentes y accionables (indican entidad, campo y causa)
- La UI captura y muestra el mensaje; no interpreta la lógica de validación

---

## 🔁 APIs Duplicadas y Servicio Compartido

### Duplicación detectada
- `cargar_fincas()` existe en 3 servicios: Animales, Reproducción, Salud

### Propuesta (sin romper dominios)
- Crear `CatalogoService` compartido con:
  - `listar_fincas_activas()`
  - `listar_animales_activos(finca_id: Optional[int])`
  - `listar_estados_*()` y `listar_tipos_*()` (según dominio)
- Los servicios de dominio delegan a `CatalogoService` en FASE 8.6.3
- Mantener métodos actuales como fachadas que internamente usan el gateway compartido

---

## 📊 Tabla AS-IS vs TO-BE (Sin ejecutar)

| Área | AS-IS | TO-BE | Compatibilidad |
|------|-------|-------|----------------|
| Filtro por finca | `finca_nombre: str` (Salud), `finca_id: int` (Reprod.), mixto (Animales) | `finca_id: Optional[int]` en todas las APIs de filtro | Mantener métodos legacy y añadir variantes `_id` |
| Naming lecturas | `listar_*` (Animales/Reprod.), `obtener_historial_*` (Salud) | Unificar en `listar_*` para colecciones; `obtener_*` para entidad | Mantener ambos; documentar preferencia |
| Estados válidos | Hardcoded en Salud (`Diagnóstico`, `Tratamiento`) | Catálogos dedicados; Service valida con datos | Añadir `cargar_estados_*()`; mantener listas hasta migrar |
| Errores | `ValueError` con mensajes variados | Excepciones de dominio con taxonomía | Mapear internamente; UI sigue mostrando mensaje |
| Delete con FK | Error genérico `SQLITE_CONSTRAINT` | Validar y lanzar `ViolacionIntegridadError` con detalle | Validación previa; no cambia firma |
| Update inexistente | Efecto silencioso | Validar existencia y lanzar `EntidadNoExisteError` | Sin cambios en firma; mejora mensajes |
| DI signature | `Optional[Repository]` (Animales/Reprod.), fijo (Salud) | Uniformar a `Optional[Repository]` | Salud añade soporte sin romper actual |

---

## 🛠️ Estrategia de Adopción Gradual (FASE 8.6.3+)

1. Añadir variantes `_id` en filtros (p. ej., `cargar_animales_por_finca_id`) manteniendo métodos existentes
2. Introducir `CatalogoService` y migrar consultas duplicadas; conservar fachadas actuales
3. Agregar loaders de estados/tipos (`cargar_estados_*`, `cargar_tipos_*`) y reemplazar listas hardcoded
4. Implementar taxonomía de errores; mapear internamente desde `ValueError` para backward compatibility
5. Uniformar `__init__(repository: Optional[Repo])` en SaludService (aceptar repo opcional); mantener actual
6. Unificar naming en nuevas APIs; mantener alias legacy y documentar deprecaciones suaves
7. Escribir pruebas unitarias para validaciones y adapters antes de tocar UI
8. Migrar por dominio (Animales → Reproducción → Salud), validando auditor y Pylance en cada paso

---

## ✅ Criterios de Éxito (de esta fase)

- 0 líneas de código modificadas (diseño únicamente)
- Contratos claros y reutilizables
- Riesgos críticos mitigados a nivel diseño
- Base sólida para refactors seguros en FASE 8.6.3+

---

## 📎 Referencias

- Auditoría previa: `docs/FASE8_6_1_AUDITORIA_CRUZADA_SERVICIOS.md`
- Servicios actuales:
  - Animales: `src/infraestructura/animales/animal_service.py`
  - Reproducción: `src/infraestructura/reproduccion/reproduccion_service.py`
  - Salud: `src/infraestructura/salud/salud_service.py`

---

Fin del documento.
