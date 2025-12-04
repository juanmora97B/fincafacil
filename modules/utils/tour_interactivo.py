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
        
        # Pasos del tour
        self.pasos = [
            {
                "titulo": "Bienvenido a FincaFacil 🎉",
                "mensaje": "Este sistema profesional te ayudará a gestionar tu finca ganadera.\n\nHaz clic en SIGUIENTE para comenzar el recorrido."
            },
            {
                "titulo": "Dashboard 📊",
                "mensaje": "Aquí verás un resumen de tu finca:\n• Total de animales\n• Inventario\n• Eventos recientes\n• Gráficos de producción"
            },
            {
                "titulo": "Módulo de Animales 🐄",
                "mensaje": "Registra y gestiona tus animales:\n• Información básica\n• Historial médico\n• Reproducción\n• Peso y producción"
            },
            {
                "titulo": "Potreros y Pastoreo 🌿",
                "mensaje": "Controla tus terrenos:\n• Registrar potreros\n• Asignar animales\n• Rotación de pastoreo\n• Control de capacidad"
            },
            {
                "titulo": "Insumos y Equipos 📦",
                "mensaje": "Gestiona suministros:\n• Inventario de medicinas\n• Herramientas\n• Alertas de bajo stock\n• Historial de mantenimiento"
            },
            {
                "titulo": "Reportes y Análisis 📋",
                "mensaje": "Genera reportes profesionales:\n• Inventario de animales\n• Ventas y producción\n• Análisis financiero\n• Exportar a Excel"
            },
            {
                "titulo": "Tour Completado 🎓",
                "mensaje": "¡Listo! Ya conoces las funciones principales.\n\nRecomendaciones:\n1. Configura tu finca\n2. Registra tus animales\n3. Actualiza regularmente\n4. Haz backups frecuentes"
            }
        ]
        
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
        self.paso_actual = 0
        self._mostrar_paso_actual()
    
    def _mostrar_paso_actual(self):
        """Muestra el paso actual del tour"""
        if self.paso_actual >= len(self.pasos):
            self.marcar_tour_completado()
            messagebox.showinfo("Tour Completado", "¡Tour finalizado! Gracias por usar FincaFacil.")
            return
        
        paso = self.pasos[self.paso_actual]
        
        # Crear ventana de tour
        self.tour_window = ctk.CTkToplevel(self.app)
        self.tour_window.title("Tour FincaFacil")
        self.tour_window.geometry("500x300")
        self.tour_window.resizable(False, False)
        
        # Centrar ventana
        self.tour_window.transient(self.app)
        self.tour_window.grab_set()
        
        # Título
        titulo_label = ctk.CTkLabel(
            self.tour_window,
            text=paso["titulo"],
            font=("Arial", 18, "bold"),
            text_color="#1f538d"
        )
        titulo_label.pack(pady=(20, 10), padx=20)
        
        # Mensaje
        mensaje_label = ctk.CTkLabel(
            self.tour_window,
            text=paso["mensaje"],
            font=("Arial", 12),
            wraplength=450,
            justify="left"
        )
        mensaje_label.pack(pady=(10, 20), padx=20, fill="both", expand=True)
        
        # Progreso
        progreso_label = ctk.CTkLabel(
            self.tour_window,
            text=f"Paso {self.paso_actual + 1} de {len(self.pasos)}",
            font=("Arial", 10),
            text_color="#666666"
        )
        progreso_label.pack(pady=(0, 10))
        
        # Botones
        botones_frame = ctk.CTkFrame(self.tour_window)
        botones_frame.pack(pady=(0, 20), padx=20, fill="x")
        
        if self.paso_actual > 0:
            btn_anterior = ctk.CTkButton(
                botones_frame,
                text="Anterior",
                command=self.anterior_paso,
                width=100,
                fg_color="#666666"
            )
            btn_anterior.pack(side="left", padx=5)
        
        btn_siguiente = ctk.CTkButton(
            botones_frame,
            text="Siguiente" if self.paso_actual < len(self.pasos) - 1 else "Finalizar",
            command=self.siguiente_paso,
            width=100,
            fg_color="#2e7d32"
        )
        btn_siguiente.pack(side="right", padx=5)
        
        btn_salir = ctk.CTkButton(
            botones_frame,
            text="Salir",
            command=self.salir_tour,
            width=100,
            fg_color="#d32f2f"
        )
        btn_salir.pack(side="right", padx=5)
    
    def siguiente_paso(self):
        """Avanza al siguiente paso del tour."""
        if self.tour_window:
            self.tour_window.destroy()
        self.paso_actual += 1
        self._mostrar_paso_actual()
    
    def anterior_paso(self):
        """Retrocede al paso anterior del tour."""
        if self.tour_window:
            self.tour_window.destroy()
        self.paso_actual -= 1
        if self.paso_actual < 0:
            self.paso_actual = 0
        self._mostrar_paso_actual()
    
    def salir_tour(self):
        """Sale del tour interactivo."""
        if self.tour_window:
            self.tour_window.destroy()
        logger.info("Tour interactivo cancelado")


def obtener_tour_interactivo(ventana=None):
    """Obtiene una instancia del tour interactivo."""
    return TourInteractivo(ventana)
