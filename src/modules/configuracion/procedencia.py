import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from infraestructura.configuracion import ConfiguracionService, ConfiguracionRepository
from modules.utils.importador_excel import parse_excel_to_dicts


class ProcedenciaFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.configuracion_service = ConfiguracionService(repository=ConfiguracionRepository())
        self.editando_codigo = None
        self.crear_widgets()
        self.cargar_procedencias()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="📍 Configuración de Procedencias", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=4, fill="x")

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
        ctk.CTkLabel(row2, text="Tipo Procedencia:", width=100).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(row2, 
            values=["Granja", "Centro Acopio", "Importación", "Producción Interna", "Otros"],
            width=150)
        self.combo_tipo.set("Granja")
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
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Procedencias Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "descripcion", "tipo_procedencia", "ubicacion", "comentario"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 120),
            ("descripcion", "Descripción", 180),
            ("tipo_procedencia", "Tipo", 120),
            ("ubicacion", "Ubicación", 150),
            ("comentario", "Comentario", 200)
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_procedencia).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_procedencia, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_procedencias).pack(side="left", padx=5)    
    def guardar_procedencia(self):
        """Guarda una nueva procedencia o actualiza si está en edición"""
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        
        if not codigo or not descripcion:
            messagebox.showwarning("Atención", "Código y Descripción son campos obligatorios.")
            return

        try:
            if self.editando_codigo:
                self.configuracion_service.actualizar_procedencia(
                    codigo=codigo,
                    descripcion=descripcion,
                    tipo_procedencia=self.combo_tipo.get(),
                    ubicacion=self.entry_ubicacion.get().strip(),
                    comentario=self.text_comentario.get("1.0", "end-1c").strip(),
                )
                messagebox.showinfo("Éxito", "Procedencia actualizada correctamente.")
            else:
                self.configuracion_service.crear_procedencia(
                    codigo=codigo,
                    descripcion=descripcion,
                    tipo_procedencia=self.combo_tipo.get(),
                    ubicacion=self.entry_ubicacion.get().strip(),
                    comentario=self.text_comentario.get("1.0", "end-1c").strip(),
                    estado="Activo",
                )
                messagebox.showinfo("Éxito", "Procedencia guardada correctamente.")
            self.limpiar_formulario()
            self.cargar_procedencias()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la procedencia:\n{e}")

    def cargar_procedencias(self):
        """Carga las procedencias en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            filas = self.configuracion_service.listar_procedencias()
            for fila in filas:
                self.tabla.insert("", "end", values=(
                    fila.get('codigo',''),
                    fila.get('descripcion',''),
                    fila.get('tipo_procedencia',''),
                    fila.get('ubicacion',''),
                    fila.get('comentario','')
                ))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las procedencias:\n{e}")

    def editar_procedencia(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una procedencia para editar.")
            return
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        try:
            proc = self.configuracion_service.obtener_procedencia(codigo)
            if not proc:
                messagebox.showerror("Error", "No se encontró la procedencia")
                return
            self.editando_codigo = codigo
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, proc.get('codigo', ''))
            self.entry_codigo.configure(state="disabled")
            self.entry_descripcion.delete(0, "end")
            self.entry_descripcion.insert(0, proc.get('descripcion', ''))
            tipo_proc = proc.get('tipo_procedencia')
            if tipo_proc:
                self.combo_tipo.set(tipo_proc)  # type: ignore[arg-type]
            self.entry_ubicacion.delete(0, "end")
            self.entry_ubicacion.insert(0, proc.get('ubicacion', ''))
            self.text_comentario.delete("1.0", "end")
            if proc.get('comentario'):
                self.text_comentario.insert("1.0", proc.get('comentario'))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la procedencia:\n{e}")

    def eliminar_procedencia(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una procedencia para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la procedencia '{codigo}'?"):
            try:
                self.configuracion_service.cambiar_estado_procedencia(codigo, "Inactivo")
                messagebox.showinfo("Éxito", "Procedencia eliminada.")
                self.cargar_procedencias()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.editando_codigo = None
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.entry_ubicacion.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self.combo_tipo.set("Granja")
        
    def importar_excel(self):
        """Importar procedencias desde un archivo Excel.
        Se esperan encabezados: codigo,descripcion,tipo_procedencia,ubicacion,estado,comentario
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
            registros = []
            for fila in filas:
                registros.append({
                    'codigo': str(fila.get('codigo') or '').strip(),
                    'descripcion': str(fila.get('descripcion') or '').strip(),
                    'tipo_procedencia': str(fila.get('tipo_procedencia') or 'Granja').strip(),
                    'ubicacion': str(fila.get('ubicacion') or '').strip(),
                    'comentario': str(fila.get('comentario') or '').strip(),
                    'estado': str(fila.get('estado') or 'Activo').strip(),
                })

            importados = 0
            errores = []
            for idx, r in enumerate(registros, start=2):
                try:
                    if not r['codigo'] or not r['descripcion']:
                        raise ValueError("faltan campos requeridos (código y descripción)")

                    self.configuracion_service.crear_procedencia(
                        codigo=r['codigo'],
                        descripcion=r['descripcion'],
                        tipo_procedencia=r['tipo_procedencia'],
                        ubicacion=r['ubicacion'],
                        comentario=r['comentario'],
                        estado=r['estado'] or 'Activo',
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

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")