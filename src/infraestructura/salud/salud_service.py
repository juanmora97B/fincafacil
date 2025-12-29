"""
SaludService - Capa de lógica de negocio para el dominio Salud
Orquesta operaciones sanitarias: diagnósticos, tratamientos, alertas
"""
from typing import Dict, Any, List, Optional
from .salud_repository import SaludRepository


class SaludService:
    """Service para la lógica de negocio del dominio Salud."""

    def __init__(self):
        """Inicializa el servicio con su repository."""
        self._repo = SaludRepository()

    # ==================== DIAGNÓSTICOS ====================

    def registrar_diagnostico(
        self,
        animal_id: int,
        fecha: str,
        tipo: str,
        detalle: str,
        severidad: str,
        estado: str,
        observaciones: Optional[str] = None
    ) -> None:
        """
        Registra un nuevo diagnóstico veterinario.
        Valida que el animal exista y esté activo antes de insertar.
        """
        # Validación: animal debe existir y estar activo
        if not self._repo.validar_animal_activo(animal_id):
            raise ValueError("El animal seleccionado no existe o no está activo")
        
        # Delegar inserción al repository
        self._repo.insertar_diagnostico(
            animal_id=animal_id,
            fecha=fecha,
            tipo=tipo,
            detalle=detalle,
            severidad=severidad,
            estado=estado,
            observaciones=observaciones
        )

    def obtener_historial_diagnosticos(self, limite: int = 100) -> List[Dict[str, Any]]:
        """Obtiene el historial de diagnósticos."""
        return self._repo.listar_diagnosticos(limite=limite)

    def obtener_detalle_diagnostico(self, diagnostico_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene el detalle completo de un diagnóstico."""
        return self._repo.obtener_diagnostico_por_id(diagnostico_id)

    def actualizar_estado_diagnostico(self, diagnostico_id: int, nuevo_estado: str) -> None:
        """Actualiza el estado de un diagnóstico."""
        # Validar estados permitidos
        estados_validos = ["Activo", "En Tratamiento", "Recuperado", "Crónico"]
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado inválido. Use uno de: {', '.join(estados_validos)}")
        
        self._repo.actualizar_estado_diagnostico(diagnostico_id, nuevo_estado)

    def obtener_estadisticas_diagnosticos(self) -> Dict[str, int]:
        """Obtiene estadísticas de diagnósticos."""
        return {
            'total_activos': self._repo.contar_diagnosticos()
        }

    # ==================== TRATAMIENTOS ====================

    def registrar_tratamiento(
        self,
        animal_id: int,
        fecha_inicio: str,
        tipo_tratamiento: str,
        producto: str,
        dosis: Optional[str] = None,
        veterinario: Optional[str] = None,
        comentario: Optional[str] = None,
        fecha_proxima: Optional[str] = None
    ) -> None:
        """
        Registra un nuevo tratamiento.
        Valida que el animal exista y que el tipo de tratamiento sea válido.
        """
        # Validación: animal debe existir y estar activo
        if not self._repo.validar_animal_activo(animal_id):
            raise ValueError("El animal seleccionado no existe o no está activo")
        
        # Validación: tipo de tratamiento debe ser válido
        tipos_validos = ["Vacunación", "Desparasitación", "Antibiótico", "Vitaminas", "Minerales", "Cirugía", "Otro"]
        if tipo_tratamiento not in tipos_validos:
            raise ValueError(f"Tipo de tratamiento inválido. Use uno de: {', '.join(tipos_validos)}")
        
        # Delegar inserción al repository
        self._repo.insertar_tratamiento(
            animal_id=animal_id,
            fecha_inicio=fecha_inicio,
            tipo_tratamiento=tipo_tratamiento,
            producto=producto,
            dosis=dosis,
            veterinario=veterinario,
            comentario=comentario,
            fecha_proxima=fecha_proxima
        )

    def obtener_historial_tratamientos(self, limite: int = 100) -> List[Dict[str, Any]]:
        """Obtiene el historial de tratamientos."""
        return self._repo.listar_tratamientos(limite=limite)

    def obtener_proximos_tratamientos(self, limite: int = 20) -> List[Dict[str, Any]]:
        """Obtiene los próximos tratamientos programados."""
        return self._repo.listar_proximos_tratamientos(limite=limite)

    def obtener_detalle_tratamiento(self, tratamiento_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene el detalle completo de un tratamiento."""
        return self._repo.obtener_tratamiento_por_id(tratamiento_id)

    def obtener_estadisticas_tratamientos(self) -> Dict[str, int]:
        """Obtiene estadísticas de tratamientos."""
        return {
            'total_activos': self._repo.contar_tratamientos(),
            'proximos_programados': self._repo.contar_proximos_tratamientos()
        }

    # ==================== CATÁLOGOS ====================

    def cargar_fincas(self) -> List[Dict[str, Any]]:
        """Carga el catálogo de fincas activas."""
        return self._repo.listar_fincas_activas()

    def cargar_animales_por_finca(self, finca_nombre: str) -> List[Dict[str, Any]]:
        """Carga animales filtrados por finca."""
        return self._repo.listar_animales_por_finca(finca_nombre)

    def cargar_animales(self) -> List[Dict[str, Any]]:
        """Carga todos los animales activos."""
        return self._repo.listar_animales_activos()
