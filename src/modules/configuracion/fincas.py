import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.importador_excel import parse_excel_to_dicts, mapear_columnas_flexibles


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

        # Frame del formulario (scrollable para evitar recortes)
        form_frame = ctk.CTkScrollableFrame(self, corner_radius=10, height=220)
        form_frame.pack(pady=10, padx=4, fill="x")

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
        ctk.CTkLabel(self, text="📋 Fincas Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20, 5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla y configuración de columnas
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
        # Diccionario interno: item_id -> finca_id
        self.finca_ids = {}

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

        # Convertir área a float seguro
        area_val = self.entry_area.get().strip()
        try:
            area = float(area_val) if area_val else 0
        except ValueError:
            area = 0

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si existe una finca inactiva con el mismo código
                cursor.execute("SELECT id, estado FROM finca WHERE codigo = ?", (codigo,))
                finca_existente = cursor.fetchone()
                
                if finca_existente:
                    if finca_existente[1] == 'Inactivo':
                        # Preguntar si desea reactivar
                        if messagebox.askyesno("Finca Inactiva", 
                            f"Ya existe una finca inactiva con el código '{codigo}'.\n¿Desea reactivarla y actualizar sus datos?"):
                            cursor.execute("""
                                UPDATE finca 
                                SET nombre = ?, propietario = ?, ubicacion = ?, area_hectareas = ?,
                                    telefono = ?, email = ?, descripcion = ?, estado = 'Activo'
                                WHERE id = ?
                            """, (
                                nombre,
                                self.entry_propietario.get().strip() or None,
                                self.entry_ubicacion.get().strip() or None,
                                area,
                                self.entry_telefono.get().strip() or None,
                                self.entry_email.get().strip() or None,
                                self.text_descripcion.get("1.0", "end-1c").strip() or None,
                                finca_existente[0]
                            ))
                            conn.commit()
                            messagebox.showinfo("Éxito", "Finca reactivada y actualizada correctamente.")
                            self.limpiar_formulario()
                            self.cargar_fincas()
                            return
                        else:
                            return
                    else:
                        messagebox.showerror("Error", "Ya existe una finca activa con ese código.")
                        return
                
                # Si no existe, insertar nueva finca
                cursor.execute(
                    """
                    INSERT INTO finca (codigo, nombre, propietario, ubicacion, area_hectareas, telefono, email, descripcion, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Activo')
                    """,
                    (
                        codigo,
                        nombre,
                        self.entry_propietario.get().strip() or None,
                        self.entry_ubicacion.get().strip() or None,
                        area,
                        self.entry_telefono.get().strip() or None,
                        self.entry_email.get().strip() or None,
                        self.text_descripcion.get("1.0", "end-1c").strip() or None,
                    ),
                )
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
                # Reiniciar mapa
                self.finca_ids.clear()
                try:
                    cursor.execute(
                        "SELECT id, codigo, nombre, propietario, area_hectareas, ubicacion FROM finca WHERE estado = 'Activo'"
                    )
                except sqlite3.OperationalError:
                    cursor.execute(
                        "SELECT id, codigo, nombre, propietario, area_hectareas, ubicacion FROM finca"
                    )

                for fila in cursor.fetchall():
                    finca_id, codigo, nombre, propietario, area, ubicacion = fila
                    valores = (
                        str(codigo or ""),
                        str(nombre or ""),
                        str(propietario or ""),
                        str(area if area is not None else 0),
                        str(ubicacion or "")
                    )
                    item_id = self.tabla.insert("", "end", values=valores)
                    self.finca_ids[item_id] = finca_id

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def editar_finca(self):
        """Edita la finca seleccionada"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una finca para editar.")
            return

        # Obtener código de la finca seleccionada
        codigo = self.tabla.item(seleccionado[0])["values"][0]

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # Intentar obtener id directo desde el mapping
                item_id = seleccionado[0]
                finca_id = getattr(self, 'finca_ids', {}).get(item_id)
                finca = None
                if finca_id:
                    cursor.execute("SELECT * FROM finca WHERE id = ?", (finca_id,))
                    finca = cursor.fetchone()
                if not finca:
                    # Fallback por variantes de código (ej: 01 vs 1)
                    codigo_str = str(codigo).strip()
                    variantes = [codigo_str]
                    sin_ceros = codigo_str.lstrip('0')
                    if sin_ceros and sin_ceros != codigo_str:
                        variantes.append(sin_ceros)
                    placeholders = ','.join(['?'] * len(variantes))
                    cursor.execute(f"SELECT * FROM finca WHERE codigo IN ({placeholders}) LIMIT 1", variantes)
                    finca = cursor.fetchone()
                if not finca:
                    messagebox.showerror("Error", "No se encontró la finca.")
                    return

                # Crear ventana de edición
                ventana_edicion = ctk.CTkToplevel(self)
                ventana_edicion.title("Editar Finca")
                ventana_edicion.geometry("600x550")
                ventana_edicion.transient(self)
                ventana_edicion.grab_set()

                # Frame principal con scroll
                main_frame = ctk.CTkScrollableFrame(ventana_edicion)
                # Compactar ancho (padx 20→4)
                main_frame.pack(padx=4, pady=20, fill="both", expand=True)

                # Título
                ctk.CTkLabel(main_frame, text="✏️ Editar Finca", 
                            font=("Segoe UI", 18, "bold")).pack(pady=10)

                # Campos del formulario
                ctk.CTkLabel(main_frame, text="Código:").pack(anchor="w", padx=5, pady=2)
                entry_codigo = ctk.CTkEntry(main_frame, width=300)
                entry_codigo.insert(0, finca[1])  # codigo
                entry_codigo.configure(state="disabled")
                entry_codigo.pack(anchor="w", padx=5, pady=2)

                ctk.CTkLabel(main_frame, text="Nombre *:").pack(anchor="w", padx=5, pady=2)
                entry_nombre = ctk.CTkEntry(main_frame, width=300)
                entry_nombre.insert(0, finca[2] if finca[2] else "")  # nombre
                entry_nombre.pack(anchor="w", padx=5, pady=2)

                ctk.CTkLabel(main_frame, text="Propietario:").pack(anchor="w", padx=5, pady=2)
                entry_propietario = ctk.CTkEntry(main_frame, width=300)
                entry_propietario.insert(0, finca[3] if finca[3] else "")  # propietario
                entry_propietario.pack(anchor="w", padx=5, pady=2)

                ctk.CTkLabel(main_frame, text="Ubicación:").pack(anchor="w", padx=5, pady=2)
                entry_ubicacion = ctk.CTkEntry(main_frame, width=300)
                entry_ubicacion.insert(0, finca[4] if finca[4] else "")  # ubicacion
                entry_ubicacion.pack(anchor="w", padx=5, pady=2)

                ctk.CTkLabel(main_frame, text="Área (Hectáreas):").pack(anchor="w", padx=5, pady=2)
                entry_area = ctk.CTkEntry(main_frame, width=300)
                entry_area.insert(0, str(finca[5]) if finca[5] else "0")  # area_hectareas
                entry_area.pack(anchor="w", padx=5, pady=2)

                ctk.CTkLabel(main_frame, text="Teléfono:").pack(anchor="w", padx=5, pady=2)
                entry_telefono = ctk.CTkEntry(main_frame, width=300)
                entry_telefono.insert(0, finca[6] if finca[6] else "")  # telefono
                entry_telefono.pack(anchor="w", padx=5, pady=2)

                ctk.CTkLabel(main_frame, text="Email:").pack(anchor="w", padx=5, pady=2)
                entry_email = ctk.CTkEntry(main_frame, width=300)
                entry_email.insert(0, finca[7] if finca[7] else "")  # email
                entry_email.pack(anchor="w", padx=5, pady=2)

                ctk.CTkLabel(main_frame, text="Descripción:").pack(anchor="w", padx=5, pady=2)
                text_descripcion = ctk.CTkTextbox(main_frame, width=300, height=100)
                text_descripcion.insert("1.0", finca[8] if finca[8] else "")  # descripcion
                text_descripcion.pack(anchor="w", padx=5, pady=2)

                def guardar_cambios():
                    """Guarda los cambios de la finca"""
                    nombre = entry_nombre.get().strip()
                    if not nombre:
                        messagebox.showwarning("Atención", "El nombre es obligatorio.")
                        return

                    # Validar área
                    area_val = entry_area.get().strip()
                    try:
                        area = float(area_val) if area_val else 0
                    except ValueError:
                        messagebox.showwarning("Atención", "El área debe ser un valor numérico.")
                        return

                    try:
                        # Crear nueva conexión para esta operación
                        with db.get_connection() as conn_update:
                            cursor_update = conn_update.cursor()
                            # Usar id en lugar de codigo para evitar problemas con variantes
                            cursor_update.execute("""
                                UPDATE finca 
                                SET nombre = ?, propietario = ?, ubicacion = ?, area_hectareas = ?,
                                    telefono = ?, email = ?, descripcion = ?
                                WHERE id = ?
                            """, (
                                nombre,
                                entry_propietario.get().strip() or None,
                                entry_ubicacion.get().strip() or None,
                                area,
                                entry_telefono.get().strip() or None,
                                entry_email.get().strip() or None,
                                text_descripcion.get("1.0", "end-1c").strip() or None,
                                finca[0]  # id es la primera columna
                            ))
                            if cursor_update.rowcount == 0:
                                messagebox.showerror("Error", "No se actualizó ningún registro (id no encontrado).")
                                return
                            conn_update.commit()
                        
                        messagebox.showinfo("Éxito", "Finca actualizada correctamente.")
                        ventana_edicion.destroy()
                        self.cargar_fincas()
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo actualizar la finca:\n{e}")

                # Botones
                btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                btn_frame.pack(pady=20)
                
                ctk.CTkButton(btn_frame, text="💾 Guardar Cambios", command=guardar_cambios,
                            fg_color="green", hover_color="#006400").pack(side="left", padx=5)
                ctk.CTkButton(btn_frame, text="❌ Cancelar", command=ventana_edicion.destroy,
                            fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la finca para editar:\n{e}")

    def eliminar_finca(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una finca para eliminar.")
            return

        try:
            codigo = self.tabla.item(seleccionado[0])["values"][0]
        except (IndexError, KeyError):
            messagebox.showerror("Error", "No se pudo obtener el código de la finca seleccionada.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la finca '{codigo}'?\n\nEsta acción no se puede deshacer."):
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # Asegurar que el código sea string para permitir operaciones de texto
                codigo_str = str(codigo).strip()
                if not codigo_str:
                    messagebox.showerror("Error", "Código vacío, no se puede eliminar.")
                    return

                # Obtener id directo desde el mapping de la tabla si existe
                item_id = seleccionado[0]
                finca_id = self.finca_ids.get(item_id)
                if not finca_id:
                    # Fallback búsqueda por variantes
                    variantes = [codigo_str]
                    sin_ceros = codigo_str.lstrip('0')
                    if sin_ceros and sin_ceros != codigo_str:
                        variantes.append(sin_ceros)
                    placeholders = ','.join(['?'] * len(variantes))
                    cursor.execute(
                        f"SELECT id FROM finca WHERE codigo IN ({placeholders}) LIMIT 1",
                        variantes
                    )
                    row = cursor.fetchone()
                    if not row:
                        messagebox.showerror("Error", "No se encontró la finca seleccionada.")
                        return
                    finca_id = row[0] if isinstance(row, tuple) else row['id']

                # Eliminar por id para evitar ambigüedades de formato
                cursor.execute("DELETE FROM finca WHERE id = ?", (finca_id,))
                if cursor.rowcount != 1:
                    messagebox.showerror("Error", "No se pudo eliminar la finca (rowcount inesperado).")
                    return
                conn.commit()
            messagebox.showinfo("Éxito", "Finca eliminada correctamente.")
            self.cargar_fincas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_propietario.delete(0, "end")
        self.entry_ubicacion.delete(0, "end")
        self.entry_area.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.text_descripcion.delete("1.0", "end")

    def importar_excel(self):
        """Importar fincas desde un archivo Excel usando el util genérico.
        Se esperan encabezados que contengan al menos 'codigo' y 'nombre'.
        """
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=(("Excel files", "*.xlsx;*.xls"), ("Todos los archivos", "*.*")),
        )
        if not ruta:
            return

        filas, errores_parse = parse_excel_to_dicts(ruta)
        if errores_parse:
            messagebox.showerror("Error", "\n".join(errores_parse))
            return

        if not filas:
            messagebox.showinfo("Importar", "No se encontraron filas para importar.")
            return

        # Definir mapa de columnas alternativas para búsqueda flexible
        mapa_columnas = {
            'codigo': ['codigo', 'código', 'cod', 'code'],
            'nombre': ['nombre', 'name', 'finca'],
            'propietario': ['propietario', 'dueño', 'dueno', 'owner'],
            'ubicacion': ['ubicacion', 'ubicación', 'direccion', 'dirección', 'location'],
            'area': ['area', 'area_ha', 'area_hectareas', 'hectareas', 'hectáreas', 'ha'],
            'telefono': ['telefono', 'teléfono', 'tel', 'phone'],
            'email': ['email', 'correo', 'e-mail', 'mail'],
            'descripcion': ['descripcion', 'descripción', 'observaciones', 'notas']
        }

        # Normalizar columnas en todas las filas
        filas_normalizadas = [mapear_columnas_flexibles(fila, mapa_columnas) for fila in filas]

        # Validar que existan columnas clave
        primera = filas_normalizadas[0]
        if not primera.get("codigo") or not primera.get("nombre"):
            messagebox.showerror("Error", 
                "El archivo debe tener columnas que correspondan a 'codigo' y 'nombre'.\n"
                "Variantes aceptadas:\n"
                "- Código: codigo, código, cod, code\n"
                "- Nombre: nombre, name, finca")
            return

        # Preguntar si desea simular la importación (modo dry-run)
        simular = messagebox.askyesno(
            "Simular importación",
            "¿Desea simular la importación?\n(Si selecciona 'Sí' se validarán los datos pero no se guardarán en la base de datos)",
        )

        importados = 0
        errores = []

        def validar_fila(idx, fila):
            codigo = str(fila.get("codigo") or "").strip()
            nombre = str(fila.get("nombre") or "").strip()
            if not codigo or not nombre:
                return False, f"Fila {idx}: falta código o nombre"
            return True, None

        try:
            if simular:
                for idx, fila in enumerate(filas_normalizadas, start=2):
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
                for idx, fila in enumerate(filas_normalizadas, start=2):
                    ok, err = validar_fila(idx, fila)
                    if not ok:
                        errores.append(err)
                        continue

                    codigo = str(fila.get("codigo") or "").strip()
                    nombre = str(fila.get("nombre") or "").strip()

                    # Convertir área a float de forma segura
                    area_raw = fila.get("area")
                    try:
                        area_val = float(area_raw) if area_raw not in (None, "") else 0
                    except (ValueError, TypeError):
                        area_val = 0

                    try:
                        cursor.execute(
                            """
                            INSERT INTO finca (codigo, nombre, propietario, ubicacion, area_hectareas, telefono, email, descripcion, estado)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Activo')
                            """,
                            (
                                codigo,
                                nombre,
                                fila.get("propietario") or None,
                                fila.get("ubicacion") or None,
                                area_val,
                                fila.get("telefono") or None,
                                fila.get("email") or None,
                                fila.get("descripcion") or None,
                            ),
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