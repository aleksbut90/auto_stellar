# Stellar system options and data
# Extracted from main.py

# Stellar system options
STELLAR_OPTIONS = [
    "PVE Пробивная способность",
    "PVE Крит. урон",
    "Усиление всех атак",
    "Пробивная способность",
    "Крит. урон",
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
