import customtkinter as ctk
import calendar
from datetime import datetime, date

class DatePicker(ctk.CTkToplevel):
    def __init__(self, master, target_entry, initial_date=None):
        super().__init__(master)
        self.title("📅 Seleccionar Fecha")
        self.resizable(False, False)
        self.target_entry = target_entry
        self.transient(master)
        self.grab_set()
        
        # Centrar ventana
        self.after(10, self.center_window)
        
        # Variables de estado
        today = datetime.today()
        if initial_date:
            try:
                today = datetime.strptime(initial_date, "%Y-%m-%d")
            except Exception:
                pass
        self.year = today.year
        self.month = today.month
        self.today = date.today()
        self.selected_date = None

        # Contenedor principal con padding elegante
        main_container = ctk.CTkFrame(self, fg_color=("#F8F9FA", "#1E1E1E"), corner_radius=15)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header con año y mes
        header = ctk.CTkFrame(main_container, fg_color=("#1976D2", "#1565C0"), corner_radius=10, height=80)
        header.pack(fill="x", padx=10, pady=(10, 15))
        header.pack_propagate(False)
        
        # Selector de año
        year_frame = ctk.CTkFrame(header, fg_color="transparent")
        year_frame.pack(pady=(8, 2))
        
        ctk.CTkButton(
            year_frame, text="◀", width=35, height=28,
            fg_color=("white", "#2196F3"), 
            text_color=("#1976D2", "white"),
            hover_color=("#E3F2FD", "#1E88E5"),
            command=self.prev_year,
            corner_radius=8,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=3)
        
        self.label_year = ctk.CTkLabel(
            year_frame, 
            text=str(self.year),
            font=("Segoe UI", 16, "bold"),
            text_color="white",
            width=80
        )
        self.label_year.pack(side="left", padx=8)
        
        ctk.CTkButton(
            year_frame, text="▶", width=35, height=28,
            fg_color=("white", "#2196F3"),
            text_color=("#1976D2", "white"),
            hover_color=("#E3F2FD", "#1E88E5"),
            command=self.next_year,
            corner_radius=8,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=3)
        
        # Selector de mes con navegación
        month_frame = ctk.CTkFrame(header, fg_color="transparent")
        month_frame.pack()
        
        ctk.CTkButton(
            month_frame, text="◀", width=35, height=28,
            fg_color=("white", "#2196F3"),
            text_color=("#1976D2", "white"),
            hover_color=("#E3F2FD", "#1E88E5"),
            command=self.prev_month,
            corner_radius=8,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=3)
        
        self.label_month = ctk.CTkLabel(
            month_frame,
            text="",
            font=("Segoe UI", 18, "bold"),
            text_color="white",
            width=180
        )
        self.label_month.pack(side="left", padx=8)
        
        ctk.CTkButton(
            month_frame, text="▶", width=35, height=28,
            fg_color=("white", "#2196F3"),
            text_color=("#1976D2", "white"),
            hover_color=("#E3F2FD", "#1E88E5"),
            command=self.next_month,
            corner_radius=8,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=3)

        # Calendar frame con borde elegante
        cal_container = ctk.CTkFrame(main_container, fg_color="transparent")
        cal_container.pack(padx=10, pady=5)
        
        self.cal_frame = ctk.CTkFrame(cal_container, fg_color="transparent")
        self.cal_frame.pack()

        # Botones de acción
        action_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        ctk.CTkButton(
            action_frame,
            text="📅 Hoy",
            command=self.go_today,
            width=120,
            height=36,
            fg_color=("#2E7D32", "#388E3C"),
            hover_color=("#388E3C", "#4CAF50"),
            font=("Segoe UI", 12, "bold"),
            corner_radius=8
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame,
            text="✖ Cancelar",
            command=self.destroy,
            width=120,
            height=36,
            fg_color=("#757575", "#616161"),
            hover_color=("#616161", "#757575"),
            font=("Segoe UI", 12, "bold"),
            corner_radius=8
        ).pack(side="right", padx=5)

        self.draw_calendar()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def draw_calendar(self):
        """Dibuja el calendario con diseño moderno y profesional"""
        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        # Actualizar etiquetas
        month_names_es = [
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.label_month.configure(text=month_names_es[self.month])
        self.label_year.configure(text=str(self.year))

        # Encabezado de días con estilo
        days_header = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        header_row = ctk.CTkFrame(self.cal_frame, fg_color="transparent")
        header_row.pack(pady=(0, 8))
        
        for i, day_name in enumerate(days_header):
            # Fin de semana en color diferente
            text_color = "#D32F2F" if i >= 5 else "#1976D2"
            ctk.CTkLabel(
                header_row,
                text=day_name,
                width=50,
                font=("Segoe UI", 11, "bold"),
                text_color=text_color
            ).pack(side="left", padx=2, pady=2)

        # Días del mes con diseño mejorado
        cal = calendar.Calendar(firstweekday=0)  # Lunes como primer día
        week_frame = None
        
        for idx, day in enumerate(cal.itermonthdays(self.year, self.month)):
            if idx % 7 == 0:
                week_frame = ctk.CTkFrame(self.cal_frame, fg_color="transparent")
                week_frame.pack()
            
            if day == 0:
                # Espacio vacío
                ctk.CTkLabel(week_frame, text="", width=50, height=40).pack(
                    side="left", padx=2, pady=2
                )
            else:
                # Verificar si es el día de hoy
                is_today = (day == self.today.day and 
                           self.month == self.today.month and 
                           self.year == self.today.year)
                
                # Verificar si es fin de semana
                is_weekend = idx % 7 >= 5
                
                # Colores según el estado
                if is_today:
                    fg_color = ("#FF6F00", "#FF8F00")
                    hover_color = ("#F57C00", "#FFB300")
                    text_color = "white"
                    border_width = 2
                elif is_weekend:
                    fg_color = ("#FFEBEE", "#3E2723")
                    hover_color = ("#FFCDD2", "#4E342E")
                    text_color = ("#D32F2F", "#FF5252")
                    border_width = 0
                else:
                    fg_color = ("#E3F2FD", "#263238")
                    hover_color = ("#BBDEFB", "#37474F")
                    text_color = ("#1976D2", "#90CAF9")
                    border_width = 0
                
                btn = ctk.CTkButton(
                    week_frame,
                    text=str(day),
                    width=50,
                    height=40,
                    fg_color=fg_color,
                    hover_color=hover_color,
                    text_color=text_color,
                    border_width=border_width,
                    border_color=("#FF6F00", "#FFB300") if is_today else None,
                    command=lambda d=day: self.select_day(d),
                    corner_radius=8,
                    font=("Segoe UI", 13, "bold" if is_today else "normal")
                )
                btn.pack(side="left", padx=2, pady=2)

    def select_day(self, day):
        """Selecciona un día y cierra el calendario"""
        date_str = f"{self.year:04d}-{self.month:02d}-{day:02d}"
        self.target_entry.delete(0, "end")
        self.target_entry.insert(0, date_str)
        self.selected_date = date_str
        self.destroy()

    def prev_month(self):
        """Navega al mes anterior"""
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.draw_calendar()

    def next_month(self):
        """Navega al mes siguiente"""
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.draw_calendar()
    
    def prev_year(self):
        """Navega al año anterior"""
        self.year -= 1
        self.draw_calendar()
    
    def next_year(self):
        """Navega al año siguiente"""
        self.year += 1
        self.draw_calendar()

    def go_today(self):
        """Vuelve a la fecha de hoy y la selecciona"""
        today = datetime.today()
        self.year = today.year
        self.month = today.month
        self.draw_calendar()
        # Auto-seleccionar hoy
        self.select_day(today.day)


def attach_date_picker(button_parent, entry, use_grid=False, grid_row=0, grid_column=0, **grid_kwargs):
    """
    Adjunta un botón de calendario profesional junto a un campo de entrada.
    
    Args:
        button_parent: Widget padre donde se colocará el botón
        entry: Campo de entrada donde se insertará la fecha seleccionada
        use_grid: Si True, usa grid() en lugar de pack()
        grid_row: Fila para grid (solo si use_grid=True)
        grid_column: Columna para grid (solo si use_grid=True)
        **grid_kwargs: Argumentos adicionales para grid() (sticky, padx, pady, etc.)
    """
    def _open():
        DatePicker(button_parent, entry, initial_date=entry.get().strip() or None)
    
    btn = ctk.CTkButton(
        button_parent,
        text="📅",
        width=40,
        height=32,
        command=_open,
        fg_color=("#1976D2", "#1565C0"),
        hover_color=("#1565C0", "#1976D2"),
        corner_radius=8,
        font=("Segoe UI", 14)
    )
    if use_grid:
        btn.grid(row=grid_row, column=grid_column, **grid_kwargs)
    else:
        btn.pack(side="left", padx=4)
    return btn
