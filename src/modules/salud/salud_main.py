"""
Módulo de Salud - Diagnósticos veterinarios y Tratamientos
Integra tanto eventos de salud como gestión de tratamientos y vacunas
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from infraestructura.salud import SaludService, SaludRepository
from modules.utils.date_picker import attach_date_picker
from modules.utils.ui import get_theme_colors, add_tooltip, style_treeview
from modules.utils.colores import obtener_colores


class SaludModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Inicializar servicio de dominio
        self.salud_service = SaludService()
        
        # Colores y modo adaptativos
        colors = get_theme_colors()
        self._modo = colors["mode"]
        self._fg_card = colors["fg"]
        self._sel = colors["sel"]
        self._hover = colors["hover"]
        
        # Colores del módulo
        self.color_bg, self.color_hover = obtener_colores('salud')
        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):

        # Título con color del módulo
        header = ctk.CTkFrame(self, fg_color=(self.color_bg, "#1a1a1a"), corner_radius=15)
        header.pack(fill="x", padx=15, pady=(10, 6))
        ctk.CTkLabel(header, text="🏥 Salud y Tratamientos", font=("Segoe UI", 22, "bold"), text_color="white").pack(side="left", anchor="w", padx=15, pady=10)
        # Notebook expandido para ocupar toda la altura disponible
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=(3, 5))

        # Pestaña de diagnósticos
        self.frame_diagnostico = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_diagnostico, text="➕ Nuevo Diagnóstico")
        
        # Pestaña de historial de diagnósticos
        self.frame_historial = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_historial, text="📋 Historial de Diagnósticos")
        
        # Pestaña de nuevo tratamiento
        self.frame_nuevo_trat = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_nuevo_trat, text="💊 Nuevo Tratamiento")
        
        # Pestaña de historial de tratamientos
        self.frame_hist_trat = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_hist_trat, text="📋 Historial de Tratamientos")

        # Pestaña de próximos tratamientos
        self.frame_proximos = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_proximos, text="📅 Próximos Tratamientos")

        # Crear contenido de cada pestaña
        self.crear_form_diagnostico()
        self.crear_historial()
        self.crear_formulario_tratamientos()
        self.crear_historial_tratamientos()
        self.crear_proximos_tratamientos()

    # ==================== DIAGNÓSTICOS ====================
    def crear_form_diagnostico(self):
        main = ctk.CTkScrollableFrame(self.frame_diagnostico)
        main.pack(fill="both", expand=True, padx=2, pady=5)

        ctk.CTkLabel(main, text="📝 Registrar Evento de Salud", 
                    font=("Segoe UI", 16, "bold")).pack(pady=(3, 8))

        form = ctk.CTkFrame(main, corner_radius=10)
        form.pack(fill="both", expand=True, pady=5)

        r0 = ctk.CTkFrame(form, fg_color="transparent")
        r0.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r0, text="Finca*:", width=150).pack(side="left", padx=5)
        self.cb_finca_diag = ctk.CTkComboBox(r0, width=300, command=lambda x: self.actualizar_animales_por_finca())
        self.cb_finca_diag.set("Seleccione la finca")
        self.cb_finca_diag.pack(side="left", padx=5)
        ctk.CTkButton(r0, text="🔄", command=self.cargar_fincas, width=40).pack(side="left", padx=5)

        r1 = ctk.CTkFrame(form, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r1, text="Animal*:", width=150).pack(side="left", padx=5)
        self.cb_animal = ctk.CTkComboBox(r1, width=300)
        self.cb_animal.set("Seleccione el animal")
        self.cb_animal.pack(side="left", padx=5)
        ctk.CTkButton(r1, text="🔄", command=self.cargar_animales, width=40).pack(side="left", padx=5)

        r2 = ctk.CTkFrame(form, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r2, text="Fecha*:", width=150).pack(side="left", padx=5)
        self.e_fecha = ctk.CTkEntry(r2, width=130, placeholder_text="YYYY-MM-DD")
        self.e_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.e_fecha.pack(side="left", padx=5)
        attach_date_picker(r2, self.e_fecha)
        
        ctk.CTkLabel(r2, text="Tipo*:", width=80).pack(side="left", padx=5)
        self.cb_tipo = ctk.CTkComboBox(r2, values=["Enfermedad", "Lesión", "Revisión", "Vacunación", "Otro"], width=150)
        self.cb_tipo.set("Seleccione tipo")
        self.cb_tipo.pack(side="left", padx=5)

        r3 = ctk.CTkFrame(form, fg_color="transparent")
        r3.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r3, text="Diagnóstico*:", width=150).pack(side="left", padx=5, anchor="n")
        self.t_diagnostico = ctk.CTkTextbox(r3, width=400, height=120)
        self.t_diagnostico.pack(side="left", padx=5, fill="both", expand=True)

        r4 = ctk.CTkFrame(form, fg_color="transparent")
        r4.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r4, text="Severidad*:", width=150).pack(side="left", padx=5)
        self.cb_severidad = ctk.CTkComboBox(r4, values=["Leve", "Moderada", "Grave", "Crítica"], width=150)
        self.cb_severidad.set("Seleccione severidad")
        self.cb_severidad.pack(side="left", padx=5)
        
        ctk.CTkLabel(r4, text="Estado*:", width=100).pack(side="left", padx=5)
        self.cb_estado = ctk.CTkComboBox(r4, values=["Activo", "En Tratamiento", "Recuperado", "Crónico"], width=150)
        self.cb_estado.set("Seleccione estado")
        self.cb_estado.pack(side="left", padx=5)

        r5 = ctk.CTkFrame(form, fg_color="transparent")
        r5.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(r5, text="Observaciones:", width=150).pack(side="left", padx=5, anchor="n")
        self.t_obs = ctk.CTkTextbox(r5, width=400, height=100)
        self.t_obs.pack(side="left", padx=5, fill="both", expand=True)

        ctk.CTkButton(form, text="💾 Registrar Diagnóstico", command=self.guardar_diagnostico,
                     fg_color="green").pack(pady=10)

    def crear_historial(self):
        main = ctk.CTkFrame(self.frame_historial)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        top = ctk.CTkFrame(main, fg_color="transparent")
        top.pack(fill="x", pady=10)
        
        ctk.CTkLabel(top, text="🏥 Historial de Eventos", 
                    font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(top, text="🔄 Actualizar", command=self.cargar_historial).pack(side="right", padx=5)

        self.tabla_hist = ttk.Treeview(main, columns=("fecha", "animal", "tipo", "diagnostico", "severidad", "estado"), 
                                       show="headings", height=15)
        for col, txt, w in [("fecha", "Fecha", 100), ("animal", "Animal", 150),
                            ("tipo", "Tipo", 100), ("diagnostico", "Diagnóstico", 200),
                            ("severidad", "Severidad", 100), ("estado", "Estado", 120)]:
            self.tabla_hist.heading(col, text=txt)
            self.tabla_hist.column(col, width=w, anchor="center" if col in ["fecha", "tipo", "severidad", "estado"] else "w")
        self.tabla_hist.pack(fill="both", expand=True, pady=10)
        self.tabla_hist.bind("<Double-1>", lambda e: self.ver_detalle())

        btn = ctk.CTkFrame(main, fg_color="transparent")
        btn.pack(pady=5)
        ctk.CTkButton(btn, text="👁️ Ver Detalle", command=self.ver_detalle).pack(side="left", padx=5)
        ctk.CTkButton(btn, text="✏️ Actualizar Estado", command=self.actualizar_estado).pack(side="left", padx=5)

    def cargar_datos(self):
        """Carga los datos iniciales del módulo"""
        self._inicializar_tablas()
        self.cargar_fincas()
        self.cargar_fincas_trat()
        self.cargar_historial()
        self.cargar_tratamientos()
        self.cargar_proximos_tratamientos()
    
    def _inicializar_tablas(self):
        """Inicializa las tablas de base de datos si no existen"""
        try:
            # Delegado a SaludRepository (FASE 8.5.2)
            self.salud_service._repo.crear_tablas_si_no_existen()
        except Exception as e:
            print(f"Error al inicializar tablas: {e}")

    def cargar_fincas(self):
        """Carga las fincas disponibles (FASE 8.5.3: Migrado a SaludService)"""
        try:
            fincas = self.salud_service.cargar_fincas()
            fincas_nombres = [f["nombre"] for f in fincas] if fincas else []
            if hasattr(self, 'cb_finca_diag'):
                self.cb_finca_diag.configure(values=fincas_nombres)
                if fincas_nombres:
                    self.cb_finca_diag.set(fincas_nombres[0])
                    self.actualizar_animales_por_finca()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def actualizar_animales_por_finca(self):
        """Actualiza la lista de animales según la finca seleccionada (FASE 8.5.3: Migrado a SaludService)"""
        finca_seleccionada = self.cb_finca_diag.get()
        if not finca_seleccionada or finca_seleccionada == "Seleccione la finca":
            self.cb_animal.configure(values=[])
            self.cb_animal.set("Seleccione el animal")
            return
        
        try:
            animales_data = self.salud_service.cargar_animales_por_finca(finca_seleccionada)
            animales = [f"{a['id']}-{a['codigo']} {a.get('nombre', '')}" for a in animales_data] if animales_data else []
            self.cb_animal.configure(values=animales)
            if animales:
                self.cb_animal.set(animales[0])
            else:
                self.cb_animal.set("No hay animales en esta finca")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar animales:\n{e}")

    def cargar_animales(self):
        """Carga todos los animales (FASE 8.5.3: Migrado a SaludService)"""
        # Si hay una finca seleccionada, actualiza por finca en lugar de todos
        finca_seleccionada = self.cb_finca_diag.get()
        if finca_seleccionada and finca_seleccionada != "Seleccione la finca":
            self.actualizar_animales_por_finca()
            return
        
        try:
            animales_data = self.salud_service.cargar_animales()
            animales = [f"{a['id']}-{a['codigo']} {a.get('nombre', '')}" for a in animales_data] if animales_data else []
            if hasattr(self, 'cb_animal'):
                self.cb_animal.configure(values=animales)
                if animales: self.cb_animal.set(animales[0])
            if hasattr(self, 'combo_animal_trat'):
                self.combo_animal_trat.configure(values=animales)
                if animales: self.combo_animal_trat.set(animales[0])
            # Recargar fincas también
            self.cargar_fincas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los animales:\n{e}")

    def cargar_fincas_trat(self):
        """Carga las fincas disponibles para tratamiento (FASE 8.5.3: Migrado a SaludService)"""
        try:
            fincas = self.salud_service.cargar_fincas()
            fincas_nombres = [f["nombre"] for f in fincas] if fincas else []
            if hasattr(self, 'cb_finca_trat'):
                self.cb_finca_trat.configure(values=fincas_nombres)
                if fincas_nombres:
                    self.cb_finca_trat.set(fincas_nombres[0])
                    self.actualizar_animales_por_finca_trat()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def actualizar_animales_por_finca_trat(self):
        """Actualiza la lista de animales según la finca seleccionada en tratamiento (FASE 8.5.3: Migrado a SaludService)"""
        finca_seleccionada = self.cb_finca_trat.get()
        if not finca_seleccionada or finca_seleccionada == "Seleccione la finca":
            self.combo_animal_trat.configure(values=[])
            self.combo_animal_trat.set("Seleccione el animal")
            return
        
        try:
            animales_data = self.salud_service.cargar_animales_por_finca(finca_seleccionada)
            animales = [f"{a['id']}-{a['codigo']} {a.get('nombre', '')}" for a in animales_data] if animales_data else []
            self.combo_animal_trat.configure(values=animales)
            if animales:
                self.combo_animal_trat.set(animales[0])
            else:
                self.combo_animal_trat.set("No hay animales en esta finca")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar animales:\n{e}")

    def cargar_animales_trat(self):
        """Carga animales para tratamiento según la finca seleccionada"""
        # Si hay una finca seleccionada, actualiza por finca en lugar de todos
        finca_seleccionada = self.cb_finca_trat.get()
        if finca_seleccionada and finca_seleccionada != "Seleccione la finca":
            self.actualizar_animales_por_finca_trat()
            return
        
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, codigo, nombre FROM animal 
                    WHERE estado = 'Activo'
                    ORDER BY codigo
                """)
                animales = [f"{r[0]}-{r[1]} {r[2] or ''}" for r in cur.fetchall()]
                self.combo_animal_trat.configure(values=animales)
                if animales:
                    self.combo_animal_trat.set(animales[0])
                # Recargar fincas también
                self.cargar_fincas_trat()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los animales:\n{e}")

    def guardar_diagnostico(self):
        """Guardar diagnóstico (FASE 8.5.3: Migrado a SaludService)"""
        if not self.cb_animal.get() or "Seleccione" in self.cb_animal.get():
            messagebox.showwarning("Atención", "Seleccione un animal")
            return
        
        if not self.t_diagnostico.get("1.0", "end-1c").strip():
            messagebox.showwarning("Atención", "Ingrese el diagnóstico")
            return
        
        try:
            # Extraer el ID del formato "ID-CODIGO NOMBRE"
            animal_id = int(self.cb_animal.get().split("-")[0].strip())
            fecha = self.e_fecha.get().strip()
            tipo = self.cb_tipo.get()
            diagnostico = self.t_diagnostico.get("1.0", "end-1c").strip()
            severidad = self.cb_severidad.get()
            estado = self.cb_estado.get()
            obs = self.t_obs.get("1.0", "end-1c").strip() or None
            
            # Usar SaludService que valida animal activo
            self.salud_service.registrar_diagnostico(
                animal_id=animal_id,
                fecha=fecha,
                tipo=tipo,
                detalle=diagnostico,
                severidad=severidad,
                estado=estado,
                observaciones=obs
            )
            
            messagebox.showinfo("Éxito", "✅ Diagnóstico registrado")
            self.t_diagnostico.delete("1.0", "end")
            self.t_obs.delete("1.0", "end")
            self.cargar_historial()
        except ValueError as ve:
            messagebox.showerror("Error", f"Validación: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def cargar_historial(self):
        """Carga el historial de diagnósticos (FASE 8.5.3: Migrado a SaludService)"""
        for item in self.tabla_hist.get_children():
            self.tabla_hist.delete(item)
        
        try:
            diagnosticos = self.salud_service.obtener_historial_diagnosticos(limite=100)
            for d in diagnosticos:
                # Manejar la fecha
                fecha = d.get('fecha', '-')
                if fecha:
                    if hasattr(fecha, 'strftime'):
                        fecha = fecha.strftime("%d/%m/%Y")
                    else:
                        fecha = str(fecha)
                else:
                    fecha = "-"
                
                self.tabla_hist.insert("", "end", iid=d['id'], 
                                      values=(fecha, d['animal'], d['tipo'], d['detalle_corto'], 
                                             d['severidad'], d['estado']))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar historial:\n{e}")

    def ver_detalle(self):
        """Ver detalle de diagnóstico (FASE 8.5.3: Migrado a SaludService)"""
        sel = self.tabla_hist.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un registro")
            return
        
        try:
            evento_id = int(sel[0])  # type: ignore[arg-type]
            detalle = self.salud_service.obtener_detalle_diagnostico(evento_id)
            
            if detalle:
                ventana = ctk.CTkToplevel(self)
                ventana.title("Detalle Diagnóstico")
                ventana.geometry("600x500")
                
                ctk.CTkLabel(ventana, text="🏥 Detalle del Diagnóstico", 
                            font=("Segoe UI", 18, "bold")).pack(pady=5)
                
                info = ctk.CTkFrame(ventana, corner_radius=10)
                info.pack(fill="both", expand=True, padx=4, pady=10)
                
                datos = [
                    ("📅 Fecha:", detalle['fecha']),
                    ("🐄 Animal:", detalle['animal']),
                    ("🏷️ Tipo:", detalle['tipo']),
                    ("💊 Severidad:", detalle['severidad']),
                    ("📊 Estado:", detalle['estado']),
                    ("📝 Diagnóstico:", detalle['detalle']),
                    ("💬 Observaciones:", detalle['observaciones'] or "Sin observaciones")
                ]
                
                for label, valor in datos:
                    f = ctk.CTkFrame(info, fg_color="transparent")
                    f.pack(fill="x", padx=10, pady=5)
                    ctk.CTkLabel(f, text=label, font=("Segoe UI", 11, "bold"), width=150, anchor="w").pack(side="left", padx=5)
                    ctk.CTkLabel(f, text=str(valor), wraplength=380, anchor="w").pack(side="left", padx=5, fill="x", expand=True)
                
                ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_estado(self):
        """Actualizar estado de diagnóstico (FASE 8.5.3: Migrado a SaludService)"""
        sel = self.tabla_hist.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un diagnóstico")
            return
        
        ventana = ctk.CTkToplevel(self)
        ventana.title("Actualizar Estado")
        ventana.geometry("400x200")
        
        ctk.CTkLabel(ventana, text="Nuevo Estado:", font=("Segoe UI", 12, "bold")).pack(pady=10)
        cb_nuevo = ctk.CTkComboBox(ventana, values=["Activo", "En Tratamiento", "Recuperado", "Crónico"], width=250)
        cb_nuevo.pack(pady=10)
        
        def guardar():
            try:
                self.salud_service.actualizar_estado_diagnostico(int(sel[0]), cb_nuevo.get())  # type: ignore[arg-type]
                messagebox.showinfo("Éxito", "Estado actualizado")
                ventana.destroy()
                self.cargar_historial()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ctk.CTkButton(ventana, text="💾 Guardar", command=guardar, fg_color="green").pack(pady=10)

    # ==================== TRATAMIENTOS ====================
    def crear_formulario_tratamientos(self):
        """Crea el formulario para registrar un tratamiento"""
        main_frame = ctk.CTkScrollableFrame(self.frame_nuevo_trat)
        main_frame.pack(fill="both", expand=True, padx=4, pady=10)

        header_form = ctk.CTkLabel(
            main_frame,
            text="📝 Registrar Nuevo Tratamiento",
            font=("Segoe UI", 18, "bold"),
            text_color=self._sel
        )
        header_form.pack(pady=(0, 15))
        add_tooltip(header_form, "Complete los campos y guarde el tratamiento")

        # Campos
        campos_frame = ctk.CTkFrame(main_frame)
        campos_frame.pack(fill="both", expand=True, pady=5, padx=10)

        # Finca
        row0 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row0.pack(fill="x", pady=8)
        ctk.CTkLabel(row0, text="Finca *:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.cb_finca_trat = ctk.CTkComboBox(row0, width=300, font=("Segoe UI", 12), command=lambda x: self.actualizar_animales_por_finca_trat())
        self.cb_finca_trat.set("Seleccione la finca")
        self.cb_finca_trat.pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(row0, text="🔄", command=self.cargar_fincas_trat, width=40).pack(side="left", padx=5)

        # Animal
        row1 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row1.pack(fill="x", pady=8)
        ctk.CTkLabel(row1, text="Animal *:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.combo_animal_trat = ctk.CTkComboBox(row1, width=300, font=("Segoe UI", 12))
        self.combo_animal_trat.set("Seleccione el animal")
        self.combo_animal_trat.pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(row1, text="🔄", command=self.cargar_animales_trat, width=40).pack(side="left", padx=5)

        # Fecha
        row2 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row2.pack(fill="x", pady=8)
        ctk.CTkLabel(row2, text="Fecha Tratamiento *:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_fecha_trat = ctk.CTkEntry(row2, width=260, font=("Segoe UI", 12), placeholder_text="YYYY-MM-DD")
        self.entry_fecha_trat.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_trat.pack(side="left", padx=5)
        attach_date_picker(row2, self.entry_fecha_trat)

        # Tipo
        row3 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row3.pack(fill="x", pady=8)
        ctk.CTkLabel(row3, text="Tipo Tratamiento *:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.combo_tipo_trat = ctk.CTkComboBox(
            row3,
            values=["Vacunación", "Desparasitación", "Antibiótico", "Vitaminas", "Minerales", "Cirugía", "Otro"],
            width=300,
            font=("Segoe UI", 12)
        )
        self.combo_tipo_trat.set("Seleccione tipo")
        self.combo_tipo_trat.pack(side="left", padx=5, fill="x", expand=True)

        # Producto
        row4 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row4.pack(fill="x", pady=8)
        ctk.CTkLabel(row4, text="Producto *:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_producto = ctk.CTkEntry(row4, width=300, font=("Segoe UI", 12))
        self.entry_producto.pack(side="left", padx=5, fill="x", expand=True)

        # Dosis
        row5 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row5.pack(fill="x", pady=8)
        ctk.CTkLabel(row5, text="Dosis:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_dosis = ctk.CTkEntry(row5, width=300, font=("Segoe UI", 12), placeholder_text="Ej: 5 ml, 1 tableta, etc.")
        self.entry_dosis.pack(side="left", padx=5, fill="x", expand=True)

        # Veterinario
        row6 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row6.pack(fill="x", pady=8)
        ctk.CTkLabel(row6, text="Veterinario:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_veterinario = ctk.CTkEntry(row6, width=300, font=("Segoe UI", 12))
        self.entry_veterinario.pack(side="left", padx=5, fill="x", expand=True)

        # Próxima fecha
        row7 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row7.pack(fill="x", pady=8)
        ctk.CTkLabel(row7, text="Próxima Aplicación:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.entry_proxima = ctk.CTkEntry(row7, width=260, font=("Segoe UI", 12), 
                         placeholder_text="YYYY-MM-DD (opcional)")
        self.entry_proxima.pack(side="left", padx=5)
        attach_date_picker(row7, self.entry_proxima)

        # Comentario
        row8 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row8.pack(fill="both", expand=True, pady=8)
        ctk.CTkLabel(row8, text="Comentarios:", width=150, font=("Segoe UI", 12)).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row8, width=300, height=150, font=("Segoe UI", 12))
        self.text_comentario.pack(side="left", padx=5, fill="both", expand=True)

        # Botones del formulario
        btn_frame = ctk.CTkFrame(campos_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)

        btn_guardar = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Tratamiento",
            command=self.guardar_tratamiento,
            fg_color=self._sel,
            hover_color=self._hover,
            width=180,
            font=("Segoe UI", 12, "bold")
        )
        btn_guardar.pack(side="left", padx=5)
        add_tooltip(btn_guardar, "Guardar tratamiento y actualizar listados")

        btn_limpiar = ctk.CTkButton(
            btn_frame,
            text="🔄 Limpiar Formulario",
            command=self.limpiar_formulario,
            width=150,
            font=("Segoe UI", 12)
        )
        btn_limpiar.pack(side="left", padx=5)
        add_tooltip(btn_limpiar, "Vaciar campos del formulario")

    def crear_historial_tratamientos(self):
        """Crea la tabla de historial de tratamientos"""
        main_frame = ctk.CTkFrame(self.frame_hist_trat)
        main_frame.pack(fill="both", expand=True, padx=4, pady=5)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        header_label = ctk.CTkLabel(
            header_frame,
            text="📋 Historial de Tratamientos",
            font=("Segoe UI", 18, "bold"),
            text_color=self._sel
        )
        header_label.pack(side="left")
        add_tooltip(header_label, "Tratamientos registrados recientemente")

        # Botones de acción
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side="right")

        btn_actualizar = ctk.CTkButton(
            action_frame,
            text="🔄 Actualizar",
            command=self.cargar_tratamientos,
            width=120,
            font=("Segoe UI", 12),
            fg_color=self._sel,
            hover_color=self._hover
        )
        btn_actualizar.pack(side="left", padx=5)
        add_tooltip(btn_actualizar, "Recargar la tabla de tratamientos")

        # Tabla
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        self.crear_tabla_tratamientos(table_frame)

    def crear_tabla_tratamientos(self, parent):
        """Crea la tabla de tratamientos"""
        style_treeview()

        self.tabla_tratamientos = ttk.Treeview(
            parent,
            columns=("id", "fecha", "animal", "tipo", "producto", "dosis", "veterinario", "proxima", "comentario"),
            show="headings",
            height=15
        )

        columnas = [
            ("id", "ID", 60),
            ("fecha", "Fecha", 100),
            ("animal", "Animal", 150),
            ("tipo", "Tipo", 120),
            ("producto", "Producto", 150),
            ("dosis", "Dosis", 100),
            ("veterinario", "Veterinario", 120),
            ("proxima", "Próxima", 100),
            ("comentario", "Comentario", 200)
        ]

        for col, heading, width in columnas:
            self.tabla_tratamientos.heading(col, text=heading)
            self.tabla_tratamientos.column(col, width=width, anchor="center")

        self.tabla_tratamientos.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tabla_tratamientos.yview)
        self.tabla_tratamientos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bind doble click para ver detalles
        self.tabla_tratamientos.bind("<Double-1>", self.ver_detalles_tratamiento)

    def crear_proximos_tratamientos(self):
        """Crea la sección de próximos tratamientos"""
        main_frame = ctk.CTkFrame(self.frame_proximos)
        main_frame.pack(fill="both", expand=True, padx=4, pady=5)

        header_prox = ctk.CTkLabel(
            main_frame,
            text="📅 Próximos Tratamientos Programados",
            font=("Segoe UI", 18, "bold"),
            text_color=self._sel
        )
        header_prox.pack(pady=(0, 10))
        add_tooltip(header_prox, "Tratamientos programados a futuro")

        # Información
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="both", expand=True, pady=10)

        self.label_proximos = ctk.CTkLabel(
            info_frame,
            text="Cargando próximos tratamientos...",
            font=("Segoe UI", 12),
            justify="left",
            anchor="nw"
        )
        self.label_proximos.pack(pady=5, padx=4, fill="both", expand=True)

        # Botón actualizar
        btn_refrescar_prox = ctk.CTkButton(
            main_frame,
            text="🔄 Actualizar",
            command=self.cargar_proximos_tratamientos,
            width=150,
            fg_color=self._sel,
            hover_color=self._hover
        )
        btn_refrescar_prox.pack(pady=10)
        add_tooltip(btn_refrescar_prox, "Recargar próximos tratamientos")

    def guardar_tratamiento(self):
        """Guarda un nuevo tratamiento"""
        """Guarda un nuevo tratamiento (FASE 8.5.3: Migrado a SaludService)"""
        # Validaciones UI
        if not self.combo_animal_trat.get() or "Seleccione" in self.combo_animal_trat.get():
            messagebox.showwarning("Atención", "Seleccione un animal")
            return
        if not self.entry_fecha_trat.get():
            messagebox.showwarning("Atención", "Ingrese la fecha del tratamiento")
            return
        if not self.combo_tipo_trat.get() or "Seleccione" in self.combo_tipo_trat.get():
            messagebox.showwarning("Atención", "Seleccione el tipo de tratamiento")
            return
        if not self.entry_producto.get():
            messagebox.showwarning("Atención", "Ingrese el producto utilizado")
            return

        try:
            # Extraer ID del animal (formato: "ID-CODIGO NOMBRE")
            animal_id = int(self.combo_animal_trat.get().split("-")[0].strip())
            # Usar SaludService que valida animal activo y tipo de tratamiento
            self.salud_service.registrar_tratamiento(
                animal_id=animal_id,
                fecha_inicio=self.entry_fecha_trat.get(),
                tipo_tratamiento=self.combo_tipo_trat.get(),
                producto=self.entry_producto.get(),
                dosis=self.entry_dosis.get() or None,
                veterinario=self.entry_veterinario.get() or None,
                comentario=self.text_comentario.get("1.0", "end-1c").strip() or None,
                fecha_proxima=self.entry_proxima.get() or None
            )
            messagebox.showinfo("Éxito", "Tratamiento registrado correctamente")
            self.limpiar_formulario()
            self.cargar_tratamientos()
            self.cargar_proximos_tratamientos()
        except ValueError as ve:
            messagebox.showerror("Error", f"Validación: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el tratamiento:\n{e}")

    def cargar_tratamientos(self):
        """Carga los tratamientos en la tabla (FASE 8.5.3: Migrado a SaludService)"""
        # Limpiar tabla si existe
        if hasattr(self, 'tabla_tratamientos'):
            for item in self.tabla_tratamientos.get_children():
                self.tabla_tratamientos.delete(item)

        try:
            tratamientos = self.salud_service.obtener_historial_tratamientos(limite=100)
            for t in tratamientos:
                # Manejar fecha_inicio (puede ser string o None)
                fecha_inicio = t.get('fecha_inicio', '-')
                if fecha_inicio:
                    if hasattr(fecha_inicio, 'strftime'):
                        fecha_inicio = fecha_inicio.strftime("%d/%m/%Y")
                    else:
                        fecha_inicio = str(fecha_inicio)
                else:
                    fecha_inicio = "-"
                
                # Manejar fecha_proxima (puede ser string o None)
                fecha_proxima = t.get('fecha_proxima', '-')
                if fecha_proxima:
                    if hasattr(fecha_proxima, 'strftime'):
                        fecha_proxima = fecha_proxima.strftime("%d/%m/%Y")
                    else:
                        fecha_proxima = str(fecha_proxima)
                else:
                    fecha_proxima = "-"
                
                # Truncar comentario si es muy largo
                comentario = t.get('comentario', '-') or '-'
                comentario = (comentario[:50] + "...") if len(comentario) > 50 else comentario
                
                self.tabla_tratamientos.insert("", "end", values=(
                    t['id'], fecha_inicio, t['animal'], t['tipo_tratamiento'], t['producto'], 
                    t.get('dosis') or "-", t.get('veterinario') or "-", fecha_proxima, comentario
                ))

        except Exception as e:
            print(f"Error al cargar tratamientos: {e}")

    def cargar_proximos_tratamientos(self):
        """Carga los próximos tratamientos programados (FASE 8.5.3: Migrado a SaludService)"""
        try:
            tratamientos = self.salud_service.obtener_proximos_tratamientos(limite=20)
            
            if tratamientos:
                info_text = "Proximos tratamientos programados\n\n"
                info_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for i, tratamiento in enumerate(tratamientos, 1):
                    # Manejar fecha_proxima (puede ser string o datetime)
                    fecha_prox = tratamiento.get('fecha_proxima', '-')
                    if fecha_prox:
                        if hasattr(fecha_prox, 'strftime'):
                            fecha_prox = fecha_prox.strftime("%d/%m/%Y")
                        else:
                            fecha_prox = str(fecha_prox)
                    else:
                        fecha_prox = "-"
                    
                    comentario_text = tratamiento.get('comentario', '')
                    if comentario_text:
                        comentario_text = (comentario_text[:50] + "...") if len(comentario_text) > 50 else comentario_text
                    
                    info_text += f"{i}. Fecha: {fecha_prox}\n"
                    info_text += f"   Animal: {tratamiento['animal']}\n"
                    info_text += f"   Tratamiento: {tratamiento['tipo_tratamiento']} - {tratamiento['producto']}\n"
                    if comentario_text:
                        info_text += f"   Notas: {comentario_text}\n"
                    info_text += "\n"
                
                info_text += f"Total: {len(tratamientos)} tratamientos programados"
            else:
                info_text = "✅ No hay tratamientos programados para el futuro.\n\n"
                info_text += "Puede programar próximos tratamientos en el formulario de 'Nuevo Tratamiento'."

            if hasattr(self, 'label_proximos'):
                self.label_proximos.configure(text=info_text)

        except Exception as e:
            print(f"Error al cargar próximos tratamientos: {e}")
            if hasattr(self, 'label_proximos'):
                self.label_proximos.configure(text="❌ Error al cargar los próximos tratamientos")

    def ver_detalles_tratamiento(self, event):
        """Muestra los detalles del tratamiento seleccionado"""
        seleccionado = self.tabla_tratamientos.selection()
        if not seleccionado:
            return

        tratamiento_id = self.tabla_tratamientos.item(seleccionado[0])["values"][0]

        try:
            tratamiento = self.salud_service.obtener_detalle_tratamiento(int(tratamiento_id))  # type: ignore[arg-type]
            if tratamiento:
                fecha_inicio = tratamiento['fecha_inicio']
                if fecha_inicio and hasattr(fecha_inicio, 'strftime'):
                    fecha_inicio = fecha_inicio.strftime("%d/%m/%Y")
                elif fecha_inicio:
                    fecha_inicio = str(fecha_inicio)
                else:
                    fecha_inicio = "-"
                
                fecha_proxima = tratamiento['fecha_proxima']
                if fecha_proxima and hasattr(fecha_proxima, 'strftime'):
                    fecha_proxima = fecha_proxima.strftime("%d/%m/%Y")
                elif fecha_proxima:
                    fecha_proxima = str(fecha_proxima)
                else:
                    fecha_proxima = "No programada"
                
                fecha_registro = tratamiento.get('fecha_registro', '-')
                if fecha_registro and hasattr(fecha_registro, 'strftime'):
                    fecha_registro = fecha_registro.strftime("%d/%m/%Y %H:%M")
                elif fecha_registro:
                    fecha_registro = str(fecha_registro)
                
                detalles = f"""
📋 DETALLES DEL TRATAMIENTO

🐄 Animal: {tratamiento['animal']}
📅 Fecha Aplicación: {fecha_inicio}
💊 Tipo: {tratamiento['tipo_tratamiento']}
🧪 Producto: {tratamiento['producto']}
📏 Dosis: {tratamiento.get('dosis') or "No especificada"}
👨‍⚕️ Veterinario: {tratamiento.get('veterinario') or "No especificado"}
🗓️ Próxima Aplicación: {fecha_proxima}
📝 Comentarios: {tratamiento.get('comentario') or "No hay comentarios"}
📅 Registrado: {fecha_registro}
                """
                messagebox.showinfo(f"Detalles Tratamiento #{tratamiento_id}", detalles)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles:\n{e}")

    def limpiar_formulario(self):
        """Limpia el formulario de tratamientos"""
        self.combo_animal_trat.set("Seleccione el animal")
        self.entry_fecha_trat.delete(0, "end")
        self.entry_fecha_trat.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.combo_tipo_trat.set("Vacunación")
        self.entry_producto.delete(0, "end")
        self.entry_dosis.delete(0, "end")
        self.entry_veterinario.delete(0, "end")
        self.entry_proxima.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        
        # Recargar animales para asegurar que esté actualizado
        self.cargar_animales()


# Helper para probar rápida standalone
if __name__ == '__main__':
    app = ctk.CTk()
    app.title('Test Salud')
    frame = SaludModule(app)
    app.geometry('1200x700')
    app.mainloop()
