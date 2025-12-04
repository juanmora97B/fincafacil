"""
Módulo de Gestión de Insumos e Inventario
Control de stock, entradas, salidas y alertas
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class InsumosModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_datos_iniciales()

    def crear_widgets(self):
        # Título compacto
        titulo = ctk.CTkLabel(self, text="📦 Gestión de Insumos e Inventario", 
                             font=("Segoe UI", 22, "bold"))
        titulo.pack(pady=(5, 3))

        # Notebook expandido para ocupar toda la altura disponible
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=(3, 5))

        # Tabs
        self.frame_inventario = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_inventario, text="📋 Inventario")
        
        self.frame_movimientos = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_movimientos, text="🔄 Movimientos")
        
        self.frame_alertas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_alertas, text="⚠️ Alertas")

        self.crear_inventario()
        self.crear_movimientos()
        self.crear_alertas()

    def crear_inventario(self):
        """Tab de inventario con registro y catálogo"""
        main = ctk.CTkScrollableFrame(self.frame_inventario)
        main.pack(fill="both", expand=True, padx=2, pady=5)

        # Formulario de registro
        ctk.CTkLabel(main, text="➕ Nuevo Insumo", font=("Segoe UI", 16, "bold")).pack(pady=(0, 5))
        
        form = ctk.CTkFrame(main, corner_radius=10)
        form.pack(fill="both", expand=True, pady=5)

        r1 = ctk.CTkFrame(form, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r1, text="Código*:", width=120).pack(side="left", padx=5)
        self.e_codigo = ctk.CTkEntry(r1, width=150)
        self.e_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(r1, text="Nombre*:", width=80).pack(side="left", padx=5)
        self.e_nombre = ctk.CTkEntry(r1, width=250)
        self.e_nombre.pack(side="left", padx=5)

        r2 = ctk.CTkFrame(form, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r2, text="Categoría*:", width=120).pack(side="left", padx=5)
        self.cb_categoria = ctk.CTkComboBox(r2, values=["Medicamento", "Alimento", "Fertilizante", "Semilla", "Herramienta", "Otro"], width=150)
        self.cb_categoria.pack(side="left", padx=5)
        ctk.CTkLabel(r2, text="Unidad*:", width=80).pack(side="left", padx=5)
        self.e_unidad = ctk.CTkEntry(r2, width=100)
        self.e_unidad.insert(0, "kg")
        self.e_unidad.pack(side="left", padx=5)

        r3 = ctk.CTkFrame(form, fg_color="transparent")
        r3.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r3, text="Stock Actual:", width=120).pack(side="left", padx=5)
        self.e_stock_actual = ctk.CTkEntry(r3, width=100)
        self.e_stock_actual.insert(0, "0")
        self.e_stock_actual.pack(side="left", padx=5)
        ctk.CTkLabel(r3, text="Mín:", width=50).pack(side="left", padx=5)
        self.e_stock_min = ctk.CTkEntry(r3, width=80)
        self.e_stock_min.insert(0, "10")
        self.e_stock_min.pack(side="left", padx=5)
        ctk.CTkLabel(r3, text="Máx:", width=50).pack(side="left", padx=5)
        self.e_stock_max = ctk.CTkEntry(r3, width=80)
        self.e_stock_max.pack(side="left", padx=5)

        r4 = ctk.CTkFrame(form, fg_color="transparent")
        r4.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r4, text="Precio Unit.:", width=120).pack(side="left", padx=5)
        self.e_precio = ctk.CTkEntry(r4, width=100)
        self.e_precio.pack(side="left", padx=5)
        ctk.CTkLabel(r4, text="Proveedor:", width=80).pack(side="left", padx=5)
        self.e_proveedor = ctk.CTkEntry(r4, width=200)
        self.e_proveedor.pack(side="left", padx=5)

        r5 = ctk.CTkFrame(form, fg_color="transparent")
        r5.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r5, text="Finca:", width=120).pack(side="left", padx=5)
        self.cb_finca_ins = ctk.CTkComboBox(r5, width=200)
        self.cb_finca_ins.pack(side="left", padx=5)
        ctk.CTkLabel(r5, text="Ubicación:", width=80).pack(side="left", padx=5)
        self.e_ubicacion = ctk.CTkEntry(r5, width=200)
        self.e_ubicacion.pack(side="left", padx=5)

        btn_f = ctk.CTkFrame(form, fg_color="transparent")
        btn_f.pack(pady=10)
        ctk.CTkButton(btn_f, text="💾 Guardar Insumo", command=self.guardar_insumo, 
                     fg_color="green").pack(side="left", padx=5)
        ctk.CTkButton(btn_f, text="🔄 Limpiar", command=self.limpiar_form_insumo).pack(side="left", padx=5)

        # Catálogo
        ctk.CTkLabel(main, text="📦 Catálogo de Insumos", font=("Segoe UI", 16, "bold")).pack(pady=10)
        # Filtro por finca
        filtro_frame = ctk.CTkFrame(main, fg_color="transparent")
        filtro_frame.pack(fill="x", padx=5, pady=(0,5))
        ctk.CTkLabel(filtro_frame, text="Filtrar Finca:", width=100).pack(side="left", padx=5)
        self.cb_finca_filtro = ctk.CTkComboBox(filtro_frame, width=220, values=["Todas"])
        self.cb_finca_filtro.set("Todas")
        self.cb_finca_filtro.pack(side="left", padx=5)
        ctk.CTkButton(filtro_frame, text="Aplicar", width=80, command=self._aplicar_filtro_finca).pack(side="left", padx=5)
        
        self.tabla_inv = ttk.Treeview(main, columns=("cod", "nom", "cat", "stock", "min", "unid", "precio"), 
                                      show="headings", height=12)
        for col, txt, w in [("cod", "Código", 100), ("nom", "Nombre", 200), ("cat", "Categoría", 120),
                            ("stock", "Stock", 80), ("min", "Mín", 70), ("unid", "Unidad", 80), ("precio", "Precio", 90)]:
            self.tabla_inv.heading(col, text=txt)
            self.tabla_inv.column(col, width=w, anchor="center")
        self.tabla_inv.pack(fill="both", expand=True, pady=10)

        btn_inv = ctk.CTkFrame(main, fg_color="transparent")
        btn_inv.pack(pady=5)
        ctk.CTkButton(btn_inv, text="🔍 Ver Detalles", command=self.ver_detalles_insumo).pack(side="left", padx=5)
        ctk.CTkButton(btn_inv, text="🗑️ Eliminar", command=self.eliminar_insumo, fg_color="#D32F2F").pack(side="left", padx=5)

    def crear_movimientos(self):
        """Tab de movimientos (entradas/salidas)"""
        main = ctk.CTkFrame(self.frame_movimientos)
        main.pack(fill="both", expand=True, padx=4, pady=10)

        ctk.CTkLabel(main, text="🔄 Registrar Movimiento", font=("Segoe UI", 16, "bold")).pack(pady=(0, 5))
        
        form = ctk.CTkFrame(main, corner_radius=10)
        form.pack(fill="both", expand=True, pady=5)

        r1 = ctk.CTkFrame(form, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r1, text="Insumo*:", width=120).pack(side="left", padx=5)
        self.cb_insumo_mov = ctk.CTkComboBox(r1, width=350)
        self.cb_insumo_mov.pack(side="left", padx=5)
        ctk.CTkButton(r1, text="🔄", command=self.cargar_insumos_combo, width=40).pack(side="left", padx=5)

        r2 = ctk.CTkFrame(form, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r2, text="Tipo*:", width=120).pack(side="left", padx=5)
        self.cb_tipo_mov = ctk.CTkComboBox(r2, values=["Entrada", "Salida", "Ajuste"], width=150)
        self.cb_tipo_mov.pack(side="left", padx=5)
        ctk.CTkLabel(r2, text="Cantidad*:", width=90).pack(side="left", padx=5)
        self.e_cantidad_mov = ctk.CTkEntry(r2, width=100)
        self.e_cantidad_mov.pack(side="left", padx=5)

        r3 = ctk.CTkFrame(form, fg_color="transparent")
        r3.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r3, text="Fecha:", width=120).pack(side="left", padx=5)
        self.e_fecha_mov = ctk.CTkEntry(r3, width=120)
        self.e_fecha_mov.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.e_fecha_mov.pack(side="left", padx=5)
        ctk.CTkLabel(r3, text="Motivo:", width=80).pack(side="left", padx=5)
        self.e_motivo = ctk.CTkEntry(r3, width=250)
        self.e_motivo.pack(side="left", padx=5)

        r4 = ctk.CTkFrame(form, fg_color="transparent")
        r4.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r4, text="Costo Unit.:", width=120).pack(side="left", padx=5)
        self.e_costo_unit = ctk.CTkEntry(r4, width=100)
        self.e_costo_unit.pack(side="left", padx=5)
        ctk.CTkLabel(r4, text="Referencia:", width=90).pack(side="left", padx=5)
        self.e_referencia = ctk.CTkEntry(r4, width=200)
        self.e_referencia.pack(side="left", padx=5)

        ctk.CTkButton(form, text="💾 Registrar Movimiento", command=self.guardar_movimiento, 
                     fg_color="green").pack(pady=10)

        # Historial
        ctk.CTkLabel(main, text="📅 Historial de Movimientos", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        self.tabla_mov = ttk.Treeview(main, columns=("fecha", "insumo", "tipo", "cant", "motivo"), 
                                      show="headings", height=12)
        for col, txt, w in [("fecha", "Fecha", 100), ("insumo", "Insumo", 250), ("tipo", "Tipo", 100),
                            ("cant", "Cantidad", 100), ("motivo", "Motivo", 200)]:
            self.tabla_mov.heading(col, text=txt)
            self.tabla_mov.column(col, width=w, anchor="center")
        self.tabla_mov.pack(fill="both", expand=True, pady=10)

    def crear_alertas(self):
        """Tab de alertas de stock bajo"""
        main = ctk.CTkFrame(self.frame_alertas)
        main.pack(fill="both", expand=True, padx=4, pady=10)

        ctk.CTkLabel(main, text="⚠️ Alertas de Stock Bajo", font=("Segoe UI", 18, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(main, text="Insumos con stock por debajo del mínimo", 
                    font=("Segoe UI", 12), text_color="gray").pack(pady=5)

        self.tabla_alertas = ttk.Treeview(main, columns=("cod", "nom", "stock", "min", "falta", "ubicacion"), 
                                         show="headings", height=15)
        for col, txt, w in [("cod", "Código", 100), ("nom", "Nombre", 250), ("stock", "Stock Actual", 100),
                            ("min", "Stock Mínimo", 100), ("falta", "Falta", 80), ("ubicacion", "Ubicación", 150)]:
            self.tabla_alertas.heading(col, text=txt)
            self.tabla_alertas.column(col, width=w, anchor="center")
        self.tabla_alertas.pack(fill="both", expand=True, pady=10)

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="🔄 Actualizar Alertas", command=self.cargar_alertas).pack(side="left", padx=5)

    def cargar_datos_iniciales(self):
        """Carga datos iniciales"""
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
                fincas = [f"{r[0]}-{r[1]}" for r in cur.fetchall()]
                if hasattr(self, 'cb_finca_ins'):
                    self.cb_finca_ins.configure(values=fincas)
                    if fincas: self.cb_finca_ins.set(fincas[0])
                if hasattr(self, 'cb_finca_filtro'):
                    # Mantener 'Todas' al inicio
                    valores_filtro = ["Todas"] + fincas
                    self.cb_finca_filtro.configure(values=valores_filtro)
        except: pass
        
        self.cargar_inventario()
        self.cargar_insumos_combo()
        self.cargar_movimientos()
        self.cargar_alertas()

    def _finca_filtro_id(self):
        if not hasattr(self, 'cb_finca_filtro'):
            return None
        sel = self.cb_finca_filtro.get()
        if not sel or sel == 'Todas':
            return None
        try:
            return int(sel.split('-')[0])
        except:
            return None

    def _aplicar_filtro_finca(self):
        # Recargar todas las vistas dependientes
        self.cargar_inventario()
        self.cargar_insumos_combo()
        self.cargar_movimientos()
        self.cargar_alertas()

    def guardar_insumo(self):
        cod = self.e_codigo.get().strip()
        nom = self.e_nombre.get().strip()
        cat = self.cb_categoria.get()
        
        if not cod or not nom or not cat:
            messagebox.showwarning("Atención", "Complete código, nombre y categoría")
            return
        
        try:
            id_finca = None
            if self.cb_finca_ins.get():
                id_finca = int(self.cb_finca_ins.get().split("-")[0])
            
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO insumo (codigo, nombre, categoria, unidad_medida, stock_actual, 
                                       stock_minimo, stock_maximo, precio_unitario, id_finca, 
                                       ubicacion, proveedor_principal)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (cod, nom, cat, self.e_unidad.get().strip(),
                      float(self.e_stock_actual.get() or 0),
                      float(self.e_stock_min.get() or 0),
                      float(self.e_stock_max.get() or 0) if self.e_stock_max.get().strip() else None,
                      float(self.e_precio.get() or 0) if self.e_precio.get().strip() else None,
                      id_finca, self.e_ubicacion.get().strip() or None,
                      self.e_proveedor.get().strip() or None))
                conn.commit()
            
            messagebox.showinfo("Éxito", "✅ Insumo registrado")
            self.limpiar_form_insumo()
            self.cargar_inventario()
            self.cargar_insumos_combo()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def limpiar_form_insumo(self):
        self.e_codigo.delete(0, "end")
        self.e_nombre.delete(0, "end")
        self.e_stock_actual.delete(0, "end")
        self.e_stock_actual.insert(0, "0")
        self.e_stock_min.delete(0, "end")
        self.e_stock_min.insert(0, "10")
        self.e_stock_max.delete(0, "end")
        self.e_precio.delete(0, "end")
        self.e_proveedor.delete(0, "end")
        self.e_ubicacion.delete(0, "end")

    def cargar_inventario(self):
        for item in self.tabla_inv.get_children():
            self.tabla_inv.delete(item)
        
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                finca_id = self._finca_filtro_id()
                if finca_id is None:
                    cur.execute("""
                        SELECT codigo, nombre, categoria, stock_actual, stock_minimo, 
                               unidad_medida, precio_unitario
                        FROM insumo WHERE estado = 'Activo'
                        ORDER BY nombre
                    """)
                else:
                    cur.execute("""
                        SELECT codigo, nombre, categoria, stock_actual, stock_minimo, 
                               unidad_medida, precio_unitario
                        FROM insumo WHERE estado = 'Activo' AND id_finca = ?
                        ORDER BY nombre
                    """, (finca_id,))
                for r in cur.fetchall():
                    precio_fmt = f"${r[6]:.2f}" if r[6] else "N/A"
                    # Marcar en rojo si está bajo
                    tag = "bajo" if r[3] < r[4] else ""
                    self.tabla_inv.insert("", "end", values=(r[0], r[1], r[2], f"{r[3]:.1f}", 
                                                             f"{r[4]:.1f}", r[5], precio_fmt), tags=(tag,))
                self.tabla_inv.tag_configure("bajo", foreground="red")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar inventario:\n{e}")

    def cargar_insumos_combo(self):
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                finca_id = self._finca_filtro_id()
                if finca_id is None:
                    cur.execute("SELECT id, codigo, nombre FROM insumo WHERE estado = 'Activo' ORDER BY nombre")
                else:
                    cur.execute("SELECT id, codigo, nombre FROM insumo WHERE estado = 'Activo' AND id_finca = ? ORDER BY nombre", (finca_id,))
                insumos = [f"{r[0]}-{r[1]} - {r[2]}" for r in cur.fetchall()]
                if hasattr(self, 'cb_insumo_mov'):
                    self.cb_insumo_mov.configure(values=insumos)
                    if insumos: self.cb_insumo_mov.set(insumos[0])
        except: pass

    def guardar_movimiento(self):
        if not self.cb_insumo_mov.get():
            messagebox.showwarning("Atención", "Seleccione un insumo")
            return
        
        try:
            insumo_id = int(self.cb_insumo_mov.get().split("-")[0])
            tipo = self.cb_tipo_mov.get()
            cantidad = float(self.e_cantidad_mov.get())
            fecha = self.e_fecha_mov.get().strip()
            
            costo_unit = None
            if self.e_costo_unit.get().strip():
                costo_unit = float(self.e_costo_unit.get())
            
            with db.get_connection() as conn:
                cur = conn.cursor()
                
                # Registrar movimiento
                cur.execute("""
                    INSERT INTO movimiento_insumo (insumo_id, tipo_movimiento, cantidad, 
                                                   motivo, referencia, costo_unitario, 
                                                   costo_total, fecha_movimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (insumo_id, tipo, cantidad, self.e_motivo.get().strip() or None,
                      self.e_referencia.get().strip() or None, costo_unit,
                      (costo_unit * cantidad) if costo_unit else None, fecha))
                
                # Actualizar stock
                if tipo == "Entrada":
                    cur.execute("UPDATE insumo SET stock_actual = stock_actual + ? WHERE id = ?", 
                               (cantidad, insumo_id))
                elif tipo == "Salida":
                    cur.execute("UPDATE insumo SET stock_actual = stock_actual - ? WHERE id = ?", 
                               (cantidad, insumo_id))
                elif tipo == "Ajuste":
                    cur.execute("UPDATE insumo SET stock_actual = ? WHERE id = ?", 
                               (cantidad, insumo_id))
                
                conn.commit()
            
            messagebox.showinfo("Éxito", "✅ Movimiento registrado")
            self.cargar_movimientos()
            self.cargar_inventario()
            self.cargar_alertas()
            
            # Limpiar
            self.e_cantidad_mov.delete(0, "end")
            self.e_motivo.delete(0, "end")
            self.e_referencia.delete(0, "end")
            self.e_costo_unit.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar:\n{e}")

    def cargar_movimientos(self):
        for item in self.tabla_mov.get_children():
            self.tabla_mov.delete(item)
        
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                finca_id = self._finca_filtro_id()
                if finca_id is None:
                    cur.execute("""
                        SELECT m.fecha_movimiento, i.codigo || ' - ' || i.nombre, 
                               m.tipo_movimiento, m.cantidad || ' ' || i.unidad_medida, m.motivo
                        FROM movimiento_insumo m
                        JOIN insumo i ON m.insumo_id = i.id
                        ORDER BY m.fecha_movimiento DESC, m.id DESC
                        LIMIT 100
                    """)
                else:
                    cur.execute("""
                        SELECT m.fecha_movimiento, i.codigo || ' - ' || i.nombre, 
                               m.tipo_movimiento, m.cantidad || ' ' || i.unidad_medida, m.motivo
                        FROM movimiento_insumo m
                        JOIN insumo i ON m.insumo_id = i.id
                        WHERE i.id_finca = ?
                        ORDER BY m.fecha_movimiento DESC, m.id DESC
                        LIMIT 100
                    """, (finca_id,))
                for r in cur.fetchall():
                    # Acceder por índice para evitar problemas con Row objects
                    valores = (r[0], r[1], r[2], r[3], r[4] if r[4] else "-")
                    self.tabla_mov.insert("", "end", values=valores)
        except Exception as e:
            print(f"Error cargar movimientos: {e}")

    def cargar_alertas(self):
        for item in self.tabla_alertas.get_children():
            self.tabla_alertas.delete(item)
        
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                finca_id = self._finca_filtro_id()
                if finca_id is None:
                    cur.execute("""
                        SELECT codigo, nombre, stock_actual, stock_minimo, 
                               (stock_minimo - stock_actual) as falta, ubicacion
                        FROM insumo
                        WHERE estado = 'Activo' AND stock_actual < stock_minimo
                        ORDER BY (stock_minimo - stock_actual) DESC
                    """)
                else:
                    cur.execute("""
                        SELECT codigo, nombre, stock_actual, stock_minimo, 
                               (stock_minimo - stock_actual) as falta, ubicacion
                        FROM insumo
                        WHERE estado = 'Activo' AND stock_actual < stock_minimo AND id_finca = ?
                        ORDER BY (stock_minimo - stock_actual) DESC
                    """, (finca_id,))
                for r in cur.fetchall():
                    self.tabla_alertas.insert("", "end", values=(
                        r[0], r[1], f"{r[2]:.1f}", f"{r[3]:.1f}", f"{r[4]:.1f}", r[5] or "N/A"
                    ))
        except: pass

    def ver_detalles_insumo(self):
        sel = self.tabla_inv.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un insumo")
            return
        
        cod = self.tabla_inv.item(sel[0])["values"][0]
        
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT i.*, f.nombre as finca_nom
                    FROM insumo i
                    LEFT JOIN finca f ON i.id_finca = f.id
                    WHERE i.codigo = ?
                """, (cod,))
                i = cur.fetchone()
                
                if i:
                    info = f"""
