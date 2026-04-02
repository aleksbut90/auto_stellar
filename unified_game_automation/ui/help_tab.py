# Help tab UI
# Provides brief explanations of what each tab does

import tkinter as tk
from tkinter import ttk
import webbrowser

class HelpTab:
    def __init__(self, parent_frame, main_window):
        """Initialize the Help tab"""
        self.parent_frame = parent_frame
        self.main_window = main_window
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        """Create the help UI"""
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
        
        # Arrival Skill section
        arrival_frame = ttk.LabelFrame(scrollable_frame, text="Arrival Skill", padding="10")
        arrival_frame.pack(fill=tk.X, pady=(0, 10))
        
        arrival_text = "Automates rerolling of arrival skills. Detects stats using OCR and applies/changes skills based on your criteria.\n\n" \
                      "• Supports custom stats - you can define your own stat names to search for\n" \
                      "• Multiple stats can be searched simultaneously (OR condition - stops when any stat matches)\n" \
                      "• Special case: 'Arrival Skill Cool Time Decreased' requires Grade OCR area (this is where 1st Grade, 2nd Grade etc. appears) \n\n" \
                      "Setup video:"
        ttk.Label(arrival_frame, text=arrival_text, wraplength=600).pack(anchor=tk.W)
        
        def open_arrival_video(event):
            webbrowser.open("https://www.youtube.com/watch?v=PpWnRMNUtG8")
        
        arrival_link = ttk.Label(arrival_frame, text="https://www.youtube.com/watch?v=PpWnRMNUtG8", 
                               foreground="blue", cursor="hand2", font=("Arial", 9, "underline"))
        arrival_link.pack(anchor=tk.W, pady=(5, 0))
        arrival_link.bind("<Button-1>", open_arrival_video)
        
        # Stellar System section
        stellar_frame = ttk.LabelFrame(scrollable_frame, text="Stellar System", padding="10")
        stellar_frame.pack(fill=tk.X, pady=(0, 10))
        
        stellar_text = "Automates rerolling of stellar system stats. Detects stats using OCR.\n\n" \
                      "• Supports custom stats - you can define your own stat names to search for\n" \
                      "• Multiple stats can be searched simultaneously (OR condition - stops when any stat matches)\n\n" \
                      "Setup video:"
        ttk.Label(stellar_frame, text=stellar_text, wraplength=600).pack(anchor=tk.W)
        
        def open_stellar_video(event):
            webbrowser.open("https://www.youtube.com/watch?v=0KVkZXdlfyY")
        
        stellar_link = ttk.Label(stellar_frame, text="https://www.youtube.com/watch?v=0KVkZXdlfyY", 
                               foreground="blue", cursor="hand2", font=("Arial", 9, "underline"))
        stellar_link.pack(anchor=tk.W, pady=(5, 0))
        stellar_link.bind("<Button-1>", open_stellar_video)
        
        # Collection Filler section
        collection_frame = ttk.LabelFrame(scrollable_frame, text="Collection Filler", padding="10")
        collection_frame.pack(fill=tk.X, pady=(0, 10))
        
        collection_text = "Automates filling collection by detecting red dots and clicking through pages.\n\n" \
                         "Setup video:"
        ttk.Label(collection_frame, text=collection_text, wraplength=600).pack(anchor=tk.W)
        
        def open_collection_video(event):
            webbrowser.open("https://youtu.be/mPaBDvGdkTA")
        
        collection_link = ttk.Label(collection_frame, text="https://youtu.be/mPaBDvGdkTA", 
                                   foreground="blue", cursor="hand2", font=("Arial", 9, "underline"))
        collection_link.pack(anchor=tk.W, pady=(5, 0))
        collection_link.bind("<Button-1>", open_collection_video)
        
        # Heils Clicker section
        heils_frame = ttk.LabelFrame(scrollable_frame, text="Heils Clicker", padding="10")
        heils_frame.pack(fill=tk.X, pady=(0, 10))
        
        heils_text = "Simple clicker that continuously clicks at a defined coordinate until stopped."
        ttk.Label(heils_frame, text=heils_text, wraplength=600).pack(anchor=tk.W)
        
        # Custom Stats section
        custom_stats_frame = ttk.LabelFrame(scrollable_frame, text="Custom Stats", padding="10")
        custom_stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        custom_stats_text = "Custom stats use substring matching to find stats in the game.\n\n" \
                           "This means the tool searches for your text anywhere within the stat name that appears in-game. " \
                           "For example, if you enter 'Attack', it will match stats like 'All Attack Up', 'Attack Rate', or any stat containing the word 'Attack'.\n\n" \
                           "You don't need to enter the exact full stat name - just enter a unique part of the stat name that you want to find."
        ttk.Label(custom_stats_frame, text=custom_stats_text, wraplength=600).pack(anchor=tk.W)
        
        # Important Notes section
        notes_frame = ttk.LabelFrame(scrollable_frame, text="Important Notes", padding="10")
        notes_frame.pack(fill=tk.X, pady=(0, 10))
        
        notes_text = "• Arrival Skill: The 'Grade' OCR area is specifically for the 'Arrival Skill Cool Time Decreased' stat, " \
                    "which cannot be detected by stat value and requires grade-based detection\n" \
                    "• Multiple Stats: When searching for multiple stats, the automation uses OR logic - " \
                    "it will stop as soon as ANY of the specified stats matches your criteria"
        ttk.Label(notes_frame, text=notes_text, wraplength=600).pack(anchor=tk.W)
