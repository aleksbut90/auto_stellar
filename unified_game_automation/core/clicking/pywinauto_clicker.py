# PyWinAuto clicking implementation (current method)
# Uses pywinauto's built-in click methods

import win32gui
from .base_clicker import BaseClicker

class PyWinAutoClicker(BaseClicker):
    """Clicking implementation using pywinauto's built-in methods"""
    
    def __init__(self, game_window=None, get_offset_callback=None):
        """
        Initialize PyWinAuto clicker
        
        Args:
            game_window: The pywinauto window object
            get_offset_callback: Function to get window-client offset
        """
        super().__init__(game_window)
        self.get_offset_callback = get_offset_callback
    
    def click(self, coords, adjust_for_client_area=True):
        """Click using pywinauto's built-in click method"""
        if not self.game_window:
            return False
        
        try:
            if adjust_for_client_area and self.get_offset_callback:
                offset = self.get_offset_callback()
                if offset:
                    adjusted_coords = (coords[0] - offset[0], coords[1] - offset[1])
                    self.game_window.click(coords=adjusted_coords)
                    return True
            
            self.game_window.click(coords=coords)
            return True
        except Exception as e:
            return False
    
    def right_click(self, coords, adjust_for_client_area=True):
        """Right-click using pywinauto's built-in right_click method"""
        if not self.game_window:
            return False
        
        try:
            if adjust_for_client_area and self.get_offset_callback:
                offset = self.get_offset_callback()
                if offset:
                    adjusted_coords = (coords[0] - offset[0], coords[1] - offset[1])
                    self.game_window.right_click(coords=adjusted_coords)
                    return True
            
            self.game_window.right_click(coords=coords)
            return True
        except Exception as e:
            return False
    
    def middle_click(self, coords, adjust_for_client_area=True):
        """Middle-click using pywinauto's built-in click method with middle button"""
        if not self.game_window:
            return False
        
        try:
            if adjust_for_client_area and self.get_offset_callback:
                offset = self.get_offset_callback()
                if offset:
                    adjusted_coords = (coords[0] - offset[0], coords[1] - offset[1])
                    self.game_window.click(coords=adjusted_coords, button='middle')
                    return True
            
            self.game_window.click(coords=coords, button='middle')
            return True
        except Exception as e:
            return False
    
    def get_name(self):
        """Return the name of this clicking method"""
        return "PyWinAuto (Built-in)"