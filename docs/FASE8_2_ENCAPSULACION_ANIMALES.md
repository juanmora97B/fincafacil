# FASE 8.2 — ENCAPSULACIÓN INICIAL DEL DOMINIO ANIMALES

**Proyecto:** FincaFácil v2.0 — ERP Ganadero  
**Fecha:** 18 de diciembre de 2025  
**Alcance:** Encapsulación inicial (Infra + Dominio) sin tocar UI ni flujos visibles  
**Compatibilidad:** 100% backward-compatible (service.py mantiene API pública)

---

## Resumen ejecutivo
- Se creó una **capa explícita de Infra/Dominio** para Animales: `infraestructura/animales/` con `AnimalRepository` (SQL) y `AnimalService` (orquestación).  
- `modules/animales/service.py` se marcó legacy/frozen y **delegó internamente** al nuevo servicio, manteniendo firmas y comportamiento.  
- No se migró UI ni se alteraron flujos visibles; todo queda listo para migración gradual.  
- Auditoría de fronteras ejecutada post-cambio (sin errores de ejecución). Las violaciones UI→BD permanecen hasta migrar UI en fases futuras.

---

## ¿Qué se encapsuló?
- **Nuevo repositorio:** `infraestructura/animales/animal_repository.py`
  - SQL crudo concentrado (`crear`, `actualizar`, `eliminar`, `obtener_por_codigo`, `listar`, `registrar_peso`, `registrar_movimiento`).
  - Usa `ejecutar_consulta` legacy para preservar formato de resultados.
- **Nuevo servicio de dominio:** `infraestructura/animales/animal_service.py`
  - Lógica ligera y validaciones mínimas (código obligatorio, sexo válido, unicidad de código) + delegación al repositorio.
- **Integración legacy:** `modules/animales/service.py` mantiene sus funciones públicas y ahora delega a `AnimalService` singleton.

## ¿Qué NO se tocó?
- Ningún archivo UI (formularios, modales, inventarios).  
- Ningún import o flujo visible.  
- Legacy existente (`service.py` público) sigue disponible y sin cambio de firma.  
- Validadores y contratos previos (`CONTRATO_VALIDACIONES.md`, `CONTRATO_LEGACY.md`) permanecen intactos.

---

## Diagrama simple (texto)
**Antes**  
UI (registro, modales, inventarios) → `modules/animales/service.py` → SQL directo (`ejecutar_consulta`, `get_db_connection`).

**Después**  
UI (sin cambios) → `modules/animales/service.py` (legacy/frozen) → `AnimalService` (dominio) → `AnimalRepository` (SQL) → BD.

---

## APIs nuevas creadas
- `infraestructura.animales.AnimalRepository`
  - `crear(data)`
  - `actualizar(animal_id, cambios)`
  - `eliminar(animal_id)`
  - `obtener_por_codigo(codigo)`
  - `existe_codigo(codigo)`
  - `listar(filtros=None)`
  - `registrar_peso(animal_id, fecha, peso, metodo=None, observaciones=None)`
  - `registrar_movimiento(animal_id, lote_destino_id, fecha_movimiento, tipo_movimiento='Traslado', lote_origen_id=None, motivo=None, observaciones=None)`
- `infraestructura.animales.AnimalService`
  - `registrar_animal(data)`
  - `actualizar_animal(animal_id, cambios)`
  - `eliminar_animal(animal_id)`
  - `obtener_animal_por_codigo(codigo)`
  - `listar_animales(filtros=None)`
  - `registrar_peso(...)`
  - `registrar_movimiento(...)`

## APIs legacy congeladas
- `modules.animales.service` (funciones públicas): `crear_animal`, `actualizar_animal`, `eliminar_animal`, `obtener_animal_por_codigo`, `listar_animales`, `registrar_peso`, `registrar_movimiento`.  
- Comportamiento y firmas **sin cambios**; ahora delegan a la nueva capa.

---

## Riesgos mitigados
- Se evita que nuevo código UI consuma directamente `database` para operaciones de Animales; punto único de acceso ahora es `AnimalService`/`AnimalRepository` vía `service.py`.
- SQL queda concentrado en una sola unidad (repositorio), facilitando futuras migraciones y testing.
- Validaciones mínimas centralizadas (código obligatorio, sexo, unicidad) viven en el servicio.

## Riesgos pendientes
- UI sigue acoplada a BD hasta que se migren importaciones a la nueva capa (futuras fases).  
- `ejecutar_consulta` legacy sigue siendo el ejecutor para mantener compatibilidad; se podrá sustituir cuando se migre Infra completa.

---

## Declaración de compatibilidad
- No se modificaron firmas públicas ni flujos visibles.  
- `service.py` sigue operativo y funciona como fachada legacy.  
- Código UI existente no requiere cambios para seguir funcionando.

## Próximos pasos sugeridos (FASE 8.3+)
1. Migrar UI crítica (registro, reubicación, ficha) para consumir `AnimalService`/`AnimalRepository` vía una API estable (puerto/adaptador) sin tocar comportamientos.
2. Sustituir usos directos de `get_db_connection` en UI por métodos del servicio/repositorio (lote por lote).
3. Considerar extraer un gateway de lectura para inventarios/reportes basado en el repositorio, eliminando PRAGMA ad-hoc en UI.
4. Evaluar reemplazo de `ejecutar_consulta` por `get_connection()` en repositorio cuando compatibilidad esté asegurada.

---

**Declaración final:** FASE 8.2 crea el primer eje estable del dominio Animales. No se modificó comportamiento, solo se introdujo una capa formal que encapsula acceso a datos y prepara migraciones seguras.
