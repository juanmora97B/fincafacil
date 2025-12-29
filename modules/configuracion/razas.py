import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from typing import Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from infraestructura.configuracion import ConfiguracionService
from modules.utils.importador_excel import parse_excel_to_dicts


class RazasFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.service = ConfiguracionService()
        self.editando_codigo: Optional[str] = None
        self.crear_widgets()
        self.cargar_razas()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="🐄 Configuración de Razas", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=5, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nueva Raza", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Nombre *:", width=100).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, width=150)
        self.entry_nombre.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Tipo Ganado:", width=100).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(row2, values=["Lechero", "Carne", "Doble Propósito", "Registro"], height=35)
        self.combo_tipo.set("Doble Propósito")
        self.combo_tipo.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Especie:", width=80).pack(side="left", padx=5)
        self.combo_especie = ctk.CTkComboBox(row2, values=["Bovino", "Bufalo", "Caprino", "Ovino", "Porcino", "Equino", "Otro"], height=35)
        self.combo_especie.set("Bovino")
        self.combo_especie.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Descripción:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_descripcion = ctk.CTkTextbox(row3, width=300, height=60)
        self.text_descripcion.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)

        ctk.CTkButton(btn_frame, text="💾 Guardar Raza", command=self.guardar_raza,
                      fg_color="green", hover_color="#006400", height=36).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario, height=36).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Razas Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20, 5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla con ancho reducido
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "tipo_ganado", "especie", "descripcion"), show="headings", height=18)

        column_config = [
            ("codigo", "Código", 120),
            ("nombre", "Nombre", 200),
            ("tipo_ganado", "Tipo Ganado", 90),
            ("especie", "Especie", 80),
            ("descripcion", "Descripción", 300),
        ]

        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        # Menu contextual
        self.menu_contextual = tk.Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_raza)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_raza)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_razas)

        # Vincular el menú contextual
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_raza())

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)  # type: ignore[arg-type]
        scrollbar.pack(side="right", fill="y")

        # Botones de acción con tamaño estándar
        action_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        action_frame.pack(pady=10)

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_raza, 
                      height=36).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_raza,
                      fg_color="red", hover_color="#8B0000", height=36).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel, 
                      height=36).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_razas, 
                      height=36).pack(side="left", padx=5)

    def guardar_raza(self):
        """Guarda una nueva raza o actualiza si está en edición"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return

        try:
            if self.editando_codigo is not None:
                self.service.actualizar_raza(
                    codigo,
                    nombre,
                    self.combo_tipo.get(),
                    self.combo_especie.get(),
                    self.text_descripcion.get("1.0", "end-1c").strip()
                )
                messagebox.showinfo("Éxito", "Raza actualizada correctamente.")
            else:
                self.service.crear_raza(
                    codigo,
                    nombre,
                    self.combo_tipo.get(),
                    self.combo_especie.get(),
                    self.text_descripcion.get("1.0", "end-1c").strip()
                )
                messagebox.showinfo("Éxito", "Raza guardada correctamente.")
            
            self.limpiar_formulario()
            self.cargar_razas()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Validación fallida: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la raza: {str(e)}")

    def cargar_razas(self):
        """Carga las razas en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            razas = self.service.listar_razas()
            for raza in razas:
                codigo = raza['codigo']
                nombre = raza['nombre']
                tipo = raza['tipo_ganado'] or "-"
                especie = raza['especie'] or "-"
                descripcion = raza['descripcion'] or ""
                if descripcion and len(descripcion) > 50:
                    descripcion = descripcion[:50] + "..."
                self.tabla.insert("", "end", values=(codigo, nombre, tipo, especie, descripcion))
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las razas: {str(e)}")

    def editar_raza(self):
        """Edita la raza seleccionada"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una raza para editar.")
            return

        codigo = self.tabla.item(seleccionado[0])["values"][0]
        try:
            raza = self.service.obtener_raza(codigo)
            if not raza:
                messagebox.showerror("Error", "No se encontró la raza")
                return
            
            self.editando_codigo = codigo
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, codigo)
            self.entry_codigo.configure(state="disabled")
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, raza['nombre'])
            self.combo_tipo.set(raza['tipo_ganado'] or "Doble Propósito")
            self.combo_especie.set(raza['especie'] or "Bovino")
            self.text_descripcion.delete("1.0", "end")
            if raza['descripcion']:
                self.text_descripcion.insert("1.0", raza['descripcion'])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la raza: {str(e)}")

    def eliminar_raza(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una raza para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la raza '{codigo}'?"):
            try:
                self.service.cambiar_estado_raza(codigo, "Inactivo")
                messagebox.showinfo("Éxito", "Raza eliminada.")
                self.cargar_razas()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def limpiar_formulario(self):
        self.editando_codigo = None
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.text_descripcion.delete("1.0", "end")
        self.combo_tipo.set("Doble Propósito")

    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual en la posición del cursor"""
        # Identificar el ítem en la posición del cursor
        item = self.tabla.identify_row(event.y)
        if item:
            # Seleccionar el ítem
            self.tabla.selection_set(item)
            # Mostrar el menú
            self.menu_contextual.post(event.x_root, event.y_root)

    def importar_excel(self):
        """Importar razas desde Excel.
        Se esperan encabezados: codigo,nombre,tipo_ganado,especie,descripcion
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
        if 'codigo' not in primera or 'nombre' not in primera:
            messagebox.showerror("Error", "El archivo debe tener columnas 'codigo' y 'nombre'.")
            return

        importados = 0
        errores = []

        try:
            for idx, fila in enumerate(filas, start=2):
                codigo = str(fila.get('codigo') or "").strip()
                nombre = str(fila.get('nombre') or "").strip()
                tipo_ganado = str(fila.get('tipo_ganado') or fila.get('tipo') or "").strip() or None
                especie = str(fila.get('especie') or "").strip() or None
                descripcion = str(fila.get('descripcion') or "").strip() or None

                if not codigo or not nombre:
                    errores.append(f"Fila {idx}: faltan campos requeridos (codigo o nombre)")
                    continue

                try:
                    if self.service.existe_raza(codigo):
                        errores.append(f"Fila {idx}: raza con código '{codigo}' ya existe")
                        continue

                    self.service.crear_raza(codigo, nombre, tipo_ganado, especie, descripcion)
                    importados += 1
                except ValueError as e:
                    errores.append(f"Fila {idx}: {str(e)}")
                except Exception as e:
                    errores.append(f"Fila {idx}: {str(e)}")

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_razas()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")
