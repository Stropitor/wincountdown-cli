# Complete Codebase Overview - wincountdown

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [File Structure](#file-structure)
3. [Code Structure (wincountdown.py)](#code-structure)
4. [Data Flow](#data-flow)
5. [Class Details](#class-details)
6. [Key Functions](#key-functions)
7. [Configuration System](#configuration-system)
8. [Display System](#display-system)
9. [Execution Flow](#execution-flow)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│              (Command line args + config file)              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    ConfigManager                            │
│  • Loads/creates %APPDATA%\wincountdown\config.json        │
│  • Merges defaults with user config                        │
│  • Validates ASCII art                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Argument Processing                        │
│  • Parse command line args                                  │
│  • Apply config defaults                                    │
│  • Validate inputs                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
                   ┌────┴─────┐
                   │          │
                   ▼          ▼
        ┌──────────────┐  ┌──────────────┐
        │ Clock Mode   │  │ Timer Mode   │
        └──────┬───────┘  └──────┬───────┘
               │                 │
               ▼                 ▼
    ┌─────────────────┐  ┌─────────────────┐
    │ DisplayManager  │  │ CountdownTimer  │
    │ ConsoleManager  │  │ DisplayManager  │
    │                 │  │ ConsoleManager  │
    └─────────────────┘  └─────────────────┘
```

---

## File Structure

```
wincountdown-windows/
├── wincountdown.py          # Main application (1,170 lines) - ALL CODE
├── setup.py                 # Python packaging configuration
├── LICENSE                  # GNU GPLv3 license
├── README.md                # User documentation
├── changelog.md             # Version history and changes
├── wincountdown-config.json # Example configuration file
│
├── docs/                    # Documentation
│   └── CODEBASE_OVERVIEW.md # This file
│
└── screenshots/             # Example screenshots
    └── (screenshot files)
```

**Note:** On Windows, config is created at:
- Installed: `%APPDATA%\wincountdown\config.json` (typically `C:\Users\<username>\AppData\Roaming\wincountdown\`)
- Standalone: Script directory (`config.json` in same folder as `wincountdown.py`)

---

## Code Structure (wincountdown.py)

The entire application is in one file (1,170 lines):

```
wincountdown.py
├── Lines 1-18     : Shebang, docstring, imports
├── Lines 19-167   : Constants & Default Data
│   ├── STD_OUTPUT_HANDLE, CURSOR_SIZE
│   ├── BORDER_WIDTH, ASCII_HEIGHT
│   ├── MAX_STANDARD_SECONDS, MAX_METRIC_MILLISECONDS
│   ├── UPDATE_INTERVAL_STANDARD, UPDATE_INTERVAL_METRIC
│   ├── DEFAULT_ASCII_DIGITS (0-9, :)
│   └── DEFAULT_CONFIG
├── Lines 168-177  : Windows Console API Structures
│   ├── COORD (ctypes structure)
│   └── CONSOLE_CURSOR_INFO (ctypes structure)
├── Lines 179-212  : Logger Class
├── Lines 214-255  : ConsoleManager Class
├── Lines 257-449  : ConfigManager Class
├── Lines 451-658  : DisplayManager Class
├── Lines 660-832  : CountdownTimer Class
├── Lines 834-918  : Helper Functions
│   ├── get_effective_args()
│   ├── parse_arguments()
│   └── validate_arguments()
├── Lines 920-1063 : print_help() Function
├── Lines 1065-1168: main() Function
└── Lines 1170-1171: if __name__ == '__main__'
```

---

## Data Flow

### Startup Flow
```
main()
  └─> ConfigManager(script_dir)
       └─> Detect if installed or standalone
       └─> Load or create config.json (location depends on install method)
            └─> Return config dict

  └─> get_effective_args(config)
       └─> Apply no-args defaults if enabled
       └─> Apply time-only defaults if enabled
       └─> Return modified sys.argv

  └─> parse_arguments(effective_args)
       └─> Use argparse to parse arguments
       └─> Return args object

  └─> validate_arguments(args)
       └─> Check frequency, beep count, time limits
       └─> Exit if invalid

  └─> Branch to Clock Mode or Timer Mode
```

### Timer Mode Flow
```
CountdownTimer.run()
  └─> DisplayManager.draw_static_ui()
       └─> ConsoleManager.clear_screen()
       └─> Print borders, title, time labels

  └─> Loop until countdown reaches 0:
       └─> Calculate remaining time
       └─> DisplayManager.update_time_display()
            └─> ConsoleManager.set_position()
            └─> DisplayManager.render_time()
                 └─> Convert time to ASCII art
                 └─> Print large digits
       └─> time.sleep(UPDATE_INTERVAL)

  └─> DisplayManager.draw_finished_screen()
       └─> Show "Time's Up!" message

  └─> play_beeps()
       └─> Try: winsound.Beep(freq, duration)
       └─> Except: print('\a')  # Terminal bell fallback

  └─> If loop mode: Restart from beginning
```

### Clock Mode Flow
```
CountdownTimer.run_clock()
  └─> DisplayManager.draw_clock_ui()
       └─> ConsoleManager.clear_screen()
       └─> Print borders, title

  └─> Loop forever (until Ctrl+C):
       └─> Get current time from datetime.now()
       └─> DisplayManager.update_time_display()
            └─> Render current time as ASCII art
       └─> time.sleep(UPDATE_INTERVAL)
```

---

## Class Details

### 1. Logger (Lines 182-211)

**Purpose:** Simple debug logging system

**Attributes:**
- `enabled` (bool) - Whether logging is active
- `file_path` (str) - Path to debug log file (location depends on install method)

**Methods:**
- `setup(enabled, file_path)` - Initialize logger
- `log(message)` - Write timestamped message to log file

**Usage:**
```python
logger = Logger()  # Global instance
logger.setup(True, "/path/to/debug.log")
logger.log("Debug message")
```

---

### 2. ConsoleManager (Lines 217-254)

**Purpose:** Terminal control using Windows Console API (kernel32.dll via ctypes)

**Attributes:**
- `kernel32` - Reference to kernel32.dll via ctypes.windll
- `h_console` - Console handle from GetStdHandle(STD_OUTPUT_HANDLE)

**Methods:**

| Method | Purpose | Windows API |
|--------|---------|-------------|
| `hide_cursor()` | Hide cursor to prevent flicker | SetConsoleCursorInfo(bVisible=False) |
| `show_cursor()` | Restore cursor visibility | SetConsoleCursorInfo(bVisible=True) |
| `set_position(x, y)` | Move cursor to coordinates | SetConsoleCursorPosition(COORD(x,y)) |
| `clear_screen()` | Clear entire screen | os.system('cls') |

**Implementation Details:**
- Uses ctypes structures (COORD, CONSOLE_CURSOR_INFO)
- Direct kernel32 API calls instead of ANSI escape codes
- Windows-native cursor and screen manipulation

**Context Manager:**
```python
with ConsoleManager() as console:
    # Cursor is hidden
    console.set_position(10, 5)
    print("Text at position")
# Cursor automatically shown on exit
```

---

### 3. ConfigManager (Lines 260-448)

**Purpose:** Load, create, and manage configuration

**Attributes:**
- `config_file` - Path to config.json (location depends on install method)
- `debug_log_file` - Path to debug.log (location depends on install method)

**Location Detection Logic:**
- **Installed via pip:** Uses Windows AppData directories
  - Config: `%APPDATA%\wincountdown\config.json`
  - Logs: `%LOCALAPPDATA%\wincountdown\debug.log`
- **Standalone script:** Uses script directory
  - Config and logs in same directory as wincountdown.py

**Methods:**

#### `__init__(script_dir=None)`
- Detects if running as installed package or standalone script
- Creates config and cache directories if needed
- Sets appropriate paths based on installation method

#### `create_config_content()`
- Returns JSON string with detailed comments
- Includes all default values
- Documents each configuration option

#### `load()`
- Checks if config file exists
- If not: creates it with defaults
- If yes: loads and parses JSON
- Filters out comment lines (keys starting with "//")
- Validates ASCII digits
- Returns config dictionary

#### `_validate_ascii_digits(config)`
- Ensures each digit (0-9, :) is exactly 8 lines
- Each line must be exactly 11 characters
- Falls back to DEFAULT_ASCII_DIGITS if invalid

**Configuration Options:**
```json
{
    "debug_mode": false,
    "default_frequency": 800,        // Beep frequency in Hz
    "default_beeps": 3,              // Number of beeps
    "default_duration": 1000,        // Beep duration in ms
    "default_gap": 300,              // Gap between beeps in ms
    "default_silent": false,         // Silent mode by default
    "default_loop": false,           // Loop mode by default
    "default_metric": false,         // Metric time by default
    "enable_no_args_default": false, // Custom behavior when no args
    "no_args_default_command": "help",
    "enable_time_only_defaults": false,
    "time_only_default_flags": [],
    "ascii_digits": { ... }          // Custom ASCII art
}
```

---

### 4. DisplayManager (Lines 454-657)

**Purpose:** Render all UI elements and ASCII art

**Attributes:**
- `ascii_art` - Dictionary of ASCII art for 0-9 and :

**Methods:**

#### `render_time(hours, minutes, seconds, show_hours, show_minutes)`
Returns 8 lines of ASCII art for time display.

**Input:** `hours=12, minutes=34, seconds=56`
**Output:** List of 8 strings (large ASCII art)

**Process:**
1. Format time string based on which units to show
2. Get ASCII art for each character
3. Concatenate horizontally line-by-line
4. Return 8-line list

#### `draw_border(char='=')`
Returns string of specified characters (115 chars wide)

#### `draw_line(content='', centered=False)`
Returns line with borders: `|` + content + `|`

#### `draw_static_ui(total_seconds, show_hours, show_minutes, metric, start_time_str, end_time_str, console)`
Draws initial countdown screen:
```
  +================================================+
  |                                                |
  |  >>>  C O U N T D O W N  [ HH:MM:SS ]  <<<   |
  |                                                |
  +================================================+

  [8 lines of ASCII art for initial time]

  +================================================+
  | Start time:       Press Ctrl+C      End time: |
  | 12:00:00                            12:05:00   |
  +================================================+
  stropitor
```

#### `update_time_display(hours, minutes, seconds, show_hours, show_minutes, console)`
Efficiently updates only the time portion (ASCII art area):
1. Move cursor to line 8
2. Render new time as ASCII art
3. Print each line at correct position
4. Avoids redrawing entire screen

#### `draw_finished_screen(show_hours, show_minutes, loop)`
Displays "Time's Up!" or "Restarting..." message after countdown completes:
```
  +================================================+
  |  >>>   T I M E ' S   U P !   <<<            |
  +================================================+

  [ASCII art showing 00:00:00]
```

#### `draw_clock_ui(console)`
Displays clock mode interface:
```
  +================================================+
  |  >>>   C L O C K   M O D E   <<<            |
  +================================================+

  [8 lines for time display]

  +================================================+
  |        Press Ctrl+C to exit                  |
  +================================================+
```

---

### 5. CountdownTimer (Lines 663-831)

**Purpose:** Core timer logic and execution

**Methods:**

#### `parse_time(time_str, metric=False)`
Parses various time formats into seconds (or milliseconds for metric).

**Supported Formats:**
- `5m` → 300 seconds
- `30s` → 30 seconds
- `1h30m` → 5400 seconds
- `2h15m30s` → 8130 seconds
- `01:30:00` → 5400 seconds
- `90:00` → 5400 seconds (90 minutes)

**Returns:** Integer (seconds for standard, milliseconds for metric)

**Validation:**
- Standard mode: Max 99:59:59 (359999 seconds)
- Metric mode: Max 99:99:99 metric (999999000 ms)

#### `play_beeps(freq, count, duration, gap, silent, loop)`
Plays audio alerts when timer finishes.

**Process:**
1. Check if silent mode → return early
2. Determine beep count (1 if loop mode, else count)
3. Try Windows winsound.Beep():
   ```python
   winsound.Beep(freq, duration)
   ```
4. If winsound fails → fallback to terminal bell (`\a`)
5. Sleep for gap duration between beeps

**Windows-Specific:**
- Uses `winsound` module (Windows standard library)
- winsound.Beep() generates actual PC speaker/audio beep
- Direct frequency and duration control

#### `run(total_seconds, beep_freq, beep_count, beep_duration, beep_gap, silent, loop, metric)`
Main countdown execution loop.

**Parameters:**
- `total_seconds` - Countdown duration
- `beep_freq` - Frequency in Hz (37-32767)
- `beep_count` - Number of beeps (1-100)
- `beep_duration` - Beep length in ms
- `beep_gap` - Gap between beeps in ms
- `silent` - Disable beeps
- `loop` - Auto-restart when finished
- `metric` - Use base-100 time display

**Process:**
1. Determine which time units to show (hours/minutes/seconds)
2. Calculate start and end times
3. Create DisplayManager and ConsoleManager
4. Draw static UI
5. **Main loop:**
   - Calculate remaining time
   - Format time string
   - Update display
   - Check if time <= 0
   - Sleep for update interval (50ms standard, 10ms metric)
6. Draw finished screen
7. Play beeps
8. If loop: restart from step 5

**Loop Mode:**
- Restarts countdown automatically
- Plays only 1 beep (not full count)
- Continues until Ctrl+C

#### `run_clock()`
Clock mode - displays current system time continuously.

**Process:**
1. Create DisplayManager and ConsoleManager
2. Draw clock UI
3. **Infinite loop:**
   - Get current time: `datetime.now()`
   - Format as HH:MM:SS (24-hour format)
   - Update display with current time
   - Sleep 50ms
4. Runs until Ctrl+C (KeyboardInterrupt)

**Features:**
- Always displays 24-hour format (HH:MM:SS)
- Updates every second (50ms check interval)
- Shows hours, minutes, and seconds in large ASCII art

---

## Key Functions

### get_effective_args(config) (Lines 837-868)

**Purpose:** Apply config defaults to command-line arguments

**Logic:**

1. **No-args default:**
   - If `enable_no_args_default` is True
   - And user provides no arguments
   - Replace with `no_args_default_command` (e.g., "help")

2. **Time-only defaults:**
   - If `enable_time_only_defaults` is True
   - And user provides only time (no flags)
   - Auto-inject flags from `time_only_default_flags`
   - Example: `wincountdown 5m` → `wincountdown 5m -l -s`

**Returns:** Modified sys.argv list

---

### parse_arguments(effective_args, config) (Lines 870-899)

**Purpose:** Parse command-line arguments using argparse

**Arguments:**

| Argument | Type | Description | Default |
|----------|------|-------------|---------|
| `time` | positional | Time string (5m, HH:MM:SS) | required |
| `-s, --silent` | flag | Disable beeps | False |
| `-l, --loop` | flag | Auto-restart countdown | False |
| `-m, --metric` | flag | Base-100 time display | False |
| `-f HZ` | int | Beep frequency (37-32767 Hz) | 800 |
| `-b COUNT` | int | Number of beeps (1-100) | 3 |
| `-d MS` | int | Beep duration (ms) | 1000 |
| `-g MS` | int | Gap between beeps (ms) | 300 |
| `-c, --clock` | flag | Clock mode | False |
| `--debug` | flag | Enable debug logging | False |

**Returns:** argparse.Namespace object

---

### validate_arguments(args, metric=False) (Lines 901-917)

**Purpose:** Validate parsed arguments

**Checks:**

1. **Frequency:** 37 ≤ freq ≤ 32767 Hz
2. **Beep count:** ≥ 1
3. **Beep duration:** ≥ 1 ms
4. **Beep gap:** ≥ 0 ms
5. **Time limits:**
   - Standard mode: ≤ 99:59:59 (359999 seconds)
   - Metric mode: ≤ 99:99:99 metric

**Returns:** List of error messages (empty if valid)

---

### print_help() (Lines 923-1062)

**Purpose:** Display comprehensive help text

**Sections:**
1. ASCII art title (WINCOUNTDOWN)
2. Description
3. Usage examples
4. Time formats
5. Options (countdown, beep, modes, utility)
6. Examples (basic, common use cases, custom alerts, clock, debug)
7. Configuration file details
8. Key features
9. Quick tips
10. Credits

**Windows-Specific Information:**
- Mentions `%APPDATA%\wincountdown\` for installed version
- Notes script directory for standalone version
- Emphasizes 24-hour clock format
- References winsound beep functionality

---

## Configuration System

### File Locations

**Installed Version:**
```
%APPDATA%\wincountdown\config.json      # User configuration
%LOCALAPPDATA%\wincountdown\debug.log   # Debug logs
```

Typically:
```
C:\Users\<username>\AppData\Roaming\wincountdown\config.json
C:\Users\<username>\AppData\Local\wincountdown\debug.log
```

**Standalone Version:**
```
<script-directory>\config.json          # User configuration
<script-directory>\debug.log            # Debug logs
```

### Config Creation Flow

```
User runs wincountdown first time
  └─> ConfigManager.load()
       └─> Detect installation type (pip vs standalone)
       └─> Set appropriate directory paths
       └─> Check if config.json exists
            └─> NO: Create directories
                 └─> Generate JSON with create_config_content()
                 └─> Write to config.json
                 └─> Load and return config

            └─> YES: Read file
                 └─> Parse JSON (skip "//"-prefixed comment lines)
                 └─> Validate ASCII digits
                 └─> Merge with DEFAULT_CONFIG (for new keys)
                 └─> Return config
```

### Comment System

Config uses JSON with pseudo-comments:
```json
{
    "//": "This is a comment line",
    "//note": "Comment lines start with //",
    "actual_setting": true
}
```

ConfigManager filters out keys starting with `"//"` during parsing.

---

## Display System

### ASCII Art Structure

Each digit is **8 lines tall × 11 characters wide**:

```
" ######### "   ← Line 0 (11 chars)
"###     ###"   ← Line 1
"###     ###"   ← Line 2
"###     ###"   ← Line 3
"###     ###"   ← Line 4
"###     ###"   ← Line 5
"###     ###"   ← Line 6
" ######### "   ← Line 7
```

### Time Rendering Process

**Input:** `hours=12, minutes=34, seconds=56`

**Process:**
1. Format time string based on display mode: `"12:34:56"`
2. Get ASCII art for each character: `1`, `2`, `:`, `3`, `4`, `:`, `5`, `6`
3. For each of 8 lines:
   - Concatenate line N from all characters
   - Result: line N of final display (88+ chars)
4. Return list of 8 concatenated lines

**Output:**
```
    ###     ######### ........(88 chars total)
  #####    ###     ###........
    ###    ###     ###........
    ###     ######### ........
    ###    ###     ###........
    ###    ###     ###........
    ###    ###     ###........
#####################........
```

### Display Update Efficiency

**Inefficient Approach (not used):**
- Clear entire screen
- Redraw all UI elements
- Causes flicker

**Efficient Approach (actual implementation):**
- Draw static UI once (borders, labels)
- **Only update time display area:**
  - Move cursor to line 8 using SetConsoleCursorPosition
  - Overwrite 8 lines of ASCII art
  - Leave borders/labels untouched

**Update Frequency:**
- Standard mode: 50ms (20 FPS)
- Metric mode: 10ms (100 FPS) - needed for fast metric seconds

### Windows Console API Usage

**Cursor Control:**
- `kernel32.SetConsoleCursorInfo()` - Hide/show cursor
- `kernel32.SetConsoleCursorPosition()` - Move cursor to (x, y)
- Uses COORD structure for position
- Uses CONSOLE_CURSOR_INFO for cursor visibility

**Screen Management:**
- `os.system('cls')` - Clear screen (Windows command)
- Direct console handle via `GetStdHandle(STD_OUTPUT_HANDLE)`

---

## Execution Flow

### Complete Program Flow Diagram

```
START
  │
  ├─> main()
  │     │
  │     ├─> Detect script directory (frozen vs normal)
  │     │
  │     ├─> ConfigManager(script_dir)
  │     │     └─> Detect install type
  │     │     └─> Load config.json from appropriate location
  │     │
  │     ├─> Logger.setup() if --debug flag
  │     │
  │     ├─> get_effective_args(config)
  │     │     ├─> Apply no-args default?
  │     │     └─> Apply time-only defaults?
  │     │
  │     ├─> parse_arguments(effective_args, config)
  │     │     └─> argparse creates args object
  │     │
  │     ├─> Check for --help flag
  │     │     └─> YES: print_help() → EXIT
  │     │
  │     ├─> Check for --clock flag
  │     │     └─> YES: timer.run_clock() → Loop forever
  │     │
  │     ├─> validate_arguments(args)
  │     │     └─> Invalid? → Print errors → EXIT
  │     │
  │     ├─> Create CountdownTimer(config)
  │     │
  │     └─> Timer mode
  │           ├─> timer.parse_time(args.time)
  │           ├─> timer.run(total_seconds, ...)
  │           │     │
  │           │     ├─> display.draw_static_ui()
  │           │     │
  │           │     ├─> LOOP: Until time = 0
  │           │     │     ├─> Calculate remaining
  │           │     │     ├─> Format time string
  │           │     │     ├─> display.update_time_display()
  │           │     │     └─> sleep(UPDATE_INTERVAL)
  │           │     │
  │           │     ├─> display.draw_finished_screen()
  │           │     │
  │           │     ├─> timer.play_beeps() [winsound.Beep()]
  │           │     │
  │           │     └─> Loop mode?
  │           │           └─> YES: Restart countdown
  │           │           └─> NO: Exit
  │           │
  │           └─> Ctrl+C (KeyboardInterrupt)
  │                 └─> console.show_cursor()
  │                 └─> EXIT
  │
EXIT
```

### Error Handling

**Graceful Exit:**
```python
try:
    # Main timer loop
except KeyboardInterrupt:
    # User pressed Ctrl+C
    console.show_cursor()  # Restore cursor
    print("\n\nTimer stopped!")
    sys.exit(0)
```

**Config Errors:**
- Missing config → Auto-create with defaults
- Invalid JSON → Print warning, use DEFAULT_CONFIG
- Invalid ASCII digits → Fall back to DEFAULT_ASCII_DIGITS

**Audio Errors:**
- `winsound.Beep()` fails → Use terminal bell (`\a`)
- Frequency out of range → Validation catches before calling

---

## Key Algorithms

### Time Parsing Algorithm

```python
def parse_time(time_str, metric=False):
    # Try colon format first (HH:MM:SS or MM:SS)
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:  # MM:SS
            minutes, seconds = int(parts[0]), int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])

    # Try component format (1h30m45s) - optimized approach
    else:
        time_str = time_str.lower()

        # Extract hours
        if 'h' in time_str:
            h_parts = time_str.split('h', 1)
            hours = int(h_parts[0])
            time_str = h_parts[1]

        # Extract minutes
        if 'm' in time_str:
            m_parts = time_str.split('m', 1)
            minutes = int(m_parts[0]) if m_parts[0] else 0
            time_str = m_parts[1]

        # Extract seconds
        if 's' in time_str:
            s_parts = time_str.split('s', 1)
            seconds = int(s_parts[0]) if s_parts[0] else 0

    total = hours * 3600 + minutes * 60 + seconds
    return int(total * 1000) if metric else total  # Metric uses milliseconds
```

### Metric Time Conversion

**Real Time → Metric Time:**
- 1 real second = 1.1574 metric seconds
- 1 metric hour = 100 metric minutes
- 1 metric minute = 100 metric seconds

```python
# Total real milliseconds → Total metric milliseconds
metric_ms = real_seconds * 1000

# Display as HH:MM:SS
metric_seconds = metric_ms // 1000
metric_hours = metric_seconds // 10000
metric_minutes = (metric_seconds // 100) % 100
metric_secs = metric_seconds % 100
```

### Windows Console Cursor Control

```python
# Hide cursor
cursor_info = CONSOLE_CURSOR_INFO()
cursor_info.dwSize = CURSOR_SIZE  # 100
cursor_info.bVisible = False
kernel32.SetConsoleCursorInfo(h_console, ctypes.byref(cursor_info))

# Set position
coord = COORD(x, y)
kernel32.SetConsoleCursorPosition(h_console, coord)
```

---

## Performance Considerations

1. **Update Intervals:**
   - Standard: 50ms (plenty for 1-second countdown)
   - Metric: 10ms (100 updates/sec for smooth metric display)

2. **String Building:**
   - Uses list comprehension + join (not concatenation)
   - Example: `''.join(line_parts)`

3. **Display Updates:**
   - Only redraws time portion (8 lines)
   - Doesn't redraw static borders/labels
   - Uses Windows Console API for efficient cursor positioning
   - Reduces flicker and improves performance

4. **Cursor Management:**
   - Hides cursor during updates via SetConsoleCursorInfo
   - Shows on exit (even on error via context manager)
   - Prevents cursor flicker

5. **Windows-Specific Optimizations:**
   - Direct kernel32 API calls instead of ANSI codes
   - Native console buffer manipulation
   - winsound.Beep() for hardware-level audio

---

## Windows-Specific Features

### Console API Integration

**ctypes Structures:**
```python
class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("bVisible", wintypes.BOOL)]
```

**kernel32.dll Functions Used:**
- `GetStdHandle(STD_OUTPUT_HANDLE)` - Get console handle
- `SetConsoleCursorInfo()` - Control cursor visibility
- `SetConsoleCursorPosition()` - Move cursor to position

### Audio System

**Primary Method:** winsound.Beep(frequency, duration)
- Windows standard library module
- Direct PC speaker/audio output
- Precise frequency control (37-32767 Hz)
- Duration in milliseconds

**Fallback:** Terminal bell (`\a`)
- Used if winsound fails
- Simple beep sound
- Less control over sound

### File System Paths

**Windows Path Conventions:**
- Uses `Path.home() / 'AppData' / 'Roaming'` for config
- Uses `Path.home() / 'AppData' / 'Local'` for cache/logs
- Supports both installed and standalone modes
- Automatic directory creation via `Path.mkdir(parents=True, exist_ok=True)`

---

## Summary

**Total Lines:** 1,170 lines

**Core Components:**
1. **Logger** - Debug logging
2. **ConsoleManager** - Terminal control (Windows Console API)
3. **ConfigManager** - Windows-aware config management
4. **DisplayManager** - ASCII art rendering
5. **CountdownTimer** - Timer logic & execution

**Key Features:**
- Flexible time input parsing
- Customizable ASCII art
- Windows AppData directory support
- Efficient display updates via Windows Console API
- Graceful error handling
- Loop mode for repeated timers
- Clock mode for 24-hour time display
- Metric time "joke mode"
- winsound-based audio alerts

**Windows-Specific Adaptations:**
- Windows Console API (kernel32) instead of ANSI escape codes
- winsound module instead of 'beep' command
- %APPDATA% paths instead of XDG directories
- os.system('cls') instead of ANSI clear codes
- ctypes structures for console manipulation
- Dual-mode operation (installed vs standalone)

**Dependencies:**
- Python 3.6+ standard library only
- Windows-specific: ctypes, winsound
- No external packages required

**File Locations:**

*Installed:*
- Config: `%APPDATA%\wincountdown\config.json`
- Logs: `%LOCALAPPDATA%\wincountdown\debug.log`

*Standalone:*
- Config: `<script-dir>\config.json`
- Logs: `<script-dir>\debug.log`
