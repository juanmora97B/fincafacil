import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Any
import os
import sqlite3
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from infraestructura.animales.animal_service import AnimalService
from database.database import get_db_connection
from modules.utils.units_helper import units_helper
from modules.utils.date_picker import attach_date_picker
from modules.utils.ui import add_tooltip
from modules.utils.validators import animal_validator  # Validaciones centralizadas
from modules.utils.constants_ui import truncate  # Truncado estándar de campos
# Autocomplete deshabilitado por solicitud del usuario: función no-op para compatibilidad
def set_autocomplete_mode(*args, **kwargs):
    return None


class RegistroAnimalFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        # Inicializar logger seguro (evita AttributeError si se usa antes de definir)
        try:
            import logging
            self.logger = logging.getLogger(__name__)
        except Exception:
            class _DummyLogger:
                def debug(self, *a, **k): pass
                def info(self, *a, **k): pass
                def warning(self, *a, **k): pass
                def error(self, *a, **k): pass
            self.logger = _DummyLogger()
        # Inicializar servicio de animales (FASE 8.3: reemplaza acceso directo a BD)
        self.animal_service = AnimalService()
        # Placeholder para switch de autocomplete global (UI eliminada, se conserva compatibilidad)
        self.switch_autocomplete_global: Any | None = None
        self.foto_path = None
        self.crear_widgets()
        self.cargar_datos_combos()

    def crear_widgets(self):
        # ======== TÍTULO ========
        titulo = ctk.CTkLabel(self, text="📝 Registro de Animales", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Eliminado: Toggle de Autocomplete global según solicitud del usuario

        # ======== NOTEBOOK PARA TIPO DE REGISTRO ========
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=2, pady=8)

        # Pestaña Nacimiento
        self.tab_nacimiento = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_nacimiento, text="👶 Nacimiento")

        # Pestaña Compra
        self.tab_compra = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_compra, text="💰 Compra")

        # Configurar ambas pestañas
        self.configurar_tab_nacimiento()
        self.configurar_tab_compra()

        # Botones generales
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        # Guardar individual
        ctk.CTkButton(btn_frame, text="💾 Guardar Animal", command=self.guardar_animal,
                      fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        # Importación general (Nacimiento + Compra)
        ctk.CTkButton(btn_frame, text="📥 Importar Excel (General)", command=self.importar_excel,
                      fg_color="#1976D2", hover_color="#1565C0").pack(side="left", padx=5)
        # Importación específica de compras
        ctk.CTkButton(btn_frame, text="💰 Importar Excel (Compras)", command=self.importar_excel_compras,
                      fg_color="#455A64", hover_color="#37474F").pack(side="left", padx=5)
        # Utilidades
        ctk.CTkButton(btn_frame, text="🔄 Limpiar Formulario", command=self.limpiar_formulario).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Refrescar Listas", command=self.refrescar_listas).pack(side="left", padx=5)

    def configurar_tab_nacimiento(self):
        """Configura la pestaña de registro por nacimiento"""
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(self.tab_nacimiento)
        main_frame.pack(fill="both", expand=True, padx=2, pady=8)

        # INFORMACIÓN BÁSICA
        frame_basica = ctk.CTkFrame(main_frame)
        frame_basica.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_basica, text="📋 INFORMACIÓN BÁSICA", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Código y Nombre
        row1 = ctk.CTkFrame(frame_basica, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        lbl_codigo = ctk.CTkLabel(row1, text="Código Animal *:", width=120)
        lbl_codigo.pack(side="left", padx=5)
        self.entry_codigo_nac = ctk.CTkEntry(row1, placeholder_text="Código Animal *", width=200)
        self.entry_codigo_nac.pack(side="left", padx=5)
        add_tooltip(lbl_codigo, "Campo obligatorio - Identificador único del animal")
        
        lbl_nombre = ctk.CTkLabel(row1, text="Nombre:", width=80)
        lbl_nombre.pack(side="left", padx=5)
        self.entry_nombre_nac = ctk.CTkEntry(row1, placeholder_text="Nombre Animal", width=200)
        self.entry_nombre_nac.pack(side="left", padx=5)
        add_tooltip(lbl_nombre, "Nombre opcional para identificar fácilmente al animal")

        # Fecha y Sexo
        row2 = ctk.CTkFrame(frame_basica, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.entry_fecha_nac = ctk.CTkEntry(row2, placeholder_text="Fecha Nacimiento (YYYY-MM-DD) *", width=180)
        self.entry_fecha_nac.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_nac.pack(side="left", padx=5)
        attach_date_picker(row2, self.entry_fecha_nac)
        
        self.combo_sexo_nac = ctk.CTkComboBox(row2, values=["Macho", "Hembra"], width=200)
        self.combo_sexo_nac.set("Macho")
        self.combo_sexo_nac.pack(side="left", padx=5)

        # Peso al nacer
        row2b = ctk.CTkFrame(frame_basica, fg_color="transparent")
        row2b.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row2b, text=f"Peso al Nacer ({units_helper.weight_unit}):", width=160).pack(side="left", padx=5)
        self.entry_peso_nacimiento = ctk.CTkEntry(row2b, placeholder_text="Peso al nacer", width=150)
        self.entry_peso_nacimiento.pack(side="left", padx=5)

        # Grupo (clasificación)
        ctk.CTkLabel(row2b, text="Grupo:", width=80).pack(side="left", padx=5)
        self.combo_grupo_nac = ctk.CTkComboBox(row2b, values=["Toros", "Vacas", "Terneros", "Novillos"], width=150)
        self.combo_grupo_nac.set("Terneros")
        self.combo_grupo_nac.pack(side="left", padx=5)
        add_tooltip(self.combo_grupo_nac, "Clasificación del animal al nacer.")

        # INFORMACIÓN DE PADRES
        frame_padres = ctk.CTkFrame(main_frame)
        frame_padres.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_padres, text="👨‍👩‍👧 INFORMACIÓN DE PADRES", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Madre
        row3 = ctk.CTkFrame(frame_padres, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row3, text="Madre:", width=100).pack(side="left", padx=5)
        self.combo_madre_nac = ctk.CTkComboBox(row3, width=300)
        self.combo_madre_nac.set("Seleccione la madre")
        self.combo_madre_nac.pack(side="left", padx=5)

        # Padre y Tipo Concepción
        row4 = ctk.CTkFrame(frame_padres, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row4, text="Padre:", width=100).pack(side="left", padx=5)
        self.combo_padre_nac = ctk.CTkComboBox(row4, width=200)
        self.combo_padre_nac.set("Seleccione el padre")
        self.combo_padre_nac.pack(side="left", padx=5)
        
        ctk.CTkLabel(row4, text="Concepción:", width=80).pack(side="left", padx=5)
        self.combo_concepcion_nac = ctk.CTkComboBox(row4, values=["Monta", "Inseminación"], width=150)
        self.combo_concepcion_nac.set("Monta")
        self.combo_concepcion_nac.pack(side="left", padx=5)

        # UBICACIÓN
        self.configurar_ubicacion(main_frame, "nac")

        # INFORMACIÓN ADICIONAL
        self.configurar_informacion_adicional(main_frame, "nac")

    def configurar_tab_compra(self):
        """Configura la pestaña de registro por compra"""
        main_frame = ctk.CTkScrollableFrame(self.tab_compra)
        main_frame.pack(fill="both", expand=True, padx=2, pady=8)

        # INFORMACIÓN BÁSICA
        frame_basica = ctk.CTkFrame(main_frame)
        frame_basica.pack(fill="x", pady=5)

        header_basica = ctk.CTkLabel(frame_basica, text="📋 INFORMACIÓN BÁSICA", 
                                      font=("Segoe UI", 16, "bold"))
        header_basica.pack(anchor="w", pady=(10, 2))
        helper_basica = ctk.CTkLabel(frame_basica, text="Campos marcados con * son obligatorios. Código y Fecha Compra requeridos.",
                                     font=("Segoe UI", 11, "italic"))
        helper_basica.pack(anchor="w", pady=(0, 6))
        add_tooltip(header_basica, "Datos generales del animal adquirido")
        add_tooltip(helper_basica, "Guía rápida de requisitos para el registro por compra")

        # Código y Nombre
        row1 = ctk.CTkFrame(frame_basica, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        self.entry_codigo_comp = ctk.CTkEntry(row1, placeholder_text="Código Animal *", width=200)
        self.entry_codigo_comp.pack(side="left", padx=5)
        add_tooltip(self.entry_codigo_comp, "Identificador único. No repetir códigos.")

        self.entry_nombre_comp = ctk.CTkEntry(row1, placeholder_text="Nombre (Opcional)", width=200)
        self.entry_nombre_comp.pack(side="left", padx=5)
        add_tooltip(self.entry_nombre_comp, "Nombre para referencia interna. Puede quedar vacío.")

        # Fechas y Sexo
        row2 = ctk.CTkFrame(frame_basica, fg_color="transparent")
        row2.pack(fill="x", pady=5)

        self.entry_fecha_nac_comp = ctk.CTkEntry(row2, placeholder_text="Fecha Nacimiento (YYYY-MM-DD)", width=180)
        self.entry_fecha_nac_comp.pack(side="left", padx=5)
        attach_date_picker(row2, self.entry_fecha_nac_comp)
        add_tooltip(self.entry_fecha_nac_comp, "Solo si se conoce; de lo contrario dejar vacío.")

        self.entry_fecha_compra = ctk.CTkEntry(row2, placeholder_text="Fecha Compra (YYYY-MM-DD) *", width=180)
        self.entry_fecha_compra.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_compra.pack(side="left", padx=5)
        attach_date_picker(row2, self.entry_fecha_compra)
        add_tooltip(self.entry_fecha_compra, "Día en que se adquirió el animal. Obligatorio.")

        self.combo_sexo_comp = ctk.CTkComboBox(row2, values=["Macho", "Hembra"], width=150)
        self.combo_sexo_comp.set("Macho")
        self.combo_sexo_comp.pack(side="left", padx=5)
        add_tooltip(self.combo_sexo_comp, "Seleccione el sexo del animal.")

        # INFORMACIÓN COMPRA
        frame_compra = ctk.CTkFrame(main_frame)
        frame_compra.pack(fill="x", pady=5)

        header_compra = ctk.CTkLabel(frame_compra, text="💰 INFORMACIÓN DE COMPRA", 
                                     font=("Segoe UI", 16, "bold"))
        header_compra.pack(anchor="w", pady=(10, 2))
        helper_compra = ctk.CTkLabel(frame_compra, text="Origen, precio y peso ayudan a análisis de costos y conversión.",
                                     font=("Segoe UI", 11, "italic"))
        helper_compra.pack(anchor="w", pady=(0, 6))
        add_tooltip(header_compra, "Datos específicos de la transacción de compra")
        add_tooltip(helper_compra, "Recomendado completar para métricas económicas")

        # Vendedor y Precio
        row3 = ctk.CTkFrame(frame_compra, fg_color="transparent")
        row3.pack(fill="x", pady=5)

        lbl_origen = ctk.CTkLabel(row3, text="Origen (Procedencia/Vendedor):", width=180)
        lbl_origen.pack(side="left", padx=5)
        self.combo_vendedor = ctk.CTkComboBox(row3, width=300)
        self.combo_vendedor.set("Seleccione procedencia o vendedor")
        self.combo_vendedor.pack(side="left", padx=5)
        add_tooltip(lbl_origen, "Seleccione primero una procedencia; si no existe, el vendedor.")
        add_tooltip(self.combo_vendedor, "Lista prioriza procedencias; luego vendedores.")

        lbl_precio = ctk.CTkLabel(row3, text="Precio Compra ($):", width=130)
        lbl_precio.pack(side="left", padx=5)
        self.entry_precio = ctk.CTkEntry(row3, placeholder_text="Ej: 1250.50", width=150)
        self.entry_precio.pack(side="left", padx=5)
        add_tooltip(lbl_precio, "Valor pagado por el animal.")
        add_tooltip(self.entry_precio, "Use punto para decimales. Puede dejarse vacío si no aplica.")

        # Peso Compra
        row4 = ctk.CTkFrame(frame_compra, fg_color="transparent")
        row4.pack(fill="x", pady=5)

        lbl_peso_compra = ctk.CTkLabel(row4, text=f"Peso al Comprar ({units_helper.weight_unit}):", width=180)
        lbl_peso_compra.pack(side="left", padx=5)
        self.entry_peso_compra = ctk.CTkEntry(row4, placeholder_text="Peso estimado en la compra", width=200)
        self.entry_peso_compra.pack(side="left", padx=5)
        add_tooltip(lbl_peso_compra, "Peso aproximado al momento de la compra.")
        add_tooltip(self.entry_peso_compra, "Puede dejarse vacío; ayudará a evaluar ganancias de peso.")

        # Grupo de compra
        lbl_grupo = ctk.CTkLabel(row4, text="Grupo:", width=80)
        lbl_grupo.pack(side="left", padx=5)
        self.combo_grupo_comp = ctk.CTkComboBox(row4, values=["Toros", "Vacas", "Terneros", "Novillos"], width=150)
        self.combo_grupo_comp.set("Novillos")
        self.combo_grupo_comp.pack(side="left", padx=5)
        add_tooltip(self.combo_grupo_comp, "Clasificación del animal al momento de la compra.")

        # UBICACIÓN
        self.configurar_ubicacion(main_frame, "comp")

        # INFORMACIÓN ADICIONAL
        self.configurar_informacion_adicional(main_frame, "comp")

    def configurar_ubicacion(self, parent, tipo):
        """Configura la sección de ubicación"""
        frame_ubicacion = ctk.CTkFrame(parent)
        frame_ubicacion.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_ubicacion, text="📍 UBICACIÓN", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Finca
        row1 = ctk.CTkFrame(frame_ubicacion, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row1, text="Finca:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_finca_nac = ctk.CTkComboBox(row1, width=300, state="readonly",
                                                    command=lambda _: self.on_finca_change("nac"))
            self.combo_finca_nac.pack(side="left", padx=5)
        else:
            self.combo_finca_comp = ctk.CTkComboBox(row1, width=300, state="readonly",
                                                     command=lambda _: self.on_finca_change("comp"))
            self.combo_finca_comp.pack(side="left", padx=5)

    # Potrero, Lote y Sector (antes 'Grupo')
        row2 = ctk.CTkFrame(frame_ubicacion, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row2, text="Potrero:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_potrero_nac = ctk.CTkComboBox(row2, width=200)
            self.combo_potrero_nac.set("Seleccione un potrero")
            self.combo_potrero_nac.pack(side="left", padx=5)
        else:
            self.combo_potrero_comp = ctk.CTkComboBox(row2, width=200)
            self.combo_potrero_comp.set("Seleccione un potrero")
            self.combo_potrero_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Lote:", width=80).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_lote_nac = ctk.CTkComboBox(row2, width=150)
            self.combo_lote_nac.set("Seleccione un lote")
            self.combo_lote_nac.pack(side="left", padx=5)
        else:
            self.combo_lote_comp = ctk.CTkComboBox(row2, width=150)
            self.combo_lote_comp.set("Seleccione un lote")
            self.combo_lote_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Sector:", width=80).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_sector_nac = ctk.CTkComboBox(row2, width=150)
            self.combo_sector_nac.set("Seleccione un sector")
            self.combo_sector_nac.pack(side="left", padx=5)
        else:
            self.combo_sector_comp = ctk.CTkComboBox(row2, width=150)
            self.combo_sector_comp.set("Seleccione un sector")
            self.combo_sector_comp.pack(side="left", padx=5)

    def configurar_informacion_adicional(self, parent, tipo):
        """Configura la sección de información adicional"""
        frame_adicional = ctk.CTkFrame(parent)
        frame_adicional.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_adicional, text="📝 INFORMACIÓN ADICIONAL", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Raza y Salud
        row1 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row1, text="Raza:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_raza_nac = ctk.CTkComboBox(row1, width=200, state="readonly")
            self.combo_raza_nac.set("Seleccione una raza")
            self.combo_raza_nac.pack(side="left", padx=5)
        else:
            self.combo_raza_comp = ctk.CTkComboBox(row1, width=200, state="readonly")
            self.combo_raza_comp.set("Seleccione una raza")
            self.combo_raza_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Salud:", width=80).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_salud_nac = ctk.CTkComboBox(row1, values=["Sano", "Enfermo"], width=150)
            self.combo_salud_nac.set("Sano")
            self.combo_salud_nac.pack(side="left", padx=5)
        else:
            self.combo_salud_comp = ctk.CTkComboBox(row1, values=["Sano", "Enfermo"], width=150)
            self.combo_salud_comp.set("Sano")
            self.combo_salud_comp.pack(side="left", padx=5)

        # Condición Corporal (cargada desde BD)
        ctk.CTkLabel(row1, text="Condición Corporal:", width=130).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_condicion_nac = ctk.CTkComboBox(row1, values=[], width=200)
            self.combo_condicion_nac.set("")
            self.combo_condicion_nac.pack(side="left", padx=5)
            add_tooltip(self.combo_condicion_nac, "Condición corporal del animal (escala BCS)")
        else:
            self.combo_condicion_comp = ctk.CTkComboBox(row1, values=[], width=200)
            self.combo_condicion_comp.set("")
            self.combo_condicion_comp.pack(side="left", padx=5)
            add_tooltip(self.combo_condicion_comp, "Condición corporal del animal (escala BCS)")

        # Estado
        row2 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row2, text="Estado:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_estado_nac = ctk.CTkComboBox(row2, values=["Activo", "Vendido", "Muerto"], width=200)
            self.combo_estado_nac.set("Activo")
            self.combo_estado_nac.pack(side="left", padx=5)
        else:
            self.combo_estado_comp = ctk.CTkComboBox(row2, values=["Activo", "Vendido", "Muerto"], width=200)
            self.combo_estado_comp.set("Activo")
            self.combo_estado_comp.pack(side="left", padx=5)

        # Características físicas
        row3 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row3, text="Color:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.entry_color_nac = ctk.CTkEntry(row3, placeholder_text="Color del animal", width=150)
            self.entry_color_nac.pack(side="left", padx=5)
        else:
            self.entry_color_comp = ctk.CTkEntry(row3, placeholder_text="Color del animal", width=150)
            self.entry_color_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row3, text="Hierro:", width=80).pack(side="left", padx=5)
        if tipo == "nac":
            self.entry_hierro_nac = ctk.CTkEntry(row3, placeholder_text="Marca de hierro", width=150)
            self.entry_hierro_nac.pack(side="left", padx=5)
        else:
            self.entry_hierro_comp = ctk.CTkEntry(row3, placeholder_text="Marca de hierro", width=150)
            self.entry_hierro_comp.pack(side="left", padx=5)

        # Número de hierros y composición racial
        row4 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row4, text="N° Hierros:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.entry_num_hierros_nac = ctk.CTkEntry(row4, placeholder_text="0", width=100)
            self.entry_num_hierros_nac.pack(side="left", padx=5)
        else:
            self.entry_num_hierros_comp = ctk.CTkEntry(row4, placeholder_text="0", width=100)
            self.entry_num_hierros_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row4, text="Composición Racial:", width=140).pack(side="left", padx=5)
        if tipo == "nac":
            self.entry_composicion_nac = ctk.CTkEntry(row4, placeholder_text="Ej: 75% Holstein, 25% Gyr", width=250)
            self.entry_composicion_nac.pack(side="left", padx=5)
        else:
            self.entry_composicion_comp = ctk.CTkEntry(row4, placeholder_text="Ej: 75% Holstein, 25% Gyr", width=250)
            self.entry_composicion_comp.pack(side="left", padx=5)

        # Comentarios
        row5 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row5.pack(fill="both", expand=True, pady=5)
        
        ctk.CTkLabel(row5, text="Comentarios:", width=100).pack(side="left", padx=5, anchor="n")
        if tipo == "nac":
            self.text_comentarios_nac = ctk.CTkTextbox(row5, width=400, height=100)
            self.text_comentarios_nac.pack(side="left", padx=5, fill="both", expand=True)
        else:
            self.text_comentarios_comp = ctk.CTkTextbox(row5, width=400, height=100)
            self.text_comentarios_comp.pack(side="left", padx=5, fill="both", expand=True)

        # Foto
        row6 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row6.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row6, text="Foto:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.btn_foto_nac = ctk.CTkButton(row6, text="📷 Cargar Foto", command=self.cargar_foto_nac)
            self.btn_foto_nac.pack(side="left", padx=5)
            self.label_foto_nac = ctk.CTkLabel(row6, text="No hay foto seleccionada")
            self.label_foto_nac.pack(side="left", padx=5)
        else:
            self.btn_foto_comp = ctk.CTkButton(row6, text="📷 Cargar Foto", command=self.cargar_foto_comp)
            self.btn_foto_comp.pack(side="left", padx=5)
            self.label_foto_comp = ctk.CTkLabel(row6, text="No hay foto seleccionada")
            self.label_foto_comp.pack(side="left", padx=5)

    def cargar_datos_combos(self):
        """Carga datos base (fincas, razas) y deja dependientes vacíos hasta seleccionar finca."""
        # Cache: si existe y no forzado y dentro de TTL, reutilizar
        import time
        TTL = 60  # segundos
        if getattr(self, '_combo_cache', None):
            ts = self._combo_cache.get('timestamp', 0)
            if time.time() - ts < TTL and not getattr(self, '_force_reload', False):
                datos = self._combo_cache['data']
                self._apply_cached_combo_data(datos)
                return
        self._force_reload = False
        try:
            # Cargar fincas usando AnimalService (FASE 8.3)
            raw_fincas = self.animal_service.cargar_fincas()
            excluir = {'eliminada','eliminado','inactiva','inactivo'}
            finca_rows = [r for r in raw_fincas if (r.get('estado') or '').lower() not in excluir]
            if not finca_rows:
                finca_rows = raw_fincas  # fallback si quedara vacío tras filtro
            # Construir valores visibles con ID-prefijo: "<id> - <nombre>"
            fincas = [f"{row['id']} - {row['nombre']}" for row in finca_rows]
            # Mapas para uso interno
            self._finca_id_map = {row['nombre']: row['id'] for row in finca_rows}
            self._finca_display_to_id = {f"{row['id']} - {row['nombre']}": row['id'] for row in finca_rows}
            # Leer finca por defecto (LEGACY: se requiere get_db_connection para app_settings)
            default_finca_key = None
            try:
                from database.database import get_db_connection as _legacy_get_db
                with _legacy_get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT valor FROM app_settings WHERE clave = 'default_finca_id'")
                    row = cursor.fetchone()
                    if row and row[0]:
                        dfid = int(str(row[0]).strip())
                        for nombre, _id in self._finca_id_map.items():
                            if _id == dfid:
                                default_finca_key = nombre
                                break
            except Exception:
                pass
            
            # Cargar razas usando AnimalService (FASE 8.3)
            raw_razas = self.animal_service.cargar_razas()
            raza_rows = [r for r in raw_razas if (r.get('estado') or '').lower() not in ('inactiva','eliminada')]
            if not raza_rows:
                raza_rows = raw_razas
            razas = [f"{row['id']} - {row['nombre']}" for row in raza_rows]
            self._raza_id_map = {row['nombre']: row['id'] for row in raza_rows}
            self._raza_display_to_id = {f"{row['id']} - {row['nombre']}": row['id'] for row in raza_rows}
            
            # Cargar condiciones corporales usando AnimalService (FASE 8.3)
            condicion_rows = self.animal_service.cargar_condiciones_corporales()
            condiciones = [f"{row['codigo']} - {row['descripcion']}" for row in condicion_rows]
            self._condicion_map = {f"{row['codigo']} - {row['descripcion']}": row['codigo'] for row in condicion_rows}
            
            # No cargar padres globales; se cargarán al elegir finca
            madres = []
            padres = []
            self._madre_id_map = {}
            self._padre_id_map = {}
            
            # No cargar procedencias/vendedores globales; se filtrarán por finca si existe FK
            procedencias = []
            vendedores = []
            self._procedencia_id_map = {}
            self._vendedor_id_map = {}
            
            # No cargar potreros/lotes/grupos hasta elegir finca
            potreros = []
            lotes = []
            grupos = []
            self._potrero_id_map = {}
            self._lote_id_map = {}
            self._grupo_id_map = {}
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{e}")
            return
        
        # DEBUG: Imprimir datos cargados para verificar
        print(f"\n{'='*60}")
        print(f"DATOS CARGADOS EN REGISTRO DE ANIMALES")
        print(f"{'='*60}")
        print(f"\n🏢 FINCAS cargadas: {len(fincas)}")
        for i, f in enumerate(fincas, 1):
            print(f"   {i}. {f}")
        print(f"\n🐄 RAZAS cargadas: {len(razas)}")
        for i, r in enumerate(razas, 1):
            print(f"   {i:2d}. {r}")
        print(f"{'='*60}\n")
        
        # Asignar a combos de nacimiento
        if hasattr(self, 'combo_finca_nac'):
            self.combo_finca_nac.configure(values=fincas)
            if fincas:
                # Selección por defecto: si hay default_finca_key (nombre), conviértelo a display con ID
                default_display = None
                if default_finca_key:
                    dfid = self._finca_id_map.get(default_finca_key)
                    if dfid is not None:
                        for disp, did in self._finca_display_to_id.items():
                            if did == dfid:
                                default_display = disp
                                break
                self.combo_finca_nac.set(default_display or fincas[0])
            print(f"✓ Combo finca_nac configurado con {len(fincas)} fincas")
            
        if hasattr(self, 'combo_raza_nac'):
            self.combo_raza_nac.configure(values=razas)
            if razas:
                self.combo_raza_nac.set(razas[0])
            print(f"✓ Combo raza_nac configurado con {len(razas)} razas")
        
        # Condiciones corporales para nacimiento
        if hasattr(self, 'combo_condicion_nac'):
            self.combo_condicion_nac.configure(values=condiciones)
            if condiciones:
                self.combo_condicion_nac.set(condiciones[0])
            
        if hasattr(self, 'combo_madre_nac'):
            self.combo_madre_nac.configure(values=madres)
            
        if hasattr(self, 'combo_padre_nac'):
            self.combo_padre_nac.configure(values=padres)
            
        if hasattr(self, 'combo_potrero_nac'):
            self.combo_potrero_nac.configure(values=["Seleccione finca primero"])
            self.combo_potrero_nac.set("Seleccione finca primero")
        if hasattr(self, 'combo_lote_nac'):
            self.combo_lote_nac.configure(values=["Seleccione finca primero"])
            self.combo_lote_nac.set("Seleccione finca primero")
        if hasattr(self, 'combo_sector_nac'):
            self.combo_sector_nac.configure(values=["Seleccione finca primero"])
            self.combo_sector_nac.set("Seleccione finca primero")
        
        # Asignar a combos de compra
        if hasattr(self, 'combo_finca_comp'):
            self.combo_finca_comp.configure(values=fincas)
            if fincas:
                self.combo_finca_comp.set(default_display or fincas[0])
            print(f"✓ Combo finca_comp configurado con {len(fincas)} fincas")
            
        if hasattr(self, 'combo_raza_comp'):
            self.combo_raza_comp.configure(values=razas)
            if razas:
                self.combo_raza_comp.set(razas[0])
            print(f"✓ Combo raza_comp configurado con {len(razas)} razas")
        
        # Condiciones corporales para compra
        if hasattr(self, 'combo_condicion_comp'):
            self.combo_condicion_comp.configure(values=condiciones)
            if condiciones:
                self.combo_condicion_comp.set(condiciones[0])
            
        if hasattr(self, 'combo_vendedor'):
            # Inicialmente vacío, se carga al seleccionar finca
            self.combo_vendedor.configure(values=["Seleccione finca primero"])
            self.combo_vendedor.set("Seleccione finca primero")
            
        if hasattr(self, 'combo_potrero_comp'):
            self.combo_potrero_comp.configure(values=["Seleccione finca primero"])
            self.combo_potrero_comp.set("Seleccione finca primero")
        if hasattr(self, 'combo_lote_comp'):
            self.combo_lote_comp.configure(values=["Seleccione finca primero"])
            self.combo_lote_comp.set("Seleccione finca primero")
        if hasattr(self, 'combo_sector_comp'):
            self.combo_sector_comp.configure(values=["Seleccione finca primero"])
            self.combo_sector_comp.set("Seleccione finca primero")

        # Guardar en cache
        try:
            import time
            self._combo_cache = {
                'timestamp': time.time(),
                'data': {
                    'fincas': fincas, 'razas': razas, 'madres': madres, 'padres': padres,
                    'procedencias': procedencias, 'vendedores': vendedores, 'potreros': potreros,
                    'lotes': lotes, 'sectores': grupos, 'default_finca': default_finca_key
                }
            }
        except Exception:
            pass

        # Autocomplete deshabilitado por solicitud del usuario
        # ===== Cargar datos dependientes de la finca por defecto =====
        # Ejecutar on_finca_change automáticamente para ambas pestañas si hay finca seleccionada
        try:
            if fincas:
                if hasattr(self, 'combo_finca_nac') and self.combo_finca_nac.get():
                    self.on_finca_change("nac")
                if hasattr(self, 'combo_finca_comp') and self.combo_finca_comp.get():
                    self.on_finca_change("comp")
        except Exception as e:
            self.logger.warning(f"Error al cargar datos dependientes iniciales: {e}")

    def _apply_cached_combo_data(self, data):
        fincas = data.get('fincas', [])
        razas = data.get('razas', [])
        madres = data.get('madres', [])
        padres = data.get('padres', [])
        procedencias = data.get('procedencias', [])
        vendedores = data.get('vendedores', [])
        potreros = data.get('potreros', [])
        lotes = data.get('lotes', [])
        # Backward compatibility: aceptar clave antigua 'grupos'
        grupos = data.get('sectores', data.get('grupos', []))
        default_finca_key = data.get('default_finca')
        # Reaplicar valores
        if hasattr(self, 'combo_finca_nac'):
            self.combo_finca_nac.configure(values=fincas)
        if hasattr(self, 'combo_finca_comp'):
            self.combo_finca_comp.configure(values=fincas)
        if hasattr(self, 'combo_raza_nac'):
            self.combo_raza_nac.configure(values=razas)
        if hasattr(self, 'combo_raza_comp'):
            self.combo_raza_comp.configure(values=razas)
        if hasattr(self, 'combo_madre_nac'):
            self.combo_madre_nac.configure(values=madres)
        if hasattr(self, 'combo_padre_nac'):
            self.combo_padre_nac.configure(values=padres)
        if hasattr(self, 'combo_vendedor'):
            base_vend = procedencias or vendedores
            self.combo_vendedor.configure(values=base_vend)
        if hasattr(self, 'combo_potrero_nac'):
            self.combo_potrero_nac.configure(values=potreros)
        if hasattr(self, 'combo_potrero_comp'):
            self.combo_potrero_comp.configure(values=potreros)
        if hasattr(self, 'combo_lote_nac'):
            self.combo_lote_nac.configure(values=lotes)
        if hasattr(self, 'combo_lote_comp'):
            self.combo_lote_comp.configure(values=lotes)
        if hasattr(self, 'combo_sector_nac'):
            self.combo_sector_nac.configure(values=grupos)
        if hasattr(self, 'combo_sector_comp'):
            self.combo_sector_comp.configure(values=grupos)
        # Autocomplete deshabilitado

    def refrescar_listas(self):
        # Forzar recarga ignorando cache
        self._force_reload = True
        super_reload = getattr(super(), 'refrescar_listas', None)
        # Reusar ya existente lógica de recarga combos
        self.cargar_datos_combos()
        modo = self._get_autocomplete_mode()
        self._apply_mode_all_combos(modo)
        messagebox.showinfo("Refrescado", "Listas recargadas (cache actualizado).")

    # ---------------- Autocomplete global mode persistence -----------------
    def _get_autocomplete_mode(self) -> str:
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT valor FROM app_settings WHERE clave='autocomplete_match_mode'")
                row = cur.fetchone()
                if row and row[0] in ("contains", "startswith"):
                    return row[0]
        except Exception:
            pass
        return "contains"

    def _save_autocomplete_mode(self, modo: str):
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE app_settings SET valor=? WHERE clave='autocomplete_match_mode'", (modo,))
                if cur.rowcount == 0:
                    cur.execute("INSERT INTO app_settings (clave, valor) VALUES (?, ?)", ("autocomplete_match_mode", modo))
                conn.commit()
        except Exception:
            pass

    def _init_global_autocomplete_switch(self):
        modo = self._get_autocomplete_mode()
        switch = getattr(self, 'switch_autocomplete_global', None)
        if modo == 'startswith':
            try:
                if switch:
                    switch.select()
            except Exception:
                pass
        else:
            try:
                if switch:
                    switch.deselect()
            except Exception:
                pass

    def _apply_mode_all_combos(self, modo: str):
        combos = [
            'combo_finca_nac','combo_finca_comp','combo_raza_nac','combo_raza_comp',
            'combo_madre_nac','combo_padre_nac','combo_vendedor','combo_potrero_nac',
            'combo_potrero_comp','combo_lote_nac','combo_lote_comp','combo_sector_nac','combo_sector_comp'
        ]
        for attr in combos:
            combo = getattr(self, attr, None)
            if combo is not None:
                try:
                    set_autocomplete_mode(combo, modo)
                except Exception:
                    pass

    def _toggle_global_autocomplete_mode(self):
        switch = getattr(self, 'switch_autocomplete_global', None)
        try:
            estado = switch.get() if switch is not None else 0
        except Exception:
            estado = 0
        modo = 'startswith' if estado == 1 else 'contains'
        self._save_autocomplete_mode(modo)
        self._apply_mode_all_combos(modo)

    def on_finca_change(self, tipo):
        """Filtra potreros y lotes cuando cambia la finca seleccionada"""
        try:
            # Obtener finca seleccionada
            if tipo == "nac":
                finca_str = self.combo_finca_nac.get()
            else:
                finca_str = self.combo_finca_comp.get()
            
            if not finca_str:
                return
            
            # Obtener ID de la finca desde el mapa (sin prefijo en display)
            finca_id = None
            if hasattr(self, '_finca_id_map') and finca_str in self._finca_id_map:
                finca_id = self._finca_id_map[finca_str]
            else:
                # Fallback por compatibilidad si viniera con formato antiguo
                if '-' in finca_str:
                    try:
                        finca_id = int(finca_str.split('-',1)[0].strip())
                    except Exception:
                        finca_id = None
            if finca_id is None:
                return
            
            # Cargar madres usando AnimalService (FASE 8.3)
            try:
                madre_list = self.animal_service.cargar_madres_por_finca(finca_id)
                madres = [f"{row['codigo']} ({row['nombre'] or 'Sin nombre'})" for row in madre_list]
                self._madre_id_map = {f"{row['codigo']} ({row['nombre'] or 'Sin nombre'})": row['id'] for row in madre_list}
                padre_list = self.animal_service.cargar_padres_por_finca(finca_id)
                padres = [f"{row['codigo']} ({row['nombre'] or 'Sin nombre'})" for row in padre_list]
                self._padre_id_map = {f"{row['codigo']} ({row['nombre'] or 'Sin nombre'})": row['id'] for row in padre_list}
            except Exception:
                madres, padres = [], []

            # Cargar potreros filtrados usando AnimalService (FASE 8.3)
            try:
                potrero_list = self.animal_service.cargar_potreros_por_finca(finca_id)
                potreros = [row['nombre'] for row in potrero_list]
                self._potrero_id_map = {row['nombre']: row['id'] for row in potrero_list}
            except Exception:
                potreros = []
                self._potrero_id_map = {}
            
            # Cargar lotes filtrados usando AnimalService (FASE 8.3)
            try:
                lote_list = self.animal_service.cargar_lotes_por_finca(finca_id)
                lotes = [row['nombre'] for row in lote_list]
                self._lote_id_map = {row['nombre']: row['id'] for row in lote_list}
            except Exception:
                lotes = []
                self._lote_id_map = {}
            
            # Cargar sectores filtrados usando AnimalService (FASE 8.3)
            grupos = []  # reutilizamos variable 'grupos' para minimizar cambios posteriores
            try:
                sector_list = self.animal_service.cargar_sectores_por_finca(finca_id)
                grupos = [row['nombre'] for row in sector_list]
                # Mapa de sectores (usamos nombre de variable legacy para compatibilidad en resto del código)
                self._sector_id_map = {row['nombre']: row['id'] for row in sector_list}
            except Exception:
                grupos = []
                self._sector_id_map = {}

            # Cargar procedencias y vendedores usando AnimalService (FASE 8.3)
            procedencias = []
            vendedores = []
            base_origen = []
            self._origen_id_map = {}
            try:
                # Intentar cargar procedencias
                proc_list = self.animal_service.cargar_procedencias(finca_id)
                procedencias = [r['descripcion'] for r in proc_list]
                self._procedencia_id_map = {r['descripcion']: r['id'] for r in proc_list}
                if not procedencias:
                    # Si no hay procedencias, cargar vendedores
                    vend_list = self.animal_service.cargar_vendedores(finca_id)
                    vendedores = [r['nombre'] for r in vend_list]
                    self._vendedor_id_map = {r['nombre']: r['id'] for r in vend_list}
                else:
                    vendedores = []
                    self._vendedor_id_map = {}
            except Exception:
                procedencias = []
                vendedores = []
                self._procedencia_id_map = {}
                self._vendedor_id_map = {}
                
                # Actualizar combos según tipo
                if tipo == "nac":
                    if hasattr(self, 'combo_potrero_nac'):
                        self.combo_potrero_nac.configure(values=potreros)
                        if potreros:
                            self.combo_potrero_nac.set(potreros[0])
                        else:
                            self.combo_potrero_nac.set("")
                    
                    if hasattr(self, 'combo_lote_nac'):
                        self.combo_lote_nac.configure(values=lotes)
                        if lotes:
                            self.combo_lote_nac.set(lotes[0])
                        else:
                            self.combo_lote_nac.set("")
                    # Actualizar sectores (variables renombradas de grupo a sector)
                    if hasattr(self, 'combo_sector_nac'):
                        self.combo_sector_nac.configure(values=grupos if grupos else ["Sin sectores"])
                        if grupos:
                            self.combo_sector_nac.set(grupos[0])
                        else:
                            self.combo_sector_nac.set("Sin sectores")
                    # Actualizar padres
                    if hasattr(self, 'combo_madre_nac'):
                        self.combo_madre_nac.configure(values=madres)
                        if madres:
                            self.combo_madre_nac.set(madres[0])
                        else:
                            self.combo_madre_nac.set("")
                    if hasattr(self, 'combo_padre_nac'):
                        self.combo_padre_nac.configure(values=padres)
                        if padres:
                            self.combo_padre_nac.set(padres[0])
                        else:
                            self.combo_padre_nac.set("")
                else:
                    if hasattr(self, 'combo_potrero_comp'):
                        self.combo_potrero_comp.configure(values=potreros)
                        if potreros:
                            self.combo_potrero_comp.set(potreros[0])
                        else:
                            self.combo_potrero_comp.set("")
                    
                    if hasattr(self, 'combo_lote_comp'):
                        self.combo_lote_comp.configure(values=lotes)
                        if lotes:
                            self.combo_lote_comp.set(lotes[0])
                        else:
                            self.combo_lote_comp.set("")
                    # Actualizar sectores (variables renombradas de grupo a sector)
                    if hasattr(self, 'combo_sector_comp'):
                        self.combo_sector_comp.configure(values=grupos if grupos else ["Sin sectores"])
                        if grupos:
                            self.combo_sector_comp.set(grupos[0])
                        else:
                            self.combo_sector_comp.set("Sin sectores")
                    # Actualizar origen/vendedor para compra
                    if hasattr(self, 'combo_vendedor'):
                        base_vend = base_origen or procedencias or vendedores
                        self.combo_vendedor.configure(values=base_vend)
                        if base_vend:
                            self.combo_vendedor.set(base_vend[0])
                        else:
                            self.combo_vendedor.set("Sin datos")
                            
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudieron cargar los datos de la finca: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado al filtrar por finca: {e}")

    def cargar_foto_nac(self):
        self.cargar_foto("nac")

    def cargar_foto_comp(self):
        self.cargar_foto("comp")

    def cargar_foto(self, tipo):
        """Carga una foto del animal"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar foto del animal",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.foto_path = file_path
            if tipo == "nac":
                self.label_foto_nac.configure(text=f"Foto: {os.path.basename(file_path)}")
            else:
                self.label_foto_comp.configure(text=f"Foto: {os.path.basename(file_path)}")

    def validar_datos(self, tipo):
        """Valida los datos antes de guardar - VERSIÓN MEJORADA"""
        if tipo == "nac":
            codigo = self.entry_codigo_nac.get().strip()
            fecha_nac = self.entry_fecha_nac.get().strip()
            finca = self.combo_finca_nac.get().strip()
            sexo = self.combo_sexo_nac.get().strip()
            raza = self.combo_raza_nac.get().strip()
        else:
            codigo = self.entry_codigo_comp.get().strip()
            fecha_compra = self.entry_fecha_compra.get().strip()
            finca = self.combo_finca_comp.get().strip()
            sexo = self.combo_sexo_comp.get().strip()
            raza = self.combo_raza_comp.get().strip()

        if not codigo:
            messagebox.showwarning("Atención", "El código del animal es obligatorio.")
            return False
        
        if not finca or finca in ("", "Seleccione una finca"):
            messagebox.showwarning("Atención", "Debe seleccionar una finca.")
            return False
        
        if not sexo or sexo in ("", "Seleccione el sexo"):
            messagebox.showwarning("Atención", "Debe seleccionar el sexo del animal.")
            return False
        
        if not raza or raza in ("", "Seleccione una raza"):
            messagebox.showwarning("Atención", "Debe seleccionar una raza.")
            return False
            
        if tipo == "nac" and not fecha_nac:
            messagebox.showwarning("Atención", "La fecha de nacimiento es obligatoria.")
            return False
            
        if tipo == "comp" and not fecha_compra:
            messagebox.showwarning("Atención", "La fecha de compra es obligatoria.")
            return False

        return True

    def guardar_animal(self):
        """Guarda el animal según la pestaña activa"""
        tab_actual = self.notebook.index(self.notebook.select())
        
        if tab_actual == 0:  # Nacimiento
            self.guardar_nacimiento()
        else:  # Compra
            self.guardar_compra()

    def guardar_nacimiento(self):
        """Guarda un animal registrado por nacimiento"""
        if not self.validar_datos("nac"):
            return

        try:
            # Recoger datos
            codigo = truncate(self.entry_codigo_nac.get().strip().upper(), "codigo_animal")
            nombre = truncate(self.entry_nombre_nac.get().strip(), "nombre_animal") or None
            fecha_nacimiento = self.entry_fecha_nac.get().strip()
            sexo = self.combo_sexo_nac.get()
            
            # Función auxiliar para extraer ID de forma segura
            def extraer_id(valor_combo, mapa=None):
                """Obtiene el ID desde el display 'ID - Nombre' o usando mapa nombre->id si existe."""
                if not valor_combo:
                    return None
                valor_combo = valor_combo.strip()
                # Si el valor viene como 'ID - Nombre', tomar el prefijo ID
                if '-' in valor_combo:
                    try:
                        return int(valor_combo.split('-',1)[0].strip())
                    except Exception:
                        return None
                # Si se pasa solo el nombre y existe mapa nombre->id
                if mapa and valor_combo in mapa:
                    return mapa[valor_combo]
                return None
            
            # Obtener IDs de forma segura
            id_finca = extraer_id(self.combo_finca_nac.get(), getattr(self, '_finca_id_map', None))
            raza_id = extraer_id(self.combo_raza_nac.get(), getattr(self, '_raza_id_map', None))
            id_madre = extraer_id(self.combo_madre_nac.get(), getattr(self, '_madre_id_map', None))
            id_padre = extraer_id(self.combo_padre_nac.get(), getattr(self, '_padre_id_map', None))
            id_potrero = extraer_id(self.combo_potrero_nac.get(), getattr(self, '_potrero_id_map', None))
            id_lote = extraer_id(self.combo_lote_nac.get(), getattr(self, '_lote_id_map', None))
            # Obtener id_grupo (tabla animal usa id_grupo para almacenar sector)
            id_sector = extraer_id(self.combo_sector_nac.get(), getattr(self, '_sector_id_map', None))
            
            # Convertir peso al nacer a kg para almacenar en BD
            peso_nac_input = self.entry_peso_nacimiento.get().strip()
            peso_nac_kg = None
            if peso_nac_input:
                try:
                    peso_nac_kg = units_helper.convert_weight_to_kg(float(peso_nac_input))
                except ValueError:
                    messagebox.showwarning("Atención", "Peso al nacer debe ser numérico.")
                    return

            # Validar campos obligatorios
            if not codigo or not codigo.strip():
                messagebox.showerror("Error de Validación", "El código del animal es obligatorio.")
                return
            
            if not fecha_nacimiento or not fecha_nacimiento.strip():
                messagebox.showerror("Error de Validación", "La fecha de nacimiento es obligatoria.")
                return
            
            # Validar formato de fecha
            try:
                datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error de Validación", "Formato de fecha inválido. Use YYYY-MM-DD.")
                return
            
            # Validar conjunto de datos antes de insertar
            es_valido, errores = animal_validator.validar_animal_completo({
                'codigo': codigo,
                'peso_nacimiento': peso_nac_kg,
                'fecha_nacimiento': fecha_nacimiento,
                'sexo': sexo,
            })
            if not es_valido:
                messagebox.showerror("Validación", "\n".join(errores[:6]))
                return
            
            # Obtener grupo y condicion_corporal
            grupo_nac = self.combo_grupo_nac.get() if hasattr(self, 'combo_grupo_nac') else None
            condicion_nac = extraer_id(self.combo_condicion_nac.get(), getattr(self, '_condicion_map', None)) if hasattr(self, 'combo_condicion_nac') else None
            
            # Preparar datos para inserción
            datos_insercion = (
                id_finca, codigo, nombre, 'Nacimiento', sexo, raza_id,
                id_potrero, id_lote, id_sector, fecha_nacimiento, None,
                peso_nac_kg,
                None,
                None,
                None,
                id_padre, id_madre, self.combo_concepcion_nac.get(),
                self.combo_salud_nac.get(), self.combo_estado_nac.get(), 0,
                self.entry_color_nac.get().strip() or None,
                self.entry_hierro_nac.get().strip() or None,
                int(self.entry_num_hierros_nac.get().strip()) if self.entry_num_hierros_nac.get().strip() else 0,
                self.entry_composicion_nac.get().strip() or None,
                self.text_comentarios_nac.get("1.0", "end-1c").strip() or None,
                self.foto_path,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                grupo_nac,  # categoria
                grupo_nac,  # grupo_compra
                condicion_nac
            )
            
            # Insertar en BD usando AnimalService (FASE 8.3)
            try:
                # Construir diccionario de datos para el servicio
                datos_insercion_dict = {
                    'id_finca': id_finca,
                    'codigo': codigo,
                    'nombre': nombre,
                    'tipo_ingreso': 'Nacimiento',
                    'sexo': sexo,
                    'raza_id': raza_id,
                    'id_potrero': id_potrero,
                    'lote_id': id_lote,
                    'id_sector': id_sector,
                    'fecha_nacimiento': fecha_nacimiento,
                    'fecha_compra': None,
                    'peso_nacimiento': peso_nac_kg,
                    'peso_compra': None,
                    'id_vendedor': None,
                    'precio_compra': None,
                    'id_padre': id_padre,
                    'id_madre': id_madre,
                    'tipo_concepcion': self.combo_concepcion_nac.get(),
                    'salud': self.combo_salud_nac.get(),
                    'estado': self.combo_estado_nac.get(),
                    'inventariado': 0,
                    'color': self.entry_color_nac.get().strip() or None,
                    'hierro': self.entry_hierro_nac.get().strip() or None,
                    'numero_hierros': int(self.entry_num_hierros_nac.get().strip()) if self.entry_num_hierros_nac.get().strip() else 0,
                    'composicion_racial': self.entry_composicion_nac.get().strip() or None,
                    'comentarios': self.text_comentarios_nac.get("1.0", "end-1c").strip() or None,
                    'foto_path': self.foto_path,
                    'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'categoria': grupo_nac,
                    'grupo_compra': grupo_nac,
                    'condicion_corporal': condicion_nac,
                    'ultimo_peso': peso_nac_kg,
                    'fecha_ultimo_peso': datetime.now().strftime('%Y-%m-%d') if peso_nac_kg else None
                }
                self.animal_service.registrar_animal(datos_insercion_dict)
            except ValueError as ve:
                # Excepciones de validación del servicio (código duplicado, sexo inválido, etc.)
                messagebox.showerror("Validación", str(ve))
                return
            except Exception as e:
                messagebox.showerror("Error", f"❌ No se pudo guardar el animal:\n{e}")
                return
                
            messagebox.showinfo("Éxito", "✅ Animal registrado por nacimiento correctamente.")
            self.limpiar_formulario()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ No se pudo guardar el animal:\n{e}")

    def guardar_compra(self):
        """Guarda un animal registrado por compra"""
        if not self.validar_datos("comp"):
            return

        try:
            # Recoger datos
            codigo = truncate(self.entry_codigo_comp.get().strip().upper(), "codigo_animal")
            nombre = truncate(self.entry_nombre_comp.get().strip(), "nombre_animal") or None
            fecha_nacimiento = self.entry_fecha_nac_comp.get().strip() or None
            fecha_compra = self.entry_fecha_compra.get().strip()
            sexo = self.combo_sexo_comp.get()
            
            # Función auxiliar para extraer ID de forma segura
            def extraer_id(valor_combo, mapa=None):
                """Obtiene el ID usando mapa nombre->id si existe, sino intenta parsear prefijo."""
                if not valor_combo:
                    return None
                valor_combo = valor_combo.strip()
                if mapa and valor_combo in mapa:
                    return mapa[valor_combo]
                if '-' in valor_combo:
                    try:
                        return int(valor_combo.split('-',1)[0].strip())
                    except Exception:
                        return None
                return None
            
            # Obtener IDs de forma segura
            id_finca = extraer_id(self.combo_finca_comp.get(), getattr(self, '_finca_id_map', None))
            raza_id = extraer_id(self.combo_raza_comp.get(), getattr(self, '_raza_id_map', None))
            # Procedencia o vendedor (ambos usan mismo combo)
            # Importante: Solo aceptar id_vendedor cuando proviene realmente de la tabla vendedor
            id_vendedor = None
            try:
                sel_origen = (self.combo_vendedor.get() or '').strip()
            except Exception:
                sel_origen = ''
            # Si tenemos mapa de vendedores y el valor pertenece a vendedores, usar ese ID
            vend_map = getattr(self, '_vendedor_id_map', {}) or {}
            if sel_origen in vend_map:
                id_vendedor = vend_map[sel_origen]
            else:
                # Si se estuviera mostrando con prefijo "ID - nombre", intentar parsear y validar contra vendedor map
                if '-' in sel_origen:
                    try:
                        posible_id = int(sel_origen.split('-', 1)[0].strip())
                        # Validar que exista en el mapa de vendedores ya cargado
                        vendor_map = getattr(self, '_vendedor_id_map', {})
                        if any(vid == posible_id for vid in vendor_map.values()):
                            id_vendedor = posible_id
                    except Exception:
                        id_vendedor = None
            id_potrero = extraer_id(self.combo_potrero_comp.get(), getattr(self, '_potrero_id_map', None))
            id_lote = extraer_id(self.combo_lote_comp.get(), getattr(self, '_lote_id_map', None))
            # Obtener id_grupo (tabla animal usa id_grupo para almacenar sector)
            id_sector = extraer_id(self.combo_sector_comp.get(), getattr(self, '_sector_id_map', None))
            
            # Convertir peso de compra a kg para almacenar en BD
            peso_comp_input = self.entry_peso_compra.get().strip()
            peso_comp_kg = None
            if peso_comp_input:
                try:
                    peso_comp_kg = units_helper.convert_weight_to_kg(float(peso_comp_input))
                except ValueError:
                    messagebox.showwarning("Atención", "Peso de compra debe ser numérico.")
                    return

            # Validar conjunto de datos antes de insertar
            es_valido, errores = animal_validator.validar_animal_completo({
                'codigo': codigo,
                'peso_compra': peso_comp_kg,
                'fecha_nacimiento': fecha_nacimiento,
                'fecha_compra': fecha_compra,
                'precio_compra': self.entry_precio.get().strip() or None,
                'sexo': sexo,
            })
            if not es_valido:
                messagebox.showerror("Validación", "\n".join(errores[:6]))
                return
            
            # Obtener grupo y condicion_corporal
            grupo_comp = self.combo_grupo_comp.get() if hasattr(self, 'combo_grupo_comp') else None
            condicion_comp = extraer_id(self.combo_condicion_comp.get(), getattr(self, '_condicion_map', None)) if hasattr(self, 'combo_condicion_comp') else None
            
            # Preparar datos para inserción
            datos_insercion = (
                id_finca, codigo, nombre, 'Compra', sexo, raza_id,
                id_potrero, id_lote, id_sector, fecha_nacimiento, fecha_compra,
                None,
                peso_comp_kg,
                id_vendedor,
                float(self.entry_precio.get()) if self.entry_precio.get().strip() else None,
                None, None, None,
                self.combo_salud_comp.get(), self.combo_estado_comp.get(), 0,
                self.entry_color_comp.get().strip() or None,
                self.entry_hierro_comp.get().strip() or None,
                int(self.entry_num_hierros_comp.get().strip()) if self.entry_num_hierros_comp.get().strip() else 0,
                self.entry_composicion_comp.get().strip() or None,
                self.text_comentarios_comp.get("1.0", "end-1c").strip() or None,
                self.foto_path,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                grupo_comp,  # categoria
                grupo_comp,  # grupo_compra
                condicion_comp
            )
            
            # Insertar en BD usando AnimalService (FASE 8.3)
            try:
                # Construir diccionario de datos para el servicio
                datos_insercion_dict = {
                    'id_finca': id_finca,
                    'codigo': codigo,
                    'nombre': nombre,
                    'tipo_ingreso': 'Compra',
                    'sexo': sexo,
                    'raza_id': raza_id,
                    'id_potrero': id_potrero,
                    'lote_id': id_lote,
                    'id_sector': id_sector,
                    'fecha_nacimiento': fecha_nacimiento,
                    'fecha_compra': fecha_compra,
                    'peso_nacimiento': None,
                    'peso_compra': peso_comp_kg,
                    'id_vendedor': id_vendedor,
                    'precio_compra': float(self.entry_precio.get()) if self.entry_precio.get().strip() else None,
                    'id_padre': None,
                    'id_madre': None,
                    'tipo_concepcion': None,
                    'salud': self.combo_salud_comp.get(),
                    'estado': self.combo_estado_comp.get(),
                    'inventariado': 0,
                    'color': self.entry_color_comp.get().strip() or None,
                    'hierro': self.entry_hierro_comp.get().strip() or None,
                    'numero_hierros': int(self.entry_num_hierros_comp.get().strip()) if self.entry_num_hierros_comp.get().strip() else 0,
                    'composicion_racial': self.entry_composicion_comp.get().strip() or None,
                    'comentarios': self.text_comentarios_comp.get("1.0", "end-1c").strip() or None,
                    'foto_path': self.foto_path,
                    'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'categoria': grupo_comp,
                    'grupo_compra': grupo_comp,
                    'condicion_corporal': condicion_comp,
                    'ultimo_peso': peso_comp_kg,
                    'fecha_ultimo_peso': datetime.now().strftime('%Y-%m-%d') if peso_comp_kg else None
                }
                self.animal_service.registrar_animal(datos_insercion_dict)
            except ValueError as ve:
                # Excepciones de validación del servicio (código duplicado, sexo inválido, etc.)
                messagebox.showerror("Validación", str(ve))
                return
            except Exception as e:
                messagebox.showerror("Error", f"❌ No se pudo guardar el animal:\n{e}")
                return
                
            messagebox.showinfo("Éxito", "✅ Animal registrado por compra correctamente.")
            self.limpiar_formulario()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ No se pudo guardar el animal:\n{e}")

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        # Limpiar pestaña nacimiento
        if hasattr(self, 'entry_codigo_nac'):
            self.entry_codigo_nac.delete(0, "end")
            self.entry_nombre_nac.delete(0, "end")
            self.entry_fecha_nac.delete(0, "end")
            self.entry_fecha_nac.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.entry_peso_nacimiento.delete(0, "end")
            self.combo_sexo_nac.set("Macho")
            self.combo_madre_nac.set("")
            self.combo_padre_nac.set("")
            self.combo_concepcion_nac.set("Monta")
            self.entry_color_nac.delete(0, "end")
            self.entry_hierro_nac.delete(0, "end")
            self.entry_num_hierros_nac.delete(0, "end")
            self.entry_composicion_nac.delete(0, "end")
            self.text_comentarios_nac.delete("1.0", "end")
            self.label_foto_nac.configure(text="No hay foto seleccionada")
        
        # Limpiar pestaña compra
        if hasattr(self, 'entry_codigo_comp'):
            self.entry_codigo_comp.delete(0, "end")
            self.entry_nombre_comp.delete(0, "end")
            self.entry_fecha_nac_comp.delete(0, "end")
            self.entry_fecha_compra.delete(0, "end")
            self.entry_fecha_compra.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.combo_sexo_comp.set("Macho")
            self.entry_peso_compra.delete(0, "end")
            self.entry_precio.delete(0, "end")
            self.entry_color_comp.delete(0, "end")
            self.entry_hierro_comp.delete(0, "end")
            self.entry_num_hierros_comp.delete(0, "end")
            self.entry_composicion_comp.delete(0, "end")
            self.text_comentarios_comp.delete("1.0", "end")
            self.label_foto_comp.configure(text="No hay foto seleccionada")
        
        self.foto_path = None
    
    def importar_excel(self):
        """Importa animales desde Excel"""
        from modules.animales.importar_excel import importar_animales_desde_excel
        importar_animales_desde_excel()
        # Recargar datos si es necesario
        self.cargar_datos_combos()

    def importar_excel_compras(self):
        """Importa animales por compra desde Excel (requiere columnas compra)"""
        from tkinter import filedialog
        from modules.utils.importador_excel import importar_animales_desde_excel
        ruta = filedialog.askopenfilename(title="Seleccionar archivo Excel de compras",
                                          filetypes=[("Excel files", "*.xlsx *.xls")])
        if not ruta:
            return
        registros, errores = importar_animales_desde_excel(ruta)
        if errores:
            messagebox.showerror("Errores de Importación", "\n".join(errores))
            return
        # Filtrar sólo tipo_ingreso Compra
        registros_compra = [r for r in registros if r.get('tipo_ingreso') == 'Compra']
        if not registros_compra:
            messagebox.showwarning("Importación", "No se encontraron registros de tipo Compra en el archivo.")
            return
        insertados = 0
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Importar helpers para búsquedas case-insensitive
            from modules.utils.database_helpers import (
                buscar_finca_id,
                buscar_raza_id,
                buscar_potrero_id,
                buscar_lote_id,
                buscar_sector_id,
                buscar_vendedor_id
            )
            
            for r in registros_compra:
                try:
                    finca_nombre = r.get('finca') or ""
                    raza_nombre = r.get('raza') or ""
                    potrero_nombre = r.get('potrero') or ""
                    lote_nombre = r.get('lote') or ""
                    sector_nombre = r.get('sector') or ""
                    vendedor_nombre = r.get('vendedor') or ""

                    # Resolución de IDs usando helpers case-insensitive
                    id_finca = buscar_finca_id(cur, finca_nombre)
                    raza_id = buscar_raza_id(cur, raza_nombre)
                    id_potrero = buscar_potrero_id(cur, potrero_nombre, id_finca or -1)
                    id_lote = buscar_lote_id(cur, lote_nombre)
                    id_sector = buscar_sector_id(cur, sector_nombre)
                    id_vendedor = buscar_vendedor_id(cur, vendedor_nombre)

                    cur.execute("""
                        INSERT INTO animal (
                            id_finca, codigo, nombre, tipo_ingreso, sexo, raza_id, id_potrero, lote_id, id_sector,
                            fecha_nacimiento, fecha_compra, peso_nacimiento, peso_compra, id_vendedor, precio_compra,
                            id_padre, id_madre, tipo_concepcion, salud, estado, inventariado, color, hierro,
                            numero_hierros, composicion_racial, comentarios, foto_path, fecha_registro, grupo_compra
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        id_finca, r.get('codigo'), r.get('nombre'), 'Compra', r.get('sexo'), raza_id,
                        id_potrero, id_lote, id_sector, r.get('fecha_nacimiento'), r.get('fecha_compra'),
                        None, r.get('peso_compra'), id_vendedor, r.get('precio_compra'),
                        None, None, None, r.get('salud') or 'Sano', 'Activo', 0,
                        r.get('color'), r.get('hierro'), r.get('numero_hierros') or 0,
                        None, r.get('observaciones'), None, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        r.get('grupo')
                    ))
                    # Actualizar ultimo_peso para importaciones si se proporcionó peso_compra
                    try:
                        peso_import = r.get('peso_compra')
                        if peso_import not in (None, '', '0'):
                            peso_float = float(peso_import)
                            cur.execute(
                                "UPDATE animal SET ultimo_peso = ?, fecha_ultimo_peso = ? WHERE codigo = ?",
                                (peso_float, datetime.now().strftime('%Y-%m-%d'), r.get('codigo'))
                            )
                    except Exception:
                        pass
                    insertados += 1
                except Exception as e:
                    print(f"Error insertando registro compra {r.get('codigo')}: {e}")
            conn.commit()
        messagebox.showinfo("Importación Compras", f"Registros de compra importados: {insertados}")
        self.cargar_datos_combos()
        
        # Notificar al módulo padre para que refresque el inventario
        self.notificar_cambios_inventario()
    
    def notificar_cambios_inventario(self):
        try:
            # Recorrer jerarquía para encontrar InventarioGeneralFrame o frame_inventario
            from modules.animales.inventario_v2 import InventarioGeneralFrame
            parent = self.winfo_toplevel()
            objetivos = []
            def _collect(fr):
                try:
                    for ch in fr.winfo_children():
                        if isinstance(ch, InventarioGeneralFrame):
                            objetivos.append(ch)
                        _collect(ch)
                except Exception:
                    pass
            _collect(parent)
            # Fallback: atributo frame_inventario con métodos de refresco antiguos
            frame_inv = getattr(parent, 'frame_inventario', None)
            if frame_inv is not None:
                objetivos.append(frame_inv)
            usados = 0
            for obj in objetivos:
                if hasattr(obj, 'refrescar_inventario_externo'):
                    obj.refrescar_inventario_externo()
                    usados += 1
                elif hasattr(obj, 'refrescar_inventario'):
                    obj.refrescar_inventario()
                    usados += 1
            if self.logger:
                self.logger.info(f"Inventario refrescado tras registro (targets={usados})")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"No se pudo notificar cambios al inventario: {e}")