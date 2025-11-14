import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db

class BitacoraComentariosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="🗒️ Bitácora de Comentarios", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        self.codigo_entry = ctk.CTkEntry(form_frame, placeholder_text="Código Animal *", width=300)
        self.autor_entry = ctk.CTkEntry(form_frame, placeholder_text="Autor *", width=300)
        self.fecha_entry = ctk.CTkEntry(form_frame, placeholder_text="Fecha", width=300)
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Campos en grid
        campos = [
            ("Código Animal:", self.codigo_entry),
            ("Autor:", self.autor_entry),
            ("Fecha:", self.fecha_entry)
        ]

        for i, (label_text, entry) in enumerate(campos):
            label = ctk.CTkLabel(form_frame, text=label_text, font=("Segoe UI", 12))
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")

        # Área de texto para el comentario
        label_nota = ctk.CTkLabel(form_frame, text="Comentario:", font=("Segoe UI", 12))
        label_nota.grid(row=3, column=0, padx=10, pady=5, sticky="nw")
        
        self.nota_txt = ctk.CTkTextbox(form_frame, width=400, height=100)
        self.nota_txt.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        form_frame.grid_columnconfigure(1, weight=1)

        # Botón
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Comentario", command=self.guardar).pack(pady=5)

    def validar_datos(self):
        codigo = self.codigo_entry.get().strip()
        autor = self.autor_entry.get().strip()
        nota = self.nota_txt.get("0.0", "end").strip()
        fecha = self.fecha_entry.get().strip()

        if not codigo or not autor or not nota:
            messagebox.showwarning("Atención", "Código, Autor y Comentario son obligatorios.")
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
        autor = self.autor_entry.get().strip()
        nota = self.nota_txt.get("0.0", "end").strip()
        fecha = self.fecha_entry.get().strip()

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar que el animal existe
                cursor.execute("SELECT id FROM animal WHERE codigo = ?", (codigo,))
                animal = cursor.fetchone()

                if not animal:
                    messagebox.showerror("Error", "Animal no encontrado.")
                    return

                id_animal = animal[0]

                # Insertar comentario
                cursor.execute("""
                    INSERT INTO comentario (id_animal, fecha, autor, nota) 
                    VALUES (?, ?, ?, ?)
                """, (id_animal, fecha, autor, nota))
                
                conn.commit()

            messagebox.showinfo("Guardado", "Comentario registrado con éxito.")
            self.limpiar_formulario()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el comentario:\n{e}")

    def limpiar_formulario(self):
        self.codigo_entry.delete(0, "end")
        self.autor_entry.delete(0, "end")
        self.nota_txt.delete("0.0", "end")
        self.fecha_entry.delete(0, "end")
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))