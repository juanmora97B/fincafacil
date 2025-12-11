import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sys
import os
from modules.utils.ui import add_tooltip
from modules.utils.logger import get_logger
from modules.utils.date_picker import attach_date_picker
from modules.utils.colores import obtener_colores
import csv
from io import StringIO
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None  # Gráficos deshabilitados si no está disponible

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class ReportesModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        # Colores y modo adaptativos
        self._modo = ctk.get_appearance_mode()
        self._fg_card = "#2B2B2B" if self._modo == "Dark" else "#F5F5F5"
        self._sel = "#1976D2" if self._modo == "Light" else "#1F538D"
        self._hover = "#90caf9" if self._modo == "Light" else "#14375E"
        # Colores del módulo
        self.color_bg, self.color_hover = obtener_colores('reportes')
        self.logger = get_logger("Reportes")
        # Rangos de fecha opcionales para filtros
        self._f_inicio = None
        self._f_fin = None
        # Filtros Inventario
        self._inv_sexo = None
        self._inv_estado = None
        self._inv_finca = None
        self._inv_raza = None
        # Filtros Potreros
        self._pot_finca = None
        self._pot_estado = None
        self._pot_ocup_min = None
        self.crear_widgets()

    def crear_widgets(self):
        # Título con color del módulo
        header = ctk.CTkFrame(self, fg_color=(self.color_bg, "#1a1a1a"), corner_radius=15)
        header.pack(fill="x", padx=15, pady=(10, 6))
        titulo = ctk.CTkLabel(header, text="📈 Reportes y Estadísticas", font=("Segoe UI", 22, "bold"), text_color="white")
        titulo.pack(side="left", anchor="w", padx=15, pady=10)
        add_tooltip(titulo, "Visualización y exportación de reportes del sistema")

        # Frame principal expandido
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=5, pady=(3, 5))

        # Panel izquierdo - Selección de reportes
        left_panel = ctk.CTkFrame(main_frame, width=280)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        lbl_tipos = ctk.CTkLabel(
            left_panel,
            text="📋 Tipos de Reportes",
            font=("Segoe UI", 16, "bold"),
            text_color=self._sel
        )
        lbl_tipos.pack(pady=5)
        add_tooltip(lbl_tipos, "Seleccione el tipo de reporte a visualizar")

        # Lista de reportes
        reportes = [
            "📊 Resumen General",
            "🐄 Inventario de Animales", 
            "💰 Reporte de Ventas",
            "🏥 Tratamientos Realizados",
            "🌿 Estado de Potreros",
            "📅 Actividad Reciente",
            "👥 Reporte de Empleados",
            "📦 Movimiento de Lotes"
        ]

        self.reportes_listbox = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.reportes_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        self.reporte_seleccionado = None
        for i, reporte in enumerate(reportes):
            btn = ctk.CTkButton(
                self.reportes_listbox,
                text=reporte,
                width=240,
                height=40,
                command=lambda r=reporte: self.mostrar_reporte(r),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                border_width=1,
                border_color=("gray70", "gray30")
            )
            btn.pack(pady=3)
            add_tooltip(btn, f"Abrir {reporte}")

        # Panel derecho - Área de reporte
        self.report_area = ctk.CTkFrame(main_frame)
        self.report_area.pack(side="right", fill="both", expand=True)

        # Mostrar reporte inicial
        self.mostrar_reporte("📊 Resumen General")

    def mostrar_reporte(self, tipo_reporte):
        """Muestra el reporte seleccionado"""
        # Limpiar área de reporte
        for widget in self.report_area.winfo_children():
            widget.destroy()

        # Frame para el título y botones
        header_frame = ctk.CTkFrame(self.report_area, fg_color="transparent")
        header_frame.pack(fill="x", padx=4, pady=10)

        # Título del reporte
        titulo_reporte = ctk.CTkLabel(
            header_frame,
            text=tipo_reporte,
            font=("Segoe UI", 18, "bold"),
            text_color=self._sel
        )
        titulo_reporte.pack(side="left")

        # Botones de acción
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        btn_export = ctk.CTkButton(
            btn_frame,
            text="📄 Exportar CSV",
            command=lambda: self.exportar_reporte(tipo_reporte),
            width=120,
            fg_color=self._sel,
            hover_color=self._hover
        )
        btn_export.pack(side="left", padx=5)
        add_tooltip(btn_export, "Exportar el reporte actual a CSV")

        btn_refresh = ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar",
            command=lambda: self.actualizar_reporte(tipo_reporte),
            width=100,
            fg_color=self._sel,
            hover_color=self._hover
        )
        btn_refresh.pack(side="left", padx=5)
        add_tooltip(btn_refresh, "Actualizar datos del reporte")

        # Botón gráfico si matplotlib disponible y tipo admite
        if plt is not None and any(k in tipo_reporte for k in ["Inventario", "Ventas", "Tratamientos", "Potreros"]):
            btn_chart = ctk.CTkButton(
                btn_frame,
                text="📊 Ver Gráfico",
                command=lambda: self.ver_grafico(tipo_reporte),
                width=110,
                fg_color=self._sel,
                hover_color=self._hover
            )
            btn_chart.pack(side="left", padx=5)
            add_tooltip(btn_chart, "Mostrar gráfico resumido")

        # Filtros de fecha (aplican a reportes con dimensión temporal)
        soporta_fecha = any(k in tipo_reporte for k in ["Ventas", "Tratamientos", "Actividad"])
        filtro_frame = None
        if soporta_fecha:
            filtro_frame = ctk.CTkFrame(self.report_area)
            filtro_frame.pack(fill="x", padx=4, pady=(0, 10))
            ctk.CTkLabel(filtro_frame, text="Filtro por Fecha", font=("Segoe UI", 14, "bold")).pack(anchor="w")
            fila_fechas = ctk.CTkFrame(filtro_frame, fg_color="transparent")
            fila_fechas.pack(fill="x", pady=5)
            hoy = datetime.now().date()
            primer_dia_mes = hoy.replace(day=1)
            lbl_ini = ctk.CTkLabel(fila_fechas, text="Inicio:")
            lbl_ini.pack(side="left", padx=5)
            entry_inicio = ctk.CTkEntry(fila_fechas, width=140, placeholder_text="YYYY-MM-DD")
            entry_inicio.pack(side="left", padx=5)
            entry_inicio.insert(0, self._f_inicio or primer_dia_mes.strftime("%Y-%m-%d"))
            attach_date_picker(fila_fechas, entry_inicio)
            add_tooltip(entry_inicio, "Fecha inicial del rango")
            lbl_fin = ctk.CTkLabel(fila_fechas, text="Fin:")
            lbl_fin.pack(side="left", padx=5)
            entry_fin = ctk.CTkEntry(fila_fechas, width=140, placeholder_text="YYYY-MM-DD")
            entry_fin.pack(side="left", padx=5)
            entry_fin.insert(0, self._f_fin or hoy.strftime("%Y-%m-%d"))
            attach_date_picker(fila_fechas, entry_fin)
            add_tooltip(entry_fin, "Fecha final del rango")
            def aplicar_filtro():
                fi = entry_inicio.get().strip(); ff = entry_fin.get().strip(); fmt = "%Y-%m-%d"
                try:
                    fi_dt = datetime.strptime(fi, fmt).date(); ff_dt = datetime.strptime(ff, fmt).date()
                    if fi_dt > ff_dt:
                        messagebox.showwarning("Atención", "La fecha inicio no puede ser posterior a la fecha fin."); return
                    self._f_inicio = fi; self._f_fin = ff
                except Exception:
                    messagebox.showwarning("Atención", "Fechas inválidas. Use formato YYYY-MM-DD."); return
                self.actualizar_reporte(tipo_reporte)
            btn_aplicar = ctk.CTkButton(filtro_frame, text="Filtrar", command=aplicar_filtro, width=100, fg_color=self._sel, hover_color=self._hover)
            btn_aplicar.pack(anchor="e", pady=5)
            add_tooltip(btn_aplicar, "Aplicar filtro de fechas al reporte")
        # Filtros Inventario
        if "Inventario" in tipo_reporte:
            filtro_inv = ctk.CTkFrame(self.report_area)
            filtro_inv.pack(fill="x", padx=4, pady=(0, 10))
            ctk.CTkLabel(filtro_inv, text="Filtros Inventario", font=("Segoe UI", 14, "bold")).pack(anchor="w")
            fila_superior = ctk.CTkFrame(filtro_inv, fg_color="transparent")
            fila_superior.pack(fill="x", pady=(4, 2))
            fila_inferior = ctk.CTkFrame(filtro_inv, fg_color="transparent")
            fila_inferior.pack(fill="x", pady=(2, 6))

            # Sexo
            ctk.CTkLabel(fila_superior, text="Sexo", width=80).pack(side="left", padx=(4, 2))
            cb_sexo = ctk.CTkComboBox(fila_superior, width=140, values=["Todos", "Macho", "Hembra"], state="readonly")
            cb_sexo.set(self._inv_sexo or "Todos")
            cb_sexo.pack(side="left", padx=4)
            add_tooltip(cb_sexo, "Elige Macho, Hembra o Todos")

            # Estado
            ctk.CTkLabel(fila_superior, text="Estado", width=80).pack(side="left", padx=(14, 2))
            cb_estado = ctk.CTkComboBox(fila_superior, width=160, values=["Todos", "Activo", "Vendido", "Muerto"], state="readonly")
            cb_estado.set(self._inv_estado or "Todos")
            cb_estado.pack(side="left", padx=4)
            add_tooltip(cb_estado, "Activo, Vendido, Muerto o Todos")

            # Finca
            ctk.CTkLabel(fila_inferior, text="Finca", width=80).pack(side="left", padx=(4, 2))
            cb_finca = ctk.CTkComboBox(fila_inferior, width=220, state="readonly")
            fincas = self._cargar_fincas_lista()
            cb_finca.configure(values=["Todas"] + fincas)
            cb_finca.set(self._inv_finca or "Todas")
            cb_finca.pack(side="left", padx=4)
            add_tooltip(cb_finca, "Selecciona una finca o Todas")

            # Raza
            ctk.CTkLabel(fila_inferior, text="Raza", width=80).pack(side="left", padx=(14, 2))
            cb_raza = ctk.CTkComboBox(fila_inferior, width=220, state="readonly")
            razas = self._cargar_razas_lista()
            cb_raza.configure(values=["Todas"] + razas)
            cb_raza.set(self._inv_raza or "Todas")
            cb_raza.pack(side="left", padx=4)
            add_tooltip(cb_raza, "Selecciona una raza o Todas")

            def aplicar_inv():
                self._inv_sexo = None if cb_sexo.get() == "Todos" else cb_sexo.get()
                self._inv_estado = None if cb_estado.get() == "Todos" else cb_estado.get()
                self._inv_finca = None if cb_finca.get() == "Todas" else cb_finca.get()
                self._inv_raza = None if cb_raza.get() == "Todas" else cb_raza.get()
                self.actualizar_reporte(tipo_reporte)

            def limpiar_inv():
                cb_sexo.set("Todos")
                cb_estado.set("Todos")
                cb_finca.set("Todas")
                cb_raza.set("Todas")
                self._inv_sexo = None
                self._inv_estado = None
                self._inv_finca = None
                self._inv_raza = None
                self.logger.info("Filtros inventario limpiados")
                self.actualizar_reporte(tipo_reporte)

            btn_frame_inv = ctk.CTkFrame(filtro_inv, fg_color="transparent")
            btn_frame_inv.pack(anchor="e", pady=5)
            ctk.CTkButton(btn_frame_inv, text="Filtrar", width=100, command=aplicar_inv, fg_color=self._sel, hover_color=self._hover).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame_inv, text="Limpiar", width=100, command=limpiar_inv, fg_color="gray40", hover_color="gray50").pack(side="left")

        # Filtros Potreros
        if "Potreros" in tipo_reporte:
            filtro_pot = ctk.CTkFrame(self.report_area)
            # Reducir padding horizontal (20→10) en barra de filtros
            filtro_pot.pack(fill="x", padx=10, pady=(0, 10))
            ctk.CTkLabel(filtro_pot, text="Filtros Potreros", font=("Segoe UI", 14, "bold")).pack(anchor="w")
            fila2 = ctk.CTkFrame(filtro_pot, fg_color="transparent")
            fila2.pack(fill="x", pady=5)
            cb_pfinca = ctk.CTkComboBox(fila2, width=160)
            fincas = self._cargar_fincas_lista()
            cb_pfinca.configure(values=[""] + fincas)
            cb_pfinca.set(self._pot_finca or "")
            cb_pfinca.pack(side="left", padx=5)
            add_tooltip(cb_pfinca, "Filtrar por finca")
            cb_pestado = ctk.CTkComboBox(fila2, width=130, values=["", "Activo", "Inactivo"])
            cb_pestado.set(self._pot_estado or "")
            cb_pestado.pack(side="left", padx=5)
            add_tooltip(cb_pestado, "Filtrar por estado")
            entry_ocup = ctk.CTkEntry(fila2, width=120, placeholder_text="Ocupación >= %")
            if self._pot_ocup_min:
                entry_ocup.insert(0, str(self._pot_ocup_min))
            entry_ocup.pack(side="left", padx=5)
            add_tooltip(entry_ocup, "Filtrar por porcentaje mínimo de ocupación")

            def aplicar_pot():
                self._pot_finca = cb_pfinca.get() or None
                self._pot_estado = cb_pestado.get() or None
                val = entry_ocup.get().strip()
                try:
                    self._pot_ocup_min = float(val) if val else None
                except ValueError:
                    messagebox.showwarning("Atención", "Ocupación mínima debe ser numérica.")
                    return
                self.actualizar_reporte(tipo_reporte)

            ctk.CTkButton(filtro_pot, text="Filtrar", width=100, command=aplicar_pot, fg_color=self._sel, hover_color=self._hover).pack(anchor="e", pady=5)

        # Generar reporte según el tipo
        if "Resumen General" in tipo_reporte:
            self.generar_resumen_general()
        elif "Inventario" in tipo_reporte:
            self.generar_inventario()
        elif "Ventas" in tipo_reporte:
            self.generar_ventas()
        elif "Tratamientos" in tipo_reporte:
            self.generar_tratamientos()
        elif "Potreros" in tipo_reporte:
            self.generar_potreros()
        elif "Actividad" in tipo_reporte:
            self.generar_actividad()
        elif "Empleados" in tipo_reporte:
            self.generar_empleados()
        elif "Lotes" in tipo_reporte:
            self.generar_lotes()

    def generar_resumen_general(self):
        """Genera el reporte de resumen general"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Frame para las estadísticas
                stats_frame = ctk.CTkFrame(self.report_area)
                # Compactar margen horizontal principal (20→4)
                stats_frame.pack(fill="both", expand=True, padx=4, pady=10)

                # Estadísticas principales
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
                total_animales = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Vendido'")
                animales_vendidos = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Muerto'")
                animales_muertos = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM potrero WHERE estado = 'Activo'")
                total_potreros = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM animal WHERE sexo = 'Macho' AND estado = 'Activo'")
                machos = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM animal WHERE sexo = 'Hembra' AND estado = 'Activo'")
                hembras = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM empleado WHERE estado = 'Activo'")
                total_empleados = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM finca WHERE estado = 'Activo'")
                total_fincas = cursor.fetchone()[0]

                # Valor del inventario
                cursor.execute("SELECT COALESCE(SUM(precio_compra), 0) FROM animal WHERE estado = 'Activo'")
                valor_inventario = cursor.fetchone()[0]

                # Mostrar estadísticas
                info_text = f"""
