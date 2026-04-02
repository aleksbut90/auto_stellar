# Main tabbed window for the Unified Game Automation Tool
# Title: "Stellar and Arrival Skill Automation"

import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading
import mouse
from core.game_connector import GameConnector
from core.ocr_engine import OCREngine
from ui.stellar_tab import StellarTab
from ui.arrival_tab import ArrivalTab
from ui.collection_tab import CollectionTab
from ui.heils_clicker_tab import HeilsClickerTab
from ui.troubleshooting_tab import TroubleshootingTab
from ui.help_tab import HelpTab

class MainWindow:
    def __init__(self):
        """Initialize the main tabbed window"""
        self.root = tk.Tk()
        self.root.title("Stellar and Arrival Skill Automation")
        self.root.geometry("700x800")
        self.root.attributes("-topmost", True)

        # Track which tool is currently running (mutual exclusion)
        self.current_running_tool = None

        # Initialize status variable first
        self.status_var = tk.StringVar(value="Initializing...")

        # Shared components (after status_var is created)
        self.game_connector = GameConnector(self.update_status)
        self.ocr_engine = OCREngine(self.update_status)

        # Set up emergency kill switch (ESC key)
        keyboard.add_hotkey('esc', self.emergency_stop)

        # Create UI
        self.create_ui()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_ui(self):
        """Create the main UI with tabs"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Auto-connect to game and show status
        self.auto_connect_to_game()

        # Emergency stop info - positioned at top for better visibility
        emergency_frame = ttk.Frame(main_frame)
        emergency_frame.pack(fill=tk.X, pady=(0, 10))
        emergency_label = ttk.Label(emergency_frame, text="Emergency Stop: ESC",
                                   foreground="red", font=("Arial", 9, "bold"))
        emergency_label.pack(anchor=tk.W)

        # Unified Start/Stop controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_start = ttk.Button(control_frame, text="Start", command=self.unified_start, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_stop = ttk.Button(control_frame, text="Stop", command=self.unified_stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event to stop automation when switching tabs
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Create tab frames
        arrival_frame = ttk.Frame(self.notebook)
        stellar_frame = ttk.Frame(self.notebook)
        collection_frame = ttk.Frame(self.notebook)
        heils_frame = ttk.Frame(self.notebook)
        troubleshooting_frame = ttk.Frame(self.notebook)
        help_frame = ttk.Frame(self.notebook)

        # Add tabs to notebook (Arrival Skill first)
        self.notebook.add(arrival_frame, text="Arrival Skill")
        self.notebook.add(stellar_frame, text="Stellar System")
        self.notebook.add(collection_frame, text="Collection Filler")
        self.notebook.add(heils_frame, text="Heils Clicker")
        self.notebook.add(help_frame, text="Help")
        self.notebook.add(troubleshooting_frame, text="Troubleshooting")

        # Create tab instances
        self.arrival_tab = ArrivalTab(arrival_frame, self)
        self.stellar_tab = StellarTab(stellar_frame, self)
        self.collection_tab = CollectionTab(collection_frame, self)
        self.heils_clicker_tab = HeilsClickerTab(heils_frame, self)
        self.help_tab = HelpTab(help_frame, self)
        self.troubleshooting_tab = TroubleshootingTab(troubleshooting_frame, self)
        
        # Update unified buttons after all tabs are loaded
        self.update_unified_buttons()

    def auto_connect_to_game(self):
        """Automatically connect to the game and show connection status"""
        if self.game_connector.connect_to_game():
            # Get game window info for display
            window_rect = self.game_connector.get_window_rect()
            if window_rect:
                window_info = f"Connected to game window ({window_rect.width}x{window_rect.height})"
            else:
                window_info = "Connected to game window"
            self.update_status(window_info)
        else:
            self.update_status("Game not found")

    def update_status(self, message):
        """Update the status display"""
        self.status_var.set(message)

    def set_running_tool(self, tool_name):
        """Set which tool is currently running (mutual exclusion)"""
        if self.current_running_tool is not None and self.current_running_tool != tool_name:
            self.update_status(f"Cannot start {tool_name}: {self.current_running_tool} is already running")
            return False

        self.current_running_tool = tool_name
        self.update_unified_buttons()
        return True

    def clear_running_tool(self):
        """Clear the currently running tool"""
        self.current_running_tool = None
        self.update_unified_buttons()
    
    def update_unified_buttons(self):
        """Update the unified Start/Stop buttons based on current state"""
        if self.current_running_tool:
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            # Check if current tab can be started
            current_tab = self.get_current_tab()
            if current_tab and hasattr(current_tab, 'can_start'):
                can_start = current_tab.can_start()
            else:
                # Troubleshooting tab or other tabs without automation
                can_start = False
            
            self.btn_start.config(state=tk.NORMAL if can_start else tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
    
    def get_current_tab(self):
        """Get the currently selected tab instance"""
        try:
            selected_index = self.notebook.index(self.notebook.select())
            tabs = [
                self.arrival_tab,
                self.stellar_tab,
                self.collection_tab,
                self.heils_clicker_tab,
                self.help_tab,
                self.troubleshooting_tab
            ]
            if 0 <= selected_index < len(tabs):
                return tabs[selected_index]
        except (AttributeError, tk.TclError):
            # Tabs not fully initialized yet or notebook not ready
            pass
        return None
    
    def on_tab_changed(self, event=None):
        """Handle tab change - stop automation if running"""
        if self.current_running_tool:
            self.unified_stop()
        
        # Update button states for new tab
        self.update_unified_buttons()
    
    def unified_start(self):
        """Unified start method - starts automation for current tab"""
        current_tab = self.get_current_tab()
        if not current_tab:
            return
        
        # Stop any running automation first
        if self.current_running_tool:
            self.unified_stop()
        
        # Start the current tab's automation
        if hasattr(current_tab, 'start_automation'):
            current_tab.start_automation()
        elif hasattr(current_tab, 'start_clicking'):
            current_tab.start_clicking()
        
        # Update buttons after starting
        self.update_unified_buttons()
    
    def unified_stop(self):
        """Unified stop method - stops any running automation"""
        if not self.current_running_tool:
            return
        
        # Stop whichever tool is running
        if self.current_running_tool == "Stellar System":
            self.stellar_tab.stop_automation()
        elif self.current_running_tool == "Arrival Skill":
            self.arrival_tab.stop_automation()
        elif self.current_running_tool == "Collection Filler":
            self.collection_tab.stop_automation()
        elif self.current_running_tool == "Heils Clicker":
            self.heils_clicker_tab.stop_clicking()
        
        self.clear_running_tool()
    
    def capture_button_coordinates(self, button_name, instruction_text, success_callback):
        """
        Shared method for capturing button coordinates across all tabs.
        
        Args:
            button_name: Name of the button (e.g., "Apply", "Change", "Imprint")
            instruction_text: Custom instruction text to show in messagebox
            success_callback: Function to call with (rel_x, rel_y) on success
        """
        # Connect to game if needed
        if not self.game_connector.is_connected():
            if not self.game_connector.connect_to_game():
                self.update_status("Game not found")
                return
        
        self.update_status(f"Click {button_name} button...")
        
        # Change cursor to indicate click mode
        self.root.config(cursor="crosshair")
        
        def capture_click():
            """Capture the mouse click coordinates"""
            try:
                # Wait for mouse click
                mouse.wait(button='left')
                x, y = mouse.get_position()
                
                # Convert to window-relative coordinates
                rel_x, rel_y, success = self.game_connector.convert_to_window_coords(x, y)
                
                if success:
                    success_callback(rel_x, rel_y)
                    self.update_status(f"{button_name} set at ({rel_x}, {rel_y})")
                else:
                    self.update_status("Failed to convert coordinates")
            
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
            finally:
                # Reset cursor
                self.root.config(cursor="")
        
        # Start capture in thread
        threading.Thread(target=capture_click, daemon=True).start()
    
    def define_ocr_area(self, area_callback):
        """
        Shared method for defining OCR area across all tabs.
        
        Args:
            area_callback: Function to call with the selected area
        """
        # Use the shared area selector
        if not hasattr(self, 'area_selector'):
            from core.area_selector import AreaSelector
            self.area_selector = AreaSelector(self.root, area_callback)
        else:
            self.area_selector.callback = area_callback
        
        self.area_selector.select_area()
    
    def emergency_stop(self):
        """Emergency stop triggered by ESC key"""
        if self.current_running_tool:
            self.update_status(f"🚨 EMERGENCY STOP - {self.current_running_tool} stopped!")

            # Stop whichever tool is running
            if self.current_running_tool == "Stellar System":
                self.stellar_tab.emergency_stop()
            elif self.current_running_tool == "Arrival Skill":
                self.arrival_tab.emergency_stop()
            elif self.current_running_tool == "Collection Filler":
                self.collection_tab.emergency_stop()
            elif self.current_running_tool == "Heils Clicker":
                self.heils_clicker_tab.emergency_stop()

            self.clear_running_tool()

            # Bring window to front
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)

    def on_closing(self):
        """Clean up when closing the application"""
        keyboard.unhook_all()  # Remove all keyboard hooks
        self.root.destroy()

    def run(self):
        """Start the application"""
        self.root.mainloop()
