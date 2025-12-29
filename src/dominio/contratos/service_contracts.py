"""
FASE 8.6.2 — Contratos de Service (Scaffold)

Este módulo define interfaces conceptuales (typing.Protocol) para los servicios
existentes sin imponer herencia ni romper compatibilidad. No modifica
implementaciones ni firmas públicas actuales. Sirve como guía operativa para
refactors futuros (FASE 8.6.3+).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


# Convenciones globales de naming (aplican a todos los contratos):
# - listar_*: colecciones (puede aceptar filtros y límite)
# - obtener_*: entidad única por ID
# - registrar_*: creación
# - actualizar_*: modificación parcial/total
# - marcar_*: cambio de estado discreto
# - cargar_*: catálogos (listas de selección)
# - validar_*: reglas de negocio testeables
# Parámetros: Preferir IDs (int). Filtro por finca: finca_id: Optional[int].
# Fechas: str en formato ISO "YYYY-MM-DD". Payloads complejos: Dict[str, Any].
# Errores esperados (contrato, no implementados aún):
#   EntidadNoExisteError, EstadoInvalidoError, ViolacionIntegridadError,
#   ParametroInvalidoError, OperacionNoPermitidaError.


@runtime_checkable
class AnimalServiceContract(Protocol):
    """Contrato conceptual para `AnimalService`.

    Notas:
    - No impone herencia; es guía de compatibilidad y naming.
    - Filtros por finca deben normalizarse a `finca_id: Optional[int]`.
    - La UI nunca debe implementar validaciones; el Service valida y lanza
      errores de dominio (por ahora `ValueError`, futuro: errores tipados).
    """

    # Escritura
    def registrar_animal(self, data: Dict[str, Any]) -> None: ...
    def actualizar_animal(self, animal_id: int, cambios: Dict[str, Any]) -> None: ...
    def eliminar_animal(self, animal_id: int) -> None: ...

    # Lectura
    def obtener_animal_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]: ...
    def listar_animales(
        self,
        finca_id: Optional[int] = None,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]: ...

    # Operaciones dominio
    def registrar_peso(self, animal_id: int, fecha: str, peso: float) -> None: ...
    def registrar_movimiento(self, animal_id: int, data: Dict[str, Any]) -> None: ...

    # Catálogos (ejemplos representativos; pueden existir más específicos)
    def cargar_fincas(self) -> List[Dict[str, Any]]: ...
    def cargar_animales(self) -> List[Dict[str, Any]]: ...


@runtime_checkable
class ReproduccionServiceContract(Protocol):
    """Contrato conceptual para `ReproduccionService`.

    Incluye validaciones explícitas y cálculos temporales.
    Filtros por finca normalizados a `finca_id: Optional[int]`.
    """

    # Validaciones
    def validar_hembra_gestante(self, hembra_id: int) -> bool: ...
    def validar_servicio_duplicado(self, hembra_id: int, fecha: str) -> bool: ...

    # Escritura
    def registrar_servicio(self, data: Dict[str, Any]) -> None: ...
    def registrar_parto(self, data: Dict[str, Any]) -> None: ...
    def marcar_servicio_vacio(self, servicio_id: int) -> None: ...

    # Lectura
    def listar_gestantes(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]: ...
    def listar_proximos_partos(self, dias: int = 30) -> List[Dict[str, Any]]: ...

    # Catálogos
    def cargar_fincas(self) -> List[Dict[str, Any]]: ...
    def cargar_hembras(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]: ...
    def cargar_machos(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]: ...

    # Estadísticas
    def obtener_estadisticas_badges(self) -> Dict[str, int]: ...


@runtime_checkable
class SaludServiceContract(Protocol):
    """Contrato conceptual para `SaludService`.

    Estados y tipos deben provenir de catálogos (no hardcoded) en el futuro.
    Filtros por finca normalizados a `finca_id: Optional[int]`.
    """

    # Diagnósticos
    def registrar_diagnostico(self, data: Dict[str, Any]) -> None: ...
    def obtener_historial_diagnosticos(self, limite: int = 100) -> List[Dict[str, Any]]: ...
    def obtener_detalle_diagnostico(self, diagnostico_id: int) -> Optional[Dict[str, Any]]: ...
    def actualizar_estado_diagnostico(self, diagnostico_id: int, nuevo_estado: str) -> None: ...
    def obtener_estadisticas_diagnosticos(self) -> Dict[str, int]: ...

    # Tratamientos
    def registrar_tratamiento(self, data: Dict[str, Any]) -> None: ...
    def obtener_historial_tratamientos(self, limite: int = 100) -> List[Dict[str, Any]]: ...
    def obtener_proximos_tratamientos(self, limite: int = 20) -> List[Dict[str, Any]]: ...
    def obtener_detalle_tratamiento(self, tratamiento_id: int) -> Optional[Dict[str, Any]]: ...
    def obtener_estadisticas_tratamientos(self) -> Dict[str, int]: ...

    # Catálogos
    def cargar_fincas(self) -> List[Dict[str, Any]]: ...
    def cargar_animales(self) -> List[Dict[str, Any]]: ...


__all__ = [
    "AnimalServiceContract",
    "ReproduccionServiceContract",
    "SaludServiceContract",
]
