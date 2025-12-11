import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.importador_excel import parse_excel_to_dicts


class ProveedoresFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_proveedores()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="🛒 Configuración de Proveedores", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Proveedor", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150,)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Nombre *:", width=100).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, width=200,)
        self.entry_nombre.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Teléfono:", width=100).pack(side="left", padx=5)
        self.entry_telefono = ctk.CTkEntry(row2, width=150,)
        self.entry_telefono.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Email:", width=80).pack(side="left", padx=5)
        self.entry_email = ctk.CTkEntry(row2, width=150,)
        self.entry_email.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Dirección:", width=100).pack(side="left", padx=5)
        self.entry_direccion = ctk.CTkEntry(row3, width=300,)
        self.entry_direccion.pack(side="left", padx=5, fill="x", expand=True)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Tipo Servicio:", width=100).pack(side="left", padx=5)
        self.combo_tipo_servicio = ctk.CTkComboBox(row4, 
            values=["Alimentos", "Medicamentos", "Equipos", "Servicios Veterinarios", "Materiales", "Otros"],
            width=200)
        self.combo_tipo_servicio.set("Alimentos")
        self.combo_tipo_servicio.pack(side="left", padx=5)

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
        ctk.CTkLabel(self, text="📋 Proveedores Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "telefono", "email", "tipo_servicio"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 200),
            ("telefono", "Teléfono", 120),
            ("email", "Email", 150),
            ("tipo_servicio", "Tipo Servicio", 150)
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
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_proveedor).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_proveedor, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="� Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="� Actualizar Lista", command=self.cargar_proveedores).pack(side="left", padx=5)

    def guardar_proveedor(self):
        """Guarda un nuevo proveedor"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO proveedor (codigo, nombre, telefono, direccion, email, tipo_servicio, comentario, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    codigo,
                    nombre,
                    self.entry_telefono.get().strip(),
                    self.entry_direccion.get().strip(),
                    self.entry_email.get().strip(),
                    self.combo_tipo_servicio.get(),
                    self.text_comentario.get("1.0", "end-1c").strip(),
                    "Activo"
                ))
                conn.commit()

            messagebox.showinfo("Éxito", "Proveedor guardado correctamente.")
            self.limpiar_formulario()
            self.cargar_proveedores()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un proveedor con ese código.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el proveedor:\n{e}")

    def cargar_proveedores(self):
        """Carga los proveedores en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, telefono, email, tipo_servicio FROM proveedor WHERE estado = 'Activo'")
                
                for fila in cursor.fetchall():
                    self.tabla.insert("", "end", values=fila)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los proveedores:\n{e}")

    def editar_proveedor(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un proveedor para editar.")
            return
        messagebox.showinfo("Editar", "Funcionalidad de edición en desarrollo")

    def eliminar_proveedor(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un proveedor para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el proveedor '{codigo}'?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE proveedor SET estado = 'Inactivo' WHERE codigo = ?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Proveedor eliminado.")
                self.cargar_proveedores()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_direccion.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self.combo_tipo_servicio.set("Alimentos")

    def importar_excel(self):
        """Importar proveedores desde un archivo Excel.
        Se esperan encabezados: codigo,nombre,telefono,email,direccion,tipo_servicio,comentario,estado
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
            messagebox.showerror("Error", "El archivo debe tener las columnas 'codigo' y 'nombre'.")
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
                        errores.append(f"Fila {idx}: faltan campos requeridos (codigo o nombre)")
                        continue

                    try:
                        cursor.execute("SELECT COUNT(*) FROM proveedor WHERE codigo = ? OR nombre = ?", (codigo, nombre))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: el proveedor con código/nombre ya existe")
                            continue

                        cursor.execute("""
                            INSERT INTO proveedor (codigo, nombre, telefono, direccion, email, tipo_servicio, comentario, estado)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            nombre,
                            str(fila.get('telefono') or "").strip() or None,
                            str(fila.get('direccion') or "").strip() or None,
                            str(fila.get('email') or "").strip() or None,
                            str(fila.get('tipo_servicio') or "").strip() or None,
                            str(fila.get('comentario') or "").strip() or None,
                            str(fila.get('estado') or "Activo").strip()
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: proveedor duplicado")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_proveedores()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")