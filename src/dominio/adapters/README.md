# Legacy Adapters (Scaffold)

Objetivo: permitir adopción gradual de contratos normalizados manteniendo
compatibilidad con firmas legacy.

- No se modifica ningún Service existente.
- Los adapters delegan 100% al Service actual o levantan `NotImplementedError`
  cuando se requiere una traducción nombre→id pendiente para FASE 8.6.3+.
- Etiquetas:
  - @legacy_alias: firma antigua que se mantiene activa
  - @contrato_oficial: firma normalizada por ID
  - @deprecable_futuro: candidata a eliminación cuando la UI migre

Archivos:
- animales_legacy_adapter.py
- reproduccion_legacy_adapter.py
- salud_legacy_adapter.py
