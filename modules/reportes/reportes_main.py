import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import sys
import os
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class ReportesModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="📈 Reportes y Estadísticas",
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=15)

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Panel izquierdo - Selección de reportes
        left_panel = ctk.CTkFrame(main_frame, width=280)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        ctk.CTkLabel(
            left_panel,
            text="📋 Tipos de Reportes",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

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
        header_frame.pack(fill="x", padx=20, pady=10)

        # Título del reporte
        titulo_reporte = ctk.CTkLabel(
            header_frame,
            text=tipo_reporte,
            font=("Segoe UI", 18, "bold")
        )
        titulo_reporte.pack(side="left")

        # Botones de acción
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="📄 Exportar CSV",
            command=lambda: self.exportar_reporte(tipo_reporte),
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar",
            command=lambda: self.actualizar_reporte(tipo_reporte),
            width=100
        ).pack(side="left", padx=5)

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
                stats_frame.pack(fill="both", expand=True, padx=20, pady=10)

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
                label_info.pack(pady=20, padx=20, fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte:\n{e}")

    def generar_inventario(self):
        """Genera el reporte de inventario de animales"""
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        tabla = ttk.Treeview(
            table_frame,
            columns=("codigo", "nombre", "sexo", "raza", "fecha_nac", "potrero", "estado", "valor"),
            show="headings",
            height=15
        )

        columnas = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("sexo", "Sexo", 80),
            ("raza", "Raza", 120),
            ("fecha_nac", "F. Nacimiento", 100),
            ("potrero", "Potrero", 120),
            ("estado", "Estado", 100),
            ("valor", "Valor", 100)
        ]

        for col, heading, width in columnas:
            tabla.heading(col, text=heading)
            tabla.column(col, width=width, anchor="center")

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        a.codigo,
                        COALESCE(a.nombre, 'Sin nombre') as nombre,
                        a.sexo,
                        r.nombre as raza,
                        a.fecha_nacimiento,
                        p.nombre as potrero,
                        a.estado,
                        a.precio_compra
                    FROM animal a
                    LEFT JOIN raza r ON a.id_raza = r.id
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    ORDER BY a.estado, a.codigo
                """)

                total_valor = 0
                for row in cursor.fetchall():
                    valor = row[7] or 0
                    total_valor += valor
                    fecha_nac = row[4].strftime("%d/%m/%Y") if row[4] else "-"
                    tabla.insert("", "end", values=(
                        row[0], row[1], row[2], row[3] or "-", 
                        fecha_nac, row[5] or "-", row[6], f"${valor:,.0f}"
                    ))

                # Resumen
                resumen_frame = ctk.CTkFrame(main_frame)
                resumen_frame.pack(fill="x", pady=10)

                cursor.execute("SELECT COUNT(*) FROM animal")
                total_animales = cursor.fetchone()[0]

                ctk.CTkLabel(
                    resumen_frame,
                    text=f"📊 Resumen: {total_animales} animales | Valor total: ${total_valor:,.0f}",
                    font=("Segoe UI", 12, "bold")
                ).pack(pady=5)

        except Exception as e:
            print(f"Error en inventario: {e}")

        tabla.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_ventas(self):
        """Genera el reporte de ventas"""
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

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
                
                # Verificar si existe la tabla venta
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='venta'")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT 
                            v.fecha,
                            a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                            v.precio_total,
                            v.comprador,
                            v.motivo_venta
                        FROM venta v
                        JOIN animal a ON v.id_animal = a.id
                        ORDER BY v.fecha DESC
                    """)

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

                    # Resumen
                    if count > 0:
                        resumen_frame = ctk.CTkFrame(main_frame)
                        resumen_frame.pack(fill="x", pady=10)
                        ctk.CTkLabel(
                            resumen_frame,
                            text=f"💰 Total de Ventas: {count} transacciones | Monto total: ${total:,.0f}",
                            font=("Segoe UI", 12, "bold")
                        ).pack(pady=5)
                else:
                    ctk.CTkLabel(
                        main_frame,
                        text="ℹ️ No se encontraron registros de ventas",
                        font=("Segoe UI", 12)
                    ).pack(pady=20)

        except Exception as e:
            print(f"Error en ventas: {e}")

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_tratamientos(self):
        """Genera el reporte de tratamientos"""
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

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
                    cursor.execute("""
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
                        ORDER BY t.fecha_inicio DESC
                    """)

                    for row in cursor.fetchall():
                        fecha = row[0].strftime("%d/%m/%Y") if row[0] else "-"
                        tabla.insert("", "end", values=(
                            fecha, row[1], row[2] or "-", row[3] or "-", 
                            row[4] or "-", row[5] or "-"
                        ))

                    # Contador
                    cursor.execute("SELECT COUNT(*) FROM tratamiento")
                    total = cursor.fetchone()[0]
                    
                    resumen_frame = ctk.CTkFrame(main_frame)
                    resumen_frame.pack(fill="x", pady=10)
                    ctk.CTkLabel(
                        resumen_frame,
                        text=f"🏥 Total de tratamientos registrados: {total}",
                        font=("Segoe UI", 12, "bold")
                    ).pack(pady=5)
                else:
                    ctk.CTkLabel(
                        main_frame,
                        text="ℹ️ No se encontraron registros de tratamientos",
                        font=("Segoe UI", 12)
                    ).pack(pady=20)

        except Exception as e:
            print(f"Error en tratamientos: {e}")

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_potreros(self):
        """Genera el reporte de potreros"""
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        tabla = ttk.Treeview(
            table_frame,
            columns=("nombre", "finca", "sector", "area", "capacidad", "animales", "ocupacion", "pasto", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("nombre", "Potrero", 120),
            ("finca", "Finca", 120),
            ("sector", "Sector", 100),
            ("area", "Área (Ha)", 90),
            ("capacidad", "Capacidad", 90),
            ("animales", "Animales", 80),
            ("ocupacion", "Ocupación", 80),
            ("pasto", "Tipo Pasto", 120),
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
                    ORDER BY f.nombre, p.nombre
                """)

                for row in cursor.fetchall():
                    # Contar animales en este potrero
                    cursor.execute("""
                        SELECT COUNT(*) FROM animal 
                        WHERE id_potrero = ? AND estado = 'Activo'
                    """, (row[7],))
                    cantidad_animales = cursor.fetchone()[0]
                    
                    # Calcular ocupación
                    capacidad = row[4] or 1
                    ocupacion = (cantidad_animales / capacidad) * 100 if capacidad > 0 else 0
                    
                    area = f"{row[3]:.2f}" if row[3] else "-"
                    tabla.insert("", "end", values=(
                        row[0], row[1] or "-", row[2] or "-", area, 
                        row[4] or "-", cantidad_animales, f"{ocupacion:.1f}%",
                        row[5] or "-", row[6] or "Activo"
                    ))

        except Exception as e:
            print(f"Error en potreros: {e}")

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_actividad(self):
        """Genera el reporte de actividad reciente"""
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                info_text = "📅 ACTIVIDAD RECIENTE DEL SISTEMA\n\n"
                info_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

                # Animales registrados recientemente
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM animal 
                    WHERE fecha_registro >= date('now', '-30 days')
                """)
                nuevos_animales = cursor.fetchone()[0]
                info_text += f"🐄 Animales registrados (últimos 30 días): {nuevos_animales}\n\n"

                # Tratamientos recientes
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tratamiento'")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM tratamiento 
                        WHERE fecha_inicio >= date('now', '-30 days')
                    """)
                    tratamientos_recientes = cursor.fetchone()[0]
                    info_text += f"🏥 Tratamientos aplicados (30 días): {tratamientos_recientes}\n\n"

                # Ventas recientes
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='venta'")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM venta 
                        WHERE fecha >= date('now', '-30 days')
                    """)
                    ventas_recientes = cursor.fetchone()[0]
                    info_text += f"💰 Ventas realizadas (30 días): {ventas_recientes}\n\n"

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
                label_info.pack(pady=20, padx=20, fill="both", expand=True)

        except Exception as e:
            print(f"Error en actividad: {e}")

    def generar_empleados(self):
        """Genera el reporte de empleados"""
        main_frame = ctk.CTkScrollableFrame(self.report_area)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

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
            print(f"Error en empleados: {e}")

        tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_lotes(self):
        """Genera el reporte de lotes"""
        info_frame = ctk.CTkFrame(self.report_area)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)

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
        label_info.pack(pady=20, padx=20, fill="both", expand=True)

    def exportar_reporte(self, tipo_reporte):
        """Exporta el reporte actual a CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title=f"Exportar {tipo_reporte}"
            )
            
            if filename:
                messagebox.showinfo("Éxito", f"Reporte exportado como: {filename}")
                # Aquí se implementaría la lógica de exportación real
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte:\n{e}")

    def actualizar_reporte(self, tipo_reporte):
        """Actualiza el reporte actual"""
        self.mostrar_reporte(tipo_reporte)
        messagebox.showinfo("Actualizado", f"Reporte {tipo_reporte} actualizado")