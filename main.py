"""
Sistema Principal FincaFacil
Módulo unificado para la gestión integral de fincas ganaderas
"""

import os
import sys
import traceback
from pathlib import Path

# Detectar si está ejecutándose como ejecutable empaquetado
if getattr(sys, 'frozen', False):
    # Ejecutándose como ejecutable empaquetado
    current_dir = Path(sys.executable).parent
    base_path = Path(getattr(sys, '_MEIPASS', current_dir))  # type: ignore
else:
    # Ejecutándose como script Python
    current_dir = Path(__file__).parent
    base_path = current_dir


def _write_startup_log(msg: str) -> None:
    """Escribe mensajes tempranos en un log para depurar arranques fallidos."""
    try:
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or str(Path.home())
        log_dir = Path(base) / "FincaFacil" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "startup.log", "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass

# Agregar el directorio raíz al path para imports absolutos
# NOTA: El orden importa. insert(0, ...) inserta al INICIO
# Si haces insert(0, x) luego insert(0, y), y termina ANTES que x
sys.path.insert(0, str(base_path / "src"))  # Primero src/ extraído (_MEIPASS o repo)
sys.path.insert(0, str(base_path))  # Luego raíz de extracción
sys.path.insert(0, str(current_dir))  # Por compatibilidad con ejecuciones locales

# Importaciones de módulos
try:
    print("DEBUG: sys.path[0:3] = " + str(sys.path[0:3]))
    
    print("DEBUG: Importando DashboardModule...")
    from modules.dashboard.dashboard_main import DashboardModule
    print("DEBUG: OK - DashboardModule")
    
    print("DEBUG: Importando AjustesFrame...")
    from modules.ajustes.ajustes_main import AjustesFrame
    print("DEBUG: OK - AjustesFrame")
    
    print("DEBUG: Importando VentasModule...")
    from modules.ventas.ventas_main import VentasModule
    print("DEBUG: OK - VentasModule")
    
    print("DEBUG: Importando logger...")
    from modules.utils.logger import setup_logger, get_logger
    print("DEBUG: OK - Logger")
    
    print("DEBUG: Importando database...")
    from database import inicializar_base_datos, verificar_base_datos, asegurar_esquema_minimo, asegurar_esquema_completo
    print("DEBUG: OK - Database")
    
    # Configuración global
    print("DEBUG: Importando config...")
    from config import config
    print("DEBUG: OK - Config")

    print("DEBUG: Importando ciclo de vida y permisos...")
    from core.app_lifecycle import get_app_lifecycle
    from core.permissions_manager import get_permissions_manager, RoleEnum, PermissionEnum
    print("DEBUG: OK - Ciclo de vida y permisos")
    
except ImportError as e:
    # Logger aun no disponible, registrar en archivo de arranque
    msg = f"ERROR CRITICO: No se pueden importar modulos necesarios: {e}"
    print(msg)
    traceback.print_exc()
    _write_startup_log(msg)
    _write_startup_log(traceback.format_exc())
    sys.exit(1)

import customtkinter as ctk
from tkinter import messagebox
from modules.utils.login_ui import mostrar_login

