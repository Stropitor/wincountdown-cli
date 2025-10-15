![wincountdown screenshot](screenshots/screenshot_1.png)

# wincountdown

A command-line countdown timer for Windows with ASCII art display and customizable alerts.


## Features

- Large ASCII art countdown display
- Customizable beep alerts (frequency, duration, count, gap)
- Loop mode for repeating countdowns
- Silent mode option
- Meme metric time mode (1 hour = 100 minutes, 1 minute = 100 seconds)
- Smart display (shows only relevant time units)

## Usage
```bash
wincountdown <time> [options]
```

### Time Formats

- Seconds only: `30s`, `90s`, `500s (converts to MM:SS)`
- Minutes only: `5m`, `45m`, `240m (converts to HH:MM:SS)`
- Hours only: `2h`, `10h`
- Combined: `1h30m`, `2h15m30s`, `45m30s`
- Colon format: `1:30:00` (HH:MM:SS), `45:30` (MM:SS)

### Options

| Option | Description |
|--------|-------------|
| `-s, --silent` | Silent mode (no beep alert) |
| `-f HZ, --freq HZ` | Beep frequency in Hz (default: 800, range: 37-32767) |
| `-b N, --beeps N` | Number of beeps when finished (default: 3) |
| `-d MS, --duration MS` | Duration of each beep in milliseconds (default: 1000) |
| `-g MS, --gap MS` | Gap between beeps in milliseconds (default: 300) |
| `-l, --loop` | Automatically restart countdown when it reaches 0 (beeps once) |
| `-m, --metric` | Display in metric time (1h=100m, 1m=100s) |
| `-h, --help` | Show help message |

### Examples
```bash
# Basic countdowns
wincountdown 30s                      # 30 second countdown
wincountdown 5m                       # 5 minute countdown
wincountdown 1h30m                    # 1 hour 30 minutes
wincountdown 90s                      # Automatically displays as 01:30

# Silent mode
wincountdown 10m --silent             # No beep alert
wincountdown 5m -s                    # Short form

# Loop mode
wincountdown 25m --loop               # Repeating timer
wincountdown 3m -l                    # Short form

# Custom beep patterns
wincountdown 1m --freq 440            # Use 440Hz beep
wincountdown 30s --beeps 5            # Beep 5 times
wincountdown 1h --duration 500        # 500ms beeps
wincountdown 5m --gap 100             # 100ms gap between beeps
wincountdown 1m -f 880 -b 3 -d 200 -g 100  # Fully custom pattern

# Metric time
wincountdown 5m --metric              # 5 real minutes in metric display
wincountdown 1h -m                    # 1 real hour in metric display

# Combinations
wincountdown 25m -l -s                # Silent looping timer
wincountdown 10s -f 1000 -b 1 -d 2000 # Single 2-second beep
```

## Building from Source
```bash
pip install pyinstaller
pyinstaller --onefile --name wincountdown wincountdown.py
```

The executable will be in the `dist/` folder.


## Installation & Running

### Option 1: Run Python Script

Requirements: Python 3.8+
```bash
git clone https://github.com/yourusername/wincountdown.git
cd wincountdown
python wincountdown.py
```

### Option 2: Run Executable (Command Prompt)

Download `wincountdown.exe` from releases or build from source and navigate to the folder:
```cmd
wincountdown 5m
```

### Option 3: Run Executable (PowerShell)

Download `wincountdown.exe` from releases or build from source and navigate to the folder:
```powershell
.\wincountdown 5m
```

To avoid the `.\` prefix, add to PATH (see Option 4).

### Option 4: Add to PATH

Adding wincountdown to PATH allows runing the tool from any terminal.

## Notes

- Maximum time: 99:59:59 (or 99:99:99 in metric mode)
- The timer automatically shows only relevant units (seconds, MM:SS, or HH:MM:SS)
- Beep alert plays when countdown finishes (customizable)
- Loop mode plays only one beep before restarting
- Metric mode is a joke option where 1 hour = 100 minutes and 1 minute = 100 seconds. Each metric second lasts 1 real second. Input time is still in real time.
- Press Ctrl+C to stop the timer