📦 DETALLES DEL INSUMO

🏷️  Código: {i[1]}
📝  Nombre: {i[2]}
📦  Categoría: {i[3]}
📋  Descripción: {i[4] or 'N/A'}

📊 STOCK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Actual: {i[6]:.2f} {i[5]}
• Mínimo: {i[7]:.2f} {i[5]}
• Máximo: {i[8]:.2f if i[8] else 'No definido'} {i[5] if i[8] else ''}
• Estado: {'⚠️ BAJO' if i[6] < i[7] else '✅ OK'}

💰 INFORMACIÓN FINANCIERA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Precio Unit.: ${i[9]:.2f if i[9] else 0}
• Valor Total: ${(i[9] * i[6]):.2f if i[9] else 0}

📍 UBICACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Finca: {i[-1] or 'N/A'}
• Ubicación: {i[11] or 'N/A'}
• Proveedor: {i[12] or 'N/A'}
                    """
                    
                    ventana = ctk.CTkToplevel(self)
                    ventana.title(f"Detalles - {i[2]}")
                    ventana.geometry("500x600")
                    
                    text = ctk.CTkTextbox(ventana, width=480, height=580)
                    text.pack(padx=10, pady=10)
                    text.insert("1.0", info)
                    text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_insumo(self):
        sel = self.tabla_inv.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un insumo")
            return
        
        cod = self.tabla_inv.item(sel[0])["values"][0]
        
        if not messagebox.askyesno("Confirmar", f"¿Eliminar insumo '{cod}'?"):
            return
        
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM insumo WHERE codigo = ?", (cod,))
                conn.commit()
            messagebox.showinfo("Éxito", "Insumo eliminado")
            self.cargar_inventario()
        except Exception as e:
            messagebox.showerror("Error", str(e))
