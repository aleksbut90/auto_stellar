# Windows API PostMessage clicking implementation
# Direct Windows API calls using PostMessage (asynchronous)
# Potentially faster than SendMessage but may be less reliable

import win32gui
import win32con
import win32api
from .base_clicker import BaseClicker

class PostMessageClicker(BaseClicker):
    """Clicking implementation using Windows API PostMessage (asynchronous)"""
    
    def __init__(self, game_window=None, get_offset_callback=None):
        """
        Initialize PostMessage clicker
        
        Args:
            game_window: The pywinauto window object
            get_offset_callback: Function to get window-client offset
        """
        super().__init__(game_window)
        self.get_offset_callback = get_offset_callback
    
    def click(self, coords, adjust_for_client_area=True):
        """Click using Windows API PostMessage - asynchronous and very fast"""
        if not self.game_window:
            return False
        
        try:
            hwnd = self.game_window.handle
            
            # Calculate the actual click coordinates
            if adjust_for_client_area and self.get_offset_callback:
                offset = self.get_offset_callback()
                if offset:
                    click_x = coords[0] - offset[0]
                    click_y = coords[1] - offset[1]
                else:
                    click_x, click_y = coords
            else:
                click_x, click_y = coords
            
            # Create the lParam for the click coordinates
            lParam = win32api.MAKELONG(click_x, click_y)
            
            # Check if window is valid
            if not win32gui.IsWindow(hwnd):
                return False
            
            # Post mouse down and up messages - asynchronous, returns immediately
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
            
            return True
        except Exception as e:
            return False
    
    def right_click(self, coords, adjust_for_client_area=True):
        """Right-click using Windows API PostMessage"""
        if not self.game_window:
            return False
        
        try:
            hwnd = self.game_window.handle
            
            # Calculate the actual click coordinates
            if adjust_for_client_area and self.get_offset_callback:
                offset = self.get_offset_callback()
                if offset:
                    click_x = coords[0] - offset[0]
                    click_y = coords[1] - offset[1]
                else:
                    click_x, click_y = coords
            else:
                click_x, click_y = coords
            
            # Create the lParam for the click coordinates
            lParam = win32api.MAKELONG(click_x, click_y)
            
            # Check if window is valid
            if not win32gui.IsWindow(hwnd):
                return False
            
            # Post right mouse down and up messages
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)
            
            return True
        except Exception as e:
            return False
    
    def middle_click(self, coords, adjust_for_client_area=True):
        """Middle-click using Windows API PostMessage"""
        if not self.game_window:
            return False
        
        try:
            hwnd = self.game_window.handle
            
            # Calculate the actual click coordinates
            if adjust_for_client_area and self.get_offset_callback:
                offset = self.get_offset_callback()
                if offset:
                    click_x = coords[0] - offset[0]
                    click_y = coords[1] - offset[1]
                else:
                    click_x, click_y = coords
            else:
                click_x, click_y = coords
            
            # Create the lParam for the click coordinates
            lParam = win32api.MAKELONG(click_x, click_y)
            
            # Check if window is valid
            if not win32gui.IsWindow(hwnd):
                return False
            
            # Post middle mouse down and up messages
            win32gui.PostMessage(hwnd, win32con.WM_MBUTTONDOWN, win32con.MK_MBUTTON, lParam)
            win32gui.PostMessage(hwnd, win32con.WM_MBUTTONUP, 0, lParam)
            
            return True
        except Exception as e:
            return False
    
    def get_name(self):
        """Return the name of this clicking method"""
        return "Windows API PostMessage (Asynchronous)"