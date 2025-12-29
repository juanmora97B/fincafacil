# 🛠️ Guía Oficial de Desarrollo de Dominios (FASE 8.7)

Objetivo: que cualquier desarrollador pueda seguir el patrón sin romper la arquitectura.

---

## Patrón Repository + Service

- UI solo consume Services; nunca accede a BD ni conoce SQL
- Service contiene reglas de negocio y orquestación; Repository solo SQL
- Inyección de dependencias: `Service(repository=Repo())` (repo opcional preferido)

---

## Reglas de Imports

- UI → importa desde `src/infraestructura/<dominio>/__init__.py`
- Service → importa solo su Repository y utilidades agnósticas
- Repository → importa wrapper de BD (`ejecutar_consulta`) y typing
- Prohibido: `ejecutar_consulta` en UI, SQL en Service

---

## Naming Conventions (oficial)

- `listar_*`: colecciones
- `obtener_*`: entidad única
- `registrar_*`: creación
- `actualizar_*`: modificación
- `marcar_*`: transición de estado
- `cargar_*`: catálogos
- `validar_*`: reglas explícitas y testeables

---

## Parámetros y Tipos

- IDs en filtros: `*_id: Optional[int]`
- Fechas: `YYYY-MM-DD` (`str` documentada)
- Booleans: `bool`
- Payloads: `Dict[str, Any]` para creación/actualización compleja
- Retornos: `List[Dict[str, Any]]`, `Optional[Dict[str, Any]]`, `Dict[str, Any]`, `None`

---

## Estados y Catálogos

- No hardcoded en Services
- Usar gateway/tablas dedicadas
- Services validan; UI solo consume

---

## Manejo de Errores

- Actual: `ValueError` con mensajes claros
- Futuro: taxonomía de dominio (ver `errores_dominio.md`)
- La UI captura y muestra; no interpreta validaciones

---

## Qué NO hacer (errores comunes)

- ❌ SQL en UI o Service
- ❌ `ejecutar_consulta` fuera de Repository
- ❌ Filtros por nombres en lugar de IDs
- ❌ Validaciones en UI
- ❌ Cambiar firmas públicas sin alias/compatibilidad

---

## Ejemplos

### Correcto
- UI: `service.obtener_historial_tratamientos(limite=100)`
- Service: valida animal activo → delega a repo
- Repository: `SELECT ... JOIN ... ORDER BY fecha DESC`

### Incorrecto
- UI: `cursor.execute("SELECT ...")`
- Service: `cursor.execute("UPDATE ...")`
- Filtro: `cargar_animales_por_finca(nombre: str)` en nuevo código

---

## Checklists rápidas

- Imports revisados (UI no toca BD)
- Naming, parámetros y tipos conforme a contrato
- Validaciones en Service con mensajes claros
- Catálogos desde gateway/tabla
- Auditor y Pylance en verde

---

Referencias:
- Contratos: [src/dominio/contratos/service_contracts.py](../src/dominio/contratos/service_contracts.py)
- Errores: [src/dominio/contratos/errores_dominio.md](../src/dominio/contratos/errores_dominio.md)
- Gateways: [src/dominio/gateways/README.md](../src/dominio/gateways/README.md)
