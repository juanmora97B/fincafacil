import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
from typing import Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.utils.importador_excel import parse_excel_to_dicts
from infraestructura.configuracion.configuracion_service import ConfiguracionService


class MotivosVentaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._service = ConfiguracionService()
        self._motivo_editando_codigo: Optional[str] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_motivos_venta()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="💰 Configuración de Motivos de Venta", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Motivo de Venta", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

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
        ctk.CTkLabel(row2, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row2, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Motivo", command=self.guardar_motivo_venta, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", height=40, command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Motivos de Venta Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "descripcion", "comentario"), show="headings", height=18)
        
        column_config = [
            ("codigo", "Código", 120),
            ("descripcion", "Descripción", 300),
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", height=40, command=self.editar_motivo_venta).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_motivo_venta, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", height=40, command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", height=40, command=self.cargar_motivos_venta).pack(side="left", padx=5)

        # Menú contextual (clic derecho)
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_motivo_venta)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_motivo_venta)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_motivos_venta)
        
        # Vincular eventos de la tabla
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_motivo_venta())

    def mostrar_menu_contextual(self, event):
        try:
            row_id = self.tabla.identify_row(event.y)
            if row_id:
                self.tabla.selection_set(row_id)
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
        
    def guardar_motivo_venta(self):
        """Guarda un nuevo motivo de venta o actualiza si está en modo edición"""
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        
        if not codigo or not descripcion:
            messagebox.showwarning("Atención", "Código y Descripción son campos obligatorios.")
            return

        try:
            comentario = self.text_comentario.get("1.0", "end-1c").strip()
            
            if self._motivo_editando_codigo:
                # Modo edición
                self._service.actualizar_motivo_venta(
                    codigo=codigo,
                    descripcion=descripcion,
                    comentario=comentario
                )
                messagebox.showinfo("Éxito", "Motivo de venta actualizado correctamente.")
            else:
                # Modo creación
                self._service.crear_motivo_venta(
                    codigo=codigo,
                    descripcion=descripcion,
                    comentario=comentario
                )
                messagebox.showinfo("Éxito", "Motivo de venta guardado correctamente.")
            
            self.limpiar_formulario()
            self.cargar_motivos_venta()
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el motivo:\n{e}")

    def cargar_motivos_venta(self):
        """Carga los motivos de venta en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            motivos = self._service.listar_motivos_venta()
            for motivo in motivos:
                valores = (
                    motivo.get('codigo', ''),
                    motivo.get('descripcion', ''),
                    motivo.get('comentario', '')
                )
                self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los motivos:\n{e}")

    def editar_motivo_venta(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un motivo para editar.")
            return
        
        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = valores[0]
        
        try:
            motivo = self._service.obtener_motivo_venta(codigo)
            if not motivo:
                messagebox.showerror("Error", "No se encontró el motivo de venta")
                return
            
            # Cargar en formulario (inline editing)
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, motivo['codigo'])
            self.entry_codigo.configure(state="disabled")
            
            self.entry_descripcion.delete(0, "end")
            self.entry_descripcion.insert(0, motivo['descripcion'])
            
            self.text_comentario.delete("1.0", "end")
            if motivo.get('comentario'):
                self.text_comentario.insert("1.0", motivo['comentario'])
            
            # Tracking para saber que estamos editando
            self._motivo_editando_codigo = codigo
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el motivo:\n{e}")

    def eliminar_motivo_venta(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un motivo para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Marcar como inactivo el motivo '{codigo}'?\n\nPodrá reactivarlo desde la base de datos."):
            try:
                self._service.cambiar_estado_motivo_venta(codigo, 'Inactivo')
                messagebox.showinfo("Éxito", "Motivo marcado como inactivo.")
                self.cargar_motivos_venta()
            except ValueError as e:
                messagebox.showerror("Error de Validación", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self._motivo_editando_codigo = None
        
    def importar_excel(self):
        """Importar motivos de venta desde un archivo Excel.
        Se esperan encabezados: codigo,descripcion,comentario
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
        
        # Compatibilidad: 'codigos' -> 'codigo', 'código' (acentos), 'descripción'
        variantes_codigo = ['codigo', 'codigos', 'código']
        variantes_descripcion = ['descripcion', 'descripción']

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

        primera = filas[0]
        if 'codigo' not in primera or 'descripcion' not in primera:
            messagebox.showerror(
                "Error",
                "El archivo debe contener encabezados equivalentes a: codigo, descripcion.\n"
                "Variantes aceptadas: codigos/código, descripción.\n"
                "El campo 'comentario' es opcional."
            )
            return

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip()
            descripcion = str(fila.get('descripcion') or "").strip()
            comentario = str(fila.get('comentario') or "").strip()

            if not codigo or not descripcion:
                errores.append(f"Fila {idx}: faltan campos requeridos (código, descripción)")
                continue

            try:
                self._service.crear_motivo_venta(
                    codigo=codigo,
                    descripcion=descripcion,
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
        self.cargar_motivos_venta()