class FincaFacilApp(ctk.CTk):
    def __init__(self, usuario_actual: str | None = None):
        super().__init__()

        self.title("FincaFácil 🐄 - Gestión Ganadera Profesional")
        
        # Configurar tema ANTES de geometry/state
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Maximizar ventana - método mejorado para Windows
        self.geometry("1400x820")  # Tamaño inicial mínimo
        self.update_idletasks()  # Procesar eventos pendientes
        self.state('zoomed')  # Maximizar en Windows
        
        # Establecer el ícono de la ventana
        try:
            # Buscar icono considerando si está empaquetado
            if getattr(sys, 'frozen', False):
                ico_path = current_dir / "assets" / "Logo.ico"
            else:
                ico_path = Path(__file__).parent / "assets" / "Logo.ico"
            
            if ico_path.exists():
                self.iconbitmap(str(ico_path))
        except Exception as e:
            # Si falla el .ico, continuar sin icono
            pass

        # Configurar logger para la UI
        try:
            self.logger = setup_logger("UI")
            self.logger.info("Interfaz gráfica iniciada")
        except:
            self.logger = None

        # Gestores centrales
        self.lifecycle = get_app_lifecycle()
        self.permissions = get_permissions_manager()

        # Usuario actual (se asigna desde login, fallback admin)
        self.current_user = usuario_actual or "admin"
        try:
            self.permissions.set_current_user(self.current_user, RoleEnum.ADMINISTRADOR)
        except Exception:
            pass

        # Hook de cierre seguro
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ----------- CONTENEDORES PRINCIPALES -----------
        # Frame contenedor del sidebar con estilo mejorado
        sidebar_container = ctk.CTkFrame(
            self, 
            width=200, 
            corner_radius=0,
            fg_color=("#F5F5F5", "#1E1E1E")
        )
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)
        
        self.sidebar = ctk.CTkScrollableFrame(
            sidebar_container, 
            width=190, 
            corner_radius=0,
            fg_color="transparent"
        )
        self.sidebar.pack(fill="both", expand=True, padx=5, pady=5)

        # Área principal para todos los módulos (sin scroll a nivel raíz)
        # Los módulos que necesitan scroll lo implementan internamente para no encoger la ventana.
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=("#FFFFFF", "#1E1E1E"),
        )
        # Colocar main_frame también a la izquierda (después del sidebar) para evitar zona muerta central
        self.main_frame.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        # Forzar propagación para que ocupe todo inmediatamente
        self.main_frame.pack_propagate(True)

        # Barra de estado inferior oculta (no es necesaria, ocupa espacio)
        # self.status_frame = ctk.CTkFrame(self, height=26, fg_color=("#ECEFF1", "#263238"))
        # self.status_frame.pack(side="bottom", fill="x")
        # self._status_label = ctk.CTkLabel(self.status_frame, text="Listo", anchor="w", font=("Segoe UI", 11))
        # self._status_label.pack(side="left", padx=10)
        # self._status_extra = ctk.CTkLabel(self.status_frame, text="", anchor="e", font=("Segoe UI", 11))
        # self._status_extra.pack(side="right", padx=10)

        # Guarda el módulo activo actual
        self.current_module = None
        
        # Control de animaciones en botones
        self.animated_buttons = {}  # {button_key: (frames, current_frame_idx, after_id)}
        self.animation_enabled = True

        # ----------- MENÚ LATERAL -----------
        self.create_sidebar()

        # Cargar pantalla inicial
        self.show_screen("dashboard")
        
        # Generar manual PDF si no existe
        self.after(500, self.verificar_manual_pdf)
        
        # Verificar si es el primer uso y mostrar tour
        self.after(1000, self.verificar_primer_uso)

        # Ejecutar detectores AI en segundo plano al inicio
        self.after(3000, self.ejecutar_ai_startup)

        # Crear menú principal
        self.crear_menu_principal()

    def verificar_manual_pdf(self):
        """Verifica y genera el manual PDF si no existe"""
        try:
            # Path ya está importado al inicio del archivo
            pdf_path = Path("docs/Manual_Usuario_FincaFacil.pdf")
            
            if not pdf_path.exists():
                if self.logger:
                    self.logger.info("Generando manual PDF inicial...")
                
                # Importar en background para no bloquear
                try:
                    from modules.utils.pdf_manual_generator import generar_manual_pdf
                    generar_manual_pdf()
                    if self.logger:
                        self.logger.info("Manual PDF generado correctamente")
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"No se pudo generar manual PDF: {e}")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Error verificando manual PDF: {e}")
    
    def verificar_primer_uso(self):
        """Verifica si es la primera vez usando el sistema e inicia el tour global"""
        try:
            from modules.utils.global_tour import GlobalTour
            
            # Crear gestor del tour global
            global_tour = GlobalTour(self)
            
            # Si es primer uso, iniciar tour automáticamente
            if global_tour.should_start_tour():
                if self.logger:
                    self.logger.info("Primer uso detectado - iniciando tour global")
                self.after(500, global_tour.start_tour)
            else:
                if self.logger:
                    self.logger.info("Sistema ya fue usado antes - tour no necesario")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"No se pudo iniciar tour global: {e}")

    def ejecutar_ai_startup(self):
        """Ejecuta detectores AI en segundo plano al iniciar, sin bloquear UI."""
        try:
            from src.services.ai_anomaly_detector import get_ai_anomaly_detector_service
            from src.services.ai_pattern_detector import get_ai_pattern_detector_service
            from src.core.audit_service import log_event

            anomaly_service = get_ai_anomaly_detector_service()
            pattern_service = get_ai_pattern_detector_service()

            anomalies = anomaly_service.evaluar_anomalias(usuario_id=None, incluir_alertas=True)
            patterns = pattern_service.detectar_patrones(usuario_id=None, incluir_alertas=True)

            if self.logger:
                self.logger.info(
                    f"Startup AI: {len(anomalies)} anomalías, {len(patterns)} patrones"
                )
            try:
                log_event(
                    usuario=self.current_user,
                    modulo="AI",
                    accion="EJECUCION_STARTUP",
                    entidad="inicio",
                    resultado="OK",
                    mensaje=f"{len(anomalies)} anomalías; {len(patterns)} patrones"
                )
            except Exception:
                pass
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Startup AI no ejecutado: {e}")

    def create_sidebar(self):
        # Header con fondo claro para resaltar el logo
        header_frame = ctk.CTkFrame(
            self.sidebar, 
            fg_color=("#FFFFFF", "#2B2B2B"),
            corner_radius=15,
            border_width=2,
            border_color=("#E0E0E0", "#404040"),
            height=170
        )
        header_frame.pack(pady=(10, 20), padx=10, fill="x")
        header_frame.pack_propagate(False)
        
        # Logo grande y prominente como elemento principal
        try:
            from PIL import Image
            logo_path = Path(__file__).parent / "assets" / "Logo.png"
            if logo_path.exists():
                logo_image = Image.open(logo_path)
                # Logo muy grande para que sobresalga
                logo_image = logo_image.resize((130, 130), Image.Resampling.LANCZOS)
                logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(130, 130))
                logo_label = ctk.CTkLabel(header_frame, image=logo_ctk, text="")
                logo_label.pack(pady=(15, 10))
        except Exception as e:
            if self.logger:
                self.logger.warning(f"No se pudo cargar el logo: {e}")
            # Emoji alternativo más grande si falla el logo
            logo_emoji = ctk.CTkLabel(header_frame, text="🐄", font=("Segoe UI", 70))
            logo_emoji.pack(pady=(15, 10))
        
        # Eslogan impactante debajo del logo
        slogan = ctk.CTkLabel(
            header_frame,
            text="La fuerza del campo, la precisión del software.",
            font=("Segoe UI", 11, "italic"),
            text_color=("#37474F", "#B0BEC5"),
            wraplength=200
        )
        slogan.pack(pady=(0, 15))
        
        # Etiqueta de sección
        section_label = ctk.CTkLabel(
            self.sidebar,
            text="📋 MÓDULOS",
            font=("Segoe UI", 11, "bold"),
            text_color=("#616161", "#BDBDBD")
        )
        section_label.pack(pady=(5, 10), padx=15, anchor="w")

        # Botones con iconos PNG grandes y colores mejorados
        try:
            from modules.utils.icons import COLORS, ICON_SYMBOLS
            from PIL import Image
            
            buttons_config = [
                ("dashboard", "Dashboard"),
                ("animales", "Animales"),
                ("reproduccion", "Reproducción"),
                ("salud", "Salud"),
                ("potreros", "Potreros"),
                ("leche", "Pesaje de Leche"),
                ("ventas", "Ventas"),
                ("insumos", "Insumos"),
                ("herramientas", "Herramientas"),
                ("reportes", "Reportes"),
                ("nomina", "Nómina"),
                ("configuracion", "Config."),
                ("ajustes", "Ajustes")
            ]
            
            self.active_button = None
            self.buttons = {}
            self.button_images = {}  # Para mantener referencias de las imágenes
            
            for screen, label in buttons_config:
                color_bg, color_hover = COLORS.get(screen, ("#1976D2", "#2196F3"))
                
                # Intentar cargar icono PNG del módulo
                icon_image = None
                icon_ctk = None
                try:
                    icon_path = Path(__file__).parent / "assets" / f"{screen}.png"
                    if not icon_path.exists():
                        # Intentar con nombres alternativos (singular)
                        if screen == "animales":
                            icon_path = Path(__file__).parent / "assets" / "animal.png"
                        elif screen == "ajustes":
                            icon_path = Path(__file__).parent / "assets" / "ajuste.png"
                        elif screen == "potreros":
                            icon_path = Path(__file__).parent / "assets" / "potrero.png"
                    
                    if icon_path.exists():
                        icon_image = Image.open(icon_path)
                        # Redimensionar icono a 36x36 para los botones
                        icon_image = icon_image.resize((36, 36), Image.Resampling.LANCZOS)
                        icon_ctk = ctk.CTkImage(light_image=icon_image, size=(36, 36))
                        self.button_images[screen] = icon_ctk  # Mantener referencia
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"No se pudo cargar icono para {screen}: {e}")
                
                # Crear botón con icono y etiqueta
                btn = ctk.CTkButton(
                    self.sidebar,
                    text=label,
                    image=icon_ctk,
                    width=180,
                    height=65,
                    font=("Segoe UI", 12, "bold"),
                    fg_color=color_bg,
                    hover_color=color_hover,
                    corner_radius=15,
                    border_width=0,
                    compound="top",  # Icono encima del texto
                    command=lambda s=screen, b=label: self.show_screen_animated(s, b)
                )
                
                btn.pack(pady=8, padx=10)
                self.buttons[label] = btn
        
        except ImportError:
            # Fallback si hay error importando módulo de iconos
            buttons_config_fallback = [
                ("Dashboard", "dashboard", "#1976D2", "#2196F3"),
                ("Animales", "animales", "#2E7D32", "#4CAF50"),
                ("Reproducción", "reproduccion", "#E91E63", "#F06292"),
                ("Salud", "salud", "#C62828", "#EF5350"),
                ("Potreros", "potreros", "#388E3C", "#66BB6A"),
                ("Leche", "leche", "#F57F17", "#FBC02D"),
                ("Ventas", "ventas", "#F57C00", "#FF9800"),
                ("Insumos", "insumos", "#0288D1", "#03A9F4"),
                ("Herramientas", "herramientas", "#616161", "#9E9E9E"),
                ("Reportes", "reportes", "#5E35B1", "#7E57C2"),
                ("Nómina", "nomina", "#00796B", "#26A69A"),
                ("Config.", "configuracion", "#455A64", "#78909C"),
                ("Ajustes", "ajustes", "#37474F", "#607D8B")
            ]
            
            self.active_button = None
            self.buttons = {}
            
            # Cargar emojis como fallback si no hay PNG
            emoji_fallback = {
                "dashboard": "📊",
                "animales": "🐄",
                "reproduccion": "🤰",
                "salud": "🏥",
                "potreros": "🌿",
                "leche": "🥛",
                "ventas": "💰",
                "insumos": "📦",
                "herramientas": "🔧",
                "reportes": "📋",
                "nomina": "👥",
                "configuracion": "⚙️",
                "ajustes": "🎨"
            }
            
            for text, screen, color, hover_color in buttons_config_fallback:
                emoji = emoji_fallback.get(screen, "")
                btn_text = f"{emoji}\n{text}" if emoji else text
                
                btn = ctk.CTkButton(
                    self.sidebar,
                    text=btn_text,
                    width=180,
                    height=65,
                    font=("Segoe UI", 11, "bold"),
                    fg_color=color,
                    hover_color=hover_color,
                    corner_radius=15,
                    border_width=0,
                    command=lambda s=screen, b=text: self.show_screen_animated(s, b)
                )
                btn.pack(pady=8, padx=10)
                self.buttons[text] = btn

    def change_appearance_mode(self, mode):
        # Permite cambiar entre modo claro y oscuro
        if mode == "Claro":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

    def show_screen_animated(self, name, button_text):
        """Cambia de pantalla con efecto visual en el botón activo"""
        # Resetear botón anterior - detener animación
        if self.active_button and self.active_button in self.buttons:
            old_btn = self.buttons[self.active_button]
            old_btn.configure(border_width=0)
            # Cancelar animación previa si existe
            if self.active_button in self.animated_buttons:
                after_id = self.animated_buttons[self.active_button].get('after_id')
                if after_id:
                    try:
                        self.after_cancel(after_id)
                    except:
                        pass
        
        # Destacar botón activo
        if button_text in self.buttons:
            self.buttons[button_text].configure(border_width=4, border_color=("#FFFFFF", "#FFD700"))
            self.active_button = button_text
            
            # Iniciar animación si existe para este módulo
            self._iniciar_animacion_boton(name, button_text)
        self.show_screen(name)
    
    def _iniciar_animacion_boton(self, module_name, button_key):
        """Inicia animación del icono en un botón - deshabilitada (solo emojis)"""
        pass
    
    def _animar_boton(self, button_key):
        """Loop de animación para un botón específico - deshabilitada"""
        pass

    def show_screen(self, name):
        """
        Cambia el contenido del main_frame dependiendo del módulo.
        Si ya existe uno, se destruye antes de cargar el nuevo.
        """
        if self.logger:
            self.logger.info(f"Cambiando a pantalla: {name}")

        # Limpia cualquier contenido previo (más robusto contra módulos que crean frames sueltos)
        try:
            for child in self.main_frame.winfo_children():
                child.destroy()
        except Exception as e:
            if self.logger:
                self.logger.warning(f"No se pudo limpiar completamente main_frame: {e}")
        self.current_module = None

        try:
            # Crea el nuevo módulo según la opción elegida
            if name == "dashboard":
                self.current_module = DashboardModule(self.main_frame)

            elif name == "ajustes":
                self.current_module = AjustesFrame(self.main_frame)

            elif name == "ventas":
                self.current_module = VentasModule(self.main_frame)

            # --- Módulos modernizados ---
            elif name == "animales":
                from modules.animales import AnimalesModule
                self.current_module = AnimalesModule(self.main_frame)
            elif name == "inventario_rapido":
                from modules.animales.inventario_rapido import InventarioRapido
                self.current_module = InventarioRapido(self.main_frame)
            elif name == "inventario":
                from modules.animales.inventario_v2 import InventarioGeneralFrame
                self.current_module = InventarioGeneralFrame(self.main_frame)
            elif name == "reproduccion":
                from modules.reproduccion.reproduccion_main import ReproduccionModule
                self.current_module = ReproduccionModule(self.main_frame)
            elif name == "salud":
                from modules.salud.salud_main import SaludModule
                self.current_module = SaludModule(self.main_frame)
            elif name == "potreros":
                from modules.potreros.potreros_main import PotrerosModule
                self.current_module = PotrerosModule(self.main_frame)
            elif name == "tratamientos":
                # NOTA: Tratamientos ahora está integrado en el módulo de Salud
                from modules.salud.salud_main import SaludModule
                self.current_module = SaludModule(self.main_frame)
            elif name == "nomina":
                from modules.nomina.nomina_main import NominaModule
                self.current_module = NominaModule(self.main_frame)
            elif name == "empleados":
                # NOTA: Empleados ahora está integrado en el módulo de Nómina
                from modules.nomina.nomina_main import NominaModule
                self.current_module = NominaModule(self.main_frame)
            elif name == "reportes":
                try:
                    from modules.reportes.reportes_fase3 import ReportesFase3
                    self.current_module = ReportesFase3(self.main_frame)
                except Exception:
                    from modules.reportes.reportes_main import ReportesModule
                    self.current_module = ReportesModule(self.main_frame)
            elif name == "configuracion":
                from modules.configuracion.__main__ import ConfiguracionModule
                self.current_module = ConfiguracionModule(self.main_frame)
            elif name == "herramientas":
                from modules.herramientas.herramientas_main import HerramientasModule
                self.current_module = HerramientasModule(self.main_frame)
            elif name == "insumos":
                from modules.insumos.insumos_main import InsumosModule
                self.current_module = InsumosModule(self.main_frame)
            elif name == "leche":
                from modules.leche.pesaje_leche import PesajeLecheFrame
                self.current_module = PesajeLecheFrame(self.main_frame)

            else:
                self.current_module = self.create_placeholder_module(
                    "❌ Módulo no encontrado", 
                    f"La pantalla '{name}' no existe"
                )

            # Asegurar que el módulo ocupe todo el ancho disponible sin padding extra
            try:
                if not self.current_module.winfo_manager():
                    self.current_module.pack(fill="both", expand=True, padx=0, pady=0)
                else:
                    # Ajustar cualquier pack existente para remover márgenes laterales
                    self.current_module.pack_configure(padx=0, pady=0)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Error al empaquetar módulo {name}: {e}")

            # Optimización ligera de espacio interno: remover padding de frames de primer nivel
            try:
                for child in self.current_module.winfo_children():
                    # Solo quitar padding en contenedores grandes típicos
                    if isinstance(child, ctk.CTkFrame):
                        # Si el frame no es barra de estado (altura muy pequeña) ni sidebar
                        padx = child.pack_info().get('padx', 0)
                        if isinstance(padx, int):
                            child.pack_configure(padx=max(padx - 3, 0))
            except Exception:
                pass

        except Exception as e:
            error_msg = f"Error al cargar módulo {name}: {e}"
            if self.logger:
                self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)

    def create_placeholder_module(self, title, message):
        """Crea un módulo placeholder para funcionalidades en desarrollo"""
        frame = ctk.CTkFrame(self.main_frame)
        
        # Contenido del placeholder
        title_label = ctk.CTkLabel(
            frame, 
            text=title, 
            font=("Arial", 24, "bold"),
            text_color="#2E8B57"
        )
        title_label.pack(pady=40)
        
        message_label = ctk.CTkLabel(
            frame, 
            text=message,
            font=("Arial", 16),
            text_color="#666666"
        )
        message_label.pack(pady=10)
        
        # Progress bar para indicar desarrollo
        progress = ctk.CTkProgressBar(frame, width=300)
        progress.pack(pady=20)
        progress.set(0.5)  # Medio camino :)
        
        return frame

    def on_closing(self):
        """Cierre controlado con validaciones, backup y auditoría"""
        try:
            # 1) Validaciones y cierres pendientes (lifecycle)
            import asyncio
            try:
                result = asyncio.run(self.lifecycle.on_app_close(usuario_id=self.current_user))
            except RuntimeError:
                # Si ya hay un loop (poco probable en Tk), usar run_until_complete
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.lifecycle.on_app_close(usuario_id=self.current_user))

            if not result:
                messagebox.showwarning(
                    "Cierre cancelado",
                    "No se pudo cerrar la aplicación. Revisa operaciones pendientes o cierres mensuales."
                )
                return

            # 2) Backup automático (mantener lógica previa)
            try:
                if self._necesita_backup_automatico():
                    respuesta = messagebox.askyesno(
                        "Backup Automático",
                        "Han pasado más de 24 horas desde el último backup.\n\n"
                        "¿Desea crear un backup de seguridad antes de salir?",
                        icon='question'
                    )
                    if respuesta:
                        self._hacer_backup_automatico()
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Backup automático falló: {e}")

            # 3) Auditoría de cierre
            try:
                from core.audit_service import log_event
                log_event(
                    usuario=self.current_user,
                    modulo="app",
                    accion="CIERRE",
                    entidad="application",
                    resultado="OK",
                    mensaje="Aplicación cerrada"
                )
            except Exception:
                pass

            if self.logger:
                self.logger.info("Aplicación cerrada por el usuario")

            # 4) Cancelar callbacks pendientes
            for after_id in self.tk.eval('after info').split():
                try:
                    self.after_cancel(after_id)
                except Exception:
                    pass

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en cierre de aplicación: {e}")
        finally:
            self.quit()
            self.destroy()

    # ------------------- Helpers de barra de estado (deshabilitado para ahorrar espacio) -------------------
    def update_status(self, message: str, extra: str | None = None):
        """Actualiza la barra de estado inferior (deshabilitada para ahorrar espacio).
        Args:
            message: Texto principal a la izquierda.
            extra: Información adicional (ej. BD, fecha backup) a la derecha.
        """
        # Barra de estado deshabilitada para aprovechar espacio vertical
        pass
    
    def _necesita_backup_automatico(self):
        """Verifica si han pasado más de 24 horas desde el último backup"""
        try:
            from pathlib import Path
            from datetime import datetime, timedelta
            
            backup_dir = config.BACKUP_DIR
            if not backup_dir.exists():
                return True  # Si no hay carpeta de backup, crear uno
            
            # Buscar el backup más reciente
            backups = list(backup_dir.glob("*.db"))
            if not backups:
                return True  # No hay backups
            
            ultimo_backup = max(backups, key=lambda p: p.stat().st_mtime)
            tiempo_ultimo = datetime.fromtimestamp(ultimo_backup.stat().st_mtime)
            tiempo_actual = datetime.now()
            
            # Retornar True si han pasado más de 24 horas
            return (tiempo_actual - tiempo_ultimo) > timedelta(hours=24)
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Error verificando backup automático: {e}")
            return False  # En caso de error, no forzar backup
    
    def _hacer_backup_automatico(self):
        """Crea un backup automático de la base de datos"""
        try:
            import shutil
            from pathlib import Path
            from datetime import datetime
            
            # Rutas
            from database.database import get_db_path_safe
            db_path = get_db_path_safe()
            if not db_path or not db_path.exists():
                return
            
            backup_dir = config.BACKUP_DIR
            backup_dir.mkdir(exist_ok=True, parents=True)
            
            # Nombre del backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"fincafacil_auto_{timestamp}.db"
            backup_path = backup_dir / backup_name
            
            # Copiar base de datos
            shutil.copy2(str(db_path), str(backup_path))
            
            if self.logger:
                self.logger.info(f"Backup automático creado: {backup_name}")
            
            messagebox.showinfo(
                "Backup Creado",
                f"[OK] Backup automatico creado exitosamente:\n{backup_name}"
            )
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creando backup automático: {e}")
            messagebox.showwarning(
                "Advertencia",
                f"No se pudo crear el backup automático:\n{e}"
            )

    def crear_menu_principal(self):
        """Crea el menú principal de la aplicación"""
        pass  # Elimino el menú principal ya que no es necesario

