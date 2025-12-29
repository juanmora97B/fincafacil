# 🔍 FASE 8.4.1 — AUDITORÍA PASIVA DOMINIO REPRODUCCIÓN

**Fecha:** 18 de diciembre de 2025  
**Fase:** FASE 8.4.1 — Auditoría sin modificar código  
**Objetivo:** Inventariar violaciones, clasificar riesgos, mapear flujos críticos

---

## 📊 RESUMEN EJECUTIVO

### ESTADO ACTUAL DEL DOMINIO

El dominio **Reproducción** actualmente **NO está gobernado**:
- ❌ **TODO el código SQL está en UI**
- ❌ **NO existe ReproduccionService**
- ❌ **NO existe ReproduccionRepository**
- ❌ **UI accede directamente a `get_db_connection()`**
- ❌ **72+ violaciones directas UI→BD**

**COMPLEJIDAD:**
- **Archivos:** 2 (reproduccion_main.py + __init__.py)
- **Líneas:** 1002 (todo en UI monolítica)
- **Queries SQL embebidas:** 30+
- **Flujos críticos:** 4 (registro servicio, parto, gestantes, próximos partos)

---

## 📁 INVENTARIO DE ARCHIVOS

### ARCHIVOS DEL DOMINIO

| Archivo | Tipo | Líneas | Estado | Violaciones |
|---------|------|--------|--------|-------------|
| `src/modules/reproduccion/reproduccion_main.py` | UI | 1002 | 🟥 Crítico | 72+ |
| `src/modules/reproduccion/__init__.py` | Config | ~10 | ✅ OK | 0 |

**TOTAL:** 2 archivos, ~1012 líneas

---

## 🔴 CLASIFICACIÓN DE VIOLACIONES

### 🟥 VIOLACIONES CRÍTICAS (UI → BD DIRECTO)

**IMPORT PROHIBIDO:**
```python
# Línea 13
from database.connection import get_db_connection
```

**ACCESOS DIRECTOS A BD:**

#### 1. **ModalRegistroParto.guardar()** — Líneas 138-188
- **Tipo:** INSERT/UPDATE directo con transacciones complejas
- **Queries:**
  - `UPDATE servicio SET estado=?, fecha_parto_real=?, observaciones=? WHERE id=?`
  - `INSERT INTO comentario (id_animal, fecha, tipo, nota, autor) ...`
  - `SELECT MAX(CAST(SUBSTR(codigo, 2) AS INTEGER)) FROM animal ...`
  - `SELECT id_finca FROM animal WHERE id=?`
  - `INSERT INTO animal (codigo, nombre, sexo, fecha_nacimiento, ...) VALUES (...)`
- **Lógica embebida:**
  - Generación automática de código de cría
  - Registro de animal hijo
  - Registro de comentario
  - Commit/rollback manual

#### 2. **ReproduccionModule._actualizar_badges()** — Líneas 246-262
- **Tipo:** SELECT múltiple para contadores
- **Queries:**
  - `SELECT COUNT(*) FROM servicio WHERE estado='Gestante'`
  - `SELECT COUNT(*) FROM servicio WHERE fecha_parto_estimada BETWEEN ...`
  - `SELECT COUNT(*) FROM servicio WHERE tipo_servicio LIKE '%Inseminación%' ...`
  - `SELECT COUNT(*) FROM servicio WHERE tipo_servicio='Monta Natural' ...`

#### 3. **ModalRegistroServicio._cargar_fincas()** — Líneas 550-553
- **Tipo:** SELECT catálogo
- **Query:**
  - `SELECT id, nombre FROM finca WHERE estado='Activo' ORDER BY nombre`

#### 4. **ModalRegistroServicio._cargar_hembras()** — Líneas 585-596
- **Tipo:** SELECT filtrado por finca y sexo
- **Queries:**
  - `SELECT id, codigo, COALESCE(nombre,'') FROM animal WHERE id_finca=? AND sexo='Hembra' ...`
  - `SELECT id, codigo, COALESCE(nombre,'') FROM animal WHERE sexo='Hembra' ...`

