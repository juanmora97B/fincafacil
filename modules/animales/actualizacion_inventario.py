import customtkinter as ctk
from tkinter import ttk, messagebox  # 👈 AGREGAR ttk
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.conexion import db

class ActualizacionInventarioFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.animal_actual = None
        self.finca_seleccionada = None
        self.crear_widgets()
        self.cargar_fincas()

    def crear_widgets(self):
        # ======== TÍTULO ========
        titulo = ctk.CTkLabel(self, text="🔄 Actualización de Inventario", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # ======== SELECCIÓN DE FINCA ========
        finca_frame = ctk.CTkFrame(self, corner_radius=10)
        finca_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(finca_frame, text="🏞️ Seleccionar Finca:", 
                    font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=5)

        row1 = ctk.CTkFrame(finca_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self.combo_fincas = ctk.CTkComboBox(row1, width=300, command=self.finca_seleccionada_cambio)
        self.combo_fincas.pack(side="left", padx=5)
        
        ctk.CTkButton(row1, text="🔄 Cargar Animales", command=self.cargar_animales_finca).pack(side="left", padx=5)

        # ======== BÚSQUEDA DE ANIMAL ========
        busqueda_frame = ctk.CTkFrame(self, corner_radius=10)
        busqueda_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(busqueda_frame, text="🔍 Buscar Animal por Código:", 
                    font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=5)

        row2 = ctk.CTkFrame(busqueda_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.entry_codigo_busqueda = ctk.CTkEntry(row2, placeholder_text="Ingrese código del animal", width=250)
        self.entry_codigo_busqueda.pack(side="left", padx=5)
        
        ctk.CTkButton(row2, text="🔍 Buscar", command=self.buscar_animal).pack(side="left", padx=5)
        self.entry_codigo_busqueda.bind("<Return>", lambda e: self.buscar_animal())

        # ======== INFORMACIÓN DEL ANIMAL ========
        self.info_frame = ctk.CTkFrame(self, corner_radius=10)
        self.info_frame.pack(pady=10, padx=20, fill="x")
        
        self.label_info_animal = ctk.CTkLabel(self.info_frame, text="Ingrese un código para buscar el animal", 
                                            font=("Segoe UI", 12), justify="left")
        self.label_info_animal.pack(pady=10)

        # ======== ACTUALIZACIONES ========
        actualizaciones_frame = ctk.CTkFrame(self, corner_radius=10)
        actualizaciones_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(actualizaciones_frame, text="📝 Actualizar Información", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Peso actual
        row3 = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row3, text="Peso Actual (kg):", width=120).pack(side="left", padx=5)
        self.entry_peso_actual = ctk.CTkEntry(row3, placeholder_text="Peso del animal", width=150)
        self.entry_peso_actual.pack(side="left", padx=5)
        
        ctk.CTkButton(row3, text="⚖️ Registrar Peso", command=self.registrar_peso).pack(side="left", padx=5)

        # Tratamiento
        row4 = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row4, text="Tratamiento:", width=120).pack(side="left", padx=5)
        self.entry_tratamiento = ctk.CTkEntry(row4, placeholder_text="Tipo de tratamiento", width=200)
        self.entry_tratamiento.pack(side="left", padx=5)
        
        ctk.CTkLabel(row4, text="Producto:", width=80).pack(side="left", padx=5)
        self.entry_producto = ctk.CTkEntry(row4, placeholder_text="Producto aplicado", width=150)
        self.entry_producto.pack(side="left", padx=5)
        
        ctk.CTkButton(row4, text="💊 Registrar Tratamiento", command=self.registrar_tratamiento).pack(side="left", padx=5)

        # Estado de inventario
        row5 = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row5.pack(fill="x", pady=10)
        
        ctk.CTkLabel(row5, text="Estado de Inventario:", width=140).pack(side="left", padx=5)
        
        self.btn_inventariado = ctk.CTkButton(row5, text="✅ Marcar como INVENTARIADO", 
                                            fg_color="green", hover_color="#006400",
                                            command=lambda: self.marcar_inventario(1))
        self.btn_inventariado.pack(side="left", padx=5)
        
        self.btn_no_inventariado = ctk.CTkButton(row5, text="❌ Marcar como FALTANTE", 
                                               fg_color="red", hover_color="#8B0000",
                                               command=lambda: self.marcar_inventario(0))
        self.btn_no_inventariado.pack(side="left", padx=5)

        # Comentario rápido
        row6 = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row6.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row6, text="Comentario Rápido:", width=120).pack(side="left", padx=5, anchor="n")
        self.text_comentario_rapido = ctk.CTkTextbox(row6, width=300, height=60)
        self.text_comentario_rapido.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(row6, text="💬 Guardar Comentario", command=self.guardar_comentario_rapido).pack(side="left", padx=5)

        # ======== LISTA DE ANIMALES SIN INVENTARIAR ========
        lista_frame = ctk.CTkFrame(self)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(lista_frame, text="📋 Animales Sin Inventariar", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=5)

        # Tabla de animales sin inventariar
        self.tabla_sin_inventariar = ttk.Treeview(lista_frame, 
                                                 columns=("codigo", "nombre", "sexo", "raza", "potrero", "ultimo_peso"), 
                                                 show="headings",
                                                 height=8)
        
        column_config = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("sexo", "Sexo", 80),
            ("raza", "Raza", 120),
            ("potrero", "Potrero", 120),
            ("ultimo_peso", "Último Peso", 100)
        ]
        
        for col, heading, width in column_config:
            self.tabla_sin_inventariar.heading(col, text=heading)
            self.tabla_sin_inventariar.column(col, width=width, anchor="center")

        self.tabla_sin_inventariar.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tabla_sin_inventariar.yview)
        self.tabla_sin_inventariar.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Doble click para seleccionar
        self.tabla_sin_inventariar.bind("<Double-1>", self.seleccionar_de_lista)

    def cargar_fincas(self):
        """Carga la lista de fincas"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa'")
                fincas = [f"{row[0]}-{row[1]}" for row in cursor.fetchall()]
                
                self.combo_fincas.configure(values=fincas)
                if fincas:
                    self.combo_fincas.set(fincas[0])
                    self.finca_seleccionada_cambio(fincas[0])
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def finca_seleccionada_cambio(self, choice):
        """Cuando se selecciona una finca diferente"""
        if choice:
            try:
                self.finca_seleccionada = int(choice.split("-")[0])
            except:
                self.finca_seleccionada = None

    def cargar_animales_finca(self):
        """Carga los animales sin inventariar de la finca seleccionada"""
        if not self.finca_seleccionada:
            messagebox.showwarning("Atención", "Seleccione una finca primero.")
            return

        # Limpiar tabla
        for fila in self.tabla_sin_inventariar.get_children():
            self.tabla_sin_inventariar.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.codigo, a.nombre, a.sexo, r.nombre, p.nombre,
                           (SELECT peso FROM peso WHERE id_animal = a.id ORDER BY fecha DESC LIMIT 1) as ultimo_peso
                    FROM animal a
                    LEFT JOIN raza r ON a.raza = r.nombre
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    WHERE a.id_finca = ? AND a.estado = 'Activo' AND a.inventariado = 0
                    ORDER BY a.codigo
                """, (self.finca_seleccionada,))
                
                for fila in cursor.fetchall():
                    ultimo_peso = f"{fila[5]} kg" if fila[5] else "No registrado"
                    valores = fila[:5] + (ultimo_peso,)
                    self.tabla_sin_inventariar.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los animales:\n{e}")

    def buscar_animal(self):
        """Busca un animal por código"""
        codigo = self.entry_codigo_busqueda.get().strip()
        if not codigo:
            messagebox.showwarning("Atención", "Ingrese un código para buscar.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.*, f.nombre as finca, r.nombre as raza, p.nombre as potrero
                    FROM animal a
                    LEFT JOIN finca f ON a.id_finca = f.id
                    LEFT JOIN raza r ON a.raza = r.nombre
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    WHERE a.codigo = ? AND a.estado = 'Activo'
                """, (codigo,))
                
                animal = cursor.fetchone()
                
                if animal:
                    self.animal_actual = animal
                    self.mostrar_info_animal(animal)
                    self.limpiar_campos_actualizacion()
                else:
                    messagebox.showerror("No encontrado", f"No se encontró un animal activo con código: {codigo}")
                    self.animal_actual = None
                    self.label_info_animal.configure(text="Animal no encontrado")
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el animal:\n{e}")

    def mostrar_info_animal(self, animal):
        """Muestra la información del animal encontrado"""
        info_text = f"""
🐄 **ANIMAL ENCONTRADO**

🏷️  **CÓDIGO:** {animal[2]}
📛  **NOMBRE:** {animal[3] or 'No asignado'}
🏞️  **FINCA:** {animal[28] or 'No asignada'}

⚤  **SEXO:** {animal[5]}
🐄  **RAZA:** {animal[29] or 'No especificada'}
📍  **POTRERO:** {animal[30] or 'No asignado'}

📥  **TIPO INGRESO:** {animal[4]}
🏥  **SALUD:** {animal[19]}
✅  **ESTADO:** {animal[20]}
📋  **INVENTARIADO:** {'Sí' if animal[21] == 1 else 'No'}

*Listo para actualizar información*
"""
        self.label_info_animal.configure(text=info_text)

    def seleccionar_de_lista(self, event):
        """Selecciona un animal de la lista de sin inventariar"""
        seleccionado = self.tabla_sin_inventariar.selection()
        if seleccionado:
            codigo = self.tabla_sin_inventariar.item(seleccionado[0])["values"][0]
            self.entry_codigo_busqueda.delete(0, "end")
            self.entry_codigo_busqueda.insert(0, codigo)
            self.buscar_animal()

    def registrar_peso(self):
        """Registra el peso actual del animal"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Busque un animal primero.")
            return

        peso_str = self.entry_peso_actual.get().strip()
        if not peso_str:
            messagebox.showwarning("Atención", "Ingrese el peso del animal.")
            return

        try:
            peso = float(peso_str)
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO peso (id_animal, fecha, peso, tipo_peso, comentario)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.animal_actual[0], datetime.now().strftime("%Y-%m-%d"), peso, "Rutina", "Registro durante inventario"))
                conn.commit()

            messagebox.showinfo("Éxito", f"Peso de {peso} kg registrado correctamente para {self.animal_actual[2]}")
            self.entry_peso_actual.delete(0, "end")
            
        except ValueError:
            messagebox.showerror("Error", "El peso debe ser un número válido.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el peso:\n{e}")

    def registrar_tratamiento(self):
        """Registra un tratamiento aplicado al animal"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Busque un animal primero.")
            return

        tratamiento = self.entry_tratamiento.get().strip()
        producto = self.entry_producto.get().strip()

        if not tratamiento or not producto:
            messagebox.showwarning("Atención", "Complete ambos campos: tratamiento y producto.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tratamiento (id_animal, fecha, tipo_tratamiento, producto, dosis, veterinario, comentario)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (self.animal_actual[0], datetime.now().strftime("%Y-%m-%d"), tratamiento, producto, "Según indicaciones", "Veterinario de finca", "Aplicado durante inventario"))
                conn.commit()

            messagebox.showinfo("Éxito", f"Tratamiento '{tratamiento}' registrado correctamente para {self.animal_actual[2]}")
            self.entry_tratamiento.delete(0, "end")
            self.entry_producto.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el tratamiento:\n{e}")

    def marcar_inventario(self, estado):
        """Marca el animal como inventariado o no inventariado"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Busque un animal primero.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE animal SET inventariado = ? WHERE id = ?", 
                             (estado, self.animal_actual[0]))
                conn.commit()

            estado_text = "INVENTARIADO" if estado == 1 else "NO INVENTARIADO (FALTANTE)"
            messagebox.showinfo("Éxito", f"Animal {self.animal_actual[2]} marcado como {estado_text}")
            
            # Actualizar lista
            self.cargar_animales_finca()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el estado de inventario:\n{e}")

    def guardar_comentario_rapido(self):
        """Guarda un comentario rápido para el animal"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Busque un animal primero.")
            return

        comentario = self.text_comentario_rapido.get("1.0", "end-1c").strip()
        if not comentario:
            messagebox.showwarning("Atención", "Escriba un comentario.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO comentario (id_animal, fecha, autor, nota)
                    VALUES (?, ?, ?, ?)
                """, (self.animal_actual[0], datetime.now().strftime("%Y-%m-%d"), "Sistema Inventario", comentario))
                conn.commit()

            messagebox.showinfo("Éxito", "Comentario guardado correctamente")
            self.text_comentario_rapido.delete("1.0", "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el comentario:\n{e}")

    def limpiar_campos_actualizacion(self):
        """Limpia los campos de actualización"""
        self.entry_peso_actual.delete(0, "end")
        self.entry_tratamiento.delete(0, "end")
        self.entry_producto.delete(0, "end")
        self.text_comentario_rapido.delete("1.0", "end")