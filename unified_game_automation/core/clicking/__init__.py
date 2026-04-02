# Clicking strategies package
# Easy imports for all clicking implementations

from .base_clicker import BaseClicker
from .pywinauto_clicker import PyWinAutoClicker
from .sendmessage_clicker import SendMessageClicker
from .postmessage_clicker import PostMessageClicker

__all__ = [
    'BaseClicker',
    'PyWinAutoClicker',
    'SendMessageClicker',
    'PostMessageClicker'
]