"""
Módulo de Reproducción - Gestión completa: servicios, gestantes y partos
Versión optimizada con UI moderna, filtros, scroll y bitácora
"""
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import sys
import os
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from infraestructura.reproduccion import ReproduccionService
from modules.utils.date_picker import attach_date_picker
from modules.utils.colores import obtener_colores


# ============================= MODAL REGISTRO DE PARTO =============================
class ModalRegistroParto(ctk.CTkToplevel):
    """Modal para registrar parto y opcionalmente crear la cría."""

    def __init__(self, parent, servicio_id, hembra_id, codigo, nombre, reproduccion_service, on_success=None):
        super().__init__(parent)
        self.servicio_id = servicio_id
        self.hembra_id = hembra_id
        self.codigo = codigo
        self.nombre = nombre or ""
        self.reproduccion_service = reproduccion_service
        self.on_success = on_success

        self.title(f"Registrar Parto - {codigo}")
        self.geometry("620x720")
        self.resizable(False, False)

        self._build_ui()
        self.transient(parent)
        self.grab_set()

    def _build_ui(self):
        main = ctk.CTkScrollableFrame(self)
        main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main, text="👶 Registrar Parto", font=("Segoe UI", 18, "bold")).pack(pady=(0, 6))
        ctk.CTkLabel(main, text=f"Hembra: {self.codigo} - {self.nombre}", text_color="gray", font=("Segoe UI", 11)).pack(pady=(0, 10))

        s1 = ctk.CTkFrame(main, corner_radius=10, fg_color=("gray90", "gray25"))
        s1.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(s1, text="📅 FECHA Y TIPO", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))

        r1 = ctk.CTkFrame(s1, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(r1, text="Fecha de parto *", width=140, anchor="e").pack(side="left", padx=(0, 10))
        fecha_frame = ctk.CTkFrame(r1, fg_color="transparent")
        fecha_frame.pack(side="left")
        self.e_fecha_parto = ctk.CTkEntry(fecha_frame, width=150, placeholder_text="YYYY-MM-DD")
        self.e_fecha_parto.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.e_fecha_parto.pack(side="left")
        attach_date_picker(fecha_frame, self.e_fecha_parto)

        r2 = ctk.CTkFrame(s1, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=(0, 10))
        ctk.CTkLabel(r2, text="Tipo de parto *", width=140, anchor="e").pack(side="left", padx=(0, 10))
        self.cb_tipo_parto = ctk.CTkComboBox(r2, values=["Normal", "Distócico", "Cesárea", "Aborto"], width=200, state="readonly")
        self.cb_tipo_parto.set("Normal")
        self.cb_tipo_parto.pack(side="left", padx=5)

        s2 = ctk.CTkFrame(main, corner_radius=10, fg_color=("gray90", "gray25"))
        s2.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(s2, text="🐮 DATOS DE LA CRÍA", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))

        r3 = ctk.CTkFrame(s2, fg_color="transparent")
        r3.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(r3, text="Sexo *", width=140, anchor="e").pack(side="left", padx=(0, 10))
        self.cb_sexo_cria = ctk.CTkComboBox(r3, values=["Macho", "Hembra"], width=120, state="readonly")
        self.cb_sexo_cria.set("Hembra")
        self.cb_sexo_cria.pack(side="left", padx=5)

        r4 = ctk.CTkFrame(s2, fg_color="transparent")
        r4.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(r4, text="Peso (kg)", width=140, anchor="e").pack(side="left", padx=(0, 10))
        self.e_peso_cria = ctk.CTkEntry(r4, width=120, placeholder_text="Opcional")
        self.e_peso_cria.pack(side="left", padx=5)

        r5 = ctk.CTkFrame(s2, fg_color="transparent")
        r5.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(r5, text="Estado de cría", width=140, anchor="e").pack(side="left", padx=(0, 10))
        self.cb_estado_cria = ctk.CTkComboBox(r5, values=["Vivo", "Muerto al nacer", "Murió después"], width=180, state="readonly")
        self.cb_estado_cria.set("Vivo")
        self.cb_estado_cria.pack(side="left", padx=5)

        r6 = ctk.CTkFrame(s2, fg_color="transparent")
        r6.pack(fill="x", padx=12, pady=(0, 10))
        self.chk_registrar_cria = ctk.CTkCheckBox(r6, text="Registrar cría automáticamente", font=("Segoe UI", 11))
        self.chk_registrar_cria.select()
        self.chk_registrar_cria.pack(side="left", padx=5)

        s3 = ctk.CTkFrame(main, corner_radius=10, fg_color=("gray90", "gray25"))
        s3.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(s3, text="📝 OBSERVACIONES", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
        self.t_obs = ctk.CTkTextbox(s3, width=520, height=140)
        self.t_obs.pack(padx=12, pady=(0, 10))

        btns = ctk.CTkFrame(main, fg_color="transparent")
        btns.pack(fill="x", pady=10)
        ctk.CTkButton(btns, text="💾 Guardar", fg_color="#2E7D32", hover_color="#1B5E20", height=38, command=self.guardar).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="❌ Cancelar", fg_color="gray", hover_color="darkgray", height=38, command=self.destroy).pack(side="left", padx=6)

    def _valid_date(self, value: str) -> bool:
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except Exception:
            return False

    def guardar(self):
        fecha_parto = self.e_fecha_parto.get().strip()
        if not self._valid_date(fecha_parto):
            messagebox.showerror("Error", "Fecha de parto inválida (YYYY-MM-DD)")
            return

        if self.cb_sexo_cria.get() not in ("Macho", "Hembra"):
            messagebox.showerror("Error", "Seleccione el sexo de la cría")
            return

        try:
            peso = self.e_peso_cria.get().strip()
            peso_val = float(peso) if peso else None
        except ValueError:
            messagebox.showerror("Error", "El peso debe ser numérico")
            return

        tipo_parto = self.cb_tipo_parto.get()
        estado_cria = self.cb_estado_cria.get()
        sexo_cria = self.cb_sexo_cria.get()
        obs = self.t_obs.get("1.0", "end-1c").strip() or None
        registrar_cria = bool(self.chk_registrar_cria.get()) and estado_cria == "Vivo" and tipo_parto != "Aborto"

        try:
            self.reproduccion_service.registrar_parto(
                servicio_id=self.servicio_id,
                hembra_id=self.hembra_id,
                fecha_parto=fecha_parto,
                tipo_parto=tipo_parto,
                sexo_cria=sexo_cria,
                peso_cria=peso_val,
                estado_cria=estado_cria,
                registrar_cria=registrar_cria,
                observaciones=obs
            )

            if registrar_cria:
                messagebox.showinfo("Éxito", "✅ Parto registrado\n✅ Cría creada automáticamente")
            else:
                messagebox.showinfo("Éxito", "✅ Parto registrado")

            if self.on_success:
                self.on_success()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el parto:\n{e}")


