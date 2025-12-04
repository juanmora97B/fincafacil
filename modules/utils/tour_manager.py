"""
Professional Interactive Tour System for FincaFácil
Provides guided tours with overlays, highlighting, and tooltips
"""

import customtkinter as ctk
from tkinter import Canvas
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
import threading
import time

from modules.utils.logger import Logger

logger = Logger(__name__)


class TourStep:
    """Represents a single step in the tour"""
    
    def __init__(
        self,
        title: str,
        description: str,
        widget: Optional[ctk.CTkWidget] = None,
        widget_name: Optional[str] = None,
        action: Optional[Callable] = None,
        duration: int = 0
    ):
        """
        Initialize a tour step
        
        Args:
            title: Step title
            description: Detailed description
            widget: Reference to the widget to highlight
            widget_name: Widget identifier for delayed binding
            action: Callback function to execute before showing this step
            duration: Auto-advance after N seconds (0 = manual)
        """
        self.title = title
        self.description = description
        self.widget = widget
        self.widget_name = widget_name
        self.action = action
        self.duration = duration


class TourTooltip:
    """Styled tooltip with arrow pointing to target element"""
    
    def __init__(self, parent: ctk.CTk, title: str, text: str):
        self.parent = parent
        self.title = title
        self.text = text
        self.window = None
        
    def create(self, x: int, y: int, position: str = "bottom") -> ctk.CTkToplevel:
        """
        Create and display tooltip
        
        Args:
            x, y: Position for tooltip
            position: "top", "bottom", "left", "right"
        """
        self.window = ctk.CTkToplevel(self.parent)
        self.window.attributes("-topmost", True)
        self.window.wm_attributes("-transparentcolor", "#1a1a1a")
        
        # Container with padding
        container = ctk.CTkFrame(
            self.window,
            fg_color="#2e2e2e",
            corner_radius=12,
            border_width=2,
            border_color="#1f538d"
        )
        container.pack(padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text=self.title,
            font=("Arial", 14, "bold"),
            text_color="#1f538d"
        )
        title_label.pack(padx=15, pady=(10, 5), anchor="w")
        
        # Separator line
        separator = ctk.CTkFrame(container, height=1, fg_color="#1f538d")
        separator.pack(padx=15, pady=5, fill="x")
        
        # Text content
        text_label = ctk.CTkLabel(
            container,
            text=self.text,
            font=("Arial", 11),
            text_color="#cccccc",
            wraplength=320,
            justify="left"
        )
        text_label.pack(padx=15, pady=(5, 10), anchor="w")
        
        # Adjust size
        self.window.update_idletasks()
        width = container.winfo_width() + 20
        height = container.winfo_height() + 20
        
        # Position with offset based on direction
        offset_x = offset_y = 15
        if position == "top":
            y -= (height + offset_y)
        elif position == "left":
            x -= (width + offset_x)
        elif position == "right":
            x += offset_x
        # "bottom" is default
        else:
            y += offset_y
        
        self.window.geometry(f"+{x}+{y}")
        return self.window


class TourOverlay:
    """Canvas-based overlay that highlights specific widgets"""
    
    def __init__(self, parent: ctk.CTk, highlight_color: str = "#1f538d", overlay_alpha: float = 0.7):
        self.parent = parent
        self.highlight_color = highlight_color
        self.overlay_alpha = overlay_alpha
        self.overlay_canvas = None
        self.highlight_id = None
        
    def create(self) -> Canvas:
        """Create overlay canvas"""
        canvas = Canvas(
            self.parent,
            bg="#000000",
            highlightthickness=0,
            cursor="arrow"
        )
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        canvas.lower()
        
        # Make slightly transparent by making it dark overlay
        self.overlay_canvas = canvas
        return canvas
    
    def highlight_widget(self, widget: ctk.CTkWidget, padding: int = 10):
        """
        Highlight a specific widget on the overlay
        
        Args:
            widget: Widget to highlight
            padding: Padding around the widget
        """
        if not self.overlay_canvas:
            return
        
        try:
            # Get widget coordinates
            x = widget.winfo_x()
            y = widget.winfo_y()
            width = widget.winfo_width()
            height = widget.winfo_height()
            
            # Clear previous highlight
            self.overlay_canvas.delete("all")
            
            # Draw dark overlay
            canvas_width = self.overlay_canvas.winfo_width()
            canvas_height = self.overlay_canvas.winfo_height()
            self.overlay_canvas.create_rectangle(
                0, 0, canvas_width, canvas_height,
                fill="#000000",
                outline="#000000",
                stipple="gray50"
            )
            
            # Create spotlight (highlight area)
            x1 = x - padding
            y1 = y - padding
            x2 = x + width + padding
            y2 = y + height + padding
            
            # Draw bright rectangle at highlight position
            self.highlight_id = self.overlay_canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=self.highlight_color,
                width=3,
                fill=""
            )
            
            # Add subtle shadow effect
            self.overlay_canvas.create_rectangle(
                x1-2, y1-2, x2+2, y2+2,
                outline="#666666",
                width=1,
                fill=""
            )
            
        except Exception as e:
            logger.error(f"Error highlighting widget: {e}")
    
    def remove(self):
        """Remove overlay"""
        if self.overlay_canvas:
            self.overlay_canvas.destroy()
            self.overlay_canvas = None


