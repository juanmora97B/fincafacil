import os
import sys
import sqlite3
from datetime import datetime, timedelta
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk

# Asegurar imports relativos al workspace
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.utils.date_picker import attach_date_picker
from database.database import get_db_connection

print(f"[Bitácora] Módulo bitacora_comentarios cargado: {__file__}")


class BitacoraComentarios(ctk.CTkFrame):
    """Bitácora de Comentarios profesional para animales.
    - Encabezado compacto con badges de estado y categoría
    - Formulario de nuevo comentario con date picker y adjuntos
    - Filtros rápidos y detallados
    - Tabla `ttk.Treeview` con tags de colores por tipo
    - Detalle/editar/eliminar
    - Indicadores en tarjetas
    - Exportación a TXT y galería de adjuntos
    """

    def __init__(self, master, animal_codigo: str = ""):
        super().__init__(master)
        print("[Bitácora] Inicializando BitacoraComentariosFrame")
        self.animal_codigo = (animal_codigo or "").strip()
        self.animal_id = None

        self._build_ui()
        self._load_animal_header()
        self._load_comments()
        self._compute_indicators()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Encabezado
        header = ctk.CTkFrame(container, fg_color=("#f5f5f5", "#2b2b2b"), corner_radius=10)
        header.pack(fill="x", padx=6, pady=(0, 8))
        ctk.CTkLabel(header, text="📝 Bitácora de Comentarios", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 8), columnspan=2)
        
        # Búsqueda de Animal
        search_frame = ctk.CTkFrame(header, fg_color="transparent")
        search_frame.grid(row=0, column=2, columnspan=2, sticky="e", padx=12, pady=(10, 8))
        ctk.CTkLabel(search_frame, text="🔍 Buscar Animal:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 8))
        self.combo_animal_search = ctk.CTkComboBox(search_frame, width=220, values=[""])
        self.combo_animal_search.set("Código o Nombre...")
        self.combo_animal_search.pack(side="left", padx=(0, 8))
        self.combo_animal_search.bind("<KeyRelease>", self._on_animal_search)
        ctk.CTkButton(search_frame, text="Cargar", width=70, height=32, command=self._load_selected_animal).pack(side="left")

        self.header_vars = {k: ctk.StringVar(value="-") for k in ["codigo", "nombre", "finca", "potrero", "estado", "categoria"]}
        self._grid_kv(header, 1, "Código", self.header_vars['codigo'])
        self._grid_kv(header, 2, "Nombre", self.header_vars['nombre'])
        self._grid_kv(header, 3, "Finca", self.header_vars['finca'])

        ctk.CTkLabel(header, text="Potrero:", font=("Segoe UI", 11, "bold"), text_color="gray").grid(row=1, column=2, sticky="e", padx=(20,4), pady=3)
        ctk.CTkLabel(header, textvariable=self.header_vars['potrero'], font=("Segoe UI", 11)).grid(row=1, column=3, sticky="w", padx=(0,12), pady=3)

        badge_frame = ctk.CTkFrame(header, fg_color="transparent")
        badge_frame.grid(row=2, column=2, columnspan=2, sticky="w", padx=(20,12), pady=3)
        ctk.CTkLabel(badge_frame, text="Estado:", font=("Segoe UI", 10, "bold"), text_color="gray").pack(side="left", padx=(0,4))
        self.badge_estado = ctk.CTkLabel(badge_frame, text="-", font=("Segoe UI", 10, "bold"), fg_color="#607D8B", corner_radius=8, padx=10, pady=3)
        self.badge_estado.pack(side="left", padx=2)
        ctk.CTkLabel(badge_frame, text="Categoría:", font=("Segoe UI", 10, "bold"), text_color="gray").pack(side="left", padx=(12,4))
        self.badge_categoria = ctk.CTkLabel(badge_frame, text="-", font=("Segoe UI", 10, "bold"), fg_color="#607D8B", corner_radius=8, padx=10, pady=3)
        self.badge_categoria.pack(side="left", padx=2)

        ctk.CTkFrame(header, height=1, fg_color="gray70").grid(row=4, column=0, columnspan=4, sticky="ew", padx=12, pady=(8,10))

        # Formulario
        form = ctk.CTkFrame(container, fg_color=("#f0f7ff", "#263238"), corner_radius=10)
        form.pack(fill="x", padx=6, pady=(0, 8))
        ctk.CTkLabel(form, text="✍️ Nuevo Comentario", font=("Segoe UI", 15, "bold")).grid(row=0, column=0, sticky="w", padx=8, pady=8, columnspan=4)

        tipos = [
            "General", "Observación", "Comportamiento", "Enfermedad / síntoma", "Tratamiento aplicado",
            "Revisión veterinaria", "Alimentación", "Reproducción", "Pesaje", "Advertencia / Nota importante"
        ]
        ctk.CTkLabel(form, text="Tipo").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.combo_tipo = ctk.CTkComboBox(form, values=tipos)
        self.combo_tipo.set("General")
        self.combo_tipo.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ctk.CTkLabel(form, text="Descripción").grid(row=2, column=0, sticky="ne", padx=6, pady=4)
        self.text_desc = ctk.CTkTextbox(form, width=520, height=140)
        self.text_desc.grid(row=2, column=1, columnspan=3, sticky="we", padx=6, pady=4)

        ctk.CTkLabel(form, text="Fecha").grid(row=3, column=0, sticky="e", padx=6, pady=4)
        fecha_frame = ctk.CTkFrame(form, fg_color="transparent")
        fecha_frame.grid(row=3, column=1, sticky="w", padx=6, pady=4)
        self.entry_fecha = ctk.CTkEntry(fecha_frame, width=120)
        self.entry_fecha.pack(side="left", padx=(0, 4))
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        attach_date_picker(fecha_frame, self.entry_fecha)

        ctk.CTkLabel(form, text="Usuario").grid(row=3, column=2, sticky="e", padx=6, pady=4)
        self.entry_usuario = ctk.CTkEntry(form)
        self.entry_usuario.grid(row=3, column=3, sticky="w", padx=6, pady=4)
        self.entry_usuario.insert(0, os.getenv("USERNAME") or "usuario")
        self.entry_usuario.configure(state="disabled")

        ctk.CTkLabel(form, text="Adjunto").grid(row=4, column=0, sticky="e", padx=6, pady=4)
        self.entry_adjunto = ctk.CTkEntry(form, width=380)
        self.entry_adjunto.grid(row=4, column=1, sticky="w", padx=6, pady=4)
        ctk.CTkButton(form, text="📎 Seleccionar archivo", command=self._pick_file).grid(row=4, column=2, sticky="w", padx=6, pady=4)

        ctk.CTkButton(form, text="💾 Guardar Comentario", fg_color="#1976D2", command=self._save_comment).grid(row=5, column=1, sticky="w", padx=6, pady=8)

        # Filtros
        filtros = ctk.CTkFrame(container, corner_radius=10)
        filtros.pack(fill="x", padx=6, pady=(0, 8))
        title_row = ctk.CTkFrame(filtros, fg_color="transparent")
        title_row.grid(row=0, column=0, columnspan=7, sticky="w", padx=12, pady=(10,8))
        ctk.CTkLabel(title_row, text="🔎 Filtros y Búsqueda", font=("Segoe UI", 15, "bold")).pack(side="left")
        self.lbl_resultados = ctk.StringVar(value="")
        ctk.CTkLabel(title_row, textvariable=self.lbl_resultados, font=("Segoe UI", 11), text_color="#1976D2").pack(side="left", padx=(15,0))

        quick = ctk.CTkFrame(filtros, fg_color="transparent")
        quick.grid(row=1, column=0, columnspan=7, sticky="w", padx=12, pady=(0,8))
        ctk.CTkLabel(quick, text="Período:", font=("Segoe UI", 10, "bold"), text_color="gray").pack(side="left", padx=(0,6))
        ctk.CTkButton(quick, text="Últimos 7 días", width=110, height=28, fg_color="#607D8B", command=lambda: self._filtro_rapido(7)).pack(side="left", padx=2)
        ctk.CTkButton(quick, text="Último mes", width=110, height=28, fg_color="#607D8B", command=lambda: self._filtro_rapido(30)).pack(side="left", padx=2)
        ctk.CTkButton(quick, text="3 meses", width=90, height=28, fg_color="#607D8B", command=lambda: self._filtro_rapido(90)).pack(side="left", padx=2)
        ctk.CTkButton(quick, text="Todo", width=80, height=28, fg_color="#607D8B", command=lambda: self._filtro_rapido(None)).pack(side="left", padx=2)

        tipos_vals = [
            "General", "Observación", "Comportamiento", "Enfermedad / síntoma", "Tratamiento aplicado",
            "Revisión veterinaria", "Alimentación", "Reproducción", "Pesaje", "Advertencia / Nota importante"
        ]
        self.entry_desde = ctk.CTkEntry(filtros, placeholder_text="Desde (YYYY-MM-DD)", width=130)
        self.entry_hasta = ctk.CTkEntry(filtros, placeholder_text="Hasta (YYYY-MM-DD)", width=130)
        self.combo_tipo_f = ctk.CTkComboBox(filtros, values=["Todos"] + tipos_vals, width=180)
        self.combo_tipo_f.set("Todos")
        self.entry_usuario_f = ctk.CTkEntry(filtros, placeholder_text="Usuario", width=120)
        self.entry_buscar = ctk.CTkEntry(filtros, placeholder_text="🔍 Buscar en descripción...", width=220)
        self.entry_buscar.bind("<KeyRelease>", lambda e: self._load_comments())
        self.entry_desde.grid(row=2, column=0, padx=6, pady=(0,10), sticky="ew")
        self.entry_hasta.grid(row=2, column=1, padx=6, pady=(0,10), sticky="ew")
        self.combo_tipo_f.grid(row=2, column=2, padx=6, pady=(0,10), sticky="ew")
        self.entry_usuario_f.grid(row=2, column=3, padx=6, pady=(0,10), sticky="ew")
        self.entry_buscar.grid(row=2, column=4, padx=6, pady=(0,10), sticky="ew")
        ctk.CTkButton(filtros, text="✓ Aplicar", command=self._load_comments, width=90, fg_color="#1976D2").grid(row=2, column=5, padx=6, pady=(0,10))
        ctk.CTkButton(filtros, text="✖ Limpiar", command=self._clear_filters, width=90, fg_color="#757575").grid(row=2, column=6, padx=6, pady=(0,10))

        # Tabla
        table_frame = ctk.CTkFrame(container, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=6, pady=(0,8))
        ctk.CTkLabel(table_frame, text="📋 Historial de Comentarios", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=12, pady=(10,8))

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("Bitacora.Treeview", background="white", foreground="black", rowheight=35, fieldbackground="white", borderwidth=0, font=('Segoe UI', 10))
        style.configure("Bitacora.Treeview.Heading", background="#1976D2", foreground="white", relief="flat", font=('Segoe UI', 11, 'bold'))
        style.map('Bitacora.Treeview', background=[('selected', '#1976D2')])

        cols = ("fecha", "tipo", "descripcion", "usuario", "adjunto")
        self.tabla = ttk.Treeview(table_frame, columns=cols, show="headings", style="Bitacora.Treeview", height=12)
        self.tabla.heading("fecha", text="📅 Fecha"); self.tabla.column("fecha", width=100, anchor="center")
        self.tabla.heading("tipo", text="🏷️ Tipo"); self.tabla.column("tipo", width=170)
        self.tabla.heading("descripcion", text="📝 Descripción"); self.tabla.column("descripcion", width=420)
        self.tabla.heading("usuario", text="👤 Usuario"); self.tabla.column("usuario", width=120)
        self.tabla.heading("adjunto", text="📎"); self.tabla.column("adjunto", width=60, anchor="center")
        self.tabla.pack(side="left", fill="both", expand=True, padx=(10,0), pady=(0,10))
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", padx=(0,10), pady=(0,10))

        # Tags de colores
        self.tabla.tag_configure('enfermedad', background='#FFEBEE')
        self.tabla.tag_configure('tratamiento', background='#E8F5E9')
        self.tabla.tag_configure('advertencia', background='#FFF3E0')
        self.tabla.tag_configure('reproduccion', background='#F3E5F5')
        self.tabla.tag_configure('pesaje', background='#E3F2FD')
        self.tabla.tag_configure('general', background='#F5F5F5')
        self.tabla.tag_configure('par', background='#FAFAFA')
        self.tabla.tag_configure('impar', background='white')

        # Acciones
        actions = ctk.CTkFrame(container, fg_color="transparent")
        actions.pack(fill="x", padx=6, pady=(0,8))
        ctk.CTkButton(actions, text="🔍 Ver Detalle", command=self._open_selected, width=120, height=36, fg_color="#1976D2").pack(side="left", padx=4)
        ctk.CTkButton(actions, text="🔄 Actualizar", command=self._load_comments, width=120, height=36, fg_color="#455A64").pack(side="left", padx=4)
        ctk.CTkButton(actions, text="📤 Exportar", command=self._exportar_txt, width=130, height=36, fg_color="#D32F2F").pack(side="left", padx=4)
        ctk.CTkButton(actions, text="📸 Ver Fotos", command=self._ver_galeria, width=120, height=36, fg_color="#7B1FA2").pack(side="left", padx=4)

        # Indicadores
        self.ind_frame = ctk.CTkFrame(container, corner_radius=10)
        self.ind_frame.pack(fill="x", padx=6, pady=(0,8))
        ctk.CTkLabel(self.ind_frame, text="📊 Resumen e Indicadores", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=12, pady=(10,8))
        cards = ctk.CTkFrame(self.ind_frame, fg_color="transparent")
        cards.pack(fill="x", padx=12, pady=(0,10))
        cards.grid_columnconfigure((0,1,2), weight=1)
        self.ind_last_tx = ctk.StringVar(value="-")
        self.ind_disease_month = ctk.StringVar(value="0")
        self.ind_weight_hist = ctk.StringVar(value="-")
        self.ind_births_hist = ctk.StringVar(value="-")
        self.ind_critical = ctk.StringVar(value="-")
        self._card(cards, 0, 0, "💊 Último Tratamiento", self.ind_last_tx, ("#E8F5E9", "#1B5E20"))
        self._card(cards, 0, 1, "🩺 Enfermedades (30d)", self.ind_disease_month, ("#FFEBEE", "#B71C1C"))
        self._card(cards, 0, 2, "⚠️ Eventos Críticos", self.ind_critical, ("#FFF3E0", "#E65100"), wrap=180)
        self._card(cards, 1, 0, "⚖️ Peso (Últimos 5)", self.ind_weight_hist, ("#E3F2FD", "#0D47A1"), colspan=2)
        self._card(cards, 1, 2, "🐄 Historial Partos", self.ind_births_hist, ("#F3E5F5", "#4A148C"), wrap=180)

    def _grid_kv(self, parent, row, key, var):
        ctk.CTkLabel(parent, text=f"{key}:", font=("Segoe UI", 11, "bold"), text_color="gray").grid(row=row, column=0, sticky="e", padx=(12,4), pady=3)
        ctk.CTkLabel(parent, textvariable=var, font=("Segoe UI", 11)).grid(row=row, column=1, sticky="w", padx=(0,12), pady=3)

    def _card(self, parent, r, c, title, var, colors, wrap=None, colspan=1):
        frame = ctk.CTkFrame(parent, fg_color=colors[0], corner_radius=8)
        frame.grid(row=r, column=c, padx=4, pady=4, sticky="ew", columnspan=colspan)
        ctk.CTkLabel(frame, text=title, font=("Segoe UI", 11, "bold")).pack(padx=10, pady=(8,2))
        ctk.CTkLabel(frame, textvariable=var, font=("Segoe UI", 10), wraplength=wrap or 0).pack(padx=10, pady=(2,8))

    # --------------------------------------------------------------- Data
    def set_animal_codigo(self, codigo: str):
        self.animal_codigo = (codigo or "").strip()
        self.animal_id = None
        for k in self.header_vars:
            self.header_vars[k].set("-")
        self._load_animal_header(); self._load_comments(); self._compute_indicators()

    def _on_animal_search(self, event=None):
        """Busca animales mientras se escribe en el combobox"""
        search_text = (self.combo_animal_search.get() or "").strip().lower()
        if not search_text or len(search_text) < 2:
            return
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT codigo, nombre 
                    FROM animal 
                    WHERE codigo LIKE ? OR nombre LIKE ?
                    ORDER BY codigo
                    LIMIT 20
                """, (f"%{search_text}%", f"%{search_text}%"))
                
                results = cur.fetchall()
                if results:
                    options = [f"{row['codigo']} - {row['nombre']}" if isinstance(row, sqlite3.Row) 
                              else f"{row[0]} - {row[1]}" for row in results]
                    self.combo_animal_search.configure(values=options)
        except Exception as e:
            print(f"Error en búsqueda: {e}")

    def _load_selected_animal(self):
        """Carga el animal seleccionado del combobox"""
        selected = (self.combo_animal_search.get() or "").strip()
        if not selected:
            messagebox.showwarning("Búsqueda", "Selecciona un animal primero")
            return
        
        # Extraer código del formato "CODIGO - NOMBRE"
        codigo = selected.split(" - ")[0].strip()
        self.set_animal_codigo(codigo)
        
    def _load_animal_header(self):
        if not self.animal_codigo:
            return
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT a.id, a.codigo, a.nombre, a.estado, a.categoria,
                       f.nombre as finca, p.nombre as potrero
                FROM animal a
                LEFT JOIN finca f ON a.id_finca = f.id
                LEFT JOIN potrero p ON a.id_potrero = p.id
                WHERE a.codigo = ?
            """, (self.animal_codigo,))
            row = cur.fetchone()
        if not row:
            messagebox.showerror("Bitácora", "Animal no encontrado")
            return
        try:
            self.animal_id = row['id'] if isinstance(row, sqlite3.Row) else row[0]
            self.header_vars['codigo'].set(row['codigo'] if isinstance(row, sqlite3.Row) else row[1])
            self.header_vars['nombre'].set((row['nombre'] if isinstance(row, sqlite3.Row) else row[2]) or "-")
            estado = (row['estado'] if isinstance(row, sqlite3.Row) else row[3]) or "-"
            categoria = (row['categoria'] if isinstance(row, sqlite3.Row) else row[4]) or "-"
            self.header_vars['finca'].set((row['finca'] if isinstance(row, sqlite3.Row) else row[5]) or "-")
            self.header_vars['potrero'].set((row['potrero'] if isinstance(row, sqlite3.Row) else row[6]) or "-")
            self._actualizar_badges(estado, categoria)
        except (KeyError, IndexError):
            pass

    def _actualizar_badges(self, estado, categoria):
        colores_estado = {"Activo": "#4CAF50", "Vendido": "#FF9800", "Muerto": "#F44336", "Descarte": "#9E9E9E"}
        self.badge_estado.configure(text=estado, fg_color=colores_estado.get(estado, "#607D8B"))
        colores_categoria = {"Vaca": "#E91E63", "Toro": "#2196F3", "Novilla": "#9C27B0", "Novillo": "#3F51B5", "Ternera": "#FF5722", "Ternero": "#00BCD4"}
        self.badge_categoria.configure(text=categoria, fg_color=colores_categoria.get(categoria, "#607D8B"))

    def _pick_file(self):
        path = filedialog.askopenfilename(title="Seleccionar adjunto", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg"), ("PDF", "*.pdf"), ("Todos", "*.*")])
        if path:
            self.entry_adjunto.delete(0, "end"); self.entry_adjunto.insert(0, path)

    def _save_comment(self):
        if not self.animal_id:
            messagebox.showwarning("Bitácora", "Primero seleccione un animal"); return
        tipo = self.combo_tipo.get().strip()
        desc = self.text_desc.get("1.0", "end-1c").strip()
        fecha = self.entry_fecha.get().strip() or datetime.now().strftime("%Y-%m-%d")
        usuario = self.entry_usuario.get().strip() or (os.getenv("USERNAME") or "usuario")
        adjunto = self.entry_adjunto.get().strip() or None
        if not desc:
            messagebox.showwarning("Bitácora", "Ingrese una descripción"); return
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO comentario (animal_id, fecha, tipo, comentario, usuario, adjunto)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.animal_id, fecha, tipo, desc, usuario, adjunto))
                conn.commit()
            messagebox.showinfo("Bitácora", "Comentario guardado")
            self._load_comments(); self._compute_indicators()
            self.text_desc.delete("1.0", "end"); self.entry_adjunto.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Bitácora", f"No se pudo guardar: {e}")

    def _clear_filters(self):
        self.entry_desde.delete(0, "end"); self.entry_hasta.delete(0, "end")
        self.combo_tipo_f.set("Todos"); self.entry_usuario_f.delete(0, "end"); self.entry_buscar.delete(0, "end")
        self._load_comments()

    def _filtro_rapido(self, dias):
        self.entry_desde.delete(0, "end"); self.entry_hasta.delete(0, "end")
        if dias:
            desde = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
            hasta = datetime.now().strftime("%Y-%m-%d")
            self.entry_desde.insert(0, desde); self.entry_hasta.insert(0, hasta)
        self._load_comments()

    def _load_comments(self):
        for iid in self.tabla.get_children(): self.tabla.delete(iid)
        if not self.animal_id: return
        condiciones, params = ["animal_id = ?"], [self.animal_id]
        def _valid_date(s):
            try:
                if not s: return False
                datetime.strptime(s, "%Y-%m-%d"); return True
            except Exception: return False
        desde = self.entry_desde.get().strip(); hasta = self.entry_hasta.get().strip()
        tipo_f = self.combo_tipo_f.get().strip(); usuario_f = self.entry_usuario_f.get().strip(); buscar = self.entry_buscar.get().strip()
        if _valid_date(desde): condiciones.append("fecha >= ?"); params.append(desde)
        if _valid_date(hasta): condiciones.append("fecha <= ?"); params.append(hasta)
        if tipo_f and tipo_f != "Todos": condiciones.append("tipo = ?"); params.append(tipo_f)
        if usuario_f: condiciones.append("usuario = ?"); params.append(usuario_f)
        if buscar: condiciones.append("comentario LIKE ?"); params.append(f"%{buscar}%")
        where_sql = " WHERE " + " AND ".join(condiciones)
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT fecha, tipo, comentario, usuario, adjunto, id
                FROM comentario
                {where_sql}
                ORDER BY fecha DESC
            """, tuple(params))
            rows = cur.fetchall()
        self.lbl_resultados.set(f"📊 {len(rows)} comentario(s)")
        for idx, r in enumerate(rows):
            try:
                if isinstance(r, sqlite3.Row):
                    fecha, tipo, com, usr, adj, cid = r['fecha'], r['tipo'], r['comentario'], r['usuario'], r['adjunto'], r['id']
                else:
                    fecha, tipo, com, usr, adj, cid = r[0], r[1], r[2], r[3], r[4], r[5]
                short = (com[:100] + "…") if com and len(com) > 100 else (com or "")
                tag = 'par' if idx % 2 == 0 else 'impar'
                if 'Enfermedad' in (tipo or '') or 'síntoma' in (tipo or ''): tag = 'enfermedad'
                elif 'Tratamiento' in (tipo or ''): tag = 'tratamiento'
                elif 'Advertencia' in (tipo or '') or 'importante' in (tipo or ''): tag = 'advertencia'
                elif 'Reproducción' in (tipo or ''): tag = 'reproduccion'
                elif 'Pesaje' in (tipo or ''): tag = 'pesaje'
                elif (tipo or '') == 'General': tag = 'general'
                self.tabla.insert("", "end", iid=f"c_{cid}", values=(fecha, tipo, short, usr, "📎" if adj else "-"), tags=(tag,))
            except (KeyError, IndexError):
                continue

    def _open_selected(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showinfo("Bitácora", "Seleccione un comentario"); return
        cid = int(sel[0].split('_')[-1])
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT fecha, tipo, comentario, usuario, adjunto FROM comentario WHERE id = ?", (cid,))
            r = cur.fetchone()
        if not r: return
        fecha, tipo, com, usr, adj = (r['fecha'], r['tipo'], r['comentario'], r['usuario'], r['adjunto']) if isinstance(r, sqlite3.Row) else (r[0], r[1], r[2], r[3], r[4])
        win = ctk.CTkToplevel(self); win.title("Detalle del comentario"); win.geometry("680x520")
        ctk.CTkLabel(win, text="Detalle del comentario", font=("Segoe UI", 16, "bold")).pack(pady=8)
        grid = ctk.CTkFrame(win); grid.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(grid, text=f"Fecha: {fecha}").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ctk.CTkLabel(grid, text=f"Tipo: {tipo}").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        ctk.CTkLabel(grid, text=f"Usuario: {usr}").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        ctk.CTkLabel(grid, text="Descripción:").grid(row=3, column=0, sticky="nw", padx=6, pady=4)
        txt = ctk.CTkTextbox(grid, width=560, height=240); txt.grid(row=3, column=1, sticky="we", padx=6, pady=4)
        txt.insert("1.0", com or ""); txt.configure(state="disabled")
        if adj: ctk.CTkButton(grid, text="Abrir adjunto", command=lambda: os.startfile(adj)).grid(row=4, column=1, sticky="w", padx=6, pady=8)
        btns = ctk.CTkFrame(win); btns.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btns, text="Editar", command=lambda: self._edit_comment(cid, win)).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Eliminar", fg_color="#c62828", command=lambda: self._delete_comment(cid, win)).pack(side="left", padx=6)

    def _edit_comment(self, cid: int, win=None):
        with get_db_connection() as conn:
            cur = conn.cursor(); cur.execute("SELECT fecha, tipo, comentario, usuario, adjunto FROM comentario WHERE id = ?", (cid,))
            r = cur.fetchone()
        if not r: return
        fecha, tipo, com, usr, adj = (r['fecha'], r['tipo'], r['comentario'], r['usuario'], r['adjunto']) if isinstance(r, sqlite3.Row) else (r[0], r[1], r[2], r[3], r[4])
        win2 = ctk.CTkToplevel(self); win2.title("Editar comentario"); win2.geometry("680x520")
        ctk.CTkLabel(win2, text="Editar comentario", font=("Segoe UI", 16, "bold")).pack(pady=8)
        grid = ctk.CTkFrame(win2); grid.pack(fill="both", expand=True, padx=10, pady=10)
        tipos = [
            "General", "Observación", "Comportamiento", "Enfermedad / síntoma", "Tratamiento aplicado",
            "Revisión veterinaria", "Alimentación", "Reproducción", "Pesaje", "Advertencia / Nota importante"
        ]
        ctk.CTkLabel(grid, text="Tipo").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        combo = ctk.CTkComboBox(grid, values=tipos); combo.set(tipo or "General"); combo.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ctk.CTkLabel(grid, text="Fecha").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        fecha_frame2 = ctk.CTkFrame(grid, fg_color="transparent"); fecha_frame2.grid(row=1, column=1, sticky="w", padx=6, pady=4)
        entry_fecha = ctk.CTkEntry(fecha_frame2, width=120); entry_fecha.pack(side="left", padx=(0,4))
        entry_fecha.insert(0, fecha or datetime.now().strftime("%Y-%m-%d")); attach_date_picker(fecha_frame2, entry_fecha)
        ctk.CTkLabel(grid, text="Descripción").grid(row=2, column=0, sticky="ne", padx=6, pady=4)
        text_desc = ctk.CTkTextbox(grid, width=520, height=160); text_desc.grid(row=2, column=1, columnspan=3, sticky="we", padx=6, pady=4)
        text_desc.insert("1.0", com or "")
        ctk.CTkLabel(grid, text="Adjunto").grid(row=3, column=0, sticky="e", padx=6, pady=4)
        entry_adj = ctk.CTkEntry(grid, width=360); entry_adj.grid(row=3, column=1, sticky="w", padx=6, pady=4)
        if adj: entry_adj.insert(0, adj)
        ctk.CTkButton(grid, text="📎 Seleccionar", command=lambda: self._set_file(entry_adj)).grid(row=3, column=2, sticky="w", padx=6, pady=4)
        def save_changes():
            tipo2 = combo.get().strip(); fecha2 = entry_fecha.get().strip(); desc2 = text_desc.get("1.0", "end-1c").strip(); adj2 = entry_adj.get().strip() or None
            with get_db_connection() as conn:
                cur = conn.cursor(); cur.execute("""
                    UPDATE comentario SET fecha=?, tipo=?, comentario=?, adjunto=? WHERE id=?
                """, (fecha2 or fecha, tipo2 or tipo, desc2 or com, adj2, cid)); conn.commit()
            messagebox.showinfo("Bitácora", "Comentario actualizado"); self._load_comments(); self._compute_indicators()
            try: win.destroy() if win else None
            except Exception: pass
            win2.destroy()
        ctk.CTkButton(win2, text="Guardar", fg_color="#1976D2", command=save_changes).pack(pady=8)

    def _set_file(self, entry: ctk.CTkEntry):
        path = filedialog.askopenfilename(title="Seleccionar adjunto", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg"), ("PDF", "*.pdf"), ("Todos", "*.*")])
        if path: entry.delete(0, "end"); entry.insert(0, path)

    def _delete_comment(self, cid: int, win=None):
        if not messagebox.askyesno("Bitácora", "¿Eliminar comentario?"): return
        with get_db_connection() as conn:
            cur = conn.cursor(); cur.execute("DELETE FROM comentario WHERE id = ?", (cid,)); conn.commit()
        messagebox.showinfo("Bitácora", "Eliminado"); self._load_comments(); self._compute_indicators()
        try: win.destroy() if win else None
        except Exception: pass

    # ------------------------------------------------------- Indicadores
    def _compute_indicators(self):
        if not self.animal_id: return
        with get_db_connection() as conn:
            cur = conn.cursor(); cur.execute("SELECT fecha FROM comentario WHERE animal_id=? AND tipo='Tratamiento aplicado' ORDER BY fecha DESC LIMIT 1", (self.animal_id,))
            r = cur.fetchone(); self.ind_last_tx.set((r['fecha'] if r and isinstance(r, sqlite3.Row) else (r[0] if r else None)) or "-")
        desde = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        with get_db_connection() as conn:
            cur = conn.cursor(); cur.execute("SELECT COUNT(*) FROM comentario WHERE animal_id=? AND tipo LIKE 'Enfermedad%' AND fecha >= ?", (self.animal_id, desde))
            r2 = cur.fetchone();
            try:
                val = r2[0] if r2 and not isinstance(r2, sqlite3.Row) else (r2['COUNT(*)'] if r2 else 0)
            except Exception:
                val = 0
            self.ind_disease_month.set(str(val or 0))
        with get_db_connection() as conn:
            cur = conn.cursor(); cur.execute("SELECT fecha, peso FROM peso WHERE animal_id=? ORDER BY fecha DESC LIMIT 5", (self.animal_id,))
            pesos = cur.fetchall()
        self.ind_weight_hist.set(" | ".join([f"{(r['fecha'] if isinstance(r, sqlite3.Row) else r[0])}:{(r['peso'] if isinstance(r, sqlite3.Row) else r[1])}" for r in pesos]) if pesos else "-")
        with get_db_connection() as conn:
            cur = conn.cursor(); cur.execute("SELECT fecha_parto_real FROM servicio WHERE id_hembra=? AND fecha_parto_real IS NOT NULL ORDER BY fecha_parto_real DESC LIMIT 5", (self.animal_id,))
            partos = cur.fetchall()
        self.ind_births_hist.set(" | ".join([(r['fecha_parto_real'] if isinstance(r, sqlite3.Row) else r[0]) for r in partos]) if partos else "-")
        with get_db_connection() as conn:
            cur = conn.cursor(); cur.execute("""
                SELECT fecha, tipo FROM comentario 
                WHERE animal_id=? AND tipo IN ('Advertencia / Nota importante','Enfermedad / síntoma') 
                  AND fecha >= ? ORDER BY fecha DESC
            """, (self.animal_id, (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")))
            crit = cur.fetchall()
        if crit:
            vals = []
            for r in crit:
                f = r['fecha'] if isinstance(r, sqlite3.Row) else r[0]
                t = r['tipo'] if isinstance(r, sqlite3.Row) else r[1]
                t_short = t.split('/')[0].strip() if '/' in t else t
                vals.append(f"{f} ({t_short})")
            self.ind_critical.set("\n".join(vals[:3]) if vals else "Ninguno")
        else:
            self.ind_critical.set("Ninguno en los últimos 14 días")

    # ----------------------------------------------- Exportar y galería
    def _exportar_txt(self):
        if not self.animal_codigo:
            messagebox.showwarning("Exportar", "Seleccione un animal primero"); return
        try:
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bitacora_{self.animal_codigo}_{fecha}.txt"
            ruta = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivo de texto", "*.txt"), ("Todos", "*.*")], initialfile=filename)
            if not ruta: return
            with get_db_connection() as conn:
                cur = conn.cursor(); cur.execute("""
                    SELECT fecha, tipo, comentario, usuario
                    FROM comentario WHERE animal_id = ? ORDER BY fecha DESC
                """, (self.animal_id,)); rows = cur.fetchall()
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write("BITÁCORA DE COMENTARIOS\n")
                f.write(f"Animal: {self.header_vars['codigo'].get()} - {self.header_vars['nombre'].get()}\n")
                f.write(f"Finca: {self.header_vars['finca'].get()}\n")
                f.write(f"Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write("="*80 + "\n\n")
                for r in rows:
                    fecha, tipo, com, usr = (r['fecha'], r['tipo'], r['comentario'], r['usuario']) if isinstance(r, sqlite3.Row) else (r[0], r[1], r[2], r[3])
                    f.write(f"Fecha: {fecha}\nTipo: {tipo}\nUsuario: {usr}\n")
                    f.write(f"Descripción:\n{com}\n" + "-"*80 + "\n\n")
            messagebox.showinfo("Éxito", f"Bitácora exportada a:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def _ver_galeria(self):
        if not self.animal_id:
            messagebox.showwarning("Galería", "Seleccione un animal primero"); return
        with get_db_connection() as conn:
            cur = conn.cursor(); cur.execute("""
                SELECT fecha, tipo, adjunto FROM comentario
                WHERE animal_id = ? AND adjunto IS NOT NULL AND adjunto != ''
                ORDER BY fecha DESC
            """, (self.animal_id,)); fotos = cur.fetchall()
        if not fotos:
            messagebox.showinfo("Galería", "No hay fotos adjuntas para este animal"); return
        win = ctk.CTkToplevel(self); win.title(f"Galería de Fotos - {self.header_vars['codigo'].get()}"); win.geometry("720x600")
        ctk.CTkLabel(win, text=f"📸 Galería de Fotos ({len(fotos)} archivo(s))", font=("Segoe UI", 16, "bold")).pack(pady=10)
        scroll_frame = ctk.CTkScrollableFrame(win); scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        for r in fotos:
            fecha, tipo, adj = (r['fecha'], r['tipo'], r['adjunto']) if isinstance(r, sqlite3.Row) else (r[0], r[1], r[2])
            card = ctk.CTkFrame(scroll_frame, fg_color=("#f5f5f5", "#2b2b2b"), corner_radius=8); card.pack(fill="x", pady=5, padx=5)
            info = ctk.CTkFrame(card, fg_color="transparent"); info.pack(fill="x", padx=10, pady=8)
            ctk.CTkLabel(info, text=f"{fecha} · {tipo}", font=("Segoe UI", 11, "bold")).pack(side="left")
            ctk.CTkButton(info, text="Abrir", width=80, command=lambda p=adj: os.startfile(p)).pack(side="right")

# Alias para mantener compatibilidad con integraciones existentes
BitacoraComentariosFrame = BitacoraComentarios
