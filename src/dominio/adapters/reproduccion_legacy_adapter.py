"""
ReproduccionLegacyAdapter — FASE 8.6.2 (Scaffold Only)

Proporciona aliases legacy y prepara traducción de `finca_nombre` → `finca_id`.
No modifica `ReproduccionService` ni firmas públicas actuales.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class ReproduccionLegacyAdapter:
    def __init__(self, service: Any) -> None:
        self._service = service

    def cargar_hembras_legacy(self, finca_nombre: str) -> List[Dict[str, Any]]:
        """@legacy_alias
        Placeholder para traducir nombre→id en FASE 8.6.3+. Por ahora, no delega
        porque el service espera `finca_id`.
        """
        raise NotImplementedError("Traducción finca_nombre→finca_id pendiente (FASE 8.6.3+)")

    def cargar_hembras(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """@contrato_oficial
        Delegación directa si el método existe en el service real.
        """
        if hasattr(self._service, "cargar_hembras"):
            return self._service.cargar_hembras(finca_id)  # type: ignore[attr-defined]
        raise NotImplementedError("El service actual no expone 'cargar_hembras' por ID")

    def cargar_fincas(self) -> List[Dict[str, Any]]:
        if hasattr(self._service, "cargar_fincas"):
            return self._service.cargar_fincas()  # type: ignore[attr-defined]
        raise NotImplementedError("El service actual no expone 'cargar_fincas'")
