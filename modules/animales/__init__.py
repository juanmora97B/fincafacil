import customtkinter as ctk
from tkinter import ttk  # 👈 AGREGAR ESTA LÍNEA

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

        titulo = ctk.CTkLabel(self, text="🐄 Módulo de Animales", font=("Segoe UI", 22, "bold"))
        titulo.pack(pady=10)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # Submódulos
        self.frame_registro = RegistroAnimalFrame(self.tabs)
        self.frame_inventario = InventarioFrame(self.tabs)
        self.frame_actualizacion = ActualizacionInventarioFrame(self.tabs)
        self.frame_ficha = FichaAnimalFrame(self.tabs)
        self.frame_reubicacion = ReubicacionFrame(self.tabs)
        self.frame_bitacora_comentarios = BitacoraComentariosFrame(self.tabs)
        self.frame_bitacora_reubicaciones = BitacoraReubicacionesFrame(self.tabs)

        # Añadir pestañas
        self.tabs.add(self.frame_registro, text="📝 Registro Animal")
        self.tabs.add(self.frame_inventario, text="📋 Inventario General")
        self.tabs.add(self.frame_actualizacion, text="🔄 Actualizar Inventario")
        self.tabs.add(self.frame_ficha, text="📄 Ficha del Animal")
        self.tabs.add(self.frame_reubicacion, text="🚚 Reubicación")
        self.tabs.add(self.frame_bitacora_comentarios, text="🗒️ Bitácora Comentarios")
        self.tabs.add(self.frame_bitacora_reubicaciones, text="📦 Bitácora Reubicaciones")