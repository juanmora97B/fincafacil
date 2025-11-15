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
        self.crear_tabla_tratamientos()

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

        # Tab: Próximos Tratamientos
        self.frame_proximos = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_proximos, text="📅 Próximos")

        # Crear contenido de cada tab
        self.crear_formulario()
        self.crear_historial()
        self.crear_proximos_tratamientos()

    def crear_formulario(self):
        """Crea el formulario para registrar un tratamiento"""
        main_frame = ctk.CTkScrollableFrame(self.frame_nuevo)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="📝 Registrar Nuevo Tratamiento",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))

        # Campos
        campos_frame = ctk.CTkFrame(main_frame)
        campos_frame.pack(fill="x", pady=10, padx=10)

        # Animal
        row1 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row1.pack(fill="x", pady=8)
        ctk.CTkLabel(row1, text="Animal *:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.combo_animal = ctk.CTkComboBox(row1, width=300, font=("Segoe UI", 12))
        self.combo_animal.pack(side="left", padx=5, fill="x", expand=True)

        # Fecha
        row2 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row2.pack(fill="x", pady=8)
        ctk.CTkLabel(row2, text="Fecha Tratamiento *:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_fecha = ctk.CTkEntry(row2, width=300, font=("Segoe UI", 12))
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(side="left", padx=5, fill="x", expand=True)

        # Tipo
        row3 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row3.pack(fill="x", pady=8)
        ctk.CTkLabel(row3, text="Tipo Tratamiento *:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(
            row3,
            values=["Vacunación", "Desparasitación", "Antibiótico", "Vitaminas", "Minerales", "Cirugía", "Otro"],
            width=300,
            font=("Segoe UI", 12)
        )
        self.combo_tipo.set("Vacunación")
        self.combo_tipo.pack(side="left", padx=5, fill="x", expand=True)

        # Producto
        row4 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row4.pack(fill="x", pady=8)
        ctk.CTkLabel(row4, text="Producto *:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_producto = ctk.CTkEntry(row4, width=300, font=("Segoe UI", 12))
        self.entry_producto.pack(side="left", padx=5, fill="x", expand=True)

        # Dosis
        row5 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row5.pack(fill="x", pady=8)
        ctk.CTkLabel(row5, text="Dosis:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_dosis = ctk.CTkEntry(row5, width=300, font=("Segoe UI", 12), placeholder_text="Ej: 5 ml, 1 tableta, etc.")
        self.entry_dosis.pack(side="left", padx=5, fill="x", expand=True)

        # Veterinario
        row6 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row6.pack(fill="x", pady=8)
        ctk.CTkLabel(row6, text="Veterinario:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_veterinario = ctk.CTkEntry(row6, width=300, font=("Segoe UI", 12))
        self.entry_veterinario.pack(side="left", padx=5, fill="x", expand=True)

        # Próxima fecha
        row7 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row7.pack(fill="x", pady=8)
        ctk.CTkLabel(row7, text="Próxima Aplicación:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_proxima = ctk.CTkEntry(row7, width=300, font=("Segoe UI", 12), 
                                         placeholder_text="YYYY-MM-DD (opcional)")
        self.entry_proxima.pack(side="left", padx=5, fill="x", expand=True)

        # Comentario
        row8 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row8.pack(fill="x", pady=8)
        ctk.CTkLabel(row8, text="Comentarios:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row8, width=300, height=100, font=("Segoe UI", 12))
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Tratamiento",
            command=self.guardar_tratamiento,
            fg_color="green",
            hover_color="#006400",
            width=180,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Limpiar Formulario",
            command=self.limpiar_formulario,
            width=150,
            font=("Segoe UI", 12)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="📋 Ver Historial",
            command=lambda: self.notebook.select(1),
            width=150,
            font=("Segoe UI", 12)
        ).pack(side="left", padx=5)

        # Cargar animales
        self.cargar_animales()

    def crear_historial(self):
        """Crea la tabla de historial"""
        main_frame = ctk.CTkFrame(self.frame_historial)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="📋 Historial de Tratamientos",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left")

        # Botones de acción
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side="right")

        ctk.CTkButton(
            action_frame,
            text="🔄 Actualizar",
            command=self.cargar_tratamientos,
            width=120,
            font=("Segoe UI", 12)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_frame,
            text="➕ Nuevo",
            command=lambda: self.notebook.select(0),
            width=120,
            font=("Segoe UI", 12)
        ).pack(side="left", padx=5)

        # Tabla
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        self.crear_tabla_tratamientos(table_frame)

    def crear_tabla_tratamientos(self, parent=None):
        """Crea la tabla de tratamientos"""
        if parent is None:
            parent = self.frame_historial

        # Tabla
        self.tabla_tratamientos = ttk.Treeview(
            parent,
            columns=("id", "fecha", "animal", "tipo", "producto", "dosis", "veterinario", "proxima", "comentario"),
            show="headings",
            height=15
        )

        columnas = [
            ("id", "ID", 60),
            ("fecha", "Fecha", 100),
            ("animal", "Animal", 150),
            ("tipo", "Tipo", 120),
            ("producto", "Producto", 150),
            ("dosis", "Dosis", 100),
            ("veterinario", "Veterinario", 120),
            ("proxima", "Próxima", 100),
            ("comentario", "Comentario", 200)
        ]

        for col, heading, width in columnas:
            self.tabla_tratamientos.heading(col, text=heading)
            self.tabla_tratamientos.column(col, width=width, anchor="center")

        self.tabla_tratamientos.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tabla_tratamientos.yview)
        self.tabla_tratamientos.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bind doble click para ver detalles
        self.tabla_tratamientos.bind("<Double-1>", self.ver_detalles_tratamiento)

    def crear_proximos_tratamientos(self):
        """Crea la sección de próximos tratamientos"""
        main_frame = ctk.CTkFrame(self.frame_proximos)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="📅 Próximos Tratamientos Programados",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 10))

        # Información
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="both", expand=True, pady=10)

        self.label_proximos = ctk.CTkLabel(
            info_frame,
            text="Cargando próximos tratamientos...",
            font=("Segoe UI", 12),
            justify="left",
            anchor="nw"
        )
        self.label_proximos.pack(pady=20, padx=20, fill="both", expand=True)

        # Botón actualizar
        ctk.CTkButton(
            main_frame,
            text="🔄 Actualizar",
            command=self.cargar_proximos_tratamientos,
            width=150
        ).pack(pady=10)

        # Cargar datos iniciales
        self.cargar_proximos_tratamientos()

    def cargar_animales(self):
        """Carga los animales en el combobox"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo || ' - ' || COALESCE(nombre, 'Sin nombre') as animal_info
                    FROM animal
                    WHERE estado = 'Activo'
                    ORDER BY codigo
                """)
                animales = [row[0] for row in cursor.fetchall()]
                self.combo_animal.configure(values=animales)
                if animales:
                    self.combo_animal.set(animales[0])
        except Exception as e:
            print(f"Error al cargar animales: {e}")

    def guardar_tratamiento(self):
        """Guarda un nuevo tratamiento"""
        # Validaciones
        if not self.combo_animal.get():
            messagebox.showwarning("Atención", "Seleccione un animal")
            return
        if not self.entry_fecha.get():
            messagebox.showwarning("Atención", "Ingrese la fecha del tratamiento")
            return
        if not self.combo_tipo.get():
            messagebox.showwarning("Atención", "Seleccione el tipo de tratamiento")
            return
        if not self.entry_producto.get():
            messagebox.showwarning("Atención", "Ingrese el producto utilizado")
            return

        try:
            codigo_animal = self.combo_animal.get().split(" - ")[0]
            
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Crear tabla si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tratamiento (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_animal INTEGER NOT NULL,
                        fecha_inicio DATE NOT NULL,
                        fecha_fin DATE,
                        tipo_tratamiento TEXT NOT NULL,
                        producto TEXT NOT NULL,
                        dosis TEXT,
                        veterinario TEXT,
                        comentario TEXT,
                        fecha_proxima DATE,
                        estado TEXT DEFAULT 'Activo',
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id_animal) REFERENCES animal(id)
                    )
                """)

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
                        id_animal, fecha_inicio, tipo_tratamiento, producto, 
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
            self.cargar_proximos_tratamientos()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el tratamiento:\n{e}")

    def cargar_tratamientos(self):
        """Carga los tratamientos en la tabla"""
        # Limpiar tabla
        for item in self.tabla_tratamientos.get_children():
            self.tabla_tratamientos.delete(item)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Crear tabla si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tratamiento (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_animal INTEGER NOT NULL,
                        fecha_inicio DATE NOT NULL,
                        fecha_fin DATE,
                        tipo_tratamiento TEXT NOT NULL,
                        producto TEXT NOT NULL,
                        dosis TEXT,
                        veterinario TEXT,
                        comentario TEXT,
                        fecha_proxima DATE,
                        estado TEXT DEFAULT 'Activo',
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    SELECT 
                        t.id,
                        t.fecha_inicio,
                        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                        t.tipo_tratamiento,
                        t.producto,
                        t.dosis,
                        t.veterinario,
                        t.fecha_proxima,
                        t.comentario
                    FROM tratamiento t
                    JOIN animal a ON t.id_animal = a.id
                    WHERE t.estado = 'Activo'
                    ORDER BY t.fecha_inicio DESC
                    LIMIT 100
                """)

                for row in cursor.fetchall():
                    fecha_inicio = row[1].strftime("%d/%m/%Y") if row[1] else "-"
                    fecha_proxima = row[7].strftime("%d/%m/%Y") if row[7] else "-"
                    
                    self.tabla_tratamientos.insert("", "end", values=(
                        row[0], fecha_inicio, row[2], row[3], row[4], 
                        row[5] or "-", row[6] or "-", fecha_proxima, 
                        (row[8] or "-")[:50] + "..." if row[8] and len(row[8]) > 50 else (row[8] or "-")
                    ))

        except Exception as e:
            print(f"Error al cargar tratamientos: {e}")

    def cargar_proximos_tratamientos(self):
        """Carga los próximos tratamientos programados"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                        t.tipo_tratamiento,
                        t.producto,
                        t.fecha_proxima,
                        t.comentario
                    FROM tratamiento t
                    JOIN animal a ON t.id_animal = a.id
                    WHERE t.fecha_proxima IS NOT NULL 
                    AND t.fecha_proxima >= date('now')
                    AND t.estado = 'Activo'
                    ORDER BY t.fecha_proxima ASC
                    LIMIT 20
                """)

                tratamientos = cursor.fetchall()
                
                if tratamientos:
                    info_text = "📋 PRÓXIMOS TRATAMIENTOS PROGRAMADOS\n\n"
                    info_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    
                    for i, tratamiento in enumerate(tratamientos, 1):
                        fecha_prox = tratamiento[3].strftime("%d/%m/%Y") if tratamiento[3] else "-"
                        info_text += f"{i}. 🗓️ {fecha_prox}\n"
                        info_text += f"   🐄 {tratamiento[0]}\n"
                        info_text += f"   💊 {tratamiento[1]} - {tratamiento[2]}\n"
                        if tratamiento[4]:
                            info_text += f"   📝 {tratamiento[4][:50]}...\n" if len(tratamiento[4]) > 50 else f"   📝 {tratamiento[4]}\n"
                        info_text += "\n"
                    
                    info_text += f"Total: {len(tratamientos)} tratamientos programados"
                else:
                    info_text = "✅ No hay tratamientos programados para el futuro.\n\n"
                    info_text += "Puede programar próximos tratamientos en el formulario de 'Nuevo Tratamiento'."

                self.label_proximos.configure(text=info_text)

        except Exception as e:
            print(f"Error al cargar próximos tratamientos: {e}")
            self.label_proximos.configure(text="❌ Error al cargar los próximos tratamientos")

    def ver_detalles_tratamiento(self, event):
        """Muestra los detalles del tratamiento seleccionado"""
        seleccionado = self.tabla_tratamientos.selection()
        if not seleccionado:
            return

        tratamiento_id = self.tabla_tratamientos.item(seleccionado[0])["values"][0]

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        t.fecha_inicio,
                        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                        t.tipo_tratamiento,
                        t.producto,
                        t.dosis,
                        t.veterinario,
                        t.fecha_proxima,
                        t.comentario,
                        t.fecha_registro
                    FROM tratamiento t
                    JOIN animal a ON t.id_animal = a.id
                    WHERE t.id = ?
                """, (tratamiento_id,))

                tratamiento = cursor.fetchone()
                if tratamiento:
                    detalles = f"""
