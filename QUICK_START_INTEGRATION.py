"""
QUICK START GUIDE FOR DEVELOPERS
5-minute integration guide for adding tour to any FincaFácil module
"""

QUICK_START = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    TOUR INTEGRATION - 5 MINUTE GUIDE                       ║
╚════════════════════════════════════════════════════════════════════════════╝

STEP 1: Add imports (30 seconds)
─────────────────────────────────────────────────────────────────────────────
At the top of your module_main.py file, add:

    from modules.utils.tour_manager import ModuleTourHelper
    import json
    from pathlib import Path


STEP 2: Initialize tour in __init__ (1 minute)
─────────────────────────────────────────────────────────────────────────────
After creating all your UI widgets, add this code:

    # Initialize tour
    self.tour_helper = ModuleTourHelper("module_name")  # Replace with your module name
    
    # Initialize with app reference (needed for overlay positioning)
    if self.master:
        self.tour_helper.initialize_tour(self.master, auto_start=False)
    
    # Register your UI widgets
    self.register_tour_widgets()
    
    # Load tour configuration
    self.setup_tour()


STEP 3: Add tour button to toolbar (30 seconds)
─────────────────────────────────────────────────────────────────────────────
In your toolbar/header frame, add:

    tour_btn = self.tour_helper.show_tour_button(toolbar_frame)
    if tour_btn:
        tour_btn.pack(side="right", padx=10)


STEP 4: Register widgets (1 minute)
─────────────────────────────────────────────────────────────────────────────
Add this method to your class:

    def register_tour_widgets(self):
        '''Register UI elements for tour highlighting'''
        self.tour_helper.tour_manager.register_widget("widget_id", self.widget)
        self.tour_helper.tour_manager.register_widget("widget_id_2", self.widget_2)
        # ... add all widgets you want highlighted in the tour


STEP 5: Load configuration (1 minute)
─────────────────────────────────────────────────────────────────────────────
Add this method to your class:

    def setup_tour(self):
        '''Load tour configuration from JSON'''
        try:
            config_path = Path("config/tour_config.json")
            if not config_path.exists():
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            module_config = config.get("module_name", {})  # Replace with your module name
            steps = module_config.get("steps", [])
            
            if steps:
                self.tour_helper.add_steps(steps)
        except Exception as e:
            logger.error(f"Error loading tour: {e}")


THAT'S IT! 🎉
─────────────────────────────────────────────────────────────────────────────
Your module now has a professional interactive tour!

When users click the "❓ Tour" button, they will see:
  ✓ Dark overlay highlighting each UI section
  ✓ Animated spotlight around widgets
  ✓ Styled tooltips with instructions
  ✓ Navigation buttons (Previous, Next, Skip)
  ✓ Progress indicator showing "Paso X de Y"


WIDGET REGISTRATION EXAMPLES
─────────────────────────────────────────────────────────────────────────────

# For different UI elements:

# CTkLabel
self.tour_helper.tour_manager.register_widget("title_label", self.title)

# CTkButton
self.tour_helper.tour_manager.register_widget("action_button", self.btn_action)

# CTkFrame
self.tour_helper.tour_manager.register_widget("content_area", self.content_frame)

# CTkEntry / CTkComboBox
self.tour_helper.tour_manager.register_widget("search_field", self.entry_search)

# CTkTabview
self.tour_helper.tour_manager.register_widget("tabs", self.tab_view)


CONFIGURATION IN tour_config.json
─────────────────────────────────────────────────────────────────────────────

Each module needs an entry in config/tour_config.json:

    "module_name": {
        "name": "Module Display Name",
        "description": "Description of what users learn",
        "steps": [
            {
                "title": "Step Title",
                "description": "Clear explanation (keep under 100 chars)",
                "widget_name": "widget_id",  # Must match registered widget ID
                "duration": 3  # 0 = manual (user clicks Next), >0 = auto-advance (seconds)
            }
        ]
    }


TESTING YOUR INTEGRATION
─────────────────────────────────────────────────────────────────────────────

1. Run the test script first:
   python tour_system_tester.py

2. Check that:
   ✓ Tour button appears in your module
   ✓ Clicking button starts the tour
   ✓ Each step highlights correct widget
   ✓ Tooltips appear with correct text
   ✓ Navigation buttons work
   ✓ No error messages in console

3. Test on different window sizes:
   ✓ Resize window while tour is running
   ✓ Spotlight should follow widget
   ✓ Tooltip should reposition automatically
   ✓ Control window stays visible


COMMON INTEGRATION PATTERNS
─────────────────────────────────────────────────────────────────────────────

