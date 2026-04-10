# Main entry point for the Unified Game Automation Tool
# This will be the main file that starts the tabbed interface

from ui.main_window import MainWindow

def main():
    """Main entry point for the unified game automation tool"""
    print("Starting Unified Game Automation Tool...")

    try:
        # Create and run the main window
        app = MainWindow()
        print("MainWindow created successfully, starting mainloop...")
        app.run()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