def mostrar_banner(logger):
    """Registra inicio del sistema en el log"""
    logger.info("� FincaFácil v2.0 - Gestión Ganadera Profesional")

def verificar_dependencias():
    """
    Verifica que todas las dependencias necesarias estén disponibles
    """
    dependencias_ok = True
    
    # Verificar módulos críticos
    modulos_criticos = [
        'customtkinter',
        'database.database',
        'modules.utils.logger',
        'modules.dashboard.dashboard_main',
        'modules.ajustes.ajustes_main'
    ]
    
    logger = get_logger("Dependencias")
    for modulo in modulos_criticos:
        try:
            __import__(modulo)
        except ImportError as e:
            logger.error(f"Módulo crítico no encontrado: {modulo} - {e}")
            dependencias_ok = False
    
    return dependencias_ok

def inicializar_sistema():
    """
    Inicializa todos los componentes del sistema
    """
    logger = get_logger("Inicializacion")
    
    try:
        # 1. Verificar base de datos
        logger.info("Verificando estado de la base de datos...")
        if not verificar_base_datos():
            logger.info("Inicializando base de datos...")
            if not inicializar_base_datos():
                logger.error("Fallo en inicialización de base de datos")
                return False
            logger.info("Base de datos inicializada exitosamente")
        else:
            logger.info("Base de datos verificada correctamente")

        # 1.1. Asegurar esquema mínimo para compatibilidad con BD antiguas
        try:
            asegurar_esquema_minimo()
        except Exception as mig_e:
            logger.warning(f"No se pudo asegurar esquema mínimo: {mig_e}")
        # 1.2. Asegurar esquema completo (migración ligera: columnas claves como id_sector)
        try:
            asegurar_esquema_completo()
        except Exception as mig_e2:
            logger.warning(f"No se pudo asegurar esquema completo: {mig_e2}")
        
        logger.info("[OK] Sistema inicializado correctamente")
        return True
        
    except Exception as e:
        logger.critical(f"Error en inicialización del sistema: {e}")
        return False

