# Installation & Testing Guide

Quick guide for installing and testing wincountdown on Windows.

## Quick Start (Testing Without Installation)

```cmd
# Command Prompt
python wincountdown.py 10s

# Test with help
python wincountdown.py --help

# Test clock mode
python wincountdown.py --clock
```

```powershell
# PowerShell
python wincountdown.py 10s

# Test with help
python wincountdown.py --help

# Test clock mode
python wincountdown.py --clock
```

## Installation Methods

### Method 1: pip Installation (Recommended)

Install wincountdown as a Python package for system-wide access.

```cmd
# Command Prompt - Install from local directory
cd d:\GITHUB\wincountdown-windows
pip install .

# Now available as system command from anywhere
wincountdown 5m
```

```powershell
# PowerShell - Install from local directory
cd d:\GITHUB\wincountdown-windows
pip install .

# Now available as system command from anywhere
wincountdown 5m
```

**Benefits:**
- Works from any directory
- Config stored in `%APPDATA%\wincountdown\`
- Easy to uninstall: `pip uninstall wincountdown`
- Easy to upgrade: `git pull && pip install --upgrade .`

**Configuration and log file locations:**
```
%APPDATA%\wincountdown\config.json       # C:\Users\USERNAME\AppData\Roaming\wincountdown\config.json
%LOCALAPPDATA%\wincountdown\debug.log    # C:\Users\USERNAME\AppData\Local\wincountdown\debug.log
```

### Method 2: Standalone Python Script

Run the script directly without installation. Requires Python 3.6+.

```cmd
# Command Prompt
cd d:\GITHUB\wincountdown-windows
python wincountdown.py 5m
```

```powershell
# PowerShell
cd d:\GITHUB\wincountdown-windows
python wincountdown.py 5m
```

**Benefits:**
- No installation needed
- Config stored in script directory (`.\config.json`)
- Good for testing or portable use
- Easy to modify and test changes

**Configuration and log file locations:**
```
.\config.json    # Configuration (in script directory)
.\debug.log      # Debug logs (in script directory)
```

### Method 3: PyInstaller Executable

Create a standalone `.exe` file that doesn't require Python installation.

```cmd
# Command Prompt - Build executable
cd d:\GITHUB\wincountdown-windows
pip install pyinstaller
pyinstaller --onefile --name wincountdown wincountdown.py

# Executable will be in dist\ folder
cd dist
wincountdown 5m
```

```powershell
# PowerShell - Build executable
cd d:\GITHUB\wincountdown-windows
pip install pyinstaller
pyinstaller --onefile --name wincountdown wincountdown.py

# Executable will be in dist\ folder
cd dist
.\wincountdown 5m
```

**To add to PATH for system-wide access:**

1. Copy `wincountdown.exe` to a permanent location (e.g., `C:\Tools\wincountdown\`)
2. Open System Properties → Environment Variables
3. Under "User variables" or "System variables", find `Path` and click Edit
4. Click New and add the folder path (e.g., `C:\Tools\wincountdown`)
5. Click OK to save
6. Restart Command Prompt or PowerShell
7. Test: `wincountdown 5m` from any directory

**Benefits:**
- No Python installation required on target system
- Portable - single executable file
- Config stored in executable directory
- Can be distributed to users without Python

**Configuration and log file locations:**
```
.\config.json    # Configuration (in executable directory)
.\debug.log      # Debug logs (in executable directory)
```

### Method 4: setup.py Installation

Alternative installation method using setup.py directly.

```cmd
# Command Prompt
cd d:\GITHUB\wincountdown-windows
python setup.py install

# Now available as system command
wincountdown 5m
```

```powershell
# PowerShell
cd d:\GITHUB\wincountdown-windows
python setup.py install

# Now available as system command
wincountdown 5m
```

## Post-Installation Testing

### 1. Basic Functionality

```cmd
# Command Prompt - 10 second countdown
wincountdown 10s

# Should display large ASCII numbers counting down
# Should beep when finished (Windows winsound module)
```

```powershell
# PowerShell - 10 second countdown
wincountdown 10s

# Should display large ASCII numbers counting down
# Should beep when finished (Windows winsound module)
```

### 2. Check Config Creation

**For pip installation:**

```cmd
# Command Prompt - Run once to create config
wincountdown 5s

# Check config was created
dir "%APPDATA%\wincountdown\config.json"
type "%APPDATA%\wincountdown\config.json"
```

```powershell
# PowerShell - Run once to create config
wincountdown 5s

# Check config was created
Get-Item "$env:APPDATA\wincountdown\config.json"
Get-Content "$env:APPDATA\wincountdown\config.json"
```

**For standalone script or executable:**

```cmd
# Command Prompt - Check config in current directory
dir config.json
type config.json
```

```powershell
# PowerShell - Check config in current directory
Get-Item .\config.json
Get-Content .\config.json
```

### 3. Test Audio Alerts

Windows uses the built-in `winsound` module (no additional packages required).

```cmd
# Command Prompt - Test custom beep pattern
wincountdown 5s -f 1000 -b 3 -d 500