📋 DETALLES DEL TRATAMIENTO

🐄 Animal: {tratamiento[1]}
📅 Fecha Aplicación: {tratamiento[0].strftime("%d/%m/%Y") if tratamiento[0] else "-"}
💊 Tipo: {tratamiento[2]}
🧪 Producto: {tratamiento[3]}
📏 Dosis: {tratamiento[4] or "No especificada"}
👨‍⚕️ Veterinario: {tratamiento[5] or "No especificado"}
🗓️ Próxima Aplicación: {tratamiento[6].strftime("%d/%m/%Y") if tratamiento[6] else "No programada"}
📝 Comentarios: {tratamiento[7] or "No hay comentarios"}
📅 Registrado: {tratamiento[8].strftime("%d/%m/%Y %H:%M") if tratamiento[8] else "-"}
                    """
                    messagebox.showinfo(f"Detalles Tratamiento #{tratamiento_id}", detalles)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles:\n{e}")

    def limpiar_formulario(self):
        """Limpia el formulario"""
        self.combo_animal.set("")
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.combo_tipo.set("Vacunación")
        self.entry_producto.delete(0, "end")
        self.entry_dosis.delete(0, "end")
        self.entry_veterinario.delete(0, "end")
        self.entry_proxima.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        
        # Recargar animales para asegurar que esté actualizado
        self.cargar_animales()