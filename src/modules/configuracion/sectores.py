import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.importador_excel import parse_excel_to_dicts
from modules.utils.constants_ui import PLACEHOLDERS, truncate
from modules.utils.db_logging import safe_execute


class SectoresFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_fincas_combobox()
        self.cargar_sectores()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        titulo = ctk.CTkLabel(scroll_container, text="🗺️ Configuración de Sectores", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Sector", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Finca
        row0 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row0.pack(fill="x", pady=5)
        ctk.CTkLabel(row0, text="Finca *:", width=100).pack(side="left", padx=5)
        self.combo_finca = ctk.CTkComboBox(row0, width=300)
        self.combo_finca.set(PLACEHOLDERS.get("finca", "Seleccione una finca"))
        self.combo_finca.pack(side="left", padx=5, fill="x", expand=True)

        # Código y Nombre
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Nombre *:", width=100).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, width=150)
        self.entry_nombre.pack(side="left", padx=5)

        # Comentario
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row2, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones formulario
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        ctk.CTkButton(btn_frame, text="💾 Guardar Sector", command=self.guardar_sector,
                      fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Sectores Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20, 5), padx=4)

        # Tabla de sectores
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)
        self.tabla = ttk.Treeview(table_frame, columns=("id", "finca", "codigo", "nombre", "comentario"),
                                  show="headings", displaycolumns=("finca", "codigo", "nombre", "comentario"), height=12)
        column_config = [
            ("id", "ID", 50),
            ("finca", "Finca", 150),
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("comentario", "Comentario", 250)
        ]
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")
        self.tabla.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Búsqueda rápida
        filtro_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        filtro_frame.pack(fill="x", padx=4)
        ctk.CTkLabel(filtro_frame, text="🔍 Buscar:").pack(side="left", padx=5)
        self.entry_buscar = ctk.CTkEntry(filtro_frame, placeholder_text=PLACEHOLDERS.get("busqueda_general", "Buscar"))
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.filtrar_tabla())

        # Botones de acción
        action_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        action_frame.pack(pady=10)
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_sector).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_sector,
                      fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_sectores).pack(side="left", padx=5)
        
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
                    self.combo_finca.set(PLACEHOLDERS.get("finca", "Seleccione una finca"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")
        
    def guardar_sector(self):
        """Guarda un nuevo sector"""
        codigo = truncate(self.entry_codigo.get().strip(), "codigo_sector")
        nombre = truncate(self.entry_nombre.get().strip(), "nombre_sector")
        finca_nombre = self.combo_finca.get().strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return
            
        if not finca_nombre or finca_nombre == PLACEHOLDERS.get("finca", "Seleccione una finca"):
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
                safe_execute(cursor, """
                    INSERT INTO sector (codigo, nombre, comentario, estado, finca_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    codigo,
                    nombre,
                    self.text_comentario.get("1.0", "end-1c").strip(),
                    "Activo",
                    finca_id
                ))
                conn.commit()

            messagebox.showinfo("Éxito", "Sector guardado correctamente.")
            self.limpiar_formulario()
            self.cargar_sectores()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un sector con ese código.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el sector:\n{e}")

    def cargar_sectores(self):
        """Carga los sectores en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                safe_execute(cursor, """
                    SELECT s.id, f.nombre as finca, s.codigo, s.nombre, 
                           COALESCE(s.comentario, s.descripcion, '') as comentario 
                    FROM sector s
                    LEFT JOIN finca f ON s.finca_id = f.id
                    WHERE s.estado = 'Activo' OR s.estado = 'Activa'
                """)
                
                self._sectores_data = []
                for fila in cursor.fetchall():
                    valores = (
                        str(fila[0]) if fila[0] is not None else "",
                        str(fila[1]) if fila[1] is not None else "Sin Finca",
                        str(fila[2]) if fila[2] is not None else "",
                        str(fila[3]) if fila[3] is not None else "",
                        str(fila[4]) if fila[4] is not None else ""
                    )
                    self._sectores_data.append(valores)
                for valores in self._sectores_data:
                    self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los sectores:\n{e}")

    def editar_sector(self):
        """Edita el sector seleccionado"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un sector para editar.")
            return

        # Obtener ID del sector seleccionado (ahora está en el índice 0 de values)
        sector_id = self.tabla.item(seleccionado[0])["values"][0]

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                safe_execute(cursor, "SELECT * FROM sector WHERE id = ?", (sector_id,))
                sector = cursor.fetchone()

                if not sector:
                    messagebox.showerror("Error", "No se encontró el sector.")
                    return

                # Crear ventana de edición con scroll
                ventana_edicion = ctk.CTkToplevel(self)
                ventana_edicion.title("Editar Sector")
                ventana_edicion.geometry("550x600")  # Aumentado tamaño para incluir finca
                ventana_edicion.transient(self)
                ventana_edicion.grab_set()

                # Frame principal scrollable
                main_frame = ctk.CTkScrollableFrame(ventana_edicion)
                # Compactar ancho (20→4)
                main_frame.pack(padx=4, pady=20, fill="both", expand=True)

                # Título
                ctk.CTkLabel(main_frame, text="✏️ Editar Sector", 
                            font=("Segoe UI", 18, "bold")).pack(pady=10)

                # Cargar fincas para el combo
                safe_execute(cursor, "SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
                fincas_rows = cursor.fetchall()
                finca_map_edit = {str(r[1]).strip(): int(r[0]) for r in fincas_rows if r[1] is not None}
                fincas_nombres = list(finca_map_edit.keys())
                
                # Campos del formulario
                ctk.CTkLabel(main_frame, text="Finca *:").pack(anchor="w", padx=5, pady=2)
                combo_finca_edit = ctk.CTkComboBox(main_frame, width=300, values=fincas_nombres)
                # Obtener finca actual del sector (índice 5 según estructura típica)
                finca_id_actual = sector[5] if len(sector) > 5 else None
                if finca_id_actual:
                    safe_execute(cursor, "SELECT nombre FROM finca WHERE id = ?", (finca_id_actual,))
                    finca_actual = cursor.fetchone()
                    if finca_actual:
                        combo_finca_edit.set(finca_actual[0])
                    elif fincas_nombres:
                        combo_finca_edit.set(fincas_nombres[0])
                elif fincas_nombres:
                    combo_finca_edit.set(fincas_nombres[0])
                combo_finca_edit.pack(anchor="w", padx=5, pady=2)
                
                ctk.CTkLabel(main_frame, text="Código:").pack(anchor="w", padx=5, pady=2)
                entry_codigo = ctk.CTkEntry(main_frame, width=300)
                entry_codigo.insert(0, sector[1])  # codigo
                entry_codigo.configure(state="disabled")
                entry_codigo.pack(anchor="w", padx=5, pady=2)

                ctk.CTkLabel(main_frame, text="Nombre *:").pack(anchor="w", padx=5, pady=2)
                entry_nombre = ctk.CTkEntry(main_frame, width=300)
                entry_nombre.insert(0, sector[2] if sector[2] else "")  # nombre
                entry_nombre.pack(anchor="w", padx=5, pady=2)

                ctk.CTkLabel(main_frame, text="Comentario:").pack(anchor="w", padx=5, pady=2)
                text_comentario = ctk.CTkTextbox(main_frame, width=300, height=100)
                # comentario puede estar en índice 3 o descripcion en otro índice
                comentario_val = ""
                if len(sector) > 3 and sector[3]:
                    comentario_val = sector[3]
                elif len(sector) > 4 and sector[4]:  # por si hay descripcion
                    comentario_val = sector[4]
                text_comentario.insert("1.0", comentario_val)
                text_comentario.pack(anchor="w", padx=5, pady=2)

                def guardar_cambios():
                    """Guarda los cambios del sector"""
                    nombre = entry_nombre.get().strip()
                    finca_nombre_edit = combo_finca_edit.get().strip()
                    
                    if not nombre:
                        messagebox.showwarning("Atención", "El nombre es obligatorio.")
                        return
                    
                    if not finca_nombre_edit or finca_nombre_edit == PLACEHOLDERS.get("finca", "Seleccione una finca"):
                        messagebox.showwarning("Atención", "Debe seleccionar una finca.")
                        return
                    
                    finca_id_edit = finca_map_edit.get(finca_nombre_edit)
                    if not finca_id_edit:
                        messagebox.showwarning("Atención", "Finca no válida.")
                        return

                    try:
                        # Crear nueva conexión para esta operación
                        with db.get_connection() as conn_update:
                            cursor_update = conn_update.cursor()
                            safe_execute(cursor_update, """
                                UPDATE sector 
                                SET nombre = ?, comentario = ?, finca_id = ?
                                WHERE id = ?
                            """, (
                                nombre,
                                text_comentario.get("1.0", "end-1c").strip() or None,
                                finca_id_edit,
                                sector_id
                            ))
                            conn_update.commit()
                        
                        messagebox.showinfo("Éxito", "Sector actualizado correctamente.")
                        ventana_edicion.destroy()
                        self.cargar_sectores()
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo actualizar el sector:\n{e}")

                # Botones
                btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                btn_frame.pack(pady=20)
                
                ctk.CTkButton(btn_frame, text="💾 Guardar Cambios", command=guardar_cambios,
                            fg_color="green", hover_color="#006400").pack(side="left", padx=5)
                ctk.CTkButton(btn_frame, text="❌ Cancelar", command=ventana_edicion.destroy,
                            fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el sector para editar:\n{e}")

    def eliminar_sector(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un sector para eliminar.")
            return
        
        # Obtener ID del sector seleccionado (índice 0 de values)
        sector_id = self.tabla.item(seleccionado[0])["values"][0]
        sector_codigo = self.tabla.item(seleccionado[0])["values"][2]  # codigo está en índice 2
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el sector '{sector_codigo}'?\n\nEsta acción no se puede deshacer."):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    # Eliminación física directa
                    safe_execute(cursor, "DELETE FROM sector WHERE id = ?", (sector_id,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Sector eliminado correctamente.")
                self.cargar_sectores()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        if hasattr(self, 'combo_finca') and hasattr(self, '_finca_map'):
            nombres = list(self._finca_map.keys())
            if nombres:
                self.combo_finca.set(nombres[0])
            else:
                self.combo_finca.set(PLACEHOLDERS.get("finca", "Seleccione una finca"))
        
    def importar_excel(self):
        """Importar sectores desde un archivo Excel usando el importador con soporte de finca."""
        ruta = filedialog.askopenfilename(title="Seleccionar archivo Excel", filetypes=[("Excel files", "*.xlsx *.xls"), ("Todos los archivos", "*.*")])
        if not ruta:
            return

        # Usar el importador que procesa el campo finca
        from modules.utils.importador_excel import importar_sector_desde_excel
        filas, errores_parse = importar_sector_desde_excel(ruta)
        
        if errores_parse:
            messagebox.showerror("Error", "\n".join(errores_parse))
            return

        if not filas:
            messagebox.showinfo("Importar", "No se encontraron filas para importar.")
            return

        importados = 0
        errores = []

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                for idx, fila in enumerate(filas, start=2):
                    codigo = str(fila.get('codigo') or "").strip()
                    nombre = str(fila.get('nombre') or "").strip()

                    if not codigo or not nombre:
                        errores.append(f"Fila {idx}: faltan campos requeridos (código y nombre)")
                        continue

                    try:
                        # Verificar si el sector ya existe
                        cursor.execute("SELECT COUNT(*) FROM sector WHERE codigo = ? OR nombre = ?", (codigo, nombre))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: el sector con código '{codigo}' o nombre '{nombre}' ya existe")
                            continue

                        # Insertar nuevo sector con finca_id
                        cursor.execute("""
                            INSERT INTO sector (codigo, nombre, finca_id, estado, descripcion, comentario)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            nombre,
                            fila.get('finca_id'),  # Ya viene procesado por importar_sector_desde_excel
                            str(fila.get('estado') or "Activo").strip(),
                            str(fila.get('descripcion') or "").strip() or None,
                            fila.get('comentario')
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: sector duplicado")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_sectores()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")

    def filtrar_tabla(self):
        """Filtra la tabla según texto en entrada de búsqueda sobre finca, código, nombre y comentario."""
        if not hasattr(self, '_sectores_data'):
            return
        termino = (self.entry_buscar.get() or '').strip().lower()
        # Limpiar tabla actual
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        if not termino:
            for valores in self._sectores_data:
                self.tabla.insert('', 'end', values=valores)
            return
        for valores in self._sectores_data:
            _, finca, codigo, nombre, comentario = valores
            texto_busqueda = ' '.join([finca.lower(), codigo.lower(), nombre.lower(), comentario.lower()])
            if termino in texto_busqueda:
                self.tabla.insert('', 'end', values=valores)