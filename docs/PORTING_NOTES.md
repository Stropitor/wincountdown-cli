# Windows Implementation Notes

This document outlines the Windows-specific implementation details and differences from the Linux version.

## Summary of Windows-Specific Implementation

### 1. Import Statements

**Windows Version:**
```python
import ctypes
import winsound
from ctypes import wintypes
```

**Linux Version:**
```python
import subprocess
from pathlib import Path
```

### 2. Terminal/Console Control

**Windows:** Windows Console API using `ctypes.windll.kernel32`
```python
class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("bVisible", wintypes.BOOL)]

class ConsoleManager:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.h_console = self.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def hide_cursor(self):
        cursor_info = CONSOLE_CURSOR_INFO()
        cursor_info.dwSize = CURSOR_SIZE
        cursor_info.bVisible = False
        self.kernel32.SetConsoleCursorInfo(self.h_console, ctypes.byref(cursor_info))

    def set_position(self, x, y):
        coord = COORD(x, y)
        self.kernel32.SetConsoleCursorPosition(self.h_console, coord)
```

**Linux:** ANSI escape codes (universal terminal standard)
```python
ANSI_HIDE_CURSOR = '\033[?25l'
ANSI_SHOW_CURSOR = '\033[?25h'
ANSI_CLEAR_SCREEN = '\033[2J\033[H'

def ansi_move_cursor(x, y):
    return f'\033[{y+1};{x+1}H'

class ConsoleManager:
    def hide_cursor(self):
        print(ANSI_HIDE_CURSOR, end='', flush=True)
```

### 3. Audio System

**Windows:** `winsound.Beep(frequency, duration)` - Built-in module
```python
winsound.Beep(freq, duration)
# No external dependencies needed
```

**Linux:** `beep` command with fallback to terminal bell
```python
subprocess.run(['beep', '-f', str(freq), '-l', str(duration)],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# Fallback: print('\a')
# Requires beep package installation: sudo pacman -S beep
```

### 4. Screen Clearing

**Windows:** `os.system('cls')`

**Linux:** `os.system('clear')`

### 5. Configuration File Paths

**Windows:** Uses AppData directories (installed) or script directory (standalone)
```python
def __init__(self, script_dir):
    if is_installed_as_package():
        # Installed via pip
        appdata_dir = os.getenv('APPDATA')
        config_dir = os.path.join(appdata_dir, 'wincountdown')
        cache_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'wincountdown')
    else:
        # Standalone mode
        config_dir = script_dir
        cache_dir = script_dir

    self.config_file = os.path.join(config_dir, "config.json")
    self.debug_log_file = os.path.join(cache_dir, "debug.log")
```

**Linux:** XDG-compliant directories
```python
def __init__(self, script_dir=None):
    config_dir = Path.home() / '.config' / 'wincountdown'
    cache_dir = Path.home() / '.cache' / 'wincountdown'

    config_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    self.config_file = str(config_dir / 'config.json')
    self.debug_log_file = str(cache_dir / 'debug.log')
```

### 6. File Locations

| Purpose | Windows Location (Installed) | Windows Location (Standalone) | Linux Location (XDG) |
|---------|------------------------------|-------------------------------|----------------------|
| Config | `%APPDATA%\wincountdown\config.json` | `.\config.json` | `~/.config/wincountdown/config.json` |
| Debug Log | `%LOCALAPPDATA%\wincountdown\debug.log` | `.\debug.log` | `~/.cache/wincountdown/debug.log` |

## Windows-Specific Files

### 1. setup.py
Python packaging file for installation via pip or setuptools.

**Key features:**
- Entry point: `wincountdown` command
- Python 3.6+ required
- No external dependencies (only stdlib + built-in winsound)
- Windows-specific classifiers

### 2. changelog.md (Windows-specific)
Version history and feature updates.

**Key features:**
- Documents clock mode addition
- Documents --debug flag addition
- Technical implementation notes

### 3. wincountdown-config.json
Example configuration file in root directory.

**Key features:**
- Heavily commented JSON (90+ comment lines)
- Complete ASCII art definitions
- All default settings documented

## Technical Implementation Details

### Windows Console API vs ANSI Escape Codes

**Windows Console API Advantages:**
- Native Windows support
- Direct hardware control
- Precise cursor positioning
- No terminal emulator dependency

**Windows Console API Disadvantages:**
- Windows-only (not portable)
- Requires ctypes and WinAPI knowledge
- More complex code

**Implementation Details:**
- Uses `kernel32.dll` via ctypes
- `GetStdHandle(STD_OUTPUT_HANDLE)` to get console handle
- `SetConsoleCursorInfo()` for cursor visibility
- `SetConsoleCursorPosition()` for cursor movement
- `COORD` structure for position coordinates
- `CONSOLE_CURSOR_INFO` structure for cursor properties

### Audio: winsound vs beep

**Windows winsound Advantages:**
- Built-in Python module (no installation required)
- Full control over frequency (Hz) and duration (ms)
- Works on all Windows systems
- Frequency range: 37 Hz to 32,767 Hz
- Duration in milliseconds

