# Stellar system options and data
# Extracted from main.py

# Stellar system options
STELLAR_OPTIONS = [
    "PVE Penetration",
    "PVE Critical DMG",
    "All Attack UP",
    "Penetration",
    "Critical DMG.",
    "Ignore Accuracy",
    "Defense"
]

# Exceptions for penetration option (from main.py)
PENETRATION_EXCEPTIONS = [
    "ignore",
    "cancel"
]

def get_stellar_options():
    """Get all available stellar options"""
    return STELLAR_OPTIONS

def get_penetration_exceptions():
    """Get penetration exceptions"""
    return PENETRATION_EXCEPTIONS
