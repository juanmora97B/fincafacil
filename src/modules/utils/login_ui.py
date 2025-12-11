"""
Interfaz de login y registro profesional.
"""
import customtkinter as ctk
from tkinter import messagebox
from modules.utils.usuario_manager import UsuarioManager
from modules.utils.license_manager import LicenseManager
import logging

logger = logging.getLogger(__name__)


class LoginWindow(ctk.CTk):
    """Ventana profesional de login"""
    
    def __init__(self):
        super().__init__()
        self.title("FincaFácil - Login")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Configuración visual
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Centro la ventana
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        self.usuario_manager = UsuarioManager()
        self.license_manager = LicenseManager()
        self.usuario_logueado = None
        
        # Iconbitmap
        try:
            self.iconbitmap("assets/Logo.ico")
        except:
            pass
        
        self._crear_widgets()
        self._mostrar_pantalla_principal()
    
    def _limpiar_widgets(self):
        """Limpia todos los widgets del frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def _crear_widgets(self):
        """Crea el frame principal"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _mostrar_pantalla_principal(self):
        """Muestra la pantalla principal según si hay usuarios"""
        self._limpiar_widgets()
        
        if self.usuario_manager.existe_algun_usuario():
            self._mostrar_login()
        else:
            self._mostrar_registro_inicial()
    
    def _mostrar_registro_inicial(self):
        """Pantalla de registro para primer usuario"""
        titulo = ctk.CTkLabel(self.main_frame, text="FincaFácil", font=("Arial", 32, "bold"))
        titulo.pack(pady=20)
        
        subtitulo = ctk.CTkLabel(self.main_frame, text="Crear cuenta inicial", font=("Arial", 16))
        subtitulo.pack(pady=10)
        
        # Usuario
        ctk.CTkLabel(self.main_frame, text="Usuario:", font=("Arial", 12)).pack(anchor="w", pady=(20, 5))
        self.entry_usuario_reg = ctk.CTkEntry(self.main_frame, placeholder_text="Ingresa tu usuario")
        self.entry_usuario_reg.pack(fill="x", pady=(0, 15))
        
        # Email (opcional)
        ctk.CTkLabel(self.main_frame, text="Email (opcional):", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        self.entry_email = ctk.CTkEntry(self.main_frame, placeholder_text="ejemplo@correo.com")
        self.entry_email.pack(fill="x", pady=(0, 15))
        
        # Contraseña
        ctk.CTkLabel(self.main_frame, text="Contraseña:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        self.entry_contraseña_reg = ctk.CTkEntry(self.main_frame, placeholder_text="Mínimo 6 caracteres", show="●")
        self.entry_contraseña_reg.pack(fill="x", pady=(0, 15))
        
        # Confirmar contraseña
        ctk.CTkLabel(self.main_frame, text="Confirmar contraseña:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        self.entry_confirmar = ctk.CTkEntry(self.main_frame, placeholder_text="Repite tu contraseña", show="●")
        self.entry_confirmar.pack(fill="x", pady=(0, 20))
        
        # Botón registrar
        btn_registrar = ctk.CTkButton(
            self.main_frame,
            text="Crear Cuenta",
            command=self._registrar_primer_usuario,
            height=40,
            font=("Arial", 14, "bold")
        )
        btn_registrar.pack(fill="x", pady=10)
    
    def _mostrar_login(self):
        """Pantalla de login"""
        titulo = ctk.CTkLabel(self.main_frame, text="FincaFácil", font=("Arial", 32, "bold"))
        titulo.pack(pady=30)
        
        subtitulo = ctk.CTkLabel(self.main_frame, text="Inicia sesión", font=("Arial", 14))
        subtitulo.pack(pady=(0, 30))
        
        # Usuario
        ctk.CTkLabel(self.main_frame, text="Usuario:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        self.entry_usuario = ctk.CTkEntry(self.main_frame, placeholder_text="Tu usuario")
        self.entry_usuario.pack(fill="x", pady=(0, 15))
        
        # Contraseña
        ctk.CTkLabel(self.main_frame, text="Contraseña:", font=("Arial", 12)).pack(anchor="w", pady=(0, 5))
        self.entry_contraseña = ctk.CTkEntry(self.main_frame, placeholder_text="Tu contraseña", show="●")
        self.entry_contraseña.pack(fill="x", pady=(0, 20))
        self.entry_contraseña.bind("<Return>", lambda e: self._validar_login())
        
        # Botón login
        btn_login = ctk.CTkButton(
            self.main_frame,
            text="Ingresar",
            command=self._validar_login,
            height=40,
            font=("Arial", 14, "bold")
        )
        btn_login.pack(fill="x", pady=10)
        
        # Información
        info_label = ctk.CTkLabel(
            self.login_frame,
            text="Periodo de prueba: 6 meses\nSin tarjeta de crédito requerida",
            font=("Arial", 10),
            text_color="gray",
            justify="center"
        )
        info_label.pack(pady=30)
    
    def _registrar_primer_usuario(self):
        """Registra el primer usuario del sistema"""
        usuario = self.entry_usuario_reg.get().strip()
        email = self.entry_email.get().strip() or None
        contraseña = self.entry_contraseña_reg.get()
        confirmar = self.entry_confirmar.get()
        
        if not usuario or not contraseña:
            messagebox.showwarning("Atención", "Completa todos los campos requeridos")
            return
        
        if contraseña != confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        exito, mensaje = self.usuario_manager.registrar_usuario(usuario, contraseña, email)
        
        if exito:
            # Obtener ID del usuario recién creado
            try:
                with self.usuario_manager.db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM usuario WHERE nombre = ?", (usuario,))
                    resultado = cursor.fetchone()
                    
                    if resultado:
                        usuario_id = resultado[0]
                        # Crear licencia de prueba
                        self.license_manager.crear_licencia_prueba(usuario_id)
                        logger.info(f"Licencia de prueba creada para nuevo usuario {usuario}")
            except Exception as e:
                logger.error(f"Error al crear licencia de prueba: {e}")
            
            messagebox.showinfo("Éxito", mensaje)
            self.usuario_manager.guardar_sesion(usuario)
            self.usuario_logueado = usuario
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)
    
    def _validar_login(self):
        """Valida el login"""
        usuario = self.entry_usuario.get().strip()
        contraseña = self.entry_contraseña.get()
        
        if not usuario or not contraseña:
            messagebox.showwarning("Atención", "Ingresa usuario y contraseña")
            return
        
        exito, mensaje = self.usuario_manager.validar_login(usuario, contraseña)
        
        if exito:
            self.usuario_manager.guardar_sesion(usuario)
            self.usuario_logueado = usuario
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)
            self.entry_contraseña.delete(0, "end")
    
    def get_usuario_logueado(self):
        """Retorna el usuario que inició sesión"""
        return self.usuario_logueado


def mostrar_login() -> str:
    """
    Muestra la ventana de login y retorna el usuario logueado.
    
    Returns:
        nombre del usuario logueado o None si se cancela
    """
    login_window = LoginWindow()
    login_window.mainloop()
    return login_window.get_usuario_logueado()
