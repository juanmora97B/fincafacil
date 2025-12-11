"""
Inventario General V2 - CORREGIDO
Versión funcional con detección de columnas
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

try:
    from database import get_db_connection
except Exception:
    from database.database import get_db_connection

# ==================== HELPERS SQL ====================

def detectar_columna_finca(tabla: str) -> str:
    """Detecta si la tabla usa finca_id o id_finca"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"PRAGMA table_info({tabla})")
            cols = [r[1] for r in cur.fetchall()]
            return 'finca_id' if 'finca_id' in cols else 'id_finca'
    except:
        return 'id_finca'  # Default para este proyecto

def get_potreros_por_finca(finca_id: int) -> List[Tuple[int, str]]:
    """Obtiene potreros de una finca específica"""
    try:
        finca_col = detectar_columna_finca('potrero')
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT id, nombre FROM potrero WHERE {finca_col} = ? ORDER BY nombre", (finca_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"Error get_potreros_por_finca: {e}")
        return []

def get_sectores_por_finca(finca_id: int) -> List[Tuple[int, str]]:
    """Obtiene sectores de una finca específica"""
    try:
        finca_col = detectar_columna_finca('sector')
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT id, nombre FROM sector WHERE {finca_col} = ? ORDER BY nombre", (finca_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"Error get_sectores_por_finca: {e}")
        return []

def get_lotes_por_finca(finca_id: int) -> List[Tuple[int, str]]:
    """Obtiene lotes de una finca específica"""
    try:
        finca_col = detectar_columna_finca('lote')
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT id, nombre FROM lote WHERE {finca_col} = ? ORDER BY nombre", (finca_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"Error get_lotes_por_finca: {e}")
        return []

