# Stellar system options and data
# Extracted from main.py

# Stellar system options
# Эти названия должны ТОЧНО совпадать с тем, что отображается в игре (OCR)
STELLAR_OPTIONS = [
    "Усиление всех атак",
    "Пробивная способность",
    "Крит. урон",
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
