import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from infraestructura.configuracion import ConfiguracionService
from modules.utils.importador_excel import parse_excel_to_dicts


class LotesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.service = ConfiguracionService()
        self.lote_editando_id: Optional[int] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_fincas_combobox()
        self.cargar_lotes()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="📦 Configuración de Lotes", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Lote", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        # Finca
        row0 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row0.pack(fill="x", pady=5)
        ctk.CTkLabel(row0, text="Finca *:", width=100).pack(side="left", padx=5)
        self.combo_finca = ctk.CTkComboBox(row0, width=300)
        self.combo_finca.set("Seleccione una finca")
        self.combo_finca.pack(side="left", padx=5, fill="x", expand=True)
        
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
        ctk.CTkLabel(scroll_container, text="📋 Lotes Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla (incluir columnas id y finca)
        self.tabla = ttk.Treeview(table_frame, columns=("id", "finca", "codigo", "nombre", "descripcion", "criterio"), show="headings", 
                                  displaycolumns=("finca", "codigo", "nombre", "descripcion", "criterio"), height=12)
        
        column_config = [
            ("id", "ID", 50),  # Oculto
            ("finca", "Finca", 130),
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 130),
            ("descripcion", "Descripción", 180),
            ("criterio", "Criterio", 130)
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_lote).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_lote, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_lotes).pack(side="left", padx=5)
    
    def cargar_fincas_combobox(self):
        """Carga las fincas en el combobox"""
        try:
            fincas = self.service.listar_fincas_para_combo_lotes()
            self._finca_map = {f['nombre']: f['id'] for f in fincas}
            nombres = list(self._finca_map.keys())
            self.combo_finca.configure(values=nombres)
            if nombres:
                self.combo_finca.set(nombres[0])
            else:
                self.combo_finca.set("Seleccione una finca")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")
        
    def guardar_lote(self):
        """Guarda un nuevo lote o actualiza uno existente"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        criterio = self.combo_criterio.get()
        finca_nombre = self.combo_finca.get().strip()
        
        # Obtener el ID de la finca
        finca_id = self._finca_map.get(finca_nombre)
        if finca_id is None:
            messagebox.showerror("Error", "Seleccione una finca válida.")
            return
        
        try:
            if self.lote_editando_id:
                # Modo edición
                self.service.actualizar_lote(
                    lote_id=self.lote_editando_id,
                    nombre=nombre,
                    descripcion=descripcion,
                    criterio=criterio,
                    finca_id=finca_id
                )
                messagebox.showinfo("Éxito", "Lote actualizado correctamente.")
            else:
                # Modo creación
                self.service.crear_lote(
                    codigo=codigo,
                    nombre=nombre,
                    finca_id=finca_id,
                    descripcion=descripcion,
                    criterio=criterio
                )
                messagebox.showinfo("Éxito", "Lote guardado correctamente.")
            
            self.limpiar_formulario()
            self.cargar_lotes()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el lote:\n{e}")

    def cargar_lotes(self):
        """Carga los lotes en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            lotes = self.service.listar_lotes_activos()
            for lote in lotes:
                self.tabla.insert("", "end", values=(
                    lote['id'],
                    lote['finca_nombre'],
                    lote['codigo'],
                    lote['nombre'],
                    lote['descripcion'],
                    lote['criterio']
                ))
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los lotes:\n{e}")

    def editar_lote(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un lote para editar.")
            return
        
        # Obtener valores de la fila seleccionada (id, finca, codigo, nombre, descripcion, criterio)
        valores = self.tabla.item(seleccionado[0])["values"]
        lote_id = int(valores[0])  # type: ignore[arg-type]
        
        try:
            lote = self.service.obtener_lote(lote_id)
            
            # Guardar ID para modo edición
            self.lote_editando_id = lote['id']
            
            # Cargar código (deshabilitar campo)
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, lote['codigo'])
            self.entry_codigo.configure(state="disabled")
            
            # Cargar nombre
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, lote['nombre'])
            
            # Cargar descripción
            self.entry_descripcion.delete(0, "end")
            self.entry_descripcion.insert(0, lote['descripcion'])
            
            # Cargar criterio
            self.combo_criterio.set(lote['criterio'])
            
            # Cargar finca (buscar nombre por finca_id)
            for nombre, fid in self._finca_map.items():
                if fid == lote['finca_id']:
                    self.combo_finca.set(nombre)
                    break
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def eliminar_lote(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un lote para desactivar.")
            return
        
        # Obtener ID, código y nombre del lote
        valores = self.tabla.item(seleccionado[0])["values"]
        lote_id = int(valores[0])  # type: ignore[arg-type]
        lote_codigo = valores[2]
        lote_nombre = valores[3]
        
        if messagebox.askyesno(
            "Confirmar Desactivación",
            f"¿Desea desactivar el lote '{lote_codigo} - {lote_nombre}'?\n\n"
            "No se eliminará, solo cambiará a estado Inactivo."
        ):
            try:
                self.service.cambiar_estado_lote(lote_id, 'Inactivo')
                messagebox.showinfo("Éxito", f"Lote '{lote_codigo}' marcado como Inactivo correctamente.")
                self.cargar_lotes()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo desactivar el lote:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.combo_criterio.set("Por Peso")
        if hasattr(self, 'combo_finca') and hasattr(self, '_finca_map'):
            nombres = list(self._finca_map.keys())
            if nombres:
                self.combo_finca.set(nombres[0])
            else:
                self.combo_finca.set("Seleccione una finca")
        # Limpiar atributo temporal de edición
        self.lote_editando_id = None
        
    def importar_excel(self):
        """Importar lotes desde un archivo Excel.
        Se esperan encabezados mínimos: codigo, nombre, finca.
        Opcionales: descripcion, criterio, estado.
        Ahora soporta columna 'finca' (nombre de la finca) para asignar finca_id.
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

        # Validar columnas requeridas
        primera = filas[0]
        encabezados_norm = {k.lower(): k for k in primera.keys()}
        if 'codigo' not in encabezados_norm or 'nombre' not in encabezados_norm or 'finca' not in encabezados_norm:
            messagebox.showerror("Error", "El archivo debe incluir columnas 'codigo', 'nombre' y 'finca'.")
            return

        importados = 0
        errores = []
        try:
            for idx, fila in enumerate(filas, start=2):
                codigo = str(fila.get('codigo') or '').strip()
                nombre = str(fila.get('nombre') or '').strip()
                finca_nombre = str(fila.get('finca') or '').strip()
                descripcion = str(fila.get('descripcion') or '').strip()
                criterio = str(fila.get('criterio') or 'Por Peso').strip()

                if not codigo or not nombre or not finca_nombre:
                    errores.append(f"Fila {idx}: faltan campos requeridos (código, nombre, finca)")
                    continue

                try:
                    finca = self.service.obtener_finca_por_nombre(finca_nombre)
                    finca_id = finca['id']
                except ValueError as e:
                    errores.append(f"Fila {idx}: {str(e)}")
                    continue

                try:
                    self.service.crear_lote(
                        codigo=codigo,
                        nombre=nombre,
                        finca_id=finca_id,
                        descripcion=descripcion,
                        criterio=criterio
                    )
                    importados += 1
                except ValueError as e:
                    errores.append(f"Fila {idx}: {str(e)}")
                except Exception as e:
                    errores.append(f"Fila {idx}: {e}")

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_lotes()
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")