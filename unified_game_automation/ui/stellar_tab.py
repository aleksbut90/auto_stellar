# Stellar System tab UI
# Ported from main.py stellar system functionality

import tkinter as tk
from tkinter import ttk, messagebox
from data.stellar_data import get_stellar_options
from automation.stellar_automation import StellarAutomation
from core.settings_manager import SettingsManager

class StellarTab:
    def __init__(self, parent_frame, main_window):
        """Initialize the Stellar System tab"""
        self.parent_frame = parent_frame
        self.main_window = main_window

        # Settings manager for persistence (using unified settings.json)
        self.settings = SettingsManager(tab_section="stellar")

        # Automation components
        self.automation = StellarAutomation(
            main_window.game_connector,
            main_window.ocr_engine,
            main_window.update_status
        )

        # UI state
        self.area = None
        self.imprint_button_coords = None
        self.stat_entries = []  # List of (stat_name, min_value_entry, frame) tuples

        # Create UI
        self.create_ui()
        
        # Load saved settings
        self.load_saved_settings()

    def create_ui(self):
        """Create the stellar system UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Content frame that can shrink (everything except buttons)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Button coordinates section
        coord_frame = ttk.LabelFrame(content_frame, text="Button Coordinates", padding="5")
        coord_frame.pack(fill=tk.X, pady=(0, 10))

        # Imprint button coordinates
        imprint_frame = ttk.Frame(coord_frame)
        imprint_frame.pack(fill=tk.X, pady=2)

        ttk.Label(imprint_frame, text="Imprint Button:").pack(side=tk.LEFT)
        self.imprint_coord_var = tk.StringVar(value="Not set")
        ttk.Label(imprint_frame, textvariable=self.imprint_coord_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(imprint_frame, text="Set Imprint Button", command=self.set_imprint_button).pack(side=tk.RIGHT)

        # Option selection section
        option_frame = ttk.LabelFrame(content_frame, text="Stat Configuration (OR Logic)", padding="5")
        option_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Add stat button and dropdown
        add_stat_frame = ttk.Frame(option_frame)
        add_stat_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(add_stat_frame, text="Select stat:").pack(side=tk.LEFT)
        stellar_options = get_stellar_options() + ["Custom"]
        self.combo_stat_selector = ttk.Combobox(add_stat_frame, values=stellar_options, state="readonly", width=20)
        self.combo_stat_selector.pack(side=tk.LEFT, padx=(5, 5))
        self.combo_stat_selector.bind("<<ComboboxSelected>>", self.on_stat_selected)
        ttk.Button(add_stat_frame, text="Add Stat", command=self.add_stat).pack(side=tk.LEFT)
        
        # Custom stat input fields (hidden by default)
        self.custom_frame = ttk.Frame(add_stat_frame)
        self.custom_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(self.custom_frame, text="Custom Name:").pack(side=tk.LEFT)
        self.custom_name_entry = ttk.Entry(self.custom_frame, width=15)
        self.custom_name_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Label(self.custom_frame, text="Min Value:").pack(side=tk.LEFT)
        self.custom_value_entry = ttk.Entry(self.custom_frame, width=8)
        self.custom_value_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        self.custom_frame.pack_forget()  # Hide initially
        
        # Container for stat entries with scrollbar
        # Store so we can insert the custom stat UI before the list container
        self.stats_container_frame = ttk.Frame(option_frame)
        self.stats_container_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrollable stat list
        canvas = tk.Canvas(self.stats_container_frame, height=150)
        scrollbar = ttk.Scrollbar(self.stats_container_frame, orient="vertical", command=canvas.yview)
        self.stats_scrollable_frame = ttk.Frame(canvas)
        
        self.stats_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.stats_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        

        # Visual effect delay section
        effect_frame = ttk.LabelFrame(content_frame, text="Visual Effect Settings", padding="5")
        effect_frame.pack(fill=tk.X, pady=(0, 10))


        # Delay setting
        delay_frame = ttk.Frame(effect_frame)
        delay_frame.pack(fill=tk.X, pady=2)

        ttk.Label(delay_frame, text="Effect clear delay:").pack(side=tk.LEFT)
        self.entry_effect_delay = ttk.Entry(delay_frame, width=8)
        self.entry_effect_delay.pack(side=tk.LEFT, padx=(5, 0))
        self.entry_effect_delay.insert(0, "1000")  # Default 1000ms = 1 second
        self.entry_effect_delay.bind("<KeyRelease>", lambda e: self.save_effect_delay())
        ttk.Label(delay_frame, text="ms", font=("Arial", 8), foreground="gray").pack(side=tk.LEFT, padx=(5, 0))

        # Area definition
        area_frame = ttk.Frame(content_frame)
        area_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_define_area = ttk.Button(area_frame, text="Define Area", command=self.define_area)
        self.btn_define_area.pack()

    def add_stat(self):
        """Add a stat with its minimum value to the list"""
        selected = self.combo_stat_selector.get().strip()
        if not selected:
            self.main_window.update_status("Select a stat first")
            return
        
        # Handle custom stat
        if selected == "Custom":
            stat_name = self.custom_name_entry.get().strip()
            min_value = self.custom_value_entry.get().strip()
            if not stat_name:
                self.main_window.update_status("Enter custom stat name")
                return
            if not min_value:
                self.main_window.update_status("Enter custom stat value")
                return
        else:
            stat_name = selected
            min_value = ""
        
        # Check if stat already added
        for existing_stat, _, _ in self.stat_entries:
            if existing_stat == stat_name:
                self.main_window.update_status(f"{stat_name} already added")
                return
        
        # Create frame for this stat entry
        stat_frame = ttk.Frame(self.stats_scrollable_frame)
        stat_frame.pack(fill=tk.X, pady=2)
        
        # Stat name label
        ttk.Label(stat_frame, text=stat_name, width=20).pack(side=tk.LEFT, padx=(0, 5))
        
        # Min value entry
        ttk.Label(stat_frame, text="Min:").pack(side=tk.LEFT)
        min_value_entry = ttk.Entry(stat_frame, width=8)
        min_value_entry.pack(side=tk.LEFT, padx=(2, 5))
        if min_value:  # Pre-fill if custom stat had a value
            min_value_entry.insert(0, min_value)
        
        # Remove button (use default parameter trick to avoid closure issues)
        remove_btn = ttk.Button(stat_frame, text="Remove", 
                               command=lambda s=stat_name, f=stat_frame: self.remove_stat(s, f))
        remove_btn.pack(side=tk.LEFT)
        
        # Store the entry
        self.stat_entries.append((stat_name, min_value_entry, stat_frame))
        
        # Save stat entries to settings
        self.save_stat_entries()
        
        # Clear selection and hide custom fields
        self.combo_stat_selector.set('')
        self.custom_frame.pack_forget()
        self.custom_name_entry.delete(0, tk.END)
        self.custom_value_entry.delete(0, tk.END)
        
        # Update unified buttons
        self.main_window.update_unified_buttons()
    
    def on_stat_selected(self, event=None):
        """Handle stat selection - show custom fields if Custom is selected"""
        selected = self.combo_stat_selector.get()
        if selected == "Custom":
            # Show custom inputs just below the selector row
            self.custom_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.custom_frame.pack_forget()
    
    def remove_stat(self, stat_name, stat_frame):
        """Remove a stat from the list"""
        # Remove from list
        self.stat_entries = [(name, entry, frame) for name, entry, frame in self.stat_entries 
                            if name != stat_name]
        # Destroy the frame
        stat_frame.destroy()
        # Save updated stat entries
        self.save_stat_entries()
        # Update unified buttons
        self.main_window.update_unified_buttons()

    def set_imprint_button(self):
        """Set the imprint button coordinates"""
        def on_success(rel_x, rel_y):
            self.imprint_button_coords = (rel_x, rel_y)
            self.automation.set_imprint_button(self.imprint_button_coords)
            self.imprint_coord_var.set(f"({rel_x}, {rel_y})")
            # Save to settings
            self.settings.set_button("imprint_button", (rel_x, rel_y))
        
        self.main_window.capture_button_coordinates(
            "Imprint",
            "Click on the 'Imprint' button in the game window.\n"
            "The coordinates will be captured automatically.",
            on_success
        )

    def can_start(self):
        """Check if automation can be started (all required settings are configured)"""
        return self.area is not None and len(self.stat_entries) > 0
    
    def define_area(self):
        """Define the OCR area using the shared area selector"""
        def area_callback(area):
            """Callback when area is selected"""
            self.area = area
            self.automation.set_area(area)
            self.main_window.update_status(f"Area defined: {area}")
            # Save to settings
            self.settings.set_area("ocr_area", area)
            self.main_window.update_unified_buttons()
        
        self.main_window.define_ocr_area(area_callback)

    def start_automation(self):
        """Start the stellar automation"""
        # Check if another tool is running
        if not self.main_window.set_running_tool("Stellar System"):
            return

        # Get configuration - stats with individual minimum values
        if not self.stat_entries:
            messagebox.showwarning("Missing Stats", "Please add at least one stat.")
            self.main_window.clear_running_tool()
            return
        
        # Build stat configuration dictionary: {stat_name: min_value}
        stat_config = {}
        for stat_name, min_value_entry, _ in self.stat_entries:
            min_value = min_value_entry.get().strip()
            stat_config[stat_name] = min_value
        
        effect_delay = self.entry_effect_delay.get().strip()

        # Validate effect delay
        try:
            effect_delay_ms = int(effect_delay) if effect_delay else 1000
            if effect_delay_ms < 0:
                effect_delay_ms = 1000
        except ValueError:
            effect_delay_ms = 1000

        # Set the effect delay in automation
        self.automation.set_effect_delay(effect_delay_ms)

        # Start automation with stat configuration
        if self.automation.start(stat_config):
            stats_display = " OR ".join([f"{name}(≥{val})" if val else name 
                                        for name, val in stat_config.items()])
            self.main_window.update_status(f"Stellar automation started - looking for: {stats_display}")
        else:
            self.main_window.clear_running_tool()

    def stop_automation(self):
        """Stop the stellar automation"""
        self.automation.stop()
        self.main_window.clear_running_tool()
        self.main_window.update_status("Stellar automation stopped")

    def save_effect_delay(self):
        """Save effect delay to settings"""
        try:
            delay = int(self.entry_effect_delay.get().strip() or "1000")
            self.settings.set_custom("effect_delay_ms", delay)
        except Exception:
            pass
    
    def save_stat_entries(self):
        """Save stat entries to settings"""
        stat_list = []
        for stat_name, min_value_entry, _ in self.stat_entries:
            min_value = min_value_entry.get().strip()
            stat_list.append({"name": stat_name, "min_value": min_value})
        self.settings.set_custom("stat_entries", stat_list)
    
    def load_saved_settings(self):
        """Load saved settings from file"""
        # Load OCR area
        area = self.settings.get_area("ocr_area")
        if area:
            self.area = area
            self.automation.set_area(area)
        
        # Load imprint button
        imprint_coords = self.settings.get_button("imprint_button")
        if imprint_coords:
            self.imprint_button_coords = imprint_coords
            self.automation.set_imprint_button(imprint_coords)
            self.imprint_coord_var.set(f"({imprint_coords[0]}, {imprint_coords[1]})")
        
        # Load effect delay
        effect_delay = self.settings.get_custom("effect_delay_ms", 1000)
        self.entry_effect_delay.delete(0, tk.END)
        self.entry_effect_delay.insert(0, str(effect_delay))
        
        # Load stat entries
        stat_entries_data = self.settings.get_custom("stat_entries", [])
        for stat_data in stat_entries_data:
            stat_name = stat_data.get("name")
            min_value = stat_data.get("min_value", "")
            if stat_name:
                # Create frame for this stat entry
                stat_frame = ttk.Frame(self.stats_scrollable_frame)
                stat_frame.pack(fill=tk.X, pady=2)
                
                # Stat name label
                ttk.Label(stat_frame, text=stat_name, width=20).pack(side=tk.LEFT, padx=(0, 5))
                
                # Min value entry
                ttk.Label(stat_frame, text="Min:").pack(side=tk.LEFT)
                min_value_entry = ttk.Entry(stat_frame, width=8)
                min_value_entry.pack(side=tk.LEFT, padx=(2, 5))
                if min_value:
                    min_value_entry.insert(0, min_value)
                
                # Remove button (use default parameter trick to avoid closure issues)
                remove_btn = ttk.Button(stat_frame, text="Remove",
                                       command=lambda s=stat_name, f=stat_frame: self.remove_stat(s, f))
                remove_btn.pack(side=tk.LEFT)
                
                # Store the entry
                self.stat_entries.append((stat_name, min_value_entry, stat_frame))

    def emergency_stop(self):
        """Emergency stop the automation"""
        self.automation.emergency_stop()
        self.main_window.clear_running_tool()

