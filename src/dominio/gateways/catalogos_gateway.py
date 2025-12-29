"""
Catalogos Gateway (Contrato + Stub) — FASE 8.6.2

Interface conceptual para centralizar catálogos compartidos entre dominios.
No centraliza implementación aún; únicamente define contrato y stub.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class CatalogosGateway(Protocol):
    """Contrato conceptual de catálogos compartidos.

    - listar_fincas(): lista fincas activas
    - listar_estados_por_dominio(dominio): estados válidos del dominio
    - listar_tipos(dominio): tipos válidos (p. ej., tratamientos)
    """

    def listar_fincas(self) -> List[Dict[str, object]]: ...

    def listar_estados_por_dominio(self, dominio: str) -> List[Dict[str, object]]: ...

    def listar_tipos(self, dominio: str) -> List[Dict[str, object]]: ...


class DefaultCatalogosGateway:
    """Stub de gateway.

    Documentación de proveedores actuales:
    - Animales: `AnimalService.cargar_fincas()`
    - Reproducción: `ReproduccionService.cargar_fincas()`
    - Salud: `SaludService.cargar_fincas()`

    FASE 8.6.3+: los Services delegarán aquí gradualmente.
    """

    def listar_fincas(self) -> List[Dict[str, object]]:  # pragma: no cover - stub
        raise NotImplementedError("Proveedor real pendiente (FASE 8.6.3+)")

    def listar_estados_por_dominio(self, dominio: str) -> List[Dict[str, object]]:  # pragma: no cover - stub
        raise NotImplementedError("Proveedor real pendiente (FASE 8.6.3+)")

    def listar_tipos(self, dominio: str) -> List[Dict[str, object]]:  # pragma: no cover - stub
        raise NotImplementedError("Proveedor real pendiente (FASE 8.6.3+)")


__all__ = ["CatalogosGateway", "DefaultCatalogosGateway"]
