"""
Example: How to integrate TourManager into your modules
Copy and adapt this pattern to each module (animales, dashboard, reportes, etc)
"""

import json
from pathlib import Path
import customtkinter as ctk
from modules.utils.tour_manager import TourManager, ModuleTourHelper
from modules.utils.logger import Logger

logger = Logger(__name__)


class AnimalesTourSetup:
    """
    Example: Tour setup for Animales module
    """
    
    @staticmethod
    def load_tour_config() -> dict:
        """Load tour configuration from JSON"""
        try:
            config_file = Path("config/tour_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("animales", {})
        except Exception as e:
            logger.error(f"Error loading tour config: {e}")
        return {}
    
    @staticmethod
    def setup_tour_for_module(main_app: ctk.CTk, module_frame: ctk.CTkFrame):
        """
        Setup tour for Animales module
        
        Example usage in your module's __init__:
        ```
        self.tour_helper = ModuleTourHelper("animales")
        self.tour_helper.initialize_tour(main_app, auto_start=False)
        
        # Register widgets
        self.tour_helper.tour_manager.register_widget("btn_new_animal", self.btn_nuevo)
        self.tour_helper.tour_manager.register_widget("tabla_animales", self.tabla)
        
        # Add tour steps
        config = AnimalesTourSetup.load_tour_config()
        if config:
            self.tour_helper.add_steps(config.get("steps", []))
        ```
        """
        pass


class DashboardTourSetup:
    """
    Example: Tour setup for Dashboard module
    """
    
    @staticmethod
    def setup_tour_for_dashboard(main_app: ctk.CTk, dashboard_frame: ctk.CTkFrame):
        """
        Setup tour for Dashboard
        
        Example usage in dashboard_main.py __init__:
        ```
        self.tour_helper = ModuleTourHelper("dashboard")
        self.tour_helper.initialize_tour(main_app, auto_start=True)
        
        # Register all dashboard components
        self.tour_helper.tour_manager.register_widget("dashboard_summary", self.summary_frame)
        self.tour_helper.tour_manager.register_widget("dashboard_charts", self.charts_frame)
        self.tour_helper.tour_manager.register_widget("dashboard_events", self.events_frame)
        
        # Add tour button to dashboard header
        tour_btn = self.tour_helper.show_tour_button(self.header_frame)
        if tour_btn:
            tour_btn.pack(side="right", padx=10)
        
        # Load and add tour steps
        config = DashboardTourSetup.load_tour_config()
        if config:
            self.tour_helper.add_steps(config.get("steps", []))
        ```
        """
        pass


# ============================================================================
# PASO A PASO: INTEGRAR TOUR EN UN MÓDULO EXISTENTE
# ============================================================================

"""
EJEMPLO COMPLETO: Agregar tour al módulo de Animales

1. En el método __init__ del módulo (después de crear los widgets principales):

    from modules.utils.tour_manager import ModuleTourHelper
    import json
    from pathlib import Path

    # Inicializar tour helper
    self.tour_helper = ModuleTourHelper("animales")
    self.tour_helper.initialize_tour(self.master, auto_start=False)

2. Registrar widgets después de crearlos:

    # Registrar botón nuevo animal
    self.btn_nuevo = ctk.CTkButton(toolbar, text="+ Nuevo Animal")
    self.tour_helper.tour_manager.register_widget("btn_new_animal", self.btn_nuevo)
    
    # Registrar tabla de animales
    self.tabla = ttk.Treeview(content_frame, columns=(...))
    self.tour_helper.tour_manager.register_widget("tabla_animales", self.tabla)
    
    # Registrar frame de filtros
    self.filtros_frame = ctk.CTkFrame(content_frame)
    self.tour_helper.tour_manager.register_widget("filtros_frame", self.filtros_frame)

3. Cargar configuración del tour:

    def cargar_tour(self):
        try:
            with open("config/tour_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                tour_steps = config.get("animales", {}).get("steps", [])
                
                # Agregar pasos al tour
                self.tour_helper.add_steps(tour_steps)
        except Exception as e:
            self.logger.error(f"Error cargando tour: {e}")

4. Crear botón "Tour" en la barra de herramientas:

    tour_btn = self.tour_helper.show_tour_button(toolbar)
    if tour_btn:
        tour_btn.pack(side="right", padx=5)

5. Opcional: Iniciar tour automáticamente para usuarios nuevos:

    self.tour_helper = ModuleTourHelper("animales")
    self.tour_helper.initialize_tour(self.master, auto_start=True)  # <-- auto_start=True

RESULTADO:
- Tour interactive aparece cuando el usuario hace clic en el botón "❓ Tour"
- Se muestran tooltips con explicaciones
- Widgets se destacan con overlay
- Usuario puede navegar con Anterior/Siguiente/Saltar
- Estado se guarda en config/tour_animales_state.json
- No molesta más en futuras visitas (salvo si reinicia el tour manualmente)
"""


# ============================================================================
# FUNCIONES AUXILIARES PARA TOURS PERSONALIZADOS
# ============================================================================

def crear_tour_personalizado(
    app: ctk.CTk,
    nombre: str,
    pasos: list,
    auto_start: bool = False
) -> TourManager:
    """
    Crear un tour personalizado con pasos específicos
    
    Args:
        app: Aplicación principal
        nombre: Nombre del tour (se usa en config)
        pasos: Lista de diccionarios con configuración de pasos
        auto_start: Iniciar automáticamente si es primera vez
    
    Returns:
        TourManager configurado y listo
    
    Ejemplo:
    ```
    pasos = [
        {
            "title": "Paso 1",
            "description": "Primera explicación",
            "widget_name": "widget_1",
            "duration": 0
        },
        {
            "title": "Paso 2",
            "description": "Segunda explicación",
            "widget_name": "widget_2",
            "duration": 3  # Auto-avanza después de 3 segundos
        }
    ]
    
    tour = crear_tour_personalizado(app, "mi_tour", pasos, auto_start=True)
    tour.start_tour()
    ```
    """
    from modules.utils.tour_manager import TourManager
    
    tour_mgr = TourManager(app, tour_name=nombre)
    tour_mgr.add_steps_from_config(pasos)
    
    if auto_start and not tour_mgr.has_completed_tour():
        tour_mgr.start_tour()
    
    return tour_mgr


def agregar_tour_button_a_toolbar(
    toolbar: ctk.CTkFrame,
    tour_manager: 'TourManager',
    position: str = "right"
) -> ctk.CTkButton:
    """
    Agregar botón de tour a toolbar
    
    Args:
        toolbar: Frame de toolbar
        tour_manager: Instancia de TourManager
        position: "left" o "right"
    
    Returns:
        El botón creado
    """
    btn = ctk.CTkButton(
        toolbar,
        text="❓ Tour",
        command=tour_manager.start_tour,
        width=80,
        height=28,
        font=("Arial", 10),
        fg_color="#1f538d",
        hover_color="#2e7d32"
    )
    
    btn.pack(side=position, padx=5, pady=5)
    return btn
