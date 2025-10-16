![wincountdown screenshot](screenshots/screenshot_1.png)

# wincountdown

A command-line countdown timer for Windows with ASCII art display, customizable alerts, and configuration file support.


## Features

- Large ASCII art countdown display
- Real-time start and end time display
- Customizable beep alerts (frequency, duration, count, gap)
- Configuration file for persistent settings
- Advanced behaviors: auto-run commands, default flags
- Loop mode for repeating countdowns
- Silent mode option
- Metric time mode (1 hour = 100 minutes, 1 minute = 100 seconds)
- Smart display (shows only relevant time units)
- Debug mode for troubleshooting

## Usage
```bash
wincountdown <time> [options]
```

### Time Formats

- Seconds only: `30s`, `90s`, `500s` (converts to MM:SS)
- Minutes only: `5m`, `45m`, `240m` (converts to HH:MM:SS)
- Hours only: `2h`, `10h`
- Combined: `1h30m`, `2h15m30s`, `45m30s`
- Colon format: `1:30:00` (HH:MM:SS), `45:30` (MM:SS)

### Options

| Option | Description |
|--------|-------------|
| `-s, --silent` | Silent mode (no beep alert) |
| `-f HZ, --freq HZ` | Beep frequency in Hz (default: from config, or 800) |
| `-b N, --beeps N` | Number of beeps when finished (default: from config, or 3) |
| `-d MS, --duration MS` | Duration of each beep in milliseconds (default: from config, or 1000) |
| `-g MS, --gap MS` | Gap between beeps in milliseconds (default: from config, or 300) |
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

## Configuration File

On first run, `wincountdown-config.json` is automatically created in the same directory. This file allows customization of default settings and advanced behaviors.

### Basic Settings

```json
{
  "debug_mode": false,            // Enable debug logging to file
  "default_frequency": 800,       // Beep frequency in Hz (37-32767)
  "default_beeps": 3,             // Number of beeps when finished
  "default_duration": 1000,       // Beep duration in milliseconds
  "default_gap": 300,             // Gap between beeps in milliseconds
  "default_silent": false,        // No beeps by default
  "default_loop": false,          // Auto-restart by default
  "default_metric": false         // Metric time by default
}
```

### Advanced Behaviors

#### No Arguments Behavior

Controls behavior when running `wincountdown` with no arguments:

```json
{
  "enable_no_args_default": true,
  "no_args_default_command": "25m"
}
```

Options for `no_args_default_command`:
- `"help"` - Show help screen (default)
- Any time string: `"5m"`, `"25m"`, `"1h30m"`
- With flags: `"10m -l"` (10-minute looping timer)

Example: Setting to `"25m"` starts a 25-minute timer when typing just `wincountdown`

#### Time-Only Arguments Behavior

Automatically adds flags when providing only a time argument:

```json
{
  "enable_time_only_defaults": true,
  "time_only_default_flags": ["-l", "-s"]
}
```

Example: With the above config, typing `wincountdown 5m` becomes `wincountdown 5m -l -s` (loop + silent)

Common flag combinations:
- `["-l", "-s"]` - Loop and silent (repeating work timers)
- `["-l"]` - Loop only
- `["-f", "1000", "-b", "5"]` - Custom frequency and beep count
- `["-m"]` - Metric mode

Note: This only applies when typing just the time. Manual flags disable these defaults.

### Configuration Examples

**Pomodoro Timer Setup:**
```json
{
  "enable_no_args_default": true,
  "no_args_default_command": "25m",
  "enable_time_only_defaults": true,
  "time_only_default_flags": ["-l"]
}
```

**Silent Work Timer:**
```json
{
  "default_silent": true,
  "default_loop": true
}
```

**Quick Timer with Custom Alert:**
```json
{
  "enable_no_args_default": true,
  "no_args_default_command": "5m -f 1000 -b 5"
}
```

## Debug Mode

Debug mode can be enabled in the configuration file:

```json
{
  "debug_mode": true
}
```

When enabled:
- Creates `wincountdown-debug.log` in the same directory
- Logs detailed execution information with timestamps
- Clears the log file on each run
- Includes information about config loading, argument processing, and advanced behavior activation

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
git clone https://github.com/Stropitor/wincountdown-cli
cd wincountdown
python wincountdown.py 5m
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

Adding wincountdown to PATH allows running the tool from any terminal without navigating to the folder.

**Windows:**
1. Copy `wincountdown.exe` to a permanent location (e.g., `C:\Tools\wincountdown\`)
2. Open System Properties → Environment Variables
3. Under "User variables" or "System variables", find `Path` and click Edit
4. Click New and add the folder path (e.g., `C:\Tools\wincountdown\`)
5. Click OK to save
6. Restart the terminal

## Notes

- Maximum time: 99:59:59 (or 99:99:99 in metric mode)
- Timer automatically shows only relevant units (seconds, MM:SS, or HH:MM:SS)
- Start time and end time are displayed at the bottom of the timer
- Beep alert plays when countdown finishes (customizable via config or flags)
- Loop mode plays only one beep before restarting
- Metric mode: 1 hour = 100 minutes, 1 minute = 100 seconds. Each metric second lasts 1 real second. Input time is in real time.
- Press Ctrl+C to stop the timer
- Configuration file is created automatically on first run
- Command-line flags override config file settings
- Config file location: Same directory as the script/executable

## Troubleshooting

**Config not working:**
1. Enable debug mode (set `"debug_mode": true` in the config file)
2. Run the program and check `wincountdown-debug.log` for errors
3. Verify `wincountdown-config.json` is valid JSON
4. Delete the config file and allow it to regenerate with defaults

**Timer not visible:**
- Terminal window must be at least 120 characters wide
- Maximize the terminal window

**No sound:**
- Check that `"default_silent": false` in config
- Verify system volume is not muted
- Try a different frequency with `-f` flag

**Debug log not created:**
- Ensure `"debug_mode": true` is set in the config file
- Check write permissions in the directory
- Log file `wincountdown-debug.log` is created in the same folder as the script/executable