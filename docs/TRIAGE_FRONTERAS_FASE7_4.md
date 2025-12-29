# TRIAGE DE FRONTERAS (FASE 7.4)

**Proyecto:** FincaFácil v2.0 — ERP Ganadero  
**Fecha:** 18 de diciembre de 2025  
**Estado:** Informe de triage (sin refactor)  
**Fuente:** REPORT_FRONTERAS.md generado por tools/auditar_fronteras.py

Criterios de categoría:
- 🟥 CRÍTICA REAL: Rompe frontera deseada y debe priorizarse en refactor futuro.
- 🟧 LEGACY CONGELADO: Patrón heredado estabilizado; no tocar sin fase específica.
- 🟨 EXCEPCIÓN ACEPTABLE: Justificada por bootstrap/framework; documentar.
- 🟩 FALSO POSITIVO: Error del auditor; ajustar regla en fase posterior.

## Tabla de violaciones

| Archivo | Tipo de violación | Zona origen → destino | Categoría | Justificación técnica (1–3 líneas) | Acción futura sugerida |
|---------|-------------------|-----------------------|-----------|------------------------------------|------------------------|
| main.py | UI usa BD directa (inicialización) | UI → Infra | 🟨 | Bootstrap hace sanity-check de BD antes de lanzar UI; acoplamiento histórico. | Extraer a servicio de arranque/infra; dejar como está hasta plan de init. |
| main.py | UI usa BD directa (inicialización) | UI → Infra | 🟨 | Verificación de BD se hace en capa UI por legado. | Igual que anterior; mover a helper de infraestructura de inicio. |
| main.py | UI usa BD directa (inicialización) | UI → Infra | 🟨 | Asegurar esquema mínimo desde UI. | Centralizar en módulo infra de setup; no urgente. |
| main.py | UI usa BD directa (inicialización) | UI → Infra | 🟨 | Asegurar esquema completo desde UI. | Idem; mover a pipeline de init controlado. |
| main.py | UI lee path BD | UI → Infra | 🟨 | Consulta DB_PATH para rutas; acoplamiento de arranque. | Encapsular en config/infra; mantener hasta fase de arranque. |
| modules/ajustes/ajustes_main.py | UI usa get_db_connection | UI → Infra | 🟧 | Pantalla de ajustes opera directo sobre BD por diseño legado. | Refactor a repositorios/servicios; plan gradual. |
| src/main.py | UI usa BD directa (inicialización) | UI → Infra | 🟨 | Duplicado del bootstrap principal en src. | Unificar bootstrap en infra; no tocar ahora. |
| src/main.py | UI usa BD directa (inicialización) | UI → Infra | 🟨 | Verificación BD desde UI. | Igual que anterior. |
| src/main.py | UI usa BD directa (inicialización) | UI → Infra | 🟨 | Asegurar esquema mínimo desde UI. | Igual que anterior. |
| src/main.py | UI usa BD directa (inicialización) | UI → Infra | 🟨 | Asegurar esquema completo desde UI. | Igual que anterior. |
| src/main.py | UI lee path BD | UI → Infra | 🟨 | Consulta DB_PATH; bootstrap legacy. | Igual que anterior. |
| src/modules/ajustes/ajustes_main.py | UI usa get_db_connection | UI → Infra | 🟧 | Pantalla ajustes en src acoplada a BD. | Refactor a repositorio; requerirá fase dedicada. |
| src/modules/ajustes/ajustes_main.py | UI lee path BD | UI → Infra | 🟧 | Usa path seguro de BD en UI. | Encapsular en servicio de configuración; plan gradual. |
| src/modules/ajustes/ajustes_main.py | UI lee path BD | UI → Infra | 🟧 | Repetición del acceso a path BD. | Igual que anterior. |
| src/modules/animales/__init__.py | UI usa get_db_connection | UI → Infra | 🟧 | Init de módulo UI depende de BD legacy. | Retirar dependencia en init; mover a servicios. |
| src/modules/animales/actualizacion_inventario.py | UI usa db | UI → Infra | 🟧 | Pantalla actualiza inventario directo en BD. | Introducir servicio/inventario_repo; legado por ahora. |
| src/modules/animales/bitacora_comentarios.py | UI usa get_db_connection | UI → Infra | 🟧 | Formulario bitácora accede BD directa. | Encapsular en repo; fase futura. |
| src/modules/animales/bitacora_comentarios.py | UI usa db | UI → Infra | 🟧 | Combina db global en UI. | Igual que anterior. |
| src/modules/animales/bitacora_historial_reubicaciones.py | UI usa get_db_connection | UI → Infra | 🟧 | Historial reubicaciones consulta BD directa. | Mover a servicio de historial. |
| src/modules/animales/bitacora_reubicaciones.py | UI usa db | UI → Infra | 🟧 | UI escribe bitácora con db global. | Igual que anterior. |
| src/modules/animales/ficha_animal.py | UI usa get_db_connection | UI → Infra | 🟧 | Ficha animal consulta BD directa. | Crear capa repo/servicio; legado estable. |
| src/modules/animales/ficha_animal.py | UI llama reubicar_animal | UI → Infra | 🟧 | UI invoca operación de BD directamente. | Encapsular en caso de uso; plan futuro. |
| src/modules/animales/importar_excel.py | UI usa db | UI → Infra | 🟧 | Import UI inserta directo en BD. | Derivar a servicio de importación. |
| src/modules/animales/inventario_v2.py | UI usa get_db_connection | UI → Infra | 🟧 | Inventario UI abre conexión directa. | Migrar a servicio de inventario. |
| src/modules/animales/inventario_v2.py | UI usa get_db_connection | UI → Infra | 🟧 | Duplicado con módulo legacy. | Igual que anterior. |
| src/modules/animales/modal_editar_animal.py | UI usa get_db_connection | UI → Infra | 🟧 | Modal edita animal contra BD directa. | Encapsular en caso de uso/servicio. |
| src/modules/animales/modal_editar_animal.py | UI usa get_db_connection | UI → Infra | 🟧 | Segundo import a BD. | Igual que anterior. |
| src/modules/animales/modal_reubicar_animal.py | UI usa get_db_connection | UI → Infra | 🟧 | Modal reubicar accede BD. | Encapsular en servicio de reubicación. |
| src/modules/animales/modal_reubicar_animal.py | UI usa get_db_connection | UI → Infra | 🟧 | Duplicado. | Igual que anterior. |
| src/modules/animales/realizar_inventario.py | UI usa get_db_connection | UI → Infra | 🟧 | Flujo UI abre conexión. | Mover a servicio. |
| src/modules/animales/realizar_inventario.py | UI usa get_db_connection | UI → Infra | 🟧 | Duplicado. | Igual. |
| src/modules/animales/registro_animal.py | UI usa get_db_connection | UI → Infra | 🟧 | Registro animal escribe BD directa. | Encapsular en caso de uso. |
| src/modules/animales/reubicacion.py | UI usa get_db_connection | UI → Infra | 🟧 | Reubicación UI abre conexión. | Encapsular en servicio. |
| src/modules/animales/reubicacion.py | UI llama reubicar_animal | UI → Infra | 🟧 | UI invoca operación infra. | Igual. |
| src/modules/animales/ventana_graficas.py | UI usa get_db_connection | UI → Infra | 🟧 | Gráficas obtienen datos directo. | Exponer servicio de consultas. |
| src/modules/animales/ventana_graficas.py | UI usa get_db_connection | UI → Infra | 🟧 | Duplicado. | Igual. |
| src/modules/configuracion/calidad_animal.py | UI usa db | UI → Infra | 🟧 | Catálogos config leen/escriben BD desde UI. | Refactor a repositorios de configuración. |
| src/modules/configuracion/causa_muerte.py | UI usa db | UI → Infra | 🟧 | Igual patrón de catálogos. | Idem. |
| src/modules/configuracion/condiciones_corporales.py | UI usa db | UI → Infra | 🟧 | Igual patrón. | Idem. |
| src/modules/configuracion/destino_venta.py | UI usa db | UI → Infra | 🟧 | Igual patrón. | Idem. |
| src/modules/configuracion/diagnosticos.py | UI usa db | UI → Infra | 🟧 | Igual patrón. | Idem. |
| src/modules/configuracion/empleados.py | UI usa get_db_connection | UI → Infra | 🟧 | Form UI accede BD. | Encapsular en repo/servicio. |
| src/modules/configuracion/empleados.py | UI usa db | UI → Infra | 🟧 | Usa instancia db global. | Idem. |
| src/modules/configuracion/empleados.py | UI lee DB_PATH | UI → Infra | 🟧 | Accede path BD desde UI. | Encapsular path en config/infra. |
| src/modules/configuracion/fincas.py | UI usa db | UI → Infra | 🟧 | Catálogo finca en UI. | Refactor a repo. |
| src/modules/configuracion/lotes.py | UI usa db | UI → Infra | 🟧 | Catálogo lote en UI. | Idem. |
| src/modules/configuracion/motivos_venta.py | UI usa db | UI → Infra | 🟧 | Catálogo motivos en UI. | Idem. |
| src/modules/configuracion/potreros.py | UI usa db | UI → Infra | 🟧 | Catálogo potreros en UI. | Idem. |
| src/modules/configuracion/procedencia.py | UI usa db | UI → Infra | 🟧 | Catálogo procedencia en UI. | Idem. |
| src/modules/configuracion/proveedores.py | UI usa db | UI → Infra | 🟧 | Catálogo proveedores en UI. | Idem. |
| src/modules/configuracion/razas.py | UI usa db | UI → Infra | 🟧 | Catálogo razas en UI. | Idem. |
| src/modules/configuracion/sectores.py | UI usa db | UI → Infra | 🟧 | Catálogo sectores en UI. | Idem. |
| src/modules/configuracion/tipo_explotacion.py | UI usa db | UI → Infra | 🟧 | Catálogo tipo explotación. | Idem. |
| src/modules/dashboard/dashboard_main.py | UI usa get_db_connection | UI → Infra | 🟧 | Dashboard UI lee BD directa. | Encapsular en servicio de reportes. |
| src/modules/herramientas/herramientas_main.py | UI usa db | UI → Infra | 🟧 | UI herramientas acoplada a BD. | Refactor a repo. |
| src/modules/insumos/insumos_main.py | UI usa db | UI → Infra | 🟧 | UI insumos acoplada a BD. | Refactor a repo. |
| src/modules/leche/pesaje_leche.py | UI usa get_db_connection | UI → Infra | 🟧 | UI pesaje abre conexión. | Encapsular en servicio de leche. |
| src/modules/nomina/nomina_main.py | UI usa db | UI → Infra | 🟧 | UI nómina usa db directa. | Refactor a servicio. |
| src/modules/potreros/potreros_main.py | UI usa db | UI → Infra | 🟧 | UI potreros usa db. | Refactor a repo. |
| src/modules/reportes/reportes_main.py | UI usa db | UI → Infra | 🟧 | UI reportes usa db. | Encapsular en servicio de reportes. |
| src/modules/reportes/reportes_profesional.py | UI usa db | UI → Infra | 🟧 | UI reportes profesional usa db. | Idem. |
| src/modules/reproduccion/reproduccion_main.py | UI usa get_db_connection | UI → Infra | 🟧 | UI reproducción abre conexión via connection. | Encapsular en servicio. |
| src/modules/salud/salud_main.py | UI usa db | UI → Infra | 🟧 | UI salud acoplada a BD. | Refactor a servicio/puerto. |
| src/modules/ventas/ventas_main.py | UI usa get_db_connection | UI → Infra | 🟧 | UI ventas abre conexión legacy. | Encapsular en repo ventas. |
| src/modules/utils/__init__.py | Re-exporta validaciones legacy | Utils → Legacy | 🟧 | Re-exports mantenidos como red de compatibilidad. | Mantener congelado; plan de retirada cuando 0 consumidores. |
| src/modules/utils/__init__.py | Re-exporta validaciones legacy | Utils → Legacy | 🟧 | Igual anterior. | Idem. |
| src/modules/utils/__init__.py | Re-exporta validaciones legacy | Utils → Legacy | 🟧 | Igual anterior. | Idem. |
| src/modules/utils/__init__.py | Re-exporta validaciones legacy | Utils → Legacy | 🟧 | Igual anterior. | Idem. |
| src/modules/utils/data_filters.py | Utils depende de Infra | Utils → Infra | 🟥 | Helper técnico abre conexiones; rompe frontera utils. | Mover a Infra o exponer interfaz; prioridad alta. |
| src/modules/utils/importador_excel.py | Utils depende de Infra | Utils → Infra | 🟥 | Importador mezcla utilidades con acceso BD. | Trasladar a Infra/servicio de importación. |
| src/modules/utils/license_manager.py | Utils depende de Infra | Utils → Infra | 🟥 | Lee path BD desde utils; debe vivir en Infra o Config. | Reubicar en Infra/Config; reducir acoplamiento. |
| src/modules/utils/notificaciones.py | Utils depende de Infra | Utils → Infra | 🟥 | Notificaciones acceden BD desde utils. | Extraer a servicio de notificaciones en Infra. |
| src/modules/utils/sistema_alertas.py | Utils depende de Infra | Utils → Infra | 🟥 | Sistema de alertas abre conexión. | Reubicar en Infra/servicio dominio. |
| src/modules/utils/units_helper.py | Utils depende de Infra | Utils → Infra | 🟥 | Helper de unidades accede BD; responsabilidad fuera de utils. | Mover a dominio/infra según uso; eliminar acceso directo. |
| src/modules/utils/usuario_manager.py | Utils depende de Infra | Utils → Infra | 🟥 | Manager de usuarios usa path BD en utils. | Trasladar a Infra/autenticación; ajustar dependencias. |
| src/modules/utils/validators.py | Utils depende de Infra | Utils → Infra | 🟨 | Validador moderno consulta BD para reglas; excepción consciente. | Mantener; documentar en contrato; posible refactor a servicio de validación futuro. |

