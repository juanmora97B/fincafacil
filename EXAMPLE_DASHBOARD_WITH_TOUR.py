"""
EXAMPLE: Practical Integration of Tour System into Dashboard Module
This shows exactly how to modify your existing dashboard to include the tour
"""

import customtkinter as ctk
import json
from pathlib import Path
from modules.utils.tour_manager import ModuleTourHelper
from modules.utils.logger import Logger

logger = Logger(__name__)


class DashboardModuleWithTour(ctk.CTkFrame):
    """
    Example: Dashboard module with integrated tour system
    Copy this pattern to your actual dashboard_main.py
    """
    
    def __init__(self, parent, app_main=None):
        super().__init__(parent)
        self.app_main = app_main
        
        # Step 1: Initialize tour helper (add this to your __init__)
        self.tour_helper = ModuleTourHelper("dashboard")
        
        # Initialize with auto_start=False (user clicks button)
        # or auto_start=True (shows on first visit automatically)
        if app_main:
            self.tour_helper.initialize_tour(app_main, auto_start=False)
        
        # Step 2: Create your UI normally
        self.setup_ui()
        
        # Step 3: Register widgets for tour highlighting
        self.register_tour_widgets()
        
        # Step 4: Load and configure tour steps
        self.setup_tour()
        
        logger.info("Dashboard initialized with tour system")
    
    def setup_ui(self):
        """Create dashboard UI (your existing code)"""
        
        # ===== HEADER / TOOLBAR =====
        header = ctk.CTkFrame(self, fg_color="#f0f0f0", height=50)
        header.pack(side="top", fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header,
            text="Dashboard - Resumen de tu Finca",
            font=("Arial", 16, "bold"),
            text_color="#1f538d"
        )
        title_label.pack(side="left", padx=15, pady=10)
        
        # Toolbar buttons
        toolbar = ctk.CTkFrame(header, fg_color="#f0f0f0")
        toolbar.pack(side="right", padx=15, pady=10)
        
        # Refresh button
        btn_refresh = ctk.CTkButton(
            toolbar,
            text="🔄 Actualizar",
            command=self.refresh_data,
            width=120,
            height=28
        )
        btn_refresh.pack(side="left", padx=5)
        
        # Settings button
        btn_settings = ctk.CTkButton(
            toolbar,
            text="⚙️ Opciones",
            width=100,
            height=28
        )
        btn_settings.pack(side="left", padx=5)
        
        # Tour button (add this - tour_helper creates it automatically)
        tour_btn = self.tour_helper.show_tour_button(toolbar)
        if tour_btn:
            tour_btn.pack(side="left", padx=5)
        
        # ===== CONTENT AREA =====
        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Row 1: Summary Cards
        summary_row = ctk.CTkFrame(content)
        summary_row.pack(fill="x", pady=(0, 10))
        
        # Card 1: Total Animals
        card1 = self.create_summary_card(
            summary_row,
            "Total de Animales",
            "23",
            "#2e7d32"
        )
        card1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Card 2: Active Animals
        card2 = self.create_summary_card(
            summary_row,
            "Activos",
            "21",
            "#1f538d"
        )
        card2.pack(side="left", fill="both", expand=True, padx=5)
        
        # Card 3: Inventory Value
        card3 = self.create_summary_card(
            summary_row,
            "Valor Inventario",
            "$28.7M",
            "#f57c00"
        )
        card3.pack(side="left", fill="both", expand=True, padx=5)
        
        # Card 4: Active Treatments
        card4 = self.create_summary_card(
            summary_row,
            "Tratamientos Activos",
            "3",
            "#d32f2f"
        )
        card4.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        # Store summary frame for tour registration
        self.summary_frame = summary_row
        
        # Row 2: Charts
        charts_row = ctk.CTkFrame(content)
        charts_row.pack(fill="both", expand=True, pady=(0, 10))
        
        # Left: Category Chart
        chart_left = ctk.CTkFrame(charts_row, fg_color="#f5f5f5", corner_radius=8)
        chart_left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        chart_title = ctk.CTkLabel(
            chart_left,
            text="Distribución por Categoría",
            font=("Arial", 12, "bold")
        )
        chart_title.pack(pady=10)
        
        chart_content = ctk.CTkLabel(
            chart_left,
            text="[Gráfica de categorías]",
            text_color="#999999"
        )
        chart_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.charts_frame = chart_left
        
        # Right: Production Chart
        chart_right = ctk.CTkFrame(charts_row, fg_color="#f5f5f5", corner_radius=8)
        chart_right.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        chart_title2 = ctk.CTkLabel(
            chart_right,
            text="Producción Últimos 30 días",
            font=("Arial", 12, "bold")
        )
        chart_title2.pack(pady=10)
        
        chart_content2 = ctk.CTkLabel(
            chart_right,
            text="[Gráfica de producción]",
            text_color="#999999"
        )
        chart_content2.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Row 3: Events and Alerts
        bottom_row = ctk.CTkFrame(content)
        bottom_row.pack(fill="both", expand=True)
        
        # Events
        events_frame = ctk.CTkFrame(bottom_row, fg_color="#f5f5f5", corner_radius=8)
        events_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        events_title = ctk.CTkLabel(
            events_frame,
            text="Eventos Recientes",
            font=("Arial", 12, "bold")
        )
        events_title.pack(pady=10, padx=10, anchor="w")
        
        events_content = ctk.CTkLabel(
            events_frame,
            text="• 15/12 - Nuevo animal registrado (Ternero #45)\n• 14/12 - Venta de 2 animales\n• 13/12 - Cambio de potrero (Lote 3)",
            text_color="#666666",
            justify="left"
        )
        events_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.events_frame = events_frame
        
        # Alerts
        alerts_frame = ctk.CTkFrame(bottom_row, fg_color="#fff3e0", corner_radius=8)
        alerts_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        alerts_title = ctk.CTkLabel(
            alerts_frame,
            text="⚠️ Alertas",
            font=("Arial", 12, "bold"),
            text_color="#e65100"
        )
        alerts_title.pack(pady=10, padx=10, anchor="w")
        
        alerts_content = ctk.CTkLabel(
            alerts_frame,
            text="• Vaca #12 sin pesaje desde hace 7 días\n• Potrero 2 capacidad al 95%\n• Falta registrar compra de medicinas",
            text_color="#e65100",
            justify="left"
        )
        alerts_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.alerts_frame = alerts_frame
    
    def create_summary_card(
        self,
        parent: ctk.CTkFrame,
        title: str,
        value: str,
        color: str
    ) -> ctk.CTkFrame:
        """Create a styled summary card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=8,
            height=80
        )
        card.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 10),
            text_color="white"
        )
        title_label.pack(pady=(8, 2))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 20, "bold"),
            text_color="white"
        )
        value_label.pack(pady=(2, 8))
        
        return card
    
    def register_tour_widgets(self):
        """
        Step 3: Register widgets for tour highlighting
        Widget names must match those in tour_config.json
        """
        self.tour_helper.tour_manager.register_widget("dashboard_summary", self.summary_frame)
        self.tour_helper.tour_manager.register_widget("dashboard_charts", self.charts_frame)
        self.tour_helper.tour_manager.register_widget("dashboard_events", self.events_frame)
        self.tour_helper.tour_manager.register_widget("dashboard_alerts", self.alerts_frame)
        
        logger.debug("Dashboard widgets registered for tour")
    
    def setup_tour(self):
        """
        Step 4: Load tour configuration and add steps
        """
        try:
            config_path = Path("config/tour_config.json")
            if not config_path.exists():
                logger.warning("tour_config.json not found")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Get dashboard tour steps
            dashboard_config = config.get("dashboard", {})
            steps = dashboard_config.get("steps", [])
            
            if steps:
                self.tour_helper.add_steps(steps)
                logger.info(f"Loaded {len(steps)} tour steps for dashboard")
            else:
                logger.warning("No tour steps found for dashboard")
                
        except Exception as e:
            logger.error(f"Error loading tour: {e}")
    
    def refresh_data(self):
        """Refresh dashboard data"""
        logger.info("Dashboard data refreshed")
        # Add your refresh logic here
        pass


# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================

"""
To add this to your actual dashboard_main.py:

