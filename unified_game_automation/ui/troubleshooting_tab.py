# Troubleshooting tab UI
# Provides troubleshooting information and common solutions

import tkinter as tk
from tkinter import ttk

class TroubleshootingTab:
    def __init__(self, parent_frame, main_window):
        """Initialize the Troubleshooting tab"""
        self.parent_frame = parent_frame
        self.main_window = main_window
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the troubleshooting UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Run as Admin section
        admin_frame = ttk.LabelFrame(scrollable_frame, text="Run as Administrator", padding="10")
        admin_frame.pack(fill=tk.X, pady=(0, 10))
        
        admin_text = "The application must be run as Administrator for proper functionality.\n" \
                     "Right-click the executable and select 'Run as administrator'."
        ttk.Label(admin_frame, text=admin_text, wraplength=600).pack(anchor=tk.W)
        
        # OCR Issues section
        ocr_frame = ttk.LabelFrame(scrollable_frame, text="OCR (Optical Character Recognition) Issues", padding="10")
        ocr_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Scaling
        scaling_frame = ttk.Frame(ocr_frame)
        scaling_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(scaling_frame, text="Display Scaling:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        scaling_text = "Set Windows display scaling to 100% (especially important for laptop users).\n" \
                       "TL;DR: Right-click on desktop → Display settings → Scale → 100%"
        ttk.Label(scaling_frame, text=scaling_text, wraplength=600).pack(anchor=tk.W, pady=(5, 0))
        
        # Game UI Size
        ui_size_frame = ttk.Frame(ocr_frame)
        ui_size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ui_size_frame, text="In-Game UI Size:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        ui_size_text = "Don't make the UI in-game too small. The smaller the in-game UI, the less consistent the OCR is.\n" \
                       "Default setting is fine, or slightly smaller (10-20% reduction max)."
        ttk.Label(ui_size_frame, text=ui_size_text, wraplength=600).pack(anchor=tk.W, pady=(5, 0))
        
        # Game Resolution
        resolution_frame = ttk.Frame(ocr_frame)
        resolution_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(resolution_frame, text="Game Resolution:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        resolution_text = "Recommended game resolution: 1920x1080"
        ttk.Label(resolution_frame, text=resolution_text, wraplength=600).pack(anchor=tk.W, pady=(5, 0))
        
        # Font
        font_frame = ttk.Frame(ocr_frame)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_frame, text="Game Font:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        font_text = "Use default font in game: Tahoma"
        ttk.Label(font_frame, text=font_text, wraplength=600).pack(anchor=tk.W, pady=(5, 0))
        
        # Delay settings
        delay_frame = ttk.LabelFrame(scrollable_frame, text="Collection Filler Delay Settings", padding="10")
        delay_frame.pack(fill=tk.X, pady=(0, 10))
        
        delay_text = "Don't set the delay too low. Around 30ms is fast enough. If you have bad ping, you may need higher values."
        ttk.Label(delay_frame, text=delay_text, wraplength=600).pack(anchor=tk.W)
        
        # Red dot images
        reddot_frame = ttk.LabelFrame(scrollable_frame, text="Red Dot Images", padding="10")
        reddot_frame.pack(fill=tk.X, pady=(0, 10))
        
        reddot_text = "The red dot PNG image red-dot.png must be in the same folder as the executable. The collection tracker is looking for the red-dot to determine which collections are still available to be filled."
        ttk.Label(reddot_frame, text=reddot_text, wraplength=600).pack(anchor=tk.W)
