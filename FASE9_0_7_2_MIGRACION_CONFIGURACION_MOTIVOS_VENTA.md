# FASE 9.0.7.2 — Migración Configuración · Motivos de Venta

## Contexto y bloqueador
- La pantalla `motivos_venta.py` ya usaba `ConfiguracionService` para CRUD, importación y soft delete, pero el service/repository no tenían métodos, causando `AttributeError` al iniciar.

## Resolución aplicada
- Se extendió `ConfiguracionRepository` con operaciones SQL puras para Motivos de Venta (listar con estado, obtener, existe, crear, actualizar, cambiar_estado) sin DELETE físico.
- Se extendió `ConfiguracionService` con validaciones de negocio: código/descr obligatorios, estado permitido {Activo, Inactivo}, normalización de strings, reutilización de `existe_motivo_venta` para duplicados, soft delete centralizado.

## Soft delete end-to-end
- La UI sigue invocando `cambiar_estado_motivo_venta(codigo, "Inactivo")` y ahora el service/repository lo soportan; no hay DELETE en UI ni infraestructura.

## UX y flujos
- Sin cambios de UX ni botones; se mantuvo el flujo actual (crear, editar, listar, importar, eliminar lógico).

## Validaciones ejecutadas
- Grep en UI `motivos_venta.py` → 0 apariciones de `get_connection|execute|commit|sqlite3` (sin SQL en UI).
- Pylance/auditor: no ejecutados en esta iteración (pendiente si se requiere pass final).

## Próximos pasos sugeridos
- Ejecutar la pantalla para confirmar carga sin `AttributeError` y probar CRUD/importación.
- Correr Pylance y auditor fronteras para el pase final del dominio.
