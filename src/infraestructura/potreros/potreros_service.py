"""
Módulo: Potreros Service
Responsabilidad: Lógica de negocio (validaciones, orquestación)
No contiene: SQL directo (solo llama a repository)

Métodos:
  - Listar: listar_fincas(), listar_potreros(), listar_potreros_filtrado()
  - Obtener: obtener_detalles(), obtener_animales()
  - Métricas: obtener_metricas()
"""

from typing import List, Dict, Any, Optional
from infraestructura.potreros.potreros_repository import PotrerosRepository


class PotrerosService:
    """Servicio de lógica de negocio para Potreros"""

    def __init__(self, repository: Optional[PotrerosRepository] = None):
        """
        Inicializa el servicio con un repositorio.
        
        Args:
            repository: Instancia de PotrerosRepository. Si None, crea una nueva.
        """
        self.repository = repository or PotrerosRepository()

    def listar_fincas(self) -> List[str]:
        """
        Lista fincas activas disponibles.
        
        Returns:
            List[str]: Lista de nombres de fincas
        
        Raises:
            Exception: Si hay error en la consulta
        """
        try:
            fincas = self.repository.obtener_fincas_activas()
            # Agregar "Todas las fincas" al inicio
            return ["Todas las fincas"] + fincas
        except Exception as e:
            raise Exception(f"Error listando fincas: {e}")

    def listar_potreros(self) -> List[Dict[str, Any]]:
        """
        Lista todos los potreros disponibles.
        
        Returns:
            List[Dict]: Lista de potreros con estructura de repository
        
        Raises:
            Exception: Si hay error en la consulta
        """
        try:
            potreros = self.repository.obtener_potreros_todos()
            return potreros
        except Exception as e:
            raise Exception(f"Error listando potreros: {e}")

    def listar_potreros_filtrado(self, finca_nombre: str) -> List[Dict[str, Any]]:
        """
        Lista potreros filtrados por finca.
        
        Args:
            finca_nombre: Nombre de la finca o "Todas las fincas"
        
        Returns:
            List[Dict]: Lista de potreros
        
        Raises:
            Exception: Si hay error en la consulta
        """
        try:
            if finca_nombre == "Todas las fincas":
                potreros = self.repository.obtener_potreros_todos()
            else:
                # Validar que la finca existe en la lista activas
                fincas = self.repository.obtener_fincas_activas()
                if finca_nombre not in fincas:
                    raise ValueError(f"Finca '{finca_nombre}' no existe o está inactiva")
                potreros = self.repository.obtener_potreros_por_finca(finca_nombre)
            return potreros
        except Exception as e:
            raise Exception(f"Error listando potreros filtrado: {e}")

    def obtener_detalles(self, nombre_potrero: str, finca_nombre: str) -> Dict[str, Any]:
        """
        Obtiene detalles completos de un potrero específico.
        
        Args:
            nombre_potrero: Nombre del potrero
            finca_nombre: Nombre de la finca
        
        Returns:
            Dict: Detalles del potrero
        
        Raises:
            Exception: Si el potrero no existe o hay error en la consulta
        """
        try:
            potrero = self.repository.obtener_detalles_potrero(nombre_potrero, finca_nombre)
            if not potrero:
                raise ValueError(f"Potrero '{nombre_potrero}' en finca '{finca_nombre}' no existe")
            return potrero
        except Exception as e:
            raise Exception(f"Error obteniendo detalles del potrero: {e}")

    def obtener_animales(self, nombre_potrero: str, finca_nombre: str) -> List[Dict[str, Any]]:
        """
        Obtiene animales asignados a un potrero.
        
        Args:
            nombre_potrero: Nombre del potrero
            finca_nombre: Nombre de la finca
        
        Returns:
            List[Dict]: Lista de animales activos en el potrero
        
        Raises:
            Exception: Si hay error en la consulta
        """
        try:
            animales = self.repository.obtener_animales_potrero(nombre_potrero, finca_nombre)
            return animales
        except Exception as e:
            raise Exception(f"Error obteniendo animales del potrero: {e}")

    def contar_animales_potrero(self, id_potrero: int) -> int:
        """
        Cuenta animales activos en un potrero.
        
        Args:
            id_potrero: ID del potrero
        
        Returns:
            int: Cantidad de animales
        
        Raises:
            Exception: Si hay error en la consulta
        """
        try:
            if id_potrero is None or id_potrero <= 0:
                raise ValueError("ID de potrero inválido")
            count = self.repository.contar_animales_por_potrero(id_potrero)
            return count
        except Exception as e:
            raise Exception(f"Error contando animales: {e}")

    def obtener_metricas(self, potreros_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Obtiene métricas agregadas de potreros.
        
        Args:
            potreros_data: Lista de potreros (si None, obtiene todos)
        
        Returns:
            Dict: Métricas agregadas
        
        Raises:
            Exception: Si hay error
        """
        try:
            if potreros_data is None:
                potreros_data = self.repository.obtener_potreros_todos()
            metricas = self.repository.obtener_metricas_potreros(potreros_data)
            return metricas
        except Exception as e:
            raise Exception(f"Error obteniendo métricas: {e}")
