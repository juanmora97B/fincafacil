# FASE 9.0 — Gobernanza Progresiva: Quick Wins
## Log de Ejecución — 5 Dominios de Bajo Riesgo

**Objetivo:** Migrar 5 dominios de bajo riesgo a gobernanza total (Repository+Service) en 4 semanas.
**Estrategia:** Auditoría pasiva → Encapsulación → UI refactoring → Validación → Documentación (1 dominio/semana).

---

## 1. AUDITORÍA PASIVA — 5 Quick-Win Domains

### Dominio: POTREROS
**Archivo principal:** `src/modules/potreros/potreros_main.py` (496 líneas)

#### Violaciones Identificadas:
- **get_connection() directo:** 2 instancias (líneas 200, 225)
- **cursor.execute():** 5 queries
  - Línea 202: `SELECT nombre FROM finca WHERE estado = 'Activo'` (cargar_fincas)
  - Línea 245: Query dinámica con filtro finca (cargar_potreros con "Todas las fincas")
  - Línea 263: Query con parámetro finca_filtro_actual
  - Línea 271: Subquery COUNT animales por potrero
- **Validaciones inline:** Estado = 'Activo' hardcoded en línea 202
- **Filtro por nombre:** Usa `WHERE nombre = ?` en lugar de ID (divergencia con contratos)
- **cursor.fetchall/fetchone():** 4 referencias
- **Métodos afectados:** `cargar_fincas()`, `cargar_potreros()`, `aplicar_filtro_finca()`, `actualizar_metricas()`

#### Complejidad:
- 🟢 **Bajo:** Solo reads, sin UPDATE/DELETE, sin transacciones complejas
- Métodos simples: ~8 operaciones SQL directas
- Riesgo de regresión: Mínimo (UI pura para visualización)

#### Patrón detectado:
```python
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT ... WHERE estado = 'Activo'")  # Hardcoded state
    for row in cursor.fetchall():
        # Procesar datos
```

---

### Dominio: AJUSTES
**Archivo principal:** `src/modules/ajustes/ajustes_main.py` (731 líneas)

#### Violaciones Identificadas:
- **get_db_connection():** 3 instancias (líneas 240, 337, 348)
- **cursor.execute():** 3 queries
  - Línea 241: `SELECT id, nombre FROM finca ORDER BY nombre` (cargar_fincas_combo)
  - Línea 338: `SELECT clave, valor FROM app_settings` (cargar_configuracion)
  - Línea 349: `INSERT OR REPLACE INTO app_settings` (guardar_configuracion)
- **conn.commit():** 1 instancia (línea 350, para INSERT)
- **Validaciones:** Manejo de app_settings sin validaciones explícitas
- **Métodos afectados:** `cargar_fincas_combo()`, `cargar_configuracion()`, `guardar_configuracion()`

#### Complejidad:
- 🟢 **Muy bajo:** 1 lectura + 1 escritura, tabla auxiliar app_settings
- Sem transacciones multitabla complejas
- Riesgo de regresión: Mínimo

#### Patrón detectado:
```python
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT ... FROM app_settings")
    # ... modificar y insertar
    cur.execute("INSERT OR REPLACE...")
    conn.commit()
```

---
### Ajustes — Estado tras migración (Week 2)
**Infraestructura creada:**
- src/infraestructura/ajustes/ajustes_repository.py
- src/infraestructura/ajustes/ajustes_service.py
- src/infraestructura/ajustes/__init__.py

**UI migrada:** `src/modules/ajustes/ajustes_main.py`
- `_populate_fincas()` → `AjustesService.listar_fincas_combo()`
- `_get_settings()` → `AjustesService.obtener_settings(defaults)`
- `_set_setting()` → `AjustesService.guardar_setting(k, v)`

**Validación:**
- Pylance: 0 errores
- Auditor: sin `get_db_connection`, `cursor.execute`, `commit` en UI

**Resultado:** Ajustes gobernado ✅; UX intacta; comportamiento preservado.

### Dominio: CONFIGURACIÓN
**Directorio:** `src/modules/configuracion/` (17 archivos Python)
**Archivo principal:** `src/modules/configuracion/__main__.py` (277 líneas)
**Módulos de catálogos:** `calidad_animal.py`, `causa_muerte.py`, `diagnosticos.py`, `empleados.py`, `fincas.py`, `lotes.py`, `motivos_venta.py`, `potreros.py`, `procedencia.py`, `proveedores.py`, `razas.py`, `sectores.py`, `tipo_explotacion.py`

