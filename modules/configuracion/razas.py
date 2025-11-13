import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.conexion import db
from modules.utils.importador_excel import parse_excel_to_dicts


class RazasFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_razas()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="🐄 Configuración de Razas", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nueva Raza", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150,)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Nombre *:", width=100).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, width=150,)
        self.entry_nombre.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Tipo Ganado:", width=100).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(row2, values=["Lechero", "Carne", "Doble Propósito", "Registro"], width=200)
        self.combo_tipo.set("Doble Propósito")
        self.combo_tipo.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Descripción:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_descripcion = ctk.CTkTextbox(row3, width=300, height=60)
        self.text_descripcion.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Raza", command=self.guardar_raza, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(self, text="📋 Razas Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=20)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "tipo", "descripcion"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("tipo", "Tipo", 120),
            ("descripcion", "Descripción", 300)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        # Menu contextual
        self.menu_contextual = tk.Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_raza)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_raza)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_razas)
        
        # Vincular el menú contextual
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_raza())

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=10)
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_raza).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_raza, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_razas).pack(side="left", padx=5)

    def guardar_raza(self):
        """Guarda una nueva raza"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO raza (codigo, nombre, tipo_ganado, descripcion, estado)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    codigo,
                    nombre,
                    self.combo_tipo.get(),
                    self.text_descripcion.get("1.0", "end-1c").strip(),
                    "Activa"
                ))
                conn.commit()

            messagebox.showinfo("Éxito", "Raza guardada correctamente.")
            self.limpiar_formulario()
            self.cargar_razas()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe una raza con ese código o nombre.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la raza:\n{e}")

    def cargar_razas(self):
        """Carga las razas en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, COALESCE(tipo_ganado, especie, 'N/A') as tipo, descripcion FROM raza WHERE estado = 'Activa' OR estado = 'Activo'")
                
                for fila in cursor.fetchall():
                    # Acortar descripción si es muy larga
                    descripcion = fila[3]
                    if descripcion and len(descripcion) > 50:
                        descripcion = descripcion[:50] + "..."
                    self.tabla.insert("", "end", values=(fila[0], fila[1], fila[2], descripcion))
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las razas:\n{e}")

    def editar_raza(self):
        """Edita la raza seleccionada"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una raza para editar.")
            return

        # Obtener datos del item seleccionado
        item = self.tabla.item(seleccionado[0])
        codigo = item["values"][0]

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM raza WHERE codigo = ?", (codigo,))
                raza = cursor.fetchone()

                if raza:
                    # Crear ventana de edición
                    ventana_edicion = ctk.CTkToplevel(self)
                    ventana_edicion.title("Editar Raza")
                    ventana_edicion.geometry("500x400")
                    ventana_edicion.transient(self)
                    ventana_edicion.grab_set()

                    # Formulario
                    form_frame = ctk.CTkFrame(ventana_edicion)
                    form_frame.pack(padx=20, pady=20, fill="both", expand=True)

                    # Campos
                    ctk.CTkLabel(form_frame, text="Código:").pack(anchor="w", padx=5, pady=2)
                    entry_codigo = ctk.CTkEntry(form_frame, width=200)
                    entry_codigo.insert(0, raza[0])
                    entry_codigo.configure(state="disabled")
                    entry_codigo.pack(anchor="w", padx=5, pady=2)

                    ctk.CTkLabel(form_frame, text="Nombre:").pack(anchor="w", padx=5, pady=2)
                    entry_nombre = ctk.CTkEntry(form_frame, width=200)
                    entry_nombre.insert(0, raza[1])
                    entry_nombre.pack(anchor="w", padx=5, pady=2)

                    ctk.CTkLabel(form_frame, text="Tipo Ganado:").pack(anchor="w", padx=5, pady=2)
                    combo_tipo = ctk.CTkComboBox(form_frame, values=["Lechero", "Carne", "Doble Propósito", "Registro"], width=200)
                    combo_tipo.set(raza[2] if raza[2] else "Doble Propósito")
                    combo_tipo.pack(anchor="w", padx=5, pady=2)

                    ctk.CTkLabel(form_frame, text="Descripción:").pack(anchor="w", padx=5, pady=2)
                    text_descripcion = ctk.CTkTextbox(form_frame, width=300, height=100)
                    text_descripcion.insert("1.0", raza[3] if raza[3] else "")
                    text_descripcion.pack(anchor="w", padx=5, pady=2)

                    def guardar_cambios():
                        try:
                            nombre = entry_nombre.get().strip()
                            if not nombre:
                                messagebox.showwarning("Atención", "El nombre es obligatorio.")
                                return

                            cursor.execute("""
                                UPDATE raza 
                                SET nombre = ?, tipo_ganado = ?, descripcion = ?
                                WHERE codigo = ?
                            """, (
                                nombre,
                                combo_tipo.get(),
                                text_descripcion.get("1.0", "end-1c").strip(),
                                codigo
                            ))
                            conn.commit()
                            messagebox.showinfo("Éxito", "Raza actualizada correctamente.")
                            ventana_edicion.destroy()
                            self.cargar_razas()
                        except Exception as e:
                            messagebox.showerror("Error", f"No se pudo actualizar la raza:\n{e}")

                    # Botones
                    btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
                    btn_frame.pack(pady=20)
                    
                    ctk.CTkButton(btn_frame, text="💾 Guardar", command=guardar_cambios,
                                fg_color="green", hover_color="#006400").pack(side="left", padx=5)
                    ctk.CTkButton(btn_frame, text="❌ Cancelar", command=ventana_edicion.destroy,
                                fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la raza para editar:\n{e}")

    def eliminar_raza(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una raza para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la raza '{codigo}'?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE raza SET estado = 'Inactiva' WHERE codigo = ?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Raza eliminada.")
                self.cargar_razas()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.text_descripcion.delete("1.0", "end")
        self.combo_tipo.set("Doble Propósito")

    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual en la posición del cursor"""
        # Identificar el ítem en la posición del cursor
        item = self.tabla.identify_row(event.y)
        if item:
            # Seleccionar el ítem
            self.tabla.selection_set(item)
            # Mostrar el menú
            self.menu_contextual.post(event.x_root, event.y_root)

    def importar_excel(self):
        """Importar razas desde Excel usando el util genérico.
        Se esperan encabezados con al menos 'codigo' y 'nombre'.
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

        primera = filas[0]
        if 'codigo' not in primera or 'nombre' not in primera:
            messagebox.showerror("Error", "El archivo debe tener columnas con encabezados 'codigo' y 'nombre'.")
            return

        # Preguntar si desea simular la importación (modo dry-run)
        simular = messagebox.askyesno("Simular importación", "¿Desea simular la importación?\n(Si selecciona 'Sí' se validarán los datos pero no se guardarán en la base de datos)")

        importados = 0
        errores = []

        # Función interna para validar una fila y devolver (ok, mensaje_error)
        def validar_fila(idx, fila):
            codigo_val = fila.get('codigo')
            nombre_val = fila.get('nombre')
            codigo = (codigo_val or "").strip() if isinstance(codigo_val, str) else (str(codigo_val) if codigo_val is not None else "")
            nombre = (nombre_val or "").strip() if isinstance(nombre_val, str) else (str(nombre_val) if nombre_val is not None else "")
            if not codigo or not nombre:
                return False, f"Fila {idx}: falta código o nombre"
            return True, None

        try:
            if simular:
                # Solo validar filas
                for idx, fila in enumerate(filas, start=2):
                    ok, err = validar_fila(idx, fila)
                    if ok:
                        importados += 1
                    else:
                        errores.append(err)

                mensaje = f"Simulación finalizada. Filas válidas: {importados}. Errores: {len(errores)}"
                if errores:
                    mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
                messagebox.showinfo("Simulación", mensaje)
                return

            # Modo real: insertar en la BD
            with db.get_connection() as conn:
                cursor = conn.cursor()
                for idx, fila in enumerate(filas, start=2):
                    ok, err = validar_fila(idx, fila)
                    if not ok:
                        errores.append(err)
                        continue

                    codigo = (fila.get('codigo') or "").strip() if isinstance(fila.get('codigo'), str) else (str(fila.get('codigo')) if fila.get('codigo') is not None else "")
                    nombre = (fila.get('nombre') or "").strip() if isinstance(fila.get('nombre'), str) else (str(fila.get('nombre')) if fila.get('nombre') is not None else "")
                    try:
                        cursor.execute(
                            """
                            INSERT INTO raza (codigo, nombre, tipo_ganado, descripcion, estado)
                            VALUES (?, ?, ?, ?, 'Activa')
                        """,
                            (
                                codigo,
                                nombre,
                                fila.get('tipo_ganado') or fila.get('tipo') or None,
                                fila.get('descripcion') or None
                            )
                        )
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: código o nombre duplicado ({codigo})")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {e}")
                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_razas()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")