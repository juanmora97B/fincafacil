"""
Ventana de Gráficas Dinámicas
Panel profesional con matplotlib para análisis visual del inventario
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

try:
    from database import get_db_connection
except Exception:
    from database.database import get_db_connection


class VentanaGraficas(ctk.CTkToplevel):
    """Ventana de análisis con gráficas interactivas"""
    
    def __init__(self, master, filters_iniciales=None):
        super().__init__(master)
        
        self.filters = filters_iniciales or {}
        
        # Configuración ventana
        self.title("📊 Análisis Gráfico del Inventario")
        self.geometry("1400x900")
        self.grab_set()
        
        # Configurar matplotlib
        plt.rcParams['font.size'] = 9
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['axes.titlesize'] = 11
        plt.rcParams['figure.titlesize'] = 12
        
        self._build_ui()
        self._renderizar_graficos()
    
    def _build_ui(self):
        """Construir interfaz"""
        # Header
        header = ctk.CTkFrame(self, corner_radius=12, fg_color="#7c3aed")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="📊 Panel de Análisis Visual",
            font=("Segoe UI", 28, "bold"),
            text_color="white"
        ).pack(side="left", padx=25, pady=20)
        
        ctk.CTkButton(
            header,
            text="🔄 Actualizar",
            command=self._renderizar_graficos,
            width=130,
            height=38,
            corner_radius=8,
            font=("Segoe UI", 12, "bold"),
            fg_color="white",
            text_color="#7c3aed",
            hover_color="#e9d5ff"
        ).pack(side="right", padx=25, pady=20)
        
        # Filtros de gráficas
        filtros_frame = ctk.CTkFrame(self, corner_radius=12)
        filtros_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            filtros_frame,
            text="⚙️ Filtros de Análisis",
            font=("Segoe UI", 14, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=20, pady=(12, 8), sticky="w")
        
        # Fincas para comparar
        ctk.CTkLabel(
            filtros_frame,
            text="Finca 1:",
            font=("Segoe UI", 11, "bold")
        ).grid(row=1, column=0, padx=(20, 5), pady=8, sticky="w")
        
        self.cmb_finca1 = ctk.CTkComboBox(
            filtros_frame,
            width=200,
            height=34,
            corner_radius=8,
            font=("Segoe UI", 11)
        )
        self.cmb_finca1.grid(row=1, column=1, padx=5, pady=8)
        
        ctk.CTkLabel(
            filtros_frame,
            text="Finca 2 (comparar):",
            font=("Segoe UI", 11, "bold")
        ).grid(row=1, column=2, padx=(20, 5), pady=8, sticky="w")
        
        self.cmb_finca2 = ctk.CTkComboBox(
            filtros_frame,
            width=200,
            height=34,
            corner_radius=8,
            font=("Segoe UI", 11),
            values=["Ninguna"]
        )
        self.cmb_finca2.set("Ninguna")
        self.cmb_finca2.grid(row=1, column=3, padx=(5, 20), pady=8)
        
        # Rango de fechas
        ctk.CTkLabel(
            filtros_frame,
            text="Período:",
            font=("Segoe UI", 11, "bold")
        ).grid(row=2, column=0, padx=(20, 5), pady=(0, 12), sticky="w")
        
        self.cmb_periodo = ctk.CTkComboBox(
            filtros_frame,
            width=200,
            height=34,
            corner_radius=8,
            font=("Segoe UI", 11),
            values=["Último mes", "Últimos 3 meses", "Últimos 6 meses", "Último año", "Todo"],
            command=lambda x: self._renderizar_graficos()
        )
        self.cmb_periodo.set("Últimos 6 meses")
        self.cmb_periodo.grid(row=2, column=1, padx=5, pady=(0, 12))
        
        ctk.CTkLabel(
            filtros_frame,
            text="Categoría:",
            font=("Segoe UI", 11, "bold")
        ).grid(row=2, column=2, padx=(20, 5), pady=(0, 12), sticky="w")
        
        self.cmb_cat_grafico = ctk.CTkComboBox(
            filtros_frame,
            width=200,
            height=34,
            corner_radius=8,
            font=("Segoe UI", 11),
            values=["Todas", "Vaca", "Toro", "Novillo", "Ternero", "Vaquillona"]
        )
        self.cmb_cat_grafico.set("Todas")
        self.cmb_cat_grafico.grid(row=2, column=3, padx=(5, 20), pady=(0, 12))
        self.cmb_cat_grafico.configure(command=lambda *_: self._renderizar_graficos())

        # Filtro Sexo
        ctk.CTkLabel(
            filtros_frame,
            text="Sexo:",
            font=("Segoe UI", 11, "bold")
        ).grid(row=3, column=0, padx=(20, 5), pady=(0, 12), sticky="w")

        self.cmb_sexo_grafico = ctk.CTkComboBox(
            filtros_frame,
            width=200,
            height=34,
            corner_radius=8,
            font=("Segoe UI", 11),
            values=["Todos", "Macho", "Hembra"],
            command=lambda *_: self._renderizar_graficos()
        )
        self.cmb_sexo_grafico.set("Todos")
        self.cmb_sexo_grafico.grid(row=3, column=1, padx=5, pady=(0, 12))
        
        # Cargar fincas
        self._load_fincas()
        
        # Contenedor de gráficos con scroll
        self.cards_scroll = ctk.CTkScrollableFrame(self, corner_radius=12)
        self.cards_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def _load_fincas(self):
        """Cargar fincas disponibles"""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM finca ORDER BY nombre")
                fincas = cur.fetchall()
            
            values = [f"{f[0]} - {f[1]}" for f in fincas]
            self.cmb_finca1.configure(values=values)
            self.cmb_finca2.configure(values=["Ninguna"] + values)
            
            if values:
                # Seleccionar finca del filtro si existe
                if self.filters.get('finca_id'):
                    for val in values:
                        if str(self.filters['finca_id']) in val.split(' - ')[0]:
                            self.cmb_finca1.set(val)
                            break
                else:
                    self.cmb_finca1.set(values[0])
        except Exception as e:
            print(f"Error cargando fincas: {e}")
    
    def _get_fecha_rango(self):
        """Obtener rango de fechas según período seleccionado"""
        periodo = self.cmb_periodo.get()
        hoy = datetime.now()
        
        if periodo == "Último mes":
            inicio = hoy - timedelta(days=30)
        elif periodo == "Últimos 3 meses":
            inicio = hoy - timedelta(days=90)
        elif periodo == "Últimos 6 meses":
            inicio = hoy - timedelta(days=180)
        elif periodo == "Último año":
            inicio = hoy - timedelta(days=365)
        else:  # Todo
            inicio = datetime(2000, 1, 1)
        
        return inicio.strftime('%Y-%m-%d'), hoy.strftime('%Y-%m-%d')

    def _get_filters_sql(self):
        """Arma fragmentos WHERE y parámetros para filtros de categoría/sexo.
        Devuelve (clause, params) para anexar con 'AND ' + clause cuando corresponda."""
        clause_parts = []
        params = []
        cat = self.cmb_cat_grafico.get() if hasattr(self, 'cmb_cat_grafico') else 'Todas'
        sexo = self.cmb_sexo_grafico.get() if hasattr(self, 'cmb_sexo_grafico') else 'Todos'
        if cat and cat != 'Todas':
            clause_parts.append("a.categoria = ?")
            params.append(cat)
        if sexo and sexo != 'Todos':
            clause_parts.append("a.sexo = ?")
            params.append(sexo)
        if clause_parts:
            return " AND " + " AND ".join(clause_parts), params
        return "", []
    
    def _renderizar_graficos(self):
        """Renderizar todas las gráficas"""
        # Limpiar contenedor
        for widget in self.cards_scroll.winfo_children():
            widget.destroy()
        
        try:
            # Obtener finca seleccionada
            finca1_val = self.cmb_finca1.get()
            if not finca1_val or '-' not in finca1_val:
                self._show_error_message("Seleccione una finca")
                return
            
            finca1_id = int(finca1_val.split(' - ')[0])
            
            # Verificar segunda finca
            finca2_id = None
            finca2_val = self.cmb_finca2.get()
            if finca2_val and finca2_val != "Ninguna" and '-' in finca2_val:
                finca2_id = int(finca2_val.split(' - ')[0])
            
            # Helper para crear una card con un gráfico
            def add_chart_card(title, render_fn):
                card = ctk.CTkFrame(self.cards_scroll, corner_radius=10, border_width=1, border_color="#e5e7eb")
                card.pack(fill="x", padx=10, pady=8)
                ctk.CTkLabel(card, text=title, font=("Segoe UI", 14, "bold"), text_color="#1f2937").pack(anchor="w", padx=15, pady=(10, 0))
                fig_local = Figure(figsize=(10, 3.6), dpi=100, facecolor='white')
                ax = fig_local.add_subplot(111)
                render_fn(ax)
                fig_local.tight_layout()
                canvas = FigureCanvasTkAgg(fig_local, master=card)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="x", expand=True, padx=12, pady=10)

            add_chart_card("Distribución por Categorías", lambda ax: self._grafico_categorias(ax, finca1_id))
            add_chart_card("Distribución por Sexo", lambda ax: self._grafico_sexo(ax, finca1_id))
            add_chart_card("Ganancia/Pérdida de Peso (Acumulado)", lambda ax: self._grafico_peso_ganancia(ax, finca1_id))
            add_chart_card("Nacidos vs Comprados", lambda ax: self._grafico_nacidos_comprados(ax, finca1_id))
            add_chart_card("Muertes por Período", lambda ax: self._grafico_muertes(ax, finca1_id))
            if finca2_id:
                add_chart_card("Comparación entre Fincas", lambda ax: self._grafico_comparacion_fincas(ax, finca1_id, finca2_id))
            else:
                add_chart_card("Estado de Inventario", lambda ax: self._grafico_inventariado(ax, finca1_id))
            
        except Exception as e:
            self._show_error_message(f"Error renderizando gráficos:\n{e}")
            print(f"Error en _renderizar_graficos: {e}")
    
    def _grafico_categorias(self, ax, finca_id):
        """Gráfico pie: distribución por categorías"""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                clause, pars = self._get_filters_sql()
                sql = f"""
                    SELECT categoria, COUNT(*) 
                    FROM animal a
                    WHERE a.id_finca = ? AND a.categoria IS NOT NULL{clause}
                    GROUP BY categoria
                """
                cur.execute(sql, (finca_id, *pars))
                
                data = cur.fetchall()
            
            if not data:
                ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=14)
                ax.set_title('Distribución por Categorías')
                return
            
            labels = [row[0] for row in data]
            sizes = [row[1] for row in data]
            
            colors = plt.cm.Pastel1(np.linspace(0, 1, len(labels)))
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.set_title('Distribución por Categorías', fontweight='bold')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {str(e)[:30]}', ha='center', va='center', fontsize=10)
            ax.set_title('Distribución por Categorías')
    
    def _grafico_sexo(self, ax, finca_id):
        """Gráfico bar: machos vs hembras"""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                clause, pars = self._get_filters_sql()
                sql = f"""
                    SELECT a.sexo, COUNT(*) 
                    FROM animal a
                    WHERE a.id_finca = ?{clause}
                    GROUP BY a.sexo
                """
                cur.execute(sql, (finca_id, *pars))
                data = cur.fetchall()
            
            if not data:
                ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=14, 
                       transform=ax.transAxes)
                ax.set_title('Distribución por Sexo')
                return
            
            sexos = [row[0] for row in data]
            counts = [row[1] for row in data]
            
            colors = ['#3b82f6' if s == 'Macho' else '#ec4899' for s in sexos]
            
            bars = ax.bar(sexos, counts, color=colors, edgecolor='black', linewidth=1.2)
            ax.set_title('Distribución por Sexo', fontweight='bold')
            ax.set_ylabel('Cantidad')
            
            # Valores en barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontweight='bold')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {str(e)[:30]}', ha='center', va='center', 
                   fontsize=10, transform=ax.transAxes)
            ax.set_title('Distribución por Sexo')
    
    def _grafico_peso_ganancia(self, ax, finca_id):
        """Gráfico line: ganancia/pérdida de peso"""
        try:
            fecha_inicio, fecha_fin = self._get_fecha_rango()
            
            with get_db_connection() as conn:
                cur = conn.cursor()
                clause, pars = self._get_filters_sql()
                sql = f"""
                    SELECT 
                        r.fecha,
                        SUM(r.peso_nuevo - r.peso_anterior) as delta
                    FROM registro_peso r
                    JOIN animal a ON a.id = r.animal_id
                    WHERE a.id_finca = ? AND r.fecha BETWEEN ? AND ?{clause}
                    GROUP BY r.fecha
                    ORDER BY r.fecha
                """
                cur.execute(sql, (finca_id, fecha_inicio, fecha_fin, *pars))
                data = cur.fetchall()
            
            if not data:
                ax.text(0.5, 0.5, 'Sin registros de peso', ha='center', va='center', 
                       fontsize=12, transform=ax.transAxes)
                ax.set_title('Ganancia/Pérdida de Peso')
                return
            
            fechas = [datetime.strptime(row[0], '%Y-%m-%d') for row in data]
            deltas = [row[1] for row in data]
            
            # Acumulado
            deltas_acum = np.cumsum(deltas)
            
            ax.plot(fechas, deltas_acum, marker='o', linewidth=2, color='#10b981')
            ax.axhline(y=0, color='red', linestyle='--', linewidth=1)
            ax.set_title('Ganancia/Pérdida de Peso (Acumulado)', fontweight='bold')
            ax.set_xlabel('Fecha')
            ax.set_ylabel('Kg acumulados')
            ax.grid(True, alpha=0.3)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {str(e)[:30]}', ha='center', va='center', 
                   fontsize=10, transform=ax.transAxes)
            ax.set_title('Ganancia/Pérdida de Peso')
    
    def _grafico_nacidos_comprados(self, ax, finca_id):
        """Gráfico bar: nacidos vs comprados"""
        try:
            fecha_inicio, fecha_fin = self._get_fecha_rango()
            
            with get_db_connection() as conn:
                cur = conn.cursor()
                clause, pars = self._get_filters_sql()
                # Nacidos
                sql_nac = f"""
                    SELECT COUNT(*) 
                    FROM animal a
                    WHERE a.id_finca = ? 
                        AND a.fecha_nacimiento BETWEEN ? AND ?{clause}
                """
                cur.execute(sql_nac, (finca_id, fecha_inicio, fecha_fin, *pars))
                nacidos = cur.fetchone()[0]
                # Comprados (procedencia_id = 2 por convención)
                sql_comp = f"""
                    SELECT COUNT(*) 
                    FROM animal a
                    WHERE a.id_finca = ? 
                        AND a.procedencia_id = 2
                        AND a.fecha_nacimiento BETWEEN ? AND ?{clause}
                """
                cur.execute(sql_comp, (finca_id, fecha_inicio, fecha_fin, *pars))
                comprados = cur.fetchone()[0]
            
            categorias = ['Nacidos', 'Comprados']
            valores = [nacidos, comprados]
            colors = ['#22c55e', '#3b82f6']
            
            bars = ax.bar(categorias, valores, color=colors, edgecolor='black', linewidth=1.2)
            ax.set_title('Nacidos vs Comprados', fontweight='bold')
            ax.set_ylabel('Cantidad')
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontweight='bold')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {str(e)[:30]}', ha='center', va='center', 
                   fontsize=10, transform=ax.transAxes)
            ax.set_title('Nacidos vs Comprados')
    
    def _grafico_muertes(self, ax, finca_id):
        """Gráfico bar: muertes por período"""
        try:
            fecha_inicio, fecha_fin = self._get_fecha_rango()
            
            with get_db_connection() as conn:
                cur = conn.cursor()
                clause, pars = self._get_filters_sql()
                sql = f"""
                    SELECT strftime('%Y-%m', a.fecha_muerte) as mes, COUNT(*)
                    FROM animal a
                    WHERE a.id_finca = ?
                        AND a.fecha_muerte IS NOT NULL
                        AND a.fecha_muerte BETWEEN ? AND ?{clause}
                    GROUP BY mes
                    ORDER BY mes
                """
                cur.execute(sql, (finca_id, fecha_inicio, fecha_fin, *pars))
                data = cur.fetchall()
            
            if not data:
                ax.text(0.5, 0.5, 'Sin registros de muertes', ha='center', va='center', 
                       fontsize=12, transform=ax.transAxes)
                ax.set_title('Muertes por Período')
                return
            
            meses = [row[0] for row in data]
            counts = [row[1] for row in data]
            
            ax.bar(meses, counts, color='#ef4444', edgecolor='black', linewidth=1.2)
            ax.set_title('Muertes por Período', fontweight='bold')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Cantidad')
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
        except Exception as e:
            # Si no existe columna fecha_muerte, mostrar mensaje alternativo
            ax.text(0.5, 0.5, 'Columna no disponible', ha='center', va='center', 
                   fontsize=12, transform=ax.transAxes)
            ax.set_title('Muertes por Período')
    
    def _grafico_inventariado(self, ax, finca_id):
        """Gráfico pie: inventariados vs no inventariados"""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                clause, pars = self._get_filters_sql()
                sql = f"""
                    SELECT a.inventariado, COUNT(*) 
                    FROM animal a
                    WHERE a.id_finca = ?{clause}
                    GROUP BY a.inventariado
                """
                cur.execute(sql, (finca_id, *pars))
                data = cur.fetchall()
            
            if not data:
                ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=14)
                ax.set_title('Estado de Inventario')
                return
            
            labels = ['No Inventariado' if row[0] == 0 else 'Inventariado' for row in data]
            sizes = [row[1] for row in data]
            colors = ['#fbbf24', '#10b981']
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.set_title('Estado de Inventario', fontweight='bold')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {str(e)[:30]}', ha='center', va='center', fontsize=10)
            ax.set_title('Estado de Inventario')
    
    def _grafico_comparacion_fincas(self, ax, finca1_id, finca2_id):
        """Gráfico bar comparativo entre dos fincas"""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                clause, pars = self._get_filters_sql()
                sql = f"SELECT COUNT(*) FROM animal a WHERE a.id_finca = ?{clause}"
                cur.execute(sql, (finca1_id, *pars))
                total1 = cur.fetchone()[0]
                cur.execute(sql, (finca2_id, *pars))
                total2 = cur.fetchone()[0]
                
                # Nombres de fincas
                cur.execute("SELECT nombre FROM finca WHERE id = ?", (finca1_id,))
                nombre1 = cur.fetchone()[0]
                
                cur.execute("SELECT nombre FROM finca WHERE id = ?", (finca2_id,))
                nombre2 = cur.fetchone()[0]
            
            fincas = [nombre1[:15], nombre2[:15]]
            totales = [total1, total2]
            
            bars = ax.bar(fincas, totales, color=['#3b82f6', '#8b5cf6'], 
                         edgecolor='black', linewidth=1.2)
            ax.set_title('Comparación entre Fincas', fontweight='bold')
            ax.set_ylabel('Total Animales')
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontweight='bold')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {str(e)[:30]}', ha='center', va='center', 
                   fontsize=10, transform=ax.transAxes)
            ax.set_title('Comparación entre Fincas')
    
    def _show_error_message(self, message):
        """Mostrar mensaje de error en el canvas"""
        error_label = ctk.CTkLabel(
            self.cards_scroll,
            text=f"⚠️  {message}",
            font=("Segoe UI", 16),
            text_color="red"
        )
        error_label.pack(expand=True)
