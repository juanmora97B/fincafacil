"""
Modal Ver Animal - Vista detallada con foto y datos completos
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from pathlib import Path


class ModalVerAnimal(ctk.CTkToplevel):
    """Modal profesional para ver detalle de animal"""
    
    def __init__(self, master, animal_data):
        super().__init__(master)
        
        self.animal = animal_data
        
        # Configuración ventana
        self.title(f"Detalles: {animal_data.get('codigo', 'N/A')}")
        self.geometry("900x650")
        self.resizable(True, True)
        try:
            self.overrideredirect(False)
            self.attributes('-toolwindow', False)
        except Exception:
            pass
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"+{x}+{y}")
        
        self._build_ui()
    
    def _build_ui(self):
        """Construir interfaz"""
        # Header
        header = ctk.CTkFrame(self, corner_radius=12, fg_color="#1f538d")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text="🐄 Información del Animal",
            font=("Segoe UI", 24, "bold"),
            text_color="white"
        ).pack(pady=20)
        
        # Contenedor principal con scroll
        content = ctk.CTkScrollableFrame(self, corner_radius=12, fg_color=("gray95", "gray20"))
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Foto
        foto_frame = ctk.CTkFrame(content, corner_radius=10, width=300, height=300)
        foto_frame.pack(pady=20)
        foto_frame.pack_propagate(False)
        
        self._load_photo(foto_frame)
        
        # Datos en dos columnas
        data_container = ctk.CTkFrame(content, fg_color="transparent")
        data_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Columna izquierda
        left_col = ctk.CTkFrame(data_container, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self._add_field(left_col, "ID", str(self.animal.get('id', 'N/A')))
        self._add_field(left_col, "Código", self.animal.get('codigo', 'N/A'))
        self._add_field(left_col, "Nombre", self.animal.get('nombre', 'N/A'))
        self._add_field(left_col, "Sexo", self.animal.get('sexo', 'N/A'))
        self._add_field(left_col, "Fecha Nacimiento", self.animal.get('fecha_nacimiento', 'N/A'))
        self._add_field(left_col, "Categoría", self.animal.get('categoria', 'N/A'))
        
        # Columna derecha
        right_col = ctk.CTkFrame(data_container, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self._add_field(right_col, "Finca", self.animal.get('finca', 'N/A'))
        self._add_field(right_col, "Potrero", self.animal.get('potrero', 'N/A'))
        self._add_field(right_col, "Lote", self.animal.get('lote', 'N/A'))
        self._add_field(right_col, "Sector", self.animal.get('sector', 'N/A'))
        
        peso = self.animal.get('ultimo_peso')
        peso_str = f"{peso:.1f} kg" if peso else "No registrado"
        self._add_field(right_col, "Último Peso", peso_str)
        
        inv = "Sí ✓" if self.animal.get('inventariado') == 1 else "No"
        self._add_field(right_col, "Inventariado", inv)
        
        # Botón cerrar (fuera del scroll, siempre visible)
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(pady=15)
        
        ctk.CTkButton(
            footer,
            text="✓ Cerrar",
            command=self.destroy,
            width=200,
            height=45,
            corner_radius=10,
            font=("Segoe UI", 14, "bold"),
            fg_color="#2d6a4f",
            hover_color="#1f4d38"
        ).pack()
    
    def _add_field(self, parent, label, value):
        """Agregar campo de datos"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            frame,
            text=f"{label}:",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            frame,
            text=str(value),
            font=("Segoe UI", 12),
            anchor="e",
            text_color="gray20"
        ).pack(side="right")
    
    def _load_photo(self, container):
        """Cargar foto del animal"""
        foto_path = self.animal.get('foto_path')
        
        if foto_path and Path(foto_path).exists():
            try:
                img = Image.open(foto_path)
                img.thumbnail((280, 280), Image.Resampling.LANCZOS)
                
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(280, 280))
                
                ctk.CTkLabel(
                    container,
                    image=photo,
                    text=""
                ).pack(expand=True)
                return
            except Exception as e:
                print(f"Error cargando foto: {e}")
        
        # Placeholder
        ctk.CTkLabel(
            container,
            text="📷\nSin foto",
            font=("Segoe UI", 32),
            text_color="gray50"
        ).pack(expand=True)
