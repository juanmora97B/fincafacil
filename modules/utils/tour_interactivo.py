"""
Tour Interactivo para Nuevos Usuarios
"""
import customtkinter as ctk
from tkinter import messagebox
import json
import os

from modules.utils.logger import Logger

logger = Logger(__name__)


class TourInteractivo:
    """Sistema de tour interactivo que guía al usuario por primera vez"""
    
    def __init__(self, app):
        """
        Inicializa el tour interactivo.
        
        Args:
            app: La ventana principal de la aplicación
        """
        self.app = app
        self.paso_actual = 0
        self.tour_window = None
        self.config_file = "config/tour_completado.json"
        self.pasos = []
        logger.info("Tour interactivo inicializado")
    
    def debe_mostrar_tour(self):
        """Verifica si el tour debe mostrarse (primera vez)"""
        if not os.path.exists(self.config_file):
            return True
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return not config.get('completado', False)
        except:
            return True
    
    def marcar_tour_completado(self):
        """Marca el tour como completado"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump({'completado': True}, f)
    
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
