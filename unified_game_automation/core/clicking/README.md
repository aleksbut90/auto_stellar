# Clicking Strategies System

This directory contains different clicking implementations that can be easily swapped for testing and performance comparison.

## 🎯 Quick Start - How to Switch Clicking Methods

**To change the clicking method, edit ONE line in `clicking_config.py`:**

```python
ACTIVE_CLICKER = SendMessageClicker  # <-- Change this line
```

## 📋 Available Clicking Methods

### 1. **PyWinAutoClicker** (Original Method)
- **File**: `pywinauto_clicker.py`
- **Method**: Uses pywinauto's built-in `.click()` method
- **Speed**: ⭐⭐ (Slower)
- **Reliability**: ⭐⭐⭐⭐ (Very reliable)
- **Pros**: 
  - Simple and well-tested
  - Handles edge cases automatically
  - Good for debugging
- **Cons**: 
  - Has built-in delays
  - Goes through abstraction layer
  - Slower than direct API calls
- **Best for**: Initial testing, debugging issues

### 2. **SendMessageClicker** 
- **File**: `sendmessage_clicker.py`
- **Method**: Windows API `SendMessage()` - synchronous
- **Speed**: ⭐⭐⭐⭐ (Fast)
- **Reliability**: ⭐⭐⭐⭐⭐ (Very reliable)
- **Pros**: 
  - Much faster than pywinauto
  - Synchronous - waits for message to be processed
  - More responsive in-game
  - No built-in delays
  - **This is what the collection tool uses**
- **Cons**: 
  - Slightly more complex implementation
- **Best for**: Production use, fast automation

### 3. **PostMessageClicker** (Experimental)
- **File**: `postmessage_clicker.py`
- **Method**: Windows API `PostMessage()` - asynchronous
- **Speed**: ⭐⭐⭐⭐⭐ (Fastest)
- **Reliability**: ⭐⭐⭐ (May miss clicks if game is busy)
- **Pros**: 
  - Fastest possible method
  - Asynchronous - returns immediately
  - No waiting for message processing
- **Cons**: 
  - May miss clicks if game's message queue is full
  - Less reliable than SendMessage
- **Best for**: Experimental testing, very fast automation

## 🔧 How to Test Different Methods

### Step 1: Edit the Config File
Open `clicking_config.py` and change the `ACTIVE_CLICKER` line:

```python
# Test PyWinAuto (original)
ACTIVE_CLICKER = PyWinAutoClicker

# Test SendMessage (recommended)
ACTIVE_CLICKER = SendMessageClicker

# Test PostMessage (experimental)
ACTIVE_CLICKER = PostMessageClicker
```

### Step 2: Restart Your Application
The clicking method is loaded when the game connector initializes, so you need to:
1. Close your automation tool
2. Reopen it
3. Connect to the game
4. Test the automation

### Step 3: Compare Performance
When testing, look for:
- **Speed**: How fast does the automation run?
- **Reliability**: Does every click register in the game?
- **Responsiveness**: Does the game respond immediately to clicks?
- **Stability**: Does it work consistently over long periods?

## 📊 Recommended Testing Order

1. **Start with SendMessageClicker** (collection tool method)
   - This is proven to work well in the collection tool
   - Should be faster than the current PyWinAuto method

2. **Compare with PyWinAutoClicker** (current method)
   - Test if SendMessage is actually faster
   - Verify both methods work correctly

3. **Try PostMessageClicker** (if you want maximum speed)
   - Only test this if SendMessage works well
   - May be faster but potentially less reliable

## 🔍 Debugging

If a clicking method doesn't work:
1. Check the status messages - they show which clicking method is active
2. Try a different method to isolate the issue
3. Check if the game window is properly connected
4. Verify coordinates are correct

## 🏗️ Architecture

```
clicking/
├── base_clicker.py          # Abstract base class (interface)
├── pywinauto_clicker.py     # PyWinAuto implementation
├── sendmessage_clicker.py   # Windows API SendMessage
├── postmessage_clicker.py   # Windows API PostMessage
├── clicking_config.py       # Configuration (CHANGE THIS)
└── README.md               # This file
```

All clickers implement the same interface from `BaseClicker`:
- `click(coords, adjust_for_client_area)` - Left click
- `right_click(coords, adjust_for_client_area)` - Right click
- `get_name()` - Get method name for logging

## 💡 Important Notes

- **All methods work without moving your physical mouse cursor** ✅
- The clicking method is shown in the status message when connecting to the game
- You can add new clicking methods by creating a new class that inherits from `BaseClicker`
- The game connector automatically uses the active clicker from the config

## 🎮 Mouse Movement vs Clicking

**Important distinction:**
- **Clicking**: All methods send click messages directly to the game window (no mouse movement)
- **Mouse Movement**: Only used for scrolling (via `win32api.SetCursorPos()`)
- Your physical mouse cursor stays free for other tasks during automation

## 📝 Adding a New Clicking Method

1. Create a new file: `your_method_clicker.py`
2. Inherit from `BaseClicker`
3. Implement `click()`, `right_click()`, and `get_name()`
4. Add import to `__init__.py`
5. Update `clicking_config.py` to include your new method
6. Test it!

Example:
```python
from .base_clicker import BaseClicker

class YourMethodClicker(BaseClicker):
    def click(self, coords, adjust_for_client_area=True):
        # Your implementation
        pass
    
    def right_click(self, coords, adjust_for_client_area=True):
        # Your implementation
        pass
    
    def get_name(self):
        return "Your Method Name"
```