import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
from typing import Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.utils.importador_excel import parse_excel_to_dicts
from infraestructura.configuracion.configuracion_service import ConfiguracionService


class TipoExplotacionFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._service = ConfiguracionService()
        self._tipo_editando_codigo: Optional[str] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_tipos_explotacion()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="🏭 Configuración de Tipos de Explotación", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        # Compactar margen horizontal del formulario (20→10)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Tipo de Explotación", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

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
        ctk.CTkLabel(row2, text="Categoría:", width=100).pack(side="left", padx=5)
        self.combo_categoria = ctk.CTkComboBox(row2, 
            values=["Carne", "Leche", "Doble Propósito", "Reproducción", "Huevos", "Otros"],
            width=150, height=35)
        self.combo_categoria.set("Carne")
        self.combo_categoria.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row3, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Tipo", command=self.guardar_tipo_explotacion, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", height=40, command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Tipos de Explotación Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "descripcion", "categoria", "comentario"), show="headings", height=18)
        
        column_config = [
            ("codigo", "Código", 120),
            ("descripcion", "Descripción", 300),
            ("categoria", "Categoría", 120),
            ("comentario", "Comentario", 400)
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", height=40, command=self.editar_tipo_explotacion).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_tipo_explotacion, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", height=40, command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", height=40, command=self.cargar_tipos_explotacion).pack(side="left", padx=5)

        # Menú contextual (clic derecho)
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_tipo_explotacion)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_tipo_explotacion)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_tipos_explotacion)
        
        # Vincular eventos de la tabla
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_tipo_explotacion())

    def mostrar_menu_contextual(self, event):
        try:
            row_id = self.tabla.identify_row(event.y)
            if row_id:
                self.tabla.selection_set(row_id)
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
        
    def guardar_tipo_explotacion(self):
        """Guarda un nuevo tipo de explotación o actualiza si está en modo edición"""
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        
        if not codigo or not descripcion:
            messagebox.showwarning("Atención", "Código y Descripción son campos obligatorios.")
            return

        try:
            categoria = self.combo_categoria.get()
            comentario = self.text_comentario.get("1.0", "end-1c").strip()
            
            if self._tipo_editando_codigo:
                # Modo edición
                self._service.actualizar_tipo_explotacion(
                    codigo=codigo,
                    descripcion=descripcion,
                    categoria=categoria,
                    comentario=comentario
                )
                messagebox.showinfo("Éxito", "Tipo de explotación actualizado correctamente.")
            else:
                # Modo creación
                self._service.crear_tipo_explotacion(
                    codigo=codigo,
                    descripcion=descripcion,
                    categoria=categoria,
                    comentario=comentario
                )
                messagebox.showinfo("Éxito", "Tipo de explotación guardado correctamente.")
            
            self.limpiar_formulario()
            self.cargar_tipos_explotacion()
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el tipo:\n{e}")

    def cargar_tipos_explotacion(self):
        """Carga los tipos de explotación en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            tipos = self._service.listar_tipos_explotacion_activos()
            for tipo in tipos:
                valores = (
                    tipo.get('codigo', ''),
                    tipo.get('descripcion', ''),
                    tipo.get('categoria', ''),
                    tipo.get('comentario', '')
                )
                self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los tipos:\n{e}")

    def editar_tipo_explotacion(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un tipo para editar.")
            return
        
        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = valores[0]
        
        try:
            tipo = self._service.obtener_tipo_explotacion(codigo)
            
            # Cargar en formulario (inline editing)
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, tipo['codigo'])
            self.entry_codigo.configure(state="disabled")
            
            self.entry_descripcion.delete(0, "end")
            self.entry_descripcion.insert(0, tipo['descripcion'])
            
            self.combo_categoria.set(tipo.get('categoria', 'Carne'))
            
            self.text_comentario.delete("1.0", "end")
            if tipo.get('comentario'):
                self.text_comentario.insert("1.0", tipo['comentario'])
            
            # Tracking para saber que estamos editando
            self._tipo_editando_codigo = codigo
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el tipo:\n{e}")

    def eliminar_tipo_explotacion(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un tipo para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Marcar como inactivo el tipo '{codigo}'?\n\nPodrá reactivarlo desde la base de datos."):
            try:
                self._service.cambiar_estado_tipo_explotacion(codigo, 'Inactivo')
                messagebox.showinfo("Éxito", "Tipo marcado como inactivo.")
                self.cargar_tipos_explotacion()
            except ValueError as e:
                messagebox.showerror("Error de Validación", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self.combo_categoria.set("Carne")
        self._tipo_editando_codigo = None
        
    def importar_excel(self):
        """Importar tipos de explotación desde un archivo Excel.
        Se esperan encabezados: codigo,descripcion,categoria,estado,comentario
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

        # Validar que existan columnas requeridas (aceptar variantes y relleno)
        primera = filas[0]
        # Compatibilidad: 'codigos' -> 'codigo', 'código' (acentos), 'descripción', 'categoría'
        variantes_codigo = ['codigo', 'codigos', 'código']
        variantes_descripcion = ['descripcion', 'descripción']
        variantes_categoria = ['categoria', 'categoría']

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
            resolver_col(fila, variantes_descripcion, 'descripcion')
            resolver_col(fila, variantes_categoria, 'categoria')
            # Si falta categoria, intentar inferir por palabra clave en comentario
            if not fila.get('categoria'):
                comentario = (fila.get('comentario') or '').lower()
                if 'carne' in comentario:
                    fila['categoria'] = 'Carne'
                elif 'leche' in comentario:
                    fila['categoria'] = 'Leche'
                elif 'doble' in comentario:
                    fila['categoria'] = 'Doble Propósito'
                else:
                    fila['categoria'] = 'Otros'

        primera = filas[0]
        if 'codigo' not in primera or 'descripcion' not in primera or 'categoria' not in primera:
            messagebox.showerror(
                "Error",
                "El archivo debe contener encabezados equivalentes a: codigo, descripcion, categoria.\n"
                "Variantes aceptadas: codigos/código, descripción, categoría.\n"
                "Si falta 'categoria' se infiere y se asigna 'Otros'."
            )
            return

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip()
            descripcion = str(fila.get('descripcion') or "").strip()
            categoria = str(fila.get('categoria') or "").strip()
            comentario = str(fila.get('comentario') or "").strip()

            if not codigo or not descripcion or not categoria:
                errores.append(f"Fila {idx}: faltan campos requeridos (código, descripción y categoría)")
                continue

            try:
                self._service.crear_tipo_explotacion(
                    codigo=codigo,
                    descripcion=descripcion,
                    categoria=categoria,
                    comentario=comentario
                )
                importados += 1
            except ValueError as e:
                errores.append(f"Fila {idx}: {str(e)}")
            except Exception as e:
                errores.append(f"Fila {idx}: {str(e)}")

        mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
        if errores:
            mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
        messagebox.showinfo("Importación", mensaje)
        self.cargar_tipos_explotacion()
