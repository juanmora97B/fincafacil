"""
QUICK REFERENCE: Tour Interactivo
Copiar y pegar para usar en tus módulos
"""

# ============================================================================
# OPCIÓN 1: Tour Simple (5 líneas)
# ============================================================================

from modules.utils.tour_manager import ModuleTourHelper

tour = ModuleTourHelper("dashboard")
tour.initialize_tour(app, auto_start=False)
btn = tour.show_tour_button(toolbar)


# ============================================================================
# OPCIÓN 2: Tour Completo (Template para módulos)
# ============================================================================

import customtkinter as ctk
from modules.utils.tour_manager import ModuleTourHelper
import json

class MyModule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Setup tour
        self.tour = ModuleTourHelper("module_name")
        self.tour.initialize_tour(parent.master, auto_start=False)
        
        # Create UI
        self.setup_ui()
        self.setup_tour()
    
    def setup_ui(self):
        # Toolbar
        toolbar = ctk.CTkFrame(self)
        
        # Buttons
        self.btn_add = ctk.CTkButton(toolbar, text="+ Add")
        self.btn_add.pack(side="left", padx=5)
        
        # Tour button
        tour_btn = self.tour.show_tour_button(toolbar)
        if tour_btn:
            tour_btn.pack(side="right", padx=5)
        
        toolbar.pack(side="top", fill="x", padx=10, pady=5)
        
        # Content
        self.content = ctk.CTkFrame(self)
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Register widgets AFTER creation
        self.tour.tour_manager.register_widget("btn_add", self.btn_add)
        self.tour.tour_manager.register_widget("content", self.content)
    
    def setup_tour(self):
        try:
            with open("config/tour_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                steps = config.get("module_name", {}).get("steps", [])
                self.tour.add_steps(steps)
        except Exception as e:
            print(f"Error: {e}")


# ============================================================================
# OPCIÓN 3: Tour Manual (Control total)
# ============================================================================

from modules.utils.tour_manager import TourManager, TourStep

tour = TourManager(app, tour_name="custom")

# Agregar widgets
tour.register_widget("widget1", my_button)
tour.register_widget("widget2", my_table)

# Crear pasos manualmente
step1 = TourStep(
    title="Primer Paso",
    description="Esto es lo primero que ves",
    widget=my_button,
    duration=0  # Manual (0) o auto-avance en segundos
)

step2 = TourStep(
    title="Segundo Paso",
    description="Ahora ves esto",
    widget=my_table,
    action=lambda: print("Action ejecutada")
)

tour.add_step(step1)
tour.add_step(step2)

# Iniciar
tour.start_tour()

# Controles
tour.next_step()
tour.previous_step()
tour.skip_tour()
tour.end_tour()


# ============================================================================
# OPCIÓN 4: Tour desde JSON
# ============================================================================

from modules.utils.tour_manager import TourManager

tour = TourManager(app, tour_name="dashboard")

steps = [
    {
        "title": "Bienvenida",
        "description": "Explicación aquí",
        "widget_name": "summary_card"
    },
    {
        "title": "Gráficas",
        "description": "Visualiza datos",
        "widget_name": "charts_frame",
        "duration": 2  # Auto-avanza en 2 seg
    }
]

tour.add_steps_from_config(steps)
tour.start_tour()


# ============================================================================
# CHECKLIST: Agregar tour a módulo existente
# ============================================================================

"""
[ ] 1. Importar ModuleTourHelper y json
    from modules.utils.tour_manager import ModuleTourHelper
    import json

[ ] 2. En __init__ crear tour_helper
    self.tour = ModuleTourHelper("nombre_modulo")
    self.tour.initialize_tour(self.master, auto_start=False)

[ ] 3. Después de crear cada widget importante, registrarlo
    self.tour.tour_manager.register_widget("widget_id", widget)

[ ] 4. En método setup_tour() cargar config
    with open("config/tour_config.json") as f:
        config = json.load(f)
        self.tour.add_steps(config["nombre_modulo"]["steps"])

[ ] 5. Agregar botón tour a toolbar
    btn = self.tour.show_tour_button(toolbar)

[ ] 6. Agregar nueva sección en tour_config.json
    {
      "nombre_modulo": {
        "name": "Nombre para mostrar",
        "steps": [...]
      }
    }

[ ] 7. Probar: ejecutar app, ir a módulo, clic en botón "❓ Tour"
"""


# ============================================================================
# EJEMPLOS: Casos de uso
# ============================================================================

# Tour que auto-avanza con timings
pasos_con_timing = [
    {"title": "Bienvenida", "description": "...", "duration": 2},   # 2 seg
    {"title": "Paso 2", "description": "...", "duration": 3},        # 3 seg
    {"title": "Paso 3", "description": "...", "duration": 0},        # Manual
]

# Tour con acciones personalizadas
def mostrar_pestaña_1():
    notebook.select(0)

pasos_con_acciones = [
    {"title": "Tab 1", "description": "...", "widget_name": "tab1", "action": mostrar_pestaña_1},
]

# Tour que no molesta (solo en primera visita)
tour = ModuleTourHelper("module")
tour.initialize_tour(app, auto_start=True)  # auto_start=True

# Tour que se puede reiniciar manualmente
# (User nunca lo hace automático de nuevo, pero puede hacer clic en botón)


# ============================================================================
# TIPS Y TRUCOS
# ============================================================================

# 1. Deshabilitar botón tour hasta que sea necesario
#    if not is_first_time:
#        tour_btn.configure(state="disabled")

# 2. Tours en cascada (Module1 -> Module2 -> etc)
#    Cada módulo carga su tour cuando se abre

# 3. Skipear ciertos pasos condicionalmente
#    if not advanced_mode:
#        pasos.remove(pasos[5])

# 4. Tour con multimedia (preparado para futuro)
#    {"title": "...", "image": "path/to/image.png"}

# 5. Localization (tours multiidioma)
#    tour_es = config["dashboard"]["steps_es"]
#    tour_en = config["dashboard"]["steps_en"]

# 6. Analytics (contar cuántos completan el tour)
#    def on_tour_complete():
#        db.update_user_stats(tour_completed=True)

# 7. Tours condicionales (según tipo de usuario)
#    if is_admin:
#        tour = "dashboard_admin"
#    else:
#        tour = "dashboard_user"


# ============================================================================
# ARCHIVOS NECESARIOS
# ============================================================================

"""
✅ modules/utils/tour_manager.py
   - TourManager (clase principal)
   - TourOverlay (efecto spotlight)
   - TourTooltip (tooltips estilizados)
   - ModuleTourHelper (wrapper para módulos)

✅ config/tour_config.json
   - Definición de todos los tours
   - Pasos para cada módulo

✅ modules/utils/__init__.py
   - Exports de tour_manager

✅ modules/utils/tour_integration_examples.py
   - Ejemplos y patrones

✅ TOUR_IMPLEMENTATION_GUIDE.md
   - Documentación completa

✅ este archivo (tour_quick_reference.py)
   - Quick reference
"""


# ============================================================================
# DEBUGGING
# ============================================================================

# Ver si tour está completado
tour = ModuleTourHelper("dashboard")
print(tour.tour_manager.has_completed_tour())  # True/False

# Ver estado actual
print(tour.tour_manager.current_step)  # Número del paso actual
print(tour.tour_manager.is_running)    # ¿Está ejecutándose?

# Ver pasos registrados
print(len(tour.tour_manager.steps))    # Cantidad de pasos

# Ver widgets registrados
print(tour.tour_manager.widget_registry)  # Dict de widgets

# Resetear tour (para testing)
import os
os.remove("config/tour_dashboard_state.json")
# Ahora el tour volverá a mostrarse
