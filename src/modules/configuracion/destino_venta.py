import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.importador_excel import parse_excel_to_dicts


class DestinoVentaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_destinos()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="🏷️ Configuración de Destinos de Venta", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Destino", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Descripción *:", width=100).pack(side="left", padx=5)
        self.entry_descripcion = ctk.CTkEntry(row1, width=200)
        self.entry_descripcion.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Tipo Destino:", width=100).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(row2, 
            values=["Mercado", "Matadero", "Exportación", "Consumo Interno", "Otros"],
            width=150)
        self.combo_tipo.set("Mercado")
        self.combo_tipo.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="NIT:", width=80).pack(side="left", padx=5)
        self.entry_nit = ctk.CTkEntry(row2, width=150)
        self.entry_nit.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Dirección:", width=100).pack(side="left", padx=5)
        self.entry_direccion = ctk.CTkEntry(row3, width=250)
        self.entry_direccion.pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="Teléfono:", width=80).pack(side="left", padx=5)
        self.entry_telefono = ctk.CTkEntry(row3, width=150)
        self.entry_telefono.pack(side="left", padx=5)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Email:", width=100).pack(side="left", padx=5)
        self.entry_email = ctk.CTkEntry(row4, width=250)
        self.entry_email.pack(side="left", padx=5)

        row5 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row5, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Destino", command=self.guardar_destino, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Destinos de Venta Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "descripcion", "tipo_destino", "nit", "telefono"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("descripcion", "Descripción", 180),
            ("tipo_destino", "Tipo", 100),
            ("nit", "NIT", 120),
            ("telefono", "Teléfono", 100)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)  # type: ignore[arg-type]
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        action_frame.pack(pady=10)

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_destino).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_destino, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_destinos).pack(side="left", padx=5)
        
    def guardar_destino(self):
        """Guarda un nuevo destino de venta o actualiza si está en edición"""
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        
        if not codigo or not descripcion:
            messagebox.showwarning("Atención", "Código y Descripción son campos obligatorios.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                if self.entry_codigo.cget("state") == "disabled":
                    cursor.execute("""
                        UPDATE destino_venta 
                        SET descripcion = ?, tipo_destino = ?, nit = ?, direccion = ?, 
                            telefono = ?, email = ?, comentario = ?
                        WHERE codigo = ?
                    """, (
                        descripcion,
                        self.combo_tipo.get(),
                        self.entry_nit.get().strip() or None,
                        self.entry_direccion.get().strip() or None,
                        self.entry_telefono.get().strip() or None,
                        self.entry_email.get().strip() or None,
                        self.text_comentario.get("1.0", "end-1c").strip() or None,
                        codigo
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO destino_venta 
                        (codigo, descripcion, tipo_destino, nit, direccion, telefono, email, comentario, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        codigo,
                        descripcion,
                        self.combo_tipo.get(),
                        self.entry_nit.get().strip() or None,
                        self.entry_direccion.get().strip() or None,
                        self.entry_telefono.get().strip() or None,
                        self.entry_email.get().strip() or None,
                        self.text_comentario.get("1.0", "end-1c").strip() or None,
                        "Activo"
                    ))
                conn.commit()

            messagebox.showinfo("Éxito", "Destino de venta guardado correctamente." if self.entry_codigo.cget("state") != "disabled" else "Destino de venta actualizado correctamente.")
            self.limpiar_formulario()
            self.cargar_destinos()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un destino con ese código.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el destino:\n{e}")

    def cargar_destinos(self):
        """Carga los destinos de venta en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, descripcion, tipo_destino, nit, telefono 
                    FROM destino_venta 
                    WHERE estado = 'Activo'
                """)
                
                for fila in cursor.fetchall():
                    valores = tuple(str(v) if v is not None else "" for v in fila)
                    self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los destinos:\n{e}")

    def editar_destino(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un destino para editar.")
            return
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, descripcion, tipo_destino, nit, direccion, telefono, email, comentario 
                    FROM destino_venta WHERE codigo = ?
                """, (codigo,))
                row = cursor.fetchone()
                if not row:
                    messagebox.showerror("Error", "No se encontró el destino")
                    return
                self.entry_codigo.delete(0, "end")
                self.entry_codigo.insert(0, str(row[0]))
                self.entry_codigo.configure(state="disabled")
                self.entry_descripcion.delete(0, "end")
                self.entry_descripcion.insert(0, str(row[1]))
                if row[2]:
                    self.combo_tipo.set(str(row[2]))
                self.entry_nit.delete(0, "end")
                if row[3]:
                    self.entry_nit.insert(0, str(row[3]))
                self.entry_direccion.delete(0, "end")
                if row[4]:
                    self.entry_direccion.insert(0, str(row[4]))
                self.entry_telefono.delete(0, "end")
                if row[5]:
                    self.entry_telefono.insert(0, str(row[5]))
                self.entry_email.delete(0, "end")
                if row[6]:
                    self.entry_email.insert(0, str(row[6]))
                self.text_comentario.delete("1.0", "end")
                if row[7]:
                    self.text_comentario.insert("1.0", str(row[7]))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el destino:\n{e}")

    def eliminar_destino(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un destino para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el destino '{codigo}'?\n\nEsta acción no se puede deshacer."):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM destino_venta WHERE codigo = ?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Destino eliminado.")
                self.cargar_destinos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.entry_nit.delete(0, "end")
        self.entry_direccion.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self.combo_tipo.set("Mercado")
        
    def importar_excel(self):
        """Importar destinos de venta desde un archivo Excel.
        Se esperan encabezados: codigo,descripcion,tipo_destino,estado,comentario
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

        # Validar que existan columnas requeridas (aceptar variantes)
        primera = filas[0]
        # Compatibilidad: 'nombre' -> 'descripcion', 'tipo' -> 'tipo_destino'
        variantes_codigo = ['codigo', 'codigos', 'código']
        variantes_descripcion = ['descripcion', 'descripción', 'nombre']
        variantes_tipo = ['tipo_destino', 'tipo']
        
        def resolver_col(registro, variantes, destino):
            if destino in registro:
                return
            for v in variantes:
                if v in registro:
                    registro[destino] = registro.get(v)
                    return
        
        # Adaptar todas las filas
        variantes_direccion = ['direccion', 'dirección']
        variantes_telefono = ['telefono', 'teléfono']
        
        for fila in filas:
            resolver_col(fila, variantes_codigo, 'codigo')
            resolver_col(fila, variantes_descripcion, 'descripcion')
            resolver_col(fila, variantes_tipo, 'tipo_destino')
            resolver_col(fila, variantes_direccion, 'direccion')
            resolver_col(fila, variantes_telefono, 'telefono')
        
        primera = filas[0]
        if 'codigo' not in primera or 'descripcion' not in primera:
            messagebox.showerror(
                "Error",
                "El archivo debe contener encabezados equivalentes a: codigo, descripcion.\n"
                "Variantes aceptadas: codigos/código, nombre, tipo/tipo_destino."
            )
            return

        importados = 0
        errores = []

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                for idx, fila in enumerate(filas, start=2):
                    codigo = str(fila.get('codigo') or "").strip()
                    descripcion = str(fila.get('descripcion') or "").strip()

                    if not codigo or not descripcion:
                        errores.append(f"Fila {idx}: faltan campos requeridos (código y descripción)")
                        continue

                    try:
                        # Verificar si el destino ya existe
                        cursor.execute("SELECT COUNT(*) FROM destino_venta WHERE codigo = ?", (codigo,))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: el destino con código '{codigo}' ya existe")
                            continue

                        # Insertar nuevo destino
                        cursor.execute("""
                            INSERT INTO destino_venta 
                            (codigo, descripcion, tipo_destino, nit, direccion, telefono, email, comentario, estado)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            descripcion,
                            str(fila.get('tipo_destino') or fila.get('tipo') or "Mercado").strip(),
                            str(fila.get('nit') or "").strip() or None,
                            str(fila.get('direccion') or fila.get('dirección') or "").strip() or None,
                            str(fila.get('telefono') or fila.get('teléfono') or "").strip() or None,
                            str(fila.get('email') or "").strip() or None,
                            str(fila.get('comentario') or "").strip() or None,
                            str(fila.get('estado') or "Activo").strip()
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: destino duplicado")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_destinos()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")
        self.text_comentario.delete("1.0", "end")
        self.combo_tipo.set("Mercado")