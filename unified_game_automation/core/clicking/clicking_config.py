# Clicking Configuration
# Change this file to switch between different clicking methods

from .pywinauto_clicker import PyWinAutoClicker
from .sendmessage_clicker import SendMessageClicker
from .postmessage_clicker import PostMessageClicker

# ============================================================================
# CHANGE THIS LINE TO SWITCH CLICKING METHODS
# ============================================================================
# Options:
#   - PyWinAutoClicker    : Original method (foreground only)
#   - SendMessageClicker  : Windows API SendMessage (background friendly)
#   - PostMessageClicker  : Windows API PostMessage (background friendly, async)

# Use SendMessage for more reliable clicking (PostMessage can be unreliable with some games)
ACTIVE_CLICKER = SendMessageClicker  # <-- Change this to test different methods

# ============================================================================

def get_clicker_class():
    """Get the currently active clicker class"""
    return ACTIVE_CLICKER

def get_clicker_name():
    """Get the name of the currently active clicker"""
    # Create a temporary instance to get the name
    temp_instance = ACTIVE_CLICKER()
    return temp_instance.get_name()