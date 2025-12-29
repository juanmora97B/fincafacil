"""
AnimalesLegacyAdapter — FASE 8.6.2 (Scaffold Only)

Objetivo: proveer aliases y traducciones de parámetros legacy sin romper
compatibilidad. No modifica `AnimalService` ni su comportamiento actual.

Uso esperado (FASE 8.6.3+):
- Adoptar métodos normalizados por ID manteniendo aliases legacy.
- Este adapter delega 100% al service real.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class AnimalesLegacyAdapter:
    def __init__(self, service: Any) -> None:
        """Recibe una instancia del service real (AnimalService).
        No realiza import directo para evitar acoplamiento.
        """
        self._service = service

    # Ejemplo de alias legacy que hoy usa nombre de finca.
    # Futuro: resolver `finca_id` a partir de `finca_nombre` y delegar a variante *_id.
    def cargar_potreros_por_finca_legacy(self, finca_nombre: str) -> List[Dict[str, Any]]:
        """@legacy_alias
        Mantiene firma por nombre. Delegación directa si el service la soporta.
        """
        if hasattr(self._service, "cargar_potreros_por_finca"):
            return self._service.cargar_potreros_por_finca(finca_nombre)  # type: ignore[attr-defined]
        raise NotImplementedError("El service actual no expone 'cargar_potreros_por_finca' por nombre")

    def cargar_potreros_por_finca_id(self, finca_id: Optional[int]) -> List[Dict[str, Any]]:
        """@contrato_oficial
        Variante normalizada por ID. Delegación condicional.
        """
        if hasattr(self._service, "cargar_potreros_por_finca"):
            # Si el service ya acepta ID, delegar; si no, implementar mapeo en 8.6.3+
            return self._service.cargar_potreros_por_finca(finca_id)  # type: ignore[arg-type, attr-defined]
        raise NotImplementedError("Adapter pendiente de mapeo nombre<->id en FASE 8.6.3+")

    # Fachada para catálogo compartido — mantiene nombre existente
    def cargar_fincas(self) -> List[Dict[str, Any]]:
        if hasattr(self._service, "cargar_fincas"):
            return self._service.cargar_fincas()  # type: ignore[attr-defined]
        raise NotImplementedError("El service actual no expone 'cargar_fincas'")