# Test silent mode (no beep)
wincountdown 5s --silent
```

```powershell
# PowerShell - Test custom beep pattern
wincountdown 5s -f 1000 -b 3 -d 500

# Test silent mode (no beep)
wincountdown 5s --silent
```

**Note:** Windows beep functionality uses the Windows Console API through `winsound.Beep()`. No external packages like the Linux `beep` utility are needed.

### 4. Test Clock Mode

```cmd
# Command Prompt - Display current time in 24-hour format
wincountdown --clock

# Press Ctrl+C to exit
```

```powershell
# PowerShell - Display current time in 24-hour format
wincountdown --clock

# Press Ctrl+C to exit
```

### 5. Test Loop Mode

```cmd
# Command Prompt - Auto-restart countdown
wincountdown 5s -l

# Press Ctrl+C to exit
```

```powershell
# PowerShell - Auto-restart countdown
wincountdown 5s -l

# Press Ctrl+C to exit
```

### 6. Test Debug Mode

**For pip installation:**

```cmd
# Command Prompt - Enable debug logging
wincountdown 10s --debug

# Check log file
type "%LOCALAPPDATA%\wincountdown\debug.log"
```

```powershell
# PowerShell - Enable debug logging
wincountdown 10s --debug

# Check log file
Get-Content "$env:LOCALAPPDATA\wincountdown\debug.log"
```

**For standalone script or executable:**

```cmd
# Command Prompt - Check log in current directory
type debug.log
```

```powershell
# PowerShell - Check log in current directory
Get-Content .\debug.log
```

## Windows Compatibility

### Tested Platforms

- Windows 10 (all versions)
- Windows 11 (all versions)
- Windows Server 2016 and later

### Terminal Compatibility

**Recommended terminals:**
- **Windows Terminal** (best support for ANSI colors and Unicode)
- Command Prompt (cmd.exe)
- PowerShell 5.1 and PowerShell 7+
- Windows PowerShell ISE

**Terminal features:**
- ANSI color support: Full support in Windows 10/11
- Unicode characters: Supported (UTF-8 encoding recommended)
- Cursor hiding: Supported via Windows Console API

**For best experience:**
1. Use Windows Terminal (available in Microsoft Store)
2. Set terminal width to at least 120 characters
3. Use a monospace font with Unicode support (e.g., Cascadia Code, Consolas)

### Python Requirements

- Python 3.6 or higher
- Standard library only (no external dependencies)
- Built-in modules used:
  - `winsound` - For beep alerts (Windows-specific, built-in)
  - `ctypes` - For Windows Console API access
  - `os`, `sys`, `time`, `json`, `argparse`, `datetime`

## Uninstallation

### If installed via pip

```cmd
# Command Prompt
pip uninstall wincountdown
```

```powershell
# PowerShell
pip uninstall wincountdown
```

### If installed via setup.py

```cmd
# Command Prompt - Find installation location
pip show wincountdown

# Uninstall
pip uninstall wincountdown
```

```powershell
# PowerShell - Find installation location
pip show wincountdown

# Uninstall
pip uninstall wincountdown
```

### If using standalone executable

```cmd
# Command Prompt - Just delete the executable
del C:\Tools\wincountdown\wincountdown.exe

# Remove from PATH if added
# Edit Environment Variables and remove the path entry
```

```powershell
# PowerShell - Just delete the executable
Remove-Item C:\Tools\wincountdown\wincountdown.exe

# Remove from PATH if added
# Edit Environment Variables and remove the path entry
```

### Remove configuration files

**For pip installation:**

```cmd
# Command Prompt - Remove config and cache
rmdir /s /q "%APPDATA%\wincountdown"
rmdir /s /q "%LOCALAPPDATA%\wincountdown"
```

```powershell
# PowerShell - Remove config and cache
Remove-Item "$env:APPDATA\wincountdown" -Recurse -Force
Remove-Item "$env:LOCALAPPDATA\wincountdown" -Recurse -Force
```

**For standalone script or executable:**

```cmd
# Command Prompt - Remove files in script/exe directory
del config.json
del debug.log
```

```powershell
# PowerShell - Remove files in script/exe directory
Remove-Item config.json
Remove-Item debug.log
```

## Troubleshooting

### Command not found

**For pip installation:**

```cmd
# Command Prompt - Check if installed
where wincountdown

# Check pip installation
pip show wincountdown

# Check Python Scripts directory is in PATH
echo %PATH%
# Should include: C:\Users\USERNAME\AppData\Local\Programs\Python\PythonXX\Scripts
```

```powershell
# PowerShell - Check if installed
Get-Command wincountdown