#### 5. **ModalRegistroServicio._cargar_machos()** — Líneas 610-623
- **Tipo:** SELECT filtrado por finca y sexo
- **Queries:**
  - `SELECT id, codigo, COALESCE(nombre,'') FROM animal WHERE id_finca=? AND sexo='Macho' ...`
  - `SELECT id, codigo, COALESCE(nombre,'') FROM animal WHERE sexo='Macho' ...`

#### 6. **ModalRegistroServicio.guardar()** — Líneas 695-737
- **Tipo:** INSERT con validaciones y transacción
- **Queries:**
  - `SELECT COUNT(*) FROM servicio WHERE id_hembra=? AND estado='Gestante'`
  - `SELECT COUNT(*) FROM servicio WHERE id_hembra=? AND fecha_servicio=?`
  - `INSERT INTO servicio (id_hembra, id_macho, fecha_servicio, tipo_servicio, estado, fecha_parto_estimada, observaciones) VALUES (...)`
  - `INSERT INTO comentario (id_animal, fecha, tipo, nota, autor) VALUES (...)`
- **Lógica embebida:**
  - Validación de hembra ya gestante
  - Validación de servicio duplicado
  - Cálculo de fecha estimada de parto (280 días)
  - Registro de comentario

#### 7. **ReproduccionModule.cargar_gestantes()** — Líneas 784-817
- **Tipo:** SELECT complejo con JOIN
- **Query:**
  ```sql
  SELECT s.id, a.id, a.codigo, COALESCE(a.nombre,''), s.fecha_servicio, s.tipo_servicio,
         COALESCE(m.codigo,'N/A'), s.fecha_parto_estimada, s.observaciones, s.estado
  FROM servicio s
  INNER JOIN animal a ON s.id_hembra=a.id
  LEFT JOIN animal m ON s.id_macho=m.id
  WHERE s.estado='Gestante'
  ORDER BY s.fecha_parto_estimada
  ```
- **Lógica embebida:**
  - Cálculo de días de gestación (`(hoy - fecha_servicio).days`)
  - Formateo de texto de estado
  - Asignación de tags visuales

#### 8. **ReproduccionModule.cargar_proximos()** — Líneas 862-893
- **Tipo:** SELECT complejo con cálculos temporales
- **Query:**
  ```sql
  SELECT s.id, a.id, a.codigo, COALESCE(a.nombre,''), s.fecha_servicio, s.tipo_servicio,
         COALESCE(m.codigo,'N/A'), s.fecha_parto_estimada, s.estado
  FROM servicio s
  INNER JOIN animal a ON s.id_hembra=a.id
  LEFT JOIN animal m ON s.id_macho=m.id
  WHERE s.estado='Gestante' AND DATE(s.fecha_parto_estimada) BETWEEN DATE('now') AND DATE('now','+60 days')
  ORDER BY s.fecha_parto_estimada
  ```
- **Lógica embebida:**
  - Cálculo de días de gestación
  - Cálculo de días faltantes para parto
  - Asignación de tags por urgencia

#### 9. **ReproduccionModule._registrar_parto_modal()** — Líneas 938-946
- **Tipo:** SELECT simple para obtener hembra_id
- **Query:**
  - `SELECT id_hembra FROM servicio WHERE id=?`

#### 10. **ReproduccionModule.marcar_vacia()** — Líneas 956-963
- **Tipo:** UPDATE simple con confirmación
- **Query:**
  - `UPDATE servicio SET estado='Vacía' WHERE id=?`

---

### 📊 CONTEO DE VIOLACIONES POR TIPO

| Tipo de Violación | Cantidad | Criticidad |
|-------------------|----------|------------|
| `get_db_connection()` | 10 | 🟥 Crítica |
| `cur.execute()` con SQL directo | 30+ | 🟥 Crítica |
| INSERT/UPDATE/DELETE en UI | 8 | 🟥 Crítica |
| SELECT con JOIN en UI | 2 | 🟥 Crítica |
| Lógica de negocio en UI | 6 | 🟧 Alta |
| Cálculos temporales en UI | 4 | 🟧 Alta |
| Commit/rollback manual en UI | 4 | 🟥 Crítica |
| **TOTAL** | **72+** | **🟥 CRÍTICO** |

