# FASE 9.0.10.1 — Auditoría Pasiva · Configuración · Fincas (Scope SIMPLIFIED)

**Fecha:** 2025-12-20  
**Dominio:** Configuración · Fincas (catálogo base)  
**Alcance permitido:** CRUD base (código_finca, nombre, ubicación/municipio/departamento si aplica, estado {Activo, Inactivo}, soft delete)  
**Exclusiones:** Producción, Animales, Potreros, Indicadores/KPIs, Reportes, lógica cruzada

## 1) Archivo auditado
- [src/modules/configuracion/fincas.py](src/modules/configuracion/fincas.py) — 574 líneas

## 2) Métricas de violaciones (UI)
- `sqlite3` import: **1**
- `db.get_connection()`: **5** (guardar, cargar, editar, eliminar, importar)
- `cursor.execute()`: **11** aprox (Select/Update/Insert/Delete dispersos)
- `conn.commit()`: **4** aprox (guardar, editar, eliminar, importar)
- DELETE físico: **1** (`DELETE FROM finca WHERE id = ?` en eliminar_finca)
- Estados usados: `'Activo'`, `'Inactivo'` (pero sin soft delete consistente)

## 3) Hallazgos clave
- SQL directo en UI: CRUD completo (SELECT/INSERT/UPDATE/DELETE) dentro de `fincas.py`.
- Hard delete: `eliminar_finca()` ejecuta `DELETE FROM finca`, rompe historial; debe ser soft delete.
- Estado: usa `estado = 'Activo'` en INSERT; no hay cambio a 'Inactivo' en eliminación (borra fila).
- Validaciones/normalización ausentes en Service: UI valida mínimos pero sin UPPER/TRIM centralizado.
- Dependencia a DB en UI: `sqlite3`, `db.get_connection()`, `cursor.execute()`, `commit()`.
- Lógica de reactivación parcial: reactivación si estado='Inactivo' pero gestionada en UI.
- Imports y paths manuales: `sys.path.append(...)` para alcanzar DB (no deseable en UI gobernada).

## 4) Alcance decidido (obligatorio, SIMPLIFIED)
- Incluir: CRUD base de fincas con campos mínimos (código_finca, nombre, ubicación/municipio/departamento si existen, estado {Activo, Inactivo}), soft delete vía `estado='Inactivo'`.
- Excluir: Producción, Animales, Potreros, Indicadores/KPIs, Reportes, lógicas cruzadas.
- Identificador: usar **código_finca** (no nombre) en service/repo; estados homogéneos {Activo, Inactivo}.

## 5) Plan (7 PASOS) — pendiente de ejecución
1. Auditoría (este documento) ✅
2. Repository (SQL-only): `listar_fincas_activas`, `obtener_finca`, `existe_codigo_finca`, `crear_finca_base`, `actualizar_finca_base`, `cambiar_estado_finca`.
3. Service: validaciones (código único, nombre obligatorio), normalización UPPER/TRIM, estados permitidos {Activo, Inactivo}, ValueError on fail.
4. UI: refactor `fincas.py` para usar solo `ConfiguracionService`; remover SQL, sqlite3, get_connection, commit; mantener UX.
5. Validación: Pylance 0, auditar_fronteras exit 0, grep SQL=0, CRUD manual OK.
6. Documentación: FASE9_0_10_2_MIGRACION_CONFIGURACION_FINCAS.md.
7. Log maestro: actualizar FASE9_0_LOG.md (Fincas gobernado, progreso y siguiente dominio).

## 6) Riesgos si no se migra
- Pérdida de historial por DELETE físico.
- Inconsistencias en estados al no usar soft delete.
- Duplicados de código por falta de validación centralizada.
- Fragilidad por SQL en UI (sin pruebas ni reutilización Service/Repo).

## 7) Recomendaciones inmediatas
- Aplicar soft delete (estado='Inactivo') en lugar de DELETE.
- Centralizar validaciones en Service (código único, nombre requerido, normalización UPPER/TRIM).
- Eliminar `sqlite3` y `get_connection` de `fincas.py`; usar `ConfiguracionService`.
- Mantener scope SIMPLIFIED; no agregar producción/animales/potreros/kpis.