# Check pip installation
pip show wincountdown

# Check Python Scripts directory is in PATH
$env:PATH
# Should include: C:\Users\USERNAME\AppData\Local\Programs\Python\PythonXX\Scripts
```

**Solution:** Add Python Scripts directory to PATH:
1. Find Python installation: `where python` or `Get-Command python`
2. Typical location: `C:\Users\USERNAME\AppData\Local\Programs\Python\PythonXX\Scripts`
3. Add to PATH via System Properties → Environment Variables
4. Restart terminal

### ImportError or ModuleNotFoundError

```cmd
# Command Prompt - Check Python version (requires 3.6+)
python --version

# Verify installation
pip show wincountdown

# Check if winsound is available (should be built-in on Windows)
python -c "import winsound; print('winsound OK')"
```

```powershell
# PowerShell - Check Python version (requires 3.6+)
python --version

# Verify installation
pip show wincountdown

# Check if winsound is available (should be built-in on Windows)
python -c "import winsound; print('winsound OK')"
```

### Beep doesn't work

**Windows uses built-in winsound module (no external packages needed).**

```cmd
# Command Prompt - Test winsound directly
python -c "import winsound; winsound.Beep(800, 500)"

# Check system volume
# Open Volume Mixer (right-click speaker icon)
# Verify system sounds are not muted

# Try different frequency
wincountdown 5s -f 1000

# Check if silent mode is accidentally enabled
type "%APPDATA%\wincountdown\config.json" | findstr silent
```

```powershell
# PowerShell - Test winsound directly
python -c "import winsound; winsound.Beep(800, 500)"

# Check system volume
# Open Volume Mixer (right-click speaker icon)
# Verify system sounds are not muted

# Try different frequency
wincountdown 5s -f 1000

# Check if silent mode is accidentally enabled
Get-Content "$env:APPDATA\wincountdown\config.json" | Select-String "silent"
```

**Common issues:**
- System volume muted or too low
- System sounds disabled in Windows settings
- Running in Windows Server Core (no audio support)
- Virtual machine without audio drivers

### Config file not created

```cmd
# Command Prompt - Check permissions
dir "%APPDATA%"

# Manually create directory (for pip installation)
mkdir "%APPDATA%\wincountdown"

# Run program again
wincountdown 5s
```

```powershell
# PowerShell - Check permissions
Get-Item "$env:APPDATA"

# Manually create directory (for pip installation)
New-Item -ItemType Directory -Path "$env:APPDATA\wincountdown" -Force

# Run program again
wincountdown 5s
```

**For standalone script:**
```cmd
# Command Prompt - Check write permissions in current directory
cd
dir

