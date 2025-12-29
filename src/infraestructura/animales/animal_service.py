"""Servicio de dominio para Animales.

Orquesta lógica ligera y delega acceso a datos al repositorio.
No contiene SQL; mantiene compatibilidad con la API legacy.
"""
from typing import Any, Dict, List, Optional

from .animal_repository import AnimalRepository


class AnimalService:
    """Servicio de dominio que opera sobre el repositorio de animales."""

    def __init__(self, repository: Optional[AnimalRepository] = None) -> None:
        self._repo = repository or AnimalRepository()

    # API pública equivalente a service.py legacy
    def registrar_animal(self, data: Dict[str, Any]) -> None:
        codigo = data.get("codigo")
        if not codigo:
            raise ValueError("El campo 'codigo' es obligatorio")

        sexo = data.get("sexo")
        if sexo not in ("Macho", "Hembra", None, ""):
            raise ValueError("El campo 'sexo' debe ser 'Macho' o 'Hembra'")

        if self._repo.existe_codigo(codigo):
            raise ValueError(f"Ya existe un animal con código '{codigo}'")

        self._repo.crear(data)

    def actualizar_animal(self, animal_id: int, cambios: Dict[str, Any]) -> None:
        if not cambios:
            return
        self._repo.actualizar(animal_id, cambios)

    def eliminar_animal(self, animal_id: int) -> None:
        self._repo.eliminar(animal_id)

    def obtener_animal_por_codigo(self, codigo: str):
        return self._repo.obtener_por_codigo(codigo)

    def listar_animales(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return self._repo.listar(filtros)

    def registrar_peso(
        self,
        animal_id: int,
        fecha: str,
        peso: float,
        metodo: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> None:
        self._repo.registrar_peso(animal_id, fecha, peso, metodo, observaciones)

    def registrar_movimiento(
        self,
        animal_id: int,
        lote_destino_id: int,
        fecha_movimiento: str,
        tipo_movimiento: str = "Traslado",
        lote_origen_id: Optional[int] = None,
        motivo: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> None:
        self._repo.registrar_movimiento(
            animal_id,
            lote_destino_id,
            fecha_movimiento,
            tipo_movimiento,
            lote_origen_id,
            motivo,
            observaciones,
        )

    # ==================== LECTURA PARA UI: Catálogos ====================
    # Estos métodos permiten que la UI cargue dropdowns sin conocer BD

    def cargar_fincas(self) -> List[Dict[str, Any]]:
        """Cargar lista de fincas activas para dropdown."""
        return self._repo.listar_fincas()

    def cargar_razas(self) -> List[Dict[str, Any]]:
        """Cargar lista de razas activas para dropdown."""
        return self._repo.listar_razas()

    def cargar_condiciones_corporales(self) -> List[Dict[str, Any]]:
        """Cargar lista de condiciones corporales."""
        return self._repo.listar_condiciones_corporales()

    def cargar_potreros_por_finca(self, finca_id: int) -> List[Dict[str, Any]]:
        """Cargar potreros de una finca."""
        return self._repo.listar_potreros_por_finca(finca_id)

    def cargar_lotes_por_finca(self, finca_id: int) -> List[Dict[str, Any]]:
        """Cargar lotes de una finca."""
        return self._repo.listar_lotes_por_finca(finca_id)

    def cargar_sectores_por_finca(self, finca_id: int) -> List[Dict[str, Any]]:
        """Cargar sectores de una finca."""
        return self._repo.listar_sectores_por_finca(finca_id)

    def cargar_madres_por_finca(self, finca_id: int) -> List[Dict[str, Any]]:
        """Cargar hembras disponibles como madres."""
        return self._repo.listar_animales_por_finca_y_sexo(finca_id, "Hembra")

    def cargar_padres_por_finca(self, finca_id: int) -> List[Dict[str, Any]]:
        """Cargar machos disponibles como padres."""
        return self._repo.listar_animales_por_finca_y_sexo(finca_id, "Macho")

    def cargar_procedencias(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Cargar procedencias para dropdown."""
        return self._repo.listar_procedencias(finca_id)

    def cargar_vendedores(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Cargar vendedores para dropdown."""
        return self._repo.listar_vendedores(finca_id)

    def cargar_calidades(self) -> List[Dict[str, Any]]:
        """Cargar calidades desde catálogo calidad_animal."""
        return self._repo.listar_calidades()

    def cargar_estados_salud(self) -> List[str]:
        """Cargar valores distintos de salud desde animal."""
        return self._repo.listar_estados_salud_distintos()

    def cargar_estados(self) -> List[str]:
        """Cargar valores distintos de estado desde animal."""
        return self._repo.listar_estados_distintos()
