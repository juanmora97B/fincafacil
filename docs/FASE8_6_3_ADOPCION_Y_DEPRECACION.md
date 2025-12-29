# 📘 FASE 8.6.3 — Plan de Adopción y Deprecación (Scaffold)

Estado: Diseño listo (sin cambios de código)
Objetivo: Adoptar contratos normalizados sin romper compatibilidad y con
rollback seguro. No toca UI ni Services actuales en esta fase.

---

## Fases y Hitos

### 8.6.3 — Habilitación (no breaking)
- Añadir variantes por ID en Services (p. ej., `*_por_finca_id`) sin eliminar legacy
- Introducir `CatalogosGateway` y delegar desde Services de forma gradual
- Añadir loaders de estados/tipos (`cargar_estados_*`, `cargar_tipos_*`)
- Mantener `ValueError`; preparar mapeo a errores tipados sin cambiar mensajes

### 8.7.x — Adopción progresiva
- UI consume variantes `_id` y catálogos desde gateway
- Services comienzan a lanzar errores de dominio; UI captura y muestra igual
- Deprecation warnings en aliases legacy (logger/telemetría)

### 9.x — Consolidación
- Eliminar aliases legacy no usados (con cobertura ≥ 95% migrada)
- Unificar proveedores reales del gateway (única fuente de catálogos)
- Sustituir listas hardcoded por catálogos persistidos

---

## Criterios de Deprecación Segura
- Métricas de uso (telemetría/logs) muestran < 5% de llamadas legacy
- UI migrada y probada con variantes `_id`
- Auditor y Pylance en verde
- Pruebas unitarias para validaciones y errores tipados

---

## Convivencia Legacy → Contrato (Ejemplos)

| Dominio | Legacy | Contrato Oficial | Estado |
|---------|--------|------------------|--------|
| Salud | `cargar_animales_por_finca(nombre)` | `cargar_animales_por_finca_id(finca_id)` | Pendiente 8.6.3 |
| Reprod. | `cargar_hembras(nombre)` | `cargar_hembras(finca_id)` | Alias por nombre (adapter) |
| Animales | `cargar_potreros_por_finca(nombre)` | `cargar_potreros_por_finca_id(finca_id)` | Alias + variante `_id` |

---

## Rollout Recomendado
1. Activar adapters en puntos controlados (sin cambiar UI masivamente)
2. Introducir variantes `_id` y mantener legacy en paralelo
3. Validar con datos reales (checklists por dominio)
4. Monitorear errores y uso de aliases
5. Planificar remoción en 9.x con ventanas de cambio y comunicación

---

## Referencias
- `docs/FASE8_6_2_CONTRATOS_DE_SERVICE.md`
- `src/dominio/contratos/` (service_contracts.py, errores_dominio.md)
- `src/dominio/adapters/` (legacy adapters)
- `src/dominio/gateways/` (catalogos_gateway.py)

---

Fin del plan.
