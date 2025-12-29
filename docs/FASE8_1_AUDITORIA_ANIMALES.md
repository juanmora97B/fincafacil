# FASE 8.1 — AUDITORÍA LEGACY DEL DOMINIO ANIMALES (SOLO LECTURA)

**Proyecto:** FincaFácil v2.0 — ERP Ganadero  
**Fecha:** 18 de diciembre de 2025  
**Alcance:** Dominio Animales (UI + lógica asociada)  
**Restricción:** Sin cambios de código; auditoría pasiva  
**Base para:** FASE 8.2 (Encapsulación)

---

## Resumen ejecutivo
- Se identificaron **17 archivos** ligados al dominio Animales (UI predominante).  
- **15 archivos UI** acceden directo a BD (`get_db_connection`/`database.database`): violación de frontera UI→Infra documentada desde FASE 7.2.  
- `modules.animales.service` concentra operaciones CRUD de negocio pero usa `ejecutar_consulta` legacy (BD directa).  
- Se usan validaciones modernas (`animal_validator`), pero la persistencia sigue acoplada a Infra en UI.  
- No se realizaron cambios en producción (auditoría documental únicamente).

---

## Inventario de archivos (zona, tipo, observaciones)
| Archivo | Zona | Tipo | Observaciones |
|---------|------|------|---------------|
| src/modules/animales/registro_animal.py | UI | Legacy activo | UI → BD directo; formularios alta/compra; usa `get_db_connection`, `animal_validator`. |
| src/modules/animales/modal_editar_animal.py | UI | Legacy activo | UI → BD; edición; múltiples conexiones directas. |
| src/modules/animales/modal_reubicar_animal.py | UI | Legacy activo | UI → BD; reubicación; usa conexiones directas. |
| src/modules/animales/reubicacion.py | UI | Legacy activo | UI → BD; reubicar y llamar `reubicar_animal` legacy. |
| src/modules/animales/ficha_animal.py | UI | Legacy activo | UI → BD (`get_db_connection`, `reubicar_animal`); consulta/edición; integra bitácora. |
| src/modules/animales/bitacora_comentarios.py | UI | Legacy activo | UI → BD; bitácora de comentarios; lectura/escritura directa. |
| src/modules/animales/bitacora_reubicaciones.py | UI | Legacy activo | UI → BD; histórico de reubicaciones. |
| src/modules/animales/bitacora_historial_reubicaciones.py | UI | Legacy activo | UI → BD; histórico extendido. |
| src/modules/animales/ventana_graficas.py | UI | Legacy activo | UI → BD; genera gráficas con consultas directas. |
| src/modules/animales/inventario_v2.py | UI | Legacy activo | UI → BD; búsquedas, detección de columnas; consultas directas. |
| src/modules/animales/inventario_rapido.py | UI | Legacy activo | UI → BD; inventario liviano; conexiones directas. |
| src/modules/animales/realizar_inventario.py | UI | Legacy activo | UI → BD; flujo de inventario; conexiones directas. |
| src/modules/animales/actualizacion_inventario.py | UI | Legacy activo | UI → BD; actualiza stock; conexiones directas. |
| src/modules/animales/importar_excel.py | UI | Legacy activo | UI → BD; importación Excel; conexiones directas. |
| src/modules/animales/__init__.py | UI | Legacy residual | Re-exporta `get_db_connection`; mantiene acoplamiento para consumidores. |
| src/modules/animales/service.py | Dominio/Infra mixto | Legacy activo | CRUD de animales usando `ejecutar_consulta` (database.database); lógica de negocio + SQL en el mismo módulo. |
| src/modules/animales/modal_ver_animal.py | UI | Legacy activo | UI → BD; lectura detallada; conexiones directas. |

---

## Legacy identificado
- **Acceso directo a BD desde UI (UI→Infra):** todos los archivos UI listados (15) usan `get_db_connection` o funciones de `database.database`. **Tipo:** 🟧 Legacy activo congelado (consumidores en producción, no tocar hasta encapsular).  
- **Re-exports legacy en UI:** `src/modules/animales/__init__.py` expone helpers BD. **Tipo:** 🧊 Legacy residual (evitar nuevos usos).  
- **Lógica de negocio + SQL acoplada:** `src/modules/animales/service.py` combina validación mínima con SQL crudo vía `ejecutar_consulta`. **Tipo:** 🟥 Legacy crítico (punto único de dominio que debería encapsularse primero).  
- **Validaciones:** UI usa `modules.utils.validators.animal_validator` (moderno); **no** se detectó uso de `modules.utils.validaciones` en Animales.  
- **Helpers históricos:** detección de columnas vía `PRAGMA`, uso de `sys.path` hacks en varios archivos; conservador para compatibilidad.

---