# Run with elevated permissions if needed
```

### Display issues (colors, cursor, ANSI codes)

```cmd
# Command Prompt - Test ANSI support
echo [31mRed Text[0m

# Enable ANSI on older Windows 10 versions
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1
```

```powershell
# PowerShell - Test ANSI support
Write-Host "`e[31mRed Text`e[0m"

# Check terminal
$PSVersionTable.PSVersion
# Use PowerShell 5.1+ or PowerShell 7+
```

**Solutions:**
- Use Windows Terminal (best ANSI and Unicode support)
- Update to latest Windows 10/11 version
- Enable ANSI support in registry (see above)
- Maximize terminal window (minimum 120 characters wide)

### Unicode characters not displaying

```cmd
# Command Prompt - Set code page to UTF-8
chcp 65001

# Make permanent: Set console font to Unicode-compatible font
# Right-click title bar → Properties → Font → Select "Consolas" or "Cascadia Code"
```

```powershell
# PowerShell - Set output encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Add to PowerShell profile to make permanent
notepad $PROFILE
# Add line: [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

**Recommended solutions:**
- Use Windows Terminal (best Unicode support)
- Use Cascadia Code, Cascadia Mono, or Consolas font
- Save config.json as UTF-8 encoding
- For custom ASCII art, use simple ASCII characters instead of Unicode blocks

### PyInstaller executable issues

```cmd
# Command Prompt - Test if Python is bundled correctly
wincountdown.exe --help

# If "VCRUNTIME140.dll missing" error:
# Download and install Microsoft Visual C++ Redistributable
# https://aka.ms/vs/17/release/vc_redist.x64.exe
```

**Common PyInstaller issues:**
- Antivirus false positives: Add exception for wincountdown.exe
- Missing DLL files: Install Visual C++ Redistributable
- Large file size: Normal for --onefile (includes Python runtime)
- Slow startup: Normal for --onefile (extracts to temp directory)

### Permission denied errors

```cmd
# Command Prompt - Run as Administrator if needed
# Right-click Command Prompt → "Run as administrator"

# For pip installation
pip install --user .

# Check file permissions
icacls wincountdown.py
```

```powershell
# PowerShell - Run as Administrator if needed
# Right-click PowerShell → "Run as administrator"

# For pip installation
pip install --user .

# Check file permissions
Get-Acl wincountdown.py | Format-List
```

## Development Setup

```cmd
# Command Prompt - Clone repository
git clone https://github.com/Stropitor/wincountdown-windows.git
cd wincountdown-windows

# Run directly (no installation)
python wincountdown.py 10s

# Edit code
notepad wincountdown.py

# Test changes immediately
python wincountdown.py 5s
```

```powershell
# PowerShell - Clone repository
git clone https://github.com/Stropitor/wincountdown-windows.git
cd wincountdown-windows

# Run directly (no installation)
python wincountdown.py 10s

# Edit code
code wincountdown.py  # VS Code
# or
notepad wincountdown.py

# Test changes immediately
python wincountdown.py 5s
```

## Building Distributable Package

### Create standalone executable

```cmd
# Command Prompt - Install PyInstaller
pip install pyinstaller

# Build single executable file
pyinstaller --onefile --name wincountdown wincountdown.py

# Output: dist\wincountdown.exe
# Can be distributed without Python installation
```

```powershell
# PowerShell - Install PyInstaller
pip install pyinstaller

# Build single executable file
pyinstaller --onefile --name wincountdown wincountdown.py

# Output: dist\wincountdown.exe
# Can be distributed without Python installation
```

### Create distributable package with PyInstaller

```cmd
# Command Prompt - Build with additional files
pyinstaller --onefile ^
  --name wincountdown ^
  --add-data "README.md;." ^
  --add-data "LICENSE;." ^
  wincountdown.py

# Clean build files
rmdir /s /q build
del wincountdown.spec
```

```powershell
# PowerShell - Build with additional files
pyinstaller --onefile `
  --name wincountdown `
  --add-data "README.md;." `
  --add-data "LICENSE;." `
  wincountdown.py

# Clean build files
Remove-Item -Recurse -Force build
Remove-Item wincountdown.spec
```

## Next Steps

1. **Customize config file:**
   - Pip installation: `%APPDATA%\wincountdown\config.json`
   - Standalone: `.\config.json`

2. **Set default beep sounds, loop mode, etc.**

3. **Customize ASCII art digits**

4. **Create shortcuts or aliases:**

**Command Prompt (doskey macros):**
```cmd
# Create macros (valid for current session)
doskey pomo=wincountdown 25m -l
doskey break=wincountdown 5m

# Save to file and load on startup
echo doskey pomo=wincountdown 25m -l > %USERPROFILE%\aliases.cmd
echo doskey break=wincountdown 5m >> %USERPROFILE%\aliases.cmd

# Add to Command Prompt startup:
# Run → regedit
# HKEY_CURRENT_USER\Software\Microsoft\Command Processor
# Create String Value: AutoRun = %USERPROFILE%\aliases.cmd
```

**PowerShell (aliases in profile):**
```powershell
# Edit PowerShell profile
notepad $PROFILE

# Add aliases
Set-Alias pomo 'wincountdown 25m -l'
Set-Alias break 'wincountdown 5m'

# Or create functions for more flexibility
function pomo { wincountdown 25m -l }
function break { wincountdown 5m }

# Save and reload
. $PROFILE
```

**Desktop shortcuts:**
1. Right-click Desktop → New → Shortcut
2. Target: `C:\Users\USERNAME\AppData\Local\Programs\Python\PythonXX\Scripts\wincountdown.exe 25m -l`
3. Name: "Pomodoro Timer"
4. Optional: Change icon (right-click → Properties → Change Icon)

## Getting Help

```cmd
# Command Prompt - Show help
wincountdown --help

# Enable debug mode for troubleshooting
wincountdown 10s --debug
type "%LOCALAPPDATA%\wincountdown\debug.log"
```

```powershell
# PowerShell - Show help
wincountdown --help

# Enable debug mode for troubleshooting
wincountdown 10s --debug
Get-Content "$env:LOCALAPPDATA\wincountdown\debug.log"
```

## Additional Resources

- **GitHub Repository:** https://github.com/Stropitor/wincountdown-windows
- **Issue Tracker:** Report bugs and request features
- **Windows Terminal:** https://aka.ms/terminal (recommended)
- **Python Downloads:** https://www.python.org/downloads/

## Tips for Windows Users

1. **Use Windows Terminal** for best experience (ANSI colors, Unicode support)
2. **Set terminal width** to at least 120 characters for proper display
3. **Pin to taskbar** for quick access (right-click wincountdown.exe → Pin to taskbar)
4. **Create scheduled tasks** with Task Scheduler for recurring timers
5. **No beep package needed** - Windows uses built-in winsound module
6. **Config location varies** based on installation method (pip vs standalone)
7. **PowerShell execution policy** - May need to allow scripts: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
