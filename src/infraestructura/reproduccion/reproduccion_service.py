"""Servicio de dominio para Reproducción.

Orquesta lógica de negocio para servicios reproductivos, gestaciones y partos.
No contiene SQL; delega al repositorio.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .reproduccion_repository import ReproduccionRepository


class ReproduccionService:
    """Servicio de dominio que orquesta operaciones de reproducción."""

    def __init__(self, repository: Optional[ReproduccionRepository] = None) -> None:
        self._repo = repository or ReproduccionRepository()

    # ==================== VALIDACIONES ====================

    def validar_hembra_gestante(self, hembra_id: int) -> bool:
        """Verificar si una hembra ya tiene un servicio activo (gestante)."""
        count = self._repo.contar_servicios_activos_hembra(hembra_id)
        return count > 0

    def validar_servicio_duplicado(self, hembra_id: int, fecha_servicio: str) -> bool:
        """Verificar si ya existe un servicio en la misma fecha."""
        count = self._repo.contar_servicios_misma_fecha(hembra_id, fecha_servicio)
        return count > 0

    # ==================== CÁLCULOS TEMPORALES ====================

    def calcular_fecha_parto_estimada(self, fecha_servicio: str, dias_gestacion: int = 280) -> str:
        """Calcular fecha estimada de parto sumando días de gestación."""
        fecha = datetime.strptime(fecha_servicio, "%Y-%m-%d")
        parto = fecha + timedelta(days=dias_gestacion)
        return parto.strftime("%Y-%m-%d")

    def calcular_dias_gestacion(self, fecha_servicio: str) -> int:
        """Calcular días transcurridos desde el servicio (días de gestación)."""
        fecha = datetime.strptime(fecha_servicio, "%Y-%m-%d")
        hoy = datetime.now()
        return (hoy - fecha).days

    def calcular_dias_para_parto(self, fecha_parto_estimada: str) -> int:
        """Calcular días restantes hasta la fecha estimada de parto."""
        parto = datetime.strptime(fecha_parto_estimada, "%Y-%m-%d")
        hoy = datetime.now()
        return (parto - hoy).days

    # ==================== GENERACIÓN DE CÓDIGOS ====================

    def generar_codigo_cria(self) -> str:
        """Generar código automático para cría (formato A0001, A0002, etc.)."""
        ultimo = self._repo.obtener_ultimo_codigo_cria()
        if ultimo:
            try:
                num = int(ultimo) + 1
            except ValueError:
                num = 1
        else:
            num = 1
        return f"A{num:04d}"

    # ==================== LECTURA (CONSULTAS) ====================

    def obtener_estadisticas_badges(self) -> Dict[str, int]:
        """Obtener contadores para badges del dashboard."""
        return {
            "gestantes": self._repo.contar_gestantes(),
            "proximos_30": self._repo.contar_proximos_partos(30),
            "inseminaciones_año": self._repo.contar_inseminaciones_ultimos_365_dias(),
            "montas_año": self._repo.contar_montas_naturales_ultimos_365_dias(),
        }

    def listar_gestantes(self) -> List[Dict[str, Any]]:
        """Listar todas las hembras gestantes."""
        return self._repo.listar_gestantes()

    def listar_proximos_partos(self, dias: int = 60) -> List[Dict[str, Any]]:
        """Listar próximos partos en N días."""
        return self._repo.listar_proximos_partos(dias)

    def cargar_fincas(self) -> List[Dict[str, Any]]:
        """Cargar fincas activas para dropdown."""
        return self._repo.listar_fincas_activas()

    def cargar_hembras(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Cargar hembras, opcionalmente filtradas por finca."""
        return self._repo.listar_hembras_por_finca(finca_id)

    def cargar_machos(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Cargar machos, opcionalmente filtrados por finca."""
        return self._repo.listar_machos_por_finca(finca_id)

    def obtener_hembra_de_servicio(self, servicio_id: int) -> Optional[int]:
        """Obtener id de hembra asociada a un servicio."""
        return self._repo.obtener_hembra_por_servicio(servicio_id)

    # ==================== ESCRITURA (OPERACIONES) ====================

    def registrar_servicio(
        self,
        hembra_id: int,
        macho_id: Optional[int],
        fecha_servicio: str,
        tipo_servicio: str,
        observaciones: Optional[str] = None,
    ) -> None:
        """Registrar nuevo servicio reproductivo (monta o inseminación).

        Validaciones:
        - Hembra no debe tener servicio activo previo
        - No duplicar servicio en misma fecha

        Args:
            hembra_id: ID de la hembra
            macho_id: ID del macho (None si es inseminación)
            fecha_servicio: Fecha del servicio (YYYY-MM-DD)
            tipo_servicio: "Monta Natural" o "Inseminación Artificial"
            observaciones: Observaciones opcionales

        Raises:
            ValueError: Si la hembra ya está gestante o hay servicio duplicado
        """
        # Validaciones
        if self.validar_hembra_gestante(hembra_id):
            raise ValueError("La hembra ya tiene un servicio activo (gestante)")

        if self.validar_servicio_duplicado(hembra_id, fecha_servicio):
            raise ValueError("Ya existe un servicio registrado en esta fecha")

        # Cálculos
        fecha_parto_estimada = self.calcular_fecha_parto_estimada(fecha_servicio)

        # Persistencia
        self._repo.insertar_servicio(
            hembra_id=hembra_id,
            macho_id=macho_id,
            fecha_servicio=fecha_servicio,
            tipo_servicio=tipo_servicio,
            estado="Gestante",
            fecha_parto_estimada=fecha_parto_estimada,
            observaciones=observaciones,
        )

        # Bitácora
        self._repo.insertar_comentario(
            animal_id=hembra_id,
            fecha=fecha_servicio,
            tipo="Reproducción",
            nota=f"Servicio: {tipo_servicio}. Parto estimado: {fecha_parto_estimada}",
        )

    def registrar_parto(
        self,
        servicio_id: int,
        hembra_id: int,
        fecha_parto: str,
        tipo_parto: str,
        sexo_cria: str,
        peso_cria: Optional[float] = None,
        estado_cria: str = "Vivo",
        registrar_cria: bool = True,
        observaciones: Optional[str] = None,
    ) -> None:
        """Registrar parto y opcionalmente crear cría.

        Flujo:
        1. Actualizar servicio a estado "Parida"
        2. Insertar comentario en bitácora de hembra
        3. Si registrar_cria=True:
           - Generar código automático
           - Obtener finca de la madre
           - Insertar nuevo animal

        Args:
            servicio_id: ID del servicio reproductivo
            hembra_id: ID de la hembra
            fecha_parto: Fecha real del parto
            tipo_parto: "Normal", "Distócico", "Cesárea", "Aborto"
            sexo_cria: "Macho" o "Hembra"
            peso_cria: Peso opcional en kg
            estado_cria: "Vivo", "Muerto al nacer", "Murió después"
            registrar_cria: Si True, crea automáticamente el animal
            observaciones: Observaciones del parto
        """
        # 1. Actualizar servicio
        self._repo.actualizar_servicio_parto(
            servicio_id=servicio_id,
            estado="Parida",
            fecha_parto_real=fecha_parto,
            observaciones=observaciones,
        )

        # 2. Comentario en bitácora
        nota_parto = f"Parto {tipo_parto}. Cría {sexo_cria}, estado: {estado_cria}"
        if peso_cria:
            nota_parto += f", peso: {peso_cria} kg"
        self._repo.insertar_comentario(
            animal_id=hembra_id,
            fecha=fecha_parto,
            tipo="Parto",
            nota=nota_parto,
        )

        # 3. Registrar cría si corresponde
        if registrar_cria and estado_cria == "Vivo":
            codigo_cria = self.generar_codigo_cria()
            finca_id = self._repo.obtener_finca_de_animal(hembra_id)

            if not finca_id:
                raise ValueError("No se pudo obtener la finca de la madre")

            nombre_cria = f"Cría de {fecha_parto}"

            self._repo.insertar_cria(
                codigo=codigo_cria,
                nombre=nombre_cria,
                sexo=sexo_cria,
                fecha_nacimiento=fecha_parto,
                tipo_ingreso="NACIMIENTO",
                madre_id=hembra_id,
                finca_id=finca_id,
                peso_nacimiento=peso_cria,
                estado_cria=estado_cria,
            )

    def marcar_servicio_vacio(self, servicio_id: int) -> None:
        """Anular servicio marcándolo como vacío."""
        self._repo.actualizar_estado_servicio(servicio_id, "Vacía")