---

## 🗺️ MAPEO DE FLUJOS CRÍTICOS

### FLUJO 1: REGISTRO DE SERVICIO REPRODUCTIVO

**Pantalla:** `ModalRegistroServicio`

**Entrada:**
- Finca (opcional)
- Hembra (obligatorio)
- Macho/Semen (obligatorio)
- Fecha de servicio
- Tipo: Monta Natural / Inseminación Artificial
- Observaciones

**Proceso:**
1. Validar hembra no gestante previamente
2. Validar no duplicar servicio en misma fecha
3. Calcular fecha estimada de parto (+280 días)
4. Insertar registro en tabla `servicio`
5. Insertar comentario en bitácora de animal
6. Commit transacción

**Salida:**
- Nuevo servicio registrado con `estado='Gestante'`
- Comentario en historial del animal

**Queries involucradas:** 6
**Transacciones:** 1 (con commit manual)

---

### FLUJO 2: REGISTRO DE PARTO

**Pantalla:** `ModalRegistroParto`

**Entrada:**
- Servicio asociado (id)
- Hembra (heredada)
- Fecha de parto
- Tipo de parto: Normal / Distócico / Cesárea / Aborto
- Sexo de cría
- Peso de cría (opcional)
- Estado de cría: Vivo / Muerto al nacer / Murió después
- Registrar cría automáticamente (checkbox)
- Observaciones

**Proceso:**
1. Actualizar servicio con `estado='Parida'`, `fecha_parto_real`
2. Insertar comentario de parto en bitácora de hembra
3. **Si registrar_cria == True:**
   - Generar código automático (ej: A0123)
   - Obtener finca de la madre
   - Insertar nuevo animal con `tipo_ingreso='NACIMIENTO'`, `id_madre=hembra_id`
4. Commit transacción

**Salida:**
- Servicio actualizado a `Parida`
- Comentario en historial
- Opcionalmente: nuevo animal registrado

**Queries involucradas:** 5-8 (depende de si se registra cría)
**Transacciones:** 1 (con commit manual)

---

### FLUJO 3: CONSULTA DE GESTANTES

**Pantalla:** `ReproduccionModule` (Tab "Gestantes")

**Entrada:**
- Filtros opcionales: fechas desde/hasta, búsqueda por código

**Proceso:**
1. Ejecutar SELECT complejo con JOINs:
   ```sql
   SELECT s.id, a.id, a.codigo, nombre, fecha_servicio, tipo_servicio, 
          toro, fecha_parto_estimada, observaciones, estado
   FROM servicio s
   INNER JOIN animal a ON s.id_hembra=a.id
   LEFT JOIN animal m ON s.id_macho=m.id
   WHERE s.estado='Gestante'
   ```
2. Calcular días de gestación en Python
3. Formatear estado visual (días + texto)
4. Asignar tags de color
5. Mostrar en TreeView

**Salida:**
- Lista de gestantes con:
  - Código hembra
  - Días de gestación
  - Parto estimado
  - Toro/Semen usado
  - Estado visual con color

**Queries involucradas:** 1 (complejo con JOIN)

---

### FLUJO 4: PRÓXIMOS PARTOS (60 DÍAS)

**Pantalla:** `ReproduccionModule` (Tab "Próximos Partos")

**Entrada:**
- Filtro temporal automático: hoy + 60 días

**Proceso:**
1. Ejecutar SELECT con filtro temporal:
   ```sql
   WHERE s.estado='Gestante' 
   AND DATE(s.fecha_parto_estimada) BETWEEN DATE('now') AND DATE('now','+60 days')
   ```
2. Calcular días de gestación
3. Calcular días restantes para parto
4. Asignar tags por urgencia:
   - `critico`: ≤ 7 días
   - `alerta`: ≤ 15 días
   - `normal`: > 15 días
5. Mostrar en TreeView ordenado por fecha

