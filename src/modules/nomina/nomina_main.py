import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.ui import get_theme_colors, add_tooltip, style_treeview
from modules.utils.date_picker import attach_date_picker
from modules.utils.logger import get_logger
from modules.utils.colores import obtener_colores


class NominaModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        # Colores y modo adaptativos
        colors = get_theme_colors()
        self._modo = colors["mode"]
        self._fg_card = colors["fg"]
        self._sel = colors["sel"]
        self._hover = colors["hover"]
        # Colores del módulo
        self.color_bg, self.color_hover = obtener_colores('nomina')
        self.logger = get_logger("Nomina")
        
        # Inicializar atributos
        self.combo_empleado = None
        self.combo_filtro_empleado = None
        self.tabla_empleados = None
        self.tabla_historial = None

        self.crear_widgets()
        self.cargar_empleados()
        self.cargar_historial()

    def crear_widgets(self):
        # Título con color del módulo
        header = ctk.CTkFrame(self, fg_color=(self.color_bg, "#1a1a1a"), corner_radius=15)
        header.pack(fill="x", padx=15, pady=(10, 6))
        titulo = ctk.CTkLabel(header, text="👥 Nómina y Empleados", font=("Segoe UI", 22, "bold"), text_color="white")
        titulo.pack(side="left", anchor="w", padx=15, pady=10)
        add_tooltip(titulo, "Gestión completa de empleados, salarios y nómina")

        # Notebook expandido para ocupar toda la altura disponible
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=(3, 5))

        # Tab: Gestión de Empleados (Completo)
        self.frame_gestion_empleados = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_gestion_empleados, text="👨‍💼 Gestión de Empleados")

        # Tab: Empleados (Lista)
        self.frame_empleados = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_empleados, text="👤 Lista de Empleados")

        # Tab: Cálculo de Nómina
        self.frame_calculo = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_calculo, text="💰 Cálculo de Nómina")

        # Tab: Historial
        self.frame_historial = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_historial, text="📋 Historial")

        # Crear contenido de cada tab
        self.crear_tab_gestion_empleados()
        self.crear_tab_empleados()
        self.crear_tab_calculo()
        self.crear_tab_historial()

    def crear_tab_gestion_empleados(self):
        """Tab de gestión completa de empleados - carga el módulo completo de empleados"""
        try:
            from modules.configuracion.empleados import EmpleadosFrame
            # Crear el frame de empleados completo dentro de esta pestaña
            empleados_frame = EmpleadosFrame(self.frame_gestion_empleados)
        except Exception as e:
            # En caso de error, mostrar mensaje
            error_label = ctk.CTkLabel(
                self.frame_gestion_empleados,
                text=f"⚠️ Error al cargar gestión de empleados:\n{str(e)}",
                font=("Segoe UI", 14)
            )
            error_label.pack(pady=50)
            print(f"Error cargando gestión de empleados: {e}")

    def crear_tab_empleados(self):
        """Tab de gestión de empleados"""
        main_frame = ctk.CTkScrollableFrame(self.frame_empleados)
        # Reducir padding horizontal para aprovechar ancho
        main_frame.pack(fill="both", expand=True, padx=2, pady=5)
        # Filtros arriba antes de título
        filtros_frame = ctk.CTkFrame(main_frame)
        filtros_frame.pack(fill="x", pady=(0,6))
        ctk.CTkLabel(filtros_frame, text="🔍 Filtros Nómina", font=("Segoe UI", 14, "bold")).pack(side="left", padx=(8,8))

        self.filtro_estado_nomina_var = getattr(self, 'filtro_estado_nomina_var', ctk.StringVar(value="Activo"))
        ctk.CTkLabel(filtros_frame, text="Estado:").pack(side="left", padx=(4,2))
        self.combo_filtro_estado_nomina = ctk.CTkOptionMenu(
            filtros_frame,
            variable=self.filtro_estado_nomina_var,
            values=["Activo", "Inactivo", "Todos"],
            width=110
        )
        self.combo_filtro_estado_nomina.pack(side="left", padx=(0,10))

        self.filtro_cargo_nomina_var = getattr(self, 'filtro_cargo_nomina_var', ctk.StringVar(value="Todos"))
        ctk.CTkLabel(filtros_frame, text="Cargo:").pack(side="left", padx=(4,2))
        self.combo_filtro_cargo_nomina = ctk.CTkOptionMenu(
            filtros_frame,
            variable=self.filtro_cargo_nomina_var,
            values=["Todos"],
            width=160
        )
        self.combo_filtro_cargo_nomina.pack(side="left", padx=(0,10))

        self.filtro_finca_nomina_var = getattr(self, 'filtro_finca_nomina_var', ctk.StringVar(value="Todas"))
        ctk.CTkLabel(filtros_frame, text="Finca:").pack(side="left", padx=(4,2))
        self.combo_filtro_finca_nomina = ctk.CTkOptionMenu(
            filtros_frame,
            variable=self.filtro_finca_nomina_var,
            values=["Todas"],
            width=160
        )
        self.combo_filtro_finca_nomina.pack(side="left", padx=(0,10))

        ctk.CTkButton(filtros_frame, text="Aplicar", width=90, command=self.cargar_empleados).pack(side="left", padx=(4,4))
        ctk.CTkButton(filtros_frame, text="Reset", width=90, fg_color="#666666", hover_color="#4d4d4d", command=self._reset_filtros_nomina).pack(side="left", padx=(4,4))

        # Inicializar opciones de cargos y fincas
        self._cargar_opciones_cargo_nomina()
        self._cargar_opciones_finca_nomina()

        # Título después de filtros
        ctk.CTkLabel(
            main_frame,
            text="📋 Lista de Empleados",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 5))

        # Frame de información
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            info_frame,
            text="💡 Para agregar o editar empleados, use el módulo de Configuración > Empleados",
            font=("Segoe UI", 12),
            wraplength=600
        ).pack(pady=10)

        # Tabla de empleados
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        style_treeview()

        self.tabla_empleados = ttk.Treeview(
            table_frame,
            columns=("id", "codigo", "nombre", "cargo", "finca", "salario", "bonos", "deducciones", "estado"),
            displaycolumns=("codigo", "nombre", "cargo", "finca", "salario", "bonos", "deducciones", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("id", "ID", 50),
            ("codigo", "Código", 90),
            ("nombre", "Nombre Completo", 180),
            ("cargo", "Cargo", 130),
            ("finca", "Finca", 130),
            ("salario", "Salario Diario", 110),
            ("bonos", "Bonos Mensual", 110),
            ("deducciones", "Deducciones", 110),
            ("estado", "Estado", 90)
        ]

        for col, heading, width in columnas:
            self.tabla_empleados.heading(col, text=heading)
            self.tabla_empleados.column(col, width=width, anchor="center")

        self.tabla_empleados.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_empleados.yview)
        self.tabla_empleados.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        btn_act = ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar",
            command=self.cargar_empleados,
            width=150,
            fg_color=self._sel,
            hover_color=self._hover
        )
        btn_act.pack(side="left", padx=5)
        add_tooltip(btn_act, "Recargar lista de empleados")

        btn_det = ctk.CTkButton(
            btn_frame,
            text="📊 Ver Detalles",
            command=self.ver_detalles_empleado,
            width=150,
            fg_color=self._sel,
            hover_color=self._hover
        )
        btn_det.pack(side="left", padx=5)
        add_tooltip(btn_det, "Ver detalle del empleado seleccionado")
        
        btn_export = ctk.CTkButton(
            btn_frame,
            text="📥 Exportar",
            command=self.exportar_empleados,
            width=150,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        )
        btn_export.pack(side="left", padx=5)
        add_tooltip(btn_export, "Exportar lista de empleados a Excel/PDF")

    def crear_tab_calculo(self):
        """Tab de cálculo de nómina"""
        main_frame = ctk.CTkScrollableFrame(self.frame_calculo)
        main_frame.pack(fill="both", expand=True, padx=4, pady=10)

        header_calc = ctk.CTkLabel(
            main_frame,
            text="💰 Cálculo de Nómina",
            font=("Segoe UI", 18, "bold"),
            text_color=self._sel
        )
        header_calc.pack(pady=(0, 10))
        add_tooltip(header_calc, "Calcule la nómina por empleado y período")

        # Período
        periodo_frame = ctk.CTkFrame(main_frame)
        periodo_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(periodo_frame, text="Período de Pago:", width=150).pack(side="left", padx=5)
        
        # Fechas predeterminadas (mes actual)
        hoy = datetime.now()
        primer_dia_mes = hoy.replace(day=1)
        self.entry_fecha_inicio = ctk.CTkEntry(periodo_frame, placeholder_text="Fecha Inicio (YYYY-MM-DD)", width=180)
        self.entry_fecha_inicio.insert(0, primer_dia_mes.strftime("%Y-%m-%d"))
        self.entry_fecha_inicio.pack(side="left", padx=5)
        attach_date_picker(periodo_frame, self.entry_fecha_inicio)
        
        self.entry_fecha_fin = ctk.CTkEntry(periodo_frame, placeholder_text="Fecha Fin (YYYY-MM-DD)", width=180)
        self.entry_fecha_fin.insert(0, hoy.strftime("%Y-%m-%d"))
        self.entry_fecha_fin.pack(side="left", padx=5)
        attach_date_picker(periodo_frame, self.entry_fecha_fin)

        # Empleado
        empleado_frame = ctk.CTkFrame(main_frame)
        empleado_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(empleado_frame, text="Empleado:", width=150).pack(side="left", padx=5)
        self.combo_empleado = ctk.CTkComboBox(empleado_frame, width=300)
        self.combo_empleado.pack(side="left", padx=5, fill="x", expand=True)

        # Días trabajados
        dias_frame = ctk.CTkFrame(main_frame)
        dias_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(dias_frame, text="Días Trabajados:", width=150).pack(side="left", padx=5)
        self.entry_dias = ctk.CTkEntry(dias_frame, width=200)
        self.entry_dias.insert(0, "30")
        self.entry_dias.pack(side="left", padx=5)

        # Opciones adicionales
        opciones_frame = ctk.CTkFrame(main_frame)
        opciones_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(opciones_frame, text="Opciones:", width=150).pack(side="left", padx=5)
        
        self.var_incluir_bonos = ctk.BooleanVar(value=True)
        self.check_bonos = ctk.CTkCheckBox(opciones_frame, text="Incluir Bonos", variable=self.var_incluir_bonos)
        self.check_bonos.pack(side="left", padx=5)
        
        self.var_incluir_deducciones = ctk.BooleanVar(value=True)
        self.check_deducciones = ctk.CTkCheckBox(opciones_frame, text="Incluir Deducciones", variable=self.var_incluir_deducciones)
        self.check_deducciones.pack(side="left", padx=5)

        # Resultado
        resultado_frame = ctk.CTkFrame(main_frame)
        resultado_frame.pack(fill="x", pady=5)

        self.label_resultado = ctk.CTkLabel(
            resultado_frame,
            text="Complete los campos y haga clic en 'Calcular'",
            font=("Segoe UI", 14),
            wraplength=600
        )
        self.label_resultado.pack(pady=5)

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        btn_calcular = ctk.CTkButton(
            btn_frame,
            text="🧮 Calcular Nómina",
            command=self.calcular_nomina,
            fg_color=self._sel,
            hover_color=self._hover,
            width=200
        )
        btn_calcular.pack(side="left", padx=5)
        add_tooltip(btn_calcular, "Ejecutar cálculo de nómina con los datos ingresados")

        btn_registrar = ctk.CTkButton(
            btn_frame,
            text="💾 Registrar Pago",
            command=self.registrar_pago,
            fg_color=self._sel,
            hover_color=self._hover,
            width=150
        )
        btn_registrar.pack(side="left", padx=5)
        add_tooltip(btn_registrar, "Guardar el pago calculado en el historial")

        btn_limpiar_calc = ctk.CTkButton(
            btn_frame,
            text="🔄 Limpiar",
            command=self.limpiar_calculo,
            width=150
        )
        btn_limpiar_calc.pack(side="left", padx=5)
        add_tooltip(btn_limpiar_calc, "Limpiar campos del cálculo")

        btn_actualizar_calc = ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar Lista",
            command=self.cargar_empleados_combo,
            width=150
        )
        btn_actualizar_calc.pack(side="left", padx=5)
        add_tooltip(btn_actualizar_calc, "Actualizar lista de empleados")

        # Cargar empleados
        self.cargar_empleados_combo()

    def crear_tab_historial(self):
        """Tab de historial de pagos"""
        main_frame = ctk.CTkScrollableFrame(self.frame_historial)
        main_frame.pack(fill="both", expand=True, padx=4, pady=10)

        header_hist = ctk.CTkLabel(
            main_frame,
            text="📋 Historial de Pagos",
            font=("Segoe UI", 18, "bold"),
            text_color=self._sel
        )
        header_hist.pack(pady=(0, 5))
        add_tooltip(header_hist, "Pagos de nómina registrados")

        # Filtros
        filtros_frame = ctk.CTkFrame(main_frame)
        filtros_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(filtros_frame, text="Empleado:", width=80).pack(side="left", padx=5)
        
        self.combo_filtro_empleado = ctk.CTkComboBox(filtros_frame, width=200, values=["Todos los empleados"])
        self.combo_filtro_empleado.set("Todos los empleados")
        self.combo_filtro_empleado.pack(side="left", padx=5)
        
        ctk.CTkLabel(filtros_frame, text="Finca:", width=50).pack(side="left", padx=5)
        self.combo_filtro_finca_historial = ctk.CTkComboBox(filtros_frame, width=150, values=["Todas las fincas"])
        self.combo_filtro_finca_historial.set("Todas las fincas")
        self.combo_filtro_finca_historial.pack(side="left", padx=5)
        
        ctk.CTkLabel(filtros_frame, text="Mes:", width=50).pack(side="left", padx=5)
        meses = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.combo_filtro_mes = ctk.CTkComboBox(filtros_frame, width=120, values=meses)
        self.combo_filtro_mes.set("Todos")
        self.combo_filtro_mes.pack(side="left", padx=5)

        ctk.CTkButton(
            filtros_frame,
            text="🔍 Aplicar Filtros",
            command=self.aplicar_filtros_historial,
            width=120
        ).pack(side="left", padx=5)

        # Cargar fincas en el filtro
        self._cargar_fincas_filtro_historial()

        # Tabla
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        style_treeview()

        self.tabla_historial = ttk.Treeview(
            table_frame,
            columns=("id", "fecha", "empleado", "finca", "periodo", "dias", "salario_base", "bonos", "deducciones", "total", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("id", "ID", 60),
            ("fecha", "Fecha Pago", 100),
            ("empleado", "Empleado", 150),
            ("finca", "Finca", 120),
            ("periodo", "Período", 100),
            ("dias", "Días", 60),
            ("salario_base", "Salario Base", 100),
            ("bonos", "Bonos", 100),
            ("deducciones", "Deducciones", 100),
            ("total", "Total", 100),
            ("estado", "Estado", 80)
        ]

        for col, heading, width in columnas:
            self.tabla_historial.heading(col, text=heading)
            self.tabla_historial.column(col, width=width, anchor="center")

        self.tabla_historial.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_historial.yview)
        self.tabla_historial.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        btn_hist_act = ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar",
            command=self.cargar_historial,
            width=150,
            fg_color=self._sel,
            hover_color=self._hover
        )
        btn_hist_act.pack(side="left", padx=5)
        add_tooltip(btn_hist_act, "Recargar historial de pagos")

        btn_ver_det = ctk.CTkButton(
            btn_frame,
            text="📄 Ver Detalle",
            command=self.ver_detalle_pago,
            width=150,
            fg_color=self._sel,
            hover_color=self._hover
        )
        btn_ver_det.pack(side="left", padx=5)
        add_tooltip(btn_ver_det, "Ver detalle del pago seleccionado")

        btn_anular = ctk.CTkButton(
            btn_frame,
            text="🗑️ Anular Pago",
            command=self.anular_pago,
            fg_color="red",
            hover_color="#8B0000",
            width=150
        )
        btn_anular.pack(side="left", padx=5)
        add_tooltip(btn_anular, "Anular el pago seleccionado")

    def cargar_empleados(self):
        """Carga los empleados en la tabla"""
        for item in self.tabla_empleados.get_children():
            self.tabla_empleados.delete(item)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT e.rowid, e.codigo, e.nombres || ' ' || e.apellidos as nombre, 
                           e.cargo, f.nombre as finca_nombre, e.salario_diario, 
                           COALESCE(e.bono_alimenticio, 0) + COALESCE(e.bono_productividad, 0) as total_bonos,
                           COALESCE(e.seguro_social, 0) + COALESCE(e.otras_deducciones, 0) as total_deducciones,
                           CASE WHEN e.estado_actual IS NULL THEN 'Activo' ELSE e.estado_actual END AS estado_actual
                    FROM empleado e
                    LEFT JOIN finca f ON e.id_finca = f.id
                """)
                # Aplicar filtros dinámicos en memoria (lista pequeña) para mayor flexibilidad
                estado_f = getattr(self, 'filtro_estado_nomina_var', None)
                estado_val = estado_f.get() if estado_f else 'Activo'
                cargo_f = getattr(self, 'filtro_cargo_nomina_var', None)
                cargo_val = cargo_f.get() if cargo_f else 'Todos'
                finca_f = getattr(self, 'filtro_finca_nomina_var', None)
                finca_val = finca_f.get() if finca_f else 'Todas'

                rows = cursor.fetchall()
                filtradas = []
                for row in rows:
                    r_estado = row['estado_actual'] if hasattr(row, 'keys') else row[8]
                    r_cargo = row['cargo'] if hasattr(row, 'keys') else row[3]
                    r_finca = row['finca_nombre'] if hasattr(row, 'keys') else row[4]
                    # Filtro estado
                    if estado_val == 'Activo' and not (r_estado == 'Activo'):
                        continue
                    if estado_val == 'Inactivo' and not (r_estado == 'Inactivo'):
                        continue
                    # 'Todos' no filtra
                    # Filtro cargo
                    if cargo_val != 'Todos' and r_cargo != cargo_val:
                        continue
                    # Filtro finca
                    if finca_val != 'Todas' and r_finca != finca_val:
                        continue
                    filtradas.append(row)

                # Limpiar tabla antes de insertar
                for item in self.tabla_empleados.get_children():
                    self.tabla_empleados.delete(item)

                for row in filtradas:
                    emp_id = row['rowid'] if hasattr(row, 'keys') else row[0]
                    codigo = row['codigo'] if hasattr(row, 'keys') else row[1]
                    nombre = row['nombre'] if hasattr(row, 'keys') else row[2]
                    cargo = row['cargo'] if hasattr(row, 'keys') else row[3]
                    finca_nombre = row['finca_nombre'] if hasattr(row, 'keys') else row[4]
                    salario_val = row['salario_diario'] if hasattr(row, 'keys') else row[5]
                    bonos_val = row['total_bonos'] if hasattr(row, 'keys') else row[6]
                    deduc_val = row['total_deducciones'] if hasattr(row, 'keys') else row[7]
                    estado = row['estado_actual'] if hasattr(row, 'keys') else row[8]
                    salario = f"${salario_val:,.0f}" if salario_val else "$0"
                    bonos = f"${bonos_val:,.0f}" if bonos_val else "$0"
                    deducciones = f"${deduc_val:,.0f}" if deduc_val else "$0"
                    self.tabla_empleados.insert("", "end", values=(
                        emp_id, codigo, nombre, cargo or "-", finca_nombre or "Sin Finca", salario, bonos, deducciones, estado or "Activo"
                    ))

                for row in cursor.fetchall():
                    emp_id = row['rowid'] if hasattr(row, 'keys') else row[0]
                    codigo = row['codigo'] if hasattr(row, 'keys') else row[1]
                    nombre = row['nombre'] if hasattr(row, 'keys') else row[2]
                    cargo = row['cargo'] if hasattr(row, 'keys') else row[3]
                    salario_val = row['salario_diario'] if hasattr(row, 'keys') else row[4]
                    bonos_val = row['total_bonos'] if hasattr(row, 'keys') else row[5]
                    deduc_val = row['total_deducciones'] if hasattr(row, 'keys') else row[6]
                    estado = row['estado_actual'] if hasattr(row, 'keys') else row[7]
                    
                    salario = f"${salario_val:,.0f}" if salario_val else "$0"
                    bonos = f"${bonos_val:,.0f}" if bonos_val else "$0"
                    deducciones = f"${deduc_val:,.0f}" if deduc_val else "$0"
                    
                    self.tabla_empleados.insert("", "end", values=(
                        emp_id, codigo, nombre, cargo or "-", salario, bonos, deducciones, estado or "Activo"
                    ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los empleados:\n{e}")

    def _cargar_opciones_cargo_nomina(self):
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT DISTINCT cargo FROM empleado WHERE cargo IS NOT NULL AND TRIM(cargo) != '' ORDER BY cargo")
                cargos = [r[0] for r in cur.fetchall() if r[0]]
            valores = ["Todos"] + cargos
            if hasattr(self, 'combo_filtro_cargo_nomina'):
                self.combo_filtro_cargo_nomina.configure(values=valores)
                if self.filtro_cargo_nomina_var.get() not in valores:
                    self.filtro_cargo_nomina_var.set("Todos")
        except Exception as e:
            print(f"[DEBUG NOMINA] Error cargando cargos filtro: {e}")

    def _cargar_opciones_finca_nomina(self):
        """Carga las fincas disponibles en el filtro"""
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM finca ORDER BY nombre")
                fincas = [r[0] for r in cur.fetchall()]
            valores = ["Todas"] + fincas
            if hasattr(self, 'combo_filtro_finca_nomina'):
                self.combo_filtro_finca_nomina.configure(values=valores)
                if self.filtro_finca_nomina_var.get() not in valores:
                    self.filtro_finca_nomina_var.set("Todas")
        except Exception as e:
            print(f"[DEBUG NOMINA] Error cargando fincas filtro: {e}")

    def _cargar_fincas_filtro_historial(self):
        """Carga las fincas disponibles en el filtro del historial"""
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM finca ORDER BY nombre")
                fincas = [r[0] for r in cur.fetchall()]
            valores = ["Todas las fincas"] + fincas
            if hasattr(self, 'combo_filtro_finca_historial'):
                self.combo_filtro_finca_historial.configure(values=valores)
        except Exception as e:
            print(f"[DEBUG NOMINA] Error cargando fincas filtro historial: {e}")

    def _reset_filtros_nomina(self):
        if hasattr(self, 'filtro_estado_nomina_var'):
            self.filtro_estado_nomina_var.set("Activo")
        if hasattr(self, 'filtro_cargo_nomina_var'):
            self.filtro_cargo_nomina_var.set("Todos")
        if hasattr(self, 'filtro_finca_nomina_var'):
            self.filtro_finca_nomina_var.set("Todas")
        self.cargar_empleados()

    def cargar_empleados_combo(self):
        """Carga empleados en los combobox"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, nombres || ' ' || apellidos as nombre
                    FROM empleado
                    WHERE estado = 'Activo'
                    ORDER BY nombres
                """)
                empleados = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
                if self.combo_empleado:
                    self.combo_empleado.configure(values=empleados)
                if self.combo_filtro_empleado:
                    self.combo_filtro_empleado.configure(values=["Todos los empleados"] + empleados)
                    self.combo_filtro_empleado.set("Todos los empleados")
        except Exception as e:
            self.logger.error(f"Error al cargar empleados: {e}")

    def ver_detalles_empleado(self):
        """Muestra los detalles del empleado seleccionado con foto"""
        seleccionado = self.tabla_empleados.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para ver sus detalles")
            return

        # Obtener código del empleado (índice 1 de la tabla)
        codigo_display = str(self.tabla_empleados.item(seleccionado[0])["values"][1]).strip()
        
        print(f"[DEBUG VER_DETALLES] Código obtenido de la tabla: '{codigo_display}'")
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                empleado = None
                
                # Intento 1: Búsqueda exacta con TRIM
                cursor.execute("""
                    SELECT codigo, nombres, apellidos, numero_identificacion, cargo, salario_diario,
                           bono_alimenticio, bono_productividad, seguro_social, otras_deducciones,
                           fecha_ingreso, fecha_contrato, fecha_nacimiento, sexo, estado_civil,
                           telefono, direccion, foto_path, comentarios, estado_actual
                    FROM empleado
                    WHERE TRIM(codigo) = TRIM(?)
                    LIMIT 1
                """, (codigo_display,))
                empleado = cursor.fetchone()
                print(f"[DEBUG VER_DETALLES] Intento 1 (TRIM): {'Encontrado' if empleado else 'No encontrado'}")
                
                # Intento 2: Agregar ceros a la izquierda
                if not empleado and codigo_display.isdigit():
                    codigo_con_ceros = codigo_display.zfill(2)
                    cursor.execute("""
                        SELECT codigo, nombres, apellidos, numero_identificacion, cargo, salario_diario,
                               bono_alimenticio, bono_productividad, seguro_social, otras_deducciones,
                               fecha_ingreso, fecha_contrato, fecha_nacimiento, sexo, estado_civil,
                               telefono, direccion, foto_path, comentarios, estado_actual
                        FROM empleado
                        WHERE TRIM(codigo) = ?
                        LIMIT 1
                    """, (codigo_con_ceros,))
                    empleado = cursor.fetchone()
                    print(f"[DEBUG VER_DETALLES] Intento 2 (zfill {codigo_con_ceros}): {'Encontrado' if empleado else 'No encontrado'}")
                
                # Intento 3: Buscar quitando ceros a la izquierda en BD
                if not empleado and codigo_display.isdigit():
                    cursor.execute("""
                        SELECT codigo, nombres, apellidos, numero_identificacion, cargo, salario_diario,
                               bono_alimenticio, bono_productividad, seguro_social, otras_deducciones,
                               fecha_ingreso, fecha_contrato, fecha_nacimiento, sexo, estado_civil,
                               telefono, direccion, foto_path, comentarios, estado_actual
                        FROM empleado
                        WHERE CAST(codigo AS INTEGER) = CAST(? AS INTEGER)
                        LIMIT 1
                    """, (codigo_display,))
                    empleado = cursor.fetchone()
                    print(f"[DEBUG VER_DETALLES] Intento 3 (CAST INTEGER): {'Encontrado' if empleado else 'No encontrado'}")
                
                if empleado:
                    self._mostrar_ventana_detalles_empleado(empleado)
                else:
                    messagebox.showerror("Error", f"No se encontró el empleado con código: {codigo_display}")

        except Exception as e:
            print(f"[DEBUG VER_DETALLES] Error: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los detalles:\n{e}")
    
    def _mostrar_ventana_detalles_empleado(self, empleado):
        """Muestra ventana modal con detalles completos del empleado y su foto"""
        from tkinter import Toplevel
        from PIL import Image, ImageTk
        import os
        
        ventana = Toplevel(self)
        ventana.title(f"📋 Detalles del Empleado - {empleado[0]}")
        ventana.geometry("900x650")
        ventana.resizable(False, False)
        ventana.transient(self)
        ventana.grab_set()
        
        # Frame principal con scroll
        main_scroll = ctk.CTkScrollableFrame(ventana)
        main_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(
            main_scroll,
            text=f"👤 {empleado[1]} {empleado[2]}",
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(pady=10)
        
        # Frame horizontal para foto y datos básicos
        top_frame = ctk.CTkFrame(main_scroll)
        top_frame.pack(fill="x", pady=10, padx=10)
        
        # Frame para la foto (izquierda)
        foto_frame = ctk.CTkFrame(top_frame)
        foto_frame.pack(side="left", padx=20, pady=10)
        
        # Cargar y mostrar foto
        foto_path = empleado[17]  # foto_path
        if foto_path and os.path.exists(foto_path):
            try:
                imagen = Image.open(foto_path)
                # Redimensionar manteniendo aspecto (máximo 200x250)
                imagen.thumbnail((200, 250), Image.Resampling.LANCZOS)
                foto_tk = ImageTk.PhotoImage(imagen)
                label_foto = ctk.CTkLabel(foto_frame, image=foto_tk, text="")
                label_foto.image = foto_tk  # Mantener referencia
                label_foto.pack()
            except Exception as e:
                ctk.CTkLabel(foto_frame, text="📷\nFoto no disponible", font=("Segoe UI", 14), 
                           text_color="gray").pack(pady=40)
        else:
            ctk.CTkLabel(foto_frame, text="📷\nSin foto", font=("Segoe UI", 14), 
                       text_color="gray").pack(pady=40)
        
        # Frame para datos básicos (derecha)
        datos_frame = ctk.CTkFrame(top_frame)
        datos_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        # Datos básicos
        info_basica = f"""
