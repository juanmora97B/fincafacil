import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
from typing import Optional
import sys
import os
import sqlite3
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.utils.importador_excel import parse_excel_to_dicts
from src.database import get_connection


def attach_date_picker(entry_widget, master_window=None):
    """Adjunta un datepicker a un widget Entry (simplificado)"""
    # En una implementación real, esto abrirá un calendario
    # Por ahora, es un placeholder
    pass


class EmpleadosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._empleado_editando_codigo: Optional[str] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_empleados()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="👥 Configuración de Empleados", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Datos del Empleado", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Crear notebook (tabs)
        self.notebook = ttk.Notebook(form_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Datos Principales
        tab_principales = ttk.Frame(self.notebook)
        self.notebook.add(tab_principales, text="Datos Principales")
        self.crear_tab_datos_principales(tab_principales)

        # Tab 2: Datos Laborales
        tab_laborales = ttk.Frame(self.notebook)
        self.notebook.add(tab_laborales, text="Datos Laborales")
        self.crear_tab_datos_laborales(tab_laborales)

        # Tab 3: Salario
        tab_salario = ttk.Frame(self.notebook)
        self.notebook.add(tab_salario, text="Salario")
        self.crear_tab_salario(tab_salario)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Empleado", command=self.guardar_empleado, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Empleados Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "cargo", "estado", "fecha_ingreso"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 200),
            ("cargo", "Cargo", 150),
            ("estado", "Estado", 100),
            ("fecha_ingreso", "Fecha Ingreso", 120)
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_empleado).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_empleado, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_empleados).pack(side="left", padx=5)

        # Menú contextual (clic derecho)
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_empleado)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_empleado)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_empleados)
        
        # Vincular eventos de la tabla
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_empleado())

    def crear_tab_datos_principales(self, parent):
        """Crea tab con datos personales del empleado"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Código *:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_codigo = ttk.Entry(frame, width=30)
        self.entry_codigo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Nombre *:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_nombre = ttk.Entry(frame, width=30)
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Apellido:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_apellido = ttk.Entry(frame, width=30)
        self.entry_apellido.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Cédula:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_cedula = ttk.Entry(frame, width=30)
        self.entry_cedula.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Fecha Nacimiento:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.entry_fecha_nacimiento = ttk.Entry(frame, width=30)
        self.entry_fecha_nacimiento.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Teléfono:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.entry_telefono = ttk.Entry(frame, width=30)
        self.entry_telefono.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Email:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.entry_email = ttk.Entry(frame, width=30)
        self.entry_email.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Dirección:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.entry_direccion = ttk.Entry(frame, width=30)
        self.entry_direccion.grid(row=7, column=1, padx=5, pady=5)

    def crear_tab_datos_laborales(self, parent):
        """Crea tab con datos laborales del empleado"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Cargo *:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_cargo = ttk.Combobox(frame, 
            values=["Gerente", "Administrador", "Operario", "Técnico", "Auxiliar", "Supervisor"],
            width=28)
        self.combo_cargo.set("Operario")
        self.combo_cargo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Departamento:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.combo_departamento = ttk.Combobox(frame, 
            values=["Ganadería", "Agricultura", "Administración", "Mantenimiento", "Veterinaria"],
            width=28)
        self.combo_departamento.set("Ganadería")
        self.combo_departamento.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Fecha Ingreso *:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_fecha_ingreso = ttk.Entry(frame, width=30)
        self.entry_fecha_ingreso.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Estado *:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.combo_estado = ttk.Combobox(frame, values=["Activo", "Inactivo", "Licencia"], width=28)
        self.combo_estado.set("Activo")
        self.combo_estado.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Tipo Contrato:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.combo_contrato = ttk.Combobox(frame, 
            values=["Indefinido", "Temporal", "Por Obra", "Aprendiz", "Practicante"],
            width=28)
        self.combo_contrato.set("Indefinido")
        self.combo_contrato.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Gerente Asignado:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.entry_gerente = ttk.Entry(frame, width=30)
        self.entry_gerente.grid(row=5, column=1, padx=5, pady=5)

    def crear_tab_salario(self, parent):
        """Crea tab con información de salario"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Salario Base *:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_salario_base = ttk.Entry(frame, width=30)
        self.entry_salario_base.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Auxilio Transporte:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_aux_transporte = ttk.Entry(frame, width=30)
        self.entry_aux_transporte.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Auxilio Alimentación:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_aux_alimentacion = ttk.Entry(frame, width=30)
        self.entry_aux_alimentacion.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Bonificación:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.entry_bonificacion = ttk.Entry(frame, width=30)
        self.entry_bonificacion.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Deducción AFILIACION:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.entry_deduccion_afiliacion = ttk.Entry(frame, width=30)
        self.entry_deduccion_afiliacion.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Deducción PRESTAMOS:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.entry_deduccion_prestamos = ttk.Entry(frame, width=30)
        self.entry_deduccion_prestamos.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Comentario:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.text_comentario = ttk.Entry(frame, width=30)
        self.text_comentario.grid(row=6, column=1, padx=5, pady=5)

    def mostrar_menu_contextual(self, event):
        try:
            row_id = self.tabla.identify_row(event.y)
            if row_id:
                self.tabla.selection_set(row_id)
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
        
    def guardar_empleado(self):
        """Guarda un nuevo empleado o actualiza si está en modo edición"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        cargo = self.combo_cargo.get().strip()
        fecha_ingreso = self.entry_fecha_ingreso.get().strip()
        salario_base_str = self.entry_salario_base.get().strip()
        
        if not codigo or not nombre or not cargo or not fecha_ingreso or not salario_base_str:
            messagebox.showwarning("Atención", "Código, Nombre, Cargo, Fecha Ingreso y Salario Base son obligatorios.")
            return

        try:
            salario_base = float(salario_base_str)
            apellido = self.entry_apellido.get().strip()
            cedula = self.entry_cedula.get().strip()
            fecha_nacimiento = self.entry_fecha_nacimiento.get().strip()
            telefono = self.entry_telefono.get().strip()
            email = self.entry_email.get().strip()
            direccion = self.entry_direccion.get().strip()
            departamento = self.combo_departamento.get().strip()
            estado = self.combo_estado.get().strip()
            tipo_contrato = self.combo_contrato.get().strip()
            gerente = self.entry_gerente.get().strip()
            aux_transporte = float(self.entry_aux_transporte.get().strip()) if self.entry_aux_transporte.get().strip() else 0
            aux_alimentacion = float(self.entry_aux_alimentacion.get().strip()) if self.entry_aux_alimentacion.get().strip() else 0
            bonificacion = float(self.entry_bonificacion.get().strip()) if self.entry_bonificacion.get().strip() else 0
            deduccion_afiliacion = float(self.entry_deduccion_afiliacion.get().strip()) if self.entry_deduccion_afiliacion.get().strip() else 0
            deduccion_prestamos = float(self.entry_deduccion_prestamos.get().strip()) if self.entry_deduccion_prestamos.get().strip() else 0
            comentario = self.text_comentario.get().strip()
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                if self._empleado_editando_codigo:
                    # Modo edición
                    cursor.execute("""
                        UPDATE empleado 
                        SET nombre=?, apellido=?, cedula=?, fecha_nacimiento=?, telefono=?, email=?, direccion=?,
                            cargo=?, departamento=?, fecha_ingreso=?, estado=?, tipo_contrato=?, gerente=?,
                            salario_base=?, aux_transporte=?, aux_alimentacion=?, bonificacion=?,
                            deduccion_afiliacion=?, deduccion_prestamos=?, comentario=?
                        WHERE codigo=?
                    """, (nombre, apellido, cedula, fecha_nacimiento, telefono, email, direccion,
                          cargo, departamento, fecha_ingreso, estado, tipo_contrato, gerente,
                          salario_base, aux_transporte, aux_alimentacion, bonificacion,
                          deduccion_afiliacion, deduccion_prestamos, comentario, self._empleado_editando_codigo))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Empleado actualizado correctamente.")
                else:
                    # Modo creación
                    cursor.execute("""
                        INSERT INTO empleado (codigo, nombre, apellido, cedula, fecha_nacimiento, telefono, email, direccion,
                                             cargo, departamento, fecha_ingreso, estado, tipo_contrato, gerente,
                                             salario_base, aux_transporte, aux_alimentacion, bonificacion,
                                             deduccion_afiliacion, deduccion_prestamos, comentario)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (codigo, nombre, apellido, cedula, fecha_nacimiento, telefono, email, direccion,
                          cargo, departamento, fecha_ingreso, estado, tipo_contrato, gerente,
                          salario_base, aux_transporte, aux_alimentacion, bonificacion,
                          deduccion_afiliacion, deduccion_prestamos, comentario))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Empleado guardado correctamente.")
            
            self.limpiar_formulario()
            self.cargar_empleados()
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", f"Valores numéricos inválidos: {e}")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El código de empleado ya existe.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el empleado:\n{e}")

    def cargar_empleados(self):
        """Carga los empleados en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, cargo, estado, fecha_ingreso FROM empleado WHERE estado IN ('Activo', 'Inactivo', 'Licencia')")
                
                for row in cursor.fetchall():
                    self.tabla.insert("", "end", values=row)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los empleados:\n{e}")

    def editar_empleado(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para editar.")
            return
        
        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = valores[0]
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, nombre, apellido, cedula, fecha_nacimiento, telefono, email, direccion,
                           cargo, departamento, fecha_ingreso, estado, tipo_contrato, gerente,
                           salario_base, aux_transporte, aux_alimentacion, bonificacion,
                           deduccion_afiliacion, deduccion_prestamos, comentario
                FROM empleado WHERE codigo=?
            """, (codigo,))
            empleado = cursor.fetchone()
            
            if not empleado:
                messagebox.showerror("Error", "No se pudo obtener el empleado.")
                return
            
            # Cargar en formulario
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, empleado[0])
            self.entry_codigo.configure(state="disabled")
            
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, empleado[1])
            
            self.entry_apellido.delete(0, "end")
            self.entry_apellido.insert(0, empleado[2] or "")
            
            self.entry_cedula.delete(0, "end")
            self.entry_cedula.insert(0, empleado[3] or "")
            
            self.entry_fecha_nacimiento.delete(0, "end")
            self.entry_fecha_nacimiento.insert(0, empleado[4] or "")
            
            self.entry_telefono.delete(0, "end")
            self.entry_telefono.insert(0, empleado[5] or "")
            
            self.entry_email.delete(0, "end")
            self.entry_email.insert(0, empleado[6] or "")
            
            self.entry_direccion.delete(0, "end")
            self.entry_direccion.insert(0, empleado[7] or "")
            
            self.combo_cargo.set(empleado[8] or "Operario")
            self.combo_departamento.set(empleado[9] or "Ganadería")
            
            self.entry_fecha_ingreso.delete(0, "end")
            self.entry_fecha_ingreso.insert(0, empleado[10] or "")
            
            self.combo_estado.set(empleado[11] or "Activo")
            self.combo_contrato.set(empleado[12] or "Indefinido")
            
            self.entry_gerente.delete(0, "end")
            self.entry_gerente.insert(0, empleado[13] or "")
            
            self.entry_salario_base.delete(0, "end")
            self.entry_salario_base.insert(0, str(empleado[14]) if empleado[14] else "")
            
            self.entry_aux_transporte.delete(0, "end")
            self.entry_aux_transporte.insert(0, str(empleado[15]) if empleado[15] else "")
            
            self.entry_aux_alimentacion.delete(0, "end")
            self.entry_aux_alimentacion.insert(0, str(empleado[16]) if empleado[16] else "")
            
            self.entry_bonificacion.delete(0, "end")
            self.entry_bonificacion.insert(0, str(empleado[17]) if empleado[17] else "")
            
            self.entry_deduccion_afiliacion.delete(0, "end")
            self.entry_deduccion_afiliacion.insert(0, str(empleado[18]) if empleado[18] else "")
            
            self.entry_deduccion_prestamos.delete(0, "end")
            self.entry_deduccion_prestamos.insert(0, str(empleado[19]) if empleado[19] else "")
            
            self.text_comentario.delete(0, "end")
            self.text_comentario.insert(0, empleado[20] or "")
            
            # Tracking
            self._empleado_editando_codigo = codigo
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el empleado:\n{e}")

    def eliminar_empleado(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Cambiar estado a 'Inactivo' para el empleado '{codigo}'?\n\nPodrá reactivarlo desde la base de datos."):
            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE empleado SET estado='Inactivo' WHERE codigo=?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Empleado marcado como inactivo.")
                self.cargar_empleados()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_apellido.delete(0, "end")
        self.entry_cedula.delete(0, "end")
        self.entry_fecha_nacimiento.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_direccion.delete(0, "end")
        self.combo_cargo.set("Operario")
        self.combo_departamento.set("Ganadería")
        self.entry_fecha_ingreso.delete(0, "end")
        self.combo_estado.set("Activo")
        self.combo_contrato.set("Indefinido")
        self.entry_gerente.delete(0, "end")
        self.entry_salario_base.delete(0, "end")
        self.entry_aux_transporte.delete(0, "end")
        self.entry_aux_alimentacion.delete(0, "end")
        self.entry_bonificacion.delete(0, "end")
        self.entry_deduccion_afiliacion.delete(0, "end")
        self.entry_deduccion_prestamos.delete(0, "end")
        self.text_comentario.delete(0, "end")
        self._empleado_editando_codigo = None
        
    def importar_excel(self):
        """Importar empleados desde un archivo Excel."""
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

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip()
            nombre = str(fila.get('nombre') or "").strip()
            cargo = str(fila.get('cargo') or "Operario").strip()
            fecha_ingreso = str(fila.get('fecha_ingreso') or "").strip()
            salario_base_str = str(fila.get('salario_base') or "0").strip()

            if not codigo or not nombre or not fecha_ingreso:
                errores.append(f"Fila {idx}: faltan campos requeridos (código, nombre, fecha_ingreso)")
                continue

            try:
                salario_base = float(salario_base_str) if salario_base_str else 0
                apellido = str(fila.get('apellido') or "").strip()
                cedula = str(fila.get('cedula') or "").strip()
                fecha_nacimiento = str(fila.get('fecha_nacimiento') or "").strip()
                telefono = str(fila.get('telefono') or "").strip()
                email = str(fila.get('email') or "").strip()
                direccion = str(fila.get('direccion') or "").strip()
                departamento = str(fila.get('departamento') or "Ganadería").strip()
                estado = str(fila.get('estado') or "Activo").strip()
                tipo_contrato = str(fila.get('tipo_contrato') or "Indefinido").strip()
                gerente = str(fila.get('gerente') or "").strip()
                aux_transporte = float(fila.get('aux_transporte') or 0) if fila.get('aux_transporte') else 0
                aux_alimentacion = float(fila.get('aux_alimentacion') or 0) if fila.get('aux_alimentacion') else 0
                bonificacion = float(fila.get('bonificacion') or 0) if fila.get('bonificacion') else 0
                deduccion_afiliacion = float(fila.get('deduccion_afiliacion') or 0) if fila.get('deduccion_afiliacion') else 0
                deduccion_prestamos = float(fila.get('deduccion_prestamos') or 0) if fila.get('deduccion_prestamos') else 0
                comentario = str(fila.get('comentario') or "").strip()
                
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO empleado (codigo, nombre, apellido, cedula, fecha_nacimiento, telefono, email, direccion,
                                             cargo, departamento, fecha_ingreso, estado, tipo_contrato, gerente,
                                             salario_base, aux_transporte, aux_alimentacion, bonificacion,
                                             deduccion_afiliacion, deduccion_prestamos, comentario)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (codigo, nombre, apellido, cedula, fecha_nacimiento, telefono, email, direccion,
                          cargo, departamento, fecha_ingreso, estado, tipo_contrato, gerente,
                          salario_base, aux_transporte, aux_alimentacion, bonificacion,
                          deduccion_afiliacion, deduccion_prestamos, comentario))
                    conn.commit()
                importados += 1
            except ValueError as e:
                errores.append(f"Fila {idx}: valores numéricos inválidos - {str(e)}")
            except sqlite3.IntegrityError:
                errores.append(f"Fila {idx}: el código '{codigo}' ya existe")
            except Exception as e:
                errores.append(f"Fila {idx}: {str(e)}")

        mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
        if errores:
            mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
        messagebox.showinfo("Importación", mensaje)
        self.cargar_empleados()