def main():
    """
    Función principal que inicializa y ejecuta el sistema FincaFacil
    """
    # Logger temporal para inicio
    logger = None
    
    try:
        # Configurar logging desde el inicio
        logger = setup_logger()
        logger.info("[START] Iniciando FincaFacil...")
        
        # Verificar dependencias
        logger.info("Verificando dependencias del sistema...")
        if not verificar_dependencias():
            logger.critical("Faltan dependencias críticas. No se puede continuar.")
            sys.exit(1)
        
        # Inicializar sistema
        if not inicializar_sistema():
            logger.error("Fallo en inicialización del sistema")
            sys.exit(1)
        
        # Mostrar interfaz
        mostrar_banner(logger)
        logger.info("Sistema listo. Cargando interfaz principal...")
        
        # Mostrar login (ANTES de iniciar la app principal)
        logger.info("Mostrando pantalla de login...")
        usuario_logueado = mostrar_login()
        
        if not usuario_logueado:
            logger.info("El usuario canceló el login")
            sys.exit(0)
        
        logger.info(f"Usuario '{usuario_logueado}' ha iniciado sesión")
        
        # Ejecutar aplicación
        app = FincaFacilApp(usuario_logueado)
        app.mainloop()
        
        logger.info("👋 FincaFacil finalizado correctamente")
        
    except KeyboardInterrupt:
        if logger:
            logger.info("Aplicación interrumpida por el usuario")
        
    except Exception as e:
        if logger:
            logger.critical(f"Error crítico en la aplicación: {e}")
            logger.critical(traceback.format_exc())
        else:
            print(f"❌ Error crítico: {e}\n{traceback.format_exc()}")

        # Mostrar un mensaje visible al usuario con la ruta del log
        try:
            from tkinter import messagebox
            try:
                from config import config as app_config
                log_path = str(app_config.LOG_DIR / "fincafacil.log")
            except Exception:
                log_path = "logs\\fincafacil.log"
            messagebox.showerror(
                "FincaFacil - Error",
                "Se produjo un error crítico y la aplicación debe cerrarse.\n\n"
                f"Detalle: {e}\n\nRevise el archivo de registro para más información:\n{log_path}"
            )
        except Exception:
            # Si no se puede mostrar el cuadro de diálogo, continuar con el cierre
            pass
        sys.exit(1)

if __name__ == "__main__":
    # Usar flujo principal que verifica/migra BD antes de abrir UI
    main()