import customtkinter as ctk
from tkinter import messagebox
# ✅ Eliminada importación innecesaria de ttk - ya se maneja en cada submódulo
from modules.utils.ui import add_tooltip

from modules.animales.registro_animal import RegistroAnimalFrame
from modules.animales.inventario_v2 import InventarioGeneralFrame
from modules.animales.realizar_inventario import RealizarInventarioFrame
from modules.animales.ficha_animal import FichaAnimalFrame
from modules.animales.reubicacion import ReubicacionFrame
from modules.animales.bitacora_comentarios import BitacoraComentarios as NewBitacoraComentarios
from modules.animales.bitacora_reubicaciones import BitacoraReubicacionesFrame
from modules.animales.bitacora_historial_reubicaciones import BitacoraHistorialReubicacionesFrame
from modules.animales.actualizacion_inventario import ActualizacionInventarioFrame
import sqlite3
from database.database import get_db_connection
from modules.utils.colores import obtener_colores


class AnimalesModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        # Colores del módulo
        self.color_bg, self.color_hover = obtener_colores('animales')

        # ======== TÍTULO PRINCIPAL ========
        header = ctk.CTkFrame(self, fg_color=(self.color_bg, "#1a1a1a"), corner_radius=15)
        header.pack(fill="x", padx=15, pady=(10, 6))
        titulo = ctk.CTkLabel(header, text="🐄 Módulo de Gestión Animal", font=("Segoe UI", 24, "bold"), text_color="white")
        titulo.pack(side="left", anchor="w", padx=15, pady=10)
        add_tooltip(titulo, "Gestión integral de animales en la finca")

        # ======== DESCRIPCIÓN ========
        descripcion = ctk.CTkLabel(self, 
                 text="Sistema integral para la gestión de inventario, registro y seguimiento de animales",
                 font=("Segoe UI", 12),
                 text_color="gray")
        descripcion.pack(pady=(0, 10))
        add_tooltip(descripcion, "Aquí puedes registrar, consultar y actualizar información de todos los animales.")

        # ======== SISTEMA DE PESTAÑAS ========
        modo = ctk.get_appearance_mode()
        fg_color = "#2B2B2B" if modo == "Dark" else "#F5F5F5"
        sel_color = "#1F538D" if modo == "Dark" else "#1976D2"
        hover_color = "#14375E" if modo == "Dark" else "#90caf9"
        self.tabs = ctk.CTkTabview(
            self,
            segmented_button_fg_color=fg_color,
            segmented_button_selected_color=sel_color,
            segmented_button_selected_hover_color=hover_color
        )
        # Eliminar padding horizontal para aprovechar todo el ancho disponible
        self.tabs.pack(fill="both", expand=True, padx=0, pady=(0, 5))

        pestañas = [
            "📝 Registro Animal",
            "📋 Inventario General",
            "🧮 Realizar Inventario",
            "📄 Ficha del Animal",
            "🚚 Reubicación",
            "🗒️ Bitácora Comentarios",
            "📦 Historial Reubicaciones"
        ]
        for pestaña in pestañas:
            self.tabs.add(pestaña)
            add_tooltip(self.tabs.tab(pestaña), f"Acceso rápido a: {pestaña}")

        # ======== INICIALIZACIÓN DE FRAMES ========
        self.frame_registro = RegistroAnimalFrame(self.tabs.tab("📝 Registro Animal"))
        self.frame_inventario_general = InventarioGeneralFrame(self.tabs.tab("📋 Inventario General"))
        self.frame_inventario_general.pack(fill="both", expand=True)
        self.frame_realizar_inventario = RealizarInventarioFrame(self.tabs.tab("🧮 Realizar Inventario"))
        self.frame_realizar_inventario.pack(fill="both", expand=True, padx=0, pady=5)
        self.frame_ficha = FichaAnimalFrame(self.tabs.tab("📄 Ficha del Animal"), on_animal_selected=self._sync_bitacora)
        self.frame_ficha.pack(fill="both", expand=True, padx=0, pady=5)
        self.frame_reubicacion = ReubicacionFrame(self.tabs.tab("🚚 Reubicación"))
        self.frame_reubicacion.pack(fill="both", expand=True, padx=0, pady=5)
        print("[Animales] Creando Nueva Bitácora (NewBitacoraComentarios) para pestaña Bitácora Comentarios")
        self.frame_bitacora_comentarios = NewBitacoraComentarios(self.tabs.tab("🗒️ Bitácora Comentarios"))
        self.frame_bitacora_comentarios.pack(fill="both", expand=True, padx=0, pady=5)
        # Usar nueva vista de historial dedicada
        self.frame_bitacora_hist = BitacoraHistorialReubicacionesFrame(self.tabs.tab("📦 Historial Reubicaciones"), on_animal_selected=self._abrir_ficha_animal)
        self.frame_bitacora_hist.pack(fill="both", expand=True, padx=0, pady=5)
        self.crear_barra_estado()

    def crear_barra_estado(self):
        """Crea una barra de estado en la parte inferior"""
        fg_barra = "#2B2B2B" if ctk.get_appearance_mode() == "Dark" else "#E3F2FD"
        barra_estado = ctk.CTkFrame(self, height=30, fg_color=fg_barra)
        barra_estado.pack(fill="x", side="bottom", pady=(5, 0))
        barra_estado.pack_propagate(False)
        self.label_estado = ctk.CTkLabel(barra_estado, 
                           text="✅ Módulo de Animales cargado correctamente | Sistema FincaFácil v1.0",
                           font=("Segoe UI", 10),
                           text_color="#1976D2" if ctk.get_appearance_mode() == "Light" else "lightgray")
        self.label_estado.pack(side="left", padx=10, pady=5)
        self.label_pestaña = ctk.CTkLabel(barra_estado,
                        text="Pestaña: Registro Animal",
                        font=("Segoe UI", 10),
                        text_color="#1976D2" if ctk.get_appearance_mode() == "Light" else "lightblue")
        self.label_pestaña.pack(side="right", padx=10, pady=5)
        self.tabs.configure(command=self.actualizar_barra_estado)

    def _sync_bitacora(self, codigo: str):
        """Sincroniza la pestaña de Bitácora con el código seleccionado en la ficha."""
        try:
            self.frame_bitacora_comentarios.set_animal_codigo(codigo)
            # Cambiar automáticamente a la pestaña de Bitácora si está habilitado en app_settings
            if self._is_auto_switch_enabled():
                self.tabs.set("🗒️ Bitácora Comentarios")
        except Exception:
            pass

    def _abrir_ficha_animal(self, codigo: str):
        """Abre la Ficha del Animal con el código especificado."""
        try:
            # Establecer el código en el entry de búsqueda
            self.frame_ficha.codigo_entry.delete(0, "end")
            self.frame_ficha.codigo_entry.insert(0, codigo.strip().upper())
            # Buscar el animal
            self.frame_ficha.buscar_animal()
            # Cambiar a la pestaña de Ficha
            self.tabs.set("📄 Ficha del Animal")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ficha: {e}")

    def _is_auto_switch_enabled(self) -> bool:
        """Lee configuración 'auto_switch_bitacora' desde app_settings. Por defecto True."""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT valor FROM app_settings WHERE clave='auto_switch_bitacora' LIMIT 1")
                r = cur.fetchone()
                if not r:
                    return True
                val = r['valor'] if isinstance(r, sqlite3.Row) else r[0]
                return str(val).strip().lower() in ("1","true","sí","si","on","yes")
        except Exception:
            return True

    # _add_tooltip eliminado: ahora se usa add_tooltip centralizado desde modules.utils.ui

    def actualizar_barra_estado(self, *args):
        """Actualiza la barra de estado cuando se cambia de pestaña.
        Acepta *args por compatibilidad con callbacks que envían el nombre.
        """
        pestaña_actual = self.tabs.get()
        self.label_pestaña.configure(text=f"Pestaña: {pestaña_actual}")

    def mostrar(self):
        """Muestra el módulo (para compatibilidad)"""
        self.pack(fill="both", expand=True)

    def ocultar(self):
        """Oculta el módulo (para compatibilidad)"""
        self.pack_forget()