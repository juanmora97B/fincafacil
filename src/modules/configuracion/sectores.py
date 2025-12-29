import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from typing import Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from infraestructura.configuracion.configuracion_service import ConfiguracionService
from modules.utils.importador_excel import parse_excel_to_dicts
from modules.utils.constants_ui import PLACEHOLDERS, truncate


class SectoresFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._service = ConfiguracionService()
        self._sector_editando_id: Optional[int] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_fincas_combobox()
        self.cargar_sectores()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        titulo = ctk.CTkLabel(scroll_container, text="🗺️ Configuración de Sectores", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Sector", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Finca
        row0 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row0.pack(fill="x", pady=5)
        ctk.CTkLabel(row0, text="Finca *:", width=100).pack(side="left", padx=5)
        self.combo_finca = ctk.CTkComboBox(row0, width=300)
        self.combo_finca.set(PLACEHOLDERS.get("finca", "Seleccione una finca"))
        self.combo_finca.pack(side="left", padx=5, fill="x", expand=True)

        # Código y Nombre
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Nombre *:", width=100).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, width=150)
        self.entry_nombre.pack(side="left", padx=5)

        # Comentario
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row2, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones formulario
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        ctk.CTkButton(btn_frame, text="💾 Guardar Sector", command=self.guardar_sector,
                      fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Sectores Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20, 5), padx=4)

        # Tabla de sectores
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)
        self.tabla = ttk.Treeview(table_frame, columns=("id", "finca", "codigo", "nombre", "comentario"),
                                  show="headings", displaycolumns=("finca", "codigo", "nombre", "comentario"), height=12)
        column_config = [
            ("id", "ID", 50),
            ("finca", "Finca", 150),
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("comentario", "Comentario", 250)
        ]
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")
        self.tabla.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)  # type: ignore[arg-type]
        scrollbar.pack(side="right", fill="y")

        # Búsqueda rápida
        filtro_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        filtro_frame.pack(fill="x", padx=4)
        ctk.CTkLabel(filtro_frame, text="🔍 Buscar:").pack(side="left", padx=5)
        self.entry_buscar = ctk.CTkEntry(filtro_frame, placeholder_text=PLACEHOLDERS.get("busqueda_general", "Buscar"))
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self.filtrar_tabla())

        # Botones de acción
        action_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        action_frame.pack(pady=10)
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_sector).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_sector,
                      fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_sectores).pack(side="left", padx=5)
        
    def cargar_fincas_combobox(self):
        """Carga las fincas en el combobox usando el servicio"""
        try:
            fincas = self._service.listar_fincas_para_combo_sectores()
            # Mapa interno id->nombre para búsqueda rápida
            self._finca_map = {f['nombre']: f['id'] for f in fincas}
            nombres = [f['nombre'] for f in fincas]
            self.combo_finca.configure(values=nombres)
            if nombres:
                self.combo_finca.set(nombres[0])
            else:
                self.combo_finca.set(PLACEHOLDERS.get("finca", "Seleccione una finca"))
        except ValueError as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")
        
    def guardar_sector(self):
        """Guarda un nuevo o actualizado sector usando el servicio"""
        codigo = self.entry_codigo.get().strip().upper()
        nombre = self.entry_nombre.get().strip().title()
        finca_nombre = self.combo_finca.get().strip()
        comentario = self.text_comentario.get("1.0", "end-1c").strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return
            
        if not finca_nombre or finca_nombre == PLACEHOLDERS.get("finca", "Seleccione una finca"):
            messagebox.showwarning("Atención", "Debe seleccionar una finca.")
            return
        
        finca_id = self._finca_map.get(finca_nombre)
        if not finca_id:
            messagebox.showwarning("Atención", "Finca no válida.")
            return

        try:
            if self._sector_editando_id is None:
                # Crear nuevo sector
                self._service.crear_sector(codigo, nombre, finca_id, comentario)
                messagebox.showinfo("Éxito", "Sector creado correctamente.")
            else:
                # Actualizar sector existente
                self._service.actualizar_sector(self._sector_editando_id, nombre, comentario, finca_id)
                messagebox.showinfo("Éxito", "Sector actualizado correctamente.")
                self._sector_editando_id = None
            
            self.limpiar_formulario()
            self.cargar_sectores()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def cargar_sectores(self):
        """Carga los sectores en la tabla usando el servicio"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            sectores = self._service.listar_sectores_activos()
            self._sectores_data = []
            for s in sectores:
                valores = (
                    str(s['id']),
                    s['finca_nombre'],
                    s['codigo'],
                    s['nombre'],
                    s['comentario']
                )
                self._sectores_data.append(valores)
                self.tabla.insert("", "end", values=valores)
                    
        except ValueError as e:
            messagebox.showerror("Error", f"No se pudieron cargar los sectores:\n{e}")

    def editar_sector(self):
        """Carga el sector seleccionado en el formulario para edición"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un sector para editar.")
            return

        sector_id = int(self.tabla.item(seleccionado[0])["values"][0])

        try:
            sector = self._service.obtener_sector(sector_id)
            
            # Cargar datos en el formulario
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, sector['codigo'])
            self.entry_codigo.configure(state="disabled")  # Código no editable
            
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, sector['nombre'])
            
            self.text_comentario.delete("1.0", "end")
            self.text_comentario.insert("1.0", sector['comentario'])
            
            # Seleccionar finca correspondiente
            finca_id = sector['finca_id']
            for nombre, fid in self._finca_map.items():
                if fid == finca_id:
                    self.combo_finca.set(nombre)
                    break
            
            # Marcar que estamos editando
            self._sector_editando_id = sector_id
            
        except ValueError as e:
            messagebox.showerror("Error", f"No se pudo cargar el sector:\n{e}")

    def eliminar_sector(self):
        """Desactiva el sector seleccionado (soft delete)"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un sector para desactivar.")
            return
        
        sector_id = int(self.tabla.item(seleccionado[0])["values"][0])
        sector_codigo = self.tabla.item(seleccionado[0])["values"][2]
        
        if messagebox.askyesno("Confirmar", f"¿Desactivar el sector '{sector_codigo}'?\n\nPodrá reactivarlo desde la base de datos si es necesario."):
            try:
                self._service.cambiar_estado_sector(sector_id, 'Inactivo')
                messagebox.showinfo("Éxito", "Sector desactivado correctamente.")
                self.cargar_sectores()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def limpiar_formulario(self):
        """Limpia el formulario y resetea el modo de edición"""
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self._sector_editando_id = None
        
        if hasattr(self, 'combo_finca') and hasattr(self, '_finca_map'):
            nombres = list(self._finca_map.keys())
            if nombres:
                self.combo_finca.set(nombres[0])
            else:
                self.combo_finca.set(PLACEHOLDERS.get("finca", "Seleccione una finca"))
        
    def importar_excel(self):
        """Importar sectores desde Excel usando el servicio"""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return

        from modules.utils.importador_excel import importar_sector_desde_excel
        filas, errores_parse = importar_sector_desde_excel(ruta)
        
        if errores_parse:
            messagebox.showerror("Error", "\n".join(errores_parse))
            return

        if not filas:
            messagebox.showinfo("Importar", "No se encontraron filas para importar.")
            return

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip().upper()
            nombre = str(fila.get('nombre') or "").strip().title()
            finca_id = fila.get('finca_id')
            comentario = str(fila.get('comentario') or "").strip()

            if not codigo or not nombre:
                errores.append(f"Fila {idx}: faltan campos requeridos (código y nombre)")
                continue
            
            if not finca_id:
                errores.append(f"Fila {idx}: falta finca_id")
                continue

            try:
                self._service.crear_sector(codigo, nombre, finca_id, comentario)
                importados += 1
            except ValueError as e:
                errores.append(f"Fila {idx}: {str(e)}")

        mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
        if errores:
            mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
        messagebox.showinfo("Importación", mensaje)
        self.cargar_sectores()

    def filtrar_tabla(self):
        """Filtra la tabla según texto en entrada de búsqueda sobre finca, código, nombre y comentario."""
        if not hasattr(self, '_sectores_data'):
            return
        termino = (self.entry_buscar.get() or '').strip().lower()
        # Limpiar tabla actual
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        if not termino:
            for valores in self._sectores_data:
                self.tabla.insert('', 'end', values=valores)
            return
        for valores in self._sectores_data:
            _, finca, codigo, nombre, comentario = valores
            texto_busqueda = ' '.join([finca.lower(), codigo.lower(), nombre.lower(), comentario.lower()])
            if termino in texto_busqueda:
                self.tabla.insert('', 'end', values=valores)