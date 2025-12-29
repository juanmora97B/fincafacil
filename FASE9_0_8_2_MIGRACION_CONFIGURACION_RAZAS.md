# FASE 9.0.8.2 — Migración Configuración · Razas

## Contexto y bloqueador
La pantalla `razas.py` contenía 6 instancias de SQL directo en UI (INSERT, SELECT, UPDATE, DELETE hard) y estados inconsistentes (`'Activa'` vs `'Activo'`).

## Resolución aplicada
- Se extendió `ConfiguracionRepository` con métodos SQL puros para Razas: listar, obtener, existe, crear, actualizar, cambiar_estado (soft delete).
- Se extendió `ConfiguracionService` con validaciones: código/nombre obligatorios, estado permitido {Activo, Inactivo}, normalización, prevención de duplicados.
- Se refactorizó `razas.py` para:
  - Eliminar TODO SQL directo (get_connection, cursor.execute, commit, sqlite3.IntegrityError).
  - Usar ConfiguracionService exclusivamente.
  - Reemplazar DELETE hard por `cambiar_estado_raza(codigo, "Inactivo")`.
  - Mantener UX idéntica (botones, flujos, edición inline).

## Violaciones detectadas y mitigadas

| Violación | Línea (antes) | Solución |
|-----------|--------|----------|
| DELETE hard | 320 | → `cambiar_estado_raza(codigo, "Inactivo")` |
| Estados inconsistentes | 158, 172, 356 | → `'Activo'` centralizado en service |
| SQL en guardar_raza | 158–190 | → `service.crear_raza(...)` |
| SQL en cargar_razas | 203–222 | → `service.listar_razas()` |
| SQL en editar_raza | 243–298 | → `service.obtener_raza()` + `service.actualizar_raza()` |
| SQL en importar_excel | 356–370 | → `service.crear_raza()` bulk |

## Soft delete end-to-end
- Eliminación ahora usa `cambiar_estado_raza(codigo, "Inactivo")`.
- No hay DELETE físico en UI ni infraestructura.
- Estado normalizado a `'Activo'` / `'Inactivo'` en toda la BD.

## UX preservada
- Mismo formulario (Código, Nombre, Tipo Ganado, Especie, Descripción).
- Mismos botones (Guardar, Limpiar, Editar, Eliminar, Importar, Actualizar).
- Mismos flujos (crear, editar, listar, importar Excel, soft-delete).

## Validaciones ejecutadas
- **Pylance:** 0 errores en configuracion_repository.py, configuracion_service.py, razas.py.
- **Grep:** 0 matches de `get_connection|execute|commit|sqlite3` en razas.py.
- **Auditor:** exit 0 (sin violaciones nuevas).
- **Service test:** Todos los métodos (listar, obtener, existe, crear, actualizar, cambiar_estado) pasan.

## Métricas
| Métrica | Valor |
|---------|-------|
| Líneas UI (antes) | 448 |
| Líneas UI (después) | ~370 (~17% reducción, sin SQL) |
| get_connection() eliminados | 6 |
| cursor.execute() eliminados | 8 |
| conn.commit() eliminados | 4 |
| DELETE hard eliminados | 1 |

## Próximos catálogos sugeridos
- **Empleados** (similar complejidad, CRUD simple)
- **Fincas** (complejidad media, relaciones FK)
- **Lotes, Potreros, Proveedores, Sectores, Tipo Explotación** (restantes)
