# INVENTARIO DE CONSUMIDORES DE VALIDACIONES LEGACY (FASE 5.1)

**Fecha:** 17 de diciembre de 2025  
**Ámbito:** Proyecto FincaFácil v2.0  
**Alcance:** Solo análisis pasivo. Sin cambios de código ni refactors.

## Resumen ejecutivo
- Se inspeccionó todo el código fuente buscando usos de wrappers legacy en `modules.utils.validaciones`:
  - `validar_email` (estático y módulo) — marcados **# DEPRECATED**.
  - `validar_telefono` (estático y módulo) — marcados **# DEPRECATED**.
  - `validar_fecha` (estático) — solicitado en alcance aunque no está marcado como deprecado.
- Resultado: **no se encontraron consumidores activos** (ni directos ni vía `modules.utils.__init__`).
- Conclusión operativa: los wrappers legacy analizados están actualmente **muertos/no referenciados**.

## Tabla de consumidores encontrados

| Archivo | Línea aprox. | Tipo de módulo | Función usada | Forma de uso |
|---------|--------------|----------------|---------------|--------------|
| _Sin hallazgos_ | — | — | — | — |

## Clasificación por tipo de módulo
- UI: sin usos detectados.
- Lógica de negocio: sin usos detectados.
- Formularios/Widgets (CustomTkinter): sin usos detectados.
- Legacy/compatibilidad: sin usos detectados fuera del propio módulo `validaciones.py` y del `__init__.py` que solo reexporta.

## Conclusión
- Wrappers revisados (`validar_email`, `validar_telefono`, `validar_fecha`) no tienen consumidores en el repositorio.
- Estado actual: **wrappers muertos**. Se mantienen únicamente por compatibilidad teórica, pero no hay llamadas reales.
- No se ejecutaron cambios ni se modificó código; análisis 100% pasivo.