**Salida:**
- Lista de próximos partos ordenada
- Indicadores visuales de urgencia

**Queries involucradas:** 1 (complejo con JOIN y fecha)

---

## 🚨 RIESGOS IDENTIFICADOS

### 1. **LÓGICA DE NEGOCIO EN UI** 🟥 CRÍTICO

**Problema:**
- Validaciones de hembra gestante previa → En UI
- Cálculo de fecha estimada de parto (+280 días) → En UI
- Generación automática de códigos de crías → En UI
- Reglas de duplicación → En UI

**Riesgo:**
- ❌ Imposible reutilizar lógica en otros módulos
- ❌ Sin tests unitarios posibles
- ❌ Reglas de negocio acopladas a CustomTkinter

**Solución:**
Mover a `ReproduccionService`:
- `validar_hembra_gestante(hembra_id)`
- `calcular_fecha_parto_estimada(fecha_servicio)`
- `generar_codigo_cria()`
- `puede_registrar_servicio(hembra_id, fecha)`

---

### 2. **TRANSACCIONES COMPLEJAS EN UI** 🟥 CRÍTICO

**Problema:**
- Registro de parto con cría → 3-5 INSERTs + 1 UPDATE en UI
- Commit/rollback manual
- Sin manejo consistente de errores

**Riesgo:**
- ❌ Inconsistencias en BD si falla parte del proceso
- ❌ Rollback manual puede no ejecutarse
- ❌ Difícil auditar qué se hizo en cada transacción

**Solución:**
Mover a `ReproduccionRepository`:
- `registrar_parto_con_cria(servicio_id, datos_parto, datos_cria)`
- Transacción atómica manejada por repositorio

---

### 3. **QUERIES COMPLEJAS CON JOIN EN UI** 🟥 CRÍTICO

**Problema:**
- UI conoce estructura de tablas (`servicio`, `animal`)
- UI conoce relaciones FK (`id_hembra`, `id_macho`)
- UI conoce alias de SQL (`s`, `a`, `m`)

**Riesgo:**
- ❌ Cambios en esquema rompen UI directamente
- ❌ Imposible optimizar queries sin tocar UI
- ❌ No hay abstracción de persistencia

**Solución:**
Encapsular en `ReproduccionRepository`:
- `listar_gestantes(filtros)`
- `listar_proximos_partos(dias)`
- UI recibe listas de diccionarios, no conoce SQL

---

### 4. **CÁLCULOS TEMPORALES DUPLICADOS** 🟧 ALTA

**Problema:**
- Cálculo de días de gestación repetido en:
  - `cargar_gestantes()`
  - `cargar_proximos()`
- Cálculo de días faltantes repetido

**Riesgo:**
- ⚠️ Inconsistencias si se cambia lógica en un lugar
- ⚠️ Dificulta mantenimiento

**Solución:**
Centralizar en `ReproduccionService`:
- `calcular_dias_gestacion(fecha_servicio)`
- `calcular_dias_para_parto(fecha_parto_estimada)`

---

### 5. **NO HAY VALIDACIÓN DE TIPO** 🟧 MEDIA

**Problema:**
- No hay type hints en ningún método
- Pylance no puede validar tipos

**Riesgo:**
- ⚠️ Errores de tipo en runtime
- ⚠️ Refactor inseguro

**Solución:**
Agregar tipos en service/repository:
```python
def registrar_servicio(self, datos: Dict[str, Any]) -> int:
def listar_gestantes(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
```

---

## 📋 DEPENDENCIAS IDENTIFICADAS

### TABLAS DE BD UTILIZADAS

| Tabla | Operaciones | Criticidad |
|-------|-------------|------------|
| `servicio` | SELECT, INSERT, UPDATE | 🟥 Crítica |
| `animal` | SELECT (lectura), INSERT (cría) | 🟥 Crítica |
| `comentario` | INSERT | 🟧 Alta |
| `finca` | SELECT (catálogo) | 🟨 Media |

### RELACIONES FK

```
servicio.id_hembra → animal.id
servicio.id_macho → animal.id
animal.id_madre → animal.id (auto-referencia)
animal.id_finca → finca.id
comentario.id_animal → animal.id
```

