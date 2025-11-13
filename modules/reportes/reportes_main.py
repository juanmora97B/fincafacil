import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.conexion import db


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
        left_panel = ctk.CTkFrame(main_frame, width=250)
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
            "📅 Actividad Reciente"
        ]

        self.reportes_listbox = ctk.CTkFrame(left_panel, fg_color="transparent")
        self.reportes_listbox.pack(fill="both", expand=True, padx=10)

        self.reporte_seleccionado = None
        for i, reporte in enumerate(reportes):
            btn = ctk.CTkButton(
                self.reportes_listbox,
                text=reporte,
                width=220,
                height=40,
                command=lambda r=reporte: self.mostrar_reporte(r),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
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

        # Título del reporte
        titulo_reporte = ctk.CTkLabel(
            self.report_area,
            text=tipo_reporte,
            font=("Segoe UI", 18, "bold")
        )
        titulo_reporte.pack(pady=15)

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

    def generar_resumen_general(self):
        """Genera el reporte de resumen general"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Frame para las estadísticas
                stats_frame = ctk.CTkFrame(self.report_area)
                stats_frame.pack(fill="both", expand=True, padx=20, pady=10)

                # Estadísticas
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
                total_animales = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM potrero WHERE estado = 'Activo'")
                total_potreros = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM animal WHERE sexo = 'Macho' AND estado = 'Activo'")
                machos = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM animal WHERE sexo = 'Hembra' AND estado = 'Activo'")
                hembras = cursor.fetchone()[0]

                # Mostrar estadísticas
                info_text = f"""
📊 RESUMEN GENERAL DEL SISTEMA

🐄 Total de Animales Activos: {total_animales}
   • Machos: {machos}
   • Hembras: {hembras}

🌿 Potreros Activos: {total_potreros}

📅 Fecha del Reporte: {datetime.now().strftime("%d/%m/%Y %H:%M")}
                """

                label_info = ctk.CTkLabel(
                    stats_frame,
                    text=info_text,
                    font=("Segoe UI", 14),
                    justify="left",
                    anchor="w"
                )
                label_info.pack(pady=20, padx=20)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte:\n{e}")

    def generar_inventario(self):
        """Genera el reporte de inventario"""
        table_frame = ctk.CTkFrame(self.report_area)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tabla = ttk.Treeview(
            table_frame,
            columns=("codigo", "nombre", "sexo", "raza", "potrero", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("sexo", "Sexo", 80),
            ("raza", "Raza", 120),
            ("potrero", "Potrero", 120),
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
                        a.codigo,
                        COALESCE(a.nombre, 'Sin nombre') as nombre,
                        a.sexo,
                        r.nombre as raza,
                        p.nombre as potrero,
                        a.estado
                    FROM animal a
                    LEFT JOIN raza r ON a.raza = r.nombre
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    ORDER BY a.codigo
                """)

                for row in cursor.fetchall():
                    tabla.insert("", "end", values=row)

        except Exception as e:
            print(f"Error: {e}")

        tabla.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_ventas(self):
        """Genera el reporte de ventas"""
        table_frame = ctk.CTkFrame(self.report_area)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tabla = ttk.Treeview(
            table_frame,
            columns=("fecha", "animal", "precio", "motivo"),
            show="headings",
            height=15
        )

        columnas = [
            ("fecha", "Fecha", 120),
            ("animal", "Animal", 200),
            ("precio", "Precio", 120),
            ("motivo", "Motivo", 150)
        ]

        for col, heading, width in columnas:
            tabla.heading(col, text=heading)
            tabla.column(col, width=width, anchor="center")

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        v.fecha,
                        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                        v.precio_total,
                        v.motivo_venta
                    FROM venta v
                    JOIN animal a ON v.id_animal = a.id
                    ORDER BY v.fecha DESC
                """)

                total = 0
                for row in cursor.fetchall():
                    precio = row[2] or 0
                    total += precio
                    tabla.insert("", "end", values=(
                        row[0], row[1], f"${precio:,.0f}", row[3] or "-"
                    ))

                # Mostrar total
                total_label = ctk.CTkLabel(
                    self.report_area,
                    text=f"💰 Total de Ventas: ${total:,.0f}",
                    font=("Segoe UI", 14, "bold")
                )
                total_label.pack(pady=10)

        except Exception as e:
            if "no such table" not in str(e).lower():
                print(f"Error: {e}")

        tabla.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_tratamientos(self):
        """Genera el reporte de tratamientos"""
        table_frame = ctk.CTkFrame(self.report_area)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tabla = ttk.Treeview(
            table_frame,
            columns=("fecha", "animal", "tipo", "producto"),
            show="headings",
            height=15
        )

        columnas = [
            ("fecha", "Fecha", 120),
            ("animal", "Animal", 200),
            ("tipo", "Tipo", 150),
            ("producto", "Producto", 200)
        ]

        for col, heading, width in columnas:
            tabla.heading(col, text=heading)
            tabla.column(col, width=width, anchor="center")

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        t.fecha,
                        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                        t.tipo_tratamiento,
                        t.producto
                    FROM tratamiento t
                    JOIN animal a ON t.id_animal = a.id
                    ORDER BY t.fecha DESC
                """)

                for row in cursor.fetchall():
                    tabla.insert("", "end", values=row)

        except Exception as e:
            if "no such table" not in str(e).lower():
                print(f"Error: {e}")

        tabla.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_potreros(self):
        """Genera el reporte de potreros"""
        table_frame = ctk.CTkFrame(self.report_area)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tabla = ttk.Treeview(
            table_frame,
            columns=("nombre", "finca", "area", "capacidad", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("nombre", "Potrero", 150),
            ("finca", "Finca", 150),
            ("area", "Área (Ha)", 100),
            ("capacidad", "Capacidad", 100),
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
                        p.area_hectareas,
                        p.capacidad_maxima,
                        p.estado
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    ORDER BY p.nombre
                """)

                for row in cursor.fetchall():
                    area = f"{row[2]:.2f}" if row[2] else "-"
                    tabla.insert("", "end", values=(
                        row[0], row[1] or "-", area, row[3] or "-", row[4]
                    ))

        except Exception as e:
            print(f"Error: {e}")

        tabla.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def generar_actividad(self):
        """Genera el reporte de actividad reciente"""
        info_frame = ctk.CTkFrame(self.report_area)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)

        info_text = "📅 Actividad Reciente del Sistema\n\n"
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Animales registrados recientemente
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM animal 
                    WHERE fecha_registro >= date('now', '-30 days')
                """)
                nuevos = cursor.fetchone()[0]
                info_text += f"🐄 Animales registrados (últimos 30 días): {nuevos}\n"

                # Reubicaciones recientes
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM reubicacion 
                    WHERE fecha >= date('now', '-30 days')
                """)
                reubicaciones = cursor.fetchone()[0]
                info_text += f"🚚 Reubicaciones (últimos 30 días): {reubicaciones}\n"

        except Exception as e:
            info_text += f"\n⚠️ Error al cargar datos: {e}"

        label_info = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Segoe UI", 14),
            justify="left",
            anchor="w"
        )
        label_info.pack(pady=20, padx=20)