📋 INFORMACIÓN BÁSICA

🆔 Código: {empleado[0]}
🪪 Identificación: {empleado[3] or 'No registrada'}
� Cargo: {empleado[4] or 'No especificado'}
👤 Sexo: {empleado[13] or 'No especificado'}
💑 Estado Civil: {empleado[14] or 'No especificado'}
� Fecha Nacimiento: {empleado[12] or 'No especificada'}
📅 Fecha Ingreso: {empleado[10] or 'No especificada'}
📅 Fecha Contrato: {empleado[11] or 'No especificada'}
📊 Estado: {empleado[19] or 'Activo'}
        """
        
        label_basica = ctk.CTkLabel(
            datos_frame,
            text=info_basica.strip(),
            font=("Segoe UI", 12),
            justify="left"
        )
        label_basica.pack(anchor="w", padx=10, pady=5)
        
        # Contacto
        contacto_frame = ctk.CTkFrame(main_scroll)
        contacto_frame.pack(fill="x", pady=10, padx=10)
        
        info_contacto = f"""
📞 INFORMACIÓN DE CONTACTO

☎️ Teléfono: {empleado[15] or 'No registrado'}
� Dirección: {empleado[16] or 'No registrada'}
        """
        
        label_contacto = ctk.CTkLabel(
            contacto_frame,
            text=info_contacto.strip(),
            font=("Segoe UI", 12),
            justify="left"
        )
        label_contacto.pack(anchor="w", padx=10, pady=10)
        
        # Información Salarial
        salario_frame = ctk.CTkFrame(main_scroll)
        salario_frame.pack(fill="x", pady=10, padx=10)
        
        salario_diario = empleado[5] or 0
        bono_alim = empleado[6] or 0
        bono_prod = empleado[7] or 0
        seg_social = empleado[8] or 0
        otras_deduc = empleado[9] or 0
        
        # Cálculos mensuales
        salario_mensual = salario_diario * 30
        total_bonos = bono_alim + bono_prod
        total_deduc = seg_social + otras_deduc
        neto_mensual = salario_mensual + total_bonos - total_deduc
        
        info_salario = f"""
