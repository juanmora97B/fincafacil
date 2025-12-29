# FASE 9.0.5 — Auditoría Pasiva: Configuración · Diagnósticos

Estado: Completada
Fecha: 2025-12-19
Archivo auditado: src/modules/configuracion/diagnosticos.py

---

## Resumen
- get_connection/get_db_connection: 4
- cursor.execute: 6
  - INSERT (guardar_diagnostico)
  - SELECT activos (cargar_diagnosticos)
  - UPDATE estado → 'Inactivo' (eliminar_diagnostico)
  - SELECT COUNT + INSERT por fila (importar_excel)
- conn.commit: 3
  - guardar_diagnostico, eliminar_diagnostico, importar_excel
- Estados hardcoded: "Activo"/"Inactivo"
- Tipos: Combo con valores ["Reproductivo", "No Reproductivo"]
- Validaciones en UI: campos obligatorios (código, descripción); duplicados en import (SELECT COUNT)

## Flujos CRUD mapeados
- Listado: SELECT codigo, descripcion, tipo_diagnostico, comentario FROM diagnostico_veterinario WHERE estado='Activo'
- Alta: INSERT INTO diagnostico_veterinario (..., estado='Activo')
- Edición: Placeholder (mensaje "Funcionalidad en desarrollo")
- Eliminación (soft): UPDATE diagnostico_veterinario SET estado='Inactivo' WHERE codigo=?
- Importación: parse Excel → por fila valida/duplica → INSERT

## Observaciones
- SQL directo en 4 métodos de UI; patrón idéntico a otros catálogos ya gobernados.
- Se reutilizará infraestructura ConfiguracionRepository + ConfiguracionService.
- La edición quedará preparada en infraestructura (service/repo) manteniendo la UI intacta para backward compatibility.

## Decisión
- Migrar a Service/Repository manteniendo UX y mensajes.
- Eliminar todo acceso a BD desde UI.