## Flujos críticos mapeados
| Flujo | Punto de entrada (UI) | Lógica intermedia | Persistencia | Dependencias externas |
|-------|-----------------------|-------------------|--------------|-----------------------|
| Alta de animal | `registro_animal.py` (pestañas nacimiento/compra) | Validación UI + `animal_validator` | Insert directo en BD (UI); también `service.crear_animal` disponible | customtkinter, validators, database (directo) |
| Edición/actualización | `modal_editar_animal.py`, `ficha_animal.py` | Validación mínima UI | Update directo en BD | customtkinter, database (directo) |
| Eliminación | `modal_editar_animal.py` (acciones), `service.eliminar_animal` | Lógica UI + llamada directa | Delete directo en BD | database (directo) |
| Reubicación / Movimientos | `modal_reubicar_animal.py`, `reubicacion.py`, `service.registrar_movimiento` | UI invoca SQL directo / helper `reubicar_animal` (legacy) | Update/insert movimiento en BD | database (directo), reubicar_animal legacy |
| Pesajes | `ficha_animal.py` (tab pesos), `service.registrar_peso` | UI recoge datos; service aplica UPSERT | Insert/Update en tabla `peso` | database (directo) |
| Eventos sanitarios / Tratamientos | `ficha_animal.py` (tab tratamientos), `bitacora_comentarios.py` (comentarios) | UI gestiona formularios | Select/Insert/Update directos | database (directo), tkinter dialogs |
| Inventario/listados | `inventario_v2.py`, `inventario_rapido.py`, `realizar_inventario.py`, `actualizacion_inventario.py`, `ventana_graficas.py` | Lógica UI (filtros, detección columnas) | Select directos, algunos PRAGMA | database (directo) |
| Importación Excel | `importar_excel.py` | Parsing Excel en UI | Insert directo en BD | openpyxl, database (directo) |
| Bitácoras | `bitacora_comentarios.py`, `bitacora_reubicaciones.py`, `bitacora_historial_reubicaciones.py` | UI arma queries y tablas | Select/Insert/Update directos | database (directo) |

---

## Matriz de riesgo
| Elemento / Archivo | Riesgo | Motivo |
|--------------------|--------|--------|
| `service.py` (CRUD/SQL) | 🔥 Alto | Punto único de dominio con SQL crudo y sin capa de repositorio; cambios rompen múltiples flujos. |
| `registro_animal.py` (alta) | 🔥 Alto | UI escribe múltiples tablas y caminos (nacimiento/compra); alto acoplamiento UI→BD. |
| `modal_reubicar_animal.py` / `reubicacion.py` | 🔥 Alto | Movimientos y reubicaciones impactan integridad de datos; UI → BD directo. |
| `ficha_animal.py` | 🔥 Alto | Lectura/escritura múltiple (pesos, tratamientos, bitácora); acoplamiento fuerte. |
| `inventario_v2.py` / `realizar_inventario.py` | ⚠️ Medio | Lecturas intensivas; menos escritura, pero UI→BD directo. |
| `importar_excel.py` | ⚠️ Medio | Inserciones masivas; riesgo de datos inconsistentes; acoplamiento UI→BD. |
| `bitacora_*` | ⚠️ Medio | Lectura/escritura comentarios e históricos; afecta trazabilidad. |
| `__init__.py` (re-export) | 🧊 Bajo | Residual; mantiene compatibilidad pero favorece acoplamiento. |

---

## Diagnóstico arquitectónico
- **Archivos que violan fronteras:** 15 UI con UI→BD directo + 1 dominio mixto (`service.py`) → **16 violaciones** categorizadas (sin tocar código).  
- **Mayor acoplamiento:** Formularios UI (registro, reubicación, ficha, inventarios) que combinan lógica, validación y SQL en la misma clase/frame.  
- **Partes que NO deben tocarse en FASE 8.2:**  
  - Firma pública de `service.py` (consumidores potenciales).  
  - Flujos de alta/compra en `registro_animal.py` (críticos en producción).  
  - Bitácoras (`bitacora_*`) por impacto en auditoría de datos.  
- **Candidatos a encapsular primero:**  
  - `service.py` → extraer repositorio/servicio de dominio (único punto de verdad para CRUD).  
  - Conexión BD en formularios de registro y reubicación (alta/movimientos) → encapsular en servicios/puertos.  
  - Lecturas masivas de inventario (`inventario_v2.py`) → usar gateway de consulta.  

---

## Recomendaciones para FASE 8.2 (Encapsulación)
1. **Crear repositorio de Animales** (Infra): exponga métodos `crear/actualizar/eliminar/obtener/listar`, absorbiendo SQL de `service.py` y llamadas UI.
2. **Servicio de casos de uso de Movimientos/Reubicación**: encapsular `reubicar_animal` y registros de `movimiento`/`peso`/tratamientos con reglas de negocio explícitas.
3. **Gateway de consulta de inventario**: API de lectura optimizada para `inventario_v2` y `ventana_graficas`, eliminando PRAGMA ad-hoc en UI.
4. **Wrapper de importación**: aislar inserciones de `importar_excel.py` detrás de un servicio de importación validado.
5. **Plan de migración gradual**: UI pasa a depender de servicios/puertos, manteniendo API actual hasta completar migración.

---

## Declaración de no cambios
- No se modificó ningún archivo de código ni configuración.  
- Auditoría realizada únicamente por inspección y lectura de código existente.