�💰 INFORMACIÓN SALARIAL

💵 Salario Diario: ${salario_diario:,.0f}
🍽️ Bono Alimenticio: ${bono_alim:,.0f}
📈 Bono Productividad: ${bono_prod:,.0f}
🏥 Seguro Social: ${seg_social:,.0f}
📉 Otras Deducciones: ${otras_deduc:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PROYECCIÓN MENSUAL (30 días)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Salario Base: ${salario_mensual:,.0f}
➕ Total Bonos: ${total_bonos:,.0f}
➖ Total Deducciones: ${total_deduc:,.0f}

💵 NETO A PAGAR: ${neto_mensual:,.0f}
        """
        
        label_salario = ctk.CTkLabel(
            salario_frame,
            text=info_salario.strip(),
            font=("Segoe UI", 12),
            justify="left"
        )
        label_salario.pack(anchor="w", padx=10, pady=10)
        
        # Comentarios
        if empleado[18]:  # comentarios
            comentarios_frame = ctk.CTkFrame(main_scroll)
            comentarios_frame.pack(fill="x", pady=10, padx=10)
            
            ctk.CTkLabel(
                comentarios_frame,
                text="📝 COMENTARIOS",
                font=("Segoe UI", 14, "bold")
            ).pack(anchor="w", padx=10, pady=5)
            
            label_comentarios = ctk.CTkLabel(
                comentarios_frame,
                text=empleado[18],
                font=("Segoe UI", 11),
                justify="left",
                wraplength=800
            )
            label_comentarios.pack(anchor="w", padx=10, pady=5)
        
        # Botón cerrar
        btn_cerrar = ctk.CTkButton(
            main_scroll,
            text="✖️ Cerrar",
            command=ventana.destroy,
            fg_color="gray",
            hover_color="#555555",
            width=150
        )
        btn_cerrar.pack(pady=20)

    def calcular_nomina(self):
        """Calcula la nómina de un empleado"""
        if not self.combo_empleado.get() or not self.entry_dias.get():
            messagebox.showwarning("Atención", "Complete todos los campos")
            return

        try:
            codigo_empleado = self.combo_empleado.get().split(" - ")[0]
            dias = int(self.entry_dias.get())
            fecha_inicio = self.entry_fecha_inicio.get()
            fecha_fin = self.entry_fecha_fin.get()

            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT salario_diario, bono_alimenticio, bono_productividad, 
                           seguro_social, otras_deducciones, nombres || ' ' || apellidos
                    FROM empleado
                    WHERE codigo = ? AND estado = 'Activo'
                """, (codigo_empleado,))

                row = cursor.fetchone()
                if not row:
                    messagebox.showerror("Error", "Empleado no encontrado")
                    return

                salario_diario = row[0] or 0
                bono_alimenticio = row[1] or 0
                bono_productividad = row[2] or 0
                seguro_social = row[3] or 0
                otras_deducciones = row[4] or 0
                nombre_empleado = row[5]

                # Cálculos
                salario_base = salario_diario * dias
                
                # Aplicar opciones
                total_bonos = (bono_alimenticio + bono_productividad) if self.var_incluir_bonos.get() else 0
                total_deducciones = (seguro_social + otras_deducciones) if self.var_incluir_deducciones.get() else 0
                
                total_pagar = salario_base + total_bonos - total_deducciones

                # Mostrar resultado
                resultado = f"""
💰 CÁLCULO DE NÓMINA

👤 Empleado: {nombre_empleado}
📅 Período: {fecha_inicio} a {fecha_fin}
📊 Días Trabajados: {dias}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DESGLOSE:

💰 Salario Base ({dias} días × ${salario_diario:,.0f}): ${salario_base:,.0f}
"""

                if self.var_incluir_bonos.get():
                    resultado += f"""➕ Bonos: ${total_bonos:,.0f}
   • Alimenticio: ${bono_alimenticio:,.0f}
   • Productividad: ${bono_productividad:,.0f}
"""

                if self.var_incluir_deducciones.get():
                    resultado += f"""➖ Deducciones: ${total_deducciones:,.0f}
   • Seguro Social: ${seguro_social:,.0f}
   • Otras: ${otras_deducciones:,.0f}
"""

                resultado += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 TOTAL A PAGAR: ${total_pagar:,.0f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

                self.label_resultado.configure(text=resultado)
                self.calculo_actual = {
                    'codigo_empleado': codigo_empleado,
                    'nombre_empleado': nombre_empleado,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'dias': dias,
                    'salario_base': salario_base,
                    'total_bonos': total_bonos,
                    'total_deducciones': total_deducciones,
                    'total_pagar': total_pagar
                }

        except ValueError:
            messagebox.showerror("Error", "Los días trabajados deben ser un número")
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular nómina:\n{e}")

    def registrar_pago(self):
        """Registra el pago de nómina en la base de datos"""
        if not hasattr(self, 'calculo_actual'):
            messagebox.showwarning("Atención", "Primero debe calcular una nómina")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Crear tabla de pagos si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pago_nomina (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo_empleado TEXT NOT NULL,
                        fecha_pago DATE DEFAULT CURRENT_DATE,
                        periodo_inicio DATE NOT NULL,
                        periodo_fin DATE NOT NULL,
                        dias_trabajados INTEGER NOT NULL,
                        salario_base REAL NOT NULL,
                        bonos REAL NOT NULL,
                        deducciones REAL NOT NULL,
                        total_pagado REAL NOT NULL,
                        estado TEXT DEFAULT 'Pagado',
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (codigo_empleado) REFERENCES empleado(codigo)
                    )
                """)

                # Insertar pago
                cursor.execute("""
                    INSERT INTO pago_nomina 
                    (codigo_empleado, periodo_inicio, periodo_fin, dias_trabajados,
                     salario_base, bonos, deducciones, total_pagado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.calculo_actual['codigo_empleado'],
                    self.calculo_actual['fecha_inicio'],
                    self.calculo_actual['fecha_fin'],
                    self.calculo_actual['dias'],
                    self.calculo_actual['salario_base'],
                    self.calculo_actual['total_bonos'],
                    self.calculo_actual['total_deducciones'],
                    self.calculo_actual['total_pagar']
                ))

                conn.commit()

            messagebox.showinfo("Éxito", "Pago registrado correctamente en el historial")
            self.cargar_historial()
            self.limpiar_calculo()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el pago:\n{e}")

    def limpiar_calculo(self):
        """Limpia el formulario de cálculo"""
        self.combo_empleado.set("")
        self.entry_dias.delete(0, "end")
        self.entry_dias.insert(0, "30")
        hoy = datetime.now()
        primer_dia_mes = hoy.replace(day=1)
        self.entry_fecha_inicio.delete(0, "end")
        self.entry_fecha_inicio.insert(0, primer_dia_mes.strftime("%Y-%m-%d"))
        self.entry_fecha_fin.delete(0, "end")
        self.entry_fecha_fin.insert(0, hoy.strftime("%Y-%m-%d"))
        self.label_resultado.configure(text="Complete los campos y haga clic en 'Calcular'")
        if hasattr(self, 'calculo_actual'):
            del self.calculo_actual

    def cargar_historial(self):
        """Carga el historial de pagos"""
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Crear tabla si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pago_nomina (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo_empleado TEXT NOT NULL,
                        fecha_pago DATE DEFAULT CURRENT_DATE,
                        periodo_inicio DATE NOT NULL,
                        periodo_fin DATE NOT NULL,
                        dias_trabajados INTEGER NOT NULL,
                        salario_base REAL NOT NULL,
                        bonos REAL NOT NULL,
                        deducciones REAL NOT NULL,
                        total_pagado REAL NOT NULL,
                        estado TEXT DEFAULT 'Pagado',
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    SELECT p.id, p.fecha_pago, e.nombres || ' ' || e.apellidos,
                           COALESCE(f.nombre, 'Sin Finca') as finca_nombre,
                           p.periodo_inicio || ' a ' || p.periodo_fin, p.dias_trabajados,
                           p.salario_base, p.bonos, p.deducciones, p.total_pagado, p.estado
                    FROM pago_nomina p
                    JOIN empleado e ON p.codigo_empleado = e.codigo
                    LEFT JOIN finca f ON e.id_finca = f.id
                    WHERE p.estado != 'Anulado'
                    ORDER BY p.fecha_pago DESC
                """)

                for row in cursor.fetchall():
                    self.tabla_historial.insert("", "end", values=(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        f"${row[6]:,.0f}",
                        f"${row[7]:,.0f}",
                        f"${row[8]:,.0f}",
                        f"${row[9]:,.0f}",
                        row[10]
                    ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial:\n{e}")

    def aplicar_filtros_historial(self):
        """Aplica filtros al historial de pagos"""
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Construir consulta base
                query = """
                    SELECT p.id, p.fecha_pago, e.nombres || ' ' || e.apellidos,
                           COALESCE(f.nombre, 'Sin Finca') as finca_nombre,
                           p.periodo_inicio || ' a ' || p.periodo_fin, p.dias_trabajados,
                           p.salario_base, p.bonos, p.deducciones, p.total_pagado, p.estado
                    FROM pago_nomina p
                    JOIN empleado e ON p.codigo_empleado = e.codigo
                    LEFT JOIN finca f ON e.id_finca = f.id
                    WHERE p.estado != 'Anulado'
                """
                
                params = []
                
                # Filtro por empleado
                empleado_filtro = self.combo_filtro_empleado.get()
                if empleado_filtro != "Todos los empleados":
                    codigo = empleado_filtro.split(" - ")[0]
                    query += " AND e.codigo = ?"
                    params.append(codigo)
                
                # Filtro por finca
                finca_filtro = self.combo_filtro_finca_historial.get()
                if finca_filtro != "Todas las fincas":
                    query += " AND f.nombre = ?"
                    params.append(finca_filtro)
                
                # Filtro por mes
                mes_filtro = self.combo_filtro_mes.get()
                if mes_filtro != "Todos":
                    meses = {"Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
                            "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
                            "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"}
                    mes_num = meses[mes_filtro]
                    query += " AND strftime('%m', p.fecha_pago) = ?"
                    params.append(mes_num)
                
                query += " ORDER BY p.fecha_pago DESC"
                
                cursor.execute(query, params)
                
                for row in cursor.fetchall():
                    self.tabla_historial.insert("", "end", values=(
                        row[0], row[1], row[2], row[3], row[4], row[5],
                        f"${row[6]:,.0f}", f"${row[7]:,.0f}",
                        f"${row[8]:,.0f}", f"${row[9]:,.0f}", row[10]
                    ))
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron aplicar los filtros:\n{e}")
        messagebox.showinfo("Info", "Los filtros se implementarán en una versión futura")

    def ver_detalle_pago(self):
        """Muestra el detalle completo de un pago seleccionado"""
        seleccionado = self.tabla_historial.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un pago para ver el detalle")
            return

        pago_id = self.tabla_historial.item(seleccionado[0])["values"][0]
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.*, e.nombres || ' ' || e.apellidos as empleado_nombre,
                           e.codigo, e.cargo, COALESCE(f.nombre, 'Sin Finca') as finca_nombre
                    FROM pago_nomina p
                    JOIN empleado e ON p.codigo_empleado = e.codigo
                    LEFT JOIN finca f ON e.id_finca = f.id
                    WHERE p.id = ?
                """, (pago_id,))
                
                pago = cursor.fetchone()
                if not pago:
                    messagebox.showerror("Error", "No se encontró el pago")
                    return
                
                # Crear ventana modal
                ventana = ctk.CTkToplevel(self)
                ventana.title(f"📄 Detalle de Pago - ID: {pago_id}")
                ventana.geometry("700x600")
                ventana.transient(self)
                ventana.grab_set()
                
                # Frame con scroll
                scroll_frame = ctk.CTkScrollableFrame(ventana)
                scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Título
                ctk.CTkLabel(
                    scroll_frame,
                    text=f"💰 Detalle del Pago #{pago_id}",
                    font=("Segoe UI", 22, "bold"),
                    text_color=self._sel
                ).pack(pady=(0, 20))
                
                # Información del empleado
                info_emp_frame = ctk.CTkFrame(scroll_frame, fg_color=self._fg_card)
                info_emp_frame.pack(fill="x", pady=10)
                
                ctk.CTkLabel(
                    info_emp_frame,
                    text="👤 INFORMACIÓN DEL EMPLEADO",
                    font=("Segoe UI", 14, "bold")
                ).pack(anchor="w", padx=15, pady=(10, 5))
                
                detalles_emp = [
                    ("Código:", pago[13]),
                    ("Nombre:", pago[12]),
                    ("Cargo:", pago[14]),
                    ("Finca:", pago[15])
                ]
                
                for label, valor in detalles_emp:
                    frame = ctk.CTkFrame(info_emp_frame, fg_color="transparent")
                    frame.pack(fill="x", padx=15, pady=2)
                    ctk.CTkLabel(frame, text=label, font=("Segoe UI", 12, "bold"), width=120, anchor="w").pack(side="left")
                    ctk.CTkLabel(frame, text=str(valor), font=("Segoe UI", 12), anchor="w").pack(side="left")
                
                # Información del pago
                info_pago_frame = ctk.CTkFrame(scroll_frame, fg_color=self._fg_card)
                info_pago_frame.pack(fill="x", pady=10)
                
                ctk.CTkLabel(
                    info_pago_frame,
                    text="📅 INFORMACIÓN DEL PERÍODO",
                    font=("Segoe UI", 14, "bold")
                ).pack(anchor="w", padx=15, pady=(10, 5))
                
                detalles_periodo = [
                    ("Fecha de Pago:", pago[2]),
                    ("Período:", f"{pago[3]} a {pago[4]}"),
                    ("Días Trabajados:", pago[5]),
                    ("Estado:", pago[11])
                ]
                
                for label, valor in detalles_periodo:
                    frame = ctk.CTkFrame(info_pago_frame, fg_color="transparent")
                    frame.pack(fill="x", padx=15, pady=2)
                    ctk.CTkLabel(frame, text=label, font=("Segoe UI", 12, "bold"), width=150, anchor="w").pack(side="left")
                    ctk.CTkLabel(frame, text=str(valor), font=("Segoe UI", 12), anchor="w").pack(side="left")
                
                # Desglose financiero
                info_dinero_frame = ctk.CTkFrame(scroll_frame, fg_color=self._fg_card)
                info_dinero_frame.pack(fill="x", pady=10)
                
                ctk.CTkLabel(
                    info_dinero_frame,
                    text="💵 DESGLOSE FINANCIERO",
                    font=("Segoe UI", 14, "bold")
                ).pack(anchor="w", padx=15, pady=(10, 5))
                
                detalles_dinero = [
                    ("Salario Base:", f"${pago[6]:,.0f}", "green"),
                    ("Bonos:", f"${pago[7]:,.0f}", "green"),
                    ("Deducciones:", f"${pago[8]:,.0f}", "red"),
                    ("TOTAL PAGADO:", f"${pago[9]:,.0f}", "blue")
                ]
                
                for label, valor, color in detalles_dinero:
                    frame = ctk.CTkFrame(info_dinero_frame, fg_color="transparent")
                    frame.pack(fill="x", padx=15, pady=2)
                    ctk.CTkLabel(frame, text=label, font=("Segoe UI", 12, "bold"), width=150, anchor="w").pack(side="left")
                    ctk.CTkLabel(frame, text=valor, font=("Segoe UI", 14, "bold"), text_color=color, anchor="w").pack(side="left")
                
                # Botón cerrar
                ctk.CTkButton(
                    scroll_frame,
                    text="✖ Cerrar",
                    command=ventana.destroy,
                    width=150,
                    fg_color="gray",
                    hover_color="#555"
                ).pack(pady=20)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el detalle del pago:\n{e}")

    def exportar_empleados(self):
        """Exporta la lista de empleados a formato Excel o PDF"""
        from tkinter import filedialog
        from modules.utils.exportador_datos import exportar_tabla_treeview
        from pathlib import Path
        
        # Preguntar formato
        ventana_formato = ctk.CTkToplevel(self)
        ventana_formato.title("Exportar Empleados")
        ventana_formato.geometry("400x200")
        ventana_formato.transient(self)
        ventana_formato.grab_set()
        
        ctk.CTkLabel(ventana_formato, text="Seleccione el formato de exportación:", 
                    font=("Segoe UI", 14, "bold")).pack(pady=5)
        
        formato_var = ctk.StringVar(value="excel")
        
        ctk.CTkRadioButton(ventana_formato, text="Excel (.xlsx)", variable=formato_var, 
                          value="excel").pack(pady=5)
        ctk.CTkRadioButton(ventana_formato, text="PDF (.pdf)", variable=formato_var, 
                          value="pdf").pack(pady=5)
        ctk.CTkRadioButton(ventana_formato, text="CSV (.csv)", variable=formato_var, 
                          value="csv").pack(pady=5)
        
        def confirmar_exportacion():
            ventana_formato.destroy()
            formato = formato_var.get()
            extension = {"excel": ".xlsx", "pdf": ".pdf", "csv": ".csv"}[formato]
            
            # Solicitar ubicación de archivo
            archivo = filedialog.asksaveasfilename(
                defaultextension=extension,
                filetypes=[(f"Archivo {formato.upper()}", f"*{extension}")],
                initialfile=f"empleados_{datetime.now().strftime('%Y%m%d')}{extension}"
            )
            
            if archivo:
                if exportar_tabla_treeview(self.tabla_empleados, Path(archivo), formato, "Lista de Empleados"):
                    messagebox.showinfo("Éxito", f"Empleados exportados correctamente a {archivo}")
                else:
                    messagebox.showerror("Error", "No se pudo exportar el archivo")
        
        ctk.CTkButton(ventana_formato, text="Exportar", command=confirmar_exportacion,
                     fg_color="#2E7D32", hover_color="#1B5E20").pack(pady=5)
    
    def anular_pago(self):
        """Anula un pago seleccionado"""
        seleccionado = self.tabla_historial.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un pago para anular")
            return

        pago_id = self.tabla_historial.item(seleccionado[0])["values"][0]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de anular el pago ID: {pago_id}?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE pago_nomina SET estado = 'Anulado' WHERE id = ?", (pago_id,))
                    conn.commit()
                
                messagebox.showinfo("Éxito", "Pago anulado correctamente")
                self.cargar_historial()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo anular el pago:\n{e}")

    # Tooltips ahora provienen de modules.utils.ui.add_tooltip