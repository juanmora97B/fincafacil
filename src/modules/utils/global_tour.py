"""
Tour interactivo global del sistema FincaFácil.
Guía al usuario a través de los principales módulos de la aplicación.
"""
from modules.utils.tour_manager import TourManager, TourStep
from modules.utils.tour_state_manager import TourStateManager
import customtkinter as ctk


class GlobalTour:
    """Gestor del tour global interactivo"""
    
    def __init__(self, app: ctk.CTk):
        self.app = app
        self.state_manager = TourStateManager()
        self.tour_manager = TourManager(app, tour_name="global_tour")
        self._setup_steps()
    
    def _setup_steps(self):
        """Define los pasos del tour global"""
        
        # Paso 1: Bienvenida
        self.tour_manager.add_step(TourStep(
            title="Bienvenido a FincaFácil",
            text="Hola! Este es tu tour interactivo por FincaFácil.\n\n"
                 "Te mostraremos los módulos principales y cómo usarlos.\n\n"
                 "Haz clic en SIGUIENTE para continuar.",
            widget=None,
            position="center",
            duration=0
        ))
        
        # Paso 2: Dashboard
        self.tour_manager.add_step(TourStep(
            title="Dashboard - Tu Centro de Control",
            text="Este es el Dashboard. Aquí verás:\n\n"
                 "• Resumen de animales en la finca\n"
                 "• Eventos y alertas importantes\n"
                 "• Estadísticas de la operación\n\n"
                 "Es el primer lugar para verificar el estado general.",
            widget=None,
            position="top",
            duration=0
        ))
        
        # Paso 3: Módulo Animales
        self.tour_manager.add_step(TourStep(
            title="Módulo de Animales",
            text="Aquí registras y gestiona todos tus animales:\n\n"
                 "• Crear registros nuevos\n"
                 "• Editar información (peso, raza, etc.)\n"
                 "• Ver historial y movimientos\n"
                 "• Consultar reubicaciones\n\n"
                 "Es el corazón de la gestión ganadera.",
            widget=None,
            position="top",
            duration=0
        ))
        
        # Paso 4: Módulo Configuración
        self.tour_manager.add_step(TourStep(
            title="Configuración - Datos Base",
            text="Aquí configura los parámetros del sistema:\n\n"
                 "• Fincas y sectores\n"
                 "• Razas y tipos de explotación\n"
                 "• Empleados y proveedores\n"
                 "• Catálogos (diagnósticos, motivos de venta, etc.)\n\n"
                 "Estos datos se usan en todos los módulos.",
            widget=None,
            position="top",
            duration=0
        ))
        
        # Paso 5: Módulo Reportes
        self.tour_manager.add_step(TourStep(
            title="Reportes - Análisis y Seguimiento",
            text="Genera reportes para análisis:\n\n"
                 "• Inventario de animales\n"
                 "• Historial de ventas\n"
                 "• Tratamientos aplicados\n"
                 "• Producción (leche, pesos, etc.)\n\n"
                 "Exporta a Excel para análisis detallados.",
            widget=None,
            position="top",
            duration=0
        ))
        
        # Paso 6: Otros Módulos
        self.tour_manager.add_step(TourStep(
            title="Otros Módulos Importantes",
            text="Tu sistema incluye también:\n\n"
                 "• LECHE: Control de producción lechera\n"
                 "• VENTAS: Registro de animales vendidos\n"
                 "• SALUD: Diagnósticos y tratamientos\n"
                 "• REPRODUCCIÓN: Control de servicios\n"
                 "• HERRAMIENTAS: Inventario de equipo\n"
                 "• NÓMINA: Gestión de empleados\n"
                 "• POTREROS: Ubicación de animales\n"
                 "• INSUMOS: Control de materiales",
            widget=None,
            position="top",
            duration=0
        ))
        
        # Paso 7: Ajustes y Ayuda
        self.tour_manager.add_step(TourStep(
            title="Ajustes y Ayuda",
            text="En la sección AJUSTES encontrarás:\n\n"
                 "• Preferencias del sistema\n"
                 "• Manual de usuario (PDF)\n"
                 "• Plantillas para importar datos\n"
                 "• Reiniciar este tour\n\n"
                 "También hay botones de tour en cada módulo.",
            widget=None,
            position="top",
            duration=0
        ))
        
        # Paso 8: Final
        self.tour_manager.add_step(TourStep(
            title="¡Tour Completado!",
            text="Felicidades! Ya conoces FincaFácil.\n\n"
                 "Tips para empezar:\n"
                 "1. Configura tus fincas y sectores\n"
                 "2. Crea registros de animales\n"
                 "3. Usa reportes para seguimiento\n"
                 "4. Consulta el manual PDF en Ajustes\n\n"
                 "¡Bienvenido a tu nuevo sistema de gestión!",
            widget=None,
            position="center",
            duration=0
        ))
    
    def should_start_tour(self) -> bool:
        """Determina si el tour debe ejecutarse automáticamente"""
        return self.state_manager.es_primer_uso()
    
    def start_tour(self, auto_complete_on_finish: bool = True):
        """Inicia el tour interactivo"""
        
        def on_tour_complete():
            """Callback cuando termina el tour"""
            if auto_complete_on_finish:
                self.state_manager.marcar_primer_uso_completado()
                self.state_manager.marcar_tour_completado()
                print("[TOUR] Tour global completado - primer uso marcado")
        
        self.tour_manager.on_complete_callback = on_tour_complete
        self.tour_manager.start_tour()
    
    def reset_tour(self):
        """Resetea el tour para que vuelva a mostrarse"""
        self.state_manager.reset_tour()
        print("[TOUR] Estado del tour reseteado")