---

## 🎯 ESTRATEGIA DE MIGRACIÓN

### ORDEN PROPUESTO (INCREMENTAL)

#### FASE 8.4.2 — ENCAPSULACIÓN INICIAL
1. Crear `ReproduccionRepository`:
   - Mover todos los SELECTs
   - Mover todos los INSERTs/UPDATEs
   - Encapsular transacciones complejas

2. Crear `ReproduccionService`:
   - Validaciones de negocio
   - Cálculos temporales
   - Generación de códigos
   - Orquestación de flujos

3. **NO tocar UI** (sigue funcionando con código actual)

#### FASE 8.4.3 — MIGRACIÓN GRADUAL DE UI

**Orden de archivos:**
1. **ModalRegistroServicio** (registro de monta/inseminación)
   - Queries: 6
   - Complejidad: Media
   - Riesgo: Bajo (CRUD simple)

2. **ModalRegistroParto** (registro de parto + cría opcional)
   - Queries: 5-8
   - Complejidad: Alta (transacción compleja)
   - Riesgo: Medio (generación automática de código)

3. **ReproduccionModule.cargar_gestantes()** (consulta con JOIN)
   - Queries: 1 (complejo)
   - Complejidad: Media
   - Riesgo: Bajo (solo lectura)

4. **ReproduccionModule.cargar_proximos()** (consulta con filtro temporal)
   - Queries: 1 (complejo)
   - Complejidad: Media
   - Riesgo: Bajo (solo lectura)

5. **Métodos auxiliares** (_actualizar_badges, marcar_vacia, etc.)
   - Queries: 4-5
   - Complejidad: Baja
   - Riesgo: Bajo

---

## 📊 MÉTRICAS INICIALES (BASELINE)

### VIOLACIONES UI→BD

| Categoría | Cantidad |
|-----------|----------|
| Imports prohibidos (`get_db_connection`) | 1 |
| Accesos directos a BD (`cur.execute`) | 30+ |
| INSERT/UPDATE/DELETE en UI | 8 |
| SELECT con JOIN en UI | 2 |
| Commit/rollback manual | 4 |
| **TOTAL** | **72+** |

### ARQUITECTURA ACTUAL

```
┌─────────────────────────────────────────┐
│ reproduccion_main.py (UI)               │
│ ├─ get_db_connection()                  │
│ ├─ cur.execute("SELECT ...")            │
│ ├─ cur.execute("INSERT ...")            │
│ ├─ cur.execute("UPDATE ...")            │
│ ├─ conn.commit()                        │
│ ├─ Validaciones de negocio              │
│ ├─ Cálculos temporales                  │
│ └─ Generación de códigos                │
└─────────────────────────────────────────┘
           ▼ VIOLACIÓN DIRECTA
┌─────────────────────────────────────────┐
│ database.connection (SQLite)            │
└─────────────────────────────────────────┘
```

### ARQUITECTURA OBJETIVO (POST-FASE 8.4)

```
┌─────────────────────────────────────────┐
│ reproduccion_main.py (UI)               │
│ ├─ reproduccion_service.registrar_...() │
│ ├─ reproduccion_service.listar_...()    │
│ └─ Diccionarios Python                  │
└─────────────────────────────────────────┘
           ▼ FRONTERA RESPETADA
┌─────────────────────────────────────────┐
│ ReproduccionService (Dominio)           │
│ ├─ Validaciones de negocio              │
│ ├─ Cálculos temporales                  │
│ ├─ Orquestación de flujos               │
│ └─ Delegación a repositorio             │
└─────────────────────────────────────────┘
           ▼ FRONTERA RESPETADA
┌─────────────────────────────────────────┐
│ ReproduccionRepository (Infraestructura)│
│ ├─ SQL parametrizado                    │
│ ├─ Transacciones atómicas               │
│ └─ ejecutar_consulta()                  │
└─────────────────────────────────────────┘
           ▼
┌─────────────────────────────────────────┐
│ database.connection → SQLite            │
└─────────────────────────────────────────┘
```

