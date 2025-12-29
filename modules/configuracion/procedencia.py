import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
from typing import Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.utils.importador_excel import parse_excel_to_dicts
from infraestructura.configuracion.configuracion_service import ConfiguracionService
from infraestructura.configuracion.configuracion_repository import ConfiguracionRepository


class ProcedenciaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._service = ConfiguracionService()
        self._repo = ConfiguracionRepository()
        self._procedencia_editando_codigo: Optional[str] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_procedencias()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="📍 Configuración de Procedencias", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nueva Procedencia", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

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
        ctk.CTkLabel(row2, text="Tipo:", width=100).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(row2, 
            values=["Granja Propia", "Centro de Acopio", "Importación", "Donación", "Compra Directa", "Otros"],
            width=150, height=35)
        self.combo_tipo.set("Granja Propia")
        self.combo_tipo.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Ubicación:", width=100).pack(side="left", padx=5)
        self.entry_ubicacion = ctk.CTkEntry(row3, width=200)
        self.entry_ubicacion.pack(side="left", padx=5)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row4, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Procedencia", command=self.guardar_procedencia, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", height=40, command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Procedencias Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "descripcion", "tipo", "ubicacion", "comentario"), show="headings", height=18)
        
        column_config = [
            ("codigo", "Código", 120),
            ("descripcion", "Descripción", 300),
            ("tipo", "Tipo", 150),
            ("ubicacion", "Ubicación", 200),
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", height=40, command=self.editar_procedencia).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_procedencia, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", height=40, command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", height=40, command=self.cargar_procedencias).pack(side="left", padx=5)

        # Menú contextual (clic derecho)
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_procedencia)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_procedencia)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_procedencias)
        
        # Vincular eventos de la tabla
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_procedencia())

    def mostrar_menu_contextual(self, event):
        try:
            row_id = self.tabla.identify_row(event.y)
            if row_id:
                self.tabla.selection_set(row_id)
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
        
    def guardar_procedencia(self):
        """Guarda una nueva procedencia o actualiza si está en modo edición"""
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        
        if not codigo or not descripcion:
            messagebox.showwarning("Atención", "Código y Descripción son campos obligatorios.")
            return

        try:
            tipo = self.combo_tipo.get()
            ubicacion = self.entry_ubicacion.get().strip()
            comentario = self.text_comentario.get("1.0", "end-1c").strip()
            
            if self._procedencia_editando_codigo:
                # Modo edición
                self._repo.actualizar_procedencia(
                    codigo=codigo,
                    descripcion=descripcion,
                    tipo_procedencia=tipo,
                    ubicacion=ubicacion,
                    comentario=comentario
                )
                messagebox.showinfo("Éxito", "Procedencia actualizada correctamente.")
            else:
                # Modo creación
                self._repo.crear_procedencia(
                    codigo=codigo,
                    descripcion=descripcion,
                    tipo_procedencia=tipo,
                    ubicacion=ubicacion,
                    comentario=comentario,
                    estado="Activo"
                )
                messagebox.showinfo("Éxito", "Procedencia guardada correctamente.")
            
            self.limpiar_formulario()
            self.cargar_procedencias()
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la procedencia:\n{e}")

    def cargar_procedencias(self):
        """Carga las procedencias en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            procedencias = self._repo.listar_procedencias()
            for proc in procedencias:
                valores = (
                    proc.get('codigo', ''),
                    proc.get('descripcion', ''),
                    proc.get('tipo_procedencia', ''),
                    proc.get('ubicacion', ''),
                    proc.get('comentario', '')
                )
                self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las procedencias:\n{e}")

    def editar_procedencia(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una procedencia para editar.")
            return
        
        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = valores[0]
        
        try:
            procedencia = self._repo.obtener_procedencia(codigo)
            if not procedencia:
                messagebox.showerror("Error", "No se encontró la procedencia")
                return
            
            # Cargar en formulario (inline editing)
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, procedencia['codigo'])
            self.entry_codigo.configure(state="disabled")
            
            self.entry_descripcion.delete(0, "end")
            self.entry_descripcion.insert(0, procedencia['descripcion'])
            
            self.combo_tipo.set(procedencia.get('tipo_procedencia', 'Granja Propia'))
            
            self.entry_ubicacion.delete(0, "end")
            self.entry_ubicacion.insert(0, procedencia.get('ubicacion', ''))
            
            self.text_comentario.delete("1.0", "end")
            if procedencia.get('comentario'):
                self.text_comentario.insert("1.0", procedencia['comentario'])
            
            # Tracking para saber que estamos editando
            self._procedencia_editando_codigo = codigo
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la procedencia:\n{e}")

    def eliminar_procedencia(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una procedencia para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Marcar como inactiva la procedencia '{codigo}'?\n\nPodrá reactivarla desde la base de datos."):
            try:
                self._repo.cambiar_estado_procedencia(codigo, 'Inactivo')
                messagebox.showinfo("Éxito", "Procedencia marcada como inactiva.")
                self.cargar_procedencias()
            except ValueError as e:
                messagebox.showerror("Error de Validación", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.entry_ubicacion.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self.combo_tipo.set("Granja Propia")
        self._procedencia_editando_codigo = None
        
    def importar_excel(self):
        """Importar procedencias desde un archivo Excel.
        Se esperan encabezados: codigo,descripcion,tipo,ubicacion,comentario
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

        # Validar y adaptar columnas
        primera = filas[0]
        variantes_codigo = ['codigo', 'codigos', 'código']
        variantes_descripcion = ['descripcion', 'descripción']
        variantes_tipo = ['tipo', 'tipo_procedencia', 'tipo_origen']
        variantes_ubicacion = ['ubicacion', 'ubicación', 'location']

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
            resolver_col(fila, variantes_tipo, 'tipo')
            resolver_col(fila, variantes_ubicacion, 'ubicacion')

        primera = filas[0]
        if 'codigo' not in primera or 'descripcion' not in primera:
            messagebox.showerror(
                "Error",
                "El archivo debe contener encabezados equivalentes a: codigo, descripcion.\n"
                "Variantes aceptadas: codigos/código, descripción.\n"
                "Los campos tipo, ubicación, comentario son opcionales."
            )
            return

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip()
            descripcion = str(fila.get('descripcion') or "").strip()
            tipo = str(fila.get('tipo') or "Granja Propia").strip()
            ubicacion = str(fila.get('ubicacion') or "").strip()
            comentario = str(fila.get('comentario') or "").strip()

            if not codigo or not descripcion:
                errores.append(f"Fila {idx}: faltan campos requeridos (código, descripción)")
                continue

            try:
                self._repo.crear_procedencia(
                    codigo=codigo,
                    descripcion=descripcion,
                    tipo_procedencia=tipo,
                    ubicacion=ubicacion,
                    comentario=comentario,
                    estado="Activo"
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
        self.cargar_procedencias()
