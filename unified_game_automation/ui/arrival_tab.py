# Arrival Skill tab UI
# Ported from arrival_skill_ocr/ui.py

import tkinter as tk
from tkinter import ttk, messagebox
import re
from data.arrival_data import get_offensive_skills, get_defensive_skills, get_stat_variations
from automation.arrival_automation import ArrivalAutomation
from core.settings_manager import SettingsManager

# Stats whose values cannot be reliably read (UI collision) and require grade-based detection
VALUE_COLLISION_STATS = {
    "Arrival Skill Cool Time decreased."
}

# Grade options to choose from when value reading is unreliable
GRADE_OPTIONS = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6"]

class ArrivalTab:
    def __init__(self, parent_frame, main_window):
        """Initialize the Arrival Skill tab"""
        self.parent_frame = parent_frame
        self.main_window = main_window

        # Settings manager for persistence (using unified settings.json)
        self.settings = SettingsManager(tab_section="arrival")

        # Automation components
        self.automation = ArrivalAutomation(
            main_window.game_connector,
            main_window.ocr_engine,
            main_window.update_status
        )

        # UI state
        self.area = None
        self.grade_area = None
        self.apply_button_coords = None
        self.change_button_coords = None
        self.offensive_stat_entries = []  # List of (stat_name, min_value_entry, frame) tuples
        self.defensive_stat_entries = []  # List of (stat_name, min_value_entry, frame) tuples
        self.stats_area_status_var = None
        self.grade_area_status_var = None

        # Create UI
        self.create_ui()
        
        # Load saved settings
        self.load_saved_settings()

    def create_ui(self):
        """Create the arrival skill UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Content frame that can shrink (everything except buttons)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Button coordinates section
        coord_frame = ttk.LabelFrame(content_frame, text="Button Coordinates", padding="5")
        coord_frame.pack(fill=tk.X, pady=(0, 10))

        # Apply button coordinates
        apply_frame = ttk.Frame(coord_frame)
        apply_frame.pack(fill=tk.X, pady=2)

        ttk.Label(apply_frame, text="Apply Button:").pack(side=tk.LEFT)
        self.apply_coord_var = tk.StringVar(value="Not set")
        ttk.Label(apply_frame, textvariable=self.apply_coord_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(apply_frame, text="Set Apply Button", command=self.set_apply_button).pack(side=tk.LEFT)

        # Change button coordinates
        change_frame = ttk.Frame(coord_frame)
        change_frame.pack(fill=tk.X, pady=2)

        ttk.Label(change_frame, text="Change Button:").pack(side=tk.LEFT)
        self.change_coord_var = tk.StringVar(value="Not set")
        ttk.Label(change_frame, textvariable=self.change_coord_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(change_frame, text="Set Change Button", command=self.set_change_button).pack(side=tk.LEFT)

        # Area definition
        area_frame = ttk.LabelFrame(content_frame, text="OCR Areas", padding="5")
        area_frame.pack(fill=tk.X, pady=(0, 10))

        # Stats area row
        stats_area_row = ttk.Frame(area_frame)
        stats_area_row.pack(fill=tk.X, pady=2)

        self.btn_define_area = ttk.Button(stats_area_row, text="Define OCR Area (Stats)", command=self.define_area)
        self.btn_define_area.pack(side=tk.LEFT)

        self.stats_area_status_var = ttk.Label(stats_area_row, text="❌ Not set", foreground="orange")
        self.stats_area_status_var.pack(side=tk.LEFT, padx=(10, 0))

        # Grade area row
        grade_area_row = ttk.Frame(area_frame)
        grade_area_row.pack(fill=tk.X, pady=2)

        self.btn_define_grade_area = ttk.Button(grade_area_row, text="Define OCR Area (Grade)", command=self.define_grade_area)
        self.btn_define_grade_area.pack(side=tk.LEFT)

        # Info button for Grade OCR area
        info_button = ttk.Button(grade_area_row, text="ℹ️", width=3, command=self.show_grade_area_info)
        info_button.pack(side=tk.LEFT, padx=(5, 0))

        self.grade_area_status_var = ttk.Label(grade_area_row, text="Optional: Not set (Required for 'Arrival Skill Cool Time Decreased')", foreground="gray")
        self.grade_area_status_var.pack(side=tk.LEFT, padx=(10, 0))

        # Stat selection section
        stats_frame = ttk.LabelFrame(content_frame, text="Desired Stats", padding="5")
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Logic selection (AND/OR between offensive and defensive)
        logic_frame = ttk.Frame(stats_frame)
        logic_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(logic_frame, text="Logic between Offensive and Defensive:").pack(anchor=tk.W, pady=(0, 3))
        self.logic_var = tk.StringVar(value="OR")  # Default to OR
        ttk.Radiobutton(logic_frame, text="OR (either category can match)", variable=self.logic_var, value="OR").pack(anchor=tk.W, padx=(20, 0))
        ttk.Radiobutton(logic_frame, text="AND (both categories must match)", variable=self.logic_var, value="AND").pack(anchor=tk.W, padx=(20, 0))

        # Offensive stats section
        off_stats_frame = ttk.LabelFrame(stats_frame, text="Offensive Stats (OR Logic)", padding="5")
        off_stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Add offensive stat button and dropdown
        add_off_stat_frame = ttk.Frame(off_stats_frame)
        add_off_stat_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(add_off_stat_frame, text="Select stat:").pack(side=tk.LEFT)
        off_skills = get_offensive_skills() + ["Custom"]
        self.combo_off_stat_selector = ttk.Combobox(add_off_stat_frame, values=off_skills, state="readonly", width=20)
        self.combo_off_stat_selector.pack(side=tk.LEFT, padx=(5, 5))
        self.combo_off_stat_selector.bind("<<ComboboxSelected>>", self.on_off_stat_selected)
        ttk.Button(add_off_stat_frame, text="Add Stat", command=self.add_offensive_stat).pack(side=tk.LEFT)
        
        # Custom offensive stat input fields (hidden by default)
        self.custom_off_frame = ttk.Frame(add_off_stat_frame)
        ttk.Label(self.custom_off_frame, text="Custom Name:").pack(side=tk.LEFT)
        self.custom_off_name_entry = ttk.Entry(self.custom_off_frame, width=15)
        self.custom_off_name_entry.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Label(self.custom_off_frame, text="Min Value:").pack(side=tk.LEFT)
        self.custom_off_value_entry = ttk.Entry(self.custom_off_frame, width=8)
        self.custom_off_value_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.custom_off_frame.pack_forget()  # Hide initially
        
        # Container for offensive stat entries with scrollbar
        off_stats_container_frame = ttk.Frame(off_stats_frame)
        off_stats_container_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrollable offensive stat list
        off_canvas = tk.Canvas(off_stats_container_frame, height=100)
        off_scrollbar = ttk.Scrollbar(off_stats_container_frame, orient="vertical", command=off_canvas.yview)
        self.off_stats_scrollable_frame = ttk.Frame(off_canvas)
        
        self.off_stats_scrollable_frame.bind(
            "<Configure>",
            lambda e: off_canvas.configure(scrollregion=off_canvas.bbox("all"))
        )
        
        off_canvas.create_window((0, 0), window=self.off_stats_scrollable_frame, anchor="nw")
        off_canvas.configure(yscrollcommand=off_scrollbar.set)
        
        off_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        off_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Defensive stats section
        def_stats_frame = ttk.LabelFrame(stats_frame, text="Defensive Stats (OR Logic)", padding="5")
        def_stats_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Add defensive stat button and dropdown
        add_def_stat_frame = ttk.Frame(def_stats_frame)
        add_def_stat_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(add_def_stat_frame, text="Select stat:").pack(side=tk.LEFT)
        def_skills = get_defensive_skills() + ["Custom"]
        self.combo_def_stat_selector = ttk.Combobox(add_def_stat_frame, values=def_skills, state="readonly", width=20)
        self.combo_def_stat_selector.pack(side=tk.LEFT, padx=(5, 5))
        self.combo_def_stat_selector.bind("<<ComboboxSelected>>", self.on_def_stat_selected)
        ttk.Button(add_def_stat_frame, text="Add Stat", command=self.add_defensive_stat).pack(side=tk.LEFT)
        
        # Custom defensive stat input fields (hidden by default)
        self.custom_def_frame = ttk.Frame(add_def_stat_frame)
        ttk.Label(self.custom_def_frame, text="Custom Name:").pack(side=tk.LEFT)
        self.custom_def_name_entry = ttk.Entry(self.custom_def_frame, width=15)
        self.custom_def_name_entry.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Label(self.custom_def_frame, text="Min Value:").pack(side=tk.LEFT)
        self.custom_def_value_entry = ttk.Entry(self.custom_def_frame, width=8)
        self.custom_def_value_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.custom_def_frame.pack_forget()  # Hide initially
        
        # Container for defensive stat entries with scrollbar
        def_stats_container_frame = ttk.Frame(def_stats_frame)
        def_stats_container_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrollable defensive stat list
        def_canvas = tk.Canvas(def_stats_container_frame, height=100)
        def_scrollbar = ttk.Scrollbar(def_stats_container_frame, orient="vertical", command=def_canvas.yview)
        self.def_stats_scrollable_frame = ttk.Frame(def_canvas)
        
        self.def_stats_scrollable_frame.bind(
            "<Configure>",
            lambda e: def_canvas.configure(scrollregion=def_canvas.bbox("all"))
        )
        
        def_canvas.create_window((0, 0), window=self.def_stats_scrollable_frame, anchor="nw")
        def_canvas.configure(yscrollcommand=def_scrollbar.set)
        
        def_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        def_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def set_apply_button(self):
        """Set the apply button coordinates"""
        def on_success(rel_x, rel_y):
            self.apply_button_coords = (rel_x, rel_y)
            self.automation.set_apply_button(self.apply_button_coords)
            self.apply_coord_var.set(f"({rel_x}, {rel_y})")
            # Save to settings
            self.settings.set_button("apply_button", (rel_x, rel_y))
        
        self.main_window.capture_button_coordinates(
            "Apply",
            "Click on the 'Apply' button in the game window.\n"
            "The coordinates will be captured automatically.",
            on_success
        )

    def set_change_button(self):
        """Set the change button coordinates"""
        def on_success(rel_x, rel_y):
            self.change_button_coords = (rel_x, rel_y)
            self.automation.set_change_button(self.change_button_coords)
            self.change_coord_var.set(f"({rel_x}, {rel_y})")
            # Save to settings
            self.settings.set_button("change_button", (rel_x, rel_y))
        
        self.main_window.capture_button_coordinates(
            "Change",
            "Click on the 'Change' button in the game window.\n"
            "The coordinates will be captured automatically.",
            on_success
        )

    def can_start(self):
        """Check if automation can be started (all required settings are configured)"""
        return self.area is not None and (len(self.offensive_stat_entries) > 0 or len(self.defensive_stat_entries) > 0)
    
    def define_area(self):
        """Define the OCR area using the shared area selector"""
        def area_callback(area):
            """Callback when area is selected"""
            self.area = area
            self.automation.set_area(area)
            self.main_window.update_status(f"OCR area defined: {area}")
            if self.stats_area_status_var:
                self.stats_area_status_var.config(text="✓ Set", foreground="green")
            # Save to settings
            self.settings.set_area("stats_area", area)
            self.main_window.update_unified_buttons()
        
        self.main_window.define_ocr_area(area_callback)

    def define_grade_area(self):
        """Define the OCR area for grade detection"""
        def area_callback(area):
            self.grade_area = area
            self.automation.set_grade_area(area)
            if self.grade_area_status_var:
                self.grade_area_status_var.config(text="✓ Grade area set", foreground="green")
            self.main_window.update_status(f"Grade OCR area defined: {area}")
            # Save to settings
            self.settings.set_area("grade_area", area)

        self.main_window.define_ocr_area(area_callback)

    def on_off_stat_selected(self, event=None):
        """Handle offensive stat selection - show custom fields if Custom is selected"""
        selected = self.combo_off_stat_selector.get()
        if selected == "Custom":
            self.custom_off_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.custom_off_frame.pack_forget()
            # Update variations for regular stats
            if selected:
                variations = get_stat_variations(selected)
                if variations:
                    self.combo_off_stat_selector.set(selected)  # Keep the selected stat

    def on_def_stat_selected(self, event=None):
        """Handle defensive stat selection - show custom fields if Custom is selected"""
        selected = self.combo_def_stat_selector.get()
        if selected == "Custom":
            self.custom_def_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.custom_def_frame.pack_forget()
            # Update variations for regular stats
            if selected:
                variations = get_stat_variations(selected)
                if variations:
                    self.combo_def_stat_selector.set(selected)  # Keep the selected stat

    def add_offensive_stat(self):
        """Add an offensive stat with its minimum value to the list"""
        selected = self.combo_off_stat_selector.get().strip()
        if not selected:
            self.main_window.update_status("Select an offensive stat first")
            return
        
        # Handle custom stat
        if selected == "Custom":
            stat_name = self.custom_off_name_entry.get().strip()
            custom_value = self.custom_off_value_entry.get().strip()
            if not stat_name:
                self.main_window.update_status("Enter custom stat name")
                return
            if not custom_value:
                self.main_window.update_status("Enter custom stat value")
                return
        else:
            stat_name = selected
            custom_value = None
        
        # Check if stat already added
        for existing_stat, _, _ in self.offensive_stat_entries:
            if existing_stat == stat_name:
                self.main_window.update_status(f"{stat_name} already added")
                return
        
        # Create frame for this stat entry
        stat_frame = ttk.Frame(self.off_stats_scrollable_frame)
        stat_frame.pack(fill=tk.X, pady=2)
        
        # Stat name label
        ttk.Label(stat_frame, text=stat_name, width=20).pack(side=tk.LEFT, padx=(0, 5))
        
        # Min value dropdown or entry
        ttk.Label(stat_frame, text="Min:").pack(side=tk.LEFT)
        min_var = tk.StringVar()
        if custom_value is not None:
            # Custom stat - use entry field
            min_var.set(custom_value)
            min_value_widget = ttk.Label(stat_frame, text=custom_value, width=8)
            min_value_widget.pack(side=tk.LEFT, padx=(2, 5))
        elif stat_name in VALUE_COLLISION_STATS:
            variations = GRADE_OPTIONS
            min_value_dropdown = ttk.Combobox(stat_frame, textvariable=min_var, values=variations, state="readonly", width=8)
            min_value_dropdown.pack(side=tk.LEFT, padx=(2, 5))
            if variations:
                min_var.set(variations[0])  # Select first variation by default
        else:
            variations = get_stat_variations(stat_name)
            min_value_dropdown = ttk.Combobox(stat_frame, textvariable=min_var, values=variations, state="readonly", width=8)
            min_value_dropdown.pack(side=tk.LEFT, padx=(2, 5))
            if variations:
                min_var.set(variations[0])  # Select first variation by default
        
        # Remove button
        remove_btn = ttk.Button(stat_frame, text="Remove",
                               command=lambda: self.remove_offensive_stat(stat_name, stat_frame))
        remove_btn.pack(side=tk.LEFT)
        
        # Store the entry
        self.offensive_stat_entries.append((stat_name, min_var, stat_frame))
        
        # Save stat entries to settings
        self.save_stat_entries()
        
        # Clear selection and hide custom fields
        self.combo_off_stat_selector.set('')
        self.custom_off_frame.pack_forget()
        self.custom_off_name_entry.delete(0, tk.END)
        self.custom_off_value_entry.delete(0, tk.END)
        
        # Update unified buttons
        self.main_window.update_unified_buttons()
    
    def add_defensive_stat(self):
        """Add a defensive stat with its minimum value to the list"""
        selected = self.combo_def_stat_selector.get().strip()
        if not selected:
            self.main_window.update_status("Select a defensive stat first")
            return
        
        # Handle custom stat
        if selected == "Custom":
            stat_name = self.custom_def_name_entry.get().strip()
            custom_value = self.custom_def_value_entry.get().strip()
            if not stat_name:
                self.main_window.update_status("Enter custom stat name")
                return
            if not custom_value:
                self.main_window.update_status("Enter custom stat value")
                return
        else:
            stat_name = selected
            custom_value = None
        
        # Check if stat already added
        for existing_stat, _, _ in self.defensive_stat_entries:
            if existing_stat == stat_name:
                self.main_window.update_status(f"{stat_name} already added")
                return
        
        # Create frame for this stat entry
        stat_frame = ttk.Frame(self.def_stats_scrollable_frame)
        stat_frame.pack(fill=tk.X, pady=2)
        
        # Stat name label
        ttk.Label(stat_frame, text=stat_name, width=20).pack(side=tk.LEFT, padx=(0, 5))
        
        # Min value dropdown or entry
        ttk.Label(stat_frame, text="Min:").pack(side=tk.LEFT)
        min_var = tk.StringVar()
        if custom_value is not None:
            # Custom stat - use entry field
            min_var.set(custom_value)
            min_value_widget = ttk.Label(stat_frame, text=custom_value, width=8)
            min_value_widget.pack(side=tk.LEFT, padx=(2, 5))
        elif stat_name in VALUE_COLLISION_STATS:
            variations = GRADE_OPTIONS
            min_value_dropdown = ttk.Combobox(stat_frame, textvariable=min_var, values=variations, state="readonly", width=8)
            min_value_dropdown.pack(side=tk.LEFT, padx=(2, 5))
            if variations:
                min_var.set(variations[0])  # Select first variation by default
        else:
            variations = get_stat_variations(stat_name)
            min_value_dropdown = ttk.Combobox(stat_frame, textvariable=min_var, values=variations, state="readonly", width=8)
            min_value_dropdown.pack(side=tk.LEFT, padx=(2, 5))
            if variations:
                min_var.set(variations[0])  # Select first variation by default
        
        # Remove button
        remove_btn = ttk.Button(stat_frame, text="Remove",
                               command=lambda: self.remove_defensive_stat(stat_name, stat_frame))
        remove_btn.pack(side=tk.LEFT)
        
        # Store the entry
        self.defensive_stat_entries.append((stat_name, min_var, stat_frame))
        
        # Save stat entries to settings
        self.save_stat_entries()
        
        # Clear selection and hide custom fields
        self.combo_def_stat_selector.set('')
        self.custom_def_frame.pack_forget()
        self.custom_def_name_entry.delete(0, tk.END)
        self.custom_def_value_entry.delete(0, tk.END)
        
        # Update unified buttons
        self.main_window.update_unified_buttons()
    
    def remove_offensive_stat(self, stat_name, stat_frame):
        """Remove an offensive stat from the list"""
        # Remove from list
        self.offensive_stat_entries = [(name, var, frame) for name, var, frame in self.offensive_stat_entries
                                     if name != stat_name]
        # Destroy the frame
        stat_frame.destroy()
        # Save updated stat entries
        self.save_stat_entries()
        # Update unified buttons
        self.main_window.update_unified_buttons()

    def remove_defensive_stat(self, stat_name, stat_frame):
        """Remove a defensive stat from the list"""
        # Remove from list
        self.defensive_stat_entries = [(name, var, frame) for name, var, frame in self.defensive_stat_entries
                                     if name != stat_name]
        # Destroy the frame
        stat_frame.destroy()
        # Save updated stat entries
        self.save_stat_entries()
        # Update unified buttons
        self.main_window.update_unified_buttons()
    
    def save_stat_entries(self):
        """Save stat entries to settings"""
        offensive_stats = []
        defensive_stats = []
        
        for stat_name, min_var, _ in self.offensive_stat_entries:
            min_value = min_var.get()
            offensive_stats.append({"name": stat_name, "min_value": min_value})
        
        for stat_name, min_var, _ in self.defensive_stat_entries:
            min_value = min_var.get()
            defensive_stats.append({"name": stat_name, "min_value": min_value})
        
        self.settings.set_custom("offensive_stat_entries", offensive_stats)
        self.settings.set_custom("defensive_stat_entries", defensive_stats)
        self.settings.set_custom("logic_mode", self.logic_var.get())
    
    def load_saved_settings(self):
        """Load saved settings from file"""
        # Load stats OCR area
        stats_area = self.settings.get_area("stats_area")
        if stats_area:
            self.area = stats_area
            self.automation.set_area(stats_area)
            if self.stats_area_status_var:
                self.stats_area_status_var.config(text="✓ Set", foreground="green")
        
        # Load grade OCR area
        grade_area = self.settings.get_area("grade_area")
        if grade_area:
            self.grade_area = grade_area
            self.automation.set_grade_area(grade_area)
            if self.grade_area_status_var:
                self.grade_area_status_var.config(text="✓ Grade area set", foreground="green")
        
        # Load apply button
        apply_coords = self.settings.get_button("apply_button")
        if apply_coords:
            self.apply_button_coords = apply_coords
            self.automation.set_apply_button(apply_coords)
            self.apply_coord_var.set(f"({apply_coords[0]}, {apply_coords[1]})")
        
        # Load change button
        change_coords = self.settings.get_button("change_button")
        if change_coords:
            self.change_button_coords = change_coords
            self.automation.set_change_button(change_coords)
            self.change_coord_var.set(f"({change_coords[0]}, {change_coords[1]})")
        
        # Load offensive stat entries
        offensive_stats_data = self.settings.get_custom("offensive_stat_entries", [])
        for stat_data in offensive_stats_data:
            stat_name = stat_data.get("name")
            min_value = stat_data.get("min_value", "")
            if stat_name:
                self._add_offensive_stat_from_saved(stat_name, min_value)
        
        # Load defensive stat entries
        defensive_stats_data = self.settings.get_custom("defensive_stat_entries", [])
        for stat_data in defensive_stats_data:
            stat_name = stat_data.get("name")
            min_value = stat_data.get("min_value", "")
            if stat_name:
                self._add_defensive_stat_from_saved(stat_name, min_value)
        
        # Load logic setting
        saved_logic = self.settings.get_custom("logic_mode", "OR")
        self.logic_var.set(saved_logic)
    
    def _add_offensive_stat_from_saved(self, stat_name, min_value):
        """Add an offensive stat from saved settings (internal helper)"""
        # Create frame for this stat entry
        stat_frame = ttk.Frame(self.off_stats_scrollable_frame)
        stat_frame.pack(fill=tk.X, pady=2)
        
        # Stat name label
        ttk.Label(stat_frame, text=stat_name, width=20).pack(side=tk.LEFT, padx=(0, 5))
        
        # Min value dropdown or entry
        ttk.Label(stat_frame, text="Min:").pack(side=tk.LEFT)
        min_var = tk.StringVar()
        if stat_name in VALUE_COLLISION_STATS:
            variations = GRADE_OPTIONS
            min_value_dropdown = ttk.Combobox(stat_frame, textvariable=min_var, values=variations, state="readonly", width=8)
            min_value_dropdown.pack(side=tk.LEFT, padx=(2, 5))
            if min_value and min_value in variations:
                min_var.set(min_value)
            elif variations:
                min_var.set(variations[0])
        else:
            variations = get_stat_variations(stat_name)
            if variations:
                min_value_dropdown = ttk.Combobox(stat_frame, textvariable=min_var, values=variations, state="readonly", width=8)
                min_value_dropdown.pack(side=tk.LEFT, padx=(2, 5))
                if min_value and min_value in variations:
                    min_var.set(min_value)
                elif variations:
                    min_var.set(variations[0])
            else:
                # Custom stat or no variations - use label to show value
                min_var.set(min_value)
                min_value_widget = ttk.Label(stat_frame, text=min_value, width=8)
                min_value_widget.pack(side=tk.LEFT, padx=(2, 5))
        
        # Remove button
        remove_btn = ttk.Button(stat_frame, text="Remove",
                               command=lambda: self.remove_offensive_stat(stat_name, stat_frame))
        remove_btn.pack(side=tk.LEFT)
        
        # Store the entry
        self.offensive_stat_entries.append((stat_name, min_var, stat_frame))
    
    def _add_defensive_stat_from_saved(self, stat_name, min_value):
        """Add a defensive stat from saved settings (internal helper)"""
        # Create frame for this stat entry
        stat_frame = ttk.Frame(self.def_stats_scrollable_frame)
        stat_frame.pack(fill=tk.X, pady=2)
        
        # Stat name label
        ttk.Label(stat_frame, text=stat_name, width=20).pack(side=tk.LEFT, padx=(0, 5))
        
        # Min value dropdown or entry
        ttk.Label(stat_frame, text="Min:").pack(side=tk.LEFT)
        min_var = tk.StringVar()
        if stat_name in VALUE_COLLISION_STATS:
            variations = GRADE_OPTIONS
            min_value_dropdown = ttk.Combobox(stat_frame, textvariable=min_var, values=variations, state="readonly", width=8)
            min_value_dropdown.pack(side=tk.LEFT, padx=(2, 5))
            if min_value and min_value in variations:
                min_var.set(min_value)
            elif variations:
                min_var.set(variations[0])
        else:
            variations = get_stat_variations(stat_name)
            if variations:
                min_value_dropdown = ttk.Combobox(stat_frame, textvariable=min_var, values=variations, state="readonly", width=8)
                min_value_dropdown.pack(side=tk.LEFT, padx=(2, 5))
                if min_value and min_value in variations:
                    min_var.set(min_value)
                elif variations:
                    min_var.set(variations[0])
            else:
                # Custom stat or no variations - use label to show value
                min_var.set(min_value)
                min_value_widget = ttk.Label(stat_frame, text=min_value, width=8)
                min_value_widget.pack(side=tk.LEFT, padx=(2, 5))
        
        # Remove button
        remove_btn = ttk.Button(stat_frame, text="Remove",
                               command=lambda: self.remove_defensive_stat(stat_name, stat_frame))
        remove_btn.pack(side=tk.LEFT)
        
        # Store the entry
        self.defensive_stat_entries.append((stat_name, min_var, stat_frame))

    def start_automation(self):
        """Start the arrival skill automation"""
        # Check if another tool is running
        if not self.main_window.set_running_tool("Arrival Skill"):
            return

        # Check if at least one stat is specified
        if not self.offensive_stat_entries and not self.defensive_stat_entries:
            self.main_window.update_status("Add at least one stat")
            self.main_window.clear_running_tool()
            return

        # Prepare desired stats
        desired_stats = {
            'offensive': [],
            'defensive': []
        }

        # Track whether grade OCR area is needed
        grade_required = False

        # Add offensive stats
        for stat_name, min_var, _ in self.offensive_stat_entries:
            variation = min_var.get()
            if not variation:
                self.main_window.update_status(f"Select value for {stat_name}")
                self.main_window.clear_running_tool()
                return

            # Extract numeric value from the variation (handle commas like "1,600")
            # Remove commas first, then extract the full number
            variation_no_commas = variation.replace(',', '')
            value_match = re.search(r'(\d+)', variation_no_commas)
            if value_match:
                off_val = int(value_match.group(1))
                meta = {}
                if stat_name in VALUE_COLLISION_STATS:
                    meta = {"mode": "grade"}
                    grade_required = True
                desired_stats['offensive'].append((stat_name, off_val, meta))

        # Add defensive stats
        for stat_name, min_var, _ in self.defensive_stat_entries:
            variation = min_var.get()
            if not variation:
                self.main_window.update_status(f"Select value for {stat_name}")
                self.main_window.clear_running_tool()
                return

            # Extract numeric value from the variation (handle commas like "1,600")
            # Remove commas first, then extract the full number
            variation_no_commas = variation.replace(',', '')
            value_match = re.search(r'(\d+)', variation_no_commas)
            if value_match:
                def_val = int(value_match.group(1))
                meta = {}
                if stat_name in VALUE_COLLISION_STATS:
                    meta = {"mode": "grade"}
                    grade_required = True
                desired_stats['defensive'].append((stat_name, def_val, meta))

        # If grade-based detection is needed, ensure grade area is defined
        if grade_required and not self.grade_area:
            self.main_window.update_status("Set the Grade OCR area before starting (required for grade-based stats)")
            self.main_window.clear_running_tool()
            return

        # Display what we're looking for
        def format_requirement(name, val, meta):
            if meta and meta.get("mode") == "grade":
                return f"{name} (Grade ≥{val})"
            return f"{name} (≥{val})"

        off_stats_display = []
        if desired_stats['offensive']:
            off_stats_display = [format_requirement(name, val, meta) for name, val, meta in desired_stats['offensive']]

        def_stats_display = []
        if desired_stats['defensive']:
            def_stats_display = [format_requirement(name, val, meta) for name, val, meta in desired_stats['defensive']]
        
        status_msg = "Looking for: "
        if off_stats_display and def_stats_display:
            status_msg += f"Offensive: {' OR '.join(off_stats_display)} AND Defensive: {' OR '.join(def_stats_display)}"
        elif off_stats_display:
            status_msg += f"Offensive: {' OR '.join(off_stats_display)}"
        elif def_stats_display:
            status_msg += f"Defensive: {' OR '.join(def_stats_display)}"
        
        self.main_window.update_status(status_msg)

        # Get logic setting (OR or AND)
        logic_mode = self.logic_var.get()
        
        # Start automation
        if self.automation.start(desired_stats, logic_mode=logic_mode):
            self.main_window.update_status("Arrival skill automation started")
        else:
            self.main_window.clear_running_tool()

    def stop_automation(self):
        """Stop the arrival skill automation"""
        self.automation.stop()
        self.main_window.clear_running_tool()
        self.main_window.update_status("Arrival skill automation stopped")

    def show_grade_area_info(self):
        """Show information about the Grade OCR area"""
        info_text = (
            "Grade OCR Area Information:\n\n"
            "This area is only required for the 'Arrival Skill Cool Time Decreased' stat.\n\n"
            "When defining this area, select the region in the game where the grade text appears "
            "(e.g., '1st Grade', '2nd Grade', '3rd Grade', etc.).\n\n"
            "This area is used to detect the grade level when the stat value cannot be read "
            "due to UI collision."
        )
        messagebox.showinfo("Grade OCR Area Info", info_text)

    def emergency_stop(self):
        """Emergency stop the automation"""
        self.automation.emergency_stop()
        self.main_window.clear_running_tool()


