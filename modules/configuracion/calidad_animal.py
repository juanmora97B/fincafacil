import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
import sqlite3
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.importador_excel import parse_excel_to_dicts


class CalidadAnimalFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_calidades()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="⭐ Configuración de Calidad Animal", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container)
        form_frame.pack(pady=10, padx=4, fill="x")

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame)
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Descripción *:", width=100).pack(side="left", padx=5)
        self.entry_descripcion = ctk.CTkEntry(row1)
        self.entry_descripcion.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame)
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row2, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar", command=self.guardar_calidad,
                     fg_color="green", hover_color="#006400", height=36).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario, height=36).pack(side="left", padx=5)

        # Tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(padx=4, pady=10, fill="both", expand=True)

        # Crear el treeview
        columns = ("codigo", "descripcion", "comentario")
        self.tabla = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Configurar las columnas
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("descripcion", text="Descripción")
        self.tabla.heading("comentario", text="Comentario")

        self.tabla.column("codigo", width=100)
        self.tabla.column("descripcion", width=200)
        self.tabla.column("comentario", width=300)

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Empacar todo
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        action_frame.pack(pady=10)
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_calidad, height=36).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_calidad, 
                     fg_color="red", hover_color="#8B0000", height=36).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel, height=36).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_calidades, height=36).pack(side="left", padx=5)

        # Agregar menú contextual como alternativa
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="Editar", command=self.editar_calidad)
        self.menu_contextual.add_command(label="Eliminar", command=self.eliminar_calidad)
        
        # Vincular el menú contextual
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_calidad())

    def guardar_calidad(self):
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        comentario = self.text_comentario.get("1.0", "end-1c").strip()
        
        if not codigo or not descripcion:
            messagebox.showerror("Error", "Los campos Código y Descripción son obligatorios")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                if self.entry_codigo.cget("state") == "disabled":
                    cursor.execute("""
                        UPDATE calidad_animal 
                        SET descripcion = ?, comentario = ?
                        WHERE codigo = ?
                    """, (descripcion, comentario, codigo))
                    messagebox.showinfo("Éxito", "Calidad animal actualizada")
                else:
                    cursor.execute("""
                        INSERT INTO calidad_animal (codigo, descripcion, comentario)
                        VALUES (?, ?, ?)
                    """, (codigo, descripcion, comentario))
                    messagebox.showinfo("Éxito", "Calidad animal guardada")
                
                conn.commit()  # Confirmar cambios en la base de datos
                
            self.limpiar_formulario()
            self.cargar_calidades()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe una calidad con ese código")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def cargar_calidades(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, descripcion, comentario FROM calidad_animal")
                for calidad in cursor.fetchall():
                    # Convertir explícitamente a strings
                    valores = (
                        str(calidad[0]) if calidad[0] is not None else "",
                        str(calidad[1]) if calidad[1] is not None else "",
                        str(calidad[2]) if calidad[2] is not None else ""
                    )
                    self.tabla.insert("", "end", values=valores)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")

    def editar_calidad(self):
        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una calidad para editar")
            return

        valores = self.tabla.item(selected[0])["values"]
        
        self.entry_codigo.delete(0, "end")
        self.entry_codigo.insert(0, valores[0])
        self.entry_codigo.configure(state="disabled")
        
        self.entry_descripcion.delete(0, "end")
        self.entry_descripcion.insert(0, valores[1])
        
        self.text_comentario.delete("1.0", "end")
        if valores[2]:
            self.text_comentario.insert("1.0", valores[2])

    def eliminar_calidad(self):
        selected = self.tabla.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una calidad para eliminar")
            return

        codigo = self.tabla.item(selected[0])["values"][0]
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la calidad '{codigo}'?\n\nEsta acción no se puede deshacer."):
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM calidad_animal WHERE codigo = ?", (codigo,))
                conn.commit()  # Agregar commit
            messagebox.showinfo("Éxito", "Calidad eliminada correctamente.")
            self.cargar_calidades()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.text_comentario.delete("1.0", "end")

    def importar_excel(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar Excel",
            filetypes=[("Excel", "*.xlsx;*.xls")]
        )
        if not file_path:
            return

        try:
            registros, errores_parse = parse_excel_to_dicts(file_path)
            
            if errores_parse:
                messagebox.showerror("Error", "\n".join(errores_parse))
                return
            
            if not registros:
                messagebox.showinfo("Importar", "No se encontraron filas para importar.")
                return
            
            importados = 0
            errores = []
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                for idx, reg in enumerate(registros, start=2):
                    try:
                        cursor.execute("""
                            INSERT INTO calidad_animal (codigo, descripcion, comentario)
                            VALUES (?, ?, ?)
                        """, (
                            str(reg.get('codigo', '')).strip(),
                            str(reg.get('descripcion', '')).strip(),
                            str(reg.get('comentario', '')).strip()
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: código duplicado")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {e}")
                conn.commit()
            
            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            
            messagebox.showinfo("Importación", mensaje)
            self.cargar_calidades()
        except Exception as e:
            messagebox.showerror("Error", f"Error en importación: {str(e)}")
    
    def mostrar_menu_contextual(self, event):
        try:
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()