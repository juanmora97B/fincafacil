import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db

class ReubicacionFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="🚚 Reubicación de Animales", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        self.codigo_entry = ctk.CTkEntry(form_frame, placeholder_text="Código del Animal *", width=300)
        self.potrero_nuevo_entry = ctk.CTkEntry(form_frame, placeholder_text="Nuevo Potrero *", width=300)
        self.motivo_entry = ctk.CTkEntry(form_frame, placeholder_text="Motivo de la reubicación", width=300)
        self.fecha_entry = ctk.CTkEntry(form_frame, placeholder_text="Fecha", width=300)
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Empaquetar campos
        campos = [
            ("Código Animal:", self.codigo_entry),
            ("Nuevo Potrero:", self.potrero_nuevo_entry),
            ("Motivo:", self.motivo_entry),
            ("Fecha:", self.fecha_entry)
        ]

        for i, (label_text, entry) in enumerate(campos):
            label = ctk.CTkLabel(form_frame, text=label_text, font=("Segoe UI", 12))
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")

        form_frame.grid_columnconfigure(1, weight=1)

        # Botón
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Reubicación", command=self.guardar).pack(pady=5)

    def validar_datos(self):
        codigo = self.codigo_entry.get().strip()
        nuevo_potrero = self.potrero_nuevo_entry.get().strip()
        fecha = self.fecha_entry.get().strip()

        if not codigo or not nuevo_potrero:
            messagebox.showwarning("Atención", "Código y Nuevo Potrero son obligatorios.")
            return False

        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Atención", "Formato de fecha inválido. Use YYYY-MM-DD")
            return False

        return True

    def guardar(self):
        if not self.validar_datos():
            return

        codigo = self.codigo_entry.get().strip()
        nuevo = self.potrero_nuevo_entry.get().strip()
        motivo = self.motivo_entry.get().strip() or "Reubicación programada"
        fecha = self.fecha_entry.get().strip()

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar que el animal existe y obtener su potrero actual
                cursor.execute("SELECT id, potrero FROM animal WHERE codigo = ?", (codigo,))
                data = cursor.fetchone()

                if not data:
                    messagebox.showerror("Error", "Animal no encontrado.")
                    return

                id_animal, potrero_ant = data

                # Actualizar potrero del animal
                cursor.execute("UPDATE animal SET potrero = ? WHERE id = ?", (nuevo, id_animal))
                
                # Registrar en bitácora de reubicaciones
                cursor.execute("""
                    INSERT INTO reubicacion (id_animal, potrero_anterior, potrero_nuevo, fecha, motivo) 
                    VALUES (?, ?, ?, ?, ?)
                """, (id_animal, potrero_ant, nuevo, fecha, motivo))
                
                conn.commit()

            messagebox.showinfo("Éxito", f"Animal {codigo} reubicado correctamente de '{potrero_ant}' a '{nuevo}'.")
            self.limpiar_formulario()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la reubicación:\n{e}")

    def limpiar_formulario(self):
        self.codigo_entry.delete(0, "end")
        self.potrero_nuevo_entry.delete(0, "end")
        self.motivo_entry.delete(0, "end")
        self.fecha_entry.delete(0, "end")
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))