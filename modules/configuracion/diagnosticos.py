import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.conexion import db
from modules.utils.importador_excel import parse_excel_to_dicts


class DiagnosticosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_diagnosticos()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="🏥 Configuración de Diagnósticos Veterinarios", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Diagnóstico", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150,)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Descripción *:", width=100).pack(side="left", padx=5)
        self.entry_descripcion = ctk.CTkEntry(row1, width=150,)
        self.entry_descripcion.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Tipo Diagnóstico:", width=120).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(row2, values=["Reproductivo", "No Reproductivo"], width=200)
        self.combo_tipo.set("Reproductivo")
        self.combo_tipo.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row3, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Diagnóstico", command=self.guardar_diagnostico, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(self, text="📋 Diagnósticos Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=20)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "descripcion", "tipo", "comentario"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("descripcion", "Descripción", 200),
            ("tipo", "Tipo", 120),
            ("comentario", "Comentario", 250)
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_diagnostico).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_diagnostico, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_diagnosticos).pack(side="left", padx=5)
        
    def guardar_diagnostico(self):
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        
        if not codigo or not descripcion:
            messagebox.showwarning("Atención", "Código y Descripción son campos obligatorios.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO diagnostico_veterinario (codigo, descripcion, tipo_diagnostico, comentario, estado)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    codigo,
                    descripcion,
                    self.combo_tipo.get(),
                    self.text_comentario.get("1.0", "end-1c").strip(),
                    "Activo"
                ))
                conn.commit()

            messagebox.showinfo("Éxito", "Diagnóstico guardado correctamente.")
            self.limpiar_formulario()
            self.cargar_diagnosticos()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un diagnóstico con ese código.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el diagnóstico:\n{e}")

    def cargar_diagnosticos(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, descripcion, tipo_diagnostico, comentario FROM diagnostico_veterinario WHERE estado = 'Activo'")
                
                for fila in cursor.fetchall():
                    self.tabla.insert("", "end", values=fila)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los diagnósticos:\n{e}")

    def editar_diagnostico(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un diagnóstico para editar.")
            return
        messagebox.showinfo("Editar", "Funcionalidad de edición en desarrollo")

    def eliminar_diagnostico(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un diagnóstico para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el diagnóstico '{codigo}'?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE diagnostico_veterinario SET estado = 'Inactivo' WHERE codigo = ?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Diagnóstico eliminado.")
                self.cargar_diagnosticos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        
    def importar_excel(self):
        """Importar diagnósticos veterinarios desde un archivo Excel.
        Se esperan encabezados: codigo,descripcion,tipo_diagnostico,estado,comentario
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
        if 'codigo' not in primera or 'descripcion' not in primera:
            messagebox.showerror("Error", "El archivo debe tener las columnas 'codigo' y 'descripcion'.")
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
                        # Verificar si el diagnóstico ya existe
                        cursor.execute("SELECT COUNT(*) FROM diagnostico_veterinario WHERE codigo = ?", (codigo,))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: el diagnóstico con código '{codigo}' ya existe")
                            continue

                        # Insertar nuevo diagnóstico
                        cursor.execute("""
                            INSERT INTO diagnostico_veterinario (codigo, descripcion, tipo_diagnostico, comentario, estado)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            descripcion,
                            str(fila.get('tipo_diagnostico') or "General").strip(),
                            str(fila.get('comentario') or "").strip() or None,
                            str(fila.get('estado') or "Activo").strip()
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: diagnóstico duplicado")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_diagnosticos()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")
        self.text_comentario.delete("1.0", "end")
        self.combo_tipo.set("Reproductivo")