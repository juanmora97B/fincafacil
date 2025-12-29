# Contratos de Service (Scaffold)

Este directorio define contratos conceptuales para los Services mediante `typing.Protocol` y documentación.

- No impone herencia ni cambios en los Services actuales.
- Sirve para alinear naming, parámetros y responsabilidades.
- Prepara el terreno para refactors controlados en FASE 8.6.3+.

## Puntos clave
- Filtros por ID (p. ej., `finca_id: Optional[int]`).
- `listar_*`, `obtener_*`, `registrar_*`, `actualizar_*`, `marcar_*`, `cargar_*`, `validar_*`.
- Estados/Tipos desde catálogos (no hardcoded) en futuras fases.
- Errores de dominio tipados (documentados, no implementados aquí).

Consulte `service_contracts.py` y `errores_dominio.md` para detalles.
