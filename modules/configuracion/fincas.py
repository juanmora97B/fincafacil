import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.importador_excel import parse_excel_to_dicts


class FincasFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_fincas()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="🏠 Configuración de Fincas", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nueva Finca", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Nombre *:", width=100).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, width=200)
        self.entry_nombre.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Propietario:", width=100).pack(side="left", padx=5)
        self.entry_propietario = ctk.CTkEntry(row2, width=200)
        self.entry_propietario.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Área (Ha):", width=80).pack(side="left", padx=5)
        self.entry_area = ctk.CTkEntry(row2, width=100)
        self.entry_area.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Ubicación:", width=100).pack(side="left", padx=5)
        self.entry_ubicacion = ctk.CTkEntry(row3, width=300)
        self.entry_ubicacion.pack(side="left", padx=5, fill="x", expand=True)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Teléfono:", width=100).pack(side="left", padx=5)
        self.entry_telefono = ctk.CTkEntry(row4, width=150)
        self.entry_telefono.pack(side="left", padx=5)
        ctk.CTkLabel(row4, text="Email:", width=80).pack(side="left", padx=5)
        self.entry_email = ctk.CTkEntry(row4, width=150)
        self.entry_email.pack(side="left", padx=5)

        row5 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Descripción:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_descripcion = ctk.CTkTextbox(row5, width=300, height=60)
        self.text_descripcion.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Finca", command=self.guardar_finca, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(self, text="📋 Fincas Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=20)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "propietario", "area", "ubicacion"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("propietario", "Propietario", 120),
            ("area", "Área (Ha)", 80),
            ("ubicacion", "Ubicación", 200)
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
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_finca).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_finca, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_fincas).pack(side="left", padx=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=10)
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_finca).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_finca, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_fincas).pack(side="left", padx=5)

    def guardar_finca(self):
        """Guarda una nueva finca"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO finca (codigo, nombre, propietario, ubicacion, area_hectareas, telefono, email, descripcion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    codigo,
                    nombre,
                    self.entry_propietario.get().strip(),
                    self.entry_ubicacion.get().strip(),
                    float(self.entry_area.get() or 0),
                    self.entry_telefono.get().strip(),
                    self.entry_email.get().strip(),
                    self.text_descripcion.get("1.0", "end-1c").strip()
                ))
                conn.commit()

            messagebox.showinfo("Éxito", "Finca guardada correctamente.")
            self.limpiar_formulario()
            self.cargar_fincas()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe una finca con ese código.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la finca:\n{e}")

    def cargar_fincas(self):
        """Carga las fincas en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, propietario, area_hectareas, ubicacion FROM finca WHERE estado = 'Activo'")
                
                for fila in cursor.fetchall():
                    self.tabla.insert("", "end", values=fila)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def editar_finca(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una finca para editar.")
            return
        messagebox.showinfo("Editar", "Funcionalidad de edición en desarrollo")

    def eliminar_finca(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una finca para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la finca '{codigo}'?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE finca SET estado = 'Inactivo' WHERE codigo = ?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Finca eliminada.")
                self.cargar_fincas()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_propietario.delete(0, "end")
        self.entry_ubicacion.delete(0, "end")
        self.entry_area.delete(0, "end")
        
    def importar_excel(self):
        """Importar fincas desde un archivo Excel.
        Se esperan encabezados: codigo,nombre,propietario,ubicacion,area,estado
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

        # Validar que exista la columna nombre
        primera = filas[0]
        if 'nombre' not in primera:
            messagebox.showerror("Error", "El archivo debe tener una columna 'nombre'.")
            return

        importados = 0
        errores = []

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                for idx, fila in enumerate(filas, start=2):
                    nombre = str(fila.get('nombre') or "").strip()
                    codigo = str(fila.get('codigo') or "").strip()

                    if not nombre:
                        errores.append(f"Fila {idx}: falta nombre")
                        continue

                    try:
                        # Verificar si la finca ya existe
                        cursor.execute("SELECT COUNT(*) FROM finca WHERE nombre = ? OR codigo = ?", (nombre, codigo))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: la finca '{nombre}' o código '{codigo}' ya existe")
                            continue

                        # Insertar nueva finca
                        cursor.execute("""
                            INSERT INTO finca (codigo, nombre, propietario, ubicacion, area_hectareas, estado)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            codigo or None,
                            nombre,
                            str(fila.get('propietario') or "").strip() or None,
                            str(fila.get('ubicacion') or "").strip() or None,
                            float(fila.get('area') or 0),
                            str(fila.get('estado') or "Activo").strip()
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: finca duplicada")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_fincas()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")
        self.entry_telefono.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.text_descripcion.delete("1.0", "end")

    def importar_excel(self):
        """Importar fincas desde un archivo Excel usando el util genérico.
        Se esperan encabezados que contengan al menos 'codigo' y 'nombre'.
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

        # Validar que existan columnas clave
        primera = filas[0]
        if 'codigo' not in primera or 'nombre' not in primera:
            messagebox.showerror("Error", "El archivo debe tener columnas con encabezados 'codigo' y 'nombre'.")
            return

        # Preguntar si desea simular la importación (modo dry-run)
        simular = messagebox.askyesno("Simular importación", "¿Desea simular la importación?\n(Si selecciona 'Sí' se validarán los datos pero no se guardarán en la base de datos)")

        importados = 0
        errores = []

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
                            INSERT INTO finca (codigo, nombre, propietario, ubicacion, area_hectareas, telefono, email, descripcion, estado)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Activo')
                        """,
                            (
                                codigo,
                                nombre,
                                fila.get('propietario') or None,
                                fila.get('ubicacion') or None,
                                float(fila.get('area') or fila.get('area_hectareas') or 0),
                                fila.get('telefono') or None,
                                fila.get('email') or None,
                                fila.get('descripcion') or None
                            )
                        )
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: código duplicado ({codigo})")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {e}")
                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_fincas()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")