## Resumen por categoría
- 🟥 CRÍTICA REAL: 7
- 🟧 LEGACY CONGELADO: 58
- 🟨 EXCEPCIÓN ACEPTABLE: 11
- 🟩 FALSO POSITIVO: 0

## Conclusiones de Gobierno Arquitectónico
- El grueso de violaciones (58) corresponde a patrón legacy UI→BD directo; requiere fase de refactor por verticales, no abordable en hotfix.
- 7 violaciones en utils hacia Infra son críticas para higiene de capas; son acotadas y prioritarias para la siguiente fase controlada.
- 11 casos marcados como excepciones aceptables pertenecen al bootstrap y al validador moderno; deben ser encapsulados más adelante pero no bloquean.
- No se detectaron falsos positivos; el auditor es coherente con la topología actual.

## Recomendaciones para FASE 7.5 / FASE 8
1. Priorizar las 7 🟥 (utils→Infra) con un refactor dirigido, moviendo lógica a Infra/servicios y dejando shims mínimos si es necesario.
2. Diseñar un plan de migración progresiva para los 58 🟧 UI→BD: abordar por dominio (animales, configuración, reportes) creando repositorios/casos de uso.
3. Encapsular el bootstrap (11 🟨) en un módulo de inicio de Infra para reducir acoplamiento de main.
4. Mantener actualizado el auditor: si se retiran dependencias legacy, ajustar reglas para prevenir regresiones.
5. Documentar cualquier excepción nueva en ENFORCEMENT_FASE7_3.md y actualizar este triage tras cada lote de refactor.
