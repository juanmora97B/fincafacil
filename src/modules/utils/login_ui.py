"""
Interfaz de login y registro profesional con navegación por frames.
Temática: Finca/Campo (verdes profundos y tonos tierra)
"""
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from PIL import Image
from config import config
from modules.utils.usuario_manager import UsuarioManager
from modules.utils.license_manager import LicenseManager
from modules.utils.tour_state_manager import TourStateManager
import logging

logger = logging.getLogger(__name__)

# Paleta de colores temática finca/campo
COLORS = {
    'verde_profundo': '#2E7D32',      # Verde oscuro (botones principales)
    'verde_hover': '#388E3C',          # Verde hover
    'verde_claro': '#66BB6A',          # Verde claro (acentos)
    'tierra': '#795548',               # Marrón tierra
    'tierra_hover': '#8D6E63',         # Marrón claro hover
    'beige': '#EFEBE9',                # Beige fondo
    'gris_texto': '#5D4037',           # Gris/marrón oscuro texto
    'blanco': '#FFFFFF',
    'error': '#C62828',
    'exito': '#2E7D32'
}


class LoginWindow(ctk.CTk):
    """Ventana profesional de login con navegación dinámica"""
    
    def __init__(self):
        super().__init__()
        self.title("FincaFácil - Gestión Ganadera Profesional")
        self.geometry("900x650")
        self.resizable(False, False)
        
        # Configuración visual
        ctk.set_appearance_mode("light")
        
        # Centrar ventana
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 650) // 2
        self.geometry(f"+{x}+{y}")
        
        # Managers
        self.usuario_manager = UsuarioManager()
        self.license_manager = LicenseManager()
        self.usuario_logueado = None
        
        # Cargar logo sin pixelación
        self.logo_image = None
        logo_path = Path(config.ASSETS_DIR) / "Logo.png"
        if logo_path.exists():
            try:
                img = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(img, size=(120, 120))
                self.logo_small = ctk.CTkImage(img, size=(40, 40))
            except Exception as e:
                logger.warning(f"No se pudo cargar logo: {e}")
        
        # Icono
        try:
            ico_path = Path(config.ASSETS_DIR) / "Logo.ico"
            if ico_path.exists():
                self.iconbitmap(str(ico_path))
        except:
            pass
        
        self._crear_interfaz()
        self._mostrar_vista_inicial()
    
    def _crear_interfaz(self):
        """Crea la estructura principal de la interfaz"""
        # Frame principal con dos columnas
        self.configure(fg_color=COLORS['beige'])
        
        # Panel izquierdo decorativo
        self.panel_izquierdo = ctk.CTkFrame(
            self,
            width=350,
            corner_radius=0,
            fg_color=COLORS['verde_profundo']
        )
        self.panel_izquierdo.pack(side="left", fill="both")
        self.panel_izquierdo.pack_propagate(False)
        
        # Contenido panel izquierdo
        if self.logo_image:
            ctk.CTkLabel(
                self.panel_izquierdo,
                image=self.logo_image,
                text=""
            ).pack(pady=(80, 20))
        
        ctk.CTkLabel(
            self.panel_izquierdo,
            text="FincaFácil",
            font=("Segoe UI", 36, "bold"),
            text_color=COLORS['blanco']
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            self.panel_izquierdo,
            text="Gestión Ganadera Profesional",
            font=("Segoe UI", 14),
            text_color=COLORS['verde_claro']
        ).pack(pady=(0, 40))
        
        ctk.CTkLabel(
            self.panel_izquierdo,
            text="🐄 Control de Animales\n📊 Reportes en Tiempo Real\n💰 Gestión Financiera\n📈 Analytics Avanzados",
            font=("Segoe UI", 13),
            text_color=COLORS['blanco'],
            justify="left"
        ).pack(pady=20, padx=30)
        
        # Panel derecho para contenido dinámico
        self.panel_derecho = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS['beige']
        )
        self.panel_derecho.pack(side="right", fill="both", expand=True)
        
        # Frame contenedor para las vistas
        self.frame_contenido = ctk.CTkFrame(
            self.panel_derecho,
            fg_color="transparent"
        )
        self.frame_contenido.pack(fill="both", expand=True, padx=40, pady=40)
    
    def _limpiar_contenido(self):
        """Limpia el frame de contenido"""
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()
    
    def _mostrar_vista_inicial(self):
        """Decide qué vista mostrar inicialmente"""
        if self.usuario_manager.existe_algun_usuario():
            self._mostrar_vista_login()
        else:
            self._mostrar_vista_registro()
    
    def _crear_boton_accion(self, parent, texto, comando, color=None):
        """Crea un botón estilizado con efecto hover"""
        color_bg = color or COLORS['verde_profundo']
        color_hover = COLORS['verde_hover'] if not color else COLORS['tierra_hover']
        
        btn = ctk.CTkButton(
            parent,
            text=texto,
            command=comando,
            height=45,
            font=("Segoe UI", 14, "bold"),
            fg_color=color_bg,
            hover_color=color_hover,
            corner_radius=8
        )
        return btn
    
    def _crear_boton_link(self, parent, texto, comando):
        """Crea un botón estilo link"""
        btn = ctk.CTkButton(
            parent,
            text=texto,
            command=comando,
            height=30,
            font=("Segoe UI", 11, "underline"),
            fg_color="transparent",
            hover_color=COLORS['beige'],
            text_color=COLORS['tierra'],
            cursor="hand2"
        )
        return btn
    
    # ==================== VISTA LOGIN ====================
    
    def _mostrar_vista_login(self):
        """Vista de inicio de sesión"""
        self._limpiar_contenido()
        
        # Título
        ctk.CTkLabel(
            self.frame_contenido,
            text="Iniciar Sesión",
            font=("Segoe UI", 28, "bold"),
            text_color=COLORS['gris_texto']
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self.frame_contenido,
            text="Ingresa tus credenciales para continuar",
            font=("Segoe UI", 12),
            text_color=COLORS['tierra']
        ).pack(pady=(0, 40))
        
        # Usuario
        ctk.CTkLabel(
            self.frame_contenido,
            text="Usuario",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['gris_texto'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.entry_usuario = ctk.CTkEntry(
            self.frame_contenido,
            placeholder_text="juan mora",
            height=45,
            font=("Segoe UI", 13),
            border_color=COLORS['verde_profundo'],
            border_width=2
        )
        self.entry_usuario.pack(fill="x", pady=(0, 20))
        
        # Contraseña
        ctk.CTkLabel(
            self.frame_contenido,
            text="Contraseña",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['gris_texto'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.entry_contraseña = ctk.CTkEntry(
            self.frame_contenido,
            placeholder_text="••••••••••",
            show="●",
            height=45,
            font=("Segoe UI", 13),
            border_color=COLORS['verde_profundo'],
            border_width=2
        )
        self.entry_contraseña.pack(fill="x", pady=(0, 10))
        self.entry_contraseña.bind("<Return>", lambda e: self._validar_login())
        
        # Link recuperar contraseña
        self._crear_boton_link(
            self.frame_contenido,
            "¿Olvidaste tu contraseña?",
            self._mostrar_vista_recuperar
        ).pack(anchor="e", pady=(0, 30))
        
        # Botón ingresar
        self._crear_boton_accion(
            self.frame_contenido,
            "Ingresar",
            self._validar_login
        ).pack(fill="x", pady=(0, 20))
        
        # Separador
        ctk.CTkLabel(
            self.frame_contenido,
            text="─────  o  ─────",
            font=("Segoe UI", 11),
            text_color=COLORS['tierra']
        ).pack(pady=10)
        
        # Botón crear cuenta
        self._crear_boton_accion(
            self.frame_contenido,
            "Crear Nueva Cuenta",
            self._mostrar_vista_registro,
            color=COLORS['tierra']
        ).pack(fill="x", pady=20)
        
        # Info
        ctk.CTkLabel(
            self.frame_contenido,
            text="Periodo de prueba: 6 meses\nSin tarjeta de crédito requerida",
            font=("Segoe UI", 10),
            text_color=COLORS['tierra'],
            justify="center"
        ).pack(pady=10)
    
    # ==================== VISTA REGISTRO ====================
    
    def _mostrar_vista_registro(self):
        """Vista de registro de nuevo usuario"""
        self._limpiar_contenido()
        
        # Título
        ctk.CTkLabel(
            self.frame_contenido,
            text="Crear Cuenta",
            font=("Segoe UI", 28, "bold"),
            text_color=COLORS['gris_texto']
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self.frame_contenido,
            text="Regístrate para comenzar a usar FincaFácil",
            font=("Segoe UI", 12),
            text_color=COLORS['tierra']
        ).pack(pady=(0, 30))
        
        # Usuario
        ctk.CTkLabel(
            self.frame_contenido,
            text="Usuario *",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS['gris_texto'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.entry_usuario_reg = ctk.CTkEntry(
            self.frame_contenido,
            placeholder_text="Elige un nombre de usuario",
            height=40,
            font=("Segoe UI", 12),
            border_color=COLORS['verde_profundo'],
            border_width=2
        )
        self.entry_usuario_reg.pack(fill="x", pady=(0, 15))
        
        # Email
        ctk.CTkLabel(
            self.frame_contenido,
            text="Email (opcional)",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS['gris_texto'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.entry_email = ctk.CTkEntry(
            self.frame_contenido,
            placeholder_text="ejemplo@correo.com",
            height=40,
            font=("Segoe UI", 12),
            border_color=COLORS['verde_profundo'],
            border_width=2
        )
        self.entry_email.pack(fill="x", pady=(0, 15))
        
        # Contraseña
        ctk.CTkLabel(
            self.frame_contenido,
            text="Contraseña *",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS['gris_texto'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.entry_contraseña_reg = ctk.CTkEntry(
            self.frame_contenido,
            placeholder_text="Mínimo 6 caracteres",
            show="●",
            height=40,
            font=("Segoe UI", 12),
            border_color=COLORS['verde_profundo'],
            border_width=2
        )
        self.entry_contraseña_reg.pack(fill="x", pady=(0, 15))
        
        # Confirmar contraseña
        ctk.CTkLabel(
            self.frame_contenido,
            text="Confirmar Contraseña *",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS['gris_texto'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.entry_confirmar = ctk.CTkEntry(
            self.frame_contenido,
            placeholder_text="Repite tu contraseña",
            show="●",
            height=40,
            font=("Segoe UI", 12),
            border_color=COLORS['verde_profundo'],
            border_width=2
        )
        self.entry_confirmar.pack(fill="x", pady=(0, 25))
        
        # Botón registrar
        self._crear_boton_accion(
            self.frame_contenido,
            "Crear Cuenta",
            self._registrar_usuario
        ).pack(fill="x", pady=(0, 15))
        
        # Volver al login
        frame_link = ctk.CTkFrame(self.frame_contenido, fg_color="transparent")
        frame_link.pack(pady=10)
        
        ctk.CTkLabel(
            frame_link,
            text="¿Ya tienes cuenta?  ",
            font=("Segoe UI", 11),
            text_color=COLORS['tierra']
        ).pack(side="left")
        
        self._crear_boton_link(
            frame_link,
            "Inicia sesión aquí",
            self._mostrar_vista_login
        ).pack(side="left")
    
    # ==================== VISTA RECUPERAR ====================
    
    def _mostrar_vista_recuperar(self):
        """Vista de recuperación de contraseña"""
        self._limpiar_contenido()
        
        # Título
        ctk.CTkLabel(
            self.frame_contenido,
            text="Recuperar Contraseña",
            font=("Segoe UI", 28, "bold"),
            text_color=COLORS['gris_texto']
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self.frame_contenido,
            text="Ingresa tu usuario o email para recuperar tu cuenta",
            font=("Segoe UI", 12),
            text_color=COLORS['tierra'],
            wraplength=400
        ).pack(pady=(0, 40))
        
        # Campo usuario/email
        ctk.CTkLabel(
            self.frame_contenido,
            text="Usuario o Email",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['gris_texto'],
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.entry_recuperar = ctk.CTkEntry(
            self.frame_contenido,
            placeholder_text="Tu usuario o correo electrónico",
            height=45,
            font=("Segoe UI", 13),
            border_color=COLORS['verde_profundo'],
            border_width=2
        )
        self.entry_recuperar.pack(fill="x", pady=(0, 30))
        
        # Botón enviar
        self._crear_boton_accion(
            self.frame_contenido,
            "Enviar Instrucciones",
            self._procesar_recuperacion
        ).pack(fill="x", pady=(0, 20))
        
        # Info
        ctk.CTkLabel(
            self.frame_contenido,
            text="📧 Te enviaremos instrucciones para restablecer tu contraseña",
            font=("Segoe UI", 11),
            text_color=COLORS['tierra'],
            wraplength=400
        ).pack(pady=20)
        
        # Volver al login
        frame_link = ctk.CTkFrame(self.frame_contenido, fg_color="transparent")
        frame_link.pack(pady=20)
        
        ctk.CTkLabel(
            frame_link,
            text="← ",
            font=("Segoe UI", 14),
            text_color=COLORS['tierra']
        ).pack(side="left")
        
        self._crear_boton_link(
            frame_link,
            "Volver al inicio de sesión",
            self._mostrar_vista_login
        ).pack(side="left")
    
    # ==================== LÓGICA DE NEGOCIO ====================
    
    def _validar_login(self):
        """Valida credenciales y cierra si es exitoso"""
        usuario = self.entry_usuario.get().strip()
        contraseña = self.entry_contraseña.get()
        
        if not usuario or not contraseña:
            self._mostrar_error("Por favor completa todos los campos")
            return
        
        exito, mensaje = self.usuario_manager.validar_login(usuario, contraseña)
        
        if exito:
            self.usuario_manager.guardar_sesion(usuario)
            self.usuario_logueado = usuario
            self._mostrar_exito("¡Bienvenido!")
            self.after(500, self.destroy)
        else:
            self._mostrar_error(mensaje)
            self.entry_contraseña.delete(0, "end")
    
    def _registrar_usuario(self):
        """Registra un nuevo usuario"""
        usuario = self.entry_usuario_reg.get().strip()
        email = self.entry_email.get().strip() or None
        contraseña = self.entry_contraseña_reg.get()
        confirmar = self.entry_confirmar.get()
        
        # Validaciones
        if not usuario or not contraseña:
            self._mostrar_error("Usuario y contraseña son obligatorios")
            return
        
        if len(contraseña) < 6:
            self._mostrar_error("La contraseña debe tener al menos 6 caracteres")
            return
        
        if contraseña != confirmar:
            self._mostrar_error("Las contraseñas no coinciden")
            return
        
        # Intentar registrar
        exito, mensaje = self.usuario_manager.registrar_usuario(usuario, contraseña, email or "")  # type: ignore[arg-type]
        
        if exito:
            # Crear licencia de prueba
            try:
                with self.usuario_manager.db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM usuario WHERE nombre = ?", (usuario,))
                    resultado = cursor.fetchone()
                    
                    if resultado:
                        usuario_id = resultado[0]
                        self.license_manager.crear_licencia_prueba(usuario_id)
                        logger.info(f"Licencia de prueba creada para {usuario}")
                        # Reset tour
                        try:
                            TourStateManager().reset_tour()
                        except:
                            pass
            except Exception as e:
                logger.error(f"Error al crear licencia: {e}")
            
            self._mostrar_exito(f"¡Cuenta creada exitosamente!\nBienvenido {usuario}")
            self.after(1500, lambda: [
                self.usuario_manager.guardar_sesion(usuario),
                setattr(self, 'usuario_logueado', usuario),
                self.destroy()
            ])
        else:
            self._mostrar_error(mensaje)
    
    def _procesar_recuperacion(self):
        """Simula el proceso de recuperación de contraseña"""
        usuario_email = self.entry_recuperar.get().strip()
        
        if not usuario_email:
            self._mostrar_error("Ingresa tu usuario o email")
            return
        
        # Verificar si existe el usuario
        try:
            with self.usuario_manager.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM usuario WHERE nombre = ? OR email = ?",
                    (usuario_email, usuario_email)
                )
                existe = cursor.fetchone()
                
                if existe:
                    self._mostrar_exito(
                        f"✓ Instrucciones enviadas\n\n"
                        f"Hemos enviado un email con los pasos para recuperar tu contraseña.\n"
                        f"Por favor revisa tu bandeja de entrada."
                    )
                    self.after(2000, self._mostrar_vista_login)
                else:
                    self._mostrar_error("Usuario o email no encontrado")
        except Exception as e:
            logger.error(f"Error en recuperación: {e}")
            self._mostrar_error("Error al procesar la solicitud")
    
    def _mostrar_error(self, mensaje):
        """Muestra mensaje de error con estilo"""
        messagebox.showerror("Error", mensaje, parent=self)
    
    def _mostrar_exito(self, mensaje):
        """Muestra mensaje de éxito con estilo"""
        messagebox.showinfo("Éxito", mensaje, parent=self)
    
    def get_usuario_logueado(self):
        """Retorna el usuario que inició sesión"""
        return self.usuario_logueado


def mostrar_login() -> str:
    """
    Muestra la ventana de login y retorna el usuario logueado.
    
    Returns:
        nombre del usuario logueado o cadena vacía si se cancela
    """
    login_window = LoginWindow()
    login_window.mainloop()
    return login_window.get_usuario_logueado() or ""  # type: ignore[return-value]
