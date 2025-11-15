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
        self.potreros = {}
        self.crear_widgets()
        self.cargar_potreros()

    def cargar_potreros(self):
        """Carga la lista de potreros disponibles"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM potrero WHERE estado = 'Activo'")
                potreros_data = cursor.fetchall()
                
                self.potreros = {f"{row[0]}-{row[1]}": row[0] for row in potreros_data}
                nombres_potreros = list(self.potreros.keys())
                
                self.combo_potrero_nuevo.configure(values=nombres_potreros)
                if nombres_potreros:
                    self.combo_potrero_nuevo.set(nombres_potreros[0])
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los potreros:\n{e}")

    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="🚚 Reubicación de Animales", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        self.codigo_entry = ctk.CTkEntry(form_frame, placeholder_text="Código del Animal *", width=300)
        
        # ComboBox para potreros en lugar de Entry
        self.combo_potrero_nuevo = ctk.CTkComboBox(form_frame, width=300, state="readonly")
        
        self.motivo_entry = ctk.CTkEntry(form_frame, placeholder_text="Motivo de la reubicación", width=300)
        self.fecha_entry = ctk.CTkEntry(form_frame, placeholder_text="Fecha", width=300)
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Campos en grid
        campos = [
            ("Código Animal:", self.codigo_entry),
            ("Nuevo Potrero:", self.combo_potrero_nuevo),
            ("Motivo:", self.motivo_entry),
            ("Fecha:", self.fecha_entry)
        ]

        for i, (label_text, widget) in enumerate(campos):
            label = ctk.CTkLabel(form_frame, text=label_text, font=("Segoe UI", 12))
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            widget.grid(row=i, column=1, padx=10, pady=5, sticky="ew")

        form_frame.grid_columnconfigure(1, weight=1)

        # Información del animal
        self.info_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.info_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.label_info_animal = ctk.CTkLabel(self.info_frame, text="Ingrese el código del animal para ver su información actual", 
                                            font=("Segoe UI", 11), justify="left", text_color="gray")
        self.label_info_animal.pack()

        # Botón
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        ctk.CTkButton(btn_frame, text="🔍 Ver Animal", command=self.ver_animal).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="💾 Guardar Reubicación", command=self.guardar).pack(side="left", padx=5)

        # Bind Enter key para buscar animal
        self.codigo_entry.bind("<Return>", lambda e: self.ver_animal())

    def ver_animal(self):
        """Muestra la información del animal antes de reubicar"""
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showwarning("Atención", "Ingrese un código de animal.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.codigo, a.nombre, p.nombre as potrero_actual, f.nombre as finca
                    FROM animal a
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    LEFT JOIN finca f ON a.id_finca = f.id
                    WHERE a.codigo = ? AND a.estado = 'Activo'
                """, (codigo,))
                
                animal = cursor.fetchone()

                if animal:
                    info_text = f"""
🐄 **INFORMACIÓN DEL ANIMAL**

🏷️  **CÓDIGO:** {animal[0]}
📛  **NOMBRE:** {animal[1] or 'No asignado'}
🏞️  **FINCA:** {animal[3] or 'No asignada'}
📍  **POTRERO ACTUAL:** {animal[2] or 'No asignado'}

*Listo para reubicación*
"""
                    self.label_info_animal.configure(text=info_text, text_color="black")
                else:
                    self.label_info_animal.configure(text="❌ Animal no encontrado o inactivo", text_color="red")
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el animal:\n{e}")

    def validar_datos(self):
        codigo = self.codigo_entry.get().strip()
        nuevo_potrero = self.combo_potrero_nuevo.get().strip()
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
        nuevo_potrero_key = self.combo_potrero_nuevo.get().strip()
        motivo = self.motivo_entry.get().strip() or "Reubicación programada"
        fecha = self.fecha_entry.get().strip()

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener ID del nuevo potrero
                id_potrero_nuevo = self.potreros.get(nuevo_potrero_key)
                if not id_potrero_nuevo:
                    messagebox.showerror("Error", "Potrero no válido.")
                    return

                # Verificar que el animal existe y obtener su información actual
                cursor.execute("""
                    SELECT a.id, p.nombre as potrero_actual, f.nombre as finca
                    FROM animal a 
                    LEFT JOIN potrero p ON a.id_potrero = p.id 
                    LEFT JOIN finca f ON a.id_finca = f.id
                    WHERE a.codigo = ? AND a.estado = 'Activo'
                """, (codigo,))
                
                data = cursor.fetchone()

                if not data:
                    messagebox.showerror("Error", "Animal no encontrado o inactivo.")
                    return

                id_animal, potrero_actual, finca_actual = data
                nuevo_potrero_nombre = nuevo_potrero_key.split("-", 1)[1] if "-" in nuevo_potrero_key else nuevo_potrero_key

                # Actualizar potrero del animal
                cursor.execute("UPDATE animal SET id_potrero = ? WHERE id = ?", 
                             (id_potrero_nuevo, id_animal))
                
                # Registrar en comentarios (como bitácora temporal)
                cursor.execute("""
                    INSERT INTO comentario (id_animal, fecha, autor, nota) 
                    VALUES (?, ?, ?, ?)
                """, (id_animal, fecha, "Sistema", 
                     f"REUBICACIÓN: De '{potrero_actual or 'Sin potrero'}' a '{nuevo_potrero_nombre}'. Motivo: {motivo}"))
                
                conn.commit()

            messagebox.showinfo("Éxito", 
                              f"✅ Animal {codigo} reubicado correctamente:\n"
                              f"• De: {potrero_actual or 'Sin potrero'}\n"
                              f"• A: {nuevo_potrero_nombre}\n"
                              f"• Finca: {finca_actual}\n"
                              f"• Fecha: {fecha}")
            self.limpiar_formulario()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la reubicación:\n{e}")

    def limpiar_formulario(self):
        self.codigo_entry.delete(0, "end")
        self.combo_potrero_nuevo.set("")
        self.motivo_entry.delete(0, "end")
        self.fecha_entry.delete(0, "end")
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.label_info_animal.configure(text="Ingrese el código del animal para ver su información actual", 
                                       text_color="gray")