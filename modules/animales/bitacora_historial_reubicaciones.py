import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime
from pathlib import Path

from database.database import get_db_connection

class BitacoraHistorialReubicacionesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_filtros()
        self.mostrar()

    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="🗂️ Historial de Reubicaciones", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        filtros = ctk.CTkFrame(self)
        filtros.pack(fill="x", padx=10, pady=5)

        self.entry_desde = ctk.CTkEntry(filtros, placeholder_text="Desde (YYYY-MM-DD)", width=160)
        self.entry_hasta = ctk.CTkEntry(filtros, placeholder_text="Hasta (YYYY-MM-DD)", width=160)
        self.combo_finca = ctk.CTkComboBox(filtros, width=200)
        self.combo_usuario = ctk.CTkComboBox(filtros, width=160)
        self.entry_buscar = ctk.CTkEntry(filtros, placeholder_text="Buscar código animal/nota", width=220)

        self.entry_desde.pack(side="left", padx=4)
        self.entry_hasta.pack(side="left", padx=4)
        self.combo_finca.pack(side="left", padx=4)
        self.combo_usuario.pack(side="left", padx=4)
        self.entry_buscar.pack(side="left", padx=4)

        ctk.CTkButton(filtros, text="Aplicar", command=self.mostrar).pack(side="left", padx=4)
        ctk.CTkButton(filtros, text="Limpiar", command=self.limpiar_filtros).pack(side="left", padx=4)

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabla = ttk.Treeview(table_frame,
                                  columns=("codigo","finca_origen","finca_destino","potrero_origen","potrero_destino","fecha","motivo","usuario"),
                                  show="headings",
                                  height=16)
        cols = [
            ("codigo","Código",120),
            ("finca_origen","Finca Origen",150),
            ("finca_destino","Finca Destino",150),
            ("potrero_origen","Potrero Origen",160),
            ("potrero_destino","Potrero Destino",160),
            ("fecha","Fecha",120),
            ("motivo","Motivo",160),
            ("usuario","Usuario",140)
        ]
        for c, h, w in cols:
            self.tabla.heading(c, text=h)
            self.tabla.column(c, width=w, anchor="center")
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")

        acciones = ctk.CTkFrame(self)
        acciones.pack(fill="x", padx=10, pady=(0,8))
        ctk.CTkButton(acciones, text="🔍 Abrir Ficha", command=self.abrir_ficha_sel).pack(side="left", padx=4)
        ctk.CTkButton(acciones, text="🔄 Actualizar", command=self.mostrar).pack(side="left", padx=4)

    def cargar_filtros(self):
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM finca WHERE estado IN ('Activo','Activa')")
                fincas = [r[0] if not isinstance(r, sqlite3.Row) else r['nombre'] for r in cur.fetchall()]
                cur.execute("SELECT DISTINCT usuario FROM historial_reubicaciones WHERE usuario IS NOT NULL AND usuario<>''")
                users = [r[0] if not isinstance(r, sqlite3.Row) else r['usuario'] for r in cur.fetchall()]
            self.combo_finca.configure(values=["Todas"] + fincas)
            self.combo_usuario.configure(values=["Todos"] + users)
            self.combo_finca.set("Todas")
            self.combo_usuario.set("Todos")
        except Exception:
            self.combo_finca.configure(values=["Todas"]) ; self.combo_finca.set("Todas")
            self.combo_usuario.configure(values=["Todos"]) ; self.combo_usuario.set("Todos")

    def limpiar_filtros(self):
        self.entry_desde.delete(0, "end")
        self.entry_hasta.delete(0, "end")
        self.combo_finca.set("Todas")
        self.combo_usuario.set("Todos")
        self.entry_buscar.delete(0, "end")
        self.mostrar()

    def mostrar(self):
        for iid in self.tabla.get_children():
            self.tabla.delete(iid)
        desde = self.entry_desde.get().strip()
        hasta = self.entry_hasta.get().strip()
        finca = self.combo_finca.get().strip()
        usuario = self.combo_usuario.get().strip()
        buscar = self.entry_buscar.get().strip()
        condiciones = []
        params = []
        def _valid_date(s):
            if not s: return False
            try:
                datetime.strptime(s, "%Y-%m-%d")
                return True
            except Exception:
                return False
        if _valid_date(desde):
            condiciones.append("fecha >= ?") ; params.append(desde)
        if _valid_date(hasta):
            condiciones.append("fecha <= ?") ; params.append(hasta)
        if finca and finca != "Todas":
            condiciones.append("(finca_origen = ? OR finca_destino = ?)") ; params.extend([finca, finca])
        if usuario and usuario != "Todos":
            condiciones.append("usuario = ?") ; params.append(usuario)
        if buscar:
            condiciones.append("(animal_codigo LIKE ? OR motivo LIKE ?)") ; params.extend([f"%{buscar}%", f"%{buscar}%"]) 
        where_sql = (" WHERE " + " AND ".join(condiciones)) if condiciones else ""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(f"""
                    SELECT animal_codigo, finca_origen, finca_destino, potrero_origen, potrero_destino, fecha, motivo, usuario
                    FROM historial_reubicaciones
                    {where_sql}
                    ORDER BY fecha DESC
                """, params)
                for r in cur.fetchall():
                    try:
                        if isinstance(r, sqlite3.Row):
                            vals = (r['animal_codigo'], r['finca_origen'], r['finca_destino'], 
                                   r['potrero_origen'], r['potrero_destino'], r['fecha'], 
                                   r['motivo'], r['usuario'])
                        else:
                            vals = (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7])
                        self.tabla.insert("", "end", values=vals)
                    except (KeyError, IndexError):
                        continue
        except Exception as e:
            messagebox.showerror("Historial", f"No se pudo cargar: {e}")

    def abrir_ficha_sel(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showinfo("Historial", "Seleccione un registro")
            return
        codigo = self.tabla.item(sel[0], 'values')[0]
        # Señal sencilla: colocar código en clipboard para usar en módulo Ficha
        try:
            self.clipboard_clear()
            self.clipboard_append(codigo)
            messagebox.showinfo("Ficha", f"Código '{codigo}' copiado. Abra la Ficha y pegue/ingrese el código.")
        except Exception:
            messagebox.showinfo("Ficha", f"Código: {codigo}")
