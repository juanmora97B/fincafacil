"""
Interfaz de licencia para el módulo de Ajustes.
Muestra estado de la licencia y permite activar códigos.
"""
import customtkinter as ctk
from tkinter import messagebox
from modules.utils.license_manager import LicenseManager
from modules.utils.usuario_manager import UsuarioManager
import logging

logger = logging.getLogger(__name__)


class LicenseFrame(ctk.CTkFrame):
    """Panel de gestión de licencia dentro de Ajustes"""
    
    def __init__(self, master, usuario_id: int | None = None):
        super().__init__(master)
        
        self.usuario_id = usuario_id
        self.license_manager = LicenseManager()
        self.usuario_manager = UsuarioManager()
        
        # Si no hay usuario_id, intentar obtenerlo de la sesión
        if self.usuario_id is None:
            usuario_actual = self.usuario_manager.obtener_usuario_actual()
            if usuario_actual:
                # Obtener ID del usuario
                with self.usuario_manager.db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM usuario WHERE nombre = ?", (usuario_actual["nombre"],))
                    resultado = cursor.fetchone()
                    if resultado:
                        self.usuario_id = resultado[0]
        
        self._crear_widgets()
    
    def _crear_widgets(self):
        """Crea los widgets del panel de licencia"""
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="Estado de Licencia",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=(0, 15))
        
        # Frame de información
        info_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#F0F0F0", "#2a2a2a"))
        info_frame.pack(fill="x", pady=10)
        
        # Obtener estado
        if self.usuario_id:
            estado = self.license_manager.obtener_estado_licencia(self.usuario_id)
        else:
            estado = {
                "tipo": "sin_licencia",
                "dias_restantes": 0,
                "fecha_expiracion": None,
                "estado": "inactiva"
            }
        
        # Tipo de licencia
        tipo_licencia = estado["tipo"].upper()
        color_tipo = "#4CAF50" if estado["estado"] == "activa" else "#F44336"
        
        tipo_label = ctk.CTkLabel(
            info_frame,
            text=f"Tipo de Licencia: {tipo_licencia}",
            font=("Arial", 12, "bold"),
            text_color=color_tipo
        )
        tipo_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Días restantes
        if estado["estado"] == "activa":
            dias_text = f"Días restantes: {estado['dias_restantes']} días"
            if estado["dias_restantes"] > 7:
                dias_color = "#4CAF50"
            elif estado["dias_restantes"] > 0:
                dias_color = "#FF9800"
            else:
                dias_color = "#F44336"
        else:
            dias_text = "Licencia expirada"
            dias_color = "#F44336"
        
        dias_label = ctk.CTkLabel(
            info_frame,
            text=dias_text,
            font=("Arial", 11),
            text_color=dias_color
        )
        dias_label.pack(anchor="w", padx=15, pady=5)
        
        # Fecha de expiración
        if estado["fecha_expiracion"]:
            fecha_label = ctk.CTkLabel(
                info_frame,
                text=f"Vencimiento: {estado['fecha_expiracion'][:10]}",
                font=("Arial", 10),
                text_color="gray"
            )
            fecha_label.pack(anchor="w", padx=15, pady=(5, 10))
        
        # Separador
        separador = ctk.CTkFrame(self, height=1, fg_color="gray")
        separador.pack(fill="x", pady=10)
        
        # Sección de activación (solo si está en período de prueba)
        if estado["tipo"] == "prueba":
            self._crear_panel_activacion()
        
        # Información adicional
        info_texto = ctk.CTkLabel(
            self,
            text="Prueba gratuita: 6 meses\nSin tarjeta de crédito requerida\n\n"
                 "Para activar versión permanente, "
                 "contacta a jfburitica97@gmail.com\nTel: 3013869653",
            font=("Arial", 10),
            text_color="gray",
            justify="left"
        )
        info_texto.pack(pady=10)
    
    def _crear_panel_activacion(self):
        """Crea el panel para activar licencia con código"""
        titulo_act = ctk.CTkLabel(
            self,
            text="Activar Licencia Permanente",
            font=("Arial", 14, "bold")
        )
        titulo_act.pack(pady=(10, 5))
        
        # Entrada de código
        ctk.CTkLabel(
            self,
            text="Ingresa tu código de activación:",
            font=("Arial", 10)
        ).pack(anchor="w", padx=5)
        
        entry_frame = ctk.CTkFrame(self)
        entry_frame.pack(fill="x", pady=5)
        
        self.entry_codigo = ctk.CTkEntry(
            entry_frame,
            placeholder_text="FINCA-XXXXX-XXXXX-XXXXX",
            font=("Arial", 11)
        )
        self.entry_codigo.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_activar = ctk.CTkButton(
            entry_frame,
            text="Activar",
            command=self._activar_licencia,
            width=80,
            font=("Arial", 11, "bold")
        )
        btn_activar.pack(side="left")
        
        # Información de soporte
        soporte_texto = ctk.CTkLabel(
            self,
            text="¿No tienes código? Solicita uno en jfburitica97@gmail.com | Tel: 3013869653",
            font=("Arial", 9),
            text_color="blue",
            cursor="hand2"
        )
        soporte_texto.pack(pady=(10, 0))
        soporte_texto.bind("<Button-1>", lambda e: self._abrir_soporte())
    
    def _activar_licencia(self):
        """Procesa la activación de licencia"""
        codigo = self.entry_codigo.get().strip().upper()
        
        if not codigo:
            messagebox.showwarning("Atención", "Por favor ingresa un código de activación")
            return
        
        if not self.usuario_id:
            messagebox.showerror("Error", "No se pudo identificar el usuario")
            return
        
        exito, mensaje = self.license_manager.activar_licencia(self.usuario_id, codigo)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            # Recargar el panel
            for widget in self.winfo_children():
                widget.destroy()
            self._crear_widgets()
        else:
            messagebox.showerror("Error", mensaje)
    
    def _abrir_soporte(self):
        """Abre el formulario de contacto (simula mailto)"""
        import webbrowser
        webbrowser.open("mailto:jfburitica97@gmail.com?subject=Solicitud%20de%20código%20de%20activación")
