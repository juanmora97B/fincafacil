"""
Tour interactivo global del sistema FincaFácil - Ventana Modal Única.
Implementa un tour dinámico en una sola ventana CTkToplevel con dos secciones:
- Sección Superior: Contenido del paso (título + descripción)
- Sección Inferior: Controles de navegación
"""
import customtkinter as ctk
from tkinter import StringVar, messagebox
from pathlib import Path
from PIL import Image
from config import config
from modules.utils.tour_state_manager import TourStateManager


class GlobalTour:
    """Gestor del tour global con ventana modal única"""
    
    def __init__(self, app: ctk.CTk):
        self.app = app
        self.state_manager = TourStateManager()
        self.current_step = 0
        
        # Ventana del tour
        self.ventana_tour: ctk.CTkToplevel | None = None
        
        # Variables dinámicas para actualización sin parpadeos
        self.var_titulo = StringVar(value="")
        self.var_descripcion = StringVar(value="")
        self.var_progreso = StringVar(value="Paso 1 de 13")
        
        # Referencias a widgets
        self.btn_anterior = None
        self.btn_siguiente = None
        self.logo_image = None
        
        # Definir los 13 pasos del tour
        self.pasos = self._definir_pasos()
    
    def _definir_pasos(self) -> list[dict[str, str]]:
        """Define los 13 pasos del tour con título y descripción"""
        return [
            {
                "titulo": "🎉 ¡Bienvenido a FincaFácil!",
                "descripcion": (
                    "Hola! Somos muy felices de que uses FincaFácil.\n\n"
                    "Este tour te guiará paso a paso por todos los\n"
                    "módulos y características del sistema.\n\n"
                    "Aprenderás a gestionar tu finca de manera profesional.\n\n"
                    "Haz clic en SIGUIENTE para comenzar."
                )
            },
            {
                "titulo": "📊 Dashboard - Tu Centro de Control",
                "descripcion": (
                    "Este es el Dashboard, tu punto de partida.\n\n"
                    "Aquí verás:\n"
                    "✓ Resumen de tu inventario de animales\n"
                    "✓ Estadísticas clave de la operación\n"
                    "✓ Eventos recientes y cambios\n"
                    "✓ Alertas importantes que necesitan atención\n\n"
                    "Es tu panel de control principal."
                )
            },
            {
                "titulo": "🐄 Módulo de Animales",
                "descripcion": (
                    "Aquí registras y gestionas TODOS tus animales.\n\n"
                    "Puedes:\n"
                    "✓ Crear nuevos registros de animales\n"
                    "✓ Registrar peso, raza, edad, sexo\n"
                    "✓ Incluir ubicación (finca, potrero, sector)\n"
                    "✓ Ver historial completo de cada animal\n"
                    "✓ Registrar movimientos y cambios de estado\n\n"
                    "Es esencial para la gestión ganadera."
                )
            },
            {
                "titulo": "⚙️ Configuración - Setup Inicial",
                "descripcion": (
                    "IMPORTANTE: Antes de registrar animales,\n"
                    "configura la base de datos.\n\n"
                    "Setup necesario:\n"
                    "✓ Tus Fincas (ubicaciones principales)\n"
                    "✓ Sectores (divisiones dentro de fincas)\n"
                    "✓ Potreros (áreas de pasto/tierra)\n"
                    "✓ Razas (tipos de ganado que tienes)\n"
                    "✓ Empleados (personal de la finca)\n"
                    "✓ Proveedores (para compras)\n\n"
                    "¡Esta información es base para todo!"
                )
            },
            {
                "titulo": "🏥 Módulo de Salud",
                "descripcion": (
                    "Registra diagnósticos y tratamientos.\n\n"
                    "Puedes:\n"
                    "✓ Registrar enfermedades detectadas\n"
                    "✓ Aplicar tratamientos y medicinas\n"
                    "✓ Dar seguimiento a recuperaciones\n"
                    "✓ Mantener historial médico por animal\n"
                    "✓ Ver alertas de animales enfermos\n\n"
                    "Fundamental para la salud del rebaño."
                )
            },
            {
                "titulo": "🤰 Reproducción - Control Reproductivo",
                "descripcion": (
                    "Gestiona servicios y partos.\n\n"
                    "Registra:\n"
                    "✓ Servicios (montería o inseminación artificial)\n"
                    "✓ Fechas de servicios\n"
                    "✓ Resultados de preñez\n"
                    "✓ Partos y descendientes\n"
                    "✓ Genealogía del rebaño\n\n"
                    "Esencial para crecimiento genético."
                )
            },
            {
                "titulo": "🥛 Producción de Leche",
                "descripcion": (
                    "Registra y analiza producción lechera.\n\n"
                    "Puedes:\n"
                    "✓ Registrar producción diaria por vaca\n"
                    "✓ Calidad de leche (grasa, proteína, etc.)\n"
                    "✓ Gráficas de tendencias\n"
                    "✓ Identificar vacas de bajo rendimiento\n"
                    "✓ Proyecciones de producción\n\n"
                    "Maximiza tu rentabilidad lechera."
                )
            },
            {
                "titulo": "💰 Ventas - Registro de Transacciones",
                "descripcion": (
                    "Documenta venta de animales.\n\n"
                    "Registra:\n"
                    "✓ Comprador y precio de venta\n"
                    "✓ Motivo de venta (descarte, reproducción, etc.)\n"
                    "✓ Documentación y trazabilidad\n"
                    "✓ Historial de transacciones\n"
                    "✓ Reportes de ventas por período\n\n"
                    "Controla ingresos y rotación."
                )
            },
            {
                "titulo": "📦 Otros Módulos Útiles",
                "descripcion": (
                    "Tu sistema incluye más características:\n\n"
                    "✓ HERRAMIENTAS: Inventario de equipo\n"
                    "✓ INSUMOS: Materiales y alimentos\n"
                    "✓ NÓMINA: Gestión de empleados\n"
                    "✓ POTREROS: Ubicación visual de animales\n"
                    "✓ REPORTES: Análisis y exportación Excel\n\n"
                    "Explora cada uno según necesites."
                )
            },
            {
                "titulo": "📈 Reportes - Análisis y Decisiones",
                "descripcion": (
                    "Genera reportes profesionales.\n\n"
                    "Disponibles:\n"
                    "✓ Inventario completo de animales\n"
                    "✓ Historial de ventas\n"
                    "✓ Producción lechera por período\n"
                    "✓ Tratamientos aplicados\n"
                    "✓ Análisis de costos\n"
                    "✓ Exportación a Excel\n\n"
                    "Toma decisiones con datos reales."
                )
            },
            {
                "titulo": "⚙️ Ajustes - Configuración",
                "descripcion": (
                    "Personaliza tu experiencia.\n\n"
                    "En Ajustes encuentras:\n"
                    "✓ Preferencias del sistema\n"
                    "✓ Manual completo del usuario (PDF)\n"
                    "✓ Plantillas para importar datos Excel\n"
                    "✓ Opción para reiniciar este tour\n"
                    "✓ Información de licencia\n\n"
                    "Accede en cualquier momento."
                )
            },
            {
                "titulo": "🚀 Próximos Pasos Recomendados",
                "descripcion": (
                    "Para comenzar ahora:\n\n"
                    "1️⃣ Ve a CONFIGURACIÓN y crea:\n"
                    "   - Tu(s) finca(s)\n"
                    "   - Sectores y potreros\n"
                    "   - Razas que manejas\n\n"
                    "2️⃣ Luego ve a ANIMALES y:\n"
                    "   - Registra tu ganado actual\n"
                    "   - Asigna a sectores\n\n"
                    "3️⃣ Usa REPORTES para verificar datos.\n\n"
                    "¡El sistema está listo para usar!"
                )
            },
            {
                "titulo": "✅ ¡Tour Completado!",
                "descripcion": (
                    "¡Felicidades! Ahora conoces FincaFácil.\n\n"
                    "Recuerda:\n"
                    "✓ Este tour está disponible en AJUSTES\n"
                    "✓ Cada módulo tiene su propio tour\n"
                    "✓ Consulta el manual PDF en AJUSTES\n"
                    "✓ Los datos se guardan automáticamente\n\n"
                    "¡Bienvenido a tu nuevo sistema\n"
                    "de gestión ganadera profesional!"
                )
            }
        ]
    
    def _cargar_logo(self):
        """Carga el logo de la empresa - no es crítico si falla"""
        try:
            logo_path = Path(config.ASSETS_DIR) / "Logo.png"
            if logo_path.exists():
                img = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(img, size=(50, 50))
                print(f"[TOUR] ✅ Logo cargado correctamente desde {logo_path}")
            else:
                print(f"[TOUR] ⚠️ Logo no encontrado en {logo_path} - continuando sin logo")
                self.logo_image = None
        except Exception as e:
            print(f"[TOUR] ⚠️ Error al cargar logo: {e} - continuando sin logo")
            self.logo_image = None  # Continuar sin logo si falla
    
    def _crear_ventana_tour(self):
        """Crea la ventana modal única del tour. Retorna True si es exitoso."""
        try:
            self.ventana_tour = ctk.CTkToplevel(self.app)
            self.ventana_tour.title("Tour Guiado - FincaFácil")
            self.ventana_tour.geometry("600x550")
            self.ventana_tour.resizable(False, False)
            
            # Configurar como flotante (sin grab_set para evitar bloqueos)
            self.ventana_tour.transient(self.app)
            self.ventana_tour.attributes("-topmost", True)
            
            # Centrar en pantalla
            self.ventana_tour.update_idletasks()
            screen_width = self.ventana_tour.winfo_screenwidth()
            screen_height = self.ventana_tour.winfo_screenheight()
            x = (screen_width - 600) // 2
            y = (screen_height - 550) // 2
            self.ventana_tour.geometry(f"+{x}+{y}")
            
            # Fondo principal
            self.ventana_tour.configure(fg_color="#1a1a1a")
            
            # ==================== SECCIÓN SUPERIOR: CONTENIDO ====================
            frame_contenido = ctk.CTkFrame(
                self.ventana_tour,
                fg_color="#2d4a3e",  # Verde bosque suave
                corner_radius=15
            )
            frame_contenido.pack(fill="both", expand=True, padx=20, pady=(20, 10))
            
            # Header con logo e icono
            frame_header = ctk.CTkFrame(frame_contenido, fg_color="transparent")
            frame_header.pack(fill="x", padx=20, pady=(15, 10))
            
            # Logo pequeño en esquina superior izquierda
            if self.logo_image:
                ctk.CTkLabel(
                    frame_header,
                    image=self.logo_image,
                    text=""
                ).pack(side="left")
            
            # Icono de ayuda decorativo
            ctk.CTkLabel(
                frame_header,
                text="❓",
                font=("Segoe UI Emoji", 40),
                text_color="#66bb6a"
            ).pack(side="right")
            
            # Título del paso (dinámico con StringVar)
            label_titulo = ctk.CTkLabel(
                frame_contenido,
                textvariable=self.var_titulo,
                font=("Segoe UI", 24, "bold"),
                text_color="#ffffff",
                wraplength=530
            )
            label_titulo.pack(pady=(10, 15), padx=20)
            
            # Separador visual
            separator = ctk.CTkFrame(
                frame_contenido,
                height=2,
                fg_color="#66bb6a",
                corner_radius=1
            )
            separator.pack(fill="x", padx=50, pady=(0, 15))
            
            # Descripción del paso (dinámico con StringVar)
            label_descripcion = ctk.CTkLabel(
                frame_contenido,
                textvariable=self.var_descripcion,
                font=("Segoe UI", 13),
                text_color="#e0e0e0",
                wraplength=530,
                justify="left"
            )
            label_descripcion.pack(pady=(0, 20), padx=30)
            
            # ==================== SECCIÓN INFERIOR: CONTROLES ====================
            frame_controles = ctk.CTkFrame(
                self.ventana_tour,
                fg_color="#212121",
                corner_radius=15,
                height=90
            )
            frame_controles.pack(fill="x", padx=20, pady=(10, 20))
            frame_controles.pack_propagate(False)
            
            # Indicador de progreso (centro)
            label_progreso = ctk.CTkLabel(
                frame_controles,
                textvariable=self.var_progreso,
                font=("Segoe UI", 14, "bold"),
                text_color="#66bb6a"
            )
            label_progreso.pack(pady=(10, 12))
            
            # Frame de botones
            frame_botones = ctk.CTkFrame(frame_controles, fg_color="transparent")
            frame_botones.pack(fill="x", padx=30, pady=(0, 10))
            
            # Botón Saltar (izquierda - rojo suave)
            btn_saltar = ctk.CTkButton(
                frame_botones,
                text="Saltar",
                command=self._saltar_tour,
                width=100,
                height=38,
                font=("Segoe UI", 13, "bold"),
                fg_color="#e57373",
                hover_color="#ef5350",
                corner_radius=15
            )
            btn_saltar.pack(side="left")
            
            # Espaciador central
            ctk.CTkLabel(frame_botones, text="", width=10).pack(side="left", expand=True)
            
            # Botón Anterior (centro-derecha)
            self.btn_anterior = ctk.CTkButton(
                frame_botones,
                text="← Anterior",
                command=self._paso_anterior,
                width=120,
                height=38,
                font=("Segoe UI", 13),
                fg_color="#616161",
                hover_color="#757575",
                corner_radius=15
            )
            self.btn_anterior.pack(side="left", padx=5)
            
            # Botón Siguiente (derecha - verde profesional)
            self.btn_siguiente = ctk.CTkButton(
                frame_botones,
                text="Siguiente →",
                command=self._paso_siguiente,
                width=130,
                height=38,
                font=("Segoe UI", 13, "bold"),
                fg_color="#66bb6a",
                hover_color="#4caf50",
                corner_radius=15
            )
            self.btn_siguiente.pack(side="left", padx=5)
            
            # Evitar cierre con X
            self.ventana_tour.protocol("WM_DELETE_WINDOW", self._saltar_tour)
            
            # Actualizar la ventana antes de devolver el control
            self.ventana_tour.update_idletasks()
            
            return True  # Éxito
            
        except Exception as e:
            print(f"[TOUR] Error creando ventana del tour: {e}")
            import traceback
            traceback.print_exc()
            if self.ventana_tour:
                try:
                    self.ventana_tour.destroy()
                except:
                    pass
            self.ventana_tour = None
            return False  # Fallo
    
    def _actualizar_contenido(self):
        """Actualiza el contenido de la ventana dinámicamente usando StringVars"""
        paso = self.pasos[self.current_step]
        
        # Actualizar textos (sin parpadeos gracias a StringVar)
        self.var_titulo.set(paso["titulo"])
        self.var_descripcion.set(paso["descripcion"])
        self.var_progreso.set(f"Paso {self.current_step + 1} de 13")
        
        # Gestionar visibilidad del botón Anterior
        if self.btn_anterior:
            if self.current_step == 0:
                self.btn_anterior.pack_forget()  # Ocultar en paso 1
            else:
                # Asegurar que esté visible desde paso 2
                if not self.btn_anterior.winfo_ismapped():
                    self.btn_anterior.pack(side="left", padx=5, before=self.btn_siguiente)
        
        # Cambiar texto del botón siguiente en el último paso
        if self.btn_siguiente:
            if self.current_step == len(self.pasos) - 1:
                self.btn_siguiente.configure(text="✓ Finalizar")
            else:
                self.btn_siguiente.configure(text="Siguiente →")
    
    def _paso_siguiente(self):
        """Avanza al siguiente paso o finaliza el tour"""
        if self.current_step < len(self.pasos) - 1:
            self.current_step += 1
            self._actualizar_contenido()
        else:
            # Último paso - finalizar tour
            self._finalizar_tour()
    
    def _paso_anterior(self):
        """Retrocede al paso anterior"""
        if self.current_step > 0:
            self.current_step -= 1
            self._actualizar_contenido()
    
    def _saltar_tour(self):
        """Salta/cancela el tour y cierra la ventana"""
        respuesta = messagebox.askyesno(
            "Saltar Tour",
            "¿Estás seguro de que quieres saltar el tour?\n\n"
            "Podrás iniciarlo nuevamente desde Ajustes.",
            parent=self.ventana_tour if self.ventana_tour else self.app
        )
        
        if respuesta:
            self._cerrar_ventana()
    
    def _finalizar_tour(self):
        """Completa el tour y marca como completado"""
        self.state_manager.marcar_primer_uso_completado()
        self.state_manager.marcar_tour_completado()
        
        messagebox.showinfo(
            "¡Bien hecho!",
            "Tu tour de bienvenida ha terminado.\n\n"
            "Recomendación: Dirígete a CONFIGURACIÓN\n"
            "y configura tu(s) finca(s), sectores y razas.\n\n"
            "Estos son datos base para todo el sistema.",
            parent=self.ventana_tour if self.ventana_tour else self.app
        )
        
        self._cerrar_ventana()
        
        # Navegar a Ajustes/Configuración si es posible
        try:
            if hasattr(self.app, "show_screen"):
                self.app.show_screen("ajustes")  # type: ignore[attr-defined]
        except Exception as e:
            print(f"Error navegando a ajustes: {e}")
    
    def _cerrar_ventana(self):
        """Destruye la ventana del tour"""
        if self.ventana_tour:
            try:
                self.ventana_tour.destroy()
            except:
                pass
            self.ventana_tour = None
            self.ventana_tour = None
    
    def should_start_tour(self) -> bool:
        """Determina si el tour debe ejecutarse automáticamente"""
        es_primer_uso = self.state_manager.es_primer_uso()
        tour_completado = self.state_manager.tour_completado()
        resultado = es_primer_uso or (not tour_completado)
        
        print(f"[TOUR] should_start_tour: es_primer_uso={es_primer_uso}, tour_completado={tour_completado}, resultado={resultado}")
        
        return resultado
    
    def start_tour(self, auto_complete_on_finish: bool = True):
        """Inicia el tour interactivo con ventana modal única"""
        try:
            print("[TOUR] 🎬 Iniciando tour global con ventana única...")
            print(f"[TOUR] Total de pasos: {len(self.pasos)}")
            
            # Resetear al primer paso
            self.current_step = 0
            
            # Cargar logo
            self._cargar_logo()
            
            # Crear ventana única
            if not self._crear_ventana_tour():
                print("[TOUR] ⚠️ Error: No se pudo crear la ventana del tour")
                return
            
            # Mostrar el primer paso
            self._actualizar_contenido()
            
            print("[TOUR] ✅ Tour en ejecución - ventana modal creada")
        except Exception as e:
            print(f"[TOUR] ❌ Error en start_tour(): {e}")
            import traceback
            traceback.print_exc()
    
    def reset_tour(self):
        """Resetea el tour para que vuelva a mostrarse"""
        self.state_manager.reset_tour()
        print("[TOUR] Estado del tour reseteado")
