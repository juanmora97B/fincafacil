import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List, Any, Optional
import sqlite3
from matplotlib.figure import Figure

try:
    from database import get_db_connection
except Exception:
    from database.database import get_db_connection

class RealizarInventarioFrame(ctk.CTkFrame):
    """
    Realizar Inventario
    - Seleccionar finca
    - Tabla animales con peso anterior, nuevo, diferencia
    - Guardar pesajes y marcar inventariado
    """
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self._build_ui()
        self.pesajes_cache = {}  # finca_id -> {codigo: peso_nuevo}
        self._ensure_historial_schema()
        self._load_fincas()
        self._load_animales()

    def _build_ui(self):
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(header, text="🧮 Realizar Inventario", font=("Segoe UI", 20, "bold")).pack(side="left", padx=8)
        self.cmb_finca = ctk.CTkComboBox(header, width=220, command=lambda *_: self._load_animales())
        self.cmb_finca.pack(side="left", padx=8)
        self.entry_buscar = ctk.CTkEntry(header, width=220, placeholder_text="Buscar código o nombre...")
        self.entry_buscar.pack(side="right", padx=8)
        self.entry_buscar.bind("<KeyRelease>", lambda *_: self._apply_search())

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=8, pady=8)
        cols = ["codigo","nombre","peso_anterior","peso_nuevo","diferencia","inventariado"]
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for c in cols:
            heading_text = c.replace('_',' ').title()
            if c == "inventariado":
                heading_text = "Inventariado (✓)"
            self.tree.heading(c, text=heading_text, anchor='center', command=lambda col=c: self._sort_by(col))
            self.tree.column(c, width=120, anchor='center', stretch=True)
        self.tree.pack(fill="both", expand=True, side="left")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(fill="y", side="right")
        self.tree.bind("<Double-1>", self._edit_weight)

        acciones = ctk.CTkFrame(self)
        acciones.pack(fill="x", padx=8, pady=(0,8))
        ctk.CTkButton(acciones, text="🔄 Actualizar", command=self._refresh_inventory, fg_color="#1976D2").pack(side="left", padx=6)
        ctk.CTkButton(acciones, text="Marcar Inventariado", command=self._mark_inventoried).pack(side="left", padx=6)
        ctk.CTkButton(acciones, text="Guardar Pesajes", command=self._save_weights).pack(side="left", padx=6)
        ctk.CTkButton(acciones, text="Gráfico Inventariados", command=self._show_invent_chart).pack(side="left", padx=6)

        # Almacen temporal para nuevos pesos (solo finca activa)
        self.nuevos_pesos = {}  # codigo -> peso_nuevo
        ctk.CTkButton(acciones, text="Exportar CSV", command=self._export_inventory).pack(side="left", padx=6)
        ctk.CTkButton(acciones, text="Historial Inventarios", command=self._view_history).pack(side="left", padx=6)

    def _sort_by(self, column: str):
        try:
            data = [(self.tree.set(k, column), k) for k in self.tree.get_children("")]
            data.sort()
            for index, (_, k) in enumerate(data):
                self.tree.move(k, "", index)
        except Exception:
            pass

    def _load_fincas(self):
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM finca ORDER BY nombre")
                fincas = []
                for r in cur.fetchall():
                    try:
                        fid = r['id'] if hasattr(r, 'keys') else r[0]
                        fname = r['nombre'] if hasattr(r, 'keys') else r[1]
                        fincas.append(f"{fid} - {fname}")
                    except (KeyError, IndexError):
                        continue
            self.cmb_finca.configure(values=fincas)
            if fincas:
                self.cmb_finca.set(fincas[0])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar fincas:\n{e}")

    def _load_animales(self):
        self.tree.delete(*self.tree.get_children())
        try:
            finca_id = self._get_finca_id()
            sql = (
                "SELECT codigo, nombre, ultimo_peso, inventariado FROM animal "
                "WHERE (? IS NULL OR id_finca = ?) ORDER BY codigo"
            )
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, (finca_id, finca_id))
                rows = cur.fetchall()
            for r in rows:
                try:
                    codigo = r['codigo'] if hasattr(r, 'keys') else r[0]
                    nombre = r['nombre'] if hasattr(r, 'keys') else r[1]
                    peso_ant = r['ultimo_peso'] if hasattr(r, 'keys') else r[2]
                    inventariado = r['inventariado'] if hasattr(r, 'keys') else r[3]
                except (KeyError, IndexError):
                    continue
                peso_ant = peso_ant or 0
                icon = "✓" if (inventariado or 0) == 1 else ""
                # Recuperar peso no guardado si existe en cache
                peso_nuevo_cached = None
                if finca_id in self.pesajes_cache:
                    peso_nuevo_cached = self.pesajes_cache[finca_id].get(codigo)
                if peso_nuevo_cached is not None:
                    dif = peso_nuevo_cached - peso_ant
                    self.tree.insert("", "end", values=[codigo, nombre, peso_ant, peso_nuevo_cached, f"{dif:+.2f}", icon])
                else:
                    self.tree.insert("", "end", values=[codigo, nombre, peso_ant, "", "", icon])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar animales:\n{e}")

    def _refresh_inventory(self):
        """Refresca la lista de fincas y animales"""
        try:
            self._load_fincas()
            self._load_animales()
            messagebox.showinfo("Actualizar", "Inventario actualizado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el inventario:\n{e}")

    def _apply_search(self):
        texto = (self.entry_buscar.get() or '').lower()
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, 'values')
            visible = any(texto in str(v).lower() for v in vals[:2])
            if visible:
                self.tree.reattach(iid, "", "end")
            else:
                self.tree.detach(iid)

    def _edit_weight(self, *_):
        sel = self.tree.focus()
        if not sel:
            return
        vals_tuple = self.tree.item(sel, 'values')
        vals: List[Any] = list(vals_tuple) if vals_tuple else []
        codigo = str(vals[0]) if vals else ""
        peso_ant = float(vals[2] or 0) if len(vals) > 2 else 0.0
        top = ctk.CTkToplevel(self)
        top.title(f"Peso nuevo - {codigo}")
        ctk.CTkLabel(top, text=f"Peso anterior: {peso_ant} kg").pack(padx=8, pady=(10,4))
        entry = ctk.CTkEntry(top, width=180)
        entry.pack(padx=8, pady=8)
        def guardar():
            try:
                peso_nuevo = float(entry.get())
                dif = peso_nuevo - peso_ant
                vals[3] = str(peso_nuevo)
                vals[4] = f"{dif:+.2f}"
                self.tree.item(sel, values=vals)
                self.nuevos_pesos[codigo] = peso_nuevo
                finca_id = self._get_finca_id()
                if finca_id is not None:
                    self.pesajes_cache.setdefault(finca_id, {})[codigo] = peso_nuevo
                # Colorear fila
                tags = ['gain'] if dif > 0 else ['loss'] if dif < 0 else []
                prev_tags = set(self.tree.item(sel, 'tags') or [])
                self.tree.item(sel, tags=list(prev_tags.union(tags)))
                top.destroy()
            except Exception:
                messagebox.showwarning("Peso", "Ingrese un número válido")
        ctk.CTkButton(top, text="Guardar", command=guardar).pack(pady=8)
        # Configurar estilos
        try:
            self.tree.tag_configure('gain', background='#d2ffd2')
            self.tree.tag_configure('loss', background='#ffd2d2')
        except Exception:
            pass

    def _mark_inventoried(self):
        sel = self.tree.focus()
        if not sel:
            return
        vals = list(self.tree.item(sel, 'values'))
        codigo = vals[0]
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE animal SET inventariado = 1 WHERE codigo = ?", (codigo,))
                conn.commit()
            vals[5] = "✓"
            prev_tags = set(self.tree.item(sel, 'tags') or [])
            self.tree.item(sel, values=vals, tags=list(prev_tags.union({'invent'})))
            try:
                self.tree.tag_configure('invent', background='#e6f7ff')
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo marcar inventariado:\n{e}")

    def _save_weights(self):
        if not self.nuevos_pesos:
            messagebox.showinfo("Pesos", "No hay cambios")
            return
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                fecha = datetime.now().strftime('%Y-%m-%d')
                for codigo, peso in self.nuevos_pesos.items():
                    # Obtener id animal
                    cur.execute("SELECT id FROM animal WHERE codigo = ?", (codigo,))
                    row = cur.fetchone()
                    if not row:
                        continue
                    try:
                        animal_id = row['id'] if hasattr(row, 'keys') else row[0]
                    except (KeyError, IndexError):
                        continue
                    # Registrar/actualizar pesaje
                    cur.execute(
                        "INSERT INTO peso (animal_id, fecha, peso) VALUES (?, ?, ?) "
                        "ON CONFLICT(animal_id, fecha) DO UPDATE SET peso=excluded.peso",
                        (animal_id, fecha, peso)
                    )
                    # Actualizar ultimo_peso y fecha
                    cur.execute(
                        "UPDATE animal SET ultimo_peso = ?, fecha_ultimo_peso = ? WHERE id = ?",
                        (peso, fecha, animal_id)
                    )
                # Registrar snapshot completo del inventario (todas las filas visibles)
                finca_id = self._get_finca_id()
                for iid in self.tree.get_children():
                    v = self.tree.item(iid, 'values')
                    try:
                        codigo, nombre, peso_ant, peso_nuevo, dif, inventariado_icon = v
                        peso_ant = float(peso_ant or 0)
                        peso_nuevo_val = float(peso_nuevo) if str(peso_nuevo).strip() != '' else peso_ant
                        dif_val = peso_nuevo_val - peso_ant
                        invent_int = 1 if str(inventariado_icon).strip() == '✓' else 0
                        cur.execute(
                            "INSERT INTO inventario_historial (fecha, finca_id, codigo, peso_anterior, peso_nuevo, diferencia, inventariado) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (fecha, finca_id, codigo, peso_ant, peso_nuevo_val, dif_val, invent_int)
                        )
                    except Exception:
                        continue
                conn.commit()
            messagebox.showinfo("Pesos", "Pesajes guardados")
            self.nuevos_pesos.clear()
            finca_id = self._get_finca_id()
            if finca_id in self.pesajes_cache:
                self.pesajes_cache[finca_id].clear()
            self._load_animales()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar pesajes:\n{e}")

    def _show_invent_chart(self):
        # Grafico inventariados vs faltantes para la finca seleccionada
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            finca_id = None
            val = self.cmb_finca.get()
            if val and '-' in val:
                try:
                    finca_id = int(val.split(' - ')[0])
                except Exception:
                    finca_id = None
            with get_db_connection() as conn:
                cur = conn.cursor()
                if finca_id:
                    cur.execute("SELECT SUM(inventariado=1), SUM(inventariado=0) FROM animal WHERE id_finca = ?", (finca_id,))
                else:
                    cur.execute("SELECT SUM(inventariado=1), SUM(inventariado=0) FROM animal")
                inv, noinv = cur.fetchone()
            inv = inv or 0; noinv = noinv or 0
            top = ctk.CTkToplevel(self)
            top.title("Inventariados vs Faltantes")
            fig = Figure(figsize=(4,3))
            ax = fig.add_subplot(111)
            ax.bar(["Inventariados","Faltantes"], [inv, noinv], color=['#4caf50','#f44336'])
            for i, v in enumerate([inv, noinv]):
                ax.text(i, v, str(v), ha='center', va='bottom')
            canvas = FigureCanvasTkAgg(fig, master=top)
            canvas.get_tk_widget().pack(fill='both', expand=True)
            canvas.draw()
        except Exception:
            # Fallback texto
            try:
                finca_id = None
                val = self.cmb_finca.get()
                if val and '-' in val:
                    finca_id = int(val.split(' - ')[0])
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    if finca_id:
                        cur.execute("SELECT SUM(inventariado=1), SUM(inventariado=0) FROM animal WHERE id_finca = ?", (finca_id,))
                    else:
                        cur.execute("SELECT SUM(inventariado=1), SUM(inventariado=0) FROM animal")
                    inv, noinv = cur.fetchone()
                top = ctk.CTkToplevel(self)
                top.title("Inventariados vs Faltantes")
                lbl = ctk.CTkLabel(top, text=f"Inventariados: {inv or 0}\nFaltantes: {noinv or 0}\n(Instala matplotlib para ver gráfico)")
                lbl.pack(padx=8, pady=8)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo mostrar gráfico: {e}")

    # -------------------- NUEVAS FUNCIONES --------------------
    def _get_finca_id(self) -> Optional[int]:
        val = self.cmb_finca.get()
        if val and '-' in val:
            try:
                return int(val.split(' - ')[0])
            except Exception:
                return None
        return None

    def _ensure_historial_schema(self):
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS inventario_historial (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT NOT NULL,
                        finca_id INTEGER,
                        codigo TEXT NOT NULL,
                        peso_anterior REAL,
                        peso_nuevo REAL,
                        diferencia REAL,
                        inventariado INTEGER DEFAULT 0
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_historial_fecha ON inventario_historial(fecha)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_historial_finca ON inventario_historial(finca_id)")
                conn.commit()
        except Exception:
            pass

    def _export_inventory(self):
        try:
            if not self.tree.get_children():
                messagebox.showinfo("Exportar", "No hay datos para exportar")
                return
            path = filedialog.asksaveasfilename(title="Exportar Inventario", defaultextension=".csv", filetypes=[("CSV","*.csv")])
            if not path:
                return
            import csv
            cols = ["codigo","nombre","peso_anterior","peso_nuevo","diferencia","inventariado"]
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow([c.replace('_',' ').title() for c in cols])
                for iid in self.tree.get_children():
                    writer.writerow(self.tree.item(iid,'values'))
            messagebox.showinfo("Exportar", f"Inventario exportado a {path}")
        except Exception as e:
            messagebox.showerror("Exportar", f"No se pudo exportar: {e}")

    def _view_history(self):
        try:
            finca_id = self._get_finca_id()
            top = ctk.CTkToplevel(self)
            top.title("Historial Inventarios")
            frame = ctk.CTkFrame(top)
            frame.pack(fill='both', expand=True, padx=8, pady=8)
            # Selector de fecha
            lista_fechas = []
            with get_db_connection() as conn:
                cur = conn.cursor()
                if finca_id is None:
                    cur.execute("SELECT DISTINCT fecha FROM inventario_historial ORDER BY fecha DESC LIMIT 200")
                else:
                    cur.execute("SELECT DISTINCT fecha FROM inventario_historial WHERE finca_id = ? ORDER BY fecha DESC LIMIT 200", (finca_id,))
                for r in cur.fetchall():
                    try:
                        fecha = r['fecha'] if hasattr(r, 'keys') else r[0]
                        lista_fechas.append(fecha)
                    except (KeyError, IndexError):
                        continue
            self.combo_historial_fechas = ctk.CTkComboBox(frame, values=lista_fechas or [""], width=200)
            if lista_fechas:
                self.combo_historial_fechas.set(lista_fechas[0])
            self.combo_historial_fechas.pack(padx=4, pady=4, anchor='w')
            hist_cols = ["codigo","peso_anterior","peso_nuevo","diferencia","inventariado"]
            tree_hist = ttk.Treeview(frame, columns=hist_cols, show='headings', height=18)
            for c in hist_cols:
                tree_hist.heading(c, text=c.replace('_',' ').title())
                tree_hist.column(c, width=120)
            tree_hist.pack(fill='both', expand=True, padx=4, pady=4)
            vsb = ttk.Scrollbar(frame, orient='vertical', command=tree_hist.yview)
            tree_hist.configure(yscrollcommand=vsb.set)
            vsb.pack(side='right', fill='y')

            def cargar_detalle(*_):
                tree_hist.delete(*tree_hist.get_children())
                fecha_sel = self.combo_historial_fechas.get()
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    if finca_id is None:
                        cur.execute("SELECT codigo, peso_anterior, peso_nuevo, diferencia, inventariado FROM inventario_historial WHERE fecha = ? ORDER BY codigo", (fecha_sel,))
                    else:
                        cur.execute("SELECT codigo, peso_anterior, peso_nuevo, diferencia, inventariado FROM inventario_historial WHERE fecha = ? AND finca_id = ? ORDER BY codigo", (fecha_sel, finca_id))
                    for r in cur.fetchall():
                        try:
                            codigo = r[0] if not isinstance(r, sqlite3.Row) else r["codigo"]
                            pa = r[1] if not isinstance(r, sqlite3.Row) else r["peso_anterior"]
                            pn = r[2] if not isinstance(r, sqlite3.Row) else r["peso_nuevo"]
                            dif = r[3] if not isinstance(r, sqlite3.Row) else r["diferencia"]
                            inv = r[4] if not isinstance(r, sqlite3.Row) else r["inventariado"]

                            def fmt_num(x):
                                if x is None:
                                    return ""
                                try:
                                    return f"{float(x):.2f}"
                                except Exception:
                                    return str(x)

                            values = (
                                str(codigo or ""),
                                fmt_num(pa),
                                fmt_num(pn),
                                fmt_num(dif if dif is not None else (float(pn or 0) - float(pa or 0))),
                                "Sí" if (inv or 0) else "No",
                            )
                            tree_hist.insert('', 'end', values=values)
                        except Exception:
                            # Fallback en caso de estructura inesperada
                            tree_hist.insert('', 'end', values=(str(r[0]), str(r[1]), str(r[2]), str(r[3]), str(r[4])))
            self.combo_historial_fechas.configure(command=cargar_detalle)
            cargar_detalle()
        except Exception as e:
            messagebox.showerror("Historial", f"No se pudo abrir historial: {e}")
