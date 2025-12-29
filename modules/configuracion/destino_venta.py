import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
from typing import Optional
import sys
import os
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.utils.importador_excel import parse_excel_to_dicts
from src.database import get_connection


class DestinoVentaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._destino_editando_codigo: Optional[str] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_destinos_venta()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="🏪 Configuración de Destinos de Venta", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Destino de Venta", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

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
        ctk.CTkLabel(row2, text="NIT:", width=100).pack(side="left", padx=5)
        self.entry_nit = ctk.CTkEntry(row2, width=150)
        self.entry_nit.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Dirección:", width=100).pack(side="left", padx=5)
        self.entry_direccion = ctk.CTkEntry(row2, width=200)
        self.entry_direccion.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Teléfono:", width=100).pack(side="left", padx=5)
        self.entry_telefono = ctk.CTkEntry(row3, width=150)
        self.entry_telefono.pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="Email:", width=100).pack(side="left", padx=5)
        self.entry_email = ctk.CTkEntry(row3, width=200)
        self.entry_email.pack(side="left", padx=5)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row4, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Destino", command=self.guardar_destino_venta, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", height=40, command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Destinos de Venta Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "nit", "direccion", "telefono", "email"), show="headings", height=18)
        
        column_config = [
            ("codigo", "Código", 120),
            ("nombre", "Nombre", 200),
            ("nit", "NIT", 120),
            ("direccion", "Dirección", 180),
            ("telefono", "Teléfono", 120),
            ("email", "Email", 150)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        action_frame.pack(pady=10)

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", height=40, command=self.editar_destino_venta).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_destino_venta, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", height=40, command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", height=40, command=self.cargar_destinos_venta).pack(side="left", padx=5)

        # Menú contextual (clic derecho)
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_destino_venta)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_destino_venta)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_destinos_venta)
        
        # Vincular eventos de la tabla
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_destino_venta())

    def mostrar_menu_contextual(self, event):
        try:
            row_id = self.tabla.identify_row(event.y)
            if row_id:
                self.tabla.selection_set(row_id)
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
        
    def guardar_destino_venta(self):
        """Guarda un nuevo destino de venta o actualiza si está en modo edición"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return

        try:
            nit = self.entry_nit.get().strip()
            direccion = self.entry_direccion.get().strip()
            telefono = self.entry_telefono.get().strip()
            email = self.entry_email.get().strip()
            comentario = self.text_comentario.get("1.0", "end-1c").strip()
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                if self._destino_editando_codigo:
                    # Modo edición
                    cursor.execute("""
                        UPDATE destino_venta 
                        SET nombre=?, nit=?, direccion=?, telefono=?, email=?, comentario=?, estado='Activo'
                        WHERE codigo=? AND estado IN ('Activo', 'Inactivo')
                    """, (nombre, nit, direccion, telefono, email, comentario, self._destino_editando_codigo))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Destino de venta actualizado correctamente.")
                else:
                    # Modo creación
                    cursor.execute("""
                        INSERT INTO destino_venta (codigo, nombre, nit, direccion, telefono, email, comentario, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'Activo')
                    """, (codigo, nombre, nit, direccion, telefono, email, comentario))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Destino de venta guardado correctamente.")
            
            self.limpiar_formulario()
            self.cargar_destinos_venta()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El código de destino ya existe.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el destino:\n{e}")

    def cargar_destinos_venta(self):
        """Carga los destinos de venta en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, nit, direccion, telefono, email FROM destino_venta WHERE estado='Activo'")
                
                for row in cursor.fetchall():
                    self.tabla.insert("", "end", values=row)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los destinos:\n{e}")

    def editar_destino_venta(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un destino para editar.")
            return
        
        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = valores[0]
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, nit, direccion, telefono, email, comentario FROM destino_venta WHERE codigo=?", (codigo,))
                destino = cursor.fetchone()
            
            if not destino:
                messagebox.showerror("Error", "No se pudo obtener el destino.")
                return
            
            # Cargar en formulario (inline editing)
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, destino[0])
            self.entry_codigo.configure(state="disabled")
            
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, destino[1])
            
            self.entry_nit.delete(0, "end")
            self.entry_nit.insert(0, destino[2] or "")
            
            self.entry_direccion.delete(0, "end")
            self.entry_direccion.insert(0, destino[3] or "")
            
            self.entry_telefono.delete(0, "end")
            self.entry_telefono.insert(0, destino[4] or "")
            
            self.entry_email.delete(0, "end")
            self.entry_email.insert(0, destino[5] or "")
            
            self.text_comentario.delete("1.0", "end")
            if destino[6]:
                self.text_comentario.insert("1.0", destino[6])
            
            # Tracking para saber que estamos editando
            self._destino_editando_codigo = codigo
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el destino:\n{e}")

    def eliminar_destino_venta(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un destino para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Marcar como inactivo el destino '{codigo}'?\n\nPodrá reactivarlo desde la base de datos."):
            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE destino_venta SET estado='Inactivo' WHERE codigo=?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Destino marcado como inactivo.")
                self.cargar_destinos_venta()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_nit.delete(0, "end")
        self.entry_direccion.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self._destino_editando_codigo = None
        
    def importar_excel(self):
        """Importar destinos de venta desde un archivo Excel.
        Se esperan encabezados: codigo,nombre,nit,direccion,telefono,email,comentario
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
        
        # Compatibilidad con variantes
        variantes_codigo = ['codigo', 'codigos', 'código']
        variantes_nombre = ['nombre', 'nomb', 'razon_social', 'razón_social']

        def resolver_col(registro, variantes, destino):
            if destino in registro:
                return
            for v in variantes:
                if v in registro:
                    registro[destino] = registro.get(v)
                    return

        # Adaptar todas las filas
        for fila in filas:
            resolver_col(fila, variantes_codigo, 'codigo')
            resolver_col(fila, variantes_nombre, 'nombre')

        primera = filas[0]
        if 'codigo' not in primera or 'nombre' not in primera:
            messagebox.showerror(
                "Error",
                "El archivo debe contener encabezados equivalentes a: codigo, nombre.\n"
                "Variantes aceptadas: codigos/código, nomb/razon_social.\n"
                "Los campos nit, dirección, teléfono, email, comentario son opcionales."
            )
            return

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip()
            nombre = str(fila.get('nombre') or "").strip()
            nit = str(fila.get('nit') or "").strip()
            direccion = str(fila.get('direccion') or fila.get('dirección') or "").strip()
            telefono = str(fila.get('telefono') or fila.get('teléfono') or "").strip()
            email = str(fila.get('email') or "").strip()
            comentario = str(fila.get('comentario') or "").strip()

            if not codigo or not nombre:
                errores.append(f"Fila {idx}: faltan campos requeridos (código, nombre)")
                continue

            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO destino_venta (codigo, nombre, nit, direccion, telefono, email, comentario, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'Activo')
                    """, (codigo, nombre, nit, direccion, telefono, email, comentario))
                    conn.commit()
                importados += 1
            except sqlite3.IntegrityError:
                errores.append(f"Fila {idx}: el código '{codigo}' ya existe")
            except Exception as e:
                errores.append(f"Fila {idx}: {str(e)}")

        mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
        if errores:
            mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
        messagebox.showinfo("Importación", mensaje)
        self.cargar_destinos_venta()
