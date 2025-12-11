import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3
import os, sys
from calendar import monthrange

# Importar matplotlib para gráficas
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from database import get_db_connection
from modules.utils.date_picker import attach_date_picker
from modules.utils.ui import add_tooltip
from modules.utils.colores import obtener_colores

class PesajeLecheFrame(ctk.CTkFrame):
    """
    Módulo profesional de gestión de producción de leche.
    Características:
    - Registro diario de pesaje por vaca y turno
    - Análisis y validación de producción
    - Comparativa mes anterior vs actual
    - Gráficas de producción por animal y total
    - Identificación de vacas con baja producción
    """
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Colores del módulo
        self.color_bg, self.color_hover = obtener_colores('leche')
        
        # Mapeos
        self._animal_map = {}  # 'codigo - nombre' -> id
        self._finca_map = {}   # 'nombre' -> id
        self._finca_id_actual = None
        
        # Configuración
        self.LIMITE_PRODUCCION_BAJA = 5.0  # Litros
        
        # Variables de estado para análisis
        self.datos_mes_actual = {}
        self.datos_mes_anterior = {}
        
        # UI
        self.crear_widgets()
        self.cargar_fincas_combo()
        self.cargar_animales_combo()
        self.actualizar_analisis()

    # ============================================================================
    # INTERFAZ GRÁFICA
    # ============================================================================
    def crear_widgets(self):
        """Crea la interfaz completa con pestañas"""
        # Header principal
        header = ctk.CTkFrame(self, fg_color=(self.color_bg, "#1a1a1a"), corner_radius=15)
        header.pack(fill="x", padx=15, pady=(10, 6))
        titulo = ctk.CTkLabel(header, text="🥛 Pesaje y Análisis de Producción de Leche", 
                             font=("Segoe UI", 20, "bold"), text_color="white")
        titulo.pack(side="left", anchor="w", padx=15, pady=10)
        add_tooltip(titulo, "Sistema profesional de gestión de producción lechera")

        # Notebook (pestañas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Registro
        self.tab_registro = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_registro, text="📝 Registro Diario")
        self._crear_tab_registro()
        
        # Tab 2: Análisis
        self.tab_analisis = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_analisis, text="📊 Análisis y Validación")
        self._crear_tab_analisis()
        
        # Tab 3: Comparativas
        self.tab_comparativas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_comparativas, text="📈 Comparativa de Meses")
        self._crear_tab_comparativas()
        
        # Tab 4: Gráficas
        self.tab_graficas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_graficas, text="📉 Gráficas")
        self._crear_tab_graficas()

    def _crear_tab_registro(self):
        """Pestaña de registro diario"""
        scroll = ctk.CTkScrollableFrame(self.tab_registro)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Formulario
        form_frame = ctk.CTkFrame(scroll)
        form_frame.pack(fill="x", pady=5)

        header_form = ctk.CTkLabel(form_frame, text="📝 Nuevo Registro de Pesaje", 
                                  font=("Segoe UI", 16, "bold"))
        header_form.pack(anchor="w", pady=(10, 2))
        helper = ctk.CTkLabel(form_frame, 
                             text="Campos con * son obligatorios. Registre los litros ordeñados en cada turno.",
                             font=("Segoe UI", 11, "italic"))
        helper.pack(anchor="w", pady=(0, 8))

        # Finca
        row0 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row0.pack(fill="x", pady=5)
        ctk.CTkLabel(row0, text="Finca *:", width=100).pack(side="left", padx=5)
        self.combo_finca = ctk.CTkComboBox(row0, width=280, command=self._on_finca_change)
        self.combo_finca.set("Seleccione la finca")
        self.combo_finca.pack(side="left", padx=5)
        add_tooltip(self.combo_finca, "Seleccione la finca para ver sus vacas")

        # Fecha y Animal
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Fecha *:", width=100).pack(side="left", padx=5)
        self.entry_fecha = ctk.CTkEntry(row1, width=140, placeholder_text="YYYY-MM-DD")
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(side="left", padx=5)
        attach_date_picker(row1, self.entry_fecha)
        add_tooltip(self.entry_fecha, "Fecha del ordeño")

        ctk.CTkLabel(row1, text="Vaca *:", width=100).pack(side="left", padx=5)
        self.combo_vaca = ctk.CTkComboBox(row1, width=280)
        self.combo_vaca.set("Seleccione la vaca")
        self.combo_vaca.pack(side="left", padx=5)
        add_tooltip(self.combo_vaca, "Seleccione la vaca a registrar")

        # Turnos
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Mañana (L):", width=120).pack(side="left", padx=5)
        self.entry_manana = ctk.CTkEntry(row2, width=100, placeholder_text="0.0")
        self.entry_manana.pack(side="left", padx=5)
        add_tooltip(self.entry_manana, "Litros ordeñados en la mañana")

        ctk.CTkLabel(row2, text="Tarde (L):", width=100).pack(side="left", padx=5)
        self.entry_tarde = ctk.CTkEntry(row2, width=100, placeholder_text="0.0")
        self.entry_tarde.pack(side="left", padx=5)
        add_tooltip(self.entry_tarde, "Litros ordeñados en la tarde")

        ctk.CTkLabel(row2, text="Noche (L):", width=100).pack(side="left", padx=5)
        self.entry_noche = ctk.CTkEntry(row2, width=100, placeholder_text="0.0")
        self.entry_noche.pack(side="left", padx=5)
        add_tooltip(self.entry_noche, "Litros ordeñados en la noche")

        # Observaciones
        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Observaciones:", width=120).pack(side="left", padx=5)
        self.text_obs = ctk.CTkTextbox(row3, width=400, height=70)
        self.text_obs.pack(side="left", padx=5, fill="x", expand=True)
        add_tooltip(self.text_obs, "Anote variaciones, problemas de salud, etc.")

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        ctk.CTkButton(btn_frame, text="💾 Guardar/Actualizar", fg_color="green", 
                     hover_color="#006400", command=self.guardar_registro).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🧹 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Refrescar", command=self.actualizar_analisis).pack(side="left", padx=5)

        # Listado de registros
        list_frame = ctk.CTkFrame(scroll)
        list_frame.pack(fill="both", expand=True, pady=10)
        header_list = ctk.CTkLabel(list_frame, text="📋 Últimos Registros (30 días)", 
                                  font=("Segoe UI", 14, "bold"))
        header_list.pack(anchor="w", pady=(10, 5))

        cols = ("id", "fecha", "animal", "total", "mañana", "tarde", "noche", "obs")
        self.tabla_registros = ttk.Treeview(list_frame, columns=cols, show="headings", 
                                           displaycolumns=("fecha", "animal", "total", "mañana", "tarde", "noche", "obs"),
                                           height=12)
        headings = {
            "id": "ID", "fecha": "Fecha", "animal": "Vaca", "total": "Total (L)",
            "mañana": "Mañana", "tarde": "Tarde", "noche": "Noche", "obs": "Observaciones"
        }
        widths = {
            "id": 50, "fecha": 90, "animal": 160, "total": 80,
            "mañana": 80, "tarde": 80, "noche": 80, "obs": 240
        }
        for c in cols:
            self.tabla_registros.heading(c, text=headings[c])
            self.tabla_registros.column(c, width=widths[c], anchor="center")
        
        self.tabla_registros.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tabla_registros.yview)
        self.tabla_registros.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_row = ctk.CTkFrame(list_frame, fg_color="transparent")
        action_row.pack(anchor="w", pady=5)
        ctk.CTkButton(action_row, text="🗑️ Eliminar Seleccionado", fg_color="red", 
                     hover_color="#8B0000", command=self.eliminar_registro).pack(side="left", padx=5)

    def _crear_tab_analisis(self):
        """Pestaña de análisis y validación de producción"""
        scroll = ctk.CTkScrollableFrame(self.tab_analisis)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Resumen del día actual
        frame_hoy = ctk.CTkFrame(scroll)
        frame_hoy.pack(fill="x", pady=5)
        
        header_hoy = ctk.CTkLabel(frame_hoy, text="📅 Análisis de Hoy", 
                                 font=("Segoe UI", 14, "bold"))
        header_hoy.pack(anchor="w", pady=5)
        
        # Info del día
        self.label_hoy_info = ctk.CTkLabel(frame_hoy, text="Seleccione una finca para ver análisis...", 
                                          font=("Segoe UI", 11), text_color="gray")
        self.label_hoy_info.pack(anchor="w", padx=10, pady=5)

        # Resumen del mes actual
        frame_mes = ctk.CTkFrame(scroll)
        frame_mes.pack(fill="x", pady=5)
        
        header_mes = ctk.CTkLabel(frame_mes, text="📊 Estadísticas del Mes Actual", 
                                 font=("Segoe UI", 14, "bold"))
        header_mes.pack(anchor="w", pady=5)
        
        self.label_mes_info = ctk.CTkLabel(frame_mes, text="Cargando...", 
                                          font=("Segoe UI", 10), justify="left")
        self.label_mes_info.pack(anchor="w", padx=10, pady=5)

        # Vacas con baja producción
        frame_bajos = ctk.CTkFrame(scroll)
        frame_bajos.pack(fill="both", expand=True, pady=5)
        
        header_bajos = ctk.CTkLabel(frame_bajos, 
                                   text=f"⚠️ Vacas con Baja Producción (<{self.LIMITE_PRODUCCION_BAJA}L promedio)", 
                                   font=("Segoe UI", 14, "bold"), text_color="#FF6B6B")
        header_bajos.pack(anchor="w", pady=5)

        cols_bajos = ("animal", "promedio", "dias", "ultimos_3")
        self.tabla_bajos = ttk.Treeview(frame_bajos, columns=cols_bajos, show="headings", height=10)
        headings_bajos = {
            "animal": "Vaca",
            "promedio": f"Promedio (L)",
            "dias": "Días registrados",
            "ultimos_3": "Últimos 3 días"
        }
        widths_bajos = {"animal": 200, "promedio": 120, "dias": 120, "ultimos_3": 120}
        
        for c in cols_bajos:
            self.tabla_bajos.heading(c, text=headings_bajos[c])
            self.tabla_bajos.column(c, width=widths_bajos[c], anchor="center")
        
        self.tabla_bajos.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_bajos = ttk.Scrollbar(frame_bajos, orient="vertical", command=self.tabla_bajos.yview)
        self.tabla_bajos.configure(yscroll=scrollbar_bajos.set)
        scrollbar_bajos.pack(side="right", fill="y")

    def _crear_tab_comparativas(self):
        """Pestaña de comparativa de meses"""
        scroll = ctk.CTkScrollableFrame(self.tab_comparativas)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Selector de animal
        filter_frame = ctk.CTkFrame(scroll)
        filter_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(filter_frame, text="Filtrar por vaca:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        self.combo_animal_comp = ctk.CTkComboBox(filter_frame, width=300, command=self.actualizar_comparativas)
        self.combo_animal_comp.set("Todas las vacas")
        self.combo_animal_comp.pack(side="left", padx=5)

        # Tabla comparativa
        frame_tabla = ctk.CTkFrame(scroll)
        frame_tabla.pack(fill="both", expand=True, pady=5)
        
        header_tabla = ctk.CTkLabel(frame_tabla, text="Comparativa Mes Anterior vs Actual", 
                                   font=("Segoe UI", 14, "bold"))
        header_tabla.pack(anchor="w", pady=5)

        cols_comp = ("animal", "mes_ant_dias", "mes_ant_total", "mes_ant_prom", 
                    "mes_act_dias", "mes_act_total", "mes_act_prom", "cambio")
        self.tabla_comparativa = ttk.Treeview(frame_tabla, columns=cols_comp, show="headings", height=15)
        
        headings_comp = {
            "animal": "Vaca",
            "mes_ant_dias": "Ant. Días",
            "mes_ant_total": "Ant. Total (L)",
            "mes_ant_prom": "Ant. Prom (L)",
            "mes_act_dias": "Act. Días",
            "mes_act_total": "Act. Total (L)",
            "mes_act_prom": "Act. Prom (L)",
            "cambio": "Cambio %"
        }
        widths_comp = {
            "animal": 200, "mes_ant_dias": 85, "mes_ant_total": 110, "mes_ant_prom": 110,
            "mes_act_dias": 85, "mes_act_total": 110, "mes_act_prom": 110, "cambio": 90
        }
        
        for c in cols_comp:
            self.tabla_comparativa.heading(c, text=headings_comp[c])
            self.tabla_comparativa.column(c, width=widths_comp[c], anchor="center")
        
        # Estilo para encabezados más visibles
        estilo = ttk.Style()
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), foreground="#2E7D32")
        
        self.tabla_comparativa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_comp = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_comparativa.yview)
        self.tabla_comparativa.configure(yscroll=scrollbar_comp.set)
        scrollbar_comp.pack(side="right", fill="y")

    def _crear_tab_graficas(self):
        """Pestaña de gráficas - Reorganizada con 3 combos"""
        if not MATPLOTLIB_AVAILABLE:
            label = ctk.CTkLabel(self.tab_graficas, 
                                text="⚠️ Matplotlib no está instalado.\nInstale con: pip install matplotlib",
                                font=("Segoe UI", 14))
            label.pack(pady=50)
            return

        scroll = ctk.CTkScrollableFrame(self.tab_graficas)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # ============ FILA 1: Tipo de DATO ============
        control_frame1 = ctk.CTkFrame(scroll)
        control_frame1.pack(fill="x", pady=5)
        
        ctk.CTkLabel(control_frame1, text="Datos a mostrar:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        
        self.combo_tipo_dato = ctk.CTkComboBox(control_frame1, width=280,
                                                 values=["Producción Total Diaria",
                                                        "Producción por Vaca",
                                                        "Baja Producción",
                                                        "Comparativa Meses",
                                                        "Producción por Turno"],
                                                 command=self.actualizar_graficas)
        self.combo_tipo_dato.set("Producción Total Diaria")
        self.combo_tipo_dato.pack(side="left", padx=5)

        # ============ FILA 2: Filtro de Vaca ============
        control_frame2 = ctk.CTkFrame(scroll)
        control_frame2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(control_frame2, text="Filtrar por vaca:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        self.combo_animal_grafica = ctk.CTkComboBox(control_frame2, width=280, command=self.actualizar_graficas)
        self.combo_animal_grafica.set("Todas las vacas")
        self.combo_animal_grafica.pack(side="left", padx=5)

        # ============ FILA 3: Tipo de VISUALIZACIÓN ============
        control_frame3 = ctk.CTkFrame(scroll)
        control_frame3.pack(fill="x", pady=5)
        
        ctk.CTkLabel(control_frame3, text="Tipo de gráfico:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        
        self.combo_tipo_visualizacion = ctk.CTkComboBox(control_frame3, width=280,
                                                 values=["Línea",
                                                        "Barras",
                                                        "Pastel",
                                                        "Columnas Apiladas",
                                                        "Combinada (Columnas+Línea)"],
                                                 command=self.actualizar_graficas)
        self.combo_tipo_visualizacion.set("Línea")
        self.combo_tipo_visualizacion.pack(side="left", padx=5)

        # Botón para refrescar
        ctk.CTkButton(control_frame3, text="🔄 Refrescar", 
                     command=self.actualizar_graficas).pack(side="left", padx=5)

        # Canvas para la gráfica
        self.frame_grafica = ctk.CTkFrame(scroll)
        self.frame_grafica.pack(fill="both", expand=True, pady=5)

    # ============================================================================
    # GESTIÓN DE DATOS
    # ============================================================================
    def cargar_fincas_combo(self):
        """Carga todas las fincas disponibles"""
        try:
            with get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM finca ORDER BY nombre")
                rows = cur.fetchall()
                self._finca_map = {}
                display = []
                for r in rows:
                    self._finca_map[r['nombre']] = r['id']
                    display.append(r['nombre'])
                self.combo_finca.configure(values=display)
                if display:
                    self.combo_finca.set(display[0])
                    self._finca_id_actual = self._finca_map[display[0]]
                else:
                    self.combo_finca.set("Sin fincas disponibles")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar fincas:\n{e}")

    def _on_finca_change(self, value):
        """Callback cuando cambia la finca seleccionada"""
        if value in self._finca_map:
            self._finca_id_actual = self._finca_map[value]
            self.cargar_animales_combo()
            self.actualizar_analisis()
        else:
            self._finca_id_actual = None
            self.combo_vaca.configure(values=[])
            self.combo_vaca.set("Seleccione la finca primero")

    def cargar_animales_combo(self):
        """Carga vacas de la finca seleccionada"""
        if not self._finca_id_actual:
            self.combo_vaca.configure(values=[])
            self.combo_vaca.set("Seleccione la finca primero")
            return
        try:
            with get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("""
                    SELECT a.id, a.codigo, COALESCE(a.nombre,'') AS nombre
                    FROM animal a
                    LEFT JOIN muerte m ON m.animal_id = a.id
                    WHERE a.sexo='Hembra' AND m.id IS NULL AND a.id_finca = ?
                    ORDER BY a.codigo
                """, (self._finca_id_actual,))
                rows = cur.fetchall()
                self._animal_map = {}
                display = []
                for r in rows:
                    label = f"{r['codigo']} - {r['nombre']}".strip().rstrip('- ')
                    self._animal_map[label] = r['id']
                    display.append(label)
                
                self.combo_vaca.configure(values=display)
                if display:
                    self.combo_vaca.set(display[0])
                else:
                    self.combo_vaca.set("Sin vacas disponibles")
                
                # Actualizar combos de comparativas y gráficas
                self.combo_animal_comp.configure(values=["Todas las vacas"] + display)
                self.combo_animal_comp.set("Todas las vacas")
                
                self.combo_animal_grafica.configure(values=["Todas las vacas"] + display)
                self.combo_animal_grafica.set("Todas las vacas")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar vacas:\n{e}")

    def guardar_registro(self):
        """Guarda un nuevo registro de pesaje"""
        finca_label = self.combo_finca.get().strip()
        if finca_label not in self._finca_map:
            messagebox.showwarning("Atención", "Debe seleccionar una finca válida.")
            return
        
        fecha = self.entry_fecha.get().strip()
        vaca_label = self.combo_vaca.get().strip()
        
        if not fecha:
            messagebox.showwarning("Atención", "La fecha es obligatoria.")
            return
        
        if vaca_label not in self._animal_map:
            messagebox.showwarning("Atención", "Debe seleccionar una vaca válida.")
            return
        
        # Validar formato de fecha
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Atención", "Formato de fecha inválido (use YYYY-MM-DD).")
            return

        animal_id = self._animal_map[vaca_label]
        
        # Parsear litros
        def parse_litros(val):
            val = (val or '').strip()
            if not val:
                return 0.0
            val = val.replace(',', '.')
            try:
                x = float(val)
                return max(x, 0.0)
            except ValueError:
                return 0.0
        
        l_man = parse_litros(self.entry_manana.get())
        l_tar = parse_litros(self.entry_tarde.get())
        l_noc = parse_litros(self.entry_noche.get())
        
        # Validación: debe haber al menos algo ordeñado
        if l_man == 0 and l_tar == 0 and l_noc == 0:
            messagebox.showwarning("Atención", "Debe registrar al menos una cantidad de litros.")
            return
        
        obs = self.text_obs.get("1.0", "end-1c").strip() or None

        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO produccion_leche (animal_id, fecha, litros_manana, litros_tarde, litros_noche, observaciones)
                    VALUES (?,?,?,?,?,?)
                    ON CONFLICT(animal_id, fecha) DO UPDATE SET
                        litros_manana=excluded.litros_manana,
                        litros_tarde=excluded.litros_tarde,
                        litros_noche=excluded.litros_noche,
                        observaciones=excluded.observaciones
                """, (animal_id, fecha, l_man, l_tar, l_noc, obs))
                conn.commit()
            
            messagebox.showinfo("Éxito", "Registro guardado correctamente.")
            self.limpiar_formulario(reset_date=False)
            self.actualizar_analisis()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Conflicto al guardar registro.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def eliminar_registro(self):
        """Elimina un registro seleccionado"""
        sel = self.tabla_registros.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un registro para eliminar.")
            return
        
        reg_id = self.tabla_registros.item(sel[0])['values'][0]
        
        if not messagebox.askyesno("Confirmar", "¿Eliminar este registro?"):
            return
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM produccion_leche WHERE id = ?", (reg_id,))
                conn.commit()
            
            messagebox.showinfo("Éxito", "Registro eliminado.")
            self.actualizar_analisis()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self, reset_date=True):
        """Limpia el formulario de registro"""
        if reset_date:
            self.entry_fecha.delete(0, 'end')
            self.entry_fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.entry_manana.delete(0, 'end')
        self.entry_tarde.delete(0, 'end')
        self.entry_noche.delete(0, 'end')
        self.text_obs.delete('1.0', 'end')

    # ============================================================================
    # ANÁLISIS Y ESTADÍSTICAS
    # ============================================================================
    def actualizar_analisis(self):
        """Actualiza todos los análisis: registros, análisis y comparativas"""
        self._cargar_registros()
        self._actualizar_estadisticas()
        self._actualizar_tabla_bajos()
        self._actualizar_comparativas()
        if MATPLOTLIB_AVAILABLE:
            self.actualizar_graficas()

    def _cargar_registros(self):
        """Carga los últimos 30 días de registros en la tabla"""
        for item in self.tabla_registros.get_children():
            self.tabla_registros.delete(item)
        
        if not self._finca_id_actual:
            return

        desde = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT pl.id, pl.fecha, a.codigo, COALESCE(a.nombre,'') AS nombre,
                           pl.litros_manana, pl.litros_tarde, pl.litros_noche, pl.observaciones
                    FROM produccion_leche pl
                    JOIN animal a ON a.id = pl.animal_id
                    WHERE pl.fecha >= ? AND a.id_finca = ?
                    ORDER BY pl.fecha DESC, a.codigo
                """, (desde, self._finca_id_actual))
                
                for r in cur.fetchall():
                    total = (r[4] or 0) + (r[5] or 0) + (r[6] or 0)
                    valores = (
                        str(r[0]),
                        str(r[1]),
                        f"{r[2]} - {r[3]}",
                        f"{total:.2f}",
                        f"{(r[4] or 0):.2f}",
                        f"{(r[5] or 0):.2f}",
                        f"{(r[6] or 0):.2f}",
                        (r[7] or '')
                    )
                    self.tabla_registros.insert('', 'end', values=valores)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar registros:\n{e}")

    def _actualizar_estadisticas(self):
        """Actualiza estadísticas del mes actual y hoy"""
        if not self._finca_id_actual:
            self.label_hoy_info.configure(text="Seleccione una finca para ver análisis...")
            self.label_mes_info.configure(text="Seleccione una finca para ver análisis...")
            return

        hoy = datetime.now().strftime("%Y-%m-%d")
        primer_dia_mes = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Datos de hoy
                cur.execute("""
                    SELECT COUNT(DISTINCT animal_id), SUM(litros_manana + litros_tarde + litros_noche)
                    FROM produccion_leche
                    WHERE fecha = ? AND animal_id IN (
                        SELECT id FROM animal WHERE id_finca = ?
                    )
                """, (hoy, self._finca_id_actual))
                
                hoy_data = cur.fetchone()
                vacas_hoy = hoy_data[0] or 0
                total_hoy = hoy_data[1] or 0.0
                
                info_hoy = f"Vacas ordeñadas hoy: {vacas_hoy} | Total producción: {total_hoy:.2f}L"
                self.label_hoy_info.configure(text=info_hoy)
                
                # Datos del mes actual
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT animal_id) as vacas,
                        COUNT(*) as registros,
                        COALESCE(SUM(litros_manana + litros_tarde + litros_noche), 0) as total,
                        COALESCE(AVG(litros_manana + litros_tarde + litros_noche), 0) as promedio
                    FROM produccion_leche
                    WHERE fecha >= ? AND animal_id IN (
                        SELECT id FROM animal WHERE id_finca = ?
                    )
                """, (primer_dia_mes, self._finca_id_actual))
                
                mes_data = cur.fetchone()
                vacas_mes = mes_data[0] or 0
                registros_mes = mes_data[1] or 0
                total_mes = mes_data[2] or 0.0
                prom_mes = mes_data[3] or 0.0
                
                info_mes = (
                    f"Vacas en producción: {vacas_mes}\n"
                    f"Total registros: {registros_mes}\n"
                    f"Producción total mes: {total_mes:.2f}L\n"
                    f"Promedio por ordeño: {prom_mes:.2f}L"
                )
                self.label_mes_info.configure(text=info_mes)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estadísticas:\n{e}")

    def _actualizar_tabla_bajos(self):
        """Actualiza tabla de vacas con baja producción"""
        for item in self.tabla_bajos.get_children():
            self.tabla_bajos.delete(item)
        
        if not self._finca_id_actual:
            return

        primer_dia_mes = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Obtener promedio de producción por vaca en el mes
                cur.execute("""
                    SELECT 
                        a.id,
                        a.codigo,
                        COALESCE(a.nombre, '') as nombre,
                        COUNT(pl.id) as dias,
                        COALESCE(AVG(pl.litros_manana + pl.litros_tarde + pl.litros_noche), 0) as promedio
                    FROM animal a
                    LEFT JOIN produccion_leche pl ON pl.animal_id = a.id AND pl.fecha >= ?
                    WHERE a.sexo = 'Hembra' AND a.id_finca = ?
                    GROUP BY a.id, a.codigo, a.nombre
                    HAVING promedio < ? OR promedio = 0
                    ORDER BY promedio ASC
                """, (primer_dia_mes, self._finca_id_actual, self.LIMITE_PRODUCCION_BAJA))
                
                for r in cur.fetchall():
                    animal_id, codigo, nombre, dias, promedio = r
                    label_animal = f"{codigo} - {nombre}".strip().rstrip('- ')
                    
                    # Últimos 3 días
                    cur2 = conn.cursor()
                    cur2.execute("""
                        SELECT COALESCE(AVG(litros_manana + litros_tarde + litros_noche), 0)
                        FROM produccion_leche
                        WHERE animal_id = ? AND fecha >= date('now', '-3 days')
                    """, (animal_id,))
                    
                    ultimos_3 = cur2.fetchone()[0] or 0.0
                    
                    valores = (
                        label_animal,
                        f"{promedio:.2f}",
                        str(dias),
                        f"{ultimos_3:.2f}"
                    )
                    self.tabla_bajos.insert('', 'end', values=valores)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar vacas bajas:\n{e}")

    def _actualizar_comparativas(self):
        """Actualiza tabla de comparativa entre meses"""
        for item in self.tabla_comparativa.get_children():
            self.tabla_comparativa.delete(item)
        
        if not self._finca_id_actual:
            return

        animal_filtro = self.combo_animal_comp.get()
        
        # Calcular fechas
        ahora = datetime.now()
        primer_dia_actual = ahora.replace(day=1)
        ultimo_dia_anterior = primer_dia_actual - timedelta(days=1)
        primer_dia_anterior = ultimo_dia_anterior.replace(day=1)
        
        fecha_inicio_actual = primer_dia_actual.strftime("%Y-%m-%d")
        fecha_inicio_anterior = primer_dia_anterior.strftime("%Y-%m-%d")
        fecha_fin_anterior = ultimo_dia_anterior.strftime("%Y-%m-%d")
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Construir query dinámica según filtro
                where_animal = ""
                params = [self._finca_id_actual]
                
                if animal_filtro != "Todas las vacas" and animal_filtro in self._animal_map:
                    animal_id = self._animal_map[animal_filtro]
                    where_animal = f"AND a.id = {animal_id}"
                
                cur.execute(f"""
                    SELECT 
                        a.codigo,
                        COALESCE(a.nombre, '') as nombre,
                        -- Mes anterior
                        COUNT(CASE WHEN pl.fecha >= ? AND pl.fecha <= ? THEN 1 END) as ant_dias,
                        COALESCE(SUM(CASE WHEN pl.fecha >= ? AND pl.fecha <= ? THEN pl.litros_manana + pl.litros_tarde + pl.litros_noche ELSE 0 END), 0) as ant_total,
                        COALESCE(AVG(CASE WHEN pl.fecha >= ? AND pl.fecha <= ? THEN pl.litros_manana + pl.litros_tarde + pl.litros_noche ELSE NULL END), 0) as ant_prom,
                        -- Mes actual
                        COUNT(CASE WHEN pl.fecha >= ? THEN 1 END) as act_dias,
                        COALESCE(SUM(CASE WHEN pl.fecha >= ? THEN pl.litros_manana + pl.litros_tarde + pl.litros_noche ELSE 0 END), 0) as act_total,
                        COALESCE(AVG(CASE WHEN pl.fecha >= ? THEN pl.litros_manana + pl.litros_tarde + pl.litros_noche ELSE NULL END), 0) as act_prom
                    FROM animal a
                    LEFT JOIN produccion_leche pl ON pl.animal_id = a.id
                    WHERE a.sexo = 'Hembra' AND a.id_finca = ? {where_animal}
                    GROUP BY a.id, a.codigo, a.nombre
                    ORDER BY a.codigo
                """, (
                    fecha_inicio_anterior, fecha_fin_anterior,
                    fecha_inicio_anterior, fecha_fin_anterior,
                    fecha_inicio_anterior, fecha_fin_anterior,
                    fecha_inicio_actual,
                    fecha_inicio_actual,
                    fecha_inicio_actual,
                    self._finca_id_actual
                ))
                
                for r in cur.fetchall():
                    codigo, nombre, ant_dias, ant_total, ant_prom, act_dias, act_total, act_prom = r
                    label_animal = f"{codigo} - {nombre}".strip().rstrip('- ')
                    
                    # Calcular cambio porcentual
                    if ant_prom > 0:
                        cambio = ((act_prom - ant_prom) / ant_prom) * 100
                        cambio_str = f"{cambio:+.1f}%"
                    else:
                        cambio_str = "N/A"
                    
                    valores = (
                        label_animal,
                        str(ant_dias),
                        f"{ant_total:.2f}",
                        f"{ant_prom:.2f}",
                        str(act_dias),
                        f"{act_total:.2f}",
                        f"{act_prom:.2f}",
                        cambio_str
                    )
                    self.tabla_comparativa.insert('', 'end', values=valores)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar comparativas:\n{e}")

    def actualizar_comparativas(self, value=None):
        """Callback para actualizar comparativas cuando cambia el filtro"""
        self._actualizar_comparativas()

    # ============================================================================
    # GRÁFICAS
    # ============================================================================
    def actualizar_graficas(self, value=None):
        """Actualiza la gráfica según datos y visualización seleccionada"""
        if not MATPLOTLIB_AVAILABLE or not self._finca_id_actual:
            return

        # Limpiar frame anterior
        for widget in self.frame_grafica.winfo_children():
            widget.destroy()

        tipo_dato = self.combo_tipo_dato.get()
        tipo_visual = self.combo_tipo_visualizacion.get()
        vaca_filtro = self.combo_animal_grafica.get()
        
        try:
            # Renderizar según DATO + VISUALIZACIÓN
            if tipo_dato == "Producción Total Diaria":
                self._render_produccion_diaria(tipo_visual, vaca_filtro)
            elif tipo_dato == "Producción por Vaca":
                self._render_produccion_por_vaca(tipo_visual, vaca_filtro)
            elif tipo_dato == "Baja Producción":
                self._render_baja_produccion(tipo_visual, vaca_filtro)
            elif tipo_dato == "Comparativa Meses":
                self._render_comparativa_meses(tipo_visual, vaca_filtro)
            elif tipo_dato == "Producción por Turno":
                self._render_produccion_por_turno(tipo_visual, vaca_filtro)
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráfica:\n{e}")

    # ============================================================================
    # MÉTODOS RENDERIZADORES DE GRÁFICAS
    # ============================================================================
    
    def _render_produccion_diaria(self, tipo_visual, vaca_filtro):
        """Renderiza producción diaria según tipo de visualización"""
        ahora = datetime.now()
        primer_dia = ahora.replace(day=1)
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                if vaca_filtro == "Todas las vacas":
                    cur.execute("""
                        SELECT fecha, SUM(litros_manana + litros_tarde + litros_noche) as total
                        FROM produccion_leche
                        WHERE fecha >= ? AND animal_id IN (
                            SELECT id FROM animal WHERE id_finca = ?
                        )
                        GROUP BY fecha ORDER BY fecha
                    """, (primer_dia.strftime("%Y-%m-%d"), self._finca_id_actual))
                    titulo_extra = "Todas las vacas"
                elif vaca_filtro in self._animal_map:
                    animal_id = self._animal_map[vaca_filtro]
                    cur.execute("""
                        SELECT fecha, SUM(litros_manana + litros_tarde + litros_noche) as total
                        FROM produccion_leche
                        WHERE fecha >= ? AND animal_id = ?
                        GROUP BY fecha ORDER BY fecha
                    """, (primer_dia.strftime("%Y-%m-%d"), animal_id))
                    titulo_extra = vaca_filtro
                else:
                    return
                
                datos = cur.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos:\n{e}")
            return

        if not datos:
            label = ctk.CTkLabel(self.frame_grafica, text="No hay datos para mostrar",
                                font=("Segoe UI", 12))
            label.pack(pady=50)
            return

        fechas = [datetime.strptime(str(d[0]), "%Y-%m-%d") for d in datos]
        totales = [d[1] or 0 for d in datos]

        fig = Figure(figsize=(12, 6), dpi=80, facecolor='#2a2a2a')
        ax = fig.add_subplot(111, facecolor='#3a3a3a')
        
        if tipo_visual == "Línea":
            ax.plot(fechas, totales, marker='o', linewidth=2, color='#FBC02D', markersize=6)
            ax.fill_between(fechas, totales, alpha=0.3, color='#FBC02D')
        elif tipo_visual == "Barras":
            ax.bar(fechas, totales, color='#4CAF50', alpha=0.8, edgecolor='white', width=0.8)
        elif tipo_visual == "Combinada (Columnas+Línea)":
            ax.bar(fechas, totales, color='#4CAF50', alpha=0.6)
            ax.plot(fechas, totales, marker='o', linewidth=2.5, color='#FFC107', markersize=7)
        elif tipo_visual == "Pastel":
            messagebox.showwarning("Atención", "El gráfico de pastel no es aplicable a datos diarios.\nUse 'Producción por Vaca'")
            return
        elif tipo_visual == "Columnas Apiladas":
            messagebox.showwarning("Atención", "Use 'Producción por Turno' para visualizar columnas apiladas")
            return
        
        ax.set_xlabel('Fecha', color='white', fontsize=10)
        ax.set_ylabel('Litros', color='white', fontsize=10)
        ax.set_title(f'Producción Total Diaria - {titulo_extra}', color='white', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, color='white')
        ax.tick_params(colors='white')
        fig.autofmt_xdate(rotation=45)
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_produccion_por_vaca(self, tipo_visual, vaca_filtro):
        """Renderiza producción acumulada por vaca"""
        ahora = datetime.now()
        primer_dia = ahora.replace(day=1)
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT a.codigo, COALESCE(a.nombre, ''),
                           SUM(pl.litros_manana + pl.litros_tarde + pl.litros_noche) as total
                    FROM animal a
                    LEFT JOIN produccion_leche pl ON pl.animal_id = a.id AND pl.fecha >= ?
                    WHERE a.sexo = 'Hembra' AND a.id_finca = ?
                    GROUP BY a.id, a.codigo, a.nombre
                    ORDER BY total DESC NULLS LAST
                """, (primer_dia.strftime("%Y-%m-%d"), self._finca_id_actual))
                
                datos = cur.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos:\n{e}")
            return

        if not datos:
            label = ctk.CTkLabel(self.frame_grafica, text="No hay datos para mostrar",
                                font=("Segoe UI", 12))
            label.pack(pady=50)
            return

        etiquetas = [f"{d[0]} - {d[1]}".strip().rstrip('- ') for d in datos]
        valores = [d[2] or 0 for d in datos]

        fig = Figure(figsize=(12, 6), dpi=80, facecolor='#2a2a2a')
        ax = fig.add_subplot(111, facecolor='#3a3a3a')
        
        colores = ['#4CAF50' if v >= self.LIMITE_PRODUCCION_BAJA else '#FF6B6B' for v in valores]

        if tipo_visual == "Barras":
            bars = ax.barh(etiquetas, valores, color=colores, alpha=0.8, edgecolor='white')
            for i, (bar, val) in enumerate(zip(bars, valores)):
                ax.text(val + 0.2, i, f'{val:.1f}L', va='center', color='white', fontsize=10)
        elif tipo_visual == "Pastel":
            valores_pos = [v for v in valores if v > 0]
            etiquetas_pos = [e for e, v in zip(etiquetas, valores) if v > 0]
            if valores_pos:
                colores_pastel = plt.cm.Set3(range(len(valores_pos)))
                wedges, texts, autotexts = ax.pie(valores_pos, labels=etiquetas_pos, autopct='%1.1f%%',
                                                   colors=colores_pastel, startangle=90, textprops={'color': 'white', 'fontsize': 9})
                for autotext in autotexts:
                    autotext.set_color('black')
                    autotext.set_fontweight('bold')
        elif tipo_visual == "Línea":
            ax.plot(range(len(etiquetas)), valores, marker='o', linewidth=2, color='#00BCD4', markersize=8)
            ax.set_xticks(range(len(etiquetas)))
            ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        elif tipo_visual == "Combinada (Columnas+Línea)":
            ax.bar(range(len(etiquetas)), valores, color=colores, alpha=0.6, edgecolor='white')
            ax.plot(range(len(etiquetas)), valores, marker='o', linewidth=2.5, color='#FFC107', markersize=8)
            ax.set_xticks(range(len(etiquetas)))
            ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        else:  # Columnas Apiladas (no aplica aquí)
            messagebox.showwarning("Atención", "Use 'Producción por Turno' para columnas apiladas")
            return
        
        ax.set_title('Producción Total por Vaca (Mes Actual)', color='white', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, color='white', axis='y' if tipo_visual == "Barras" else 'both')
        ax.tick_params(colors='white')
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_baja_produccion(self, tipo_visual, vaca_filtro):
        """Renderiza vacas con baja producción"""
        primer_dia_mes = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT a.codigo, COALESCE(a.nombre, '') as nombre,
                           COALESCE(AVG(pl.litros_manana + pl.litros_tarde + pl.litros_noche), 0) as promedio
                    FROM animal a
                    LEFT JOIN produccion_leche pl ON pl.animal_id = a.id AND pl.fecha >= ?
                    WHERE a.sexo = 'Hembra' AND a.id_finca = ?
                    GROUP BY a.id, a.codigo, a.nombre
                    HAVING promedio < ? OR promedio = 0
                    ORDER BY promedio ASC
                """, (primer_dia_mes, self._finca_id_actual, self.LIMITE_PRODUCCION_BAJA))
                
                datos = cur.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos:\n{e}")
            return

        if not datos:
            label = ctk.CTkLabel(self.frame_grafica, 
                               text=f"✅ ¡Excelente! Todas las vacas tienen producción ≥ {self.LIMITE_PRODUCCION_BAJA}L",
                               font=("Segoe UI", 12), text_color="lightgreen")
            label.pack(pady=50)
            return

        etiquetas = [f"{d[0]} - {d[1]}".strip().rstrip('- ') for d in datos]
        valores = [d[2] for d in datos]

        fig = Figure(figsize=(12, 6), dpi=80, facecolor='#2a2a2a')
        ax = fig.add_subplot(111, facecolor='#3a3a3a')

        if tipo_visual == "Barras":
            bars = ax.barh(etiquetas, valores, color='#FF6B6B', alpha=0.8, edgecolor='white')
            ax.axvline(x=self.LIMITE_PRODUCCION_BAJA, color='#FBC02D', linestyle='--', linewidth=2, label=f'Límite ({self.LIMITE_PRODUCCION_BAJA}L)')
            for i, (bar, val) in enumerate(zip(bars, valores)):
                ax.text(val + 0.1, i, f'{val:.1f}L', va='center', color='white', fontsize=10)
        elif tipo_visual == "Pastel":
            colores_pastel = plt.cm.Set3(range(len(valores)))
            wedges, texts, autotexts = ax.pie(valores, labels=etiquetas, autopct='%1.1f%%',
                                               colors=colores_pastel, startangle=90, textprops={'color': 'white', 'fontsize': 9})
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
        elif tipo_visual == "Línea":
            ax.plot(range(len(etiquetas)), valores, marker='o', linewidth=2, color='#FF6B6B', markersize=8)
            ax.axhline(y=self.LIMITE_PRODUCCION_BAJA, color='#FBC02D', linestyle='--', linewidth=2, label=f'Límite ({self.LIMITE_PRODUCCION_BAJA}L)')
            ax.set_xticks(range(len(etiquetas)))
            ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        elif tipo_visual == "Combinada (Columnas+Línea)":
            ax.bar(range(len(etiquetas)), valores, color='#FF6B6B', alpha=0.6, edgecolor='white')
            ax.plot(range(len(etiquetas)), valores, marker='o', linewidth=2, color='#FFC107', markersize=8)
            ax.set_xticks(range(len(etiquetas)))
            ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        else:
            messagebox.showwarning("Atención", "Tipo de visualización no compatible")
            return

        ax.set_xlabel('Promedio de Producción (L)', color='white', fontsize=10)
        ax.set_title(f'Vacas con Baja Producción (< {self.LIMITE_PRODUCCION_BAJA}L)', 
                    color='white', fontsize=14, fontweight='bold')
        if tipo_visual == "Barras":
            ax.legend(loc='lower right', labelcolor='white')
        ax.grid(True, alpha=0.3, color='white', axis='x' if tipo_visual == "Barras" else 'both')
        ax.tick_params(colors='white')
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_comparativa_meses(self, tipo_visual, vaca_filtro):
        """Renderiza comparativa de meses anterior vs actual"""
        ahora = datetime.now()
        primer_dia_actual = ahora.replace(day=1)
        ultimo_dia_anterior = primer_dia_actual - timedelta(days=1)
        primer_dia_anterior = ultimo_dia_anterior.replace(day=1)
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                cur.execute("""
                    SELECT SUM(litros_manana + litros_tarde + litros_noche)
                    FROM produccion_leche
                    WHERE fecha >= ? AND fecha <= ? AND animal_id IN (
                        SELECT id FROM animal WHERE id_finca = ?
                    )
                """, (primer_dia_anterior.strftime("%Y-%m-%d"), 
                      ultimo_dia_anterior.strftime("%Y-%m-%d"),
                      self._finca_id_actual))
                total_ant = cur.fetchone()[0] or 0
                
                cur.execute("""
                    SELECT SUM(litros_manana + litros_tarde + litros_noche)
                    FROM produccion_leche
                    WHERE fecha >= ? AND animal_id IN (
                        SELECT id FROM animal WHERE id_finca = ?
                    )
                """, (primer_dia_actual.strftime("%Y-%m-%d"), self._finca_id_actual))
                total_act = cur.fetchone()[0] or 0
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos:\n{e}")
            return

        meses = [f"Mes Anterior\n({primer_dia_anterior.strftime('%b')})", 
                f"Mes Actual\n({primer_dia_actual.strftime('%b')})"]
        valores = [total_ant, total_act]

        fig = Figure(figsize=(10, 6), dpi=80, facecolor='#2a2a2a')
        ax = fig.add_subplot(111, facecolor='#3a3a3a')
        
        colores = ['#2196F3', '#4CAF50']

        if tipo_visual == "Barras":
            bars = ax.barh(meses, valores, color=colores, alpha=0.8, edgecolor='white', height=0.5)
            for bar, val in zip(bars, valores):
                ax.text(val + 20, bar.get_y() + bar.get_height()/2, f'{val:.0f}L',
                       va='center', color='white', fontsize=12, fontweight='bold')
        elif tipo_visual == "Línea":
            ax.plot(meses, valores, marker='o', linewidth=2.5, color='#00BCD4', markersize=10)
            for i, (mes, val) in enumerate(zip(meses, valores)):
                ax.text(i, val + 100, f'{val:.0f}L', ha='center', color='white', fontsize=11, fontweight='bold')
        else:  # Columnas, Pastel, Combinada
            bars = ax.bar(meses, valores, color=colores, alpha=0.8, edgecolor='white', width=0.6)
            for bar, val in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.0f}L', ha='center', va='bottom', color='white', fontsize=12, fontweight='bold')
        
        if total_ant > 0:
            cambio = ((total_act - total_ant) / total_ant) * 100
            ax.text(0.5, max(valores) * 0.9, f'Cambio: {cambio:+.1f}%',
                   transform=ax.transAxes, fontsize=14, fontweight='bold',
                   ha='center', bbox=dict(boxstyle='round', facecolor='#FBC02D', alpha=0.8))
        
        ax.set_ylabel('Litros Totales', color='white', fontsize=11)
        ax.set_title('Comparativa de Producción Total: Mes Anterior vs Actual', 
                    color='white', fontsize=14, fontweight='bold')
        ax.tick_params(colors='white')
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_produccion_por_turno(self, tipo_visual, vaca_filtro):
        """Renderiza producción por turno (Mañana, Tarde, Noche)"""
        ahora = datetime.now()
        primer_dia = ahora.replace(day=1)
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT fecha, SUM(litros_manana) as manana,
                           SUM(litros_tarde) as tarde, SUM(litros_noche) as noche
                    FROM produccion_leche
                    WHERE fecha >= ? AND animal_id IN (
                        SELECT id FROM animal WHERE id_finca = ?
                    )
                    GROUP BY fecha ORDER BY fecha
                """, (primer_dia.strftime("%Y-%m-%d"), self._finca_id_actual))
                
                datos = cur.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos:\n{e}")
            return

        if not datos:
            label = ctk.CTkLabel(self.frame_grafica, text="No hay datos para mostrar",
                                font=("Segoe UI", 12))
            label.pack(pady=50)
            return

        fechas = [datetime.strptime(str(d[0]), "%Y-%m-%d") for d in datos]
        manana = [d[1] or 0 for d in datos]
        tarde = [d[2] or 0 for d in datos]
        noche = [d[3] or 0 for d in datos]

        fig = Figure(figsize=(12, 6), dpi=80, facecolor='#2a2a2a')
        ax = fig.add_subplot(111, facecolor='#3a3a3a')

        if tipo_visual == "Columnas Apiladas":
            x = range(len(fechas))
            ax.bar(x, manana, label='Mañana', color='#FF9800', alpha=0.8)
            ax.bar(x, tarde, bottom=manana, label='Tarde', color='#2196F3', alpha=0.8)
            ax.bar(x, noche, bottom=[m+t for m,t in zip(manana, tarde)], label='Noche', color='#9C27B0', alpha=0.8)
            ax.set_xticks(x[::max(1, len(x)//10)])
            ax.set_xticklabels([f.strftime('%d/%m') for f in fechas[::max(1, len(fechas)//10)]], rotation=45)
        elif tipo_visual == "Línea":
            ax.plot(fechas, manana, marker='o', linewidth=2, color='#FF9800', label='Mañana', markersize=5)
            ax.plot(fechas, tarde, marker='s', linewidth=2, color='#2196F3', label='Tarde', markersize=5)
            ax.plot(fechas, noche, marker='^', linewidth=2, color='#9C27B0', label='Noche', markersize=5)
            fig.autofmt_xdate(rotation=45)
        elif tipo_visual == "Barras":
            x = range(len(fechas))
            width = 0.25
            ax.bar([i - width for i in x], manana, width, label='Mañana', color='#FF9800', alpha=0.8)
            ax.bar(x, tarde, width, label='Tarde', color='#2196F3', alpha=0.8)
            ax.bar([i + width for i in x], noche, width, label='Noche', color='#9C27B0', alpha=0.8)
            ax.set_xticks(x[::max(1, len(x)//10)])
            ax.set_xticklabels([f.strftime('%d/%m') for f in fechas[::max(1, len(fechas)//10)]], rotation=45)
        else:
            messagebox.showwarning("Atención", "Tipo de visualización no compatible con datos por turno")
            return
        
        ax.set_xlabel('Fecha', color='white', fontsize=10)
        ax.set_ylabel('Litros', color='white', fontsize=10)
        ax.set_title('Producción por Turno Horario', color='white', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', labelcolor='white')
        ax.grid(True, alpha=0.3, color='white', axis='y')
        ax.tick_params(colors='white')
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


# Helper para probar
if __name__ == '__main__':
    app = ctk.CTk()
    app.title('Test Pesaje Leche v2')
    frame = PesajeLecheFrame(app)
    app.geometry('1400x800')
    app.mainloop()
