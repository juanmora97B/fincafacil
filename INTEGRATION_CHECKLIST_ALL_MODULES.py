"""
INTEGRATION CHECKLIST FOR ALL MODULES
Quick reference for integrating tour system into every module
"""

MODULE_INTEGRATION_STEPS = {
    "dashboard": {
        "file": "modules/ui/dashboard_main.py",
        "widgets_to_register": [
            "dashboard_summary",
            "dashboard_charts",
            "dashboard_events",
            "dashboard_alerts"
        ],
        "description": "Main dashboard showing farm overview"
    },
    
    "animales": {
        "file": "modules/ui/animales_main.py",
        "widgets_to_register": [
            "animales_tabla",
            "animales_filtros",
            "animales_btn_nuevo",
            "animales_busqueda",
            "animales_acciones"
        ],
        "description": "Animal registry and management"
    },
    
    "ficha_animal": {
        "file": "modules/ui/ficha_animal_main.py",
        "widgets_to_register": [
            "ficha_info_general",
            "ficha_foto",
            "ficha_procedencia",
            "ficha_peso",
            "ficha_salud",
            "ficha_reproduccion",
            "ficha_movimientos",
            "ficha_eventos"
        ],
        "description": "Individual animal record details"
    },
    
    "reubicacion": {
        "file": "modules/ui/reubicacion_main.py",
        "widgets_to_register": [
            "reubicacion_animal",
            "reubicacion_origen",
            "reubicacion_destino",
            "reubicacion_potreros",
            "reubicacion_motivo",
            "reubicacion_fecha",
            "reubicacion_observaciones"
        ],
        "description": "Animal relocation between paddocks"
    },
    
    "reportes": {
        "file": "modules/ui/reportes_main.py",
        "widgets_to_register": [
            "reportes_finca",
            "reportes_fecha_inicio",
            "reportes_fecha_fin",
            "reportes_tipo",
            "reportes_grafica",
            "reportes_tabla",
            "reportes_exportar",
            "reportes_comparativa",
            "reportes_filtros",
            "reportes_periodo"
        ],
        "description": "Reports and analytics"
    },
    
    "ajustes": {
        "file": "modules/ui/settings_main.py",
        "widgets_to_register": [
            "ajustes_datos",
            "ajustes_tema",
            "ajustes_idioma",
            "ajustes_respaldo",
            "ajustes_usuarios",
            "ajustes_permisos",
            "ajustes_avanzado"
        ],
        "description": "Settings and preferences"
    },
    
    "potreros": {
        "file": "modules/ui/potreros_main.py",
        "widgets_to_register": [
            "potreros_tabla",
            "potreros_nuevo",
            "potreros_editar",
            "potreros_eliminar",
            "potreros_animales"
        ],
        "description": "Paddock management"
    },
    
    "insumos": {
        "file": "modules/ui/insumos_main.py",
        "widgets_to_register": [
            "insumos_tabla",
            "insumos_nuevo",
            "insumos_entrada",
            "insumos_salida",
            "insumos_stock"
        ],
        "description": "Inventory management"
    },
    
    "nomina": {
        "file": "modules/ui/nomina_main.py",
        "widgets_to_register": [
            "nomina_empleados",
            "nomina_salarios",
            "nomina_generador",
            "nomina_descuentos",
            "nomina_exportar"
        ],
        "description": "Payroll management"
    }
}


CODE_TEMPLATE = """
# TEMPLATE: How to integrate tour into any module
# Copy this pattern to your module_main.py

# ============================================================================
# STEP 1: Add imports at the top of your file
# ============================================================================
from modules.utils.tour_manager import ModuleTourHelper
import json
from pathlib import Path

# ============================================================================
# STEP 2: In your __init__ method, add these lines after creating UI
# ============================================================================
        # Initialize tour system
        self.tour_helper = ModuleTourHelper("MODULE_NAME")  # Replace with actual module name
        
        # Initialize with app reference (for overlay overlay positioning)
        if self.master:
            self.tour_helper.initialize_tour(self.master, auto_start=False)
        
        # Register widgets after they're created
        self.register_tour_widgets()
        
        # Load tour configuration
        self.setup_tour()

# ============================================================================
# STEP 3: Add tour button to your toolbar
# ============================================================================
        # In your toolbar/header setup:
        tour_btn = self.tour_helper.show_tour_button(toolbar_frame)
        if tour_btn:
            tour_btn.pack(side="right", padx=10)

# ============================================================================
# STEP 4: Add these two methods to your class
# ============================================================================
    def register_tour_widgets(self):
        '''Register UI elements for tour highlighting'''
        self.tour_helper.tour_manager.register_widget("widget_id_1", self.widget_1)
        self.tour_helper.tour_manager.register_widget("widget_id_2", self.widget_2)
        self.tour_helper.tour_manager.register_widget("widget_id_3", self.widget_3)
        # Add all widgets from MODULE_INTEGRATION_STEPS["MODULE_NAME"]["widgets_to_register"]
    
    def setup_tour(self):
        '''Load tour configuration from JSON'''
        try:
            config_path = Path("config/tour_config.json")
            if not config_path.exists():
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            module_config = config.get("MODULE_NAME", {})  # Replace with actual module name
            steps = module_config.get("steps", [])
            
            if steps:
                self.tour_helper.add_steps(steps)
        except Exception as e:
            logger.error(f"Error loading tour: {e}")

# ============================================================================
# THAT'S IT! 5 lines of code in __init__ + 2 new methods
# ============================================================================
"""


