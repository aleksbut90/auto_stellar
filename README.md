# Cabal Online helper for Stellar rolling, Arrival skill rolling, Heils clicker, Collection auto filler

Automated tool for game automation using OCR detection.

## Features

### Arrival Skill Tab
Rerolls arrival skill stats by detecting two stats (offensive and defensive).

- Set Apply and Change button coordinates
- Define OCR area for stat detection (draw a rectangle around the area where the stats + their values appear)
- Define Grade OCR area (required for "Arrival Skill Cool Time Decreased" stat, this stat can only be searched for by Grade and not its value)
- Add offensive and defensive stats with minimum values
- Within each category: OR logic (stops when any stat matches)
- Between categories: Choose OR (either category) or AND (both categories)
- Supports custom stats (Enter the text you want to seach for: If you type "Attack" it should stop at the stat "All Attack Up")

### Stellar System Tab
Rerolls stellar system stats by detecting single stat.

- Set Imprint button coordinate
- Define OCR area for stat detection
- Add multiple stats with minimum values
- OR logic (stops when any stat matches)
- Supports custom stats

### Collection Filler Tab
Fills collection by detecting red dots and navigating pages.

- Define OCR areas (collection tabs, dungeon list, collection items)
- Set button coordinates (auto refill, register, yes, page navigation)
- Configure click delay (for low ping recommended 30ms)
- Detects red dots to identify unfilled collections

### Heils Clicker Tab
Continuously clicks at a defined coordinate. Frees up your mouse

- Set click position coordinate
- Configure click delay

## Custom Stats

Arrival Skill and Stellar System tabs support custom stats.

- Select "Custom" from stat dropdown
- Enter exact stat name as it appears in-game
- Enter minimum value
- Tool searches for stat name using substring matching

Works for any stat name in the game, even if not in predefined list.

## Requirements

- Windows 10/11
- Game in windowed mode
- Run as Administrator
- Game font: Tahoma (default)
- Display scaling: 100%
- Game UI size: default or slightly smaller (10-20% max)
- Recommended resolution: 1920x1080

## Usage

1. Run executable as Administrator
2. Select tab
3. Set button coordinates
4. Define OCR areas
5. Configure settings
6. Click Start
7. Press ESC for emergency stop

Settings saved to `settings.json`.

## Building from Source

**Step 1: Create virtual environment**
```bash
python -m venv venv
```

**Step 2: Activate virtual environment**
```bash
venv\Scripts\activate.bat
```

**Step 3: Install dependencies**
```bash
pip install -r requirements_minimal.txt
```

**Step 4: Build executable**
```bash
pyinstaller main.spec
```

**Step 5: Find executable**
Built executable in `dist` folder:
```
dist\Stellar_and_Arrival_Automation.exe
```