Pattern 1: Simple Module with Main Frame
────────────────────────────────────────
class MyModuleUI(ctk.CTkFrame):
    def __init__(self, parent, app_main=None):
        super().__init__(parent)
        self.app_main = app_main
        
        # Initialize tour
        self.tour_helper = ModuleTourHelper("my_module")
        if app_main:
            self.tour_helper.initialize_tour(app_main, auto_start=False)
        
        # Create UI
        self.setup_ui()
        
        # Register and load tour
        self.register_tour_widgets()
        self.setup_tour()


Pattern 2: Complex Module with Multiple Frames
───────────────────────────────────────────────
class MyComplexModule(ctk.CTkFrame):
    def __init__(self, parent, app_main=None):
        super().__init__(parent)
        self.app_main = app_main
        
        # Tour
        self.tour_helper = ModuleTourHelper("complex_module")
        if app_main:
            self.tour_helper.initialize_tour(app_main, auto_start=False)
        
        # Create multiple frames
        self.header = self.create_header()      # Tour highlights this
        self.toolbar = self.create_toolbar()    # Tour highlights this
        self.content = self.create_content()    # Tour highlights sections
        self.footer = self.create_footer()      # Tour highlights this
        
        # Register all sections
        self.register_tour_widgets()
        self.setup_tour()


Pattern 3: Module with Tab View
────────────────────────────────
class TabbedModule(ctk.CTkFrame):
    def __init__(self, parent, app_main=None):
        super().__init__(parent)
        self.app_main = app_main
        
        # Tour
        self.tour_helper = ModuleTourHelper("tabbed_module")
        if app_main:
            self.tour_helper.initialize_tour(app_main, auto_start=False)
        
        # Create tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True)
        
        # Add tabs and register each
        self.tab1 = self.tab_view.add("Tab 1")
        self.tab2 = self.tab_view.add("Tab 2")
        self.tab3 = self.tab_view.add("Tab 3")
        
        self.register_tour_widgets()
        self.setup_tour()


TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────

Q: Tour button doesn't appear
A: Make sure you call show_tour_button() AFTER creating toolbar frame
   and pack() the frame before calling the method

Q: Widget not highlighting during tour
A: 1. Check widget name in config matches registered name exactly
   2. Make sure widget is actually created before registering
   3. Verify widget is visible and has a valid size

Q: Overlay doesn't appear
A: Make sure you pass the main app window to initialize_tour()
   Example: self.tour_helper.initialize_tour(self.master, auto_start=False)

Q: Tour steps not loading
A: 1. Check tour_config.json file exists in config/ folder
   2. Verify JSON is valid (use: python -m json.tool config/tour_config.json)
   3. Check module name in code matches name in JSON
   4. Verify steps array is not empty

Q: Error: "No module named 'modules.utils.tour_manager'"
A: Make sure:
   1. You're running from project root directory
   2. modules/utils/tour_manager.py file exists
   3. Python path includes project root

Q: Tour buttons not clickable
A: The control window might be behind your main window
   Solution: The system keeps it on top automatically
   If issue persists, check window manager settings


PERFORMANCE TIPS
─────────────────────────────────────────────────────────────────────────────

✓ Register widgets AFTER they're created (in __init__)
✓ Don't register hidden widgets
✓ Keep widget registry small (only tour widgets)
✓ Load config once at startup, not on every tour start
✓ Use duration=0 for user-paced tours, duration>0 for guided tours
✓ Don't create new TourManager for each tour, reuse ModuleTourHelper


NEXT STEPS
─────────────────────────────────────────────────────────────────────────────

1. See EXAMPLE_DASHBOARD_WITH_TOUR.py for complete working example
2. See tour_quick_reference.py for copy-paste templates
3. See TOUR_IMPLEMENTATION_GUIDE.md for detailed documentation
4. Run tour_system_tester.py to test your integration
5. Check tour_config.json for available tour configurations


QUESTIONS?
─────────────────────────────────────────────────────────────────────────────

See these files for help:
  • tour_manager.py - Core implementation (400+ lines of well-commented code)
  • tour_quick_reference.py - Quick code templates
  • TOUR_IMPLEMENTATION_GUIDE.md - Comprehensive guide
  • INTEGRATION_CHECKLIST_ALL_MODULES.py - Integration steps for all modules
  • EXAMPLE_DASHBOARD_WITH_TOUR.py - Complete working example


═════════════════════════════════════════════════════════════════════════════
HAPPY TOURING! 🎉
═════════════════════════════════════════════════════════════════════════════
"""


def print_quick_start():
    """Print quick start guide"""
    print(QUICK_START)


if __name__ == "__main__":
    print_quick_start()
