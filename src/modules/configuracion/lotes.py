import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.importador_excel import parse_excel_to_dicts


class LotesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_fincas_combobox()
        self.cargar_lotes()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="📦 Configuración de Lotes", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Lote", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        # Finca
        row0 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row0.pack(fill="x", pady=5)
        ctk.CTkLabel(row0, text="Finca *:", width=100).pack(side="left", padx=5)
        self.combo_finca = ctk.CTkComboBox(row0, width=300)
        self.combo_finca.set("Seleccione una finca")
        self.combo_finca.pack(side="left", padx=5, fill="x", expand=True)
        
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150, )
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Nombre *:", width=100).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, width=150,)
        self.entry_nombre.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Descripción:", width=100).pack(side="left", padx=5)
        self.entry_descripcion = ctk.CTkEntry(row2, width=300, )
        self.entry_descripcion.pack(side="left", padx=5, fill="x", expand=True)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Criterio:", width=100).pack(side="left", padx=5)
        self.combo_criterio = ctk.CTkComboBox(row3, values=["Por Peso", "Por Edad", "Por Origen", "Por Salud", "Por Producción", "Personalizado"], width=300)
        self.combo_criterio.set("Por Peso")
        self.combo_criterio.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Lote", command=self.guardar_lote, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Lotes Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla (incluir columnas id y finca)
        self.tabla = ttk.Treeview(table_frame, columns=("id", "finca", "codigo", "nombre", "descripcion", "criterio"), show="headings", 
                                  displaycolumns=("finca", "codigo", "nombre", "descripcion", "criterio"), height=12)
        
        column_config = [
            ("id", "ID", 50),  # Oculto
            ("finca", "Finca", 130),
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 130),
            ("descripcion", "Descripción", 180),
            ("criterio", "Criterio", 130)
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
        action_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        action_frame.pack(pady=10)

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_lote).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_lote, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_lotes).pack(side="left", padx=5)
    
    def cargar_fincas_combobox(self):
        """Carga las fincas en el combobox"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
                rows = cursor.fetchall()
                # Mapa interno nombre->id
                self._finca_map = {str(r[1]).strip(): int(r[0]) for r in rows if r[1] is not None}
                nombres = list(self._finca_map.keys())
                self.combo_finca.configure(values=nombres)
                if nombres:
                    self.combo_finca.set(nombres[0])
                else:
                    self.combo_finca.set("Seleccione una finca")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")
        
    def guardar_lote(self):
        """Guarda un nuevo lote o actualiza uno existente"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        finca_nombre = self.combo_finca.get().strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return
        
        if not finca_nombre or finca_nombre == "Seleccione una finca":
            messagebox.showwarning("Atención", "Debe seleccionar una finca.")
            return
        
        # Obtener el ID de la finca
        finca_id = self._finca_map.get(finca_nombre)
        if not finca_id:
            messagebox.showwarning("Atención", "Finca no válida.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si está en modo edición (código deshabilitado)
                if self.entry_codigo.cget("state") == "disabled":
                    # Obtener el ID del lote desde el atributo temporal
                    lote_id = getattr(self, '_editing_lote_id', None)
                    if lote_id:
                        cursor.execute("""
                            UPDATE lote 
                            SET nombre = ?, descripcion = ?, criterio = ?, finca_id = ?
                            WHERE id = ?
                        """, (
                            nombre,
                            self.entry_descripcion.get().strip(),
                            self.combo_criterio.get(),
                            finca_id,
                            lote_id
                        ))
                        messagebox.showinfo("Éxito", "Lote actualizado correctamente.")
                else:
                    cursor.execute("""
                        INSERT INTO lote (codigo, nombre, descripcion, criterio, estado, finca_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        codigo,
                        nombre,
                        self.entry_descripcion.get().strip(),
                        self.combo_criterio.get(),
                        "Activo",
                        finca_id
                    ))
                    messagebox.showinfo("Éxito", "Lote guardado correctamente.")
                
                conn.commit()

            self.limpiar_formulario()
            self.cargar_lotes()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un lote con ese código.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el lote:\n{e}")

    def cargar_lotes(self):
        """Carga los lotes en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT l.id, f.nombre as finca, l.codigo, l.nombre, l.descripcion, 
                           COALESCE(l.criterio, 'N/A') as criterio 
                    FROM lote l
                    LEFT JOIN finca f ON l.finca_id = f.id
                    WHERE l.estado = 'Activo' OR l.estado = 'Activa'
                """)
                
                for fila in cursor.fetchall():
                    # Convertir explícitamente cada valor a string
                    valores = (
                        str(fila[0]) if fila[0] is not None else "",  # id
                        str(fila[1]) if fila[1] is not None else "Sin Finca",  # finca
                        str(fila[2]) if fila[2] is not None else "",  # codigo
                        str(fila[3]) if fila[3] is not None else "",  # nombre
                        str(fila[4]) if fila[4] is not None else "",  # descripcion
                        str(fila[5]) if fila[5] is not None else ""   # criterio
                    )
                    self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los lotes:\n{e}")

    def editar_lote(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un lote para editar.")
            return
        
        # Obtener valores de la fila seleccionada (id, finca, codigo, nombre, descripcion, criterio)
        valores = self.tabla.item(seleccionado[0])["values"]
        
        # Guardar el ID del lote en atributo temporal
        self._editing_lote_id = valores[0]
        
        # Cargar en el formulario
        # Finca
        if valores[1] and valores[1] != "Sin Finca":
            self.combo_finca.set(valores[1])
        
        # Código (índice 2)
        self.entry_codigo.delete(0, "end")
        self.entry_codigo.insert(0, valores[2])
        self.entry_codigo.configure(state="disabled")
        
        # Nombre (índice 3)
        self.entry_nombre.delete(0, "end")
        self.entry_nombre.insert(0, valores[3])
        
        # Descripción (índice 4)
        self.entry_descripcion.delete(0, "end")
        if valores[4]:
            self.entry_descripcion.insert(0, valores[4])
        
        # Criterio (índice 5)
        if valores[5]:
            self.combo_criterio.set(valores[5])
        else:
            self.combo_criterio.set("Por Peso")

    def eliminar_lote(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un lote para eliminar.")
            return
        
        # Obtener ID y código del lote seleccionado
        valores = self.tabla.item(seleccionado[0])["values"]
        lote_id = valores[0]
        lote_codigo = valores[2]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el lote '{lote_codigo}'?\n\nEsta acción no se puede deshacer."):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM lote WHERE id = ?", (lote_id,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Lote eliminado correctamente.")
                self.cargar_lotes()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.combo_criterio.set("Por Peso")
        if hasattr(self, 'combo_finca') and hasattr(self, '_finca_map'):
            nombres = list(self._finca_map.keys())
            if nombres:
                self.combo_finca.set(nombres[0])
            else:
                self.combo_finca.set("Seleccione una finca")
        # Limpiar atributo temporal de edición
        if hasattr(self, '_editing_lote_id'):
            delattr(self, '_editing_lote_id')
        
    def importar_excel(self):
        """Importar lotes desde un archivo Excel.
        Se esperan encabezados mínimos: codigo, nombre, finca.
        Opcionales: descripcion, criterio, estado.
        Ahora soporta columna 'finca' (nombre de la finca) para asignar finca_id.
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

        # Validar columnas requeridas
        primera = filas[0]
        encabezados_norm = {k.lower(): k for k in primera.keys()}
        if 'codigo' not in encabezados_norm or 'nombre' not in encabezados_norm or 'finca' not in encabezados_norm:
            messagebox.showerror("Error", "El archivo debe incluir columnas 'codigo', 'nombre' y 'finca'.")
            return

        importados = 0
        errores = []

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                for idx, fila in enumerate(filas, start=2):
                    codigo = str(fila.get('codigo') or '').strip()
                    nombre = str(fila.get('nombre') or '').strip()
                    finca_nombre = str(fila.get('finca') or '').strip()

                    if not codigo or not nombre or not finca_nombre:
                        errores.append(f"Fila {idx}: faltan campos requeridos (código, nombre, finca)")
                        continue

                    # Resolver finca_id (búsqueda case-insensitive)
                    cursor.execute("SELECT id FROM finca WHERE LOWER(nombre) = LOWER(?) AND (estado='Activo' OR estado='Activa') LIMIT 1", (finca_nombre,))
                    row_finca = cursor.fetchone()
                    if not row_finca:
                        errores.append(f"Fila {idx}: finca '{finca_nombre}' no encontrada o inactiva")
                        continue
                    finca_id = row_finca[0]

                    try:
                        # Verificar duplicado por código o nombre dentro de la misma finca
                        cursor.execute("SELECT COUNT(*) FROM lote WHERE (codigo = ? OR nombre = ?) AND finca_id = ?", (codigo, nombre, finca_id))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: lote duplicado en finca (código '{codigo}' o nombre '{nombre}')")
                            continue

                        cursor.execute("""
                            INSERT INTO lote (codigo, nombre, descripcion, criterio, estado, finca_id)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            nombre,
                            str(fila.get('descripcion') or '').strip() or None,
                            str(fila.get('criterio') or 'Por Peso').strip(),
                            str(fila.get('estado') or 'Activo').strip(),
                            finca_id
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: lote duplicado")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {e}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_lotes()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")