VERIFICATION_CHECKLIST = """
VERIFICATION CHECKLIST - After integrating tour into each module:

[ ] Tour button appears in module header/toolbar
[ ] Clicking tour button starts the tour
[ ] Each step highlights the correct widget
[ ] Tooltip appears with correct text
[ ] Previous/Next buttons work correctly
[ ] Skip button exits the tour
[ ] Tour completes without errors
[ ] State persists (tour won't show again until reset)
[ ] Works on different window sizes
[ ] Overlay properly darkens background
[ ] Spotlight box appears around highlighted widget
[ ] Text is readable (good contrast)
[ ] Navigation buttons are clickable
[ ] No error messages in logger
"""


TESTING_SCRIPT = """
# Quick test to verify tour system is working

import customtkinter as ctk
from modules.utils.tour_manager import ModuleTourHelper
import json

app = ctk.CTk()
app.geometry("1000x600")

# Initialize tour for test module
tour = ModuleTourHelper("test")
tour.initialize_tour(app, auto_start=False)

# Create sample widgets
frame = ctk.CTkFrame(app)
frame.pack(fill="both", expand=True, padx=10, pady=10)

label = ctk.CTkLabel(frame, text="Test Widget", font=("Arial", 14, "bold"))
label.pack(pady=20)

button = ctk.CTkButton(frame, text="Start Tour", command=tour.tour_manager.start_tour)
button.pack(pady=10)

# Register widgets
tour.tour_manager.register_widget("test_label", label)
tour.tour_manager.register_widget("test_button", button)

# Create simple tour steps
steps = [
    {
        "title": "Welcome to Tour",
        "description": "This is a test of the tour system",
        "widget_name": "test_label",
        "duration": 3
    },
    {
        "title": "Click to Continue",
        "description": "Press Next to continue",
        "widget_name": "test_button",
        "duration": 0
    }
]

tour.add_steps(steps)

app.mainloop()
"""


COMMON_ISSUES_SOLUTIONS = """
COMMON ISSUES & SOLUTIONS:

Issue 1: Tour button doesn't appear
  Solution: Make sure tour_helper.show_tour_button() is called AFTER UI is created
  
Issue 2: Widget not highlighted
  Solution: Widget name in config must match registered name exactly
  Example: 
    - Register: tour.register_widget("animales_tabla", self.tabla)
    - Config: "widget_name": "animales_tabla"
  
Issue 3: Overlay doesn't appear
  Solution: Make sure initialize_tour() is called with the main app window
  Example: tour.tour_manager.initialize_tour(root_window, auto_start=False)
  
Issue 4: Tooltip text cut off
  Solution: Keep description under 100 characters, or use line breaks
  
Issue 5: Tour buttons not clickable
  Solution: Make sure control window is not behind main window
  - The system keeps it on top automatically
  
Issue 6: Tour repeats every time user visits module
  Solution: State is automatically saved. If it's repeating:
    - Check that tour_config.json exists
    - Verify JSON syntax is valid
    - Check user_data/tour_state.json permissions
  
Issue 7: TypeError in tour_manager
  Solution: Make sure you're running Python 3.7+
  - Check: python --version
  - Verify all imports in tour_manager.py are available
  
Issue 8: Widget registry is empty
  Solution: Register widgets AFTER they're created in __init__
  - Don't register in __init__ before creating widgets
  - Register immediately after widget creation
  
Issue 9: Tour steps not loading from JSON
  Solution: Check file path and JSON syntax
  - Path should be "config/tour_config.json"
  - Use json.tool to validate: python -m json.tool config/tour_config.json
  
Issue 10: Module crashes when starting tour
  Solution: Make sure all imports are correct
  - from modules.utils.tour_manager import TourManager, ModuleTourHelper
  - Verify these files exist in modules/utils/
"""


def print_integration_guide():
    """Print complete integration guide to console"""
    print("\n" + "="*80)
    print("TOUR SYSTEM INTEGRATION GUIDE")
    print("="*80 + "\n")
    
    print("MODULES TO INTEGRATE:")
    print("-" * 80)
    for module, info in MODULE_INTEGRATION_STEPS.items():
        print(f"\n{module.upper()}")
        print(f"  File: {info['file']}")
        print(f"  Widgets ({len(info['widgets_to_register'])}):")
        for widget in info['widgets_to_register']:
            print(f"    - {widget}")
    
    print("\n\n" + "="*80)
    print("CODE TEMPLATE")
    print("="*80)
    print(CODE_TEMPLATE)
    
    print("\n\n" + "="*80)
    print("VERIFICATION CHECKLIST")
    print("="*80)
    print(VERIFICATION_CHECKLIST)
    
    print("\n\n" + "="*80)
    print("TESTING SCRIPT")
    print("="*80)
    print(TESTING_SCRIPT)
    
    print("\n\n" + "="*80)
    print("COMMON ISSUES & SOLUTIONS")
    print("="*80)
    print(COMMON_ISSUES_SOLUTIONS)


if __name__ == "__main__":
    print_integration_guide()
