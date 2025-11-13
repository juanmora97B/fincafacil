import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.conexion import db
from modules.utils.importador_excel import parse_excel_to_dicts


class LotesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_lotes()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="📦 Configuración de Lotes", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Lote", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
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
        ctk.CTkLabel(self, text="📋 Lotes Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=20)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "descripcion", "criterio"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 120),
            ("nombre", "Nombre", 150),
            ("descripcion", "Descripción", 200),
            ("criterio", "Criterio", 150)
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_lote).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_lote, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_lotes).pack(side="left", padx=5)
        
    def guardar_lote(self):
        """Guarda un nuevo lote"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lote (codigo, nombre, descripcion, criterio, estado)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    codigo,
                    nombre,
                    self.entry_descripcion.get().strip(),
                    self.combo_criterio.get(),
                    "Activo"
                ))
                conn.commit()

            messagebox.showinfo("Éxito", "Lote guardado correctamente.")
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
                cursor.execute("SELECT codigo, nombre, descripcion, COALESCE(criterio, 'N/A') as criterio FROM lote WHERE estado = 'Activo' OR estado = 'Activa'")
                
                for fila in cursor.fetchall():
                    self.tabla.insert("", "end", values=fila)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los lotes:\n{e}")

    def editar_lote(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un lote para editar.")
            return
        messagebox.showinfo("Editar", "Funcionalidad de edición en desarrollo")

    def eliminar_lote(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un lote para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el lote '{codigo}'?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE lote SET estado = 'Inactivo' WHERE codigo = ?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Lote eliminado.")
                self.cargar_lotes()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.combo_criterio.set("Por Peso")
        
    def importar_excel(self):
        """Importar lotes desde un archivo Excel.
        Se esperan encabezados: codigo,nombre,criterio,estado,descripcion
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
                        errores.append(f"Fila {idx}: faltan campos requeridos (código y nombre)")
                        continue

                    try:
                        # Verificar si el lote ya existe
                        cursor.execute("SELECT COUNT(*) FROM lote WHERE codigo = ? OR nombre = ?", (codigo, nombre))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: el lote con código '{codigo}' o nombre '{nombre}' ya existe")
                            continue

                        # Insertar nuevo lote
                        cursor.execute("""
                            INSERT INTO lote (codigo, nombre, descripcion, criterio, estado)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            nombre,
                            str(fila.get('descripcion') or "").strip() or None,
                            str(fila.get('criterio') or "Por Peso").strip(),
                            str(fila.get('estado') or "Activo").strip()
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: lote duplicado")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_lotes()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")