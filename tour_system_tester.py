"""
TOUR SYSTEM TEST & VALIDATION SCRIPT
Run this to verify the tour system is working correctly before integration
"""

import customtkinter as ctk
import json
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.utils.tour_manager import TourManager, TourStep, ModuleTourHelper
from modules.utils.logger import Logger

logger = Logger(__name__)


class TourSystemTester(ctk.CTk):
    """Interactive tour system test application"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Tour System - Test & Validation")
        self.geometry("1000x700")
        
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Tour System Test & Validation",
            font=("Arial", 18, "bold"),
            text_color="#1f538d"
        )
        title.pack(pady=(0, 20))
        
        # Tabs
        tab_view = ctk.CTkTabview(main_frame)
        tab_view.pack(fill="both", expand=True)
        
        # Tab 1: System Tests
        self.create_tests_tab(tab_view)
        
        # Tab 2: Configuration Check
        self.create_config_tab(tab_view)
        
        # Tab 3: Interactive Demo
        self.create_demo_tab(tab_view)
        
        # Results frame
        results_frame = ctk.CTkFrame(main_frame, fg_color="#f5f5f5", corner_radius=8)
        results_frame.pack(fill="both", pady=(10, 0), padx=0)
        
        results_title = ctk.CTkLabel(
            results_frame,
            text="Test Results & Logs",
            font=("Arial", 12, "bold")
        )
        results_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.results_text = ctk.CTkTextbox(results_frame, height=150)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
    def create_tests_tab(self, tab_view):
        """Tab 1: System component tests"""
        tab = tab_view.add("System Tests")
        
        # Test buttons
        test_frame = ctk.CTkFrame(tab)
        test_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Test 1: Import Check
        btn1 = ctk.CTkButton(
            test_frame,
            text="✓ Test 1: Check Imports",
            command=self.test_imports,
            fg_color="#2e7d32",
            height=40
        )
        btn1.pack(fill="x", pady=5)
        
        # Test 2: Config File
        btn2 = ctk.CTkButton(
            test_frame,
            text="✓ Test 2: Check Config File",
            command=self.test_config_file,
            fg_color="#2e7d32",
            height=40
        )
        btn2.pack(fill="x", pady=5)
        
        # Test 3: TourManager Initialization
        btn3 = ctk.CTkButton(
            test_frame,
            text="✓ Test 3: Initialize TourManager",
            command=self.test_tour_manager_init,
            fg_color="#2e7d32",
            height=40
        )
        btn3.pack(fill="x", pady=5)
        
        # Test 4: Widget Registration
        btn4 = ctk.CTkButton(
            test_frame,
            text="✓ Test 4: Widget Registration",
            command=self.test_widget_registration,
            fg_color="#2e7d32",
            height=40
        )
        btn4.pack(fill="x", pady=5)
        
        # Test 5: Step Loading
        btn5 = ctk.CTkButton(
            test_frame,
            text="✓ Test 5: Load Tour Steps",
            command=self.test_step_loading,
            fg_color="#2e7d32",
            height=40
        )
        btn5.pack(fill="x", pady=5)
        
        # Run All Tests
        btn_all = ctk.CTkButton(
            test_frame,
            text="🧪 RUN ALL TESTS",
            command=self.run_all_tests,
            fg_color="#1f538d",
            height=40,
            font=("Arial", 12, "bold")
        )
        btn_all.pack(fill="x", pady=(20, 5))
        
    def create_config_tab(self, tab_view):
        """Tab 2: Configuration validation"""
        tab = tab_view.add("Configuration")
        
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Check Config
        btn1 = ctk.CTkButton(
            frame,
            text="📋 Check tour_config.json",
            command=self.check_config_structure,
            height=40
        )
        btn1.pack(fill="x", pady=5)
        
        # Validate JSON
        btn2 = ctk.CTkButton(
            frame,
            text="✓ Validate JSON Syntax",
            command=self.validate_json_syntax,
            height=40
        )
        btn2.pack(fill="x", pady=5)
        
        # List All Tours
        btn3 = ctk.CTkButton(
            frame,
            text="📚 List All Available Tours",
            command=self.list_all_tours,
            height=40
        )
        btn3.pack(fill="x", pady=5)
        
        # Count Steps
        btn4 = ctk.CTkButton(
            frame,
            text="🔢 Count Total Tour Steps",
            command=self.count_tour_steps,
            height=40
        )
        btn4.pack(fill="x", pady=5)
        
    def create_demo_tab(self, tab_view):
        """Tab 3: Interactive demo"""
        tab = tab_view.add("Interactive Demo")
        
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Demo widgets
        demo_title = ctk.CTkLabel(
            frame,
            text="Demo: Try the Tour System",
            font=("Arial", 12, "bold")
        )
        demo_title.pack(pady=(0, 20))
        
        # Create sample widgets
        widget1 = ctk.CTkLabel(
            frame,
            text="Widget 1: Main Content Area",
            fg_color="#f5f5f5",
            padx=10,
            pady=20,
            corner_radius=8
        )
        widget1.pack(fill="x", pady=10)
        
        widget2 = ctk.CTkLabel(
            frame,
            text="Widget 2: Form Input Area",
            fg_color="#f5f5f5",
            padx=10,
            pady=20,
            corner_radius=8
        )
        widget2.pack(fill="x", pady=10)
        
        widget3 = ctk.CTkLabel(
            frame,
            text="Widget 3: Action Buttons",
            fg_color="#f5f5f5",
            padx=10,
            pady=20,
            corner_radius=8
        )
        widget3.pack(fill="x", pady=10)
        
        # Demo buttons
        btn_demo = ctk.CTkButton(
            frame,
            text="▶ Start Demo Tour",
            command=lambda: self.run_demo_tour(widget1, widget2, widget3),
            fg_color="#2e7d32",
            height=40,
            font=("Arial", 12, "bold")
        )
        btn_demo.pack(fill="x", pady=(20, 5))
        
    # ========================================================================
    # TEST METHODS
    # ========================================================================
    
    def log_result(self, message: str, status: str = "INFO"):
        """Log test result to results textbox"""
        colors = {
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "INFO": "ℹ️"
        }
        emoji = colors.get(status, "•")
        self.results_text.insert("end", f"{emoji} {message}\n")
        self.results_text.see("end")
        logger.info(f"{status}: {message}")
    
    def clear_results(self):
        """Clear results textbox"""
        self.results_text.delete("1.0", "end")
    
    def test_imports(self):
        """Test 1: Check if all imports work"""
        self.clear_results()
        self.log_result("Testing imports...", "INFO")
        
        try:
            from modules.utils.tour_manager import TourManager
            self.log_result("✓ TourManager imported", "SUCCESS")
        except ImportError as e:
            self.log_result(f"✗ Failed to import TourManager: {e}", "ERROR")
            return
        
        try:
            from modules.utils.tour_manager import TourStep
            self.log_result("✓ TourStep imported", "SUCCESS")
        except ImportError as e:
            self.log_result(f"✗ Failed to import TourStep: {e}", "ERROR")
            return
        
        try:
            from modules.utils.tour_manager import ModuleTourHelper
            self.log_result("✓ ModuleTourHelper imported", "SUCCESS")
        except ImportError as e:
            self.log_result(f"✗ Failed to import ModuleTourHelper: {e}", "ERROR")
            return
        
        self.log_result("All imports successful!", "SUCCESS")
    
    def test_config_file(self):
        """Test 2: Check if config file exists and is readable"""
        self.clear_results()
        self.log_result("Checking config file...", "INFO")
        
        config_path = Path("config/tour_config.json")
        
        if not config_path.exists():
            self.log_result(f"✗ Config file not found: {config_path}", "ERROR")
            return
        
        self.log_result(f"✓ Config file found: {config_path}", "SUCCESS")
        
        file_size = config_path.stat().st_size
        self.log_result(f"✓ File size: {file_size} bytes", "SUCCESS")
    
    def test_tour_manager_init(self):
        """Test 3: Initialize TourManager"""
        self.clear_results()
        self.log_result("Initializing TourManager...", "INFO")
        
        try:
            # Create a test window
            test_window = ctk.CTk()
            test_window.withdraw()  # Hide it
            
            # Initialize TourManager
            manager = TourManager(test_window, "test")
            self.log_result("✓ TourManager initialized", "SUCCESS")
            
            # Check properties
            if hasattr(manager, 'tour_name'):
                self.log_result(f"✓ Tour name: {manager.tour_name}", "SUCCESS")
            
            test_window.destroy()
            self.log_result("✓ Test window cleanup successful", "SUCCESS")
            
        except Exception as e:
            self.log_result(f"✗ Error initializing TourManager: {e}", "ERROR")
    
    def test_widget_registration(self):
        """Test 4: Widget registration"""
        self.clear_results()
        self.log_result("Testing widget registration...", "INFO")
        
        try:
            test_window = ctk.CTk()
            test_window.withdraw()
            
            manager = TourManager(test_window, "test")
            
            # Create test widget
            test_label = ctk.CTkLabel(test_window, text="Test")
            
            # Register widget
            manager.register_widget("test_widget", test_label)
            self.log_result("✓ Widget registered", "SUCCESS")
            
            # Check if registered
            if "test_widget" in manager.widget_registry:
                self.log_result("✓ Widget found in registry", "SUCCESS")
            else:
                self.log_result("✗ Widget not found in registry", "ERROR")
            
            test_window.destroy()
            
        except Exception as e:
            self.log_result(f"✗ Error during widget registration: {e}", "ERROR")
    
    def test_step_loading(self):
        """Test 5: Load tour steps from config"""
        self.clear_results()
        self.log_result("Loading tour steps from config...", "INFO")
        
        try:
            config_path = Path("config/tour_config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.log_result("✓ Config file loaded", "SUCCESS")
            
            # Check structure
            tours = [k for k in config.keys() if k != "metadata"]
            self.log_result(f"✓ Found {len(tours)} tours", "SUCCESS")
            
            # Show tours
            for tour in tours:
                steps = config[tour].get("steps", [])
                self.log_result(f"  • {tour}: {len(steps)} steps", "INFO")
            
        except json.JSONDecodeError as e:
            self.log_result(f"✗ Invalid JSON: {e}", "ERROR")
        except Exception as e:
            self.log_result(f"✗ Error loading steps: {e}", "ERROR")
    
    def run_all_tests(self):
        """Run all tests sequentially"""
        self.clear_results()
        self.log_result("=" * 60, "INFO")
        self.log_result("RUNNING ALL TESTS", "INFO")
        self.log_result("=" * 60, "INFO")
        self.update()
        
        self.test_imports()
        self.update()
        
        self.test_config_file()
        self.update()
        
        self.test_tour_manager_init()
        self.update()
        
        self.test_widget_registration()
        self.update()
        
        self.test_step_loading()
        self.update()
        
        self.log_result("=" * 60, "INFO")
        self.log_result("ALL TESTS COMPLETED", "SUCCESS")
        self.log_result("=" * 60, "INFO")
    
    def check_config_structure(self):
        """Check tour_config.json structure"""
        self.clear_results()
        self.log_result("Checking config structure...", "INFO")
        
        try:
            with open("config/tour_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Expected keys
            expected_tours = ["dashboard", "animales", "ficha_animal", "reubicacion", 
                            "reportes", "ajustes", "potreros", "insumos", "nomina"]
            
            for tour in expected_tours:
                if tour in config:
                    self.log_result(f"✓ Tour '{tour}' found", "SUCCESS")
                else:
                    self.log_result(f"⚠️ Tour '{tour}' missing", "WARNING")
            
            # Check step structure
            sample_tour = config.get("dashboard", {})
            if "steps" in sample_tour:
                steps = sample_tour["steps"]
                self.log_result(f"✓ Dashboard tour has {len(steps)} steps", "SUCCESS")
                
                # Check first step structure
                if steps:
                    first_step = steps[0]
                    required_fields = ["title", "description", "widget_name", "duration"]
                    for field in required_fields:
                        if field in first_step:
                            self.log_result(f"  ✓ Field '{field}' present", "INFO")
                        else:
                            self.log_result(f"  ✗ Field '{field}' missing", "ERROR")
            
        except Exception as e:
            self.log_result(f"✗ Error: {e}", "ERROR")
    
    def validate_json_syntax(self):
        """Validate JSON syntax"""
        self.clear_results()
        self.log_result("Validating JSON syntax...", "INFO")
        
        try:
            with open("config/tour_config.json", 'r', encoding='utf-8') as f:
                json.load(f)
            self.log_result("✓ JSON syntax is valid", "SUCCESS")
        except json.JSONDecodeError as e:
            self.log_result(f"✗ Invalid JSON: {e.msg} at line {e.lineno}", "ERROR")
        except Exception as e:
            self.log_result(f"✗ Error: {e}", "ERROR")
    
    def list_all_tours(self):
        """List all available tours"""
        self.clear_results()
        self.log_result("Available tours:", "INFO")
        
        try:
            with open("config/tour_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            tours = [k for k in config.keys() if k != "metadata"]
            for i, tour in enumerate(tours, 1):
                steps = config[tour].get("steps", [])
                self.log_result(f"{i}. {tour.replace('_', ' ').title()} ({len(steps)} steps)", "INFO")
            
        except Exception as e:
            self.log_result(f"✗ Error: {e}", "ERROR")
    
    def count_tour_steps(self):
        """Count total tour steps"""
        self.clear_results()
        self.log_result("Counting tour steps...", "INFO")
        
        try:
            with open("config/tour_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            total_steps = 0
            for tour_name, tour_data in config.items():
                if tour_name != "metadata":
                    steps = tour_data.get("steps", [])
                    total_steps += len(steps)
                    self.log_result(f"  {tour_name}: {len(steps)} steps", "INFO")
            
            self.log_result(f"\n✓ Total steps across all tours: {total_steps}", "SUCCESS")
            
        except Exception as e:
            self.log_result(f"✗ Error: {e}", "ERROR")
    
    def run_demo_tour(self, widget1, widget2, widget3):
        """Run interactive demo tour"""
        self.log_result("Starting demo tour...", "INFO")
        
        try:
            # Create tour manager
            tour_manager = TourManager(self, "demo")
            
            # Register demo widgets
            tour_manager.register_widget("demo_widget_1", widget1)
            tour_manager.register_widget("demo_widget_2", widget2)
            tour_manager.register_widget("demo_widget_3", widget3)
            
            # Create demo steps
            steps = [
                TourStep(
                    title="Welcome!",
                    description="This is step 1 of the demo tour",
                    widget_name="demo_widget_1",
                    duration=3
                ),
                TourStep(
                    title="Step 2",
                    description="Now we're highlighting step 2",
                    widget_name="demo_widget_2",
                    duration=3
                ),
                TourStep(
                    title="Final Step",
                    description="This is the last step. Click Next to finish!",
                    widget_name="demo_widget_3",
                    duration=0
                )
            ]
            
            tour_manager.add_steps(steps)
            tour_manager.start_tour()
            
            self.log_result("✓ Demo tour started", "SUCCESS")
            
        except Exception as e:
            self.log_result(f"✗ Error starting demo tour: {e}", "ERROR")


if __name__ == "__main__":
    app = TourSystemTester()
    app.mainloop()
