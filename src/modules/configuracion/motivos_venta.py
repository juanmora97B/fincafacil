import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from typing import Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from infraestructura.configuracion import ConfiguracionService
from modules.utils.importador_excel import parse_excel_to_dicts


class MotivosVentaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.service = ConfiguracionService()
        self.editando_codigo: Optional[str] = None
        self.crear_widgets()
        self.cargar_motivos()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="📋 Configuración de Motivos de Venta", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Motivo", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150,)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Descripción *:", width=100).pack(side="left", padx=5)
        self.entry_descripcion = ctk.CTkEntry(row1, width=200,)
        self.entry_descripcion.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row2, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Motivo", command=self.guardar_motivo, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Motivos Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "descripcion", "comentario"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 120),
            ("descripcion", "Descripción", 200),
            ("comentario", "Comentario", 300)
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
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_motivo).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_motivo, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_motivos).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)

    def guardar_motivo(self):
        """Guarda un nuevo motivo de venta o actualiza si está en edición"""
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        comentario = self.text_comentario.get("1.0", "end-1c").strip()
        
        if not codigo or not descripcion:
            messagebox.showwarning("Atención", "Código y Descripción son campos obligatorios.")
            return

        try:
            if self.editando_codigo is not None:
                self.service.actualizar_motivo_venta(codigo, descripcion, comentario if comentario else None)
                messagebox.showinfo("Éxito", "Motivo de venta actualizado correctamente.")
            else:
                self.service.crear_motivo_venta(codigo, descripcion, comentario if comentario else None)
                messagebox.showinfo("Éxito", "Motivo de venta guardado correctamente.")
            
            self.limpiar_formulario()
            self.cargar_motivos()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Validación fallida: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el motivo: {str(e)}")

    def cargar_motivos(self):
        """Carga los motivos en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            motivos = self.service.listar_motivos_venta()
            for motivo in motivos:
                valores = (motivo['codigo'], motivo['descripcion'], motivo['comentario'])
                self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los motivos: {str(e)}")

    def editar_motivo(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un motivo para editar.")
            return
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        try:
            motivo = self.service.obtener_motivo_venta(codigo)
            if not motivo:
                messagebox.showerror("Error", "No se encontró el motivo")
                return
            
            self.editando_codigo = codigo
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, codigo)
            self.entry_codigo.configure(state="disabled")
            self.entry_descripcion.delete(0, "end")
            self.entry_descripcion.insert(0, motivo['descripcion'])
            self.text_comentario.delete("1.0", "end")
            if motivo['comentario']:
                self.text_comentario.insert("1.0", motivo['comentario'])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el motivo: {str(e)}")

    def eliminar_motivo(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un motivo para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el motivo '{codigo}'?"):
            try:
                self.service.cambiar_estado_motivo_venta(codigo, "Inactivo")
                messagebox.showinfo("Éxito", "Motivo eliminado.")
                self.cargar_motivos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def limpiar_formulario(self):
        self.editando_codigo = None
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.text_comentario.delete("1.0", "end")

    def importar_excel(self):
        """Importar motivos de venta desde un archivo Excel.
        Se esperan encabezados: codigo,descripcion,comentario,estado
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
        if 'codigo' not in primera or 'descripcion' not in primera:
            messagebox.showerror("Error", "El archivo debe tener las columnas 'codigo' y 'descripcion'.")
            return

        importados = 0
        errores = []

        try:
            for idx, fila in enumerate(filas, start=2):
                codigo = str(fila.get('codigo') or "").strip()
                descripcion = str(fila.get('descripcion') or "").strip()
                comentario = str(fila.get('comentario') or "").strip() or None
                estado = str(fila.get('estado') or "Activo").strip() or "Activo"

                if not codigo or not descripcion:
                    errores.append(f"Fila {idx}: faltan campos requeridos (codigo o descripcion)")
                    continue

                try:
                    if self.service.existe_motivo_venta(codigo):
                        errores.append(f"Fila {idx}: motivo con código '{codigo}' ya existe")
                        continue

                    self.service.crear_motivo_venta(codigo, descripcion, comentario)
                    if estado not in ("Activo", "Inactivo"):
                        estado = "Activo"
                    if estado == "Inactivo":
                        self.service.cambiar_estado_motivo_venta(codigo, estado)
                    importados += 1
                except ValueError as e:
                    errores.append(f"Fila {idx}: {str(e)}")
                except Exception as e:
                    errores.append(f"Fila {idx}: {str(e)}")

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_motivos()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")