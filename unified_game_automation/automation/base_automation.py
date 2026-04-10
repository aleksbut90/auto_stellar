# Base automation class with shared functionality
# Provides common methods for all automation types

import threading

class BaseAutomation:
    """Base class for all automation types with shared functionality"""
    
    def __init__(self, game_connector, ocr_engine, status_callback=None):
        """Initialize base automation"""
        self.game_connector = game_connector
        self.ocr_engine = ocr_engine
        self.status_callback = status_callback
        self.running = False
        self.stop_event = threading.Event()
    
    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)
    
    def emergency_stop(self):
        """Emergency stop the automation - shared implementation"""
        if self.running:
            self.stop_event.set()
            self.running = False
            self.update_status("🚨 EMERGENCY STOP - Automation stopped!")
    
    def stop(self):
        """Stop the automation - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement stop()")