# ============================= MÓDULO PRINCIPAL =============================
class ReproduccionModule(ctk.CTkFrame):
    def __init__(self, master, on_animal_selected=None):
        super().__init__(master)
        self.on_animal_selected = on_animal_selected
        self._fincas_cache = []
        self.reproduccion_service = ReproduccionService()
        self.pack(fill="both", expand=True)
        # Colores del módulo
        self.color_bg, self.color_hover = obtener_colores('reproduccion')
        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        # Header con color del módulo
        header = ctk.CTkFrame(self, fg_color=(self.color_bg, "#1a1a1a"), corner_radius=15)
        header.pack(fill="x", padx=15, pady=(10, 6))
        ctk.CTkLabel(header, text="🐄 Gestión Reproductiva", font=("Segoe UI", 22, "bold"), text_color="white").pack(side="left", anchor="w", padx=15, pady=10)

        stats = ctk.CTkFrame(header, fg_color="transparent")
        stats.pack(side="right", anchor="e")
        self.badge_gestantes = self._crear_badge(stats, "🤰", "0", "Gestantes")
        self.badge_gestantes.pack(side="left", padx=3)
        self.badge_partos = self._crear_badge(stats, "👶", "0", "Próx (7d)")
        self.badge_partos.pack(side="left", padx=3)
        self.badge_ia = self._crear_badge(stats, "💉", "0", "IAs")
        self.badge_ia.pack(side="left", padx=3)
        self.badge_montas = self._crear_badge(stats, "🐂", "0", "Montas")
        self.badge_montas.pack(side="left", padx=3)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(3, 8))

        self.frame_servicios = ctk.CTkFrame(self.notebook)
        self.frame_gestantes = ctk.CTkFrame(self.notebook)
        self.frame_partos = ctk.CTkFrame(self.notebook)

        self.notebook.add(self.frame_servicios, text="➕ Nuevo Servicio")
        self.notebook.add(self.frame_gestantes, text="🤰 Gestantes")
        self.notebook.add(self.frame_partos, text="👶 Próximos Partos")

        self.crear_form_servicio()
        self.crear_lista_gestantes()
        self.crear_proximos_partos()

    def _crear_badge(self, parent, icono, valor, texto):
        frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=("gray85", "gray25"))
        ctk.CTkLabel(frame, text=icono, font=("Segoe UI", 16)).pack(side="left", padx=(8, 4), pady=5)
        info = ctk.CTkFrame(frame, fg_color="transparent")
        info.pack(side="left", padx=(0, 8), pady=5)
        val = ctk.CTkLabel(info, text=valor, font=("Segoe UI", 14, "bold"))
        val.pack(anchor="w")
        ctk.CTkLabel(info, text=texto, font=("Segoe UI", 9), text_color="gray").pack(anchor="w")
        frame.__dict__['valor_label'] = val  # type: ignore[attr-defined]
        return frame

    def _actualizar_badges(self):
        try:
            stats = self.reproduccion_service.obtener_estadisticas_badges()
            self.badge_gestantes.__dict__['valor_label'].configure(text=str(stats.get('gestantes', 0)))  # type: ignore[index]
            self.badge_partos.__dict__['valor_label'].configure(text=str(stats.get('proximos_7_dias', 0)))  # type: ignore[index]
            self.badge_ia.__dict__['valor_label'].configure(text=str(stats.get('inseminaciones', 0)))  # type: ignore[index]
            self.badge_montas.__dict__['valor_label'].configure(text=str(stats.get('montas', 0)))  # type: ignore[index]
        except Exception as e:
            print(f"Error actualizando badges: {e}")

    def crear_form_servicio(self):
        main = ctk.CTkScrollableFrame(self.frame_servicios)
        main.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(main, text="📝 Registrar Servicio Reproductivo", font=("Segoe UI", 18, "bold")).pack(pady=(0, 12))

        sec1 = ctk.CTkFrame(main, corner_radius=10, fg_color=("gray90", "gray25"))
        sec1.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(sec1, text="📋 DATOS BÁSICOS", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))

        r1 = ctk.CTkFrame(sec1, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(r1, text="Finca *:", width=140, anchor="e").pack(side="left", padx=(0, 10))
        self.cb_finca_serv = ctk.CTkComboBox(r1, width=300, state="readonly", command=self._on_finca_servicio_change)
        self.cb_finca_serv.set("Seleccione finca")
        self.cb_finca_serv.pack(side="left", padx=5)

        r2 = ctk.CTkFrame(sec1, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(r2, text="Hembra *:", width=140, anchor="e").pack(side="left", padx=(0, 10))
        self.cb_animal = ctk.CTkComboBox(r2, width=300, state="readonly")
        self.cb_animal.set("Seleccione hembra")
        self.cb_animal.pack(side="left", padx=5)
        ctk.CTkButton(r2, text="🔄", width=40, fg_color="gray", hover_color="darkgray", command=self.cargar_hembras).pack(side="left", padx=5)

        r3 = ctk.CTkFrame(sec1, fg_color="transparent")
        r3.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(r3, text="Fecha Servicio *:", width=140, anchor="e").pack(side="left", padx=(0, 10))
        fecha_frame = ctk.CTkFrame(r3, fg_color="transparent")
        fecha_frame.pack(side="left", padx=5)
        self.e_fecha_serv = ctk.CTkEntry(fecha_frame, width=140, placeholder_text="YYYY-MM-DD")
        self.e_fecha_serv.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.e_fecha_serv.pack(side="left")
        attach_date_picker(fecha_frame, self.e_fecha_serv)

        ctk.CTkLabel(r3, text="Tipo *:", width=80, anchor="e").pack(side="left", padx=(20, 10))
        self.cb_tipo_serv = ctk.CTkComboBox(r3, values=["Monta Natural", "IA (Inseminación)", "Transferencia", "Embrión"], width=180, state="readonly", command=self._on_tipo_servicio_change)
        self.cb_tipo_serv.set("Seleccione tipo")
        self.cb_tipo_serv.pack(side="left", padx=5)

        self.sec_dyn = ctk.CTkFrame(main, corner_radius=10, fg_color=("gray90", "gray25"))
        self.sec_dyn.pack(fill="x", pady=(0, 10))

        self.frame_monta = ctk.CTkFrame(self.sec_dyn, fg_color="transparent")
        ctk.CTkLabel(self.frame_monta, text="🐂 MONTA NATURAL", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
        f_m1 = ctk.CTkFrame(self.frame_monta, fg_color="transparent")
        f_m1.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(f_m1, text="Toro Reproductor *:", width=150, anchor="e").pack(side="left", padx=(0, 10))
        self.cb_toro = ctk.CTkComboBox(f_m1, width=300, state="readonly")
        self.cb_toro.set("Seleccione toro")
        self.cb_toro.pack(side="left", padx=5)
        ctk.CTkButton(f_m1, text="🔄", width=40, fg_color="gray", hover_color="darkgray", command=self._cargar_toros).pack(side="left", padx=5)

        self.frame_ia = ctk.CTkFrame(self.sec_dyn, fg_color="transparent")
        ctk.CTkLabel(self.frame_ia, text="💉 INSEMINACIÓN ARTIFICIAL", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
        f_i1 = ctk.CTkFrame(self.frame_ia, fg_color="transparent")
        f_i1.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(f_i1, text="Código Semen *:", width=150, anchor="e").pack(side="left", padx=(0, 10))
        self.e_codigo_semen = ctk.CTkEntry(f_i1, width=260, placeholder_text="Ej: SEM-2025-001")
        self.e_codigo_semen.pack(side="left", padx=5)
        f_i2 = ctk.CTkFrame(self.frame_ia, fg_color="transparent")
        f_i2.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(f_i2, text="Procedencia:", width=150, anchor="e").pack(side="left", padx=(0, 10))
        self.e_procedencia_semen = ctk.CTkEntry(f_i2, width=260, placeholder_text="Centro o proveedor")
        self.e_procedencia_semen.pack(side="left", padx=5)
        f_i3 = ctk.CTkFrame(self.frame_ia, fg_color="transparent")
        f_i3.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(f_i3, text="Técnico:", width=150, anchor="e").pack(side="left", padx=(0, 10))
        self.e_tecnico = ctk.CTkEntry(f_i3, width=260, placeholder_text="Nombre del técnico")
        self.e_tecnico.pack(side="left", padx=5)

        self.frame_transfer = ctk.CTkFrame(self.sec_dyn, fg_color="transparent")
        ctk.CTkLabel(self.frame_transfer, text="🔬 TRANSFERENCIA / EMBRIÓN", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
        f_t1 = ctk.CTkFrame(self.frame_transfer, fg_color="transparent")
        f_t1.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(f_t1, text="Donadora:", width=150, anchor="e").pack(side="left", padx=(0, 10))
        self.cb_donadora = ctk.CTkComboBox(f_t1, width=260, state="readonly")
        self.cb_donadora.set("Seleccione donadora")
        self.cb_donadora.pack(side="left", padx=5)
        f_t2 = ctk.CTkFrame(self.frame_transfer, fg_color="transparent")
        f_t2.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(f_t2, text="Receptora *:", width=150, anchor="e").pack(side="left", padx=(0, 10))
        self.cb_receptora = ctk.CTkComboBox(f_t2, width=260, state="readonly")
        self.cb_receptora.set("(Es la hembra seleccionada)")
        self.cb_receptora.pack(side="left", padx=5)

        self.frame_monta.pack_forget()
        self.frame_ia.pack_forget()
        self.frame_transfer.pack_forget()

        sec3 = ctk.CTkFrame(main, corner_radius=10, fg_color=("gray90", "gray25"))
        sec3.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(sec3, text="📝 OBSERVACIONES", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
        self.t_obs = ctk.CTkTextbox(sec3, height=100)
        self.t_obs.pack(fill="x", padx=12, pady=(0, 10))

        btns = ctk.CTkFrame(main, fg_color="transparent")
        btns.pack(fill="x", pady=8)
        ctk.CTkButton(btns, text="💾 Registrar Servicio", fg_color="#2E7D32", hover_color="#1B5E20", height=40, command=self.guardar_servicio).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="🗑️ Limpiar Formulario", fg_color="gray", hover_color="darkgray", height=40, command=self._limpiar_formulario_servicio).pack(side="left", padx=5)

        info = ctk.CTkFrame(main, corner_radius=10, fg_color=("gray85", "gray25"))
        info.pack(fill="x", pady=10)
        ctk.CTkLabel(info, text="ℹ️ Gestación promedio: 280 días | Se calculará automáticamente la fecha probable de parto", font=("Segoe UI", 10, "italic")).pack(padx=12, pady=8)

    def crear_lista_gestantes(self):
        scroll = ctk.CTkScrollableFrame(self.frame_gestantes)
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(header, text="🤰 Animales en Gestación", font=("Segoe UI", 18, "bold")).pack(side="left", anchor="w")
        self.label_count_gest = ctk.CTkLabel(header, text="Total: 0", text_color="gray", font=("Segoe UI", 11, "italic"))
        self.label_count_gest.pack(side="right", anchor="e")

        filtros = ctk.CTkFrame(scroll, corner_radius=10, fg_color=("gray90", "gray25"))
        filtros.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(filtros, text="🔍 FILTROS", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))

        f1 = ctk.CTkFrame(filtros, fg_color="transparent")
        f1.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(f1, text="Finca:", width=80, anchor="e").pack(side="left", padx=(0, 8))
        self.cb_finca_gest = ctk.CTkComboBox(f1, width=200, state="readonly", command=lambda x: self.cargar_gestantes())
        self.cb_finca_gest.set("Todas las fincas")
        self.cb_finca_gest.pack(side="left", padx=5)
        ctk.CTkLabel(f1, text="Estado:", width=80, anchor="e").pack(side="left", padx=(20, 8))
        self.cb_estado_gest = ctk.CTkComboBox(f1, values=["Todos", "Normal", "Próxima (260-280d)", "Atrasada (>280d)"], width=180, state="readonly", command=lambda x: self.cargar_gestantes())
        self.cb_estado_gest.set("Todos")
        self.cb_estado_gest.pack(side="left", padx=5)

        f2 = ctk.CTkFrame(filtros, fg_color="transparent")
        f2.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(f2, text="Desde:", width=80, anchor="e").pack(side="left", padx=(0, 8))
        fd = ctk.CTkFrame(f2, fg_color="transparent")
        fd.pack(side="left", padx=5)
        self.e_desde_gest = ctk.CTkEntry(fd, width=120, placeholder_text="YYYY-MM-DD")
        self.e_desde_gest.pack(side="left")
        attach_date_picker(fd, self.e_desde_gest)
        ctk.CTkLabel(f2, text="Hasta:", width=80, anchor="e").pack(side="left", padx=(20, 8))
        fh = ctk.CTkFrame(f2, fg_color="transparent")
        fh.pack(side="left", padx=5)
        self.e_hasta_gest = ctk.CTkEntry(fh, width=120, placeholder_text="YYYY-MM-DD")
        self.e_hasta_gest.pack(side="left")
        attach_date_picker(fh, self.e_hasta_gest)

        f3 = ctk.CTkFrame(filtros, fg_color="transparent")
        f3.pack(fill="x", padx=12, pady=(5, 12))
        ctk.CTkLabel(f3, text="Buscar:", width=80, anchor="e").pack(side="left", padx=(0, 8))
        self.e_buscar_gest = ctk.CTkEntry(f3, width=250, placeholder_text="Código o nombre...")
        self.e_buscar_gest.pack(side="left", padx=5)
        self.e_buscar_gest.bind("<Return>", lambda e: self.cargar_gestantes())
        ctk.CTkButton(f3, text="🔎 Aplicar", fg_color="#1976D2", hover_color="#1565C0", width=100, command=self.cargar_gestantes).pack(side="left", padx=5)
        ctk.CTkButton(f3, text="🗑️ Limpiar", fg_color="gray", hover_color="darkgray", width=100, command=self._limpiar_filtros_gestantes).pack(side="left", padx=5)
        ctk.CTkButton(f3, text="📥 Exportar CSV", fg_color="#4CAF50", hover_color="#45a049", width=120, command=self._exportar_gestantes).pack(side="left", padx=5)

        table_frame = ctk.CTkFrame(scroll)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        container = ctk.CTkFrame(table_frame, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.tabla_gest = ttk.Treeview(container, columns=("id", "codigo", "nombre", "fecha_serv", "tipo", "toro_semen", "dias", "parto_est", "estado"), show="headings", height=16)
        cols = [
            ("codigo", "Código", 90),
            ("nombre", "Nombre", 150),
            ("fecha_serv", "Fecha Servicio", 110),
            ("tipo", "Tipo", 130),
            ("toro_semen", "Toro/Semen", 150),
            ("dias", "Días Gestación", 110),
            ("parto_est", "Parto Estimado", 110),
            ("estado", "Estado", 120)
        ]
        for col, header, width in cols:
            self.tabla_gest.heading(col, text=header)
            self.tabla_gest.column(col, width=width, anchor="center" if col in ["codigo", "dias", "fecha_serv", "parto_est"] else "w")
        self.tabla_gest.column("id", width=0, stretch=False)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.tabla_gest.tag_configure('normal', background='#E8F5E9')
        self.tabla_gest.tag_configure('proxima', background='#FFF9C4')
        self.tabla_gest.tag_configure('atrasada', background='#FFCDD2')

        self.tabla_gest.grid(row=0, column=0, sticky="nsew")
        sy = ttk.Scrollbar(container, orient="vertical", command=self.tabla_gest.yview)
        sx = ttk.Scrollbar(container, orient="horizontal", command=self.tabla_gest.xview)
        self.tabla_gest.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")

        btns = ctk.CTkFrame(scroll, fg_color="transparent")
        btns.pack(fill="x", pady=5)
        ctk.CTkButton(btns, text="📄 Ver Ficha", fg_color="#FF9800", hover_color="#F57C00", width=120, command=self._abrir_ficha_gestante).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="👶 Registrar Parto", fg_color="#2E7D32", hover_color="#1B5E20", width=140, command=self._registrar_parto_modal).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="❌ Anular Servicio", fg_color="#D32F2F", hover_color="#C62828", width=140, command=self.marcar_vacia).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="🔄 Actualizar", fg_color="#2196F3", hover_color="#1976D2", width=120, command=self.cargar_gestantes).pack(side="left", padx=5)

    def crear_proximos_partos(self):
        scroll = ctk.CTkScrollableFrame(self.frame_partos)
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(header, text="👶 Próximos Partos", font=("Segoe UI", 18, "bold")).pack(side="left", anchor="w")
        self.label_count_partos = ctk.CTkLabel(header, text="Total: 0", text_color="gray", font=("Segoe UI", 11, "italic"))
        self.label_count_partos.pack(side="right", anchor="e")

        filtros = ctk.CTkFrame(scroll, corner_radius=10, fg_color=("gray90", "gray25"))
        filtros.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(filtros, text="🔍 FILTROS", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))

        f1 = ctk.CTkFrame(filtros, fg_color="transparent")
        f1.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(f1, text="Finca:", width=80, anchor="e").pack(side="left", padx=(0, 8))
        self.cb_finca_partos = ctk.CTkComboBox(f1, width=200, state="readonly", command=lambda x: self.cargar_proximos())
        self.cb_finca_partos.set("Todas las fincas")
        self.cb_finca_partos.pack(side="left", padx=5)
        ctk.CTkLabel(f1, text="Días:", width=80, anchor="e").pack(side="left", padx=(20, 8))
        self.cb_dias_partos = ctk.CTkComboBox(f1, values=["7 días", "15 días", "30 días", "60 días", "Todos"], width=120, state="readonly", command=lambda x: self.cargar_proximos())
        self.cb_dias_partos.set("30 días")
        self.cb_dias_partos.pack(side="left", padx=5)

        f2 = ctk.CTkFrame(filtros, fg_color="transparent")
        f2.pack(fill="x", padx=12, pady=(5, 12))
        ctk.CTkLabel(f2, text="Buscar:", width=80, anchor="e").pack(side="left", padx=(0, 8))
        self.e_buscar_partos = ctk.CTkEntry(f2, width=250, placeholder_text="Código o nombre...")
        self.e_buscar_partos.pack(side="left", padx=5)
        self.e_buscar_partos.bind("<Return>", lambda e: self.cargar_proximos())
        ctk.CTkButton(f2, text="🔎 Aplicar", fg_color="#1976D2", hover_color="#1565C0", width=100, command=self.cargar_proximos).pack(side="left", padx=5)
        ctk.CTkButton(f2, text="🗑️ Limpiar", fg_color="gray", hover_color="darkgray", width=100, command=self._limpiar_filtros_partos).pack(side="left", padx=5)
        ctk.CTkButton(f2, text="📥 Exportar CSV", fg_color="#4CAF50", hover_color="#45a049", width=120, command=self._exportar_partos).pack(side="left", padx=5)

        table_frame = ctk.CTkFrame(scroll)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        container = ctk.CTkFrame(table_frame, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.tabla_partos = ttk.Treeview(container, columns=("id", "codigo", "nombre", "fecha_serv", "dias_gest", "fecha_est", "dias_falta", "tipo", "toro_semen"), show="headings", height=16)
        cols = [
            ("codigo", "Código", 90),
            ("nombre", "Nombre", 150),
            ("fecha_serv", "Fecha Servicio", 110),
            ("dias_gest", "Días Gestación", 110),
            ("fecha_est", "Parto Estimado", 110),
            ("dias_falta", "Días Restantes", 110),
            ("tipo", "Tipo", 130),
            ("toro_semen", "Toro/Semen", 150)
        ]
        for col, header, width in cols:
            self.tabla_partos.heading(col, text=header)
            self.tabla_partos.column(col, width=width, anchor="center" if col in ["codigo", "dias_gest", "dias_falta", "fecha_serv", "fecha_est"] else "w")
        self.tabla_partos.column("id", width=0, stretch=False)

        self.tabla_partos.tag_configure('hoy', background='#BBDEFB')
        self.tabla_partos.tag_configure('proximo', background='#FFF9C4')
        self.tabla_partos.tag_configure('atrasado', background='#FFCDD2')
        self.tabla_partos.tag_configure('normal', background='white')

        self.tabla_partos.grid(row=0, column=0, sticky="nsew")
        sy = ttk.Scrollbar(container, orient="vertical", command=self.tabla_partos.yview)
        sx = ttk.Scrollbar(container, orient="horizontal", command=self.tabla_partos.xview)
        self.tabla_partos.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")

        btns = ctk.CTkFrame(scroll, fg_color="transparent")
        btns.pack(fill="x", pady=5)
        ctk.CTkButton(btns, text="📄 Ver Ficha", fg_color="#FF9800", hover_color="#F57C00", width=120, command=self._abrir_ficha_parto).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="👶 Registrar Parto", fg_color="#2E7D32", hover_color="#1B5E20", width=140, command=self._registrar_parto_modal).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="🔄 Actualizar", fg_color="#2196F3", hover_color="#1976D2", width=120, command=self.cargar_proximos).pack(side="left", padx=5)

    def cargar_datos(self):
        self.cargar_fincas()
        self.cargar_hembras()
        self.cargar_gestantes()
        self.cargar_proximos()
        self._actualizar_badges()

    def cargar_fincas(self):
        try:
            fincas_data = self.reproduccion_service.cargar_fincas()
            self._fincas_cache = [(f['id'], f['nombre']) for f in fincas_data]
            fincas = [f"{f['id']} - {f['nombre']}" for f in fincas_data]
            if fincas:
                self.cb_finca_serv.configure(values=fincas)
                self.cb_finca_gest.configure(values=["Todas las fincas"] + fincas)
                self.cb_finca_partos.configure(values=["Todas las fincas"] + fincas)
                self.cb_finca_serv.set(fincas[0])
                self.cb_finca_gest.set("Todas las fincas")
                self.cb_finca_partos.set("Todas las fincas")
        except Exception as e:
            print(f"Error cargando fincas: {e}")

    def _parse_combo_id(self, value: str):
        try:
            return int(value.split('-')[0].strip())
        except Exception:
            return None

    def _valid_date(self, s: str) -> bool:
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return True
        except Exception:
            return False

    def _on_finca_servicio_change(self, _event=None):
        self.cargar_hembras()
        self._cargar_toros()

    def cargar_hembras(self):
        try:
            finca_id = self._parse_combo_id(self.cb_finca_serv.get())
            hembras_data = self.reproduccion_service.cargar_hembras(finca_id)
            hembras = [f"{h['id']}-{h['codigo']} {h['nombre']}".strip() for h in hembras_data]
            if hembras:
                self.cb_animal.configure(values=hembras)
                self.cb_animal.set(hembras[0])
            self.cb_receptora.configure(values=hembras or ["(Sin datos)"])
        except Exception as e:
            print(f"Error cargando hembras: {e}")

    def _cargar_toros(self):
        try:
            finca_id = self._parse_combo_id(self.cb_finca_serv.get())
            machos_data = self.reproduccion_service.cargar_machos(finca_id)
            toros = [f"{m['id']}-{m['codigo']} {m['nombre']}".strip() for m in machos_data]
            if toros:
                self.cb_toro.configure(values=toros)
                self.cb_toro.set(toros[0])
            self.cb_donadora.configure(values=toros or ["(Sin datos)"])
        except Exception as e:
            print(f"Error cargando toros: {e}")

    def _on_tipo_servicio_change(self, value=None):
        self.frame_monta.pack_forget()
        self.frame_ia.pack_forget()
        self.frame_transfer.pack_forget()
        tipo = self.cb_tipo_serv.get()
        if tipo == "Monta Natural":
            self.frame_monta.pack(fill="x")
        elif "Inseminación" in tipo:
            self.frame_ia.pack(fill="x")
        elif tipo in ("Transferencia", "Embrión"):
            self.frame_transfer.pack(fill="x")

    def _build_extra_observaciones(self):
        tipo = self.cb_tipo_serv.get()
        if tipo == "Monta Natural":
            return f"Toro: {self.cb_toro.get()}"
        if "Inseminación" in tipo:
            return " | ".join([
                f"Semen: {self.e_codigo_semen.get().strip()}",
                f"Procedencia: {self.e_procedencia_semen.get().strip()}",
                f"Técnico: {self.e_tecnico.get().strip()}",
            ])
        if tipo in ("Transferencia", "Embrión"):
            return " | ".join([
                f"Donadora: {self.cb_donadora.get()}",
                f"Receptora: {self.cb_receptora.get()}",
            ])
        return ""

    def guardar_servicio(self):
        if "Seleccione" in self.cb_animal.get():
            messagebox.showwarning("Atención", "Seleccione una hembra")
            return
        if "Seleccione" in self.cb_tipo_serv.get():
            messagebox.showwarning("Atención", "Seleccione el tipo de servicio")
            return

        fecha_serv = self.e_fecha_serv.get().strip()
        if not self._valid_date(fecha_serv):
            messagebox.showerror("Error", "Fecha inválida (YYYY-MM-DD)")
            return
        if datetime.strptime(fecha_serv, "%Y-%m-%d") > datetime.now():
            messagebox.showerror("Error", "La fecha no puede ser futura")
            return

        hembra_id = self._parse_combo_id(self.cb_animal.get())
        if not hembra_id:
            messagebox.showerror("Error", "No se pudo obtener la hembra seleccionada")
            return

        tipo = self.cb_tipo_serv.get()
        id_macho = None
        extra_obs = self._build_extra_observaciones()

        if tipo == "Monta Natural":
            id_macho = self._parse_combo_id(self.cb_toro.get())
            if not id_macho:
                messagebox.showerror("Error", "Seleccione el toro")
                return

        try:
            obs = self.t_obs.get("1.0", "end-1c").strip()
            obs_full = " | ".join(filter(None, [obs, extra_obs])) or None

            self.reproduccion_service.registrar_servicio(
                hembra_id=hembra_id,
                macho_id=id_macho,
                fecha_servicio=fecha_serv,
                tipo_servicio=tipo,
                observaciones=obs_full
            )

            messagebox.showinfo("Éxito", "✅ Servicio registrado")
            self._limpiar_formulario_servicio()
            self.cargar_gestantes()
            self.cargar_proximos()
            self._actualizar_badges()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _limpiar_formulario_servicio(self):
        self.e_fecha_serv.delete(0, "end")
        self.e_fecha_serv.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.cb_tipo_serv.set("Seleccione tipo")
        self.cb_toro.set("Seleccione toro") if hasattr(self, 'cb_toro') else None
        for entry in [getattr(self, n, None) for n in ["e_codigo_semen", "e_procedencia_semen", "e_tecnico"]]:
            if entry:
                entry.delete(0, "end")
        self.t_obs.delete("1.0", "end")
        self.frame_monta.pack_forget(); self.frame_ia.pack_forget(); self.frame_transfer.pack_forget()

    def _limpiar_filtros_gestantes(self):
        self.cb_finca_gest.set("Todas las fincas")
        self.cb_estado_gest.set("Todos")
        self.e_desde_gest.delete(0, "end")
        self.e_hasta_gest.delete(0, "end")
        self.e_buscar_gest.delete(0, "end")
        self.cargar_gestantes()

    def cargar_gestantes(self):
        for iid in self.tabla_gest.get_children():
            self.tabla_gest.delete(iid)

        estado_filtro = self.cb_estado_gest.get()
        buscar = self.e_buscar_gest.get().strip().upper()

        try:
            gestantes = self.reproduccion_service.listar_gestantes()
            total = 0
            for row in gestantes:
                try:
                    servicio_id = row['servicio_id']
                    codigo = row['codigo']
                    nombre = row['nombre']
                    fecha_serv = row['fecha_servicio']
                    tipo = row['tipo_servicio']
                    toro_s = row['toro_semen']
                    dias = row.get('dias_gestacion', 0)  # Usar .get() con default
                    parto_est = row['fecha_parto_estimada']

                    estado_tag = 'normal'
                    estado_txt = 'Normal'
                    if dias > 280:
                        estado_tag = 'atrasada'; estado_txt = 'Atrasada'
                    elif dias >= 260:
                        estado_tag = 'proxima'; estado_txt = 'Próxima'

                    if estado_filtro == "Próxima (260-280d)" and estado_tag != 'proxima':
                        continue
                    if estado_filtro == "Atrasada (>280d)" and estado_tag != 'atrasada':
                        continue
                    if estado_filtro == "Normal" and estado_tag != 'normal':
                        continue

                    if buscar and buscar not in codigo.upper() and buscar not in nombre.upper():
                        continue

                    self.tabla_gest.insert("", "end", iid=str(servicio_id), values=(servicio_id, codigo, nombre, fecha_serv, tipo, toro_s, dias, parto_est, estado_txt), tags=(estado_tag,))
                    total += 1
                except KeyError as ke:
                    print(f"[ERROR] KeyError en gestante: {ke}, row keys: {list(row.keys())}")
                    continue
                    
            self.label_count_gest.configure(text=f"Total: {total}")
        except Exception as e:
            import traceback
            print(f"[ERROR] Traceback completo: {traceback.format_exc()}")
            messagebox.showerror("Error", f"No se pudieron cargar gestantes:\n{type(e).__name__}: {str(e)}")

    def _limpiar_filtros_partos(self):
        self.cb_finca_partos.set("Todas las fincas")
        self.cb_dias_partos.set("30 días")
        self.e_buscar_partos.delete(0, "end")
        self.cargar_proximos()

    def _dias_hasta_parto(self, fecha_servicio: str) -> int:
        try:
            parto_est = datetime.strptime(fecha_servicio, "%Y-%m-%d") + timedelta(days=280)
            return (parto_est.date() - datetime.now().date()).days
        except Exception:
            return 0

    def cargar_proximos(self):
        for iid in self.tabla_partos.get_children():
            self.tabla_partos.delete(iid)

        dias_sel = self.cb_dias_partos.get()
        buscar = self.e_buscar_partos.get().strip().upper()

        limite = None
        if dias_sel != "Todos":
            try:
                limite = int(dias_sel.split()[0])
            except Exception:
                limite = 30

        try:
            proximos = self.reproduccion_service.listar_proximos_partos(dias=limite or 999)
            total = 0
            for row in proximos:
                servicio_id = row['servicio_id']
                codigo = row['codigo']
                nombre = row['nombre']
                fecha_serv = row['fecha_servicio']
                tipo = row['tipo_servicio']
                toro_s = row['toro_semen']
                dias_gest = row['dias_gestacion']
                parto_est = row['fecha_parto_estimada']
                dias_falta = row['dias_para_parto']

                if limite is not None and dias_falta > limite:
                    continue

                if buscar and buscar not in codigo.upper() and buscar not in nombre.upper():
                    continue

                tag = 'normal'
                if dias_falta < 0:
                    tag = 'atrasado'
                elif dias_falta == 0:
                    tag = 'hoy'
                elif dias_falta <= 7:
                    tag = 'proximo'

                self.tabla_partos.insert("", "end", iid=str(servicio_id), values=(servicio_id, codigo, nombre, fecha_serv, dias_gest, parto_est, dias_falta, tipo, toro_s), tags=(tag,))
                total += 1
            self.label_count_partos.configure(text=f"Total: {total}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar próximos partos:\n{e}")

    def _get_selected_servicio(self, tabla):
        sel = tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un registro")
            return None
        try:
            servicio_id = int(sel[0])
            item = tabla.item(sel[0])
            values = item["values"]
            return servicio_id, values
        except Exception:
            return None

    def _abrir_ficha_gestante(self):
        data = self._get_selected_servicio(self.tabla_gest)
        if not data:
            return
        _sid, values = data
        codigo = values[1]
        if self.on_animal_selected:
            self.on_animal_selected(codigo)

    def _abrir_ficha_parto(self):
        data = self._get_selected_servicio(self.tabla_partos)
        if not data:
            return
        _sid, values = data
        codigo = values[1]
        if self.on_animal_selected:
            self.on_animal_selected(codigo)

    def _registrar_parto_modal(self):
        data = self._get_selected_servicio(self.tabla_partos if self.notebook.index(self.notebook.select()) == 2 else self.tabla_gest)
        if not data:
            return
        servicio_id, values = data
        codigo = values[1]
        nombre = values[2] if len(values) > 2 else ""
        try:
            hembra_id = self.reproduccion_service.obtener_hembra_de_servicio(servicio_id)
            if not hembra_id:
                messagebox.showerror("Error", "No se pudo obtener la hembra del servicio")
                return
            modal = ModalRegistroParto(self, servicio_id, hembra_id, codigo, nombre, self.reproduccion_service, on_success=self._refrescar_todo)
            modal.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el registro de parto:\n{e}")

    def marcar_vacia(self):
        data = self._get_selected_servicio(self.tabla_gest)
        if not data:
            return
        servicio_id, values = data
        codigo = values[1]
        if not messagebox.askyesno("Confirmar", f"¿Anular servicio y marcar {codigo} como vacía?"):
            return
        try:
            self.reproduccion_service.marcar_servicio_vacio(servicio_id)
            messagebox.showinfo("Éxito", "Servicio anulado")
            self._refrescar_todo()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo anular el servicio:\n{e}")

    def _refrescar_todo(self):
        self.cargar_gestantes()
        self.cargar_proximos()
        self._actualizar_badges()

    def _exportar_gestantes(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Exportar gestantes")
        if not path:
            return
        try:
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Código", "Nombre", "Fecha Servicio", "Tipo", "Toro/Semen", "Días", "Parto Estimado", "Estado"])
                for iid in self.tabla_gest.get_children():
                    vals = self.tabla_gest.item(iid)["values"][1:]
                    writer.writerow(vals)
            messagebox.showinfo("Éxito", "Gestantes exportadas")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")

    def _exportar_partos(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Exportar próximos partos")
        if not path:
            return
        try:
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Código", "Nombre", "Fecha Servicio", "Días Gestación", "Parto Estimado", "Días Restantes", "Tipo", "Toro/Semen"])
                for iid in self.tabla_partos.get_children():
                    vals = self.tabla_partos.item(iid)["values"][1:]
                    writer.writerow(vals)
            messagebox.showinfo("Éxito", "Próximos partos exportados")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")


__all__ = ["ReproduccionModule"]