#### Violaciones Identificadas (por archivo):
- **calidad_animal.py:** 
  - get_connection() directo: 3 instancias (líneas 111, 141, 185)
  - cursor.execute(): 4 queries (INSERT, SELECT, DELETE con WHERE código)
  - conn.commit(): 1 instancia (línea 127)
  - Estados hardcoded: Ausentes (estructurado como catálogo)
  - Métodos: `agregar()`, `cargar()`, `eliminar()`

#### Complejidad:
- 🟢 **Bajo:** Catálogos simples (CRUD básico, sin relaciones FK complejas)
- **Riesgo combinado:** 17 archivos de catálogos → 100+ queries directas

#### Patrón detectado:
```python
def agregar(self):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO tabla (col1, col2) VALUES (?, ?)""", (val1, val2))
    conn.commit()
```

---

### Dominio: REPORTES
**Archivo principal:** `src/modules/reportes/reportes_main.py` (1265 líneas, GRANDE)

#### Violaciones Identificadas:
- **get_connection() directo:** 4+ instancias (línea 333, más sin contar)
- **cursor.execute():** 20+ queries (reads only, muy vocalizadas)
  - Línea 342–357: Multiple COUNT queries en `mostrar_resumen_general()`
  - Estados hardcoded: `WHERE estado = 'Activo'`, `WHERE estado = 'Vendido'`, `WHERE estado = 'Muerto'`
  - Sexo hardcoded: `WHERE sexo = 'Macho'`, `WHERE sexo = 'Hembra'`
  - Todas las queries son SELECT (sin UPDATE/DELETE)
- **Validaciones:** Ausentes (reads puras)
- **Métodos afectados:** `mostrar_resumen_general()`, `mostrar_reporte_inventario()`, `mostrar_reporte_ventas()`, etc.

#### Complejidad:
- 🟢 **Bajo-Medio:** Solo reads, pero múltiples estados/filtros hardcoded
- Riesgo de regresión: Bajo (UI informativa)
- Riesgo de mantenimiento: Medio (hardcoded valores dispersos)

#### Patrón detectado:
```python
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
    total_animales = cursor.fetchone()[0]
    # ... múltiples queries similares
```

---

### Dominio: HERRAMIENTAS
**Archivo principal:** `src/modules/herramientas/herramientas_main.py` (1955 líneas, MÁS GRANDE)

#### Violaciones Identificadas:
- **get_connection() directo:** 6+ instancias (línea 603, 625, 734, ...)
- **cursor.execute():** 20+ queries (reads + writes)
  - Línea 605: `SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'` (divergencia: Activa vs Activo)
  - Línea 628: Sistema check `SELECT name FROM sqlite_master...` (tabla existe?)
  - Línea 637: SELECT empleados con condiciones
  - Múltiples operaciones de CREATE TABLE inline si no existe
- **CREATE TABLE inline:** Línea ~637–650 (Problematic: DB drift si tabla se crea manualmente)
- **Validaciones:** Manejo de valores monetarios con parsing complejo (`_parse_valor()`, línea ~50–100)
- **conn.commit():** Múltiples instancias (implícitas en context manager)
- **Métodos afectados:** `cargar_fincas()`, `cargar_trabajadores()`, `cargar_herramientas()`, `guardar_herramienta()`, etc.

#### Complejidad:
- 🟡 **Medio:** CREATE TABLE inline, divergencia de estados (Activa vs Activo), múltiples operaciones
- Riesgo de regresión: Medio (CREATE TABLE puede causar schema drift)
- Riesgo de validación: Medio (_parse_valor es crítica para datos monetarios)

#### Patrón detectado:
```python
with db.get_connection() as conn:
    cursor = conn.cursor()
    # Sistema fallible: IF NOT EXISTS CREATE TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleado (
            id INTEGER PRIMARY KEY,
            ...
        )
    """)
    cursor.execute("SELECT ... FROM empleado WHERE estado = 'Activo'")
```

---

## 2. RESUMEN COMPARATIVO

