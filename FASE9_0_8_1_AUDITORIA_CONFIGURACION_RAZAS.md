# FASE 9.0.8.1 — Auditoría Configuración · Razas

## Archivo analizado
[src/modules/configuracion/razas.py](src/modules/configuracion/razas.py) — 448 líneas

## Métricas
| Métrica | Valor |
|---------|-------|
| Líneas | 448 |
| `db.get_connection()` | 6 |
| `cursor.execute()` | 8 queries |
| `conn.commit()` | 4 |
| Métodos UI con SQL | 6 (guardar_raza, cargar_razas, editar_raza, eliminar_raza, importar_excel, guardar_cambios) |

## Violaciones identificadas

### 1. DELETE físico (CRÍTICO)
- **Línea 320:** `DELETE FROM raza WHERE codigo = ?`
- **Riesgo:** Inconsistencia con patrón soft delete adoptado en catálogos gobernados
- **Solución:** Reemplazar por `UPDATE raza SET estado = 'Inactivo' WHERE codigo = ?`

### 2. Estados hardcoded inconsistentes
- **Línea 158, 172, 356:** Estado `'Activa'` (con 'a')
- **Motivos/Procedencia/Diagnósticos:** Estado `'Activo'` (sin 'a')
- **Riesgo:** Divergencia en BD; queries de listado filtran por estado de forma inconsistente
- **Solución:** Normalizar a `'Activo'` / `'Inactivo'` en service

### 3. SQL directo en UI
- **guardar_raza():** INSERT + reactivación con UPDATE (línea 158–190)
- **cargar_razas():** SELECT con filtro estado (línea 203–222)
- **editar_raza():** SELECT + UPDATE (línea 243, 284–298)
- **eliminar_raza():** DELETE (línea 320)
- **importar_excel():** INSERT bulk (línea 356–370)
- **Riesgo:** Sin validaciones centralizadas; lógica duplicada; hard a mantener
- **Solución:** Migrar todo a ConfiguracionService

### 4. Validaciones inline y lógica de reactivación
- **Línea ~175:** Intenta reactivar raza inactiva con mismo código/nombre
- **Riesgo:** Lógica específica de dominio en UI; difícil de probar/reutilizar
- **Solución:** Centralizar en service

### 5. Importación Excel sin validaciones especializadas
- **Línea 356 ss:** `importar_excel()` usa genérico `parse_excel_to_dicts`
- **Riesgo:** Sin validación de duplicados previos; modo dry-run inline
- **Solución:** Delegar a `ConfiguracionService.importar_razas_bulk()`

## Catálogo afectado
- **Tabla BD:** `raza`
- **Campos:** `codigo`, `nombre`, `tipo_ganado`, `especie`, `descripcion`, `estado` (faltante o inconsistente)
- **Relaciones FK:** Ninguna conocida (catálogo simple)
- **Volumen esperado:** 20–100 registros típicos

## Pasos de resolución
1. ✅ Auditoría completada
2. → Extender `ConfiguracionRepository` con métodos para razas (SQL-only)
3. → Extender `ConfiguracionService` con validaciones/normalización
4. → Migrar `razas.py` a usar service (sin SQL)
5. → Validar Pylance + auditor + UI
6. → Documentar cierre
7. → Actualizar log maestro

## Próximos catálogos después de Razas
- Empleados (similar complejidad, sin DELETE hard conocido)
- Fincas (complejidad media, relaciones FK)
- Otros catálogos restantes (Lotes, Potreros, Proveedores, Sectores, Tipo Explotación)
