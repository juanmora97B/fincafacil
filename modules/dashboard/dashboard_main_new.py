import customtkinter as ctk
from tkinter import ttk, messagebox
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

                # Actualizar gráficos
                self.actualizar_graficos(cursor)
                self.actualizar_actividad_reciente(cursor)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron actualizar las estadísticas:\n{e}")

    def actualizar_card(self, card, nuevo_valor):
        """Actualiza el valor de una card"""
        try:
            label_valor = card.winfo_children()[1]
            label_valor.configure(text=nuevo_valor)
        except:
            pass

    def actualizar_graficos(self, cursor):
        """Actualiza los gráficos de distribución y tendencias"""
        try:
            # Distribución de animales por estado
            cursor.execute("""
                SELECT estado, COUNT(*) as cantidad
                FROM animal
                GROUP BY estado
                ORDER BY cantidad DESC
            """)
            estados = []
            cantidades = []
            for estado, cantidad in cursor.fetchall():
                estados.append(estado)
                cantidades.append(cantidad)

            # Limpiar figura anterior
            self.figura_distribucion.clear()
            ax = self.figura_distribucion.add_subplot(111)
            
            # Crear gráfico de pastel
            colors = ['#2E7D32', '#1976D2', '#F57C00', '#C62828', '#6A1B9A']
            wedges, texts, autotexts = ax.pie(cantidades, labels=estados, autopct='%1.1f%%',
                                            colors=colors[:len(estados)])
            
            ax.set_title('Distribución de Animales por Estado')
            self.canvas_distribucion.draw()

            # Actualizar gráfico de tendencias
            cursor.execute("""
                SELECT strftime('%Y-%m', fecha_registro) as mes, COUNT(*) as cantidad
                FROM animal
                GROUP BY mes
                ORDER BY mes DESC
                LIMIT 12
            """)
            meses = []
            cant_por_mes = []
            for mes, cant in cursor.fetchall():
                meses.append(mes)
                cant_por_mes.append(cant)

            # Invertir para mostrar orden cronológico
            meses.reverse()
            cant_por_mes.reverse()

            # Limpiar figura anterior
            self.figura_tendencias.clear()
            ax = self.figura_tendencias.add_subplot(111)
            
            # Crear gráfico de línea
            ax.plot(meses, cant_por_mes, marker='o')
            ax.set_title('Tendencia de Crecimiento del Hato')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Cantidad de Animales')
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            self.figura_tendencias.tight_layout()
            self.canvas_tendencias.draw()

        except Exception as e:
            print(f"Error al actualizar gráficos: {e}")

    def actualizar_actividad_reciente(self, cursor):
        """Actualiza la tabla de actividad reciente"""
        for item in self.tabla_actividad.get_children():
            self.tabla_actividad.delete(item)

        try:
            # Obtener actividad reciente (últimos 7 días)
            cursor.execute("""
                SELECT fecha, accion, detalle
                FROM (
                    SELECT fecha_registro as fecha, 
                           'Registro Animal' as accion, 
                           ('Animal: ' || numero_arete) as detalle
                    FROM animal
                    WHERE fecha_registro >= date('now', '-7 days')
                    UNION ALL
                    SELECT fecha,
                           'Tratamiento' as accion,
                           ('Animal: ' || id_animal || ' - ' || descripcion) as detalle
                    FROM tratamiento
                    WHERE fecha >= date('now', '-7 days')
                    UNION ALL
                    SELECT fecha,
                           'Venta' as accion,
                           ('Cantidad: ' || cantidad || ' animales') as detalle
                    FROM venta
                    WHERE fecha >= date('now', '-7 days')
                )
                ORDER BY fecha DESC
                LIMIT 8
            """)
            
            for fecha, accion, detalle in cursor.fetchall():
                fecha_format = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
                self.tabla_actividad.insert("", "end", values=(fecha_format, accion, detalle))

        except Exception as e:
            print(f"Error al actualizar actividad reciente: {e}")

    def nuevo_animal(self):
        """Abre el módulo de registro de animales"""
        try:
            from modules.animales.registro_animal import RegistroAnimalFrame
            for widget in self.master.winfo_children():
                widget.destroy()
            RegistroAnimalFrame(self.master)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el registro de animales:\n{e}")

    def nuevo_tratamiento(self):
        """Abre el módulo de tratamientos"""
        try:
            from modules.tratamientos.tratamientos_main import TratamientosModule
            for widget in self.master.winfo_children():
                widget.destroy()
            TratamientosModule(self.master)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir tratamientos:\n{e}")

    def nuevo_registro(self):
        """Abre el módulo de bitácora"""
        try:
            from modules.animales.bitacora_comentarios import BitacoraComentariosFrame
            for widget in self.master.winfo_children():
                widget.destroy()
            BitacoraComentariosFrame(self.master)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la bitácora:\n{e}")