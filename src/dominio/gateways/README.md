# Gateways de Catálogos (Scaffold)

Define contrato `CatalogosGateway` para centralizar catálogos comunes.
No se implementa la centralización aún; se provee `DefaultCatalogosGateway`
como stub que será reemplazado/inyectado en FASE 8.6.3+.

Proveedores actuales (por Service):
- Animales: `cargar_fincas()`
- Reproducción: `cargar_fincas()`
- Salud: `cargar_fincas()`

Meta: reducir duplicación (ej. `cargar_fincas()` 3 veces) y
consistencia de estados/tipos desde catálogos dinámicos.
