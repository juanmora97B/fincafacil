import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.conexion import db
from modules.utils.importador_excel import parse_excel_to_dicts


class CondicionesCorporalesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_condiciones()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="⚖️ Configuración de Condiciones Corporales", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nueva Condición Corporal", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150,)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Descripción *:", width=100).pack(side="left", padx=5)
        self.entry_descripcion = ctk.CTkEntry(row1, width=200,)
        self.entry_descripcion.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Puntuación *:", width=100).pack(side="left", padx=5)
        self.entry_puntuacion = ctk.CTkEntry(row2, width=100,)
        self.entry_puntuacion.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Escala:", width=80).pack(side="left", padx=5)
        self.combo_escala = ctk.CTkComboBox(row2, 
            values=["1-5", "1-9", "1-10", "A-E", "Otra"],
            width=120)
        self.combo_escala.set("1-5")
        self.combo_escala.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Especie:", width=100).pack(side="left", padx=5)
        self.combo_especie = ctk.CTkComboBox(row3, 
            values=["Bovino", "Porcino", "Ovino", "Caprino", "Equino", "Aves", "Todos"],
            width=150)
        self.combo_especie.set("Bovino")
        self.combo_especie.pack(side="left", padx=5)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Características:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_caracteristicas = ctk.CTkTextbox(row4, width=300, height=80,)
        self.text_caracteristicas.pack(side="left", padx=5, fill="x", expand=True)

        row5 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Recomendaciones:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_recomendaciones = ctk.CTkTextbox(row5, width=300, height=80,)
        self.text_recomendaciones.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Condición", command=self.guardar_condicion, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(self, text="📋 Condiciones Corporales Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=20)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "descripcion", "puntuacion", "escala", "especie"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("descripcion", "Descripción", 180),
            ("puntuacion", "Puntuación", 100),
            ("escala", "Escala", 80),
            ("especie", "Especie", 100)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=10)
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_condicion).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_condicion, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_condiciones).pack(side="left", padx=5)

        # Menú contextual (clic derecho)
        from tkinter import Menu
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_condicion)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_condicion)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_condiciones)
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_condicion())

        def mostrar_menu_contextual(self, event):
            try:
                row_id = self.tabla.identify_row(event.y)
                if row_id:
                    self.tabla.selection_set(row_id)
                self.menu_contextual.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu_contextual.grab_release()

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=10)

        ctk.CTkButton(action_frame, text="👁️ Ver Detalles", command=self.ver_detalles).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_condicion).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_condicion, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_condiciones).pack(side="left", padx=5)
        
    def guardar_condicion(self):
        """Guarda una nueva condición corporal"""
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        puntuacion = self.entry_puntuacion.get().strip()
        
        if not codigo or not descripcion or not puntuacion:
            messagebox.showwarning("Atención", "Código, Descripción y Puntuación son campos obligatorios.")
            return

        # Validar que la puntuación sea numérica
        try:
            float(puntuacion)
        except ValueError:
            messagebox.showwarning("Atención", "La puntuación debe ser un valor numérico.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO condicion_corporal 
                    (codigo, descripcion, puntuacion, escala, especie, caracteristicas, recomendaciones, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    codigo,
                    descripcion,
                    puntuacion,
                    self.combo_escala.get(),
                    self.combo_especie.get(),
                    self.text_caracteristicas.get("1.0", "end-1c").strip(),
                    self.text_recomendaciones.get("1.0", "end-1c").strip(),
                    "Activo"
                ))
                conn.commit()

            messagebox.showinfo("Éxito", "Condición corporal guardada correctamente.")
            self.limpiar_formulario()
            self.cargar_condiciones()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe una condición con ese código.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la condición:\n{e}")

    def cargar_condiciones(self):
        """Carga las condiciones corporales en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, descripcion, puntuacion, escala, especie 
                    FROM condicion_corporal 
                    WHERE estado = 'Activo'
                    ORDER BY especie, puntuacion
                """)
                
                for fila in cursor.fetchall():
                    self.tabla.insert("", "end", values=fila)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las condiciones:\n{e}")

    def ver_detalles(self):
        """Muestra los detalles de la condición corporal seleccionada"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una condición para ver los detalles.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT descripcion, puntuacion, escala, especie, caracteristicas, recomendaciones
                    FROM condicion_corporal 
                    WHERE codigo = ?
                """, (codigo,))
                
                resultado = cursor.fetchone()
                if resultado:
                    descripcion, puntuacion, escala, especie, caracteristicas, recomendaciones = resultado
                    
                    # Crear ventana de detalles
                    detalles_window = ctk.CTkToplevel(self)
                    detalles_window.title(f"Detalles - {codigo}")
                    detalles_window.geometry("600x500")
                    detalles_window.transient(self)
                    detalles_window.grab_set()
                    
                    # Contenido de la ventana
                    frame = ctk.CTkFrame(detalles_window)
                    frame.pack(fill="both", expand=True, padx=20, pady=20)
                    
                    ctk.CTkLabel(frame, text=f"📋 Detalles de Condición Corporal", 
                                font=("Segoe UI", 18, "bold")).pack(pady=10)
                    
                    # Información básica
                    info_frame = ctk.CTkFrame(frame)
                    info_frame.pack(fill="x", pady=10, padx=10)
                    
                    datos = [
                        ("Código:", codigo),
                        ("Descripción:", descripcion),
                        ("Puntuación:", puntuacion),
                        ("Escala:", escala),
                        ("Especie:", especie)
                    ]
                    
                    for label, valor in datos:
                        row = ctk.CTkFrame(info_frame, fg_color="transparent")
                        row.pack(fill="x", pady=2)
                        ctk.CTkLabel(row, text=label, width=120, font=("Segoe UI", 12, "bold")).pack(side="left")
                        ctk.CTkLabel(row, text=valor, font=("Segoe UI", 12)).pack(side="left")
                    
                    # Características
                    ctk.CTkLabel(frame, text="📝 Características Físicas:", 
                                font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(20,5))
                    text_caracteristicas = ctk.CTkTextbox(frame, height=80)
                    text_caracteristicas.pack(fill="x", pady=5)
                    text_caracteristicas.insert("1.0", caracteristicas or "No especificado")
                    text_caracteristicas.configure(state="disabled")
                    
                    # Recomendaciones
                    ctk.CTkLabel(frame, text="💡 Recomendaciones:", 
                                font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(20,5))
                    text_recomendaciones = ctk.CTkTextbox(frame, height=80)
                    text_recomendaciones.pack(fill="x", pady=5)
                    text_recomendaciones.insert("1.0", recomendaciones or "No especificado")
                    text_recomendaciones.configure(state="disabled")
                    
                    # Botón cerrar
                    ctk.CTkButton(frame, text="Cerrar", command=detalles_window.destroy).pack(pady=10)
                    
                else:
                    messagebox.showerror("Error", "No se encontraron los detalles de la condición seleccionada.")
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles:\n{e}")

    def editar_condicion(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una condición para editar.")
            return
        messagebox.showinfo("Editar", "Funcionalidad de edición en desarrollo")

    def eliminar_condicion(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una condición para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        descripcion = self.tabla.item(seleccionado[0])["values"][1]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar la condición '{codigo} - {descripcion}'?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE condicion_corporal SET estado = 'Inactivo' WHERE codigo = ?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Condición corporal eliminada.")
                self.cargar_condiciones()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.entry_puntuacion.delete(0, "end")
        self.text_caracteristicas.delete("1.0", "end")
        self.text_recomendaciones.delete("1.0", "end")
        self.combo_escala.set("1-5")
        self.combo_especie.set("Bovino")
        
    def importar_excel(self):
        """Importar condiciones corporales desde un archivo Excel.
        Se esperan encabezados: codigo,descripcion,puntuacion,escala,especie,caracteristicas,recomendaciones,estado
        """
        ruta = filedialog.askopenfilename(title="Seleccionar archivo Excel", filetypes=[("Excel files", "*.xlsx *.xls"), ("Todos los archivos", "*.*")])
        if not ruta:
            return

        filas, errores_parse = parse_excel_to_dicts(ruta)
        if errores_parse:
            messagebox.showerror("Error", "\n".join(errores_parse))
            return

        if not filas:
            messagebox.showinfo("Importar", "No se encontraron filas para importar.")
            return

        # Validar que existan columnas requeridas
        primera = filas[0]
        if 'codigo' not in primera or 'descripcion' not in primera or 'puntuacion' not in primera:
            messagebox.showerror("Error", "El archivo debe tener las columnas 'codigo', 'descripcion' y 'puntuacion'.")
            return

        importados = 0
        errores = []

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                for idx, fila in enumerate(filas, start=2):
                    codigo = str(fila.get('codigo') or "").strip()
                    descripcion = str(fila.get('descripcion') or "").strip()
                    puntuacion = str(fila.get('puntuacion') or "").strip()

                    if not codigo or not descripcion or not puntuacion:
                        errores.append(f"Fila {idx}: faltan campos requeridos (código, descripción y puntuación)")
                        continue

                    # Validar puntuación numérica
                    try:
                        float(puntuacion)
                    except ValueError:
                        errores.append(f"Fila {idx}: la puntuación debe ser un número")
                        continue

                    try:
                        # Verificar si la condición ya existe
                        cursor.execute("SELECT COUNT(*) FROM condicion_corporal WHERE codigo = ?", (codigo,))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: la condición con código '{codigo}' ya existe")
                            continue

                        # Insertar nueva condición corporal
                        cursor.execute("""
                            INSERT INTO condicion_corporal 
                            (codigo, descripcion, puntuacion, escala, especie, caracteristicas, recomendaciones, estado)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            descripcion,
                            float(puntuacion),
                            str(fila.get('escala') or "1-5").strip(),
                            str(fila.get('especie') or "Bovino").strip(),
                            str(fila.get('caracteristicas') or "").strip() or None,
                            str(fila.get('recomendaciones') or "").strip() or None,
                            str(fila.get('estado') or "Activo").strip()
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: condición corporal duplicada")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_condiciones()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")