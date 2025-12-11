import customtkinter as ctk
from tkinter import ttk, messagebox
import re
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db

class BitacoraReubicacionesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self._potrero_filter_values = []
        self.crear_widgets()
        self.cargar_fincas_filtro()
        self.cargar_potreros_filtro()
        self._load_filters_persisted()
        self.mostrar()

    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="📦 Bitácora de Reubicaciones", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Filtros
        filtros_frame = ctk.CTkFrame(self)
        filtros_frame.pack(fill="x", padx=10, pady=5)

        self.entry_fecha_desde = ctk.CTkEntry(filtros_frame, placeholder_text="Desde (YYYY-MM-DD)", width=140)
        self.entry_fecha_desde.pack(side="left", padx=5)
        self.entry_fecha_hasta = ctk.CTkEntry(filtros_frame, placeholder_text="Hasta (YYYY-MM-DD)", width=140)
        self.entry_fecha_hasta.pack(side="left", padx=5)
        self.combo_finca_filter = ctk.CTkComboBox(filtros_frame, width=160)
        self.combo_finca_filter.pack(side="left", padx=5)
        self.combo_potrero_filter = ctk.CTkComboBox(filtros_frame, width=160)
        self.combo_potrero_filter.pack(side="left", padx=5)
        self.entry_motivo_filter = ctk.CTkEntry(filtros_frame, placeholder_text="Motivo contiene...", width=180)
        self.entry_motivo_filter.pack(side="left", padx=5)
        ctk.CTkButton(filtros_frame, text="Aplicar Filtros", command=self.mostrar).pack(side="left", padx=5)
        ctk.CTkButton(filtros_frame, text="Limpiar", command=self.limpiar_filtros).pack(side="left", padx=5)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Contenedor para tabla y scrollbars
        table_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        table_container.pack(fill="both", expand=True)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Configurar tabla con scroll horizontal y vertical
        self.tabla = ttk.Treeview(table_container, 
                 columns=("codigo", "potrero_ant", "potrero_nuevo", "fecha", "motivo", "autor"), 
                     show="headings",
                     height=14)
        
        # Configurar columnas
        column_config = [
            ("codigo", "Código Animal", 120),
            ("potrero_ant", "Potrero Anterior", 150),
            ("potrero_nuevo", "Potrero Nuevo", 150),
            ("fecha", "Fecha", 120),
            ("motivo", "Motivo", 200),
            ("autor", "Autor", 140)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        # Usar grid para colocar scrollbars sin solapar
        self.tabla.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(table_container, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(table_container, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        # Botón actualizar
        btn_actualizar = ctk.CTkButton(self, text="🔄 Actualizar Lista", command=self.mostrar)
        btn_actualizar.pack(pady=5)

    def mostrar(self):
        """Muestra el historial de reubicaciones con filtros y parseo de metadata."""
        # Limpiar tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        fecha_desde = self.entry_fecha_desde.get().strip()
        fecha_hasta = self.entry_fecha_hasta.get().strip()
        potrero_filtro = self.combo_potrero_filter.get().strip()
        finca_filtro = self.combo_finca_filter.get().strip()
        motivo_substr = self.entry_motivo_filter.get().strip()
        if potrero_filtro.lower() == "todos": potrero_filtro = ""
        if finca_filtro.lower() == "todos": finca_filtro = ""

        # Preferir tabla reubicacion; si filtros no producen resultados, se hará fallback a comentarios parseados
        condiciones = ["1=1"]
        params = []

        def _valid_date(s):
            if not s: return False
            try:
                from datetime import datetime as _dt
                _dt.strptime(s, "%Y-%m-%d")
                return True
            except Exception:
                return False

        if _valid_date(fecha_desde):
            condiciones.append("r.fecha >= ?")
            params.append(fecha_desde)
        if _valid_date(fecha_hasta):
            condiciones.append("r.fecha <= ?")
            params.append(fecha_hasta)

        # Filtros adicionales
        if finca_filtro:
            condiciones.append("f.nombre = ?")
            params.append(finca_filtro)
        if motivo_substr:
            condiciones.append("COALESCE(r.motivo, '') LIKE ?")
            params.append(f"%{motivo_substr}%")

        where_sql = " AND ".join(condiciones)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # Primero intentar obtener desde la tabla reubicacion
                cursor.execute(f"""
                    SELECT a.codigo, r.fecha, COALESCE(r.from_potrero, '-'), COALESCE(r.to_potrero, '-'), COALESCE(r.motivo, ''), COALESCE(r.autor,''), f.nombre as finca
                    FROM reubicacion r
                    JOIN animal a ON r.animal_id = a.id
                    LEFT JOIN finca f ON a.id_finca = f.id
                    WHERE {where_sql}
                    ORDER BY r.fecha DESC
                """, params)

                rows = cursor.fetchall()
                if rows:
                    for codigo, fecha, potrero_ant, potrero_nuevo, motivo, autor, finca_nombre in rows:
                        if potrero_filtro and not (potrero_ant == potrero_filtro or potrero_nuevo == potrero_filtro):
                            continue
                        if len(motivo) > 100:
                            motivo = motivo[:100] + "..."
                        self.tabla.insert("", "end", values=(codigo, potrero_ant, potrero_nuevo, fecha, motivo, autor))
                else:
                    # Fallback: parsear desde comentarios
                    cursor.execute(f"""
                        SELECT a.codigo, c.fecha, c.comentario, f.nombre as finca
                        FROM comentario c
                        JOIN animal a ON c.animal_id = a.id
                        LEFT JOIN finca f ON a.id_finca = f.id
                        WHERE (c.comentario LIKE '%reubicación%' OR c.comentario LIKE '%potrero%' OR c.comentario LIKE '%Reubicación%' OR c.comentario LIKE '%traslado%')
                        ORDER BY c.fecha DESC
                    """)

                    patron_legacy = re.compile(r"REUBICACIÓN: De '([^']*)' a '([^']*)'\.")
                    patron_meta = re.compile(r"\[META\](\{.*\})", re.DOTALL)

                    for codigo, fecha, nota, finca_nombre in cursor.fetchall():
                        potrero_ant = "-"
                        potrero_nuevo = "-"
                        motivo_legible = nota
                        autor = ""
                        m_meta = patron_meta.search(nota)
                        if m_meta:
                            try:
                                meta = json.loads(m_meta.group(1))
                                potrero_ant = meta.get("from", potrero_ant)
                                potrero_nuevo = meta.get("to", potrero_nuevo)
                                motivo_legible = meta.get("motivo", motivo_legible.split('\n')[0])
                                autor = meta.get("autor", "")
                            except Exception:
                                pass
                        else:
                            m_legacy = patron_legacy.search(nota)
                            if m_legacy:
                                potrero_ant = m_legacy.group(1) or "Sin potrero"
                                potrero_nuevo = m_legacy.group(2) or "Sin potrero"

                        if potrero_filtro and not (potrero_ant == potrero_filtro or potrero_nuevo == potrero_filtro):
                            continue

                        motivo = motivo_legible
                        if len(motivo) > 100:
                            motivo = motivo[:100] + "..."

                        self.tabla.insert("", "end", values=(codigo, potrero_ant, potrero_nuevo, fecha, motivo, autor))

            # Persistir filtros actuales
            self._save_filters_persisted(fecha_desde, fecha_hasta, finca_filtro, potrero_filtro, motivo_substr)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las reubicaciones:\n{e}")

    def cargar_potreros_filtro(self):
        """Carga todos los potreros activos para filtro de búsqueda.
        Nota: Sistema limitado a 2 fincas activas (Finca El Prado, Finca El León)"""
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM potrero WHERE estado='Activo'")
                rows = [r[0] for r in cur.fetchall() if r and r[0]]
                self._potrero_filter_values = sorted(set(rows))
                self.combo_potrero_filter.configure(values=["Todos"] + self._potrero_filter_values)
                if not self.combo_potrero_filter.get():
                    self.combo_potrero_filter.set("Todos")
        except Exception:
            self.combo_potrero_filter.configure(values=["Todos"])
            self.combo_potrero_filter.set("Todos")

    def limpiar_filtros(self):
        self.entry_fecha_desde.delete(0, "end")
        self.entry_fecha_hasta.delete(0, "end")
        self.entry_motivo_filter.delete(0, "end")
        self.combo_potrero_filter.set("Todos")
        self.combo_finca_filter.set("Todos")
        self.mostrar()

    # ---------------- Persistencia de filtros -----------------
    def cargar_fincas_filtro(self):
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM finca WHERE estado='Activa' OR estado='Activo'")
                rows = [r[0] for r in cur.fetchall() if r and r[0]]
                valores = sorted(set(rows))
                self.combo_finca_filter.configure(values=["Todos"] + valores)
                self.combo_finca_filter.set("Todos")
        except Exception:
            self.combo_finca_filter.configure(values=["Todos"])
            self.combo_finca_filter.set("Todos")

    def _save_filters_persisted(self, fd, fh, finca, potrero, motivo):
        import json as _json
        data = {"fecha_desde": fd, "fecha_hasta": fh, "finca": finca, "potrero": potrero, "motivo": motivo}
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE app_settings SET valor=? WHERE clave='bitacora_reubicaciones_filters'", (_json.dumps(data, ensure_ascii=False),))
                if cur.rowcount == 0:
                    cur.execute("INSERT INTO app_settings (clave, valor) VALUES (?, ?)", ("bitacora_reubicaciones_filters", _json.dumps(data, ensure_ascii=False)))
                conn.commit()
        except Exception:
            pass

    def _load_filters_persisted(self):
        import json as _json
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT valor FROM app_settings WHERE clave='bitacora_reubicaciones_filters'")
                row = cur.fetchone()
                if row and row[0]:
                    data = _json.loads(row[0])
                    if data.get("fecha_desde"): self.entry_fecha_desde.insert(0, data["fecha_desde"])
                    if data.get("fecha_hasta"): self.entry_fecha_hasta.insert(0, data["fecha_hasta"])
                    if data.get("motivo"): self.entry_motivo_filter.insert(0, data["motivo"])
                    # After fincas/potreros loaded, set values if present
                    finca = data.get("finca") or "Todos"
                    potrero = data.get("potrero") or "Todos"
                    self.combo_finca_filter.set(finca if finca else "Todos")
                    self.combo_potrero_filter.set(potrero if potrero else "Todos")
        except Exception:
            pass