1. Import at the top:
   from modules.utils.tour_manager import ModuleTourHelper
   import json
   from pathlib import Path

2. In your __init__, add after existing setup:
   # Tour setup
   self.tour_helper = ModuleTourHelper("dashboard")
   if self.master:
       self.tour_helper.initialize_tour(self.master, auto_start=False)
   
3. When creating your toolbar/header, add:
   tour_btn = self.tour_helper.show_tour_button(toolbar)
   if tour_btn:
       tour_btn.pack(side="right", padx=10)

4. After all UI is created, register widgets:
   # Register widgets for tour
   self.tour_helper.tour_manager.register_widget("dashboard_summary", self.summary_frame)
   self.tour_helper.tour_manager.register_widget("dashboard_charts", self.charts_frame)
   self.tour_helper.tour_manager.register_widget("dashboard_events", self.events_frame)
   self.tour_helper.tour_manager.register_widget("dashboard_alerts", self.alerts_frame)

5. Load tour configuration:
   def setup_tour(self):
       try:
           with open("config/tour_config.json", "r", encoding="utf-8") as f:
               config = json.load(f)
               steps = config.get("dashboard", {}).get("steps", [])
               self.tour_helper.add_steps(steps)
       except Exception as e:
           logger.error(f"Error loading tour: {e}")

6. Call setup_tour() in __init__:
   self.setup_tour()

That's it! Now when user clicks "❓ Tour" button, they'll see the interactive tour.
"""


if __name__ == "__main__":
    # Test standalone
    app = ctk.CTk()
    app.geometry("1200x700")
    app.title("Dashboard with Tour - Demo")
    
    dashboard = DashboardModuleWithTour(app, app)
    dashboard.pack(fill="both", expand=True)
    
    app.mainloop()
