# Collection system data and constants

# Collection tab types
COLLECTION_TABS = [
    "Dungeon",
    "World", 
    "Special",
    "Boss"
]

def get_collection_tabs():
    """Get list of collection tab names"""
    return COLLECTION_TABS.copy()

# Collection button types for calibration
COLLECTION_BUTTONS = {
    "auto_refill": "Auto Refill",
    "register": "Register", 
    "yes": "Yes"
}

def get_collection_buttons():
    """Get dictionary of collection button types"""
    return COLLECTION_BUTTONS.copy()