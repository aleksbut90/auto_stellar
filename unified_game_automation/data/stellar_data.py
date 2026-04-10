# Stellar system options and data
# Extracted from main.py

# Stellar system options
STELLAR_OPTIONS = [
    "усиление всех атак",
    "пробивная способность",
    "крит урон",
    "Пустота"
]

# Exceptions for penetration option (from main.py)так
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
