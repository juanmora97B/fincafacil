import customtkinter as ctk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from tkinter import PhotoImage
import io

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.conexion import db


class DashboardModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.actualizar_estadisticas()

    def crear_widgets(self):
        # Título
        titulo_frame = ctk.CTkFrame(self, fg_color="transparent")
        titulo_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        titulo = ctk.CTkLabel(
            titulo_frame,
            text="📊 Dashboard - Resumen General",
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(side="left")
        
        btn_actualizar = ctk.CTkButton(
            titulo_frame,
            text="🔄 Actualizar",
            width=120,
            height=30,
            command=self.actualizar_estadisticas,
            font=("Segoe UI", 11)
        )
        btn_actualizar.pack(side="right")

        # Cards de estadísticas
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=20, pady=10)
        
        # Configurar grid para las cards
        for i in range(4):
            self.cards_frame.grid_columnconfigure(i, weight=1)

        # Cards de métricas
        self.card_animales = self.crear_card("🐄 Total Animales", "0", "#2E7D32", 0)
        self.card_potreros = self.crear_card("🌿 Potreros Activos", "0", "#1976D2", 1)
        self.card_ventas_mes = self.crear_card("💰 Ventas del Mes", "$0", "#F57C00", 2)
        self.card_tratamientos = self.crear_card("🏥 Tratamientos Pendientes", "0", "#C62828", 3)

        # Separador
        separador = ctk.CTkFrame(self, height=2, fg_color="gray")
        separador.pack(fill="x", padx=20, pady=15)

        # Sección de información detallada
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Configurar grid
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_rowconfigure(0, weight=1)

        # Panel izquierdo - Gráficos
        panel_izq = ctk.CTkFrame(info_frame)
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        panel_izq.grid_columnconfigure(0, weight=1)

        # Tabs para gráficos
        notebook = ttk.Notebook(panel_izq)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 1: Distribución de Animales
        tab_distribucion = ctk.CTkFrame(notebook)
        notebook.add(tab_distribucion, text="📊 Distribución")
        
        self.figura_distribucion = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas_distribucion = FigureCanvasTkAgg(self.figura_distribucion, tab_distribucion)
        self.canvas_distribucion.get_tk_widget().pack(fill="both", expand=True)

        # Tab 2: Tendencias
        tab_tendencias = ctk.CTkFrame(notebook)
        notebook.add(tab_tendencias, text="📈 Tendencias")
        
        self.figura_tendencias = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas_tendencias = FigureCanvasTkAgg(self.figura_tendencias, tab_tendencias)
        self.canvas_tendencias.get_tk_widget().pack(fill="both", expand=True)

        # Acciones Rápidas
        acciones_frame = ctk.CTkFrame(panel_izq)
        acciones_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(acciones_frame, text="🐄 Nuevo Animal", 
                     command=self.nuevo_animal).pack(side="left", padx=2, expand=True)
        ctk.CTkButton(acciones_frame, text="💉 Nuevo Tratamiento",
                     command=self.nuevo_tratamiento).pack(side="left", padx=2, expand=True)
        ctk.CTkButton(acciones_frame, text="📋 Nuevo Registro",
                     command=self.nuevo_registro).pack(side="left", padx=2, expand=True)

        # Panel derecho - Actividad reciente
        panel_der = ctk.CTkFrame(info_frame)
        panel_der.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        panel_der.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel_der,
            text="📅 Actividad Reciente",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        self.tabla_actividad = ttk.Treeview(
            panel_der,
            columns=("fecha", "accion", "detalle"),
            show="headings",
            height=8
        )
        self.tabla_actividad.heading("fecha", text="Fecha")
        self.tabla_actividad.heading("accion", text="Acción")
        self.tabla_actividad.heading("detalle", text="Detalle")
        self.tabla_actividad.column("fecha", width=100, anchor="center")
        self.tabla_actividad.column("accion", width=120, anchor="center")
        self.tabla_actividad.column("detalle", width=200, anchor="w")
        self.tabla_actividad.pack(fill="both", expand=True, padx=10, pady=10)

    def crear_card(self, titulo, valor, color, columna):
        """Crea una card de estadística"""
        card = ctk.CTkFrame(self.cards_frame, fg_color=color, corner_radius=12)
        card.grid(row=0, column=columna, sticky="ew", padx=5)
        
        label_titulo = ctk.CTkLabel(
            card,
            text=titulo,
            font=("Segoe UI", 12),
            text_color="white"
        )
        label_titulo.pack(pady=(15, 5), padx=15)

        label_valor = ctk.CTkLabel(
            card,
            text=valor,
            font=("Segoe UI", 28, "bold"),
            text_color="white"
        )
        label_valor.pack(pady=(0, 15), padx=15)
        
        return card

    def actualizar_estadisticas(self):
        """Actualiza todas las estadísticas del dashboard"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Total de animales
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
                total_animales = cursor.fetchone()[0]

                # Potreros activos
                cursor.execute("SELECT COUNT(*) FROM potrero WHERE estado = 'Activo'")
                total_potreros = cursor.fetchone()[0]

                # Ventas del mes (si existe la tabla)
                try:
                    cursor.execute("""
                        SELECT COALESCE(SUM(precio_total), 0) 
                        FROM venta 
                        WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
                    """)
                    ventas_mes = cursor.fetchone()[0]
                except:
                    ventas_mes = 0

                # Tratamientos pendientes
                try:
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM tratamiento 
                        WHERE fecha_proxima IS NOT NULL 
                        AND fecha_proxima <= date('now', '+7 days')
                    """)
                    tratamientos_pendientes = cursor.fetchone()[0]
                except:
                    tratamientos_pendientes = 0

                # Actualizar cards
                self.actualizar_card(self.card_animales, str(total_animales))
                self.actualizar_card(self.card_potreros, str(total_potreros))
                self.actualizar_card(self.card_ventas_mes, f"${ventas_mes:,.0f}")
                self.actualizar_card(self.card_tratamientos, str(tratamientos_pendientes))

                # Distribución de animales por estado
                self.actualizar_distribucion_animales(cursor)

                # Actividad reciente
                self.actualizar_actividad_reciente(cursor)

        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")

    def actualizar_card(self, card, nuevo_valor):
        """Actualiza el valor de una card"""
        for widget in card.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("font")[1] == 28:
                widget.configure(text=nuevo_valor)
                break

    def actualizar_distribucion_animales(self, cursor):
        """Actualiza la tabla de distribución de animales"""
        # Limpiar tabla
        for item in self.tabla_animales.get_children():
            self.tabla_animales.delete(item)

        try:
            cursor.execute("""
                SELECT estado, COUNT(*) as cantidad
                FROM animal
                GROUP BY estado
                ORDER BY cantidad DESC
            """)
            
            for row in cursor.fetchall():
                self.tabla_animales.insert("", "end", values=row)
        except Exception as e:
            print(f"Error al cargar distribución: {e}")

    def actualizar_actividad_reciente(self, cursor):
        """Actualiza la tabla de actividad reciente"""
        # Limpiar tabla
        for item in self.tabla_actividad.get_children():
            self.tabla_actividad.delete(item)

        actividades = []

        try:
            # Animales registrados recientemente
            cursor.execute("""
                SELECT fecha_registro, 'Registro Animal', codigo || ' - ' || COALESCE(nombre, 'Sin nombre')
                FROM animal
                WHERE fecha_registro IS NOT NULL
                ORDER BY fecha_registro DESC
                LIMIT 5
            """)
            for row in cursor.fetchall():
                actividades.append(row)

            # Reubicaciones recientes
            cursor.execute("""
                SELECT fecha, 'Reubicación', potrero_anterior || ' → ' || potrero_nuevo
                FROM reubicacion
                ORDER BY fecha DESC
                LIMIT 5
            """)
            for row in cursor.fetchall():
                actividades.append(row)

            # Ordenar por fecha y mostrar las 5 más recientes
            actividades.sort(key=lambda x: x[0] if x[0] else "", reverse=True)
            for act in actividades[:5]:
                self.tabla_actividad.insert("", "end", values=act)

        except Exception as e:
            print(f"Error al cargar actividad: {e}")

