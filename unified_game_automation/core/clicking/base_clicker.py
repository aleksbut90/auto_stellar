# Base class for clicking strategies
# This defines the interface that all clicking implementations must follow

from abc import ABC, abstractmethod

class BaseClicker(ABC):
    """Abstract base class for clicking strategies"""
    
    def __init__(self, game_window=None):
        """Initialize the clicker with a game window reference"""
        self.game_window = game_window
    
    def set_game_window(self, game_window):
        """Update the game window reference"""
        self.game_window = game_window
    
    @abstractmethod
    def click(self, coords, adjust_for_client_area=True):
        """
        Perform a left click at the specified coordinates
        
        Args:
            coords: Tuple of (x, y) coordinates relative to window
            adjust_for_client_area: Whether to adjust for window borders/title bar
            
        Returns:
            bool: True if click succeeded, False otherwise
        """
        pass
    
    @abstractmethod
    def right_click(self, coords, adjust_for_client_area=True):
        """
        Perform a right click at the specified coordinates
        
        Args:
            coords: Tuple of (x, y) coordinates relative to window
            adjust_for_client_area: Whether to adjust for window borders/title bar
            
        Returns:
            bool: True if click succeeded, False otherwise
        """
        pass
    
    @abstractmethod
    def middle_click(self, coords, adjust_for_client_area=True):
        """
        Perform a middle click at the specified coordinates
        
        Args:
            coords: Tuple of (x, y) coordinates relative to window
            adjust_for_client_area: Whether to adjust for window borders/title bar
            
        Returns:
            bool: True if click succeeded, False otherwise
        """
        pass
    
    @abstractmethod
    def get_name(self):
        """Return the name of this clicking method for logging/debugging"""
        pass