**Windows winsound Implementation:**
```python
import winsound

def play_beeps(self, freq, count, duration, gap, silent, loop):
    if silent:
        return

    beep_count = 1 if loop else count

    for i in range(beep_count):
        try:
            winsound.Beep(freq, duration)
        except RuntimeError:
            print('\a', end='', flush=True)  # Fallback to terminal bell

        if i < beep_count - 1:
            time.sleep(gap / 1000.0)
```

**Linux beep Disadvantages:**
- Requires external package installation
- May require permissions configuration
- Kernel module dependencies

## Windows Compatibility

### Supported Windows Versions
- Windows 10 (tested)
- Windows 11 (tested)
- Windows 8.1 (should work)
- Windows 7 (should work, but untested)

### Terminal Compatibility
- **Windows Terminal** (recommended) - Full support, best experience
- **Command Prompt (cmd.exe)** - Full support
- **PowerShell** - Full support
- **PowerShell Core (pwsh)** - Full support
- **ConEmu** - Full support
- **Cmder** - Full support

### Known Limitations
- Requires Windows Console API support (all modern Windows)
- Audio requires PC speaker or audio output device
- Some older Windows versions may have limited frequency range

## Dual-Mode Operation

The Windows version supports two operation modes:

### 1. Installed Mode (via pip)
```
Config: %APPDATA%\wincountdown\config.json
Debug:  %LOCALAPPDATA%\wincountdown\debug.log
```

**Detection:** Checks if running from Python's Scripts directory

### 2. Standalone Mode (run as script)
```
Config: .\config.json
Debug:  .\debug.log
```

**Detection:** Running directly from script directory

**Implementation:**
```python
def is_installed_as_package():
    script_path = os.path.abspath(sys.argv[0])
    python_scripts_dir = os.path.join(sys.prefix, 'Scripts')
    return script_path.startswith(python_scripts_dir)
```

## Testing Recommendations

1. **Basic functionality:**
   ```cmd
   wincountdown 10s
   ```

2. **Config file creation:**
   ```cmd
   dir "%APPDATA%\wincountdown\config.json"
   ```

3. **Audio with custom frequency:**
   ```cmd
   wincountdown 5s -f 1000 -b 3
   ```

4. **Clock mode:**
   ```cmd
   wincountdown --clock
   ```

5. **Debug logging:**
   ```cmd
   wincountdown 5s --debug
   type "%LOCALAPPDATA%\wincountdown\debug.log"
   ```

6. **Standalone mode:**
   ```cmd
   python wincountdown.py 10s
   ```

7. **PyInstaller executable:**
   ```cmd
   pyinstaller --onefile wincountdown.py
   dist\wincountdown.exe 10s
   ```

## PowerShell Testing

```powershell
# Basic test
wincountdown 10s

# Config location
Get-Item "$env:APPDATA\wincountdown\config.json"

# Debug log
Get-Content "$env:LOCALAPPDATA\wincountdown\debug.log"

# Clock mode
wincountdown --clock

# Custom frequency
wincountdown 5s -f 1500 -b 5
```

## Known Issues & Limitations

1. **Audio range:** Windows winsound has hardware limitations on some systems
2. **Terminal buffer:** Large displays may require terminal buffer size adjustment
3. **Unicode:** Some terminal configurations may not display box-drawing characters correctly
4. **Frequency accuracy:** Actual beep frequency may vary on different hardware

## Future Considerations

1. **Cross-platform version:** Could use platform detection to support both OSes in one codebase
2. **Alternative audio:** Could add support for WAV file playback
3. **Modern Terminal features:** Could leverage Windows Terminal's enhanced ANSI support
4. **Registry integration:** Could store config in Windows Registry as alternative
5. **Windows notifications:** Could add Windows 10/11 toast notifications

## PyInstaller Deployment

The Windows version can be compiled to a standalone .exe:

```cmd
pip install pyinstaller
pyinstaller --onefile --name wincountdown wincountdown.py
```

**Advantages:**
- No Python installation required on target system
- Single .exe file distribution
- Faster startup time
- Easy deployment

**Considerations:**
- Larger file size (~10MB)
- Antivirus false positives possible
- Config file still in %APPDATA% by default

## Distribution Methods

1. **pip install** - Standard Python package installation
2. **Standalone .py** - Run directly with Python interpreter
3. **PyInstaller .exe** - Compiled executable (no Python needed)
4. **Chocolatey** - Windows package manager (future possibility)
5. **winget** - Windows Package Manager (future possibility)

## Resources

- [Windows Console API Documentation](https://docs.microsoft.com/en-us/windows/console/console-functions)
- [ctypes Documentation](https://docs.python.org/3/library/ctypes.html)
- [winsound Documentation](https://docs.python.org/3/library/winsound.html)
- [Python Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [PyInstaller Manual](https://pyinstaller.readthedocs.io/)