class TourManager:
    """
    Main tour management class
    Handles tour state, navigation, and UI
    """
    
    def __init__(
        self,
        app: ctk.CTk,
        tour_name: str = "default",
        config_file: Optional[str] = None
    ):
        """
        Initialize TourManager
        
        Args:
            app: Main application window
            tour_name: Identifier for this tour
            config_file: Path to tour config JSON (if None, uses memory)
        """
        self.app = app
        self.tour_name = tour_name
        self.config_file = config_file or f"config/tour_{tour_name}_state.json"
        
        self.steps: List[TourStep] = []
        self.current_step = 0
        self.is_running = False
        self.is_paused = False
        
        self.overlay = None
        self.tooltip_window = None
        self.control_window = None
        self.tooltip = None
        
        # Widget registry for delayed binding
        self.widget_registry: Dict[str, ctk.CTkWidget] = {}
        
        # Auto-advance timer
        self.auto_advance_timer = None
        
        logger.info(f"TourManager initialized: {tour_name}")
    
    def register_widget(self, name: str, widget: ctk.CTkWidget):
        """Register a widget for later reference"""
        self.widget_registry[name] = widget
        logger.debug(f"Registered widget: {name}")
    
    def add_step(self, step: TourStep):
        """Add a step to the tour"""
        self.steps.append(step)
    
    def add_steps_from_config(self, steps_data: List[Dict]):
        """
        Add steps from configuration data
        
        Args:
            steps_data: List of dicts with step information
        """
        for step_data in steps_data:
            widget = None
            if "widget_name" in step_data and step_data["widget_name"]:
                widget = self.widget_registry.get(step_data["widget_name"])
            
            action = None
            if "action" in step_data and callable(step_data["action"]):
                action = step_data["action"]
            
            step = TourStep(
                title=step_data.get("title", ""),
                description=step_data.get("description", ""),
                widget=widget,
                widget_name=step_data.get("widget_name"),
                action=action,
                duration=step_data.get("duration", 0)
            )
            self.add_step(step)
    
    def has_completed_tour(self) -> bool:
        """Check if user has completed this tour"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('completed', False)
        except Exception as e:
            logger.warning(f"Error checking tour completion: {e}")
        return False
    
    def mark_tour_completed(self):
        """Mark this tour as completed"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'completed': True, 'timestamp': time.time()}, f)
            logger.info(f"Tour marked as completed: {self.tour_name}")
        except Exception as e:
            logger.error(f"Error marking tour completed: {e}")
    
    def start_tour(self):
        """Start the tour from the beginning"""
        if not self.steps:
            logger.warning("No steps defined for tour")
            return
        
        self.is_running = True
        self.current_step = 0
        
        # Create overlay
        self.overlay = TourOverlay(self.app)
        self.overlay.create()
        
        logger.info(f"Tour started: {self.tour_name}")
        self._show_current_step()
    
    def _show_current_step(self):
        """Display the current step"""
        if self.current_step >= len(self.steps):
            self.end_tour()
            return
        
        # Cancel auto-advance timer if running
        if self.auto_advance_timer:
            self.app.after_cancel(self.auto_advance_timer)
            self.auto_advance_timer = None
        
        step = self.steps[self.current_step]
        
        # Execute step action if defined
        if step.action:
            try:
                step.action()
            except Exception as e:
                logger.error(f"Error executing step action: {e}")
        
        # Highlight widget if available
        if step.widget and self.overlay:
            self.overlay.highlight_widget(step.widget)
        
        # Show tooltip
        self._show_tooltip(step)
        
        # Show control buttons
        self._show_controls()
        
        # Set up auto-advance if duration > 0
        if step.duration > 0:
            self.auto_advance_timer = self.app.after(
                step.duration * 1000,
                self.next_step
            )
        
        logger.debug(f"Showing step {self.current_step + 1}: {step.title}")
    
    def _show_tooltip(self, step: TourStep):
        """Display tooltip for current step"""
        # Close previous tooltip
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except:
                pass
        
        # Determine position for tooltip
        position = "bottom"
        x, y = 100, 100
        
        if step.widget:
            try:
                x = step.widget.winfo_x() + step.widget.winfo_width() // 2
                y = step.widget.winfo_y() + step.widget.winfo_height()
                # Adjust position based on widget location
                if y > self.app.winfo_height() * 0.6:
                    position = "top"
                    y = step.widget.winfo_y()
            except:
                pass
        else:
            # Center on screen
            x = self.app.winfo_width() // 2
            y = self.app.winfo_height() // 2
        
        self.tooltip = TourTooltip(
            self.app,
            title=step.title,
            text=step.description
        )
        self.tooltip_window = self.tooltip.create(x, y, position)
    
    def _show_controls(self):
        """Display control buttons (previous, next, skip)"""
        # Close previous control window
        if self.control_window:
            try:
                self.control_window.destroy()
            except:
                pass
        
        # Create new control window
        self.control_window = ctk.CTkToplevel(self.app)
        self.control_window.attributes("-topmost", True)
        self.control_window.title("Tour Controls")
        self.control_window.geometry("350x80")
        
        # Position at bottom center
        screen_width = self.app.winfo_width()
        window_x = self.app.winfo_x() + (screen_width - 350) // 2
        window_y = self.app.winfo_y() + self.app.winfo_height() - 100
        self.control_window.geometry(f"+{window_x}+{window_y}")
        
        # Progress label
        progress_text = f"Paso {self.current_step + 1} de {len(self.steps)}"
        progress_label = ctk.CTkLabel(
            self.control_window,
            text=progress_text,
            font=("Arial", 11),
            text_color="#999999"
        )
        progress_label.pack(pady=(10, 5))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.control_window)
        buttons_frame.pack(pady=10, padx=10, fill="x")
        
        # Previous button
        if self.current_step > 0:
            btn_prev = ctk.CTkButton(
                buttons_frame,
                text="← Anterior",
                command=self.previous_step,
                width=90,
                fg_color="#666666",
                hover_color="#777777"
            )
            btn_prev.pack(side="left", padx=5)
        
        # Skip button
        btn_skip = ctk.CTkButton(
            buttons_frame,
            text="Saltar",
            command=self.skip_tour,
            width=90,
            fg_color="#d32f2f",
            hover_color="#e53935"
        )
        btn_skip.pack(side="left", padx=5)
        
        # Next button
        btn_next = ctk.CTkButton(
            buttons_frame,
            text="Siguiente →" if self.current_step < len(self.steps) - 1 else "Finalizar",
            command=self.next_step,
            width=90,
            fg_color="#2e7d32",
            hover_color="#388e3c"
        )
        btn_next.pack(side="right", padx=5)
    
    def next_step(self):
        """Advance to next step"""
        self.current_step += 1
        self._show_current_step()
    
    def previous_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._show_current_step()
    
    def skip_tour(self):
        """Skip the tour"""
        response = ctk.CTkInputDialog(
            text="¿Estás seguro que deseas salir del tour?",
            title="Confirmar salida"
        )
        # In real app, you might use messagebox instead
        self.end_tour()
    
    def end_tour(self):
        """End the tour and clean up"""
        self.is_running = False
        
        # Cancel auto-advance timer
        if self.auto_advance_timer:
            self.app.after_cancel(self.auto_advance_timer)
            self.auto_advance_timer = None
        
        # Clean up UI elements
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except:
                pass
            self.tooltip_window = None
        
        if self.control_window:
            try:
                self.control_window.destroy()
            except:
                pass
            self.control_window = None
        
        if self.overlay:
            self.overlay.remove()
            self.overlay = None
        
        self.mark_tour_completed()
        logger.info(f"Tour ended: {self.tour_name}")
    
    def pause_tour(self):
        """Pause the tour"""
        self.is_paused = True
        if self.control_window:
            self.control_window.lower()
    
    def resume_tour(self):
        """Resume the tour"""
        self.is_paused = False
        if self.control_window:
            self.control_window.lift()


class ModuleTourHelper:
    """Helper class for module-specific tour integration"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.tour_manager: Optional[TourManager] = None
    
    def initialize_tour(self, app: ctk.CTk, auto_start: bool = False):
        """
        Initialize tour for this module
        
        Args:
            app: Main application window
            auto_start: Automatically start if never completed
        """
        self.tour_manager = TourManager(app, tour_name=self.module_name)
        
        if auto_start and not self.tour_manager.has_completed_tour():
            self.tour_manager.start_tour()
    
    def show_tour_button(self, parent: ctk.CTkFrame) -> ctk.CTkButton:
        """Create and return a tour button"""
        if not self.tour_manager:
            return None
        
        btn = ctk.CTkButton(
            parent,
            text="❓ Tour",
            command=self.tour_manager.start_tour,
            width=80,
            height=28,
            font=("Arial", 10),
            fg_color="#1f538d",
            hover_color="#2e7d32"
        )
        return btn
    
    def add_steps(self, steps_data: List[Dict]):
        """Add tour steps from configuration"""
        if self.tour_manager:
            self.tour_manager.add_steps_from_config(steps_data)
