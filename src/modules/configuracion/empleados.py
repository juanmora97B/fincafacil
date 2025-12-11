import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sqlite3
import os
import sys

from modules.utils.date_picker import attach_date_picker

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Unificación de acceso a BD con nuevo módulo central
try:
    from database.database import get_db_connection as get_connection
except ImportError:
    from database import db  # Legacy fallback
    get_connection = db.get_connection  # type: ignore

from modules.utils.importador_excel import parse_excel_to_dicts


class EmpleadosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.foto_path = None
        # Al editar, almacenamos el código original (PK). No existe columna 'id' en la tabla.
        self.empleado_editando = None  # Código del empleado que se está editando
        self.crear_widgets()
        self.cargar_fincas()
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
        self.tabla.configure(yscroll=scrollbar.set)
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
        """Carga las fincas activas en el combobox"""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo' ORDER BY nombre")
                fincas = cursor.fetchall()
                
                if fincas:
                    valores = [f"{f[0]}-{f[1]}" for f in fincas]
                    self.combo_finca.configure(values=valores)
                    if valores:
                        self.combo_finca.set(valores[0])
                else:
                    self.combo_finca.configure(values=["Sin fincas registradas"])
                    self.combo_finca.set("Sin fincas registradas")
        except Exception as e:
            print(f"Error al cargar fincas: {e}")
            self.combo_finca.configure(values=["Error al cargar"])
            self.combo_finca.set("Error al cargar")

    def guardar_empleado(self):
        """Guarda un nuevo empleado o actualiza uno existente (sin cambiar el código en modo edición)"""
        # Validaciones básicas mejoradas
        if not self.entry_codigo.get().strip():
            messagebox.showerror("Error de Validación", "El Código del empleado es obligatorio.")
            self.entry_codigo.focus()
            return
        
        if not self.entry_identificacion.get().strip():
            messagebox.showerror("Error de Validación", "El N° de Identificación es obligatorio.")
            self.entry_identificacion.focus()
            return

        if not self.entry_nombres.get().strip():
            messagebox.showerror("Error de Validación", "Los Nombres son obligatorios.")
            self.entry_nombres.focus()
            return
        
        if not self.entry_apellidos.get().strip():
            messagebox.showerror("Error de Validación", "Los Apellidos son obligatorios.")
            self.entry_apellidos.focus()
            return

        if not self.entry_fecha_ingreso.get().strip():
            messagebox.showerror("Error de Validación", "La Fecha de Ingreso es obligatoria.")
            self.entry_fecha_ingreso.focus()
            return
        
        # Validar formato de fecha
        try:
            datetime.strptime(self.entry_fecha_ingreso.get().strip(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error de Validación", "La Fecha de Ingreso debe tener formato YYYY-MM-DD.")
            self.entry_fecha_ingreso.focus()
            return
        
        # Validar valores numéricos
        try:
            salario = float(self.entry_salario_diario.get() or 0)
            if salario < 0:
                messagebox.showerror("Error de Validación", "El Salario Diario no puede ser negativo.")
                return
        except ValueError:
            messagebox.showerror("Error de Validación", "El Salario Diario debe ser un valor numérico.")
            return

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Obtener id_finca del combo
                id_finca = None
                if self.combo_finca.get() and self.combo_finca.get() != "Sin fincas registradas" and self.combo_finca.get() != "Error al cargar":
                    try:
                        id_finca = int(self.combo_finca.get().split("-")[0])
                    except:
                        pass

                if self.empleado_editando:  # Modo edición
                    # Actualizar (sin cambiar código para evitar problemas de FK)
                    cursor.execute(
                        """
                        UPDATE empleado SET
                            nombres = ?, apellidos = ?, numero_identificacion = ?,
                            cargo = ?, estado_actual = ?, fecha_ingreso = ?, fecha_contrato = ?,
                            fecha_nacimiento = ?, fecha_retiro = ?, sexo = ?, estado_civil = ?,
                            telefono = ?, direccion = ?, salario_diario = ?, bono_alimenticio = ?,
                            bono_productividad = ?, seguro_social = ?, otras_deducciones = ?,
                            foto_path = ?, comentarios = ?, id_finca = ?
                        WHERE codigo = ?
                        """,
                        (
                            self.entry_nombres.get().strip(),
                            self.entry_apellidos.get().strip(),
                            self.entry_identificacion.get().strip(),
                            self.combo_cargo.get(),
                            self.combo_estado.get(),
                            self.entry_fecha_ingreso.get().strip(),
                            self.entry_fecha_contrato.get().strip() or None,
                            self.entry_fecha_nacimiento.get().strip() or None,
                            self.entry_fecha_retiro.get().strip() or None,
                            self.combo_sexo.get(),
                            self.combo_estado_civil.get(),
                            self.entry_telefono.get().strip(),
                            self.entry_direccion.get().strip(),
                            float(self.entry_salario_diario.get() or 0),
                            float(self.entry_bono_alimenticio.get() or 0),
                            float(self.entry_bono_productividad.get() or 0),
                            float(self.entry_seguro_social.get() or 0),
                            float(self.entry_otras_deducciones.get() or 0),
                            self.foto_path,
                            self.text_comentarios.get("1.0", "end-1c").strip(),
                            id_finca,
                            self.empleado_editando
                        )
                    )
                    messagebox.showinfo("Éxito", "Empleado actualizado correctamente.")
                else:  # Inserción nuevo empleado
                    codigo_nuevo = self.entry_codigo.get().strip()
                    # Verificar si ya existe ese código
                    cursor.execute("SELECT estado_actual FROM empleado WHERE TRIM(codigo)=TRIM(?)", (codigo_nuevo,))
                    existente = cursor.fetchone()
                    if existente:
                        estado_existente = existente[0]
                        if estado_existente == 'Inactivo':
                            # Reactivar y actualizar datos sobre el registro existente
                            cursor.execute(
                                """
                                UPDATE empleado SET
                                    nombres = ?, apellidos = ?, numero_identificacion = ?,
                                    cargo = ?, estado_actual = 'Activo', fecha_ingreso = ?, fecha_contrato = ?,
                                    fecha_nacimiento = ?, fecha_retiro = ?, sexo = ?, estado_civil = ?,
                                    telefono = ?, direccion = ?, salario_diario = ?, bono_alimenticio = ?,
                                    bono_productividad = ?, seguro_social = ?, otras_deducciones = ?,
                                    foto_path = ?, comentarios = ?, estado='Activo', id_finca = ?
                                WHERE TRIM(codigo)=TRIM(?)
                                """,
                                (
                                    self.entry_nombres.get().strip(),
                                    self.entry_apellidos.get().strip(),
                                    self.entry_identificacion.get().strip(),
                                    self.combo_cargo.get(),
                                    self.entry_fecha_ingreso.get().strip(),
                                    self.entry_fecha_contrato.get().strip() or None,
                                    self.entry_fecha_nacimiento.get().strip() or None,
                                    self.entry_fecha_retiro.get().strip() or None,
                                    self.combo_sexo.get(),
                                    self.combo_estado_civil.get(),
                                    self.entry_telefono.get().strip(),
                                    self.entry_direccion.get().strip(),
                                    float(self.entry_salario_diario.get() or 0),
                                    float(self.entry_bono_alimenticio.get() or 0),
                                    float(self.entry_bono_productividad.get() or 0),
                                    float(self.entry_seguro_social.get() or 0),
                                    float(self.entry_otras_deducciones.get() or 0),
                                    self.foto_path,
                                    self.text_comentarios.get("1.0", "end-1c").strip(),
                                    id_finca,
                                    codigo_nuevo
                                )
                            )
                            messagebox.showinfo("Éxito", "Empleado reactivado y actualizado correctamente.")
                        else:
                            messagebox.showerror("Error", f"Ya existe un empleado activo con código {codigo_nuevo}.")
                            return
                    else:
                        # Insertar nuevo porque no existe ningún registro previo
                        cursor.execute(
                            """
                            INSERT INTO empleado (
                                codigo, nombres, apellidos, numero_identificacion, cargo, estado_actual,
                                fecha_ingreso, fecha_contrato, fecha_nacimiento, fecha_retiro,
                                sexo, estado_civil, telefono, direccion,
                                salario_diario, bono_alimenticio, bono_productividad,
                                seguro_social, otras_deducciones, foto_path, comentarios, estado, id_finca
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                codigo_nuevo,
                                self.entry_nombres.get().strip(),
                                self.entry_apellidos.get().strip(),
                                self.entry_identificacion.get().strip(),
                                self.combo_cargo.get(),
                                self.combo_estado.get(),
                                self.entry_fecha_ingreso.get().strip(),
                                self.entry_fecha_contrato.get().strip() or None,
                                self.entry_fecha_nacimiento.get().strip() or None,
                                self.entry_fecha_retiro.get().strip() or None,
                                self.combo_sexo.get(),
                                self.combo_estado_civil.get(),
                                self.entry_telefono.get().strip(),
                                self.entry_direccion.get().strip(),
                                float(self.entry_salario_diario.get() or 0),
                                float(self.entry_bono_alimenticio.get() or 0),
                                float(self.entry_bono_productividad.get() or 0),
                                float(self.entry_seguro_social.get() or 0),
                                float(self.entry_otras_deducciones.get() or 0),
                                self.foto_path,
                                self.text_comentarios.get("1.0", "end-1c").strip(),
                                "Activo",
                                id_finca
                            )
                        )
                        messagebox.showinfo("Éxito", "Empleado guardado correctamente.")

                conn.commit()

            self.limpiar_formulario()
            self.cargar_empleados()

        except sqlite3.IntegrityError as e:
            if "numero_identificacion" in str(e):
                messagebox.showerror("Error", "Ya existe un empleado con ese número de identificación.")
            else:
                messagebox.showerror("Error", "Ya existe un empleado con ese código.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el empleado:\n{e}")

    def cargar_empleados(self):
        """Carga los empleados en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Construir filtros dinámicos
                condiciones = []
                params = []

                estado_filtro = getattr(self, 'filtro_estado_var', None)
                estado_val = estado_filtro.get() if estado_filtro else 'Todos'
                if estado_val == 'Activo':
                    condiciones.append("(estado_actual IS NULL OR estado_actual='Activo')")
                elif estado_val == 'Inactivo':
                    condiciones.append("estado_actual='Inactivo'")

                cargo_filtro = getattr(self, 'filtro_cargo_var', None)
                cargo_val = cargo_filtro.get() if cargo_filtro else 'Todos'
                if cargo_val and cargo_val != 'Todos':
                    condiciones.append("cargo = ?")
                    params.append(cargo_val)

                query = """
                    SELECT codigo, nombres || ' ' || apellidos, cargo,
                           CASE WHEN estado_actual IS NULL THEN 'Activo' ELSE estado_actual END AS estado_mostrar,
                           salario_diario, fecha_ingreso
                    FROM empleado
                """
                if condiciones:
                    query += " WHERE " + " AND ".join(condiciones)
                query += " ORDER BY fecha_ingreso DESC"

                cursor.execute(query, params)
                
                # Mapa para resolver códigos con ceros a la izquierda
                self._codigo_map = {}
                for fila in cursor.fetchall():
                    salario = f"${fila[4]:,.0f}" if fila[4] else "No definido"
                    # Insertar valores: el código se muestra tal cual para comprobar ceros a la izquierda
                    self.tabla.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3], salario, fila[5]))
                    # Si el código es numérico y tiene ceros a la izquierda, guardar versión sin ceros
                    codigo_real = str(fila[0])
                    if codigo_real.isdigit() and codigo_real.startswith('0'):
                        codigo_normalizado = codigo_real.lstrip('0') or '0'
                        if codigo_normalizado != codigo_real:
                            self._codigo_map[codigo_normalizado] = codigo_real
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los empleados:\n{e}")

    def _cargar_opciones_cargo_empleados(self):
        """Obtiene lista de cargos distintos para el filtro de empleados"""
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT DISTINCT cargo FROM empleado WHERE cargo IS NOT NULL AND TRIM(cargo) != '' ORDER BY cargo")
                cargos = [row[0] for row in cur.fetchall() if row[0]]
            valores = ["Todos"] + cargos
            if hasattr(self, 'combo_filtro_cargo'):
                self.combo_filtro_cargo.configure(values=valores)
                # Mantener selección si todavía existe
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
        """Carga datos del empleado seleccionado con búsqueda robusta (TRIM, sin ceros, case-insensitive)."""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para editar.")
            return

        codigo_display = str(self.tabla.item(seleccionado[0])["values"][0]).strip()
        # Resolver código real si se mostró sin ceros a la izquierda
        codigo = self._codigo_map.get(codigo_display, codigo_display)

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Intento 1: exacto TRIM
                cursor.execute(
                    """
                    SELECT codigo, nombres, apellidos, numero_identificacion, cargo, estado_actual,
                           fecha_ingreso, fecha_contrato, fecha_nacimiento, fecha_retiro,
                           sexo, estado_civil, telefono, direccion,
                           salario_diario, bono_alimenticio, bono_productividad,
                           seguro_social, otras_deducciones, foto_path, comentarios, id_finca
                    FROM empleado
                    WHERE TRIM(codigo) = TRIM(?)
                    LIMIT 1
                    """,
                    (codigo,)
                )
                empleado = cursor.fetchone()

                # Intento 2: quitar ceros a la izquierda
                if not empleado and codigo.startswith('0'):
                    alt = codigo.lstrip('0')
                    if alt:
                        cursor.execute(
                            """
                            SELECT codigo, nombres, apellidos, numero_identificacion, cargo, estado_actual,
                                   fecha_ingreso, fecha_contrato, fecha_nacimiento, fecha_retiro,
                                   sexo, estado_civil, telefono, direccion,
                                   salario_diario, bono_alimenticio, bono_productividad,
                                   seguro_social, otras_deducciones, foto_path, comentarios, id_finca
                            FROM empleado
                            WHERE TRIM(codigo) = TRIM(?)
                            LIMIT 1
                            """,
                            (alt,)
                        )
                        empleado = cursor.fetchone()

                # Intento 3: case-insensitive
                if not empleado:
                    cursor.execute(
                        """
                        SELECT codigo, nombres, apellidos, numero_identificacion, cargo, estado_actual,
                               fecha_ingreso, fecha_contrato, fecha_nacimiento, fecha_retiro,
                               sexo, estado_civil, telefono, direccion,
                               salario_diario, bono_alimenticio, bono_productividad,
                               seguro_social, otras_deducciones, foto_path, comentarios, id_finca
                        FROM empleado
                        WHERE LOWER(TRIM(codigo)) = LOWER(TRIM(?))
                        LIMIT 1
                        """,
                        (codigo,)
                    )
                    empleado = cursor.fetchone()

                # Intento 4: comparación numérica si ambos son dígitos
                if not empleado and codigo.isdigit():
                    cursor.execute(
                        """
                        SELECT codigo, nombres, apellidos, numero_identificacion, cargo, estado_actual,
                               fecha_ingreso, fecha_contrato, fecha_nacimiento, fecha_retiro,
                               sexo, estado_civil, telefono, direccion,
                               salario_diario, bono_alimenticio, bono_productividad,
                               seguro_social, otras_deducciones, foto_path, comentarios, id_finca
                        FROM empleado
                        WHERE CAST(codigo AS INTEGER) = CAST(? AS INTEGER)
                        LIMIT 1
                        """,
                        (codigo,)
                    )
                    empleado = cursor.fetchone()

                if not empleado:
                    messagebox.showerror(
                        "Error",
                        f"No se encontró el empleado seleccionado. Código usado: '{codigo}'."
                    )
                    return

                # Guardar código PK
                self.empleado_editando = empleado[0]
                # Limpiar sin salir de edición
                self._limpiar_campos_formulario_basico()

                # Cargar campos
                self.entry_codigo.insert(0, empleado[0] or "")
                self.entry_nombres.insert(0, empleado[1] or "")
                self.entry_apellidos.insert(0, empleado[2] or "")
                self.entry_identificacion.insert(0, empleado[3] or "")
                if empleado[4]:
                    self.combo_cargo.set(empleado[4])
                if empleado[5]:
                    self.combo_estado.set(empleado[5])
                self.entry_fecha_ingreso.insert(0, empleado[6] or "")
                self.entry_fecha_contrato.insert(0, empleado[7] or "")
                self.entry_fecha_nacimiento.insert(0, empleado[8] or "")
                self.entry_fecha_retiro.insert(0, empleado[9] or "")
                if empleado[10]:
                    self.combo_sexo.set(empleado[10])
                if empleado[11]:
                    self.combo_estado_civil.set(empleado[11])
                self.entry_telefono.insert(0, empleado[12] or "")
                self.entry_direccion.insert(0, empleado[13] or "")
                self.entry_salario_diario.insert(0, str(empleado[14] or ""))
                self.entry_bono_alimenticio.insert(0, str(empleado[15] or ""))
                self.entry_bono_productividad.insert(0, str(empleado[16] or ""))
                self.entry_seguro_social.insert(0, str(empleado[17] or ""))
                self.entry_otras_deducciones.insert(0, str(empleado[18] or ""))
                if empleado[19]:
                    self.foto_path = empleado[19]
                    self.label_foto.configure(text=f"Foto: {os.path.basename(empleado[19])}")
                if empleado[20]:
                    self.text_comentarios.insert("1.0", empleado[20])
                
                # Cargar finca (columna 21 - id_finca)
                if empleado[21]:
                    cursor.execute("SELECT id, nombre FROM finca WHERE id = ?", (empleado[21],))
                    finca = cursor.fetchone()
                    if finca:
                        self.combo_finca.set(f"{finca[0]}-{finca[1]}")

                self.btn_guardar.configure(text="💾 Actualizar Empleado", fg_color="orange", hover_color="#CC8800")
                try:
                    self.entry_codigo.configure(state="disabled")
                except Exception:
                    pass

                # Debug opcional: verificar código real en BD tras carga
                cursor.execute("SELECT codigo, estado, estado_actual FROM empleado WHERE codigo = ?", (self.empleado_editando,))
                dbg = cursor.fetchone()
                if dbg:
                    print(f"[DEBUG EDIT] codigo={dbg[0]} estado={dbg[1]} estado_actual={dbg[2]}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el empleado para editar:\n{e}")

    def eliminar_empleado(self):
        """Marca como Inactivo el empleado seleccionado. NUNCA elimina de la base de datos para mantener historial."""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para marcar como inactivo.")
            return

        valores = self.tabla.item(seleccionado[0])["values"]
        codigo_display = str(valores[0]).strip()
        codigo = self._codigo_map.get(codigo_display, codigo_display)
        nombre_completo = valores[1]
        estado_actual = valores[2] if len(valores) > 2 else "Activo"

        # Si ya está inactivo, informar y no hacer nada
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
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE empleado SET estado_actual='Inactivo' WHERE TRIM(codigo)=TRIM(?)",
                        (codigo,)
                    )
                    filas_afectadas = cursor.rowcount
                    # Fallback numérico (códigos con ceros a la izquierda)
                    if filas_afectadas == 0 and codigo.isdigit():
                        cursor.execute(
                            "UPDATE empleado SET estado_actual='Inactivo' WHERE CAST(codigo AS INTEGER)=CAST(? AS INTEGER)",
                            (codigo,)
                        )
                        filas_afectadas = cursor.rowcount
                    conn.commit()
                if filas_afectadas == 0:
                    messagebox.showwarning("Aviso", f"No se pudo marcar como inactivo. Código '{codigo}' no encontrado.")
                else:
                    messagebox.showinfo("Éxito", f"Empleado '{nombre_completo}' marcado como Inactivo correctamente.\n\nSe mantendrá en el historial laboral.")
                self.cargar_empleados()
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
        """Importar empleados desde Excel. Se esperan como mínimo: codigo,nombres,apellidos
        Se pueden incluir columnas opcionales que coincidan con los campos del formulario.
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
        if 'codigo' not in primera or 'nombres' not in primera or 'apellidos' not in primera:
            messagebox.showerror("Error", "El archivo debe tener al menos las columnas 'codigo', 'nombres' y 'apellidos'.")
            return

        def safe_float(val):
            try:
                return float(val)
            except Exception:
                return 0.0

        importados = 0
        errores = []

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                for idx, fila in enumerate(filas, start=2):
                    codigo = str(fila.get('codigo') or "").strip()
                    nombres = str(fila.get('nombres') or "").strip()
                    apellidos = str(fila.get('apellidos') or "").strip()

                    if not codigo or not nombres or not apellidos:
                        errores.append(f"Fila {idx}: faltan campos requeridos (codigo, nombres o apellidos)")
                        continue

                    try:
                        cursor.execute("SELECT COUNT(*) FROM empleado WHERE codigo = ? OR numero_identificacion = ?", (codigo, fila.get('numero_identificacion')))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: empleado con código o identificación ya existe")
                            continue

                        cursor.execute("""
                            INSERT INTO empleado (
                                codigo, nombres, apellidos, numero_identificacion, cargo, estado_actual,
                                fecha_ingreso, fecha_contrato, fecha_nacimiento, fecha_retiro,
                                sexo, estado_civil, telefono, direccion,
                                salario_diario, bono_alimenticio, bono_productividad,
                                seguro_social, otras_deducciones, foto_path, comentarios, estado
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            nombres,
                            apellidos,
                            str(fila.get('numero_identificacion') or "").strip() or None,
                            str(fila.get('cargo') or self.combo_cargo.get()).strip(),
                            str(fila.get('estado_actual') or self.combo_estado.get()).strip(),
                            str(fila.get('fecha_ingreso') or self.entry_fecha_ingreso.get()).strip() or None,
                            str(fila.get('fecha_contrato') or "").strip() or None,
                            str(fila.get('fecha_nacimiento') or "").strip() or None,
                            str(fila.get('fecha_retiro') or "").strip() or None,
                            str(fila.get('sexo') or self.combo_sexo.get()).strip(),
                            str(fila.get('estado_civil') or self.combo_estado_civil.get()).strip(),
                            str(fila.get('telefono') or "").strip() or None,
                            str(fila.get('direccion') or "").strip() or None,
                            safe_float(fila.get('salario_diario') or 0),
                            safe_float(fila.get('bono_alimenticio') or 0),
                            safe_float(fila.get('bono_productividad') or 0),
                            safe_float(fila.get('seguro_social') or 0),
                            safe_float(fila.get('otras_deducciones') or 0),
                            str(fila.get('foto_path') or "").strip() or None,
                            str(fila.get('comentarios') or "").strip() or None,
                            str(fila.get('estado') or "Activo").strip()
                        ))
                        importados += 1
                    except sqlite3.IntegrityError as e:
                        errores.append(f"Fila {idx}: empleado duplicado ({e})")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_empleados()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        # Limpiar campos de texto
        campos_texto = [
            self.entry_codigo, self.entry_identificacion, self.entry_nombres,
            self.entry_apellidos, self.entry_fecha_nacimiento, self.entry_fecha_ingreso,
            self.entry_fecha_contrato, self.entry_fecha_retiro, self.entry_telefono,
            self.entry_direccion, self.entry_salario_diario, self.entry_bono_alimenticio,
            self.entry_bono_productividad, self.entry_seguro_social, self.entry_otras_deducciones
        ]
        
        for campo in campos_texto:
            campo.delete(0, "end")

        # Restablecer combos
        self.combo_cargo.set("Vaquero")
        self.combo_estado.set("Activo")
        self.combo_sexo.set("Masculino")
        self.combo_estado_civil.set("Soltero")

        # Limpiar áreas de texto
        self.text_comentarios.delete("1.0", "end")

        # Limpiar foto
        self.foto_path = None
        self.label_foto.configure(text="No hay foto seleccionada")

        # Establecer fecha de ingreso actual
        self.entry_fecha_ingreso.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Salir del modo edición: reactivar código
        self.empleado_editando = None
        try:
            self.entry_codigo.configure(state="normal")
        except Exception:
            pass
        self.btn_guardar.configure(text="💾 Guardar Empleado", fg_color="green", hover_color="#006400")

    def _limpiar_campos_formulario_basico(self):
        """Limpia campos sin alterar modo edición ni botón guardar. Usado al entrar en edición."""
        campos_texto = [
            self.entry_codigo, self.entry_identificacion, self.entry_nombres,
            self.entry_apellidos, self.entry_fecha_nacimiento, self.entry_fecha_ingreso,
            self.entry_fecha_contrato, self.entry_fecha_retiro, self.entry_telefono,
            self.entry_direccion, self.entry_salario_diario, self.entry_bono_alimenticio,
            self.entry_bono_productividad, self.entry_seguro_social, self.entry_otras_deducciones
        ]
        for campo in campos_texto:
            try:
                campo.delete(0, "end")
            except Exception:
                pass
        # Comentarios y foto
        try:
            self.text_comentarios.delete("1.0", "end")
        except Exception:
            pass
        self.foto_path = None
        try:
            self.label_foto.configure(text="No hay foto seleccionada")
        except Exception:
            pass