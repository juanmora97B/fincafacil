import customtkinter as ctk
from tkinter import messagebox

# 🔥 Importamos correctamente los módulos reales
from modules.dashboard import DashboardModule
from modules.ajustes import AjustesFrame

class FincaFacilApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FincaFácil - Sistema Ganadero")
        self.geometry("1200x700")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # ----------- CONTENEDORES PRINCIPALES -----------
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Guarda el módulo activo actual
        self.current_module = None

        # ----------- MENÚ LATERAL -----------
        self.create_sidebar()

        # Cargar pantalla inicial
        self.show_screen("dashboard")

    def create_sidebar(self):
        title = ctk.CTkLabel(self.sidebar, text="🐄 Finca Fácil",
                             font=("Roboto", 20, "bold"))
        title.pack(pady=20)

        # Botones generales
        buttons = [
            ("Dashboard", "dashboard"),
            ("Animales", "animales"),
            ("Potreros", "potreros"),
            ("Ventas", "ventas"),
            ("Tratamientos", "tratamientos"),
            ("Nómina", "nomina"),
            ("Reportes", "reportes"),
            ("Configuración", "configuracion"),
            ("Ajustes", "ajustes")
        ]

        for text, screen in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=180,
                command=lambda s=screen: self.show_screen(s)
            )
            btn.pack(pady=5)

    # ============================================================
    #   CAMBIO DINÁMICO DE PANTALLAS / MÓDULOS
    # ============================================================
    def show_screen(self, name):
        """
        Cambia el contenido del main_frame dependiendo del módulo.
        Si ya existe uno, se destruye antes de cargar el nuevo.
        """

        # Limpia el módulo actual
        if self.current_module is not None:
            self.current_module.destroy()

        # Crea el nuevo módulo según la opción elegida
        if name == "dashboard":
            self.current_module = DashboardModule(self.main_frame)

        elif name == "ajustes":
            self.current_module = AjustesFrame(self.main_frame)

        # --- módulos temporales (placeholder) ---
        elif name == "animales":
            self.current_module = ctk.CTkLabel(self.main_frame, text="Módulo Animales")
        elif name == "potreros":
            self.current_module = ctk.CTkLabel(self.main_frame, text="Gestión de Potreros")
        elif name == "ventas":
            self.current_module = ctk.CTkLabel(self.main_frame, text="Módulo Ventas")
        elif name == "tratamientos":
            self.current_module = ctk.CTkLabel(self.main_frame, text="Tratamientos Veterinarios")
        elif name == "nomina":
            self.current_module = ctk.CTkLabel(self.main_frame, text="Nómina y Empleados")
        elif name == "reportes":
            self.current_module = ctk.CTkLabel(self.main_frame, text="Reportes Generales")
        elif name == "configuracion":
            self.current_module = ctk.CTkLabel(self.main_frame, text="Configuración del Sistema")

        else:
            self.current_module = ctk.CTkLabel(
                self.main_frame, text=f"❌ Pantalla '{name}' no existe"
            )

        self.current_module.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = FincaFacilApp()
    app.mainloop()