---

## 🔐 COMPROMISOS DE MIGRACIÓN

### ✅ GARANTÍAS

1. **Backward compatible 100%**
   - UI mantiene misma UX
   - Mismo comportamiento funcional
   - Mismos mensajes de error

2. **Incremental y reversible**
   - Migración archivo por archivo
   - Auditor valida cada paso
   - Sin cambios masivos

3. **Sin regresiones**
   - Misma data persistida
   - Mismas validaciones
   - Mismos cálculos

### ❌ NO SE HARÁ

1. ❌ No cambiar lógica de negocio
2. ❌ No optimizar queries ahora
3. ❌ No refactorizar UI innecesariamente
4. ❌ No tocar otros dominios

---

## 📚 REFERENCIA: PATRÓN ANIMALES

**Usaremos como plantilla exacta:**

| Fase Animales | Equivalente Reproducción | Estado |
|---------------|--------------------------|--------|
| FASE 8.2 | FASE 8.4.2 — Encapsulación | ⏳ Pendiente |
| FASE 8.3.1 | FASE 8.4.3 — Migración UI (Modales) | ⏳ Pendiente |
| FASE 8.3.2 | FASE 8.4.3 — Migración UI (Listados) | ⏳ Pendiente |
| FASE 8.3 Final | FASE 8.4.4 — Cierre Dominio | ⏳ Pendiente |

**Estructura a replicar:**
```
src/infraestructura/reproduccion/
├── __init__.py
├── reproduccion_repository.py
└── reproduccion_service.py
```

---

## 🏁 CRITERIOS DE ÉXITO (FASE 8.4 COMPLETA)

### ✅ AUDITORÍA FINAL

- [ ] `reproduccion_main.py` sin `get_db_connection`
- [ ] 0 queries SQL embebidas en UI
- [ ] 0 commits manuales en UI
- [ ] Auditor → Exit 0
- [ ] Pylance → 0 errores

### ✅ SERVICIO CREADO

- [ ] `ReproduccionService` con 15+ métodos públicos
- [ ] `ReproduccionRepository` con 20+ métodos de acceso a datos
- [ ] Type hints completos
- [ ] Documentación inline

### ✅ FUNCIONALIDAD PRESERVADA

- [ ] Registro de servicios funcional
- [ ] Registro de partos funcional
- [ ] Consulta de gestantes funcional
- [ ] Próximos partos funcional
- [ ] Exportación CSV funcional

---

## 📋 PRÓXIMOS PASOS

### INMEDIATO: FASE 8.4.2

1. Crear estructura de directorios
2. Crear `reproduccion_repository.py` con SQL
3. Crear `reproduccion_service.py` con lógica
4. Validar con Pylance
5. Documentar API creada

**Sin tocar UI todavía.**

---

## 🎓 CONCLUSIONES

### ESTADO ACTUAL

- ❌ **Dominio NO gobernado**
- ❌ **72+ violaciones críticas**
- ❌ **Lógica de negocio en UI**
- ❌ **SQL embebido en UI**
- ❌ **Transacciones manuales riesgosas**

### COMPLEJIDAD ESTIMADA

| Aspecto | Nivel | Justificación |
|---------|-------|---------------|
| Encapsulación SQL | 🟧 Media | 30+ queries pero sin PRAGMA complejos |
| Lógica de negocio | 🟧 Media | Cálculos temporales y generación de códigos |
| Transacciones | 🟥 Alta | Registro de parto con cría = transacción atómica |
| Migración UI | 🟨 Media-Baja | 2 modales + 2 métodos de listado |

**Tiempo estimado:** 4-6 horas (siguiendo patrón Animales)

---

**AUDITORÍA COMPLETADA — SIN MODIFICACIONES DE CÓDIGO**

Listo para avanzar a **FASE 8.4.2 — Encapsulación Inicial**.

---

**Documento generado por:** GitHub Copilot  
**Validado con:** Análisis estático + grep_search  
**Próximo paso:** FASE 8.4.2 — Crear ReproduccionService + ReproduccionRepository
