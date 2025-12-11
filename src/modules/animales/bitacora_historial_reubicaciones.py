import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import csv
from datetime import datetime
from pathlib import Path

from database.database import get_db_connection
from modules.utils.date_picker import attach_date_picker

class BitacoraHistorialReubicacionesFrame(ctk.CTkFrame):
    def __init__(self, master, on_animal_selected=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.on_animal_selected = on_animal_selected
        self.crear_widgets()
        self.cargar_filtros()
        self.mostrar()

    def crear_widgets(self):
        """Crear interfaz profesional con secciones bien organizadas"""
        
        # ==================== ENCABEZADO ====================
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        titulo = ctk.CTkLabel(header_frame, text="📦 Historial de Reubicaciones", 
                             font=("Segoe UI", 22, "bold"))
        titulo.pack(side="left", anchor="w")
        
        self.label_resultados = ctk.CTkLabel(header_frame, text="Registros: 0", 
                                            font=("Segoe UI", 11, "italic"), 
                                            text_color="gray")
        self.label_resultados.pack(side="right", anchor="e")

        # ==================== SCROLL PRINCIPAL PARA TODO ====================
        scroll_main = ctk.CTkScrollableFrame(self, orientation="vertical")
        scroll_main.pack(fill="both", expand=True, padx=0, pady=0)

        # ==================== FILTROS SECCIÓN 1: FECHAS ====================
        filtros_frame1 = ctk.CTkFrame(scroll_main, corner_radius=8, fg_color=("gray90", "gray25"))
        filtros_frame1.pack(fill="x", padx=15, pady=(8, 8), anchor="w")
        
        ctk.CTkLabel(filtros_frame1, text="🗓️ RANGO DE FECHAS", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(8, 5))
        
        fecha_frame = ctk.CTkFrame(filtros_frame1, fg_color="transparent")
        fecha_frame.pack(fill="x", padx=12, pady=(0, 10))
        fecha_frame.columnconfigure((0, 2), weight=1)
        
        ctk.CTkLabel(fecha_frame, text="Desde:").grid(row=0, column=0, sticky="e", padx=(0, 8))
        entrada_desde_frame = ctk.CTkFrame(fecha_frame, fg_color="transparent")
        entrada_desde_frame.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        self.entry_desde = ctk.CTkEntry(entrada_desde_frame, placeholder_text="YYYY-MM-DD", width=140)
        self.entry_desde.pack(side="left", fill="x", expand=True)
        attach_date_picker(entrada_desde_frame, self.entry_desde)
        
        ctk.CTkLabel(fecha_frame, text="Hasta:").grid(row=0, column=2, sticky="e", padx=(0, 8))
        entrada_hasta_frame = ctk.CTkFrame(fecha_frame, fg_color="transparent")
        entrada_hasta_frame.grid(row=0, column=3, sticky="ew")
        self.entry_hasta = ctk.CTkEntry(entrada_hasta_frame, placeholder_text="YYYY-MM-DD", width=140)
        self.entry_hasta.pack(side="left", fill="x", expand=True)
        attach_date_picker(entrada_hasta_frame, self.entry_hasta)

        # ==================== FILTROS SECCIÓN 2: UBICACIONES ====================
        filtros_frame2 = ctk.CTkFrame(scroll_main, corner_radius=8, fg_color=("gray90", "gray25"))
        filtros_frame2.pack(fill="x", padx=15, pady=(0, 8), anchor="w")
        
        ctk.CTkLabel(filtros_frame2, text="📍 UBICACIONES", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(8, 5))
        
        ubicacion_frame = ctk.CTkFrame(filtros_frame2, fg_color="transparent")
        ubicacion_frame.pack(fill="x", padx=12, pady=(0, 10))
        ubicacion_frame.columnconfigure((0, 2), weight=1)
        
        ctk.CTkLabel(ubicacion_frame, text="Finca:").grid(row=0, column=0, sticky="e", padx=(0, 8))
        self.combo_finca = ctk.CTkComboBox(ubicacion_frame, width=160, state="readonly")
        self.combo_finca.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        
        ctk.CTkLabel(ubicacion_frame, text="Usuario:").grid(row=0, column=2, sticky="e", padx=(0, 8))
        self.combo_usuario = ctk.CTkComboBox(ubicacion_frame, width=160, state="readonly")
        self.combo_usuario.grid(row=0, column=3, sticky="ew")

        # ==================== FILTROS SECCIÓN 3: BÚSQUEDA ====================
        filtros_frame3 = ctk.CTkFrame(scroll_main, corner_radius=8, fg_color=("gray90", "gray25"))
        filtros_frame3.pack(fill="x", padx=15, pady=(0, 12), anchor="w")
        
        ctk.CTkLabel(filtros_frame3, text="🔍 BÚSQUEDA", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(8, 5))
        
        busqueda_frame = ctk.CTkFrame(filtros_frame3, fg_color="transparent")
        busqueda_frame.pack(fill="x", padx=12, pady=(0, 10))
        busqueda_frame.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(busqueda_frame, text="Buscar:").grid(row=0, column=0, sticky="e", padx=(0, 8))
        self.entry_buscar = ctk.CTkEntry(busqueda_frame, placeholder_text="Código animal, motivo o finca...", width=300)
        self.entry_buscar.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.entry_buscar.bind("<Return>", lambda e: self.mostrar())

        # ==================== BOTONES DE ACCIÓN ====================
        botones_frame = ctk.CTkFrame(scroll_main, fg_color="transparent")
        botones_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        ctk.CTkButton(botones_frame, text="🔎 Aplicar Filtros", command=self.mostrar, 
                     fg_color="#1976D2", hover_color="#1565C0").pack(side="left", padx=4)
        ctk.CTkButton(botones_frame, text="🗑️ Limpiar Filtros", command=self.limpiar_filtros, 
                     fg_color="#666", hover_color="#777").pack(side="left", padx=4)
        ctk.CTkButton(botones_frame, text="📥 Exportar CSV", command=self.exportar_csv, 
                     fg_color="#4CAF50", hover_color="#45a049").pack(side="left", padx=4)

        # ==================== TABLA ====================
        table_frame = ctk.CTkFrame(scroll_main)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        # Contenedor para manejar ambos scrollbars
        table_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        table_container.pack(fill="both", expand=True)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        self.tabla = ttk.Treeview(table_container,
                      columns=("codigo", "animal", "finca_origen", "finca_destino", 
                          "potrero_origen", "potrero_destino", "fecha", "motivo", "usuario"),
                      show="headings", height=16)
        
        cols = [
            ("codigo", "🐄 Código", 90),
            ("animal", "Nombre Animal", 120),
            ("finca_origen", "Finca Origen", 140),
            ("finca_destino", "Finca Destino", 140),
            ("potrero_origen", "Potrero Origen", 140),
            ("potrero_destino", "Potrero Destino", 140),
            ("fecha", "📅 Fecha", 110),
            ("motivo", "Motivo", 130),
            ("usuario", "👤 Usuario", 110)
        ]
        
        for col, header, width in cols:
            self.tabla.heading(col, text=header)
            self.tabla.column(col, width=width, anchor="center" if col in ["codigo", "fecha"] else "w")
        
        # Configurar estilos
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        
        # Ubicar tabla y scrollbars con grid para evitar solapado
        self.tabla.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(table_container, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(table_container, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        # ==================== BARRA DE ACCIONES ====================
        acciones_frame = ctk.CTkFrame(scroll_main, fg_color="transparent")
        acciones_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        ctk.CTkButton(acciones_frame, text="📄 Abrir Ficha", command=self.abrir_ficha_sel,
                     fg_color="#FF9800", hover_color="#F57C00", width=120).pack(side="left", padx=4)
        ctk.CTkButton(acciones_frame, text="🔄 Actualizar", command=self.mostrar,
                     fg_color="#2196F3", hover_color="#1976D2", width=120).pack(side="left", padx=4)
        
        self.label_estado = ctk.CTkLabel(acciones_frame, text="",
                                        font=("Segoe UI", 10, "italic"),
                                        text_color="gray")
        self.label_estado.pack(side="right", anchor="e")

    def cargar_filtros(self):
        """Cargar opciones disponibles en los filtros"""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Obtener fincas únicas del historial
                cur.execute("""
                    SELECT DISTINCT finca_origen 
                    FROM historial_reubicaciones 
                    WHERE finca_origen IS NOT NULL
                    UNION
                    SELECT DISTINCT finca_destino 
                    FROM historial_reubicaciones 
                    WHERE finca_destino IS NOT NULL
                    ORDER BY 1
                """)
                fincas = [r[0] if not isinstance(r, sqlite3.Row) else r['finca_origen'] or r['finca_destino'] for r in cur.fetchall()]
                
                # Obtener usuarios únicos
                cur.execute("""
                    SELECT DISTINCT usuario FROM historial_reubicaciones 
                    WHERE usuario IS NOT NULL AND usuario <> '' 
                    ORDER BY usuario
                """)
                usuarios = [r[0] if not isinstance(r, sqlite3.Row) else r['usuario'] for r in cur.fetchall()]
            
            self.combo_finca.configure(values=["Todas las fincas"] + fincas)
            self.combo_usuario.configure(values=["Todos los usuarios"] + usuarios)
            self.combo_finca.set("Todas las fincas")
            self.combo_usuario.set("Todos los usuarios")
        except Exception as e:
            self.combo_finca.configure(values=["Todas las fincas"])
            self.combo_finca.set("Todas las fincas")
            self.combo_usuario.configure(values=["Todos los usuarios"])
            self.combo_usuario.set("Todos los usuarios")
            print(f"Error cargando filtros: {e}")

    def limpiar_filtros(self):
        """Limpiar todos los filtros"""
        self.entry_desde.delete(0, "end")
        self.entry_hasta.delete(0, "end")
        self.combo_finca.set("Todas las fincas")
        self.combo_usuario.set("Todos los usuarios")
        self.entry_buscar.delete(0, "end")
        self.mostrar()

    def mostrar(self):
        """Cargar y mostrar registros en la tabla"""
        for iid in self.tabla.get_children():
            self.tabla.delete(iid)
        
        desde = self.entry_desde.get().strip()
        hasta = self.entry_hasta.get().strip()
        finca = self.combo_finca.get().strip()
        usuario = self.combo_usuario.get().strip()
        buscar = self.entry_buscar.get().strip().upper()
        
        condiciones = []
        params = []
        
        # Validar fechas
        def _valid_date(s):
            if not s:
                return False
            try:
                datetime.strptime(s, "%Y-%m-%d")
                return True
            except Exception:
                return False
        
        if _valid_date(desde):
            condiciones.append("fecha >= ?")
            params.append(desde)
        if _valid_date(hasta):
            condiciones.append("fecha <= ?")
            params.append(hasta)
        
        if finca and finca != "Todas las fincas":
            condiciones.append("(finca_origen = ? OR finca_destino = ?)")
            params.extend([finca, finca])
        
        if usuario and usuario != "Todos los usuarios":
            condiciones.append("usuario = ?")
            params.append(usuario)
        
        if buscar:
            condiciones.append("(animal_codigo LIKE ? OR motivo LIKE ? OR finca_origen LIKE ? OR finca_destino LIKE ?)")
            params.extend([f"%{buscar}%", f"%{buscar}%", f"%{buscar}%", f"%{buscar}%"])
        
        where_sql = (" WHERE " + " AND ".join(condiciones)) if condiciones else ""
        
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Obtener datos con nombre del animal
                cur.execute(f"""
                    SELECT 
                        hr.animal_codigo,
                        COALESCE(a.nombre, '---') AS animal_nombre,
                        hr.finca_origen,
                        hr.finca_destino,
                        hr.potrero_origen,
                        hr.potrero_destino,
                        hr.fecha,
                        hr.motivo,
                        hr.usuario
                    FROM historial_reubicaciones hr
                    LEFT JOIN animal a ON a.codigo = hr.animal_codigo
                    {where_sql}
                    ORDER BY hr.fecha DESC
                """, params)
                
                registros = cur.fetchall()
                total = len(registros)
                
                for r in registros:
                    try:
                        if isinstance(r, sqlite3.Row):
                            vals = (r['animal_codigo'], r['animal_nombre'], r['finca_origen'],
                                   r['finca_destino'], r['potrero_origen'], r['potrero_destino'],
                                   r['fecha'], r['motivo'], r['usuario'])
                        else:
                            vals = (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8])
                        self.tabla.insert("", "end", values=vals)
                    except (KeyError, IndexError, TypeError):
                        continue
                
                # Actualizar etiquetas de estado
                self.label_resultados.configure(text=f"Registros: {total}")
                if total == 0:
                    self.label_estado.configure(text="Sin resultados")
                else:
                    self.label_estado.configure(text=f"Mostrando {total} registro{'s' if total != 1 else ''}")
        
        except Exception as e:
            messagebox.showerror("Error al cargar", f"No se pudieron cargar los registros:\n{e}")
            self.label_estado.configure(text="Error al cargar datos")

    def exportar_csv(self):
        """Exportar datos actuales a archivo CSV"""
        try:
            archivo = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"historial_reubicaciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not archivo:
                return
            
            # Obtener datos visibles en la tabla
            datos = []
            headers = ["Código", "Nombre Animal", "Finca Origen", "Finca Destino", 
                      "Potrero Origen", "Potrero Destino", "Fecha", "Motivo", "Usuario"]
            datos.append(headers)
            
            for item in self.tabla.get_children():
                datos.append(self.tabla.item(item)['values'])
            
            # Escribir CSV
            with open(archivo, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(datos)
            
            messagebox.showinfo("Exportar", f"✅ Datos exportados correctamente a:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")

    def abrir_ficha_sel(self):
        """Abrir la ficha del animal seleccionado"""
        sel = self.tabla.selection()
        if not sel:
            messagebox.showinfo("Seleccionar", "Por favor, seleccione un registro de la tabla")
            return
        
        codigo = self.tabla.item(sel[0], 'values')[0]
        
        if callable(self.on_animal_selected):
            try:
                self.on_animal_selected(codigo)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la ficha:\n{e}")
        else:
            messagebox.showinfo("Ficha", f"Código del animal: {codigo}\n\nVaya a la pestaña 'Ficha del Animal' e ingrese este código.")
