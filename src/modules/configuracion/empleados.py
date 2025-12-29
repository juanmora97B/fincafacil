import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sys
from typing import Optional

from modules.utils.date_picker import attach_date_picker

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from infraestructura.configuracion import ConfiguracionService
from modules.utils.importador_excel import parse_excel_to_dicts


class EmpleadosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.service = ConfiguracionService()
        self.empleado_editando: Optional[str] = None  # Código del empleado en edición
        self.crear_widgets()
        self.cargar_empleados()

    def crear_widgets(self):
        # Frame scrollable principal
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="👨‍💼 Configuración de Empleados", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Notebook para diferentes secciones
        self.notebook = ttk.Notebook(scroll_container)
        self.notebook.pack(fill="both", expand=True, padx=2, pady=6)

        # Pestaña Datos Principales
        self.tab_principal = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_principal, text="📋 Datos Principales")

        # Pestaña Asignaciones y Deducciones
        self.tab_salario = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_salario, text="💰 Salario y Deducciones")

        self.configurar_tab_principal()
        self.configurar_tab_salario()

        # Botones generales
        btn_frame = ctk.CTkFrame(scroll_container)
        btn_frame.pack(pady=10)

        self.btn_guardar = ctk.CTkButton(btn_frame, text="💾 Guardar Empleado", command=self.guardar_empleado, 
                     fg_color="green", hover_color="#006400")
        self.btn_guardar.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Tabla de empleados
        self.crear_tabla_empleados(scroll_container)

    def configurar_tab_principal(self):
        """Configura la pestaña de datos principales"""
        main_frame = ctk.CTkScrollableFrame(self.tab_principal)
        main_frame.pack(fill="both", expand=True, padx=2, pady=8)

        # DATOS BÁSICOS
        frame_basicos = ctk.CTkFrame(main_frame)
        frame_basicos.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_basicos, text="📝 Datos Básicos", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Código y N° Identificación
        row1 = ctk.CTkFrame(frame_basicos, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=120).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150,)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="N° Identificación *:", width=140).pack(side="left", padx=5)
        self.entry_identificacion = ctk.CTkEntry(row1, width=150,)
        self.entry_identificacion.pack(side="left", padx=5)

        # Nombres y Apellidos
        row2 = ctk.CTkFrame(frame_basicos, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Nombres *:", width=120).pack(side="left", padx=5)
        self.entry_nombres = ctk.CTkEntry(row2, width=200,)
        self.entry_nombres.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Apellidos *:", width=120).pack(side="left", padx=5)
        self.entry_apellidos = ctk.CTkEntry(row2, width=200,)
        self.entry_apellidos.pack(side="left", padx=5)

        # Cargo y Estado
        row3 = ctk.CTkFrame(frame_basicos, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Cargo *:", width=120).pack(side="left", padx=5)
        self.combo_cargo = ctk.CTkComboBox(row3, values=["Administrador", "Vaquero", "Ordeñador", "Veterinario", "Secretario", "Otro"], width=200)
        self.combo_cargo.set("Vaquero")
        self.combo_cargo.pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="Estado *:", width=100).pack(side="left", padx=5)
        self.combo_estado = ctk.CTkComboBox(row3, values=["Activo", "Inactivo", "Vacaciones", "Licencia"], width=150)
        self.combo_estado.set("Activo")
        self.combo_estado.pack(side="left", padx=5)

        # Finca asignada
        row3b = ctk.CTkFrame(frame_basicos, fg_color="transparent")
        row3b.pack(fill="x", pady=5)
        ctk.CTkLabel(row3b, text="Finca *:", width=120).pack(side="left", padx=5)
        self.combo_finca = ctk.CTkComboBox(row3b, width=350)
        self.combo_finca.pack(side="left", padx=5)

        # DATOS PERSONALES
        frame_personales = ctk.CTkFrame(main_frame)
        frame_personales.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_personales, text="👤 Datos Personales", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Sexo y Estado Civil
        row4 = ctk.CTkFrame(frame_personales, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Sexo:", width=120).pack(side="left", padx=5)
        self.combo_sexo = ctk.CTkComboBox(row4, values=["Masculino", "Femenino", "Otro"], width=150)
        self.combo_sexo.set("Masculino")
        self.combo_sexo.pack(side="left", padx=5)
        ctk.CTkLabel(row4, text="Estado Civil:", width=120).pack(side="left", padx=5)
        self.combo_estado_civil = ctk.CTkComboBox(row4, values=["Soltero", "Casado", "Unión Libre", "Divorciado", "Viudo"], width=150)
        self.combo_estado_civil.set("Soltero")
        self.combo_estado_civil.pack(side="left", padx=5)

        # Fechas importantes
        row5 = ctk.CTkFrame(frame_personales, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        # Fecha Nacimiento con botón de calendario alineado
        nac_frame = ctk.CTkFrame(row5, fg_color="transparent")
        nac_frame.pack(side="left", padx=5)
        ctk.CTkLabel(nac_frame, text="Fecha Nacimiento:", width=140).pack(side="left", padx=(0,5))
        self.entry_fecha_nacimiento = ctk.CTkEntry(nac_frame, width=150)
        self.entry_fecha_nacimiento.pack(side="left")
        attach_date_picker(nac_frame, self.entry_fecha_nacimiento)

        # Fecha Ingreso con botón de calendario alineado
        ing_frame = ctk.CTkFrame(row5, fg_color="transparent")
        ing_frame.pack(side="left", padx=5)
        ctk.CTkLabel(ing_frame, text="Fecha Ingreso *:", width=120).pack(side="left", padx=(0,5))
        self.entry_fecha_ingreso = ctk.CTkEntry(ing_frame, width=150)
        self.entry_fecha_ingreso.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_ingreso.pack(side="left")
        attach_date_picker(ing_frame, self.entry_fecha_ingreso)

        # Fecha Contrato y Retiro
        row6 = ctk.CTkFrame(frame_personales, fg_color="transparent")
        row6.pack(fill="x", pady=5)
        # Fecha Contrato con botón de calendario alineado
        con_frame = ctk.CTkFrame(row6, fg_color="transparent")
        con_frame.pack(side="left", padx=5)
        ctk.CTkLabel(con_frame, text="Fecha Contrato:", width=140).pack(side="left", padx=(0,5))
        self.entry_fecha_contrato = ctk.CTkEntry(con_frame, width=150)
        self.entry_fecha_contrato.pack(side="left")
        attach_date_picker(con_frame, self.entry_fecha_contrato)

        # Fecha Retiro con botón de calendario alineado
        ret_frame = ctk.CTkFrame(row6, fg_color="transparent")
        ret_frame.pack(side="left", padx=5)
        ctk.CTkLabel(ret_frame, text="Fecha Retiro:", width=120).pack(side="left", padx=(0,5))
        self.entry_fecha_retiro = ctk.CTkEntry(ret_frame, width=150)
        self.entry_fecha_retiro.pack(side="left")
        attach_date_picker(ret_frame, self.entry_fecha_retiro)

        # CONTACTO
        frame_contacto = ctk.CTkFrame(main_frame)
        frame_contacto.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_contacto, text="📞 Información de Contacto", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Teléfono y Dirección
        row7 = ctk.CTkFrame(frame_contacto, fg_color="transparent")
        row7.pack(fill="x", pady=5)
        ctk.CTkLabel(row7, text="Teléfono:", width=120).pack(side="left", padx=5)
        self.entry_telefono = ctk.CTkEntry(row7, width=200,)
        self.entry_telefono.pack(side="left", padx=5)
        ctk.CTkLabel(row7, text="Dirección:", width=120).pack(side="left", padx=5)
        self.entry_direccion = ctk.CTkEntry(row7, width=200,)
        self.entry_direccion.pack(side="left", padx=5)

        # FOTO Y COMENTARIOS
        frame_adicional = ctk.CTkFrame(main_frame)
        frame_adicional.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_adicional, text="📷 Foto y Comentarios", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Foto
        row8 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row8.pack(fill="x", pady=5)
        ctk.CTkLabel(row8, text="Foto:", width=120).pack(side="left", padx=5)
        self.btn_foto = ctk.CTkButton(row8, text="📷 Cargar Foto", command=self.cargar_foto)
        self.btn_foto.pack(side="left", padx=5)
        self.label_foto = ctk.CTkLabel(row8, text="No hay foto seleccionada")
        self.label_foto.pack(side="left", padx=5)

        # Comentarios
        row9 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row9.pack(fill="x", pady=5)
        ctk.CTkLabel(row9, text="Comentarios:", width=120).pack(side="left", padx=5, anchor="n")
        self.text_comentarios = ctk.CTkTextbox(row9, width=400, height=80)
        self.text_comentarios.pack(side="left", padx=5, fill="x", expand=True)

    def configurar_tab_salario(self):
        """Configura la pestaña de salario y deducciones"""
        main_frame = ctk.CTkScrollableFrame(self.tab_salario)
        main_frame.pack(fill="both", expand=True, padx=2, pady=8)

        # SALARIO BASE
        frame_salario = ctk.CTkFrame(main_frame)
        frame_salario.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_salario, text="💰 Salario Base", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        row1 = ctk.CTkFrame(frame_salario, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Salario Diario ($):", width=150).pack(side="left", padx=5)
        self.entry_salario_diario = ctk.CTkEntry(row1, width=200,)
        self.entry_salario_diario.pack(side="left", padx=5)

        # ASIGNACIONES
        frame_asignaciones = ctk.CTkFrame(main_frame)
        frame_asignaciones.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_asignaciones, text="📈 Asignaciones Adicionales", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        ctk.CTkLabel(frame_asignaciones, text="Bonos y adicionales al salario base", font=("Segoe UI", 12)).pack(anchor="w", pady=5)

        row2 = ctk.CTkFrame(frame_asignaciones, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Bono Alimenticio ($):", width=150).pack(side="left", padx=5)
        self.entry_bono_alimenticio = ctk.CTkEntry(row2, width=200,)
        self.entry_bono_alimenticio.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(frame_asignaciones, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Bono Productividad ($):", width=150).pack(side="left", padx=5)
        self.entry_bono_productividad = ctk.CTkEntry(row3, width=200,)
        self.entry_bono_productividad.pack(side="left", padx=5)

        # DEDUCCIONES
        frame_deducciones = ctk.CTkFrame(main_frame)
        frame_deducciones.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_deducciones, text="📉 Deducciones Obligatorias", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        ctk.CTkLabel(frame_deducciones, text="Deducciones según ley colombiana", font=("Segoe UI", 12)).pack(anchor="w", pady=5)

        row4 = ctk.CTkFrame(frame_deducciones, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Seguro Social (%):", width=150).pack(side="left", padx=5)
        self.entry_seguro_social = ctk.CTkEntry(row4, width=200,)
        self.entry_seguro_social.pack(side="left", padx=5)

        row5 = ctk.CTkFrame(frame_deducciones, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Otras Deducciones ($):", width=150).pack(side="left", padx=5)
        self.entry_otras_deducciones = ctk.CTkEntry(row5, width=200,)
        self.entry_otras_deducciones.pack(side="left", padx=5)

        # RESUMEN
        frame_resumen = ctk.CTkFrame(main_frame)
        frame_resumen.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_resumen, text="🧮 Resumen Estimado", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        self.label_resumen = ctk.CTkLabel(frame_resumen, text="Complete los campos para ver el resumen", font=("Segoe UI", 12))
        self.label_resumen.pack(anchor="w", pady=5)

    def crear_tabla_empleados(self, container):
        """Crea la tabla de empleados registrados"""
        # Filtros (Estado / Cargo) colocados ARRIBA antes del título
        filtros_frame = ctk.CTkFrame(container)
        filtros_frame.pack(fill="x", padx=6, pady=(12,4))

        ctk.CTkLabel(filtros_frame, text="🔍 Filtros Empleados", font=("Segoe UI", 14, "bold")).pack(side="left", padx=(8,8))

        # Estado
        if not hasattr(self, 'filtro_estado_var'):
            self.filtro_estado_var = ctk.StringVar(value="Todos")
        ctk.CTkLabel(filtros_frame, text="Estado:").pack(side="left", padx=(4,2))
        self.combo_filtro_estado = ctk.CTkOptionMenu(
            filtros_frame,
            variable=self.filtro_estado_var,
            values=["Todos", "Activo", "Inactivo"],
            width=110
        )
        self.combo_filtro_estado.pack(side="left", padx=(0,10))

        # Cargo
        if not hasattr(self, 'filtro_cargo_var'):
            self.filtro_cargo_var = ctk.StringVar(value="Todos")
        ctk.CTkLabel(filtros_frame, text="Cargo:").pack(side="left", padx=(4,2))
        self.combo_filtro_cargo = ctk.CTkOptionMenu(
            filtros_frame,
            variable=self.filtro_cargo_var,
            values=["Todos"],  # Se actualizará dinámicamente
            width=160
        )
        self.combo_filtro_cargo.pack(side="left", padx=(0,10))

        ctk.CTkButton(
            filtros_frame,
            text="Aplicar",
            width=90,
            command=self.cargar_empleados
        ).pack(side="left", padx=(4,4))

        ctk.CTkButton(
            filtros_frame,
            text="Reset",
            width=90,
            fg_color="#666666",
            hover_color="#4d4d4d",
            command=self._reset_filtros_empleados
        ).pack(side="left", padx=(4,4))

        # Cargar opciones de cargo al iniciar
        self._cargar_opciones_cargo_empleados()

        # Separador / Título de la sección (debajo de filtros)
        ctk.CTkLabel(container, text="📋 Empleados Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(4,5), padx=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombres", "cargo", "estado", "salario", "fecha_ingreso"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("nombres", "Nombres", 200),
            ("cargo", "Cargo", 150),
            ("estado", "Estado", 100),
            ("salario", "Salario Diario", 120),
            ("fecha_ingreso", "Fecha Ingreso", 120)
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
        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.pack(pady=10)
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_empleado).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_empleado, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_empleados).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)

    def cargar_foto(self):
        """Carga una foto para el empleado"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar foto del empleado",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.foto_path = file_path
            self.label_foto.configure(text=f"Foto: {os.path.basename(file_path)}")

    def cargar_fincas(self):
        """Nota: Esta función se mantiene vacía para compatibilidad.
        La UI no valida fincas en el alcance base.
        """
        # En FASE 9.2+ se integrará con FincasService
        self.combo_finca.configure(values=["No asignada"])
        self.combo_finca.set("No asignada")

    def guardar_empleado(self):
        """Guarda un nuevo empleado o actualiza uno existente"""
        codigo = self.entry_codigo.get().strip()
        identificacion = self.entry_identificacion.get().strip()
        nombres = self.entry_nombres.get().strip()
        apellidos = self.entry_apellidos.get().strip()
        cargo = self.combo_cargo.get().strip()
        
        if not codigo or not identificacion or not nombres or not apellidos or not cargo:
            messagebox.showerror("Error de Validación", "Código, Identificación, Nombres, Apellidos y Cargo son obligatorios.")
            return

        try:
            if self.empleado_editando is not None:
                self.service.actualizar_empleado(codigo, identificacion, nombres, apellidos, cargo)
                messagebox.showinfo("Éxito", "Empleado actualizado correctamente.")
            else:
                self.service.crear_empleado(codigo, identificacion, nombres, apellidos, cargo)
                messagebox.showinfo("Éxito", "Empleado guardado correctamente.")
            
            self.limpiar_formulario()
            self.cargar_empleados()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Validación fallida: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el empleado: {str(e)}")

    def cargar_empleados(self):
        """Carga los empleados en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            empleados = self.service.listar_empleados_activos()
            for emp in empleados:
                codigo = emp['codigo']
                nombres_apellidos = f"{emp['nombres']} {emp['apellidos']}"
                cargo = emp['cargo'] or "-"
                estado = emp['estado']
                self.tabla.insert("", "end", values=(codigo, nombres_apellidos, cargo, estado))
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los empleados: {str(e)}")

    def _cargar_opciones_cargo_empleados(self):
        """Obtiene lista de cargos distintos para el filtro de empleados"""
        try:
            empleados = self.service.listar_empleados_activos()
            cargos = sorted(list(set(emp.get('cargo') for emp in empleados if emp.get('cargo'))))  # type: ignore[type-var]
            valores = ["Todos"] + cargos
            if hasattr(self, 'combo_filtro_cargo'):
                self.combo_filtro_cargo.configure(values=valores)
                if self.filtro_cargo_var.get() not in valores:
                    self.filtro_cargo_var.set("Todos")
        except Exception as e:
            print(f"[DEBUG EMPLEADOS] Error cargando cargos para filtro: {e}")

    def _reset_filtros_empleados(self):
        if hasattr(self, 'filtro_estado_var'):
            self.filtro_estado_var.set("Todos")
        if hasattr(self, 'filtro_cargo_var'):
            self.filtro_cargo_var.set("Todos")
        self.cargar_empleados()

    def editar_empleado(self):
        """Carga un empleado seleccionado en el formulario para editar"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para editar.")
            return

        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = str(valores[0]).strip()

        try:
            empleado = self.service.obtener_empleado(codigo)
            if not empleado:
                messagebox.showerror("Error", f"No se encontró el empleado con código '{codigo}'.")
                return

            self.empleado_editando = codigo
            self._limpiar_campos_formulario_basico()

            self.entry_codigo.insert(0, empleado.get('codigo', ''))
            self.entry_nombres.insert(0, empleado.get('nombres', ''))
            self.entry_apellidos.insert(0, empleado.get('apellidos', ''))
            self.entry_identificacion.insert(0, empleado.get('numero_identificacion', ''))
            
            cargo = empleado.get('cargo')
            if cargo:
                self.combo_cargo.set(cargo)
            
            estado = empleado.get('estado')
            if estado:
                self.combo_estado.set(estado)

            self.btn_guardar.configure(text="💾 Actualizar Empleado", fg_color="orange", hover_color="#CC8800")
            try:
                self.entry_codigo.configure(state="disabled")
            except Exception:
                pass

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el empleado para editar:\n{e}")

    def eliminar_empleado(self):
        """Marca como Inactivo el empleado seleccionado. NUNCA elimina de la base de datos para mantener historial."""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para marcar como inactivo.")
            return

        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = str(valores[0]).strip()
        nombre_completo = valores[1]
        estado_actual = valores[3] if len(valores) > 3 else "Activo"

        if estado_actual == "Inactivo":
            messagebox.showinfo(
                "Información",
                f"El empleado '{nombre_completo}' ya está marcado como Inactivo.\n\n"
                f"Los empleados inactivos se mantienen en la base de datos para conservar el historial laboral."
            )
            return

        if messagebox.askyesno(
            "Confirmar Marcado como Inactivo",
            f"¿Está seguro de marcar como Inactivo al empleado?\n\n"
            f"Código: {codigo}\n"
            f"Nombre: {nombre_completo}\n\n"
            f"⚠️ El empleado NO se eliminará de la base de datos.\n"
            f"Se marcará como Inactivo para mantener el registro histórico de quien trabajó en la finca."
        ):
            try:
                self.service.cambiar_estado_empleado(codigo, 'Inactivo')
                messagebox.showinfo("Éxito", f"Empleado '{nombre_completo}' marcado como Inactivo correctamente.\n\nSe mantendrá en el historial laboral.")
                self.cargar_empleados()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo marcar como inactivo:\n{e}")

    def mostrar_ruta_bd(self):
        """Muestra la ruta física de la base de datos en uso para diagnosticar múltiples copias."""
        try:
            from database.database import DB_PATH
            messagebox.showinfo("Ruta BD", f"Base de datos usada:\n{DB_PATH}")
        except Exception as e:
            messagebox.showerror("Ruta BD", f"No se pudo determinar la ruta de la BD:\n{e}")

    def importar_excel(self):
        """Importar empleados desde Excel. Se esperan como mínimo: codigo, nombres, apellidos, numero_identificacion, cargo"""
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
        if 'codigo' not in primera or 'nombres' not in primera or 'apellidos' not in primera:
            messagebox.showerror("Error", "El archivo debe tener al menos las columnas 'codigo', 'nombres' y 'apellidos'.")
            return

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip()
            nombres = str(fila.get('nombres') or "").strip()
            apellidos = str(fila.get('apellidos') or "").strip()
            documento = str(fila.get('numero_identificacion') or "").strip()
            cargo = str(fila.get('cargo') or "Vaquero").strip()

            if not codigo or not nombres or not apellidos:
                errores.append(f"Fila {idx}: faltan campos requeridos (codigo, nombres o apellidos)")
                continue

            try:
                self.service.crear_empleado(codigo, documento, nombres, apellidos, cargo)
                importados += 1
            except ValueError as e:
                errores.append(f"Fila {idx}: {str(e)}")
            except Exception as e:
                errores.append(f"Fila {idx}: {str(e)}")

        mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
        if errores:
            mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
        messagebox.showinfo("Importación", mensaje)
        self.cargar_empleados()

    def limpiar_formulario(self):
        """Limpia los campos base del formulario"""
        self.entry_codigo.delete(0, "end")
        self.entry_identificacion.delete(0, "end")
        self.entry_nombres.delete(0, "end")
        self.entry_apellidos.delete(0, "end")
        
        self.combo_cargo.set("Vaquero")
        self.combo_estado.set("Activo")
        
        # Salir del modo edición: reactivar código
        self.empleado_editando = None
        try:
            self.entry_codigo.configure(state="normal")
        except Exception:
            pass
        self.btn_guardar.configure(text="💾 Guardar Empleado", fg_color="green", hover_color="#006400")

    def _limpiar_campos_formulario_basico(self):
        """Limpia campos base sin alterar modo edición. Usado al entrar en edición."""
        self.entry_codigo.delete(0, "end")
        self.entry_identificacion.delete(0, "end")
        self.entry_nombres.delete(0, "end")
        self.entry_apellidos.delete(0, "end")