📊 RESUMEN GENERAL DEL SISTEMA

🏠 FINCAS Y ESTRUCTURA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Fincas activas: {total_fincas}
• Potreros activos: {total_potreros}
• Empleados activos: {total_empleados}

🐄 INVENTARIO ANIMAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total animales activos: {total_animales}
   ├── Machos: {machos}
   └── Hembras: {hembras}
• Animales vendidos: {animales_vendidos}
• Animales muertos: {animales_muertos}
• Valor inventario: ${valor_inventario:,.0f}

📅 INFORMACIÓN DEL REPORTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Fecha generación: {datetime.now().strftime("%d/%m/%Y %H:%M")}
• Sistema: FincaFácil v1.0
                """

                label_info = ctk.CTkLabel(
                    stats_frame,
                    text=info_text,
                    font=("Consolas", 12),  # Fuetypewriter para mejor alineación
                    justify="left",
                    anchor="nw"
                )
                # Mantener algo de aire visual (padx 20→10)
                label_info.pack(pady=5, padx=10, fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte:\n{e}")

    def generar_inventario(self):
        """Genera el reporte de inventario de animales"""
        self._style_treeview()
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        # Compactar margen horizontal (20→4)
        main_frame.pack(fill="both", expand=True, padx=4, pady=10)
        
        # Mostrar resumen de filtros activos
        if any([self._inv_sexo, self._inv_estado, self._inv_finca, self._inv_raza]):
            filtros_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B", corner_radius=8)
            filtros_frame.pack(fill="x", padx=5, pady=(0, 10))
            filtros_text = "Filtros Activos: "
            if self._inv_finca:
                filtros_text += f"Finca: {self._inv_finca} | "
            if self._inv_sexo:
                filtros_text += f"Sexo: {self._inv_sexo} | "
            if self._inv_estado:
                filtros_text += f"Estado: {self._inv_estado} | "
            if self._inv_raza:
                filtros_text += f"Raza: {self._inv_raza}"
            ctk.CTkLabel(filtros_frame, text=filtros_text.rstrip(" | "), font=("Segoe UI", 11, "bold"), text_color="#FFC107").pack(padx=10, pady=8)
        
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)
        tabla = ttk.Treeview(
            table_frame,
            columns=("codigo", "nombre", "sexo", "raza", "fecha_nac", "potrero", "finca", "estado", "valor"),
            show="headings",
            height=15
        )
        columnas = [
            ("codigo", "Código", 80), ("nombre", "Nombre", 140), ("sexo", "Sexo", 70),
            ("raza", "Raza", 110), ("fecha_nac", "F. Nac.", 90), ("potrero", "Potrero", 110),
            ("finca", "Finca", 130), ("estado", "Estado", 90), ("valor", "Valor", 100)
        ]
        for col, heading, width in columnas:
            tabla.heading(col, text=heading); tabla.column(col, width=width, anchor="center")
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                where_parts = []; params = []
                if self._inv_sexo: where_parts.append("a.sexo = ?"); params.append(self._inv_sexo)
                if self._inv_estado: where_parts.append("a.estado = ?"); params.append(self._inv_estado)
                if self._inv_raza: where_parts.append("r.nombre = ?"); params.append(self._inv_raza)
                if self._inv_finca:
                    where_parts.append("a.id_finca IN (SELECT id FROM finca WHERE lower(trim(nombre)) = lower(trim(?)))")
                    params.append(self._inv_finca)
                where_clause = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
                query = f"""
                    SELECT a.codigo, COALESCE(a.nombre,'Sin nombre'), a.sexo, r.nombre, a.fecha_nacimiento,
                           p.nombre as potrero, a.estado, a.precio_compra, f.nombre as finca
                    FROM animal a
                    LEFT JOIN raza r ON a.raza_id = r.id
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    LEFT JOIN finca f ON a.id_finca = f.id
                    {where_clause}
                    ORDER BY a.estado, a.codigo
                """
                cursor.execute(query, params)
                resultados = cursor.fetchall()
                total_valor = 0; count = 0
                for row in resultados:
                    valor = row[7] or 0; total_valor += valor; count += 1
                    fecha_nac_val = row[4]
                    if hasattr(fecha_nac_val, "strftime"):
                        fecha_nac = fecha_nac_val.strftime("%d/%m/%Y")
                    else:
                        fecha_nac = fecha_nac_val or "-"
                    # row: codigo, nombre, sexo, raza, fecha_nac, potrero, estado, precio_compra, finca
                    tabla.insert("", "end", values=(row[0], row[1], row[2], row[3] or "-", fecha_nac, row[5] or "-", row[8] or "-", row[6], f"${valor:,.0f}"))
                if count == 0:
                    self.logger.warning(f"Inventario sin resultados con filtros: sexo={self._inv_sexo}, estado={self._inv_estado}, finca={self._inv_finca}, raza={self._inv_raza}")
                resumen_frame = ctk.CTkFrame(main_frame); resumen_frame.pack(fill="x", pady=10)
                rango_text = ""
                if any([self._inv_sexo, self._inv_estado, self._inv_finca, self._inv_raza]):
                    filtros_activos = [f for f in [self._inv_sexo, self._inv_estado, self._inv_finca, self._inv_raza] if f]
                    rango_text = " | Filtros: " + ", ".join(filtros_activos)
                cursor.execute("SELECT COUNT(*) FROM animal")
                total_animales = cursor.fetchone()[0]
                ctk.CTkLabel(resumen_frame, text=f"📊 Resumen: {count}/{total_animales} animales | Valor mostrado: ${total_valor:,.0f}{rango_text}", font=("Segoe UI", 12, "bold")).pack(pady=5)
        except Exception as e:
            self.logger.error(f"Error en inventario: {e}")
        tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_ventas(self):
        """Genera el reporte de ventas"""
        self._style_treeview()
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=4, pady=10)

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        tabla = ttk.Treeview(
            table_frame,
            columns=("fecha", "animal", "precio", "comprador", "motivo"),
            show="headings",
            height=15
        )

        columnas = [
            ("fecha", "Fecha", 100),
            ("animal", "Animal", 200),
            ("precio", "Precio", 100),
            ("comprador", "Comprador", 150),
            ("motivo", "Motivo", 150)
        ]

        for col, heading, width in columnas:
            tabla.heading(col, text=heading)
            tabla.column(col, width=width, anchor="center")

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='venta'")
                if cursor.fetchone():
                    # Construir filtro dinámico
                    params = []
                    where_clause = ""
                    if self._f_inicio and self._f_fin:
                        where_clause = "WHERE date(v.fecha) BETWEEN date(?) AND date(?)"
                        params.extend([self._f_inicio, self._f_fin])
                    query = f"""
                        SELECT 
                            v.fecha,
                            a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                            v.precio_total,
                            v.comprador,
                            v.motivo_venta
                        FROM venta v
                        JOIN animal a ON v.id_animal = a.id
                        {where_clause}
                        ORDER BY v.fecha DESC
                    """
                    cursor.execute(query, params)
                    total = 0
                    count = 0
                    for row in cursor.fetchall():
                        precio = row[2] or 0
                        total += precio
                        count += 1
                        fecha = row[0].strftime("%d/%m/%Y") if row[0] else "-"
                        tabla.insert("", "end", values=(
                            fecha, row[1], f"${precio:,.0f}", row[3] or "-", row[4] or "-"
                        ))
                    if count > 0:
                        resumen_frame = ctk.CTkFrame(main_frame)
                        resumen_frame.pack(fill="x", pady=10)
                        rango_text = "" if not (self._f_inicio and self._f_fin) else f" | Rango: {self._f_inicio} a {self._f_fin}"
                        ctk.CTkLabel(
                            resumen_frame,
                            text=f"💰 Total de Ventas: {count} transacciones | Monto total: ${total:,.0f}{rango_text}",
                            font=("Segoe UI", 12, "bold")
                        ).pack(pady=5)
                    else:
                        ctk.CTkLabel(
                            main_frame,
                            text="ℹ️ No hay ventas en el rango seleccionado" if (self._f_inicio and self._f_fin) else "ℹ️ No se encontraron registros de ventas",
                            font=("Segoe UI", 12)
                        ).pack(pady=5)
                else:
                    ctk.CTkLabel(
                        main_frame,
                        text="ℹ️ La tabla de ventas no existe aún",
                        font=("Segoe UI", 12)
                    ).pack(pady=5)
        except Exception as e:
            self.logger.error(f"Error en ventas: {e}")

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_tratamientos(self):
        """Genera el reporte de tratamientos"""
        self._style_treeview()
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=4, pady=10)

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        tabla = ttk.Treeview(
            table_frame,
            columns=("fecha", "animal", "diagnostico", "producto", "dosis", "veterinario"),
            show="headings",
            height=15
        )

        columnas = [
            ("fecha", "Fecha", 100),
            ("animal", "Animal", 150),
            ("diagnostico", "Diagnóstico", 150),
            ("producto", "Producto", 150),
            ("dosis", "Dosis", 100),
            ("veterinario", "Veterinario", 150)
        ]

        for col, heading, width in columnas:
            tabla.heading(col, text=heading)
            tabla.column(col, width=width, anchor="center")

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tratamiento'")
                if cursor.fetchone():
                    params = []
                    where_clause = ""
                    if self._f_inicio and self._f_fin:
                        where_clause = "WHERE date(t.fecha_inicio) BETWEEN date(?) AND date(?)"
                        params.extend([self._f_inicio, self._f_fin])
                    query = f"""
                        SELECT 
                            t.fecha_inicio,
                            a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                            d.descripcion,
                            t.producto,
                            t.dosis,
                            t.veterinario
                        FROM tratamiento t
                        JOIN animal a ON t.id_animal = a.id
                        LEFT JOIN diagnostico_veterinario d ON t.id_diagnostico = d.id
                        {where_clause}
                        ORDER BY t.fecha_inicio DESC
                    """
                    cursor.execute(query, params)
                    count = 0
                    for row in cursor.fetchall():
                        fecha = row[0].strftime("%d/%m/%Y") if row[0] else "-"
                        tabla.insert("", "end", values=(
                            fecha, row[1], row[2] or "-", row[3] or "-", 
                            row[4] or "-", row[5] or "-"
                        ))
                        count += 1
                    resumen_frame = ctk.CTkFrame(main_frame)
                    resumen_frame.pack(fill="x", pady=10)
                    rango_text = "" if not (self._f_inicio and self._f_fin) else f" | Rango: {self._f_inicio} a {self._f_fin}"
                    ctk.CTkLabel(
                        resumen_frame,
                        text=f"🏥 Total de tratamientos: {count}{rango_text}",
                        font=("Segoe UI", 12, "bold")
                    ).pack(pady=5)
                    if count == 0:
                        ctk.CTkLabel(
                            main_frame,
                            text="ℹ️ No hay tratamientos en el rango seleccionado" if (self._f_inicio and self._f_fin) else "ℹ️ No se encontraron registros de tratamientos",
                            font=("Segoe UI", 12)
                        ).pack(pady=10)
                else:
                    ctk.CTkLabel(
                        main_frame,
                        text="ℹ️ La tabla de tratamientos no existe aún",
                        font=("Segoe UI", 12)
                    ).pack(pady=5)
        except Exception as e:
            self.logger.error(f"Error en tratamientos: {e}")

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_potreros(self):
        """Genera el reporte de potreros"""
        self._style_treeview()
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=4, pady=10)

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        tabla = ttk.Treeview(
            table_frame,
            columns=("nombre", "finca", "sector", "area", "capacidad", "animales", "ocupacion", "pasto", "estado"),
            show="headings",
            height=15
        )

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                where_parts = []
                params = []
                if self._pot_finca:
                    where_parts.append("f.nombre = ?")
                    params.append(self._pot_finca)
                if self._pot_estado:
                    where_parts.append("p.estado = ?")
                    params.append(self._pot_estado)
                where_clause = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
                query = f"""
                    SELECT 
                        p.nombre,
                        f.nombre as finca,
                        p.sector,
                        p.area_hectareas,
                        p.capacidad_maxima,
                        p.tipo_pasto,
                        p.estado,
                        p.id
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    {where_clause}
                    ORDER BY f.nombre, p.nombre
                """
                cursor.execute(query, params)
                mostrados = 0
                for row in cursor.fetchall():
                    cursor.execute("SELECT COUNT(*) FROM animal WHERE id_potrero = ? AND estado = 'Activo'", (row[7],))
                    cantidad_animales = cursor.fetchone()[0]
                    capacidad = row[4] or 1
                    ocupacion = (cantidad_animales / capacidad) * 100 if capacidad > 0 else 0
                    if self._pot_ocup_min is not None and ocupacion < self._pot_ocup_min:
                        continue
                    area = f"{row[3]:.2f}" if row[3] else "-"
                    tabla.insert("", "end", values=(
                        row[0], row[1] or "-", row[2] or "-", area,
                        row[4] or "-", cantidad_animales, f"{ocupacion:.1f}%", row[5] or "-", row[6] or "Activo"
                    ))
                    mostrados += 1
                resumen_frame = ctk.CTkFrame(main_frame)
                resumen_frame.pack(fill="x", pady=10)
                filtros = []
                if self._pot_finca: filtros.append(self._pot_finca)
                if self._pot_estado: filtros.append(self._pot_estado)
                if self._pot_ocup_min is not None: filtros.append(f"Ocup ≥ {self._pot_ocup_min}%")
                filtros_text = " | Filtros: " + ", ".join(filtros) if filtros else ""
                ctk.CTkLabel(resumen_frame, text=f"🌿 Potreros mostrados: {mostrados}{filtros_text}", font=("Segoe UI", 12, "bold")).pack(pady=5)

        except Exception as e:
            self.logger.error(f"Error en potreros: {e}")

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_actividad(self):
        """Genera el reporte de actividad reciente"""
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=4, pady=10)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                info_text = "📅 ACTIVIDAD RECIENTE DEL SISTEMA\n\n"
                info_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

                # Determinar rango base
                rango_texto = "Últimos 30 días"
                cond_animales = "fecha_registro >= date('now', '-30 days')"
                cond_tratamientos = "fecha_inicio >= date('now', '-30 days')"
                cond_ventas = "fecha >= date('now', '-30 days')"
                params_anim = params_trat = params_ven = []
                if self._f_inicio and self._f_fin:
                    rango_texto = f"Rango {self._f_inicio} a {self._f_fin}"
                    cond_animales = "date(fecha_registro) BETWEEN date(?) AND date(?)"
                    cond_tratamientos = "date(fecha_inicio) BETWEEN date(?) AND date(?)"
                    cond_ventas = "date(fecha) BETWEEN date(?) AND date(?)"
                    params_anim = params_trat = params_ven = [self._f_inicio, self._f_fin]

                # Animales registrados en rango
                cursor.execute(f"SELECT COUNT(*) FROM animal WHERE {cond_animales}", params_anim)
                nuevos_animales = cursor.fetchone()[0]
                info_text += f"🐄 Animales registrados ({rango_texto}): {nuevos_animales}\n\n"

                # Tratamientos en rango
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tratamiento'")
                if cursor.fetchone():
                    cursor.execute(f"SELECT COUNT(*) FROM tratamiento WHERE {cond_tratamientos}", params_trat)
                    tratamientos_recientes = cursor.fetchone()[0]
                    info_text += f"🏥 Tratamientos aplicados ({rango_texto}): {tratamientos_recientes}\n\n"

                # Ventas en rango
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='venta'")
                if cursor.fetchone():
                    cursor.execute(f"SELECT COUNT(*) FROM venta WHERE {cond_ventas}", params_ven)
                    ventas_recientes = cursor.fetchone()[0]
                    info_text += f"💰 Ventas realizadas ({rango_texto}): {ventas_recientes}\n\n"

                # Empleados activos
                cursor.execute("SELECT COUNT(*) FROM empleado WHERE estado = 'Activo'")
                empleados_activos = cursor.fetchone()[0]
                info_text += f"👥 Empleados activos: {empleados_activos}\n\n"

                info_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                info_text += f"📋 Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"

                label_info = ctk.CTkLabel(
                    main_frame,
                    text=info_text,
                    font=("Consolas", 12),
                    justify="left",
                    anchor="nw"
                )
                # Mantener algo de aire visual (padx 20→10)
                label_info.pack(pady=5, padx=10, fill="both", expand=True)

        except Exception as e:
            self.logger.error(f"Error en actividad: {e}")

    def generar_empleados(self):
        """Genera el reporte de empleados"""
        self._style_treeview()
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        # Compactar margen horizontal (20→4)
        main_frame.pack(fill="both", expand=True, padx=4, pady=10)

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        tabla = ttk.Treeview(
            table_frame,
            columns=("codigo", "nombre", "cargo", "fecha_ingreso", "salario", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 200),
            ("cargo", "Cargo", 150),
            ("fecha_ingreso", "F. Ingreso", 100),
            ("salario", "Salario Diario", 120),
            ("estado", "Estado", 100)
        ]

        for col, heading, width in columnas:
            tabla.heading(col, text=heading)
            tabla.column(col, width=width, anchor="center")

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        codigo, 
                        nombres || ' ' || apellidos as nombre,
                        cargo,
                        fecha_ingreso,
                        salario_diario,
                        estado_actual
                    FROM empleado
                    ORDER BY estado_actual, nombres
                """)

                total_salarios = 0
                for row in cursor.fetchall():
                    salario = row[4] or 0
                    total_salarios += salario
                    fecha_ing = row[3].strftime("%d/%m/%Y") if row[3] else "-"
                    tabla.insert("", "end", values=(
                        row[0], row[1], row[2] or "-", fecha_ing, 
                        f"${salario:,.0f}", row[5] or "Activo"
                    ))

                # Resumen
                cursor.execute("SELECT COUNT(*) FROM empleado WHERE estado = 'Activo'")
                activos = cursor.fetchone()[0]
                
                resumen_frame = ctk.CTkFrame(main_frame)
                resumen_frame.pack(fill="x", pady=10)
                ctk.CTkLabel(
                    resumen_frame,
                    text=f"👥 Resumen: {activos} empleados activos | Nómina diaria: ${total_salarios:,.0f}",
                    font=("Segoe UI", 12, "bold")
                ).pack(pady=5)

        except Exception as e:
            self.logger.error(f"Error en empleados: {e}")

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_lotes(self):
        """Genera el reporte de lotes"""
        info_frame = ctk.CTkFrame(self.report_area)
        info_frame.pack(fill="both", expand=True, padx=4, pady=10)

        info_text = """
📦 REPORTE DE LOTES

ℹ️ Esta funcionalidad estará disponible en la próxima actualización.

Los lotes permiten agrupar animales por criterios específicos como:
• Peso
• Edad  
• Estado de salud
• Propósito (leche, carne, reproducción)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Características próximas:
• Gestión de lotes dinámicos
• Seguimiento de rendimiento por lote
• Reportes comparativos entre lotes
• Análisis de productividad
        """

        label_info = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Segoe UI", 12),
            justify="left",
            anchor="nw"
        )
        label_info.pack(pady=5, padx=10, fill="both", expand=True)

    def exportar_reporte(self, tipo_reporte):
        """Exporta el reporte actual a CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title=f"Exportar {tipo_reporte}"
            )
            if not filename:
                return
            # Preparar datos según reporte
            headers, rows = self._generar_dataset(tipo_reporte)
            if not rows:
                messagebox.showinfo("Exportación", "No hay datos para exportar con los filtros actuales.")
                return
            # Escritura con BOM para Excel
            with open(filename, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            messagebox.showinfo("Éxito", f"Reporte exportado correctamente ({len(rows)} filas).")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte:\n{e}")

    def _generar_dataset(self, tipo_reporte):
        """Devuelve (headers, rows) según tipo y filtros activos"""
        try:
            if "Inventario" in tipo_reporte:
                headers = ["Código", "Nombre", "Sexo", "Raza", "Fecha Nac", "Potrero", "Finca", "Estado", "Valor"]
                rows = []
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    where_parts = []
                    params = []
                    if self._inv_sexo:
                        where_parts.append("a.sexo = ?")
                        params.append(self._inv_sexo)
                    if self._inv_estado:
                        where_parts.append("a.estado = ?")
                        params.append(self._inv_estado)
                    if self._inv_raza:
                        where_parts.append("r.nombre = ?")
                        params.append(self._inv_raza)
                    if self._inv_finca:
                        where_parts.append("a.id_finca IN (SELECT id FROM finca WHERE lower(trim(nombre)) = lower(trim(?)))")
                        params.append(self._inv_finca)
                    where_clause = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
                    query = f"""
                        SELECT a.codigo, COALESCE(a.nombre,''), a.sexo, r.nombre, a.fecha_nacimiento, p.nombre, a.estado, a.precio_compra, f.nombre as finca
                        FROM animal a
                        LEFT JOIN raza r ON a.raza_id = r.id
                        LEFT JOIN potrero p ON a.id_potrero = p.id
                        LEFT JOIN finca f ON a.id_finca = f.id
                        {where_clause}
                        ORDER BY a.estado, a.codigo
                    """
                    cursor.execute(query, params)
                    for r in cursor.fetchall():
                        fecha_val = r[4]
                        if hasattr(fecha_val, "strftime"):
                            fecha = fecha_val.strftime('%Y-%m-%d')
                        else:
                            fecha = fecha_val or ''
                        rows.append([r[0], r[1], r[2], r[3] or '', fecha, r[5] or '', r[8] or '', r[6], r[7] or 0])
                return headers, rows
            if "Ventas" in tipo_reporte:
                headers = ["Fecha", "Animal", "Precio", "Comprador", "Motivo"]
                rows = []
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='venta'")
                    if not cursor.fetchone():
                        return headers, rows
                    where_clause = ""
                    params = []
                    if self._f_inicio and self._f_fin:
                        where_clause = "WHERE date(v.fecha) BETWEEN date(?) AND date(?)"
                        params = [self._f_inicio, self._f_fin]
                    query = f"""
                        SELECT v.fecha, a.codigo || ' - ' || COALESCE(a.nombre,''), v.precio_total, v.comprador, v.motivo_venta
                        FROM venta v JOIN animal a ON v.id_animal = a.id
                        {where_clause}
                        ORDER BY v.fecha DESC
                    """
                    cursor.execute(query, params)
                    for r in cursor.fetchall():
                        fecha = r[0].strftime('%Y-%m-%d') if r[0] else ''
                        rows.append([fecha, r[1], r[2] or 0, r[3] or '', r[4] or ''])
                return headers, rows
            if "Tratamientos" in tipo_reporte:
                headers = ["Fecha", "Animal", "Diagnóstico", "Producto", "Dosis", "Veterinario"]
                rows = []
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tratamiento'")
                    if not cursor.fetchone():
                        return headers, rows
                    where_clause = ""
                    params = []
                    if self._f_inicio and self._f_fin:
                        where_clause = "WHERE date(t.fecha_inicio) BETWEEN date(?) AND date(?)"
                        params = [self._f_inicio, self._f_fin]
                    query = f"""
                        SELECT t.fecha_inicio, a.codigo || ' - ' || COALESCE(a.nombre,''), d.descripcion, t.producto, t.dosis, t.veterinario
                        FROM tratamiento t
                        JOIN animal a ON t.id_animal = a.id
                        LEFT JOIN diagnostico_veterinario d ON t.id_diagnostico = d.id
                        {where_clause}
                        ORDER BY t.fecha_inicio DESC
                    """
                    cursor.execute(query, params)
                    for r in cursor.fetchall():
                        fecha = r[0].strftime('%Y-%m-%d') if r[0] else ''
                        rows.append([fecha, r[1], r[2] or '', r[3] or '', r[4] or '', r[5] or ''])
                return headers, rows
            if "Potreros" in tipo_reporte:
                headers = ["Potrero", "Finca", "Sector", "Área Ha", "Capacidad", "Animales", "Ocupación %", "Tipo Pasto", "Estado"]
                rows = []
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    where_parts = []
                    params = []
                    if self._pot_finca: where_parts.append("f.nombre = ?") or params.append(self._pot_finca)
                    if self._pot_estado: where_parts.append("p.estado = ?") or params.append(self._pot_estado)
                    where_clause = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
                    query = f"""
                        SELECT p.nombre, f.nombre, p.sector, p.area_hectareas, p.capacidad_maxima, p.tipo_pasto, p.estado, p.id
                        FROM potrero p LEFT JOIN finca f ON p.id_finca = f.id
                        {where_clause}
                        ORDER BY f.nombre, p.nombre
                    """
                    cursor.execute(query, params)
                    for r in cursor.fetchall():
                        cursor.execute("SELECT COUNT(*) FROM animal WHERE id_potrero = ? AND estado='Activo'", (r[7],))
                        cant = cursor.fetchone()[0]
                        cap = r[4] or 1
                        ocup = (cant / cap) * 100 if cap > 0 else 0
                        if self._pot_ocup_min is not None and ocup < self._pot_ocup_min:
                            continue
                        rows.append([r[0], r[1] or '', r[2] or '', f"{(r[3] or 0):.2f}", r[4] or 0, cant, f"{ocup:.1f}", r[5] or '', r[6] or 'Activo'])
                return headers, rows
            if "Actividad" in tipo_reporte:
                headers = ["Métrica", "Valor"]
                # Reutilizar texto mostrado ya calculado con nueva consulta
                rows = []
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    # Similar a generar_actividad pero resumido
                    cond_animales = "fecha_registro >= date('now','-30 days')"
                    params_anim = []
                    if self._f_inicio and self._f_fin:
                        cond_animales = "date(fecha_registro) BETWEEN date(?) AND date(?)"
                        params_anim = [self._f_inicio, self._f_fin]
                    cursor.execute(f"SELECT COUNT(*) FROM animal WHERE {cond_animales}", params_anim)
                    rows.append(["Animales registrados", cursor.fetchone()[0]])
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tratamiento'")
                    if cursor.fetchone():
                        cond_trat = "fecha_inicio >= date('now','-30 days')"
                        params_trat = []
                        if self._f_inicio and self._f_fin:
                            cond_trat = "date(fecha_inicio) BETWEEN date(?) AND date(?)"
                            params_trat = [self._f_inicio, self._f_fin]
                        cursor.execute(f"SELECT COUNT(*) FROM tratamiento WHERE {cond_trat}", params_trat)
                        rows.append(["Tratamientos aplicados", cursor.fetchone()[0]])
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='venta'")
                    if cursor.fetchone():
                        cond_ven = "fecha >= date('now','-30 days')"
                        params_ven = []
                        if self._f_inicio and self._f_fin:
                            cond_ven = "date(fecha) BETWEEN date(?) AND date(?)"
                            params_ven = [self._f_inicio, self._f_fin]
                        cursor.execute(f"SELECT COUNT(*) FROM venta WHERE {cond_ven}", params_ven)
                        rows.append(["Ventas realizadas", cursor.fetchone()[0]])
                return headers, rows
        except Exception as e:
            self.logger.error(f"Error generando dataset: {e}")
        return [], []

    def ver_grafico(self, tipo_reporte):
        if plt is None:
            messagebox.showwarning("Gráfico", "matplotlib no disponible.")
            return
        headers, rows = self._generar_dataset(tipo_reporte)
        if not rows:
            messagebox.showinfo("Gráfico", "No hay datos para graficar.")
            return
        win = ctk.CTkToplevel(self)
        win.title(f"Gráfico - {tipo_reporte}")
        win.geometry("640x480")
        # Crear figura según tipo
        fig, ax = plt.subplots(figsize=(6,4))
        if "Inventario" in tipo_reporte:
            # Layout profesional: 3 gráficos
            fig.set_size_inches(14, 6)
            gs = fig.add_gridspec(1, 3, width_ratios=[1.2, 1.2, 1])
            ax_sexo = fig.add_subplot(gs[0])
            ax_estado = fig.add_subplot(gs[1])
            ax_raza = fig.add_subplot(gs[2])

            sexo_counts = {}
            estado_counts = {}
            raza_counts = {}
            
            for r in rows:
                # r: codigo, nombre, sexo, raza, fecha_nac, potrero, finca, estado, valor
                sexo_counts[r[2]] = sexo_counts.get(r[2], 0) + 1
                estado_counts[r[7]] = estado_counts.get(r[7], 0) + 1
                raza = r[3] or "(Sin raza)"
                raza_counts[raza] = raza_counts.get(raza, 0) + 1

            # GRÁFICO 1: Barras por Sexo
            if sexo_counts:
                categorias_sexo = list(sexo_counts.keys())
                valores_sexo = [sexo_counts[c] for c in categorias_sexo]
                colores_sexo = ["#FF9800" if c == "Macho" else "#E91E63" for c in categorias_sexo]
                ax_sexo.bar(categorias_sexo, valores_sexo, color=colores_sexo, edgecolor='black', linewidth=1.5)
                ax_sexo.set_title("Inventario por Sexo", fontsize=12, fontweight='bold')
                ax_sexo.set_ylabel("Cantidad", fontweight='bold')
                ax_sexo.grid(axis='y', alpha=0.3)
                for i, v in enumerate(valores_sexo):
                    ax_sexo.text(i, v + 0.3, str(v), ha='center', fontweight='bold')
            else:
                ax_sexo.text(0.5, 0.5, "Sin datos", ha='center', va='center')

            # GRÁFICO 2: Barras por Estado
            if estado_counts:
                categorias_estado = list(estado_counts.keys())
                valores_estado = [estado_counts[c] for c in categorias_estado]
                colores_estado = {"Activo": "#4CAF50", "Vendido": "#FF6F00", "Muerto": "#9C27B0", "Eliminado": "#616161"}
                colores = [colores_estado.get(c, "#2196F3") for c in categorias_estado]
                ax_estado.bar(categorias_estado, valores_estado, color=colores, edgecolor='black', linewidth=1.5)
                ax_estado.set_title("Inventario por Estado", fontsize=12, fontweight='bold')
                ax_estado.set_ylabel("Cantidad", fontweight='bold')
                ax_estado.grid(axis='y', alpha=0.3)
                ax_estado.tick_params(axis='x', rotation=15)
                for i, v in enumerate(valores_estado):
                    ax_estado.text(i, v + 0.3, str(v), ha='center', fontweight='bold')
            else:
                ax_estado.text(0.5, 0.5, "Sin datos", ha='center', va='center')

            # GRÁFICO 3: Pastel por Raza (top 8 + otros)
            if raza_counts:
                # Limitar a top 8 razas
                razas_top = dict(sorted(raza_counts.items(), key=lambda x: x[1], reverse=True)[:8])
                otras = sum(raza_counts.values()) - sum(razas_top.values())
                if otras > 0:
                    razas_top["Otras"] = otras
                
                labels = list(razas_top.keys())
                valores = list(razas_top.values())
                colores_pie = plt.cm.Set3(range(len(labels)))
                
                wedges, texts, autotexts = ax_raza.pie(valores, labels=labels, autopct='%1.1f%%', 
                                                         colors=colores_pie, startangle=90, textprops={'fontsize': 9})
                ax_raza.set_title("Distribución por Raza", fontsize=12, fontweight='bold')
                
                # Mejorar legibilidad de porcentajes
                for autotext in autotexts:
                    autotext.set_color('black')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(8)
            else:
                ax_raza.text(0.5, 0.5, "Sin datos", ha='center', va='center')

            fig.suptitle("Análisis de Inventario de Animales", fontsize=14, fontweight='bold', y=0.98)
            fig.tight_layout()
        elif "Ventas" in tipo_reporte:
            # Distribución por motivo
            motivo_idx = headers.index("Motivo")
            motivo_counts = {}
            for r in rows:
                motivo = r[motivo_idx] or "(Sin)"
                motivo_counts[motivo] = motivo_counts.get(motivo,0)+1
            categorias = list(motivo_counts.keys())
            valores = [motivo_counts[c] for c in categorias]
            ax.barh(categorias, valores, color="#388E3C")
            ax.set_title("Ventas por Motivo")
        elif "Tratamientos" in tipo_reporte:
            diag_idx = headers.index("Diagnóstico")
            diag_counts = {}
            for r in rows:
                d = r[diag_idx] or "(Sin)"
                diag_counts[d] = diag_counts.get(d,0)+1
            categorias = list(diag_counts.keys())[:15]
            valores = [diag_counts[c] for c in categorias]
            ax.barh(categorias, valores, color="#D32F2F")
            ax.set_title("Top Diagnósticos")
        elif "Potreros" in tipo_reporte:
            ocup_idx = headers.index("Ocupación %")
            pot_idx = headers.index("Potrero")
            categorias = [r[pot_idx] for r in rows][:20]
            valores = [float(r[ocup_idx]) for r in rows][:20]
            ax.bar(categorias, valores, color="#FFA000")
            ax.set_title("Ocupación Potreros (%)")
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5,0.5,"Tipo no soportado", ha='center', va='center')
        ax.grid(alpha=0.3)
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            self.logger.error(f"Error incrustando gráfico: {e}")
            plt.close(fig)
            messagebox.showerror("Gráfico", f"No se pudo mostrar el gráfico:\n{e}")

    def actualizar_reporte(self, tipo_reporte):
        """Actualiza el reporte actual"""
        self.mostrar_reporte(tipo_reporte)

    # _add_tooltip eliminado: ahora se usa add_tooltip centralizado desde modules.utils.ui

    def _style_treeview(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Treeview",
            background=self._fg_card,
            fieldbackground=self._fg_card,
            foreground="black" if self._modo == "Light" else "white",
            rowheight=28
        )
        style.map("Treeview", background=[('selected', self._sel)])

    # Helpers para cargar listas
    def _cargar_fincas_lista(self):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor(); cursor.execute("SELECT nombre FROM finca WHERE estado='Activo'");
                return [r[0] for r in cursor.fetchall() if r[0]]
        except Exception:
            return []

    def _cargar_razas_lista(self):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor(); cursor.execute("SELECT nombre FROM raza ORDER BY nombre");
                return [r[0] for r in cursor.fetchall() if r[0]]
        except Exception:
            return []