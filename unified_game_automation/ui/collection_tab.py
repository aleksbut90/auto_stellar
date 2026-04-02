# Collection tab UI - Simplified with Start/Stop buttons

import tkinter as tk
from tkinter import ttk
import threading
import mouse
from data.collection_data import get_collection_buttons
from automation.collection_automation import CollectionAutomation
from core.settings_manager import SettingsManager

class CollectionTab:
    def __init__(self, parent_frame, main_window):
        """Initialize the Collection tab"""
        self.parent_frame = parent_frame
        self.main_window = main_window

        # Settings manager for persistence (using unified settings.json)
        self.settings = SettingsManager(tab_section="collection")

        # Automation components
        self.automation = CollectionAutomation(
            main_window.game_connector,
            main_window.update_status
        )

        # UI state variables
        self.button_coord_vars = {}
        self.area_status_vars = {}
        
        # Create UI
        self.create_ui()
        
        # Load saved settings
        self.load_saved_settings()

    def create_ui(self):
        """Create the collection UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Content frame that can shrink (everything except buttons)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Setup status section
        status_frame = ttk.LabelFrame(content_frame, text="Setup Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.setup_status_label = ttk.Label(status_frame, text="⚠ Setup incomplete", 
                                           foreground="orange", font=("Arial", 10, "bold"))
        self.setup_status_label.pack()

        # Areas Section
        area_frame = ttk.LabelFrame(content_frame, text="Detection Areas", padding="5")
        area_frame.pack(fill=tk.X, pady=(0, 10))

        areas = [
            ("collection_tabs", "Collection Tabs"),
            ("dungeon_list", "Dungeon List"),
            ("collection_items", "Collection Items")
        ]

        for area_key, area_name in areas:
            frame = ttk.Frame(area_frame)
            frame.pack(fill=tk.X, pady=1)
            
            ttk.Button(frame, text=f"Set {area_name}", 
                      command=lambda k=area_key: self.define_area(k)).pack(side=tk.LEFT)
            
            status_label = ttk.Label(frame, text="❌", foreground="red")
            status_label.pack(side=tk.RIGHT)
            self.area_status_vars[area_key] = status_label

        # Buttons Section
        button_frame = ttk.LabelFrame(content_frame, text="Button Coordinates", padding="5")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        all_buttons = {**get_collection_buttons(), 
                      "page_2": "Page 2", "page_3": "Page 3", 
                      "page_4": "Page 4", "arrow_right": "Arrow Right"}

        for button_key, button_name in all_buttons.items():
            frame = ttk.Frame(button_frame)
            frame.pack(fill=tk.X, pady=1)

            ttk.Label(frame, text=f"{button_name}:").pack(side=tk.LEFT)
            
            coord_var = tk.StringVar(value="Not set")
            self.button_coord_vars[button_key] = coord_var
            ttk.Label(frame, textvariable=coord_var, foreground="blue", 
                     font=("Arial", 8)).pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Button(frame, text="Set", 
                      command=lambda k=button_key, n=button_name: self.set_button_coordinate(k, n)).pack(side=tk.RIGHT)

        # Delay Settings
        delay_frame = ttk.LabelFrame(content_frame, text="Delay Settings", padding="5")
        delay_frame.pack(fill=tk.X, pady=(0, 10))
        
        delay_input_frame = ttk.Frame(delay_frame)
        delay_input_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(delay_input_frame, text="Delay (milliseconds):").pack(side=tk.LEFT)
        
        self.delay_var = tk.IntVar(value=1000)  # Default 1000ms (1 second)
        delay_spinbox = ttk.Spinbox(delay_input_frame, from_=0, to=10000, increment=100, 
                                   textvariable=self.delay_var, width=8,
                                   command=self.update_delay)
        delay_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        # Bind to variable changes to catch manual typing
        self.delay_var.trace('w', lambda *args: self.update_delay())

    def load_saved_settings(self):
        """Load settings from file and update UI"""
        # Load delay (convert from old multiplier format if needed)
        delay_ms = self.settings.get_delay_ms()
        self.delay_var.set(delay_ms)
        self.automation.set_delay_ms(delay_ms)
        
        # Load and apply areas
        areas = self.settings.get_all_areas()
        for area_name, coords in areas.items():
            if coords:
                if area_name == "collection_tabs":
                    self.automation.set_collection_tabs_area(coords)
                elif area_name == "dungeon_list":
                    self.automation.set_dungeon_list_area(coords)
                elif area_name == "collection_items":
                    self.automation.set_collection_items_area(coords)
                
                # Update status
                if area_name in self.area_status_vars:
                    self.area_status_vars[area_name].config(text="✓", foreground="green")
        
        # Load and apply buttons
        buttons = self.settings.get_all_buttons()
        for button_name, coords in buttons.items():
            if coords:
                # Set in automation
                if button_name == "auto_refill":
                    self.automation.set_auto_refill_button(coords)
                elif button_name == "register":
                    self.automation.set_register_button(coords)
                elif button_name == "yes":
                    self.automation.set_yes_button(coords)
                elif button_name == "page_2":
                    self.automation.set_page_2_button(coords)
                elif button_name == "page_3":
                    self.automation.set_page_3_button(coords)
                elif button_name == "page_4":
                    self.automation.set_page_4_button(coords)
                elif button_name == "arrow_right":
                    self.automation.set_arrow_right_button(coords)
                
                # Update UI
                if button_name in self.button_coord_vars:
                    self.button_coord_vars[button_name].set(f"({coords[0]}, {coords[1]})")
        
        self.update_setup_status()

    def update_setup_status(self):
        """Update the setup status display"""
        if self.settings.is_setup_complete():
            self.setup_status_label.config(text="✓ Ready", foreground="green")
        else:
            self.setup_status_label.config(text="⚠ Setup incomplete", foreground="orange")

    def define_area(self, area_name, callback=None):
        """Define a specific area"""
        def area_callback(area):
            """Callback when area is selected"""
            # Save to settings
            self.settings.set_area(area_name, area)
            
            # Set in automation
            if area_name == "collection_tabs":
                self.automation.set_collection_tabs_area(area)
            elif area_name == "dungeon_list":
                self.automation.set_dungeon_list_area(area)
            elif area_name == "collection_items":
                self.automation.set_collection_items_area(area)
            
            # Update UI
            if area_name in self.area_status_vars:
                self.area_status_vars[area_name].config(text="✓", foreground="green")
            
            self.main_window.update_status(f"✓ {area_name.replace('_', ' ').title()} area saved")
            self.update_setup_status()
            self.main_window.update_unified_buttons()
            
            if callback:
                callback()

        # Use the shared area selector from main window
        self.main_window.define_ocr_area(area_callback)

    def set_button_coordinate(self, button_key, button_name, callback=None):
        """Set coordinates for an action button"""
        # Connect to game if needed
        if not self.main_window.game_connector.is_connected():
            if not self.main_window.game_connector.connect_to_game():
                self.main_window.update_status("Game not found")
                return

        self.main_window.update_status(f"Click on '{button_name}' button...")

        # Change cursor to indicate click mode
        self.main_window.root.config(cursor="crosshair")

        def capture_click():
            """Capture the mouse click coordinates"""
            try:
                # Wait for mouse click
                mouse.wait(button='left')
                x, y = mouse.get_position()

                # Convert to window-relative coordinates
                rel_x, rel_y, success = self.main_window.game_connector.convert_to_window_coords(x, y)

                if success:
                    # Save to settings
                    self.settings.set_button(button_key, (rel_x, rel_y))
                    
                    # Set coordinates in automation based on button type
                    if button_key == "auto_refill":
                        self.automation.set_auto_refill_button((rel_x, rel_y))
                    elif button_key == "register":
                        self.automation.set_register_button((rel_x, rel_y))
                    elif button_key == "yes":
                        self.automation.set_yes_button((rel_x, rel_y))
                    elif button_key == "page_2":
                        self.automation.set_page_2_button((rel_x, rel_y))
                    elif button_key == "page_3":
                        self.automation.set_page_3_button((rel_x, rel_y))
                    elif button_key == "page_4":
                        self.automation.set_page_4_button((rel_x, rel_y))
                    elif button_key == "arrow_right":
                        self.automation.set_arrow_right_button((rel_x, rel_y))
                    
                    # Update UI
                    if button_key in self.button_coord_vars:
                        self.button_coord_vars[button_key].set(f"({rel_x}, {rel_y})")
                    
                    self.main_window.update_status(f"✓ {button_name} button saved")
                    self.update_setup_status()
                    self.main_window.update_unified_buttons()
                    
                    # Call callback if provided
                    if callback:
                        callback()
                else:
                    self.main_window.update_status("Failed to convert coordinates")

            except Exception as e:
                self.main_window.update_status(f"Error: {str(e)}")
            finally:
                # Reset cursor
                self.main_window.root.config(cursor="")

        # Start capture in thread
        threading.Thread(target=capture_click, daemon=True).start()

    def update_delay(self):
        """Update the delay in automation"""
        try:
            delay_ms = self.delay_var.get()
            self.automation.set_delay_ms(delay_ms)
            self.settings.set_delay_ms(delay_ms)
            self.main_window.update_status(f"Delay: {delay_ms}ms")
        except Exception as e:
            pass

    def can_start(self):
        """Check if automation can be started (all required settings are configured)"""
        return self.settings.is_setup_complete()
    
    def start_automation(self):
        """Start the collection automation"""
        # Check if automation is already running using main window's tracking
        if not self.main_window.set_running_tool("Collection Filler"):
            return

        # Start automation
        if not self.automation.start():
            # Failed to start, clear running tool
            self.main_window.clear_running_tool()

    def stop_automation(self):
        """Stop the collection automation"""
        self.automation.stop()
        self.main_window.clear_running_tool()

    def emergency_stop(self):
        """Emergency stop the automation"""
        self.automation.stop()
        self.main_window.clear_running_tool()