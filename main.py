import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import sqlite3
from datetime import datetime
from database.conexion import DatabaseManager

# ==============================
# CONFIGURACIÓN DE LA VENTANA
# ==============================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class FincaFacilApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🐄 FincaFácil - Sistema Ganadero")
        self.geometry("1100x650")
        self.minsize(1000, 600)

        # ==========================
        # MENÚ LATERAL
        # ==========================
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Logo lateral
        logo_path = "assets/Logo.png"
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(100, 100))
            self.logo_label = ctk.CTkLabel(self.sidebar, image=logo_img, text="")
            self.logo_label.image = logo_img
            self.logo_label.pack(pady=(25, 10))

        # Título y lema lateral
        self.title_label = ctk.CTkLabel(
            self.sidebar, text="FincaFácil", font=("Segoe UI", 22, "bold")
        )
        self.title_label.pack()

        self.slogan_label = ctk.CTkLabel(
            self.sidebar,
            text="“La eficiencia que tu ganadería merece.”",
            font=("Segoe UI", 11, "italic"),
            wraplength=180,
            justify="center",
        )
        self.slogan_label.pack(pady=(0, 20))

        # Botones de menú lateral con iconos modernos
        menu_items = [
            ("📊 Dashboard", self.mostrar_dashboard),
            ("🐄 Animales", self.mostrar_animales),
            ("🌿 Potreros", self.mostrar_potreros),
            ("💰 Ventas", self.mostrar_ventas),
            ("🏥 Tratamientos", self.mostrar_tratamientos),
            ("👥 Nómina", self.mostrar_nomina),
            ("📈 Reportes", self.mostrar_reportes),
            ("⚙️ Configuración", self.mostrar_configuracion),
            ("🔧 Ajustes", self.mostrar_ajustes),
        ]

        self.menu_buttons = {}
        for texto, comando in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=texto,
                width=200,
                height=40,
                corner_radius=10,
                command=comando,
                font=("Segoe UI", 13),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
            )
            btn.pack(pady=3, padx=10)
            self.menu_buttons[texto] = btn
        
        # Separador antes del botón salir
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray")
        separator.pack(side="bottom", fill="x", padx=10, pady=(10, 5))
        
        # Botón salir
        ctk.CTkButton(
            self.sidebar,
            text="🚪 Salir",
            width=200,
            height=40,
            fg_color="#C62828",
            hover_color="#8B0000",
            command=self.confirmar_salida,
            font=("Segoe UI", 13),
        ).pack(side="bottom", pady=15, padx=10)

        # ==========================
        # ÁREA PRINCIPAL
        # ==========================
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Inicializar base de datos
        self.crear_base_datos()

        # Mostrar dashboard por defecto
        self.mostrar_dashboard()

    # ==========================
    # FUNCIONES DEL MENÚ
    # ==========================
    def limpiar_main(self):
        """Limpia el área principal antes de mostrar un módulo nuevo"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mostrar_dashboard(self):
        """Dashboard moderno con estadísticas"""
        try:
            from modules.dashboard import DashboardModule
            self.limpiar_main()
            DashboardModule(self.main_frame)
        except Exception as e:
            # Si no existe el módulo, mostrar pantalla de bienvenida
            self.mostrar_inicio()
    
    def mostrar_inicio(self):
        """Pantalla de bienvenida (fallback)"""
        self.limpiar_main()

        logo_path = "assets/Logo.png"
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(180, 180))
            logo_label = ctk.CTkLabel(self.main_frame, image=logo_img, text="")
            logo_label.image = logo_img
            logo_label.pack(pady=(40, 15))

        label_titulo = ctk.CTkLabel(
            self.main_frame,
            text="🐄 Bienvenido a FincaFácil",
            font=("Segoe UI", 28, "bold"),
        )
        label_titulo.pack(pady=10)

        lema = ctk.CTkLabel(
            self.main_frame,
            text="La eficiencia que tu ganadería merece.",
            font=("Segoe UI", 18, "italic"),
        )
        lema.pack(pady=(0, 20))

    def mostrar_animales(self):
        """Carga el módulo de animales"""
        try:
            from modules.animales import AnimalesModule
            self.limpiar_main()
            AnimalesModule(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de animales:\n{e}")

    def mostrar_potreros(self):
        """Carga el módulo de potreros"""
        self.limpiar_main()
        try:
            from modules.potreros import PotrerosModule
            PotrerosModule(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de potreros:\n{e}")

    def mostrar_ventas(self):
        """Carga el módulo de ventas"""
        try:
            from modules.ventas import VentasModule
            self.limpiar_main()
            VentasModule(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de ventas:\n{e}")

    def mostrar_tratamientos(self):
        """Carga el módulo de tratamientos"""
        try:
            from modules.tratamientos import TratamientosModule
            self.limpiar_main()
            TratamientosModule(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de tratamientos:\n{e}")

    def mostrar_configuracion(self):
        """Carga el módulo de configuración"""
        try:
            from modules.configuracion import ConfiguracionModule
            self.limpiar_main()
            ConfiguracionModule(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de configuración:\n{e}")

    def mostrar_nomina(self):
        """Carga el módulo de nómina"""
        try:
            from modules.nomina import NominaModule
            self.limpiar_main()
            NominaModule(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de nómina:\n{e}")

    def mostrar_reportes(self):
        """Carga el módulo de reportes"""
        try:
            from modules.reportes import ReportesModule
            self.limpiar_main()
            ReportesModule(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de reportes:\n{e}")

    def mostrar_ajustes(self):
        """Carga el módulo de ajustes"""
        try:
            from modules.ajustes import AjustesModule
            self.limpiar_main()
            AjustesModule(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo de ajustes:\n{e}")

    # ==========================
    # BASE DE DATOS
    # ==========================
    def crear_base_datos(self):
        """Inicializa la base de datos delegando en DatabaseManager"""
        os.makedirs("database", exist_ok=True)
        DatabaseManager()  # Crea/asegura tablas con nombres en singular y FKs correctas

    def actualizar_base_datos(self):
        """Actualiza la base de datos con nuevas tablas y columnas"""
        try:
            # Importar y ejecutar la función de actualización
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))
            
            from actualizar_db import actualizar_base_datos as actualizar_bd  # pyright: ignore[reportMissingImports]
            actualizar_bd()
            print("Base de datos actualizada correctamente")
        except Exception as e:
            print(f"Error al actualizar BD: {e}")

    # ==========================
    # SALIDA
    # ==========================
    def confirmar_salida(self):
        """Confirma la salida de la aplicación"""
        if messagebox.askyesno("Salir", "¿Desea salir de FincaFácil?"):
            self.destroy()


# ==============================
# EJECUCIÓN PRINCIPAL
# ==============================
if __name__ == "__main__":
    try:
        app = FincaFacilApp()
        app.mainloop()
    except Exception as e:
        print(f"Error crítico al iniciar la aplicación: {e}")
        messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n{e}")