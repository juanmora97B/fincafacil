"""
Módulo de tour interactivo para la aplicación FincaFácil.
Proporciona guías paso a paso para los usuarios nuevos.
"""

from modules.utils.logger import Logger

logger = Logger(__name__)


class TourInteractivo:
    """Gestor del tour interactivo de la aplicación."""
    
    def __init__(self, ventana_principal=None):
        """
        Inicializa el tour interactivo.
        
        Args:
            ventana_principal: La ventana principal de la aplicación
        """
        self.ventana_principal = ventana_principal
        self.pasos_completados = []
        logger.info("Tour interactivo inicializado")
    
    def iniciar_tour(self):
        """Inicia el tour interactivo."""
        logger.info("Iniciando tour interactivo")
        pass
    
    def siguiente_paso(self):
        """Avanza al siguiente paso del tour."""
        pass
    
    def anterior_paso(self):
        """Retrocede al paso anterior del tour."""
        pass
    
    def salir_tour(self):
        """Sale del tour interactivo."""
        logger.info("Tour interactivo finalizado")
        pass


def obtener_tour_interactivo(ventana=None):
    """Obtiene una instancia del tour interactivo."""
    return TourInteractivo(ventana)
