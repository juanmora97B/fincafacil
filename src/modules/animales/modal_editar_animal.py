"""
Modal Editar Animal - Formulario completo con preview de foto
Versión mejorada con filtrado dinámico y tipo de ingreso
FASE 8.3: Migrado para usar AnimalService en lugar de acceso directo a BD
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkcalendar import Calendar
from PIL import Image
from pathlib import Path
import shutil
from datetime import datetime
from typing import Any
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from infraestructura.animales.animal_service import AnimalService
from modules.utils.date_picker import attach_date_picker
# FASE 8.3.2: No se importa get_db_connection, solo AnimalService


class ModalEditarAnimal(ctk.CTkToplevel):
    """Modal profesional para editar animal con secciones organizadas"""
    
    def __init__(self, master, animal_data, callback=None):
        super().__init__(master)
        
        self.animal = animal_data
        self.callback = callback
        self.new_photo_path = None
        self.animal_service = AnimalService()  # FASE 8.3: inyectar servicio
        
        # Variables para campos condicionales
        self.campos_compra = []
        self.campos_nacimiento = []
        
        # Configuración ventana
        self.title(f"Editar: {animal_data.get('codigo', 'N/A')}")
        self.geometry("1000x700")
        self.resizable(True, True)
        try:
            self.overrideredirect(False)
            self.attributes('-toolwindow', False)
        except Exception:
            pass
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")
        
        self._build_ui()
        self._load_data()
    
    def _build_ui(self):
        """Construir interfaz con secciones organizadas"""
        # Header
        header = ctk.CTkFrame(self, corner_radius=12, fg_color="#2d6a4f")
        header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            header,
            text="✏ Editar Animal",
            font=("Segoe UI", 22, "bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Contenedor con scroll interno
        main_container = ctk.CTkScrollableFrame(self, corner_radius=12, fg_color=("gray95", "gray20"))
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # ========== E) IMAGEN DEL ANIMAL ==========
        self._build_seccion_imagen(main_container)
        
        # ========== A) DATOS GENERALES ==========
        self._build_seccion_datos_generales(main_container)
        
        # ========== B) DATOS PRODUCTIVOS ==========
        self._build_seccion_datos_productivos(main_container)
        
        # ========== C) UBICACIÓN ==========
        self._build_seccion_ubicacion(main_container)
        
        # ========== D) REPRODUCCIÓN ==========
        self._build_seccion_reproduccion(main_container)
        
        # Botones
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.pack(pady=15)
        
        ctk.CTkButton(
            btn_container,
            text="✓ Guardar Cambios",
            command=self._guardar,
            width=180,
            height=45,
            corner_radius=10,
            font=("Segoe UI", 14, "bold"),
            fg_color="#2d6a4f",
            hover_color="#1f4d38"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_container,
            text="✗ Cancelar",
            command=self.destroy,
            width=140,
            height=45,
            corner_radius=10,
            font=("Segoe UI", 14, "bold"),
            fg_color="gray40",
            hover_color="gray50"
        ).pack(side="left", padx=10)
    
    # ========== MÉTODOS PARA CONSTRUIR SECCIONES ==========
    
    def _build_seccion_imagen(self, parent):
        """E) Imagen del animal"""
        seccion = self._crear_seccion(parent, "📷 Imagen del Animal")
        
        foto_container = ctk.CTkFrame(seccion, corner_radius=10)
        foto_container.pack(pady=15, padx=20)
        
        self.foto_label = ctk.CTkLabel(
            foto_container,
            text="📷\nSin foto",
            width=220,
            height=220,
            corner_radius=10,
            font=("Segoe UI", 20),
            text_color="gray50"
        )
        self.foto_label.pack(padx=10, pady=10)
        
        ctk.CTkButton(
            foto_container,
            text="📁 Cambiar Foto",
            command=self._cambiar_foto,
            width=180,
            height=36,
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        ).pack(pady=8)
    
    def _build_seccion_datos_generales(self, parent):
        """A) Datos generales"""
        seccion = self._crear_seccion(parent, "📋 A) Datos Generales")
        
        grid = ctk.CTkFrame(seccion, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=10)
        grid.grid_columnconfigure((0, 1), weight=1)
        
        # Fila 1: Código y Nombre
        self.entry_codigo = self._add_input_grid(grid, "Código *", 0, 0)
        self.entry_nombre = self._add_input_grid(grid, "Nombre", 0, 1)
        
        # Fila 2: Sexo y Origen del animal
        self.cmb_sexo = self._add_combo_grid(grid, "Sexo *", ["Macho", "Hembra"], 1, 0)
        self.cmb_tipo_ingreso = self._add_combo_grid(grid, "Origen del animal *", 
                       ["COMPRA", "NACIMIENTO"], 1, 1, 
                       command=self._on_tipo_ingreso_change)
        
        # Fila 3: Fecha de nacimiento / fecha de compra (condicional)
        self.lbl_fecha_nac = ctk.CTkLabel(grid, text="Fecha Nacimiento", 
                  font=("Segoe UI", 11, "bold"), anchor="w")
        self.lbl_fecha_nac.grid(row=2, column=0, padx=10, pady=(10, 2), sticky="w")
        # Contenedor para fecha nacimiento con calendario estilo registro
        self.fecha_nac_container = ctk.CTkFrame(grid, fg_color="transparent")
        self.fecha_nac_container.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.fecha_nac_container.grid_columnconfigure(0, weight=1)
        self.entry_fecha_nac = ctk.CTkEntry(self.fecha_nac_container, height=36, corner_radius=8, font=("Segoe UI", 11))
        self.entry_fecha_nac.pack(side="left", fill="x", expand=True)
        attach_date_picker(self.fecha_nac_container, self.entry_fecha_nac)
        
        # Campos de COMPRA (ocultos inicialmente)
        self.lbl_fecha_compra = ctk.CTkLabel(grid, text="Fecha Compra", 
                     font=("Segoe UI", 11, "bold"), anchor="w")
        self.fecha_comp_container = ctk.CTkFrame(grid, fg_color="transparent")
        self.fecha_comp_container.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")
        self.fecha_comp_container.grid_columnconfigure(0, weight=1)
        self.entry_fecha_compra = ctk.CTkEntry(self.fecha_comp_container, height=36, corner_radius=8, font=("Segoe UI", 11))
        self.entry_fecha_compra.pack(side="left", fill="x", expand=True)
        attach_date_picker(self.fecha_comp_container, self.entry_fecha_compra)
        self.campos_compra.extend([self.lbl_fecha_compra, self.entry_fecha_compra])
        
        self.lbl_precio_compra = ctk.CTkLabel(grid, text="Precio Compra *", 
                                              font=("Segoe UI", 11, "bold"), anchor="w")
        self.entry_precio_compra = ctk.CTkEntry(grid, height=36, corner_radius=8, font=("Segoe UI", 11))
        self.campos_compra.extend([self.lbl_precio_compra, self.entry_precio_compra])

        # Procedencia (por finca) y Vendedor (COMPRA)
        self.lbl_procedencia = ctk.CTkLabel(grid, text="Procedencia", 
                            font=("Segoe UI", 11, "bold"), anchor="w")
        self.cmb_procedencia = ctk.CTkComboBox(grid, values=[""], height=36, corner_radius=8, font=("Segoe UI", 11))
        self.campos_compra.extend([self.lbl_procedencia, self.cmb_procedencia])

        self.lbl_vendedor = ctk.CTkLabel(grid, text="Vendedor", 
                          font=("Segoe UI", 11, "bold"), anchor="w")
        self.entry_vendedor = ctk.CTkEntry(grid, height=36, corner_radius=8, font=("Segoe UI", 11))
        self.campos_compra.extend([self.lbl_vendedor, self.entry_vendedor])
    
    def _build_seccion_datos_productivos(self, parent):
        """B) Datos productivos"""
        seccion = self._crear_seccion(parent, "🐄 B) Datos Productivos")
        
        grid = ctk.CTkFrame(seccion, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=10)
        grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Fila 1
        self.cmb_raza = self._add_combo_grid(grid, "Raza", 
                             ["Cargando..."], 0, 0)
        self.entry_peso_nacimiento = self._add_input_grid(grid, "Peso Nacimiento (kg)", 0, 1)
        
        # Peso compra (solo si tipo = COMPRA)
        self.lbl_peso_compra = ctk.CTkLabel(grid, text="Peso Compra (kg)", 
                                           font=("Segoe UI", 11, "bold"), anchor="w")
        self.entry_peso_compra = ctk.CTkEntry(grid, height=36, corner_radius=8, font=("Segoe UI", 11))
        self.campos_compra.extend([self.lbl_peso_compra, self.entry_peso_compra])
        
        # Fila 2
        self.cmb_condicion = self._add_combo_grid(grid, "Condición Corporal", 
                              ["Cargando..."], 1, 0)
        self.cmb_estado = self._add_combo_grid(grid, "Estado", 
                               ["Cargando..."], 1, 1)
        self.cmb_salud = self._add_combo_grid(grid, "Salud", 
                              ["Cargando..."], 1, 2)
        
        # Fila 3
        self.cmb_calidad = self._add_combo_grid(grid, "Calidad", 
                            ["Cargando..."], 2, 0)
        self.entry_peso_actual = self._add_input_grid(grid, "Peso Actual (kg)", 2, 1)

        # Campos adicionales del animal
        self.entry_color = self._add_input_grid(grid, "Color", 3, 0)
        self.entry_hierro = self._add_input_grid(grid, "Hierro", 3, 1)
        self.entry_inventariado = self._add_input_grid(grid, "Inventariado (Sí/No)", 4, 0)
        self.entry_comentarios = self._add_input_grid(grid, "Comentarios", 4, 1)
    
    def _build_seccion_ubicacion(self, parent):
        """C) Ubicación con filtrado dinámico"""
        seccion = self._crear_seccion(parent, "📍 C) Ubicación")
        
        grid = ctk.CTkFrame(seccion, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=10)
        grid.grid_columnconfigure((0, 1), weight=1)
        
        # Finca con listener para filtrado dinámico
        self.cmb_finca = self._add_combo_grid(grid, "Finca *", [], 0, 0, 
                                              command=self._on_finca_change)
        
        # Campos dependientes (se llenan al seleccionar finca)
        self.cmb_potrero = self._add_combo_grid(grid, "Potrero", ["Seleccione finca primero"], 0, 1)
        self.cmb_sector = self._add_combo_grid(grid, "Sector", ["Seleccione finca primero"], 1, 0)
        self.cmb_lote = self._add_combo_grid(grid, "Lote", ["Seleccione finca primero"], 1, 1)
        
        self.cmb_grupo = self._add_combo_grid(grid, "Grupo", 
                                              ["Ninguno", "Grupo 1", "Grupo 2", "Grupo 3"], 2, 0)
    
    def _build_seccion_reproduccion(self, parent):
        """D) Reproducción (solo visible si tipo_ingreso = NACIMIENTO)"""
        seccion = self._crear_seccion(parent, "🤰 D) Reproducción (Nacimiento)")
        
        grid = ctk.CTkFrame(seccion, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=10)
        grid.grid_columnconfigure((0, 1), weight=1)
        
        # Campos de reproducción
        self.cmb_madre = self._add_combo_grid(grid, "Madre *", ["Cargando..."], 0, 0)
        self.cmb_padre = self._add_combo_grid(grid, "Padre", ["Cargando..."], 0, 1)
        self.cmb_tipo_reproduccion = self._add_combo_grid(
            grid,
            "Tipo de reproducción",
            ["Natural", "Inseminación"],
            1,
            0
        )
        
        # Inseminación: usar solo esta casilla para simplificar
        self.chk_inseminacion = ctk.CTkCheckBox(
            grid,
            text="Inseminación Artificial (padre no requerido)",
            font=("Segoe UI", 11),
            command=self._on_inseminacion_change
        )
        self.chk_inseminacion.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Guardar referencias para ocultar/mostrar
        self.seccion_reproduccion = seccion
        self.campos_nacimiento = [seccion]
    
    # ========== HELPERS PARA UI ==========
    
    def _crear_seccion(self, parent, titulo):
        """Crea un frame de sección con título"""
        frame = ctk.CTkFrame(parent, corner_radius=10, fg_color=("white", "gray25"))
        frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(
            frame,
            text=titulo,
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        ).pack(padx=15, pady=(10, 5), anchor="w")
        
        return frame
    
    def _add_input_grid(self, parent, label, row, col):
        """Agregar input en grid"""
        ctk.CTkLabel(
            parent,
            text=label,
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        ).grid(row=row*2, column=col, padx=10, pady=(10, 2), sticky="w")
        
        entry = ctk.CTkEntry(parent, height=36, corner_radius=8, font=("Segoe UI", 11))
        entry.grid(row=row*2+1, column=col, padx=10, pady=(0, 10), sticky="ew")
        return entry
    
    def _add_combo_grid(self, parent, label, values, row, col, command=None):
        """Agregar combobox en grid"""
        ctk.CTkLabel(
            parent,
            text=label,
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        ).grid(row=row*2, column=col, padx=10, pady=(10, 2), sticky="w")
        
        combo = ctk.CTkComboBox(
            parent,
            values=values,
            height=36,
            corner_radius=8,
            font=("Segoe UI", 11),
            command=command
        )
        if values:
            combo.set(values[0])
        combo.grid(row=row*2+1, column=col, padx=10, pady=(0, 10), sticky="ew")
        return combo
    
    def _add_input(self, parent, label):
        """Agregar campo de entrada"""
        ctk.CTkLabel(
            parent,
            text=label,
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 2))
        
        entry = ctk.CTkEntry(
            parent,
            height=36,
            corner_radius=8,
            font=("Segoe UI", 12)
        )
        entry.pack(fill="x", pady=(0, 5))
        return entry
    
    def _add_combo(self, parent, label, values):
        """Agregar combobox"""
        ctk.CTkLabel(
            parent,
            text=label,
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 2))
        
        combo = ctk.CTkComboBox(
            parent,
            values=values,
            height=36,
            corner_radius=8,
            font=("Segoe UI", 11)
        )
        if values:
            combo.set(values[0])
        combo.pack(fill="x", pady=(0, 5))
        return combo
    
    # ========== EVENTOS Y FILTRADO DINÁMICO ==========
    
    def _on_tipo_ingreso_change(self, value=None):
        """Cambiar campos visibles según tipo de ingreso"""
        tipo = self.cmb_tipo_ingreso.get()
        
        if tipo == "COMPRA":
            # Mostrar campos de compra
            self.lbl_fecha_compra.grid(row=2, column=1, padx=10, pady=(10, 2), sticky="w")
            self.fecha_comp_container.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")
            self.lbl_precio_compra.grid(row=4, column=0, padx=10, pady=(10, 2), sticky="w")
            self.entry_precio_compra.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")
            self.lbl_peso_compra.grid(row=0, column=2, padx=10, pady=(10, 2), sticky="w")
            self.entry_peso_compra.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")
            # Procedencia y Vendedor
            self.lbl_procedencia.grid(row=4, column=1, padx=10, pady=(10,2), sticky="w")
            self.cmb_procedencia.grid(row=5, column=1, padx=10, pady=(0,10), sticky="ew")
            self.lbl_vendedor.grid(row=6, column=0, padx=10, pady=(10,2), sticky="w")
            self.entry_vendedor.grid(row=7, column=0, padx=10, pady=(0,10), sticky="ew")
            
            # Ocultar sección reproducción
            self.seccion_reproduccion.pack_forget()
            
            # Cambiar etiqueta de fecha
            self.lbl_fecha_nac.configure(text="Fecha Nacimiento")
            
        else:  # NACIMIENTO
            # Ocultar campos de compra
            self.lbl_fecha_compra.grid_forget()
            self.fecha_comp_container.grid_forget()
            self.lbl_precio_compra.grid_forget()
            self.entry_precio_compra.grid_forget()
            self.lbl_peso_compra.grid_forget()
            self.entry_peso_compra.grid_forget()
            self.lbl_procedencia.grid_forget()
            self.cmb_procedencia.grid_forget()
            self.lbl_vendedor.grid_forget()
            self.entry_vendedor.grid_forget()
            
            # Mostrar sección reproducción
            # Importante: empacar en su mismo padre (main_container) sin 'before'
            # para evitar error de Tk por padres diferentes
            self.seccion_reproduccion.pack(fill="x", padx=10, pady=8)
            
            # Cargar opciones de padres/madres
            self._cargar_opciones_reproduccion()
    
    def _on_finca_change(self, value=None):
        """Filtrar potreros, sectores y lotes por finca seleccionada (FASE 8.3.2: usa AnimalService)"""
        finca_val = self.cmb_finca.get()
        if not finca_val or '-' not in finca_val:
            return
        
        try:
            finca_id = int(finca_val.split(' - ')[0])
            
            # Potreros de la finca
            potreros_data = self.animal_service.cargar_potreros_por_finca(finca_id)
            potrero_values = ["Ninguno"] + [f"{p['id']} - {p['nombre']}" for p in potreros_data]
            self.cmb_potrero.configure(values=potrero_values)
            self.cmb_potrero.set("Ninguno")
            
            # Sectores de la finca
            sectores_data = self.animal_service.cargar_sectores_por_finca(finca_id)
            sector_values = ["Ninguno"] + [f"{s['id']} - {s['nombre']}" for s in sectores_data]
            self.cmb_sector.configure(values=sector_values)
            self.cmb_sector.set("Ninguno")
            
            # Lotes de la finca
            lotes_data = self.animal_service.cargar_lotes_por_finca(finca_id)
            lote_values = ["Ninguno"] + [f"{l['id']} - {l['nombre']}" for l in lotes_data]
            self.cmb_lote.configure(values=lote_values)
            self.cmb_lote.set("Ninguno")

            # Procedencias desde servicio
            try:
                procedencias_data = self.animal_service.cargar_procedencias(finca_id)
                procedencias = [p.get('descripcion', '') for p in procedencias_data if p.get('descripcion')]
                if not procedencias:
                    procedencias = [""]
                self.cmb_procedencia.configure(values=procedencias)
                self.cmb_procedencia.set(procedencias[0])
            except Exception:
                pass
                
        except Exception as e:
            print(f"Error filtrando por finca: {e}")
    
    def _on_inseminacion_change(self):
        """Habilitar/deshabilitar campo padre según inseminación"""
        if self.chk_inseminacion.get():
            self.cmb_padre.configure(state="disabled")
            self.cmb_padre.set("No aplica (Inseminación)")
        else:
            self.cmb_padre.configure(state="normal")
            self._cargar_opciones_reproduccion()
    
    def _cargar_opciones_reproduccion(self):
        """Cargar animales disponibles como padres/madres (FASE 8.3.2: usa AnimalService)"""
        try:
            finca_val = self.cmb_finca.get()
            if not finca_val or '-' not in finca_val:
                return
            
            finca_id = int(finca_val.split(' - ')[0])
            
            # Madres (hembras de la finca)
            madres_data = self.animal_service.cargar_madres_por_finca(finca_id)
            madre_values = [f"{m['id']} - {m['codigo']} ({m.get('nombre') or 'Sin nombre'})" for m in madres_data]
            if madre_values:
                self.cmb_madre.configure(values=madre_values)
                self.cmb_madre.set(madre_values[0])
            else:
                self.cmb_madre.configure(values=["No hay hembras en esta finca"])
                self.cmb_madre.set("No hay hembras en esta finca")
            
            # Padres (machos de la finca) si aplica
            if not self.chk_inseminacion.get():
                padres_data = self.animal_service.cargar_padres_por_finca(finca_id)
                padre_values = ["Ninguno"] + [f"{p['id']} - {p['codigo']} ({p.get('nombre') or 'Sin nombre'})" for p in padres_data]
                self.cmb_padre.configure(values=padre_values)
                self.cmb_padre.set("Ninguno")
                
        except Exception as e:
            print(f"Error cargando opciones reproducción: {e}")

    def _cargar_catalogos(self):
        """Carga catálogos desde servicio (FASE 8.3.2: usa AnimalService)
        - raza: desde cargar_razas()
        - condicion_corporal: desde cargar_condiciones_corporales()
        - calidad: desde cargar_calidades()
        - salud/estado: desde cargar_estados_salud() y cargar_estados()
        """
        try:
            # Raza
            try:
                razas_data = self.animal_service.cargar_razas()
                vals = [r['nombre'] for r in razas_data if r.get('nombre')]
                if not vals:
                    vals = ["-"]
                self.cmb_raza.configure(values=vals)
                self.cmb_raza.set(vals[0])
            except Exception:
                pass

            # Condición corporal
            try:
                condiciones_data = self.animal_service.cargar_condiciones_corporales()
                vals = [c['descripcion'] for c in condiciones_data if c.get('descripcion')]
                if not vals:
                    vals = ["-"]
                self.cmb_condicion.configure(values=vals)
                self.cmb_condicion.set(vals[0])
            except Exception:
                pass

            # Calidad
            try:
                calidades_data = self.animal_service.cargar_calidades()
                vals = [cal['descripcion'] for cal in calidades_data if cal.get('descripcion')]
                if not vals:
                    vals = ["-"]
                self.cmb_calidad.configure(values=vals)
                self.cmb_calidad.set(vals[0])
            except Exception:
                pass

            # Salud
            try:
                vals = self.animal_service.cargar_estados_salud()
                if not vals:
                    vals = ["-"]
                self.cmb_salud.configure(values=vals)
                self.cmb_salud.set(vals[0])
            except Exception:
                pass

            # Estado
            try:
                vals = self.animal_service.cargar_estados()
                if not vals:
                    vals = ["-"]
                self.cmb_estado.configure(values=vals)
                self.cmb_estado.set(vals[0])
            except Exception:
                pass
        except Exception as e:
            print(f"Error cargando catálogos: {e}")
    
    # ========== CARGA DE DATOS INICIALES ==========
    
    def _load_data(self):
        """Cargar datos actuales del animal"""
        codigo = self.animal.get('codigo')
        self.entry_codigo.insert(0, '' if codigo is None else str(codigo))

        nombre = self.animal.get('nombre')
        self.entry_nombre.insert(0, '' if nombre is None else str(nombre))
        
        # Sexo
        sexo = self.animal.get('sexo', '')
        if sexo in ["Macho", "Hembra"]:
            self.cmb_sexo.set(sexo)
        
        # Tipo de ingreso (intentar detectar)
        tipo_ingreso = self.animal.get('tipo_ingreso', '')
        if not tipo_ingreso:
            # Si no existe, inferir por datos existentes
            if self.animal.get('precio_compra') or self.animal.get('fecha_compra'):
                tipo_ingreso = "COMPRA"
            else:
                tipo_ingreso = "NACIMIENTO"
        
        self.cmb_tipo_ingreso.set(tipo_ingreso)
        
        # Fechas
        fecha_nac = self.animal.get('fecha_nacimiento')
        if fecha_nac:
            try:
                # If DateEntry supports set_date, use it; else fallback
                if hasattr(self.entry_fecha_nac, 'set_date'):
                    getattr(self.entry_fecha_nac, 'set_date')(datetime.strptime(str(fecha_nac), "%Y-%m-%d").date())
                else:
                    self.entry_fecha_nac.delete(0, 'end')
                    self.entry_fecha_nac.insert(0, str(fecha_nac))
            except Exception:
                pass
        
        fecha_compra = self.animal.get('fecha_compra')
        if fecha_compra:
            try:
                if hasattr(self.entry_fecha_compra, 'set_date'):
                    getattr(self.entry_fecha_compra, 'set_date')(datetime.strptime(str(fecha_compra), "%Y-%m-%d").date())
                else:
                    self.entry_fecha_compra.delete(0, 'end')
                    self.entry_fecha_compra.insert(0, str(fecha_compra))
            except Exception:
                pass
        
        # Precio compra
        precio_compra = self.animal.get('precio_compra')
        if precio_compra:
            self.entry_precio_compra.insert(0, str(precio_compra))
        procedencia = self.animal.get('procedencia')
        if procedencia:
            try:
                self.cmb_procedencia.set(str(procedencia))
            except Exception:
                pass
        vendedor = self.animal.get('vendedor')
        if vendedor:
            self.entry_vendedor.insert(0, str(vendedor))
        
        # Datos productivos
        raza = self.animal.get('raza', '')
        if raza:
            self.cmb_raza.set(raza)
        
        peso_nac = self.animal.get('peso_nacimiento')
        if peso_nac:
            self.entry_peso_nacimiento.insert(0, str(peso_nac))
        
        peso_compra = self.animal.get('peso_compra')
        if peso_compra:
            self.entry_peso_compra.insert(0, str(peso_compra))
        
        condicion = self.animal.get('condicion_corporal', '')
        if condicion:
            self.cmb_condicion.set(str(condicion))
        
        estado = self.animal.get('estado', '')
        if estado:
            self.cmb_estado.set(estado)
        
        salud = self.animal.get('salud', '')
        if salud:
            self.cmb_salud.set(salud)
        
        calidad = self.animal.get('calidad', '')
        if calidad:
            self.cmb_calidad.set(calidad)
        
        peso_actual = self.animal.get('ultimo_peso')
        if peso_actual:
            self.entry_peso_actual.insert(0, str(peso_actual))

        # Adicionales
        color = self.animal.get('color')
        if color:
            self.entry_color.insert(0, str(color))
        hierro = self.animal.get('hierro')
        if hierro:
            self.entry_hierro.insert(0, str(hierro))
        inventariado = self.animal.get('inventariado')
        if inventariado is not None:
            self.entry_inventariado.insert(0, str(inventariado))
        comentarios = self.animal.get('comentarios')
        if comentarios:
            self.entry_comentarios.insert(0, str(comentarios))
        
        # Cargar fincas y ubicación
        self._load_fincas()
        
        # Reproducción
        madre_id = self.animal.get('madre_id')
        padre_id = self.animal.get('padre_id')
        # Tipo de reproducción / inseminación
        tipo_repro_db = self.animal.get('tipo_reproduccion')
        inseminacion = self.animal.get('inseminacion_artificial', 0)
        
        if inseminacion:
            self.chk_inseminacion.select()
            if hasattr(self, 'cmb_tipo_reproduccion'):
                self.cmb_tipo_reproduccion.set('Inseminación')
        else:
            if hasattr(self, 'cmb_tipo_reproduccion'):
                if tipo_repro_db in ('Natural', 'Inseminación'):
                    self.cmb_tipo_reproduccion.set(tipo_repro_db)
                else:
                    self.cmb_tipo_reproduccion.set('Natural')
        
        # Aplicar visibilidad según tipo
        self._on_tipo_ingreso_change()
        
        # Cargar foto
        foto_path = self.animal.get('foto_path')
        if foto_path and Path(foto_path).exists():
            self._show_photo(foto_path)
    
    def _load_fincas(self):
        """Cargar fincas y aplicar filtrado dinámico (FASE 8.3.2: usa AnimalService)"""
        try:
            # Cargar fincas desde servicio
            fincas_data = self.animal_service.cargar_fincas()
            finca_values = [f"{f['id']} - {f['nombre']}" for f in fincas_data]
            self.cmb_finca.configure(values=finca_values)
            
            # Seleccionar finca actual y activar filtrado
            finca_id_actual = self.animal.get('id_finca') or self.animal.get('finca_id')
            finca_actual = self.animal.get('finca') or self.animal.get('nombre_finca')
            
            if finca_id_actual:
                for val in finca_values:
                    if val.startswith(f"{finca_id_actual} -"):
                        self.cmb_finca.set(val)
                        # Activar filtrado dinámico
                        self._on_finca_change()
                        break
            elif finca_actual:
                for val in finca_values:
                    if finca_actual in val:
                        self.cmb_finca.set(val)
                        self._on_finca_change()
                        break

            # Después del filtrado, seleccionar ubicación actual
            self._seleccionar_ubicacion_actual()

            # Cargar catálogos globales
            self._cargar_catalogos()
                
        except Exception as e:
            print(f"Error cargando fincas: {e}")
    
    def _seleccionar_ubicacion_actual(self):
        """Seleccionar la ubicación actual del animal en los combos"""
        try:
            # Potrero
            potrero_id = self.animal.get('id_potrero') or self.animal.get('potrero_id')
            if potrero_id and self.cmb_potrero.cget("values"):
                for val in self.cmb_potrero.cget("values"):
                    if val.startswith(f"{potrero_id} -"):
                        self.cmb_potrero.set(val)
                        break
            
            # Sector
            sector_id = self.animal.get('id_sector') or self.animal.get('sector_id')
            if sector_id and self.cmb_sector.cget("values"):
                for val in self.cmb_sector.cget("values"):
                    if val.startswith(f"{sector_id} -"):
                        self.cmb_sector.set(val)
                        break
            
            # Lote
            lote_id = self.animal.get('lote_id')
            if lote_id and self.cmb_lote.cget("values"):
                for val in self.cmb_lote.cget("values"):
                    if val.startswith(f"{lote_id} -"):
                        self.cmb_lote.set(val)
                        break
            
            # Grupo
            grupo = self.animal.get('grupo', '')
            if grupo:
                self.cmb_grupo.set(grupo)
                
        except Exception as e:
            print(f"Error seleccionando ubicación: {e}")
    
    def _cambiar_foto(self):
        """Cambiar foto del animal"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar Foto",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos", "*.*")]
        )
        
        if filepath:
            self.new_photo_path = filepath
            self._show_photo(filepath)
    
    def _show_photo(self, path):
        """Mostrar preview de foto"""
        try:
            img = Image.open(path)
            img.thumbnail((230, 230), Image.Resampling.LANCZOS)
            
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(230, 230))
            
            self.foto_label.configure(image=photo, text="")
            # Guardar referencia en un atributo ignorado por el type checker
            setattr(self.foto_label, "_photo_ref", photo)
        except Exception as e:
            print(f"Error mostrando foto: {e}")
    
    def _guardar(self):
        """Guardar cambios con validaciones y columnas dinámicas"""
        try:
            # ================== VALIDACIONES BÁSICAS ==================
            codigo = self.entry_codigo.get().strip()
            if not codigo:
                messagebox.showerror("Error", "El código es obligatorio")
                return
            sexo = self.cmb_sexo.get()
            if sexo not in ["Macho", "Hembra"]:
                messagebox.showerror("Error", "Seleccione un sexo válido")
                return
            tipo_ingreso = self.cmb_tipo_ingreso.get()
            if tipo_ingreso not in ["COMPRA", "NACIMIENTO"]:
                messagebox.showerror("Error", "Seleccione un tipo de ingreso válido")
                return
            finca_val = self.cmb_finca.get()
            if not finca_val or '-' not in finca_val:
                messagebox.showerror("Error", "Seleccione una finca")
                return
            finca_id = int(finca_val.split(' - ')[0])

            # ================== IDs DEPENDIENTES ==================
            def parse_id(val):
                try:
                    return int(val.split(' - ')[0]) if val and '-' in val else None
                except Exception:
                    return None
            potrero_id = parse_id(self.cmb_potrero.get())
            lote_id = parse_id(self.cmb_lote.get())
            sector_id = parse_id(self.cmb_sector.get())
            grupo = (self.cmb_grupo.get() or "").strip() or None

            # ================== CAMPOS FECHA/PESOS ==================
            fecha_nac = self.entry_fecha_nac.get().strip() or None
            fecha_compra = None
            precio_compra = None
            peso_compra = None
            if tipo_ingreso == "COMPRA":
                fecha_compra = self.entry_fecha_compra.get().strip()
                if not fecha_compra:
                    messagebox.showerror("Error", "La fecha de compra es obligatoria para tipo COMPRA")
                    return
                precio_txt = self.entry_precio_compra.get().strip()
                if not precio_txt:
                    messagebox.showerror("Error", "El precio de compra es obligatorio para tipo COMPRA")
                    return
                try:
                    precio_compra = float(precio_txt)
                except ValueError:
                    messagebox.showerror("Error", "El precio de compra debe ser un número válido")
                    return
                peso_compra_txt = self.entry_peso_compra.get().strip()
                if peso_compra_txt:
                    try:
                        peso_compra = float(peso_compra_txt)
                    except ValueError:
                        messagebox.showerror("Error", "El peso de compra debe ser numérico")
                        return

            # ================== REPRODUCCIÓN ==================
            inseminacion = 1 if hasattr(self, 'chk_inseminacion') and self.chk_inseminacion.get() else 0
            madre_id = None
            padre_id = None
            if tipo_ingreso == "NACIMIENTO":
                madre_val = self.cmb_madre.get()
                if not madre_val or madre_val.startswith("No hay hembras"):
                    messagebox.showerror("Error", "Debe seleccionar una madre para tipo NACIMIENTO")
                    return
                madre_id = parse_id(madre_val)
                if not inseminacion:
                    padre_val = self.cmb_padre.get()
                    if not padre_val or padre_val == "Ninguno":
                        messagebox.showerror("Error", "Debe seleccionar un padre o marcar inseminación artificial")
                        return
                    padre_id = parse_id(padre_val)

            # ================== DATOS PRODUCTIVOS ==================
            raza = (self.cmb_raza.get() or "").strip() or None
            peso_nac = None
            if hasattr(self, 'entry_peso_nacimiento'):
                pn = self.entry_peso_nacimiento.get().strip()
                if pn:
                    try:
                        peso_nac = float(pn)
                    except ValueError:
                        messagebox.showerror("Error", "El peso de nacimiento debe ser numérico")
                        return
            condicion = (self.cmb_condicion.get() or "").strip() or None
            estado = (self.cmb_estado.get() or "").strip() or None
            salud = (self.cmb_salud.get() or "").strip() or None
            calidad = (self.cmb_calidad.get() or "").strip() or None
            peso_actual = None
            if hasattr(self, 'entry_peso_actual'):
                pa = self.entry_peso_actual.get().strip()
                if pa:
                    try:
                        peso_actual = float(pa)
                    except ValueError:
                        messagebox.showerror("Error", "El peso actual debe ser numérico")
                        return

            # ================== FOTO ==================
            foto_final_path = self.animal.get('foto_path')
            if self.new_photo_path:
                try:
                    fotos_dir = Path("data/fotos_animales"); fotos_dir.mkdir(parents=True, exist_ok=True)
                    ext = Path(self.new_photo_path).suffix
                    nuevo_nombre = f"{codigo}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                    destino = fotos_dir / nuevo_nombre
                    shutil.copy2(self.new_photo_path, destino)
                    foto_final_path = str(destino)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar la foto:\n{e}")
                    return

            # ================== PERSISTENCIA (FASE 8.3.2: usa AnimalService) ==================
            # Construir diccionario de cambios
            val_proc = None
            try:
                val_proc = (self.cmb_procedencia.get().strip() or None)
            except Exception:
                val_proc = (getattr(self, 'entry_procedencia', ctk.CTkEntry(self)).get().strip() or None)
            
            repro_val = None
            if tipo_ingreso == 'NACIMIENTO':
                if hasattr(self, 'cmb_tipo_reproduccion'):
                    repro_val = self.cmb_tipo_reproduccion.get()
            
            cambios = {
                'codigo': codigo,
                'nombre': (self.entry_nombre.get().strip() or None),
                'sexo': sexo,
                'foto_path': foto_final_path,
                'fecha_nacimiento': fecha_nac,
                'finca_id': finca_id,
                'id_finca': finca_id,
                'potrero_id': potrero_id,
                'id_potrero': potrero_id,
                'lote_id': lote_id,
                'sector_id': sector_id,
                'id_sector': sector_id,
                'ultimo_peso': peso_actual,
                'tipo_ingreso': tipo_ingreso,
                'fecha_compra': fecha_compra,
                'precio_compra': precio_compra,
                'peso_compra': peso_compra,
                'procedencia': val_proc,
                'vendedor': (self.entry_vendedor.get().strip() or None),
                'raza': raza,
                'peso_nacimiento': peso_nac,
                'condicion_corporal': condicion,
                'estado': estado,
                'salud': salud,
                'calidad': calidad,
                'grupo': grupo,
                'categoria': grupo,
                'grupo_compra': grupo,
                'color': (self.entry_color.get().strip() or None),
                'hierro': (self.entry_hierro.get().strip() or None),
                'inventariado': (self.entry_inventariado.get().strip() or None),
                'comentarios': (self.entry_comentarios.get().strip() or None),
                'tipo_reproduccion': repro_val,
                'madre_id': madre_id if tipo_ingreso == 'NACIMIENTO' else None,
                'padre_id': padre_id if (tipo_ingreso == 'NACIMIENTO' and not inseminacion) else None,
                'inseminacion_artificial': inseminacion if tipo_ingreso == 'NACIMIENTO' else 0,
            }
            
            self.animal_service.actualizar_animal(self.animal['id'], cambios)

            messagebox.showinfo("Éxito", "Animal actualizado correctamente")
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            try:
                import traceback
                print("[ModalEditarAnimal] Error en _guardar:")
                traceback.print_exc()
            except Exception:
                pass
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    # --------- Date Picker Helper ---------
    def _add_datepicker(self, parent, row, col):
        """Campo compacto con botón de calendario popup."""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row, column=col, padx=10, pady=(0, 10), sticky="ew")
        container.grid_columnconfigure(0, weight=1)
        entry = ctk.CTkEntry(container, height=36, corner_radius=8, font=("Segoe UI", 11))
        entry.grid(row=0, column=0, sticky="ew")

        def open_calendar():
            top = ctk.CTkToplevel(self)
            top.title("Seleccionar fecha")
            top.geometry("320x320")
            cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
            cal.pack(fill='both', expand=True, padx=10, pady=10)
            def choose():
                entry.delete(0, 'end')
                entry.insert(0, cal.get_date())
                top.destroy()
            ctk.CTkButton(top, text="Usar fecha", command=choose).pack(pady=8)

        ctk.CTkButton(container, text="📅", width=40, height=36, corner_radius=8, command=open_calendar).grid(row=0, column=1, padx=(6,0))
        return entry
