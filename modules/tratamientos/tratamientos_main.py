import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class TratamientosModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_tratamientos()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="🏥 Gestión de Tratamientos y Vacunas",
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=15)

        # Frame principal con tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab: Nuevo Tratamiento
        self.frame_nuevo = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_nuevo, text="➕ Nuevo Tratamiento")

        # Tab: Historial
        self.frame_historial = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_historial, text="📋 Historial")

        # Crear formulario
        self.crear_formulario()
        
        # Crear historial
        self.crear_historial()

    def crear_formulario(self):
        """Crea el formulario para registrar un tratamiento"""
        form_frame = ctk.CTkFrame(self.frame_nuevo)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            form_frame,
            text="📝 Registrar Nuevo Tratamiento",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))

        # Campos
        campos_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        campos_frame.pack(fill="x", pady=10)

        # Animal
        row1 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Animal *:", width=150).pack(side="left", padx=5)
        self.combo_animal = ctk.CTkComboBox(row1, width=300)
        self.combo_animal.pack(side="left", padx=5, fill="x", expand=True)

        # Fecha
        row2 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Fecha Tratamiento *:", width=150).pack(side="left", padx=5)
        self.entry_fecha = ctk.CTkEntry(row2, width=300)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(side="left", padx=5, fill="x", expand=True)

        # Tipo
        row3 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Tipo Tratamiento *:", width=150).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(
            row3,
            values=["Vacunación", "Desparasitación", "Antibiótico", "Vitaminas", "Otro"],
            width=300
        )
        self.combo_tipo.pack(side="left", padx=5, fill="x", expand=True)

        # Producto
        row4 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Producto *:", width=150).pack(side="left", padx=5)
        self.entry_producto = ctk.CTkEntry(row4, width=300)
        self.entry_producto.pack(side="left", padx=5, fill="x", expand=True)

        # Dosis
        row5 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Dosis:", width=150).pack(side="left", padx=5)
        self.entry_dosis = ctk.CTkEntry(row5, width=300)
        self.entry_dosis.pack(side="left", padx=5, fill="x", expand=True)

        # Veterinario
        row6 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row6.pack(fill="x", pady=5)
        ctk.CTkLabel(row6, text="Veterinario:", width=150).pack(side="left", padx=5)
        self.entry_veterinario = ctk.CTkEntry(row6, width=300)
        self.entry_veterinario.pack(side="left", padx=5, fill="x", expand=True)

        # Próxima fecha
        row7 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row7.pack(fill="x", pady=5)
        ctk.CTkLabel(row7, text="Próxima Aplicación:", width=150).pack(side="left", padx=5)
        self.entry_proxima = ctk.CTkEntry(row7, width=300)
        self.entry_proxima.pack(side="left", padx=5, fill="x", expand=True)

        # Comentario
        row8 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row8.pack(fill="x", pady=5)
        ctk.CTkLabel(row8, text="Comentarios:", width=150).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row8, width=300, height=80)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(campos_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Tratamiento",
            command=self.guardar_tratamiento,
            fg_color="green",
            hover_color="#006400",
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Limpiar",
            command=self.limpiar_formulario,
            width=150
        ).pack(side="left", padx=5)

        # Cargar animales
        self.cargar_animales()

    def crear_historial(self):
        """Crea la tabla de historial"""
        table_frame = ctk.CTkFrame(self.frame_historial)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            table_frame,
            text="📋 Historial de Tratamientos",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 10))

        # Tabla
        self.tabla_tratamientos = ttk.Treeview(
            table_frame,
            columns=("fecha", "animal", "tipo", "producto", "veterinario"),
            show="headings",
            height=15
        )

        columnas = [
            ("fecha", "Fecha", 120),
            ("animal", "Animal", 150),
            ("tipo", "Tipo", 120),
            ("producto", "Producto", 200),
            ("veterinario", "Veterinario", 150)
        ]

        for col, heading, width in columnas:
            self.tabla_tratamientos.heading(col, text=heading)
            self.tabla_tratamientos.column(col, width=width, anchor="center")

        self.tabla_tratamientos.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_tratamientos.yview)
        self.tabla_tratamientos.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones
        action_frame = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
        action_frame.pack(pady=10)
        
        ctk.CTkButton(
            action_frame,
            text="🔄 Actualizar",
            command=self.cargar_tratamientos,
            width=150
        ).pack(side="left", padx=5)

    def cargar_animales(self):
        """Carga los animales en el combobox"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo || ' - ' || COALESCE(nombre, 'Sin nombre')
                    FROM animal
                    WHERE estado = 'Activo'
                    ORDER BY codigo
                """)
                animales = [row[0] for row in cursor.fetchall()]
                self.combo_animal.configure(values=animales)
        except Exception as e:
            print(f"Error al cargar animales: {e}")

    def guardar_tratamiento(self):
        """Guarda un nuevo tratamiento"""
        if not self.combo_animal.get() or not self.entry_fecha.get() or not self.combo_tipo.get() or not self.entry_producto.get():
            messagebox.showwarning("Atención", "Complete los campos obligatorios (*)")
            return

        try:
            codigo_animal = self.combo_animal.get().split(" - ")[0]
            
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Obtener ID del animal
                cursor.execute("SELECT id FROM animal WHERE codigo = ?", (codigo_animal,))
                animal_row = cursor.fetchone()
                if not animal_row:
                    messagebox.showerror("Error", "Animal no encontrado")
                    return
                
                id_animal = animal_row[0]

                # Insertar tratamiento
                cursor.execute("""
                    INSERT INTO tratamiento (
                        id_animal, fecha, tipo_tratamiento, producto, 
                        dosis, veterinario, comentario, fecha_proxima
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_animal,
                    self.entry_fecha.get(),
                    self.combo_tipo.get(),
                    self.entry_producto.get(),
                    self.entry_dosis.get() or None,
                    self.entry_veterinario.get() or None,
                    self.text_comentario.get("1.0", "end-1c").strip() or None,
                    self.entry_proxima.get() or None
                ))

                conn.commit()

            messagebox.showinfo("Éxito", "Tratamiento registrado correctamente")
            self.limpiar_formulario()
            self.cargar_tratamientos()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el tratamiento:\n{e}")

    def cargar_tratamientos(self):
        """Carga los tratamientos en la tabla"""
        for item in self.tabla_tratamientos.get_children():
            self.tabla_tratamientos.delete(item)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        t.fecha,
                        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                        t.tipo_tratamiento,
                        t.producto,
                        t.veterinario
                    FROM tratamiento t
                    JOIN animal a ON t.id_animal = a.id
                    ORDER BY t.fecha DESC
                    LIMIT 100
                """)

                for row in cursor.fetchall():
                    self.tabla_tratamientos.insert("", "end", values=row)

        except Exception as e:
            if "no such table" not in str(e).lower():
                print(f"Error al cargar tratamientos: {e}")

    def limpiar_formulario(self):
        """Limpia el formulario"""
        self.combo_animal.set("")
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.combo_tipo.set("")
        self.entry_producto.delete(0, "end")
        self.entry_dosis.delete(0, "end")
        self.entry_veterinario.delete(0, "end")
        self.entry_proxima.delete(0, "end")
        self.text_comentario.delete("1.0", "end")

