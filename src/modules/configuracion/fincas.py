import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from infraestructura.configuracion import ConfiguracionService
from modules.utils.importador_excel import parse_excel_to_dicts, mapear_columnas_flexibles


class FincasFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.service = ConfiguracionService()
        self.finca_editando: Optional[str] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_fincas()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="🏠 Configuración de Fincas", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario (scrollable para evitar recortes)
        form_frame = ctk.CTkScrollableFrame(self, corner_radius=10, height=220)
        form_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nueva Finca", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Nombre *:", width=100).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, width=200)
        self.entry_nombre.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Propietario:", width=100).pack(side="left", padx=5)
        self.entry_propietario = ctk.CTkEntry(row2, width=200)
        self.entry_propietario.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Área (Ha):", width=80).pack(side="left", padx=5)
        self.entry_area = ctk.CTkEntry(row2, width=100)
        self.entry_area.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Ubicación:", width=100).pack(side="left", padx=5)
        self.entry_ubicacion = ctk.CTkEntry(row3, width=300)
        self.entry_ubicacion.pack(side="left", padx=5, fill="x", expand=True)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Teléfono:", width=100).pack(side="left", padx=5)
        self.entry_telefono = ctk.CTkEntry(row4, width=150)
        self.entry_telefono.pack(side="left", padx=5)
        ctk.CTkLabel(row4, text="Email:", width=80).pack(side="left", padx=5)
        self.entry_email = ctk.CTkEntry(row4, width=150)
        self.entry_email.pack(side="left", padx=5)

        row5 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Descripción:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_descripcion = ctk.CTkTextbox(row5, width=300, height=60)
        self.text_descripcion.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        ctk.CTkButton(btn_frame, text="💾 Guardar Finca", command=self.guardar_finca,
                      fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(self, text="📋 Fincas Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20, 5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla y configuración de columnas
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "propietario", "area", "ubicacion"), show="headings", height=12)

        column_config = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("propietario", "Propietario", 120),
            ("area", "Área (Ha)", 80),
            ("ubicacion", "Ubicación", 200)
        ]

        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)
        # Diccionario interno: item_id -> finca_id
        self.finca_ids = {}

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)  # type: ignore[arg-type]
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=10)
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_finca).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_finca,
                      fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_fincas).pack(side="left", padx=5)

    def guardar_finca(self):
        """Guarda una nueva finca o actualiza existente"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        ubicacion = self.entry_ubicacion.get().strip()

        try:
            if self.finca_editando:
                self.service.actualizar_finca(self.finca_editando, nombre, ubicacion)
                messagebox.showinfo("Éxito", "Finca actualizada correctamente.")
            else:
                self.service.crear_finca(codigo, nombre, ubicacion)
                messagebox.showinfo("Éxito", "Finca creada correctamente.")
            
            self.limpiar_formulario()
            self.cargar_fincas()
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la finca: {str(e)}")

    def cargar_fincas(self):
        """Carga las fincas en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            fincas = self.service.listar_fincas_activas()
            for finca in fincas:
                codigo = finca.get('codigo', '')
                nombre = finca.get('nombre', '')
                ubicacion = finca.get('ubicacion', '')
                valores = (codigo, nombre, '', '', ubicacion)
                self.tabla.insert("", "end", values=valores)
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas: {str(e)}")

    def editar_finca(self):
        """Carga una finca seleccionada en el formulario para editar"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una finca para editar.")
            return

        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = str(valores[0]).strip()

        try:
            finca = self.service.obtener_finca(codigo)
            
            self.finca_editando = codigo
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, finca.get('codigo', ''))
            self.entry_codigo.configure(state="disabled")
            
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, finca.get('nombre', ''))
            
            self.entry_ubicacion.delete(0, "end")
            self.entry_ubicacion.insert(0, finca.get('ubicacion', ''))

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la finca para editar: {str(e)}")

    def eliminar_finca(self):
        """Marca como inactiva la finca seleccionada (soft delete)"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una finca para desactivar.")
            return

        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = str(valores[0]).strip()
        nombre = str(valores[1])

        if not messagebox.askyesno(
            "Confirmar Desactivación",
            f"¿Está seguro de marcar como Inactiva la finca '{nombre}' (código: {codigo})?\n\n"
            f"⚠️ La finca NO se eliminará de la base de datos.\n"
            f"Se marcará como Inactiva para mantener el historial."
        ):
            return

        try:
            self.service.cambiar_estado_finca(codigo, 'Inactivo')
            messagebox.showinfo("Éxito", f"Finca '{nombre}' marcada como Inactiva correctamente.")
            self.cargar_fincas()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo desactivar la finca: {str(e)}")

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_propietario.delete(0, "end")
        self.entry_ubicacion.delete(0, "end")
        self.entry_area.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.text_descripcion.delete("1.0", "end")
        self.finca_editando = None

    def importar_excel(self):
        """Importar fincas desde un archivo Excel. Esperamos código, nombre y ubicación."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=(("Excel files", "*.xlsx;*.xls"), ("Todos los archivos", "*.*")),
        )
        if not ruta:
            return

        filas, errores_parse = parse_excel_to_dicts(ruta)
        if errores_parse:
            messagebox.showerror("Error", "\n".join(errores_parse))
            return

        if not filas:
            messagebox.showinfo("Importar", "No se encontraron filas para importar.")
            return

        # Definir mapa de columnas alternativas para búsqueda flexible
        mapa_columnas = {
            'codigo': ['codigo', 'código', 'cod', 'code'],
            'nombre': ['nombre', 'name', 'finca'],
            'ubicacion': ['ubicacion', 'ubicación', 'direccion', 'dirección', 'location'],
        }

        # Normalizar columnas en todas las filas
        filas_normalizadas = [mapear_columnas_flexibles(fila, mapa_columnas) for fila in filas]

        # Validar que existan columnas clave
        primera = filas_normalizadas[0]
        if not primera.get("codigo") or not primera.get("nombre"):
            messagebox.showerror("Error", 
                "El archivo debe tener columnas que correspondan a 'codigo', 'nombre' y 'ubicacion'.\n"
                "Variantes aceptadas:\n"
                "- Código: codigo, código, cod, code\n"
                "- Nombre: nombre, name, finca\n"
                "- Ubicación: ubicacion, ubicación, direccion, location")
            return

        importados = 0
        errores = []

        for idx, fila in enumerate(filas_normalizadas, start=2):
            codigo = str(fila.get("codigo") or "").strip()
            nombre = str(fila.get("nombre") or "").strip()
            ubicacion = str(fila.get("ubicacion") or "").strip()

            if not codigo or not nombre:
                errores.append(f"Fila {idx}: falta código o nombre")
                continue

            try:
                self.service.crear_finca(codigo, nombre, ubicacion)
                importados += 1
            except ValueError as e:
                errores.append(f"Fila {idx}: {str(e)}")
            except Exception as e:
                errores.append(f"Fila {idx}: {str(e)}")

        mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
        if errores:
            mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
        messagebox.showinfo("Importación", mensaje)
        self.cargar_fincas()