| Dominio | Líneas | Queries | get_conn | commit | Estados HC | Riesgo | Prioridad |
|---------|--------|---------|----------|--------|-----------|--------|-----------|
| **Potreros** | 496 | 5 | 0 | 0 | 0 | 🟢 Bajo | ✅ |
| **Ajustes** | 731 | 3 | 0 | 0 | 0 | 🟢 Bajo | ✅ |
| **Configuración** | 17 archivos, 3000+L total | 100+ | 30+ | 10+ | Varios | 🟢 Bajo | #3 |
| **Reportes** | 1265 | 20+ | 4+ | 0 | 6+ | 🟢 Bajo-Med | #4 |
| **Herramientas** | 1955 | 20+ | 6+ | 5+ | 2 (divergencia) | 🟡 Medio | #5 |

---

## 3. PLAN DE MIGRACIÓN (Week-by-Week)

### ✅ Auditoría Completada
- [x] Potreros: 5 queries identificadas, 1 estado HC, baja complejidad
- [x] Ajustes: 3 queries, 0 estados HC, muy baja complejidad
- [x] Configuración: 17 módulos, ~100 queries directas, arquitectura de catálogos consistente
- [x] Reportes: 20+ queries (reads), 6+ estados HC, baja complejidad
- [x] Herramientas: 20+ queries (reads+writes), 2 divergencias estado, CREATE TABLE inline

---

### Week 1: POTREROS (Target: 1 dominio completo)
**Status:** Pendiente (siguiente)

**Tareas:**
1. Crear `src/infraestructura/potreros/potreros_repository.py`
   - Métodos: `obtener_fincas_activas()`, `obtener_potreros_por_finca()`, `obtener_potreros_todos()`, `obtener_metricas_potrero()`
2. Crear `src/infraestructura/potreros/potreros_service.py`
   - Validaciones: Estado = 'Activo' (centralizado), finca_id vs nombre
   - Métodos: `listar_fincas()`, `listar_potreros()`, `listar_potreros_filtrado()`, `obtener_metricas()`
3. Refactorizar `src/modules/potreros/potreros_main.py`
   - Importar: `from infraestructura.potreros import PotrerosService, PotrerosRepository`
   - Reemplazar: Todos los `db.get_connection()` → `self.service.método()`
   - Resultado esperado: 0 get_connection(), 0 cursor.execute(), 0 SQL en UI
4. Validación:
   - [ ] Pylance 0 errors
   - [ ] Auditor Exit 0
   - [ ] UI sin cambios visuales
5. Documentar: `FASE9_0_POTREROS_CLOSURE.md`

**Entrada:** Potreros abierto en workspace, auditoría completada
**Salida:** Potreros 100% gobernado, próximo: Ajustes

---

### Week 2: AJUSTES (Target: 1 dominio completo)
**Status:** Pendiente

**Tareas:** (Similar a Potreros)
1. Crear repository + service
2. Refactorizar UI
3. Validar + documentar

---

### Week 3: CONFIGURACIÓN (Target: 17 módulos de catálogos)
**Status:** Pendiente
**Desafío:** Arquitectura distribuida (17 archivos) → requiere coordinación centralizada en service

---

### Week 4: REPORTES + HERRAMIENTAS (Target: 2 dominios)
**Status:** Pendiente
**Nota:** Reportes es rápido (reads only); Herramientas tiene complejidad media

---

## 4. RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|--------|-----------|
| Regresión visual (filtros no funcionan) | 🔴 Alta en Potreros | Alto | Pruebas manuales antes/después |
| Estados hardcoded divergen | 🟡 Media | Medio | Usar contratos de service (centralizar) |
| CREATE TABLE inline en Herramientas | 🟡 Media | Medio | Migrar a schema.sql + migrations |
| Validaciones incompletas en Ajustes | 🟢 Baja | Bajo | Agregar validaciones en Service |

---

## 5. PROGRESO EN TIEMPO REAL

