"""LEGACY/FROZEN - service.py

Punto de entrada legacy para operaciones de animales. Mantiene la API pública
existente y delega internamente a la nueva capa de dominio/infraestructura
(`AnimalService` + `AnimalRepository`).
"""
from typing import Optional, List, Dict, Any

from infraestructura.animales import AnimalRepository, AnimalService


# Singleton para mantener compatibilidad y permitir inyección en tests
_service = AnimalService(AnimalRepository())


def crear_animal(data: Dict[str, Any]) -> None:
    """Crea un animal (delegado en AnimalService)."""
    _service.registrar_animal(data)


def actualizar_animal(animal_id: int, cambios: Dict[str, Any]) -> None:
    """Actualiza columnas específicas del animal."""
    _service.actualizar_animal(animal_id, cambios)


def eliminar_animal(animal_id: int) -> None:
    """Elimina un animal por id."""
    _service.eliminar_animal(animal_id)


def obtener_animal_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """Devuelve un animal por su código."""
    return _service.obtener_animal_por_codigo(codigo)


def listar_animales(filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Lista animales con filtros opcionales."""
    return _service.listar_animales(filtros)


def registrar_peso(animal_id: int, fecha: str, peso: float, metodo: Optional[str] = None, observaciones: Optional[str] = None) -> None:
    """Registra o actualiza un pesaje para un animal en una fecha."""
    _service.registrar_peso(animal_id, fecha, peso, metodo, observaciones)


def registrar_movimiento(animal_id: int, lote_destino_id: int, fecha_movimiento: str, tipo_movimiento: str = "Traslado", lote_origen_id: Optional[int] = None, motivo: Optional[str] = None, observaciones: Optional[str] = None) -> None:
    """Registra un movimiento en la tabla movimiento."""
    _service.registrar_movimiento(
        animal_id,
        lote_destino_id,
        fecha_movimiento,
        tipo_movimiento,
        lote_origen_id,
        motivo,
        observaciones,
    )
