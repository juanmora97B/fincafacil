import customtkinter as ctk
from tkinter import messagebox
from database.db import get_connection


class AjustesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.label = ctk.CTkLabel(
            self, 
            text="Ajustes del sistema", 
            font=("Arial", 20)
        )
        self.label.pack(pady=20)

        # Botón para mostrar los ajustes registrados
        self.boton_ver = ctk.CTkButton(
            self, 
            text="Ver ajustes",
            command=self.mostrar_ajustes
        )
        self.boton_ver.pack(pady=10)

    def mostrar_ajustes(self):
        """Muestra la información de la tabla 'configuracion'."""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Crear tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    clave TEXT UNIQUE NOT NULL,
                    valor TEXT
                )
            """)

            # Leer registros
            cursor.execute("SELECT clave, valor FROM configuracion ORDER BY clave ASC")
            registros = cursor.fetchall()

            conn.close()

            if not registros:
                messagebox.showinfo("Ajustes", "No hay configuraciones registradas.")
                return

            texto = "\n".join([f"{clave}: {valor}" for clave, valor in registros])
            messagebox.showinfo("Ajustes Registrados", texto)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los ajustes.\n\n{e}")
