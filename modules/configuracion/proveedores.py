import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
from typing import Optional
import sys
import os
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.utils.importador_excel import parse_excel_to_dicts
from src.database import get_connection


class ProveedoresFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._proveedor_editando_codigo: Optional[str] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_proveedores()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="🤝 Configuración de Proveedores", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Proveedor", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

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
        ctk.CTkLabel(row2, text="Tipo de Servicio *:", width=100).pack(side="left", padx=5)
        self.combo_tipo_servicio = ctk.CTkComboBox(row2, 
            values=["Alimentación", "Medicinas", "Equipo", "Servicios Profesionales", "Otros"],
            width=150)
        self.combo_tipo_servicio.set("Alimentación")
        self.combo_tipo_servicio.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Contacto:", width=100).pack(side="left", padx=5)
        self.entry_contacto = ctk.CTkEntry(row3, width=150)
        self.entry_contacto.pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="Teléfono:", width=100).pack(side="left", padx=5)
        self.entry_telefono = ctk.CTkEntry(row3, width=200)
        self.entry_telefono.pack(side="left", padx=5)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Email:", width=100).pack(side="left", padx=5)
        self.entry_email = ctk.CTkEntry(row4, width=200)
        self.entry_email.pack(side="left", padx=5)

        row5 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row5, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Proveedor", command=self.guardar_proveedor, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Proveedores Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "tipo_servicio", "contacto", "telefono", "email"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 180),
            ("tipo_servicio", "Tipo de Servicio", 150),
            ("contacto", "Contacto", 150),
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_proveedor).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_proveedor, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_proveedores).pack(side="left", padx=5)

        # Menú contextual (clic derecho)
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_proveedor)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_proveedor)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_proveedores)
        
        # Vincular eventos de la tabla
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_proveedor())

    def mostrar_menu_contextual(self, event):
        try:
            row_id = self.tabla.identify_row(event.y)
            if row_id:
                self.tabla.selection_set(row_id)
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
        
    def guardar_proveedor(self):
        """Guarda un nuevo proveedor o actualiza si está en modo edición"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        tipo_servicio = self.combo_tipo_servicio.get().strip()
        
        if not codigo or not nombre or not tipo_servicio:
            messagebox.showwarning("Atención", "Código, Nombre y Tipo de Servicio son campos obligatorios.")
            return

        try:
            contacto = self.entry_contacto.get().strip()
            telefono = self.entry_telefono.get().strip()
            email = self.entry_email.get().strip()
            comentario = self.text_comentario.get("1.0", "end-1c").strip()
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                if self._proveedor_editando_codigo:
                    # Modo edición
                    cursor.execute("""
                        UPDATE proveedor 
                        SET nombre=?, tipo_servicio=?, contacto=?, telefono=?, email=?, comentario=?, estado='Activo'
                        WHERE codigo=? AND estado IN ('Activo', 'Inactivo')
                    """, (nombre, tipo_servicio, contacto, telefono, email, comentario, self._proveedor_editando_codigo))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Proveedor actualizado correctamente.")
                else:
                    # Modo creación
                    cursor.execute("""
                        INSERT INTO proveedor (codigo, nombre, tipo_servicio, contacto, telefono, email, comentario, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'Activo')
                    """, (codigo, nombre, tipo_servicio, contacto, telefono, email, comentario))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Proveedor guardado correctamente.")
            
            self.limpiar_formulario()
            self.cargar_proveedores()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El código de proveedor ya existe.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el proveedor:\n{e}")

    def cargar_proveedores(self):
        """Carga los proveedores en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, tipo_servicio, contacto, telefono, email FROM proveedor WHERE estado='Activo'")
                
                for row in cursor.fetchall():
                    self.tabla.insert("", "end", values=row)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los proveedores:\n{e}")

    def editar_proveedor(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un proveedor para editar.")
            return
        
        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = valores[0]
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, tipo_servicio, contacto, telefono, email, comentario FROM proveedor WHERE codigo=?", (codigo,))
                proveedor = cursor.fetchone()
            
            if not proveedor:
                messagebox.showerror("Error", "No se pudo obtener el proveedor.")
                return
            
            # Cargar en formulario (inline editing)
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, proveedor[0])
            self.entry_codigo.configure(state="disabled")
            
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, proveedor[1])
            
            self.combo_tipo_servicio.set(proveedor[2] or "Alimentación")
            
            self.entry_contacto.delete(0, "end")
            self.entry_contacto.insert(0, proveedor[3] or "")
            
            self.entry_telefono.delete(0, "end")
            self.entry_telefono.insert(0, proveedor[4] or "")
            
            self.entry_email.delete(0, "end")
            self.entry_email.insert(0, proveedor[5] or "")
            
            self.text_comentario.delete("1.0", "end")
            if proveedor[6]:
                self.text_comentario.insert("1.0", proveedor[6])
            
            # Tracking para saber que estamos editando
            self._proveedor_editando_codigo = codigo
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el proveedor:\n{e}")

    def eliminar_proveedor(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un proveedor para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Marcar como inactivo el proveedor '{codigo}'?\n\nPodrá reactivarlo desde la base de datos."):
            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE proveedor SET estado='Inactivo' WHERE codigo=?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Proveedor marcado como inactivo.")
                self.cargar_proveedores()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_contacto.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self.combo_tipo_servicio.set("Alimentación")
        self._proveedor_editando_codigo = None
        
    def importar_excel(self):
        """Importar proveedores desde un archivo Excel."""
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

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip()
            nombre = str(fila.get('nombre') or "").strip()
            tipo_servicio = str(fila.get('tipo_servicio') or "Alimentación").strip()

            if not codigo or not nombre:
                errores.append(f"Fila {idx}: faltan campos requeridos (código, nombre)")
                continue

            try:
                contacto = str(fila.get('contacto') or "").strip()
                telefono = str(fila.get('telefono') or "").strip()
                email = str(fila.get('email') or "").strip()
                comentario = str(fila.get('comentario') or "").strip()
                
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO proveedor (codigo, nombre, tipo_servicio, contacto, telefono, email, comentario, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'Activo')
                    """, (codigo, nombre, tipo_servicio, contacto, telefono, email, comentario))
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
        self.cargar_proveedores()
