"""
SaludLegacyAdapter — FASE 8.6.2 (Scaffold Only)

Mantiene firmas legacy (por nombre de finca) y prepara variantes por ID.
No altera `SaludService` ni cambia comportamiento actual.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class SaludLegacyAdapter:
    def __init__(self, service: Any) -> None:
        self._service = service

    def cargar_animales_por_finca_legacy(self, finca_nombre: str) -> List[Dict[str, Any]]:
        """@legacy_alias
        Delegación directa a la firma actual basada en nombre.
        """
        if hasattr(self._service, "cargar_animales_por_finca"):
            return self._service.cargar_animales_por_finca(finca_nombre)  # type: ignore[attr-defined]
        raise NotImplementedError("El service actual no expone 'cargar_animales_por_finca' por nombre")

    def cargar_animales_por_finca_id(self, finca_id: Optional[int]) -> List[Dict[str, Any]]:
        """@contrato_oficial
        Variante normalizada por ID — implementación pendiente de FASE 8.6.3+.
        """
        raise NotImplementedError("Pendiente implementar variante *_id en el service real (FASE 8.6.3+)")

    def cargar_fincas(self) -> List[Dict[str, Any]]:
        if hasattr(self._service, "cargar_fincas"):
            return self._service.cargar_fincas()  # type: ignore[attr-defined]
        raise NotImplementedError("El service actual no expone 'cargar_fincas'")