### Cronología
- **2025-12-21:** Week 11 (Lotes - COMPLETE) completado ✅ — **DECISIÓN:** Validaciones centralizadas (FK activa, unicidad por finca), soft delete, normalización UPPER/title, -43% código (~387→~220)
- **2025-12-21:** Week 10 (Fincas - base scope) completado ✅ — **DECISIÓN ARQUITECTÓNICA:** SIMPLIFIED scope (codigo, nombre, ubicacion, estado) con soft delete, -50% código (574→288 líneas)
- **2025-12-20:** Week 9 (Empleados - base scope) completado ✅ — **DECISIÓN ARQUITECTÓNICA:** SIMPLIFIED scope (sin nómina) habilita handoff limpio a FASE 9.2
- **2025-12-20:** Week 8 (Razas) completado ✅
- **2025-12-20:** Week 7 (Motivos de Venta) completado ✅
- **2025-12-19:** Week 6 (Procedencia) completado ✅ — **RIESGO CRÍTICO MITIGADO:** DELETE hard → soft delete
- **2025-12-19:** Week 5 (Diagnósticos) completado ✅
- **2025-12-19:** Week 4 (Causa de Muerte) completado ✅
- **2025-12-19:** Week 3 (Calidad Animal) completado ✅
- Semana 1: Potreros gobernado ✅
- Semana 2: Ajustes gobernado ✅
- **Estado:** FASE 9.0 en curso, 11/13 dominios gobernados (85%)


---

## 6. MATRIZ DE DOMINIOS

| # | Dominio | Status | Repository | Service | UI Migrada | Pylance | Auditor | Doc |
|---|---------|--------|------------|---------|-----------|---------|--------|-----|
| 1 | Potreros | ✅ | 9M | 7M | ✅ | 0E | 0E | ✅ |
| 2 | Ajustes | ✅ | 3M | 3M | ✅ | 0E | 0E | ✅ |
| 3 | Config (Calidad) | ✅ | 8M | 4M | ✅ | 0E | 0E | ✅ |
| 4 | Config (Causa Muerte) | ✅ | 6M | 4M | ✅ | 0E | 0E | ✅ |
| 5 | Config (Diagnósticos) | ✅ | 5M | 4M | ✅ | 0E | 0E | ✅ |
| 6 | Config (Procedencia) | ✅ | 6M | 5M | ✅ | 0E | 0E | ✅ |
| 7 | Config (Motivos Venta) | ✅ | 5M | 6M | ✅ | 0E | 0E | ✅ |
| 8 | Config (Razas) | ✅ | 6M | 6M | ✅ | 0E | 0E | ✅ |
| 9 | Config (Empleados) | ✅ | 7M | 6M | ✅ | 0E | 0E | ✅ |
| 10 | Config (Fincas - base) | ✅ | 6M | 5M | ✅ | 0E | 0E | ✅ |
| 11 | Config (Lotes - complete) | ✅ | 8M | 7M | ✅ | 0E | 0E | ✅ |
| 12 | Config (Sectores) | ✅ | 8M | 7M | ✅ | 0E | 0E | ✅ |
| 13 | Config (Tipo Explotación) | ✅ | 7M | 6M | ✅ | 0E | 0E | ✅ |
| 17 | Reportes | ⏳ | ~20M | ~10M | TBD | TBD | TBD | TBD |
| 18 | Herramientas | ⏳ | ~20M | ~15M | TBD | TBD | TBD | TBD |

**Gobernados:** 13/13 (100%)  
**En progreso:** 0/13 (0%)

---
### Cronología — Actualización
- **2025-12-21:** Week 10 (Fincas - base scope) completado ✅ — **DECISIÓN ARQUITECTÓNICA:** SIMPLIFIED scope (base fields only, no propietario/área/teléfono/email/descripción) = clean architecture, -50% código
- **2025-12-21:** Week 11 PASO 2 (Lotes) completado ✅ — Inline editing pattern (-50% código), soft delete confirmado
- **2025-12-21:** Week 11 PASO 3 (Sectores) completado ✅ — Inline editing (-77% código), corruption recovery via Python scripts
- **2025-12-22:** Week 12 PASO FINAL (Tipo Explotación) completado ✅ — Cierre limpio: UI sin SQL, soft delete, validaciones y normalización

**Semana siguiente recomendada:** Week 12 — Configuración · [Catálogo 13/13 final] + Evaluación módulos Reportes/Herramientas

**Próximos pasos:** Week 12 para completar 13/13 catálogos (100% Config) → Evaluación Reportes + Herramientas → Fase 9.0 closure