def buscar_animales(filters: Dict[str, Any], search_query: str = "") -> List[Dict[str, Any]]:
    """Busca animales con filtros y texto de búsqueda"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            # Detectar columnas
            cur.execute("PRAGMA table_info(animal)")
            cols = [r[1] for r in cur.fetchall()]
            has_hierro = 'hierro' in cols
            finca_col = 'finca_id' if 'finca_id' in cols else 'id_finca'
            sector_col = 'sector_id' if 'sector_id' in cols else 'id_sector'
            potrero_col = 'potrero_id' if 'potrero_id' in cols else 'id_potrero'

            # Diagnóstico: columnas detectadas
            try:
                print(f"[InventarioV2] Columnas detectadas -> finca:{finca_col}, sector:{sector_col}, potrero:{potrero_col}, hierro:{has_hierro}")
            except Exception:
                pass

            where = []
            params = []

            if filters.get('finca_id'):
                where.append(f"a.{finca_col} = ?")
                params.append(filters['finca_id'])

            if filters.get('sector_id'):
                where.append(f"a.{sector_col} = ?")
                params.append(filters['sector_id'])

            if filters.get('lote_id'):
                where.append("a.lote_id = ?")
                params.append(filters['lote_id'])

            if filters.get('potrero_id'):
                where.append(f"a.{potrero_col} = ?")
                params.append(filters['potrero_id'])

            if filters.get('categoria'):
                where.append("COALESCE(a.categoria, 'Sin categoría') = ?")
                params.append(filters['categoria'])

            if search_query:
                like_val = f"%{search_query}%"
                if has_hierro:
                    where.append("(a.nombre LIKE ? OR a.codigo LIKE ? OR a.hierro LIKE ?)")
                    params.extend([like_val, like_val, like_val])
                else:
                    where.append("(a.nombre LIKE ? OR a.codigo LIKE ?)")
                    params.extend([like_val, like_val])

            # Detectar columnas opcionales de peso y fechas
            has_peso_nac = 'peso_nacimiento' in cols
            has_peso_comp = 'peso_compra' in cols
            has_fecha_up = 'fecha_ultimo_peso' in cols

            sql = f"""
                SELECT 
                    a.id,
                    a.codigo,
                    a.nombre,
                    a.sexo,
                    a.fecha_nacimiento,
                    COALESCE(a.categoria, 'Sin categoría') AS categoria,
                    f.nombre AS finca,
                    s.nombre AS sector,
                    l.nombre AS lote,
                    p.nombre AS potrero,
                    COALESCE(a.ultimo_peso, 0) AS ultimo_peso,
                    { 'a.peso_nacimiento,' if has_peso_nac else 'NULL AS peso_nacimiento,' }
                    { 'a.peso_compra,' if has_peso_comp else 'NULL AS peso_compra,' }
                    { 'a.fecha_ultimo_peso,' if has_fecha_up else 'NULL AS fecha_ultimo_peso,' }
                    a.inventariado,
                    a.foto_path,
                    CASE WHEN a.inventariado = 1 THEN 'Inventariado' ELSE 'No inventariado' END AS estado
                FROM animal a
                LEFT JOIN finca f ON a.{finca_col} = f.id
                LEFT JOIN sector s ON a.{sector_col} = s.id
                LEFT JOIN lote l ON a.lote_id = l.id
                LEFT JOIN potrero p ON a.{potrero_col} = p.id
            """

            if where:
                sql += " WHERE " + " AND ".join(where)

            sql += " ORDER BY a.codigo"

            # Diagnóstico: preview del WHERE y parámetros
            try:
                print(f"[InventarioV2] WHERE parts: {len(where)} | Params: {params}")
            except Exception:
                pass

            cur.execute(sql, tuple(params))
            columns = [desc[0] for desc in cur.description]

            results = []
            for row in cur.fetchall():
                results.append(dict(zip(columns, row)))

            # Diagnóstico: total resultados
            try:
                print(f"[InventarioV2] Resultados cargados: {len(results)}")
            except Exception:
                pass

            return results
    except Exception as e:
        print(f"Error buscar_animales: {e}")
        import traceback
        traceback.print_exc()
        return []

def asegurar_tabla_categorias():
    """Crea tabla categoria e inserta valores por defecto"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categoria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE
                )
            """)
            cur.execute("SELECT COUNT(*) FROM categoria")
            if cur.fetchone()[0] == 0:
                valores = [("Vaca",), ("Toro",), ("Novillo",), ("Ternero",), ("Vaquillona",)]
                cur.executemany("INSERT OR IGNORE INTO categoria(nombre) VALUES(?)", valores)
                conn.commit()
    except Exception as e:
        print(f"Error asegurar_tabla_categorias: {e}")

def asegurar_columnas_inventario():
    """Agrega columnas faltantes"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(animal)")
            columns = [row[1] for row in cur.fetchall()]
            
            if 'ultimo_peso' not in columns:
                cur.execute("ALTER TABLE animal ADD COLUMN ultimo_peso REAL")
            if 'inventariado' not in columns:
                cur.execute("ALTER TABLE animal ADD COLUMN inventariado INTEGER DEFAULT 0")
            if 'categoria' not in columns:
                cur.execute("ALTER TABLE animal ADD COLUMN categoria TEXT")
            
            conn.commit()
    except Exception as e:
        print(f"Error asegurar_columnas_inventario: {e}")


def ejecutar_migracion_inventario() -> bool:
    """Punto de entrada de migración para el inventario v2.

    - Crea/asegura tabla `categoria` con valores por defecto.
    - Asegura columnas nuevas en `animal` (ultimo_peso, inventariado, categoria).
    Devuelve True si no hubo excepciones.
    """
    try:
        asegurar_columnas_inventario()
        asegurar_tabla_categorias()
        return True
    except Exception as e:
        print(f"Error ejecutar_migracion_inventario: {e}")
        return False


# ==================== CLASE PRINCIPAL ====================

class InventarioGeneralFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        asegurar_columnas_inventario()
        asegurar_tabla_categorias()
        self._asignar_categorias_defecto_silencioso()
        
        self.current_filters = {}
        self.search_timer = None
        self.current_data = []
        
        # Scroll container
        self.scroll_container = ctk.CTkScrollableFrame(self)
        self.scroll_container.pack(fill="both", expand=True, padx=2, pady=8)
        
        self._build_header()
        self._build_filters()
        self._build_table()
        self._build_actions()
        self._build_footer()
        
        self._load_fincas()
        self._aplicar_filtros()

    def _asignar_categorias_defecto_silencioso(self):
        """Asegura que exista al menos una categoría asignada a animales sin categoría.
        No muestra UI; corre al iniciar para mejorar la experiencia del filtro."""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE animal SET categoria = 'Vaca' WHERE categoria IS NULL OR categoria = ''")
                conn.commit()
        except Exception:
            pass
    
    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, corner_radius=12)
        header.pack(fill="x", pady=10, padx=10)
        
        top_row = ctk.CTkFrame(header, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(10, 5))
        
        title_label = ctk.CTkLabel(top_row, text="📋 Inventario General de Animales",
                font=("Segoe UI", 24, "bold"))
        title_label.pack(side="left", padx=10)
        
        # Acciones arriba a la derecha
        header_actions = ctk.CTkFrame(top_row, fg_color="transparent")
        header_actions.pack(side="right")
        
        btn_exportar = ctk.CTkButton(header_actions, text="📦 Exportar", width=130, height=40,
                   fg_color="#2563eb", command=self._exportar_actual)
        btn_exportar.pack(side="right", padx=6)
        
        btn_graficas = ctk.CTkButton(header_actions, text="📊 Gráficas", width=130, height=40,
                   fg_color="#7c3aed", command=self._abrir_graficas)
        btn_graficas.pack(side="right", padx=6)
        
        self.lbl_count = ctk.CTkLabel(header, text="0 animales",
                          font=("Segoe UI", 14, "bold"), text_color="#1f538d")
        self.lbl_count.pack(anchor="w", padx=20, pady=(0, 10))
    
    def _build_filters(self):
        filters_frame = ctk.CTkFrame(self.scroll_container, corner_radius=12)
        filters_frame.pack(fill="x", pady=5, padx=10)
        filters_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        filters_title = ctk.CTkLabel(filters_frame, text="⚙️ Filtros Avanzados",
                    font=("Segoe UI", 16, "bold"))
        filters_title.grid(row=0, column=0, columnspan=6, padx=20, pady=(15, 10), sticky="w")
        
        # Finca
        lbl_finca = ctk.CTkLabel(filters_frame, text="Finca *", font=("Segoe UI", 12, "bold"))
        lbl_finca.grid(row=1, column=0, padx=12, pady=(5, 2), sticky="w")
        self.cmb_finca = ctk.CTkComboBox(filters_frame, width=180, height=36, command=self._on_finca_change)
        self.cmb_finca.grid(row=2, column=0, padx=12, pady=(0, 15), sticky="ew")
        
        # Sector
        lbl_sector = ctk.CTkLabel(filters_frame, text="Sector", font=("Segoe UI", 12, "bold"))
        lbl_sector.grid(row=1, column=1, padx=12, pady=(5, 2), sticky="w")
        self.cmb_sector = ctk.CTkComboBox(filters_frame, width=160, height=36, state="disabled")
        self.cmb_sector.grid(row=2, column=1, padx=12, pady=(0, 15), sticky="ew")
        
        # Lote
        lbl_lote = ctk.CTkLabel(filters_frame, text="Lote", font=("Segoe UI", 12, "bold"))
        lbl_lote.grid(row=1, column=2, padx=12, pady=(5, 2), sticky="w")
        self.cmb_lote = ctk.CTkComboBox(filters_frame, width=160, height=36, state="disabled")
        self.cmb_lote.grid(row=2, column=2, padx=12, pady=(0, 15), sticky="ew")
        
        # Potrero
        lbl_potrero = ctk.CTkLabel(filters_frame, text="Potrero", font=("Segoe UI", 12, "bold"))
        lbl_potrero.grid(row=1, column=3, padx=12, pady=(5, 2), sticky="w")
        self.cmb_potrero = ctk.CTkComboBox(filters_frame, width=160, height=36, state="disabled")
        self.cmb_potrero.grid(row=2, column=3, padx=12, pady=(0, 15), sticky="ew")
        
        # Categoría
        lbl_categoria = ctk.CTkLabel(filters_frame, text="Categoría", font=("Segoe UI", 12, "bold"))
        lbl_categoria.grid(row=1, column=4, padx=12, pady=(5, 2), sticky="w")
        self.cmb_categoria = ctk.CTkComboBox(filters_frame, width=160, height=36)
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM categoria ORDER BY nombre")
                cats = [r[0] for r in cur.fetchall()]
            self.cmb_categoria.configure(values=["Todas"] + cats if cats else ["Todas", "Vaca", "Toro"])
            self.cmb_categoria.set("Todas")
        except:
            self.cmb_categoria.configure(values=["Todas"])
            self.cmb_categoria.set("Todas")
        self.cmb_categoria.grid(row=2, column=4, padx=12, pady=(0, 15), sticky="ew")
        
        # Búsqueda
        lbl_buscar = ctk.CTkLabel(filters_frame, text="Buscar", font=("Segoe UI", 12, "bold"))
        lbl_buscar.grid(row=1, column=5, padx=12, pady=(5, 2), sticky="w")
        self.search_entry = ctk.CTkEntry(filters_frame, placeholder_text="Código, nombre, hierro...", height=36)
        self.search_entry.grid(row=2, column=5, padx=12, pady=(0, 15), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        
        # Botones
        btn_container = ctk.CTkFrame(filters_frame, fg_color="transparent")
        btn_container.grid(row=3, column=0, columnspan=6, padx=20, pady=(0, 15))
        
        btn_aplicar = ctk.CTkButton(btn_container, text="✓ Aplicar Filtros", command=self._aplicar_filtros,
                     width=160, height=40, fg_color="#1f538d")
        btn_aplicar.pack(side="left", padx=5)
        
        btn_limpiar = ctk.CTkButton(btn_container, text="↻ Limpiar", command=self._limpiar_filtros,
                     width=140, height=40, fg_color="gray40")
        btn_limpiar.pack(side="left", padx=5)
    
    def _build_table(self):
        self.table_container = ctk.CTkFrame(self.scroll_container, corner_radius=12)
        self.table_container.pack(fill="both", expand=True, pady=10, padx=10)
        
        table_header = ctk.CTkFrame(self.table_container, fg_color="transparent")
        table_header.pack(fill="x", padx=20, pady=(15, 10))
        
        table_title = ctk.CTkLabel(table_header, text="📊 Lista de Animales",
                    font=("Segoe UI", 16, "bold"))
        table_title.pack(side="left")
        
        self.lbl_status = ctk.CTkLabel(table_header, text="", font=("Segoe UI", 11), text_color="gray60")
        self.lbl_status.pack(side="right", padx=10)
        
        # Use tk.Frame instead of ctk.CTkFrame for TTkinter Treeview compatibility
        # CTkFrame uses a different widget system that conflicts with TTkinter widgets
        table_frame = tk.Frame(self.table_container, bg="white")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Estilo TTK
        try:
            style = ttk.Style()
            style.theme_use('default')
            style.configure('Treeview', background='#ffffff', fieldbackground='#ffffff',
                           foreground='#000000', rowheight=26)
            style.configure('Treeview.Heading', background='#e6edf5', foreground='#1f538d',
                           font=('Segoe UI', 11, 'bold'))
            style.map('Treeview', background=[('selected', '#cfe8ff')])
        except:
            pass
        
        columns = ["codigo", "nombre", "categoria", "finca", "sector", "lote", "potrero", "peso", "inventariado", "estado", "fecha_peso", "peso_inicial"]
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", height=15)
        
        col_config = {
            "codigo": ("Código", 110, "w"),
            "nombre": ("Nombre", 170, "w"),
            "categoria": ("Categoría", 110, "w"),
            "finca": ("Finca", 130, "w"),
            "sector": ("Sector", 110, "w"),
            "lote": ("Lote", 110, "w"),
            "potrero": ("Potrero", 110, "w"),
            "peso": ("Peso (kg)", 95, "center"),
            "inventariado": ("Inventariado (✓)", 120, "center"),
            "estado": ("Estado", 115, "center"),
            "fecha_peso": ("Fecha Últ. Peso", 120, "center"),
            "peso_inicial": ("Peso Inicial", 95, "center")
        }
        
        for col, (text, width, anchor) in col_config.items():
            self.tree.heading(col, text=text, anchor='center')
            # For uniform centered appearance, center all columns
            self.tree.column(col, width=width, anchor='center', stretch=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        
        self.tree.tag_configure('inventariado', background='#e6f4ea')
        self.tree.tag_configure('evenrow', background='#f8f9fa')
        self.tree.tag_configure('oddrow', background='white')
    
    def _build_actions(self):
        actions_frame = ctk.CTkFrame(self.scroll_container, corner_radius=12)
        actions_frame.pack(fill="x", pady=5, padx=10)

        actions_label = ctk.CTkLabel(actions_frame, text="🛠 Acciones", font=("Segoe UI", 15, "bold"))
        actions_label.pack(anchor="w", padx=20, pady=(12, 0))

        btn_container = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btn_container.pack(fill="x", pady=12, padx=10)

        # Secciones: Selección, Globales
        frame_sel = ctk.CTkFrame(btn_container, fg_color="transparent")
        frame_sel.pack(side="left", padx=5)
        frame_global = ctk.CTkFrame(btn_container, fg_color="transparent")
        frame_global.pack(side="right", padx=5)

        # Botones dependientes de selección
        self.action_buttons = []
        acciones_seleccion = [
            ("👁 Ver", self._ver_animal, "#1f538d"),
            ("✏ Editar", self._editar_animal, "#2d6a4f"),
            ("🚚 Reubicar", self._reubicar_animal, "#0ea5e9"),
            ("🗑 Eliminar", self._eliminar_animal, "#dc2626"),
        ]
        for text, command, color in acciones_seleccion:
            b = ctk.CTkButton(frame_sel, text=text, command=command, width=130, height=40,
                              fg_color=color, state="disabled")
            b.pack(side="left", padx=4)
            self.action_buttons.append(b)

        # Botones globales siempre activos
        btn_actualizar = ctk.CTkButton(frame_global, text="🔄 Actualizar", width=130, height=40,
                       fg_color="#1f2937", command=self._aplicar_filtros)
        btn_actualizar.pack(side="left", padx=4)
        # Botones globales (arriba ya están Exportar/Gráficas)
        # Mantener aquí solo Actualizar para evitar duplicados visuales
    
    def _build_footer(self):
        footer = ctk.CTkFrame(self.scroll_container, corner_radius=12)
        footer.pack(fill="x", pady=(5, 10), padx=10)
        footer_label = ctk.CTkLabel(footer, text="Inventario V2 • Gestión avanzada", font=("Segoe UI", 11),
                     text_color="gray60")
        footer_label.pack(anchor="e", padx=15, pady=8)
    
    def _load_fincas(self):
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM finca ORDER BY nombre")
                fincas = cur.fetchall()
            
            values = [f"{f[0]} - {f[1]}" for f in fincas]
            self.cmb_finca.configure(values=values)
            
            if values:
                self.cmb_finca.set(values[0])
                self._on_finca_change(values[0])
        except Exception as e:
            print(f"Error cargando fincas: {e}")
    
    def _on_finca_change(self, value=None):
        # Alias público solicitado: cargar_filtros_por_finca
        self.cargar_filtros_por_finca()

    def cargar_filtros_por_finca(self):
        try:
            finca_val = self.cmb_finca.get()
            if not finca_val or '-' not in finca_val:
                return
            
            finca_id = int(finca_val.split(' - ')[0])
            
            sectores = get_sectores_por_finca(finca_id)
            sector_values = ["Todos"] + [f"{s[0]} - {s[1]}" for s in sectores]
            self.cmb_sector.configure(values=sector_values, state="normal")
            self.cmb_sector.set("Todos")
            
            lotes = get_lotes_por_finca(finca_id)
            lote_values = ["Todos"] + [f"{l[0]} - {l[1]}" for l in lotes]
            self.cmb_lote.configure(values=lote_values, state="normal")
            self.cmb_lote.set("Todos")
            
            potreros = get_potreros_por_finca(finca_id)
            potrero_values = ["Todos"] + [f"{p[0]} - {p[1]}" for p in potreros]
            self.cmb_potrero.configure(values=potrero_values, state="normal")
            self.cmb_potrero.set("Todos")
            
        except Exception as e:
            print(f"Error cargando filtros dependientes: {e}")
    
    def _limpiar_filtros(self):
        self.cmb_sector.set("Todos")
        self.cmb_lote.set("Todos")
        self.cmb_potrero.set("Todos")
        self.cmb_categoria.set("Todas")
        self.search_entry.delete(0, 'end')
        self._aplicar_filtros()
    
    def _aplicar_filtros(self):
        try:
            self.lbl_status.configure(text="Cargando...")
            self.update()
            
            filters = {}
            
            finca_val = self.cmb_finca.get()
            if finca_val and '-' in finca_val:
                filters['finca_id'] = int(finca_val.split(' - ')[0])
            
            sector_val = self.cmb_sector.get()
            if sector_val and sector_val != "Todos" and '-' in sector_val:
                filters['sector_id'] = int(sector_val.split(' - ')[0])
            
            lote_val = self.cmb_lote.get()
            if lote_val and lote_val != "Todos" and '-' in lote_val:
                filters['lote_id'] = int(lote_val.split(' - ')[0])
            
            potrero_val = self.cmb_potrero.get()
            if potrero_val and potrero_val != "Todos" and '-' in potrero_val:
                filters['potrero_id'] = int(potrero_val.split(' - ')[0])
            
            cat_val = self.cmb_categoria.get()
            if cat_val and cat_val != "Todas":
                filters['categoria'] = cat_val
            
            search_query = self.search_entry.get().strip()
            
            self.current_data = buscar_animales(filters, search_query)
            self.current_filters = filters
            
            self._update_table()
            
            self.lbl_count.configure(text=f"{len(self.current_data)} animales")
            self.lbl_status.configure(text=f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")

            # Diagnóstico: resumen de carga
            try:
                print(f"[InventarioV2] _aplicar_filtros -> {len(self.current_data)} animales | filtros={filters} | search='{search_query}'")
            except Exception:
                pass
            
        except Exception as e:
            self.lbl_status.configure(text="Error al cargar")
            print(f"Error aplicando filtros: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_search_change(self, event):
        if self.search_timer:
            self.after_cancel(self.search_timer)
        self.search_timer = self.after(250, self._aplicar_filtros)
    
    def _update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, animal in enumerate(self.current_data):
            peso_inicial = animal.get('peso_nacimiento') or animal.get('peso_compra') or ''
            values = (
                animal.get('codigo', ''),
                animal.get('nombre', '') or '',
                animal.get('categoria', 'Sin categoría') or 'Sin categoría',
                animal.get('finca', '') or '',
                animal.get('sector', '') or '',
                animal.get('lote', '') or '',
                animal.get('potrero', '') or '',
                f"{(animal.get('ultimo_peso') or 0):.1f}",
                ("✓" if (animal.get('inventariado') or 0) == 1 else ""),
                animal.get('estado', ''),
                (animal.get('fecha_ultimo_peso') or '')[:10],
                f"{peso_inicial:.1f}" if isinstance(peso_inicial, (int, float)) else ''
            )
            
            estado = animal.get('estado', '')
            if estado == 'Inventariado':
                tags = ('inventariado',)
            else:
                tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            
            iid = str(animal.get('id', f"row-{i}"))
            self.tree.insert('', 'end', iid=iid, values=values, tags=tags)
    
    def _on_tree_select(self, event):
        selection = self.tree.selection()
        state = "normal" if selection else "disabled"
        for btn in self.action_buttons:
            btn.configure(state=state)
    
    def _get_selected_animal(self) -> Optional[Dict[str, Any]]:
        selection = self.tree.selection()
        if not selection:
            return None
        
        iid = selection[0]
        for animal in self.current_data:
            if str(animal['id']) == iid:
                return animal
        return None
    
    def _ver_animal(self):
        animal = self._get_selected_animal()
        if animal:
            try:
                # Asegurar compatibilidad de campos esperados por el modal
                data = dict(animal)
                if 'ultimo_peso' not in data:
                    data['ultimo_peso'] = animal.get('ultimo_peso') or 0
                from modules.animales.modal_ver_animal import ModalVerAnimal
                # Usar el toplevel como master para mayor estabilidad en Toplevels
                master = self.winfo_toplevel()
                ModalVerAnimal(master, data)
            except Exception as e:
                try:
                    import traceback
                    print("[InventarioV2][_ver_animal] Error al abrir modal Ver:")
                    traceback.print_exc()
                except Exception:
                    pass
                messagebox.showerror("Ver Animal", f"No se pudo abrir la ventana:\n{e}")
    
    def _editar_animal(self):
        animal = self._get_selected_animal()
        if animal:
            try:
                data = dict(animal)
                if 'ultimo_peso' not in data:
                    data['ultimo_peso'] = animal.get('ultimo_peso') or 0
                from modules.animales.modal_editar_animal import ModalEditarAnimal
                # Usar el toplevel como master para mayor estabilidad en Toplevels
                master = self.winfo_toplevel()
                ModalEditarAnimal(master, data, callback=self._aplicar_filtros)
            except Exception as e:
                try:
                    import traceback
                    print("[InventarioV2][_editar_animal] Error al abrir modal Editar:")
                    traceback.print_exc()
                except Exception:
                    pass
                messagebox.showerror("Editar Animal", f"No se pudo abrir la ventana de edición:\n{e}")

    def _reubicar_animal(self):
        animal = self._get_selected_animal()
        if animal:
            try:
                from modules.animales.modal_reubicar_animal import ModalReubicarAnimal
                ModalReubicarAnimal(self, animal, on_saved=self._aplicar_filtros)
            except Exception as e:
                messagebox.showerror("Reubicar", f"No se pudo abrir la ventana de reubicación:\n{e}")
    
    def _eliminar_animal(self):
        animal = self._get_selected_animal()
        if not animal:
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar {animal['codigo']}?"):
            try:
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM animal WHERE id = ?", (animal['id'],))
                    conn.commit()
                messagebox.showinfo("Éxito", "Animal eliminado")
                self._aplicar_filtros()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    # ==================== NUEVAS ACCIONES ====================
    def _exportar_actual(self):
        if not self.current_data:
            messagebox.showinfo("Exportar", "No hay datos para exportar")
            return
        try:
            ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")],
                                                title="Guardar Inventario")
            if not ruta:
                return
            headers = ["Código", "Nombre", "Categoría", "Finca", "Sector", "Lote", "Potrero", "Peso", "Inventariado", "Estado", "Fecha Últ. Peso", "Peso Inicial"]
            rows = []
            for a in self.current_data:
                peso_inicial = a.get('peso_nacimiento') or a.get('peso_compra') or ''
                rows.append([
                    a.get('codigo',''), a.get('nombre',''), a.get('categoria','Sin categoría'),
                    a.get('finca',''), a.get('sector',''), a.get('lote',''), a.get('potrero',''),
                    f"{(a.get('ultimo_peso') or 0):.1f}", ("✓" if (a.get('inventariado') or 0) == 1 else ""), a.get('estado',''), (a.get('fecha_ultimo_peso') or '')[:10],
                    f"{peso_inicial:.1f}" if isinstance(peso_inicial,(int,float)) else ''
                ])
            # Intentar Excel
            try:
                from openpyxl import Workbook
                wb = Workbook()
                ws = wb.active
                ws.append(headers)
                for r in rows:
                    ws.append(r)
                wb.save(ruta)
                messagebox.showinfo("Exportar", f"Archivo Excel guardado:\n{ruta}")
            except Exception:
                import csv
                ruta_csv = ruta.replace('.xlsx', '.csv')
                with open(ruta_csv, 'w', newline='', encoding='utf-8') as f:
                    w = csv.writer(f)
                    w.writerow(headers)
                    w.writerows(rows)
                messagebox.showinfo("Exportar", f"openpyxl no disponible. Exportado CSV:\n{ruta_csv}")
        except Exception as e:
            messagebox.showerror("Exportar", f"Error exportando:\n{e}")

    def _abrir_graficas(self):
        try:
            from modules.animales.ventana_graficas import VentanaGraficas
            VentanaGraficas(self, filters_iniciales=self.current_filters)
        except Exception as e:
            messagebox.showerror("Gráficas", f"No se pudo abrir ventana de gráficas:\n{e}")

    # Método público para refrescar desde otros módulos
    def refrescar_inventario_externo(self):
        try:
            self._aplicar_filtros()
        except Exception:
            pass

    def _asignar_categorias_faltantes(self):
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                # Heurística simple según sexo
                cur.execute("SELECT id, sexo FROM animal WHERE (categoria IS NULL OR categoria='' )")
                pendientes = cur.fetchall()
                if not pendientes:
                    messagebox.showinfo("Categorías", "No hay animales sin categoría.")
                    return
                asignados = 0
                for aid, sexo in pendientes:
                    sexo_norm = (sexo or '').lower()
                    if 'tor' in sexo_norm or sexo_norm.startswith('m'):
                        cat = 'Toro'
                    elif 'nov' in sexo_norm:
                        cat = 'Novillo'
                    elif 'terner' in sexo_norm:
                        cat = 'Ternero'
                    else:
                        cat = 'Vaca'
                    cur.execute("UPDATE animal SET categoria = ? WHERE id = ?", (cat, aid))
                    asignados += 1
                conn.commit()
            messagebox.showinfo("Categorías", f"Asignadas {asignados} categorías por defecto.")
            self._aplicar_filtros()
        except Exception as e:
            messagebox.showerror("Categorías", f"Error asignando categorías:\n{e}")
