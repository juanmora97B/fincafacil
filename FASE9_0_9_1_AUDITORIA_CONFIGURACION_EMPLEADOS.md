# FASE 9.0.9.1 — Auditoría Configuración · Empleados

## Archivo analizado
[src/modules/configuracion/empleados.py](src/modules/configuracion/empleados.py) — 1045 líneas

## Métricas
| Métrica | Valor |
|---------|-------|
| Líneas | 1045 |
| `get_connection()/get_db_connection()` | 7+ |
| `cursor.execute()` | 15+ queries |
| `conn.commit()` | 3+ |
| Métodos UI con SQL | 6 (cargar_fincas, guardar_empleado, cargar_empleados, editar_empleado, eliminar_empleado, importar_excel) |

## Violaciones identificadas

### 1. SQL masivo en UI (CRÍTICO)
- **cargar_fincas()** (línea ~389): SELECT fincas activas
- **guardar_empleado()** (línea ~424): INSERT + reactivación con UPDATE + lógica duplicada
- **cargar_empleados()** (línea ~560): SELECT con filtros dinámicos
- **editar_empleado()** (línea ~645): SELECT con 4 intentos de búsqueda robusta
- **eliminar_empleado()** (línea ~840): UPDATE estado a 'Inactivo'
- **importar_excel()** (línea ~900): INSERT bulk
- **Riesgo:** Lógica de negocio dispersa en UI; difícil de mantener y probar

### 2. Búsquedas robustas duplicadas
- **Líneas 645–840:** 4 intentos de búsqueda (TRIM exacto, sin ceros, case-insensitive, numérico)
- **Riesgo:** Complejidad innecesaria; código confuso
- **Solución:** Centralizar en service con método `buscar_empleado_robusto()`

### 3. Estados inconsistentes pero parcialmente correctos
- **Columna `estado_actual`:** `'Activo'`, `'Inactivo'`, `'Vacaciones'`, `'Licencia'`
- **Columna `estado`:** `'Activo'` (redundante con `estado_actual`)
- **Cargar fincas:** Filtro `'Activa' OR 'Activo'` (divergencia de nombres)
- **Riesgo:** Confusión en BD; queries frágiles
- **Solución:** Normalizar a `{Activo, Inactivo}` en service; descarta Vacaciones/Licencia (FASE 9.3+)

### 4. Soft delete parcialmente implementado ✅
- **Línea 849:** `UPDATE empleado SET estado_actual='Inactivo'` (correcto)
- **No hay DELETE físico** (BIEN)
- **Aún falta:** Normalización de estados, centralización

### 5. Validaciones básicas en UI (mejorable)
- **Obligatorios:** código, identificación, nombres, apellidos, fecha_ingreso
- **Faltantes:** Validar formato de fechas más robustamente, prevenir identificaciones duplicadas en insert, validar numéricos
- **Solución:** Delegar al service

### 6. Lógica de reactivación compleja
- **Línea ~490–520:** Si existe con estado 'Inactivo', reactivar y actualizar
- **Línea ~500:** Actualizar también `estado='Activo'` (redundancia)
- **Riesgo:** Lógica específica de dominio en UI; difícil de probar
- **Solución:** Mover a service con método `crear_o_reactivar_empleado()`

### 7. Importación Excel sin validaciones especializadas
- **Línea 900 ss:** INSERT bulk genérico
- **Falta:** Prevención de duplicados por identificación numérica, validación de fechas
- **Solución:** Delegar a `ConfiguracionService.importar_empleados_bulk()`

## Catálogo afectado
- **Tabla BD:** `empleado`
- **Campos clave:** `codigo` (PK), `numero_identificacion` (UNIQUE), `nombres`, `apellidos`, `estado_actual`, `id_finca` (FK)
- **Relaciones FK:** `id_finca` → `finca` (tabla simple, sin cascade conocida)
- **Volumen esperado:** 5–50 empleados típicos
- **Impacto cruzado:** Nómina, Ventas, Dashboard (FASE 9.2+)

## Decisión de alcance (FASE 9.0.9)

### IN SCOPE (esta semana)
- ✅ CRUD base (crear, leer, actualizar, soft delete)
- ✅ Validaciones mínimas (obligatorios, uniqueness)
- ✅ Normalización básica (strip, mayúsculas si aplica)
- ✅ Importación Excel

### OUT OF SCOPE (FASE 9.2+)
- ❌ Cálculos de nómina (salarios, deducciones)
- ❌ Reglas laborales (vacaciones, licencias, contrataciones)
- ❌ Validaciones legales (salario mínimo, jornadas)
- ❌ Integración con módulos (Ventas, Nómina, Dashboard)

## Pasos de resolución
1. ✅ Auditoría completada
2. → Extender `ConfiguracionRepository` con métodos para empleados (SQL-only)
3. → Extender `ConfiguracionService` con validaciones/normalización
4. → Migrar `empleados.py` a usar service (sin SQL)
5. → Validar Pylance + auditor + UI
6. → Documentar cierre
7. → Actualizar log maestro

## Próximos catálogos después de Empleados
- **Fincas** (complejidad media, relaciones FK, estado inconsistente)
- **Lotes, Potreros, Proveedores, Sectores, Tipo Explotación** (restantes)
- **Herramientas, Reportes** (dominios mayores, FASE 9.1)
