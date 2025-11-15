import customtkinter as ctk
# ✅ Eliminada importación innecesaria de ttk - ya se maneja en cada submódulo

from modules.animales.registro_animal import RegistroAnimalFrame
from modules.animales.inventario import InventarioFrame
from modules.animales.ficha_animal import FichaAnimalFrame
from modules.animales.reubicacion import ReubicacionFrame
from modules.animales.bitacora_comentarios import BitacoraComentariosFrame
from modules.animales.bitacora_reubicaciones import BitacoraReubicacionesFrame
from modules.animales.actualizacion_inventario import ActualizacionInventarioFrame


class AnimalesModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        # ======== TÍTULO PRINCIPAL ========
        titulo = ctk.CTkLabel(self, text="🐄 Módulo de Gestión Animal", font=("Segoe UI", 24, "bold"))
        titulo.pack(pady=15)

        # ======== DESCRIPCIÓN ========
        descripcion = ctk.CTkLabel(self, 
                                 text="Sistema integral para la gestión de inventario, registro y seguimiento de animales",
                                 font=("Segoe UI", 12),
                                 text_color="gray")
        descripcion.pack(pady=(0, 20))

        # ======== SISTEMA DE PESTAÑAS ========
        self.tabs = ctk.CTkTabview(self, 
                                 segmented_button_fg_color="#2B2B2B",
                                 segmented_button_selected_color="#1F538D",
                                 segmented_button_selected_hover_color="#14375E")
        self.tabs.pack(fill="both", expand=True, padx=15, pady=10)

        # Crear todas las pestañas
        pestañas = [
            "📝 Registro Animal",
            "📋 Inventario General", 
            "🔄 Actualizar Inventario",
            "📄 Ficha del Animal",
            "🚚 Reubicación",
            "🗒️ Bitácora Comentarios",
            "📦 Historial Reubicaciones"
        ]

        for pestaña in pestañas:
            self.tabs.add(pestaña)

        # ======== INICIALIZACIÓN DE FRAMES ========
        
        # Pestaña 1: Registro Animal
        self.frame_registro = RegistroAnimalFrame(self.tabs.tab("📝 Registro Animal"))
        self.frame_registro.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña 2: Inventario General
        self.frame_inventario = InventarioFrame(self.tabs.tab("📋 Inventario General"))
        self.frame_inventario.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña 3: Actualizar Inventario
        self.frame_actualizacion = ActualizacionInventarioFrame(self.tabs.tab("🔄 Actualizar Inventario"))
        self.frame_actualizacion.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña 4: Ficha del Animal
        self.frame_ficha = FichaAnimalFrame(self.tabs.tab("📄 Ficha del Animal"))
        self.frame_ficha.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña 5: Reubicación
        self.frame_reubicacion = ReubicacionFrame(self.tabs.tab("🚚 Reubicación"))
        self.frame_reubicacion.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña 6: Bitácora Comentarios
        self.frame_bitacora_comentarios = BitacoraComentariosFrame(self.tabs.tab("🗒️ Bitácora Comentarios"))
        self.frame_bitacora_comentarios.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña 7: Historial Reubicaciones
        self.frame_bitacora_reubicaciones = BitacoraReubicacionesFrame(self.tabs.tab("📦 Historial Reubicaciones"))
        self.frame_bitacora_reubicaciones.pack(fill="both", expand=True, padx=10, pady=10)

        # ======== BARRA DE ESTADO ========
        self.crear_barra_estado()

    def crear_barra_estado(self):
        """Crea una barra de estado en la parte inferior"""
        barra_estado = ctk.CTkFrame(self, height=30, fg_color="#2B2B2B")
        barra_estado.pack(fill="x", side="bottom", pady=(5, 0))
        barra_estado.pack_propagate(False)

        # Información de estado
        self.label_estado = ctk.CTkLabel(barra_estado, 
                                       text="✅ Módulo de Animales cargado correctamente | Sistema FincaFácil v1.0",
                                       font=("Segoe UI", 10),
                                       text_color="lightgray")
        self.label_estado.pack(side="left", padx=10, pady=5)

        # Contador de pestaña actual
        self.label_pestaña = ctk.CTkLabel(barra_estado,
                                        text="Pestaña: Registro Animal",
                                        font=("Segoe UI", 10),
                                        text_color="lightblue")
        self.label_pestaña.pack(side="right", padx=10, pady=5)

        # Configurar evento para cambiar el texto de la pestaña actual
        self.tabs.configure(command=self.actualizar_barra_estado)

    def actualizar_barra_estado(self):
        """Actualiza la barra de estado cuando se cambia de pestaña"""
        pestaña_actual = self.tabs.get()
        self.label_pestaña.configure(text=f"Pestaña: {pestaña_actual}")

    def mostrar(self):
        """Muestra el módulo (para compatibilidad)"""
        self.pack(fill="both", expand=True)

    def ocultar(self):
        """Oculta el módulo (para compatibilidad)"""
        self.pack_forget()