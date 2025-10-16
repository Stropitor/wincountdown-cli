import sys
import time
import os
import ctypes
import winsound
import argparse
import json
import shlex
from ctypes import wintypes
from datetime import datetime

# ============================================================================
# CONSTANTS
# ============================================================================

# Console constants
STD_OUTPUT_HANDLE = -11
CURSOR_SIZE = 100
BORDER_WIDTH = 115
ASCII_HEIGHT = 8

# Time constants  
MAX_STANDARD_SECONDS = 359999  # 99:59:59
MAX_METRIC_MILLISECONDS = 999999000  # 99:99:99 metric

# Display constants
UPDATE_INTERVAL_STANDARD = 0.05
UPDATE_INTERVAL_METRIC = 0.01

# Default ASCII art for digits
DEFAULT_ASCII_DIGITS = {
    '0': [
        " ######### ",
        "###     ###",
        "###     ###",
        "###     ###",
        "###     ###",
        "###     ###",
        "###     ###",
        " ######### "
    ],
    '1': [
        "    ###    ",
        "  #####    ",
        "    ###    ",
        "    ###    ",
        "    ###    ",
        "    ###    ",
        "    ###    ",
        "###########"
    ],
    '2': [
        " ######### ",
        "###     ###",
        "        ###",
        "      ###  ",
        "    ###    ",
        "  ###      ",
        " ###       ",
        "###########"
    ],
    '3': [
        "###########",
        "        ###",
        "        ###",
        "  #########",
        "        ###",
        "        ###",
        "        ###",
        "###########"
    ],
    '4': [
        "     ##### ",
        "    ###### ",
        "   ### ### ",
        "  ###  ### ",
        " ###   ### ",
        "###########",
        "       ### ",
        "       ### "
    ],
    '5': [
        "###########",
        "###        ",
        "###        ",
        "###########",
        "        ###",
        "        ###",
        "###     ###",
        " ######### "
    ],
    '6': [
        "  #########",
        " ###       ",
        "###        ",
        "###########",
        "###     ###",
        "###     ###",
        "###     ###",
        " ######### "
    ],
    '7': [
        "###########",
        "        ###",
        "       ### ",
        "      ###  ",
        "     ###   ",
        "    ###    ",
        "   ###     ",
        "   ###     "
    ],
    '8': [
        " ######### ",
        "###     ###",
        "###     ###",
        " ######### ",
        "###     ###",
        "###     ###",
        "###     ###",
        " ######### "
    ],
    '9': [
        " ######### ",
        "###     ###",
        "###     ###",
        "###     ###",
        " ##########",
        "        ###",
        "       ### ",
        "########   "
    ],
    ':': [
        "           ",
        "    ###    ",
        "    ###    ",
        "           ",
        "           ",
        "    ###    ",
        "    ###    ",
        "           "
    ]
}

# Default configuration
DEFAULT_CONFIG = {
    "debug_mode": False,
    "default_frequency": 800,
    "default_beeps": 3,
    "default_duration": 1000,
    "default_gap": 300,
    "default_silent": False,
    "default_loop": False,
    "default_metric": False,
    "enable_no_args_default": False,
    "no_args_default_command": "help",
    "enable_time_only_defaults": False,
    "time_only_default_flags": [],
    "ascii_digits": DEFAULT_ASCII_DIGITS
}

# ============================================================================
# WINDOWS CONSOLE API STRUCTURES
# ============================================================================

class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("bVisible", wintypes.BOOL)]

# ============================================================================
# LOGGER CLASS
# ============================================================================

class Logger:
    """Simple logger that can be enabled/disabled via config"""
    
    def __init__(self):
        self.enabled = False
        self.file_path = None
        
    def setup(self, enabled, file_path):
        """Setup logger with debug mode and file path"""
        self.enabled = enabled
        self.file_path = file_path
        
        if enabled and file_path and os.path.exists(file_path):
            os.remove(file_path)
    
    def log(self, message):
        """Log message if debugging is enabled"""
        if not self.enabled:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}\n"
        
        if self.file_path:
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(log_message)
        print(log_message.rstrip())

# Global logger instance
logger = Logger()

# ============================================================================
# CONSOLE MANAGER CLASS
# ============================================================================

class ConsoleManager:
    """Handles all console/terminal operations"""
    
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.h_console = self.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        
    def hide_cursor(self):
        """Hide the console cursor to prevent flickering"""
        cursor_info = CONSOLE_CURSOR_INFO()
        cursor_info.dwSize = CURSOR_SIZE
        cursor_info.bVisible = False
        self.kernel32.SetConsoleCursorInfo(self.h_console, ctypes.byref(cursor_info))
    
    def show_cursor(self):
        """Show the console cursor again"""
        cursor_info = CONSOLE_CURSOR_INFO()
        cursor_info.dwSize = CURSOR_SIZE
        cursor_info.bVisible = True
        self.kernel32.SetConsoleCursorInfo(self.h_console, ctypes.byref(cursor_info))
        
    def set_position(self, x, y):
        """Move cursor to specific position without clearing"""
        coord = COORD(x, y)
        self.kernel32.SetConsoleCursorPosition(self.h_console, coord)
        
    def clear_screen(self):
        """Clear screen"""
        os.system('cls')
        
    def __enter__(self):
        """Context manager entry - hide cursor"""
        self.hide_cursor()
        return self
        
    def __exit__(self, *args):
        """Context manager exit - show cursor"""
        self.show_cursor()

# ============================================================================
# CONFIG MANAGER CLASS
# ============================================================================

class ConfigManager:
    """Handles configuration loading and creation"""
    
    def __init__(self, script_dir):
        self.config_file = os.path.join(script_dir, "wincountdown-config.json")
        self.debug_log_file = os.path.join(script_dir, "wincountdown-debug.log")
        
    def create_config_content(self):
        """Create a configuration file with detailed comments"""
        return '''{
    "//": "================================================================",
    "//1": "WINCOUNTDOWN CONFIGURATION FILE",
    "//2": "================================================================",
    "//3": "This file controls default settings for the wincountdown timer.",
    "//4": "Edit values below to customize behavior.",
    "//5": "",
    
    "//debug_section": "--- DEBUG MODE ---",
    "//debug_desc": "Enable debug logging to wincountdown-debug.log for troubleshooting",
    
    "debug_mode": false,
    "//debug_note": "Set to true to enable detailed debug logging. Creates wincountdown-debug.log file with timestamps.",
    
    "//separator1": "",
    "//basic": "--- BASIC DEFAULTS ---",
    "//basic1": "These settings apply to all countdown executions unless overridden by command-line flags",
    
    "default_frequency": 800,
    "//freq": "Beep frequency in Hz (range: 37-32767). Common: 440 (A note), 800 (default), 1000 (high)",
    
    "default_beeps": 3,
    "//beeps": "Number of beeps when countdown finishes (minimum: 1)",
    
    "default_duration": 1000,
    "//duration": "Duration of each beep in milliseconds (1000ms = 1 second)",
    
    "default_gap": 300,
    "//gap": "Gap between beeps in milliseconds (only applies when beeps > 1)",
    
    "default_silent": false,
    "//silent": "Silent mode: true = no beeps by default, false = beeps enabled",
    
    "default_loop": false,
    "//loop": "Loop mode: true = auto-restart after finish, false = stop after finish",
    
    "default_metric": false,
    "//metric": "Metric mode (joke): true = display in metric time (1h=100m, 1m=100s), false = normal time",
    
    "//separator2": "",
    "//adv": "--- ADVANCED BEHAVIORS ---",
    "//adv1": "Configure these options to customize behavior for specific use cases",
    "//adv2": "",
    
    "//noargs": "=== NO ARGUMENTS BEHAVIOR ===",
    "//noargs1": "Controls what happens when you run 'wincountdown' with no arguments",
    "//noargs2": "By default (when disabled), it shows the help screen",
    
    "enable_no_args_default": false,
    "//enable_noargs": "Set to true to enable custom behavior when no arguments provided",
    
    "no_args_default_command": "help",
    "//noargs_cmd1": "What to run when 'wincountdown' executed with no arguments:",
    "//noargs_cmd2": "  - 'help' = show help screen (default)",
    "//noargs_cmd3": "  - Any time string like '5m', '25m', '1h30m'",
    "//noargs_cmd4": "  - Can include flags: '10m -l' = 10min looping timer",
    "//noargs_cmd5": "Example: Set to '25m' to start a 25-minute timer by default",
    
    "//separator3": "",
    "//timeonly": "=== TIME-ONLY ARGUMENTS BEHAVIOR ===",
    "//timeonly1": "Controls what happens when you provide ONLY a time argument (no flags)",
    "//timeonly2": "Example: Make 'wincountdown 5m' automatically run as 'wincountdown 5m -l -s'",
    
    "enable_time_only_defaults": false,
    "//enable_timeonly": "Set to true to automatically add default flags when only time provided",
    
    "time_only_default_flags": [],
    "//timeonly_flags1": "Array of flags to add when only time argument provided:",
    "//timeonly_flags2": "  Example: [\\"-l\\\", \\\"-s\\\"] = loop + silent",
    "//timeonly_flags3": "  Example: [\\"-l\\\"] = loop only",
    "//timeonly_flags4": "  Example: [\\"-f\\\", \\\"1000\\\", \\\"-b\\\", \\\"5\\\"] = 1000Hz frequency, 5 beeps",
    "//timeonly_flags5": "Available flags: -s (silent), -l (loop), -m (metric),",
    "//timeonly_flags6": "  -f <hz> (frequency), -b <n> (beeps), -d <ms> (duration), -g <ms> (gap)",
    "//timeonly_flags7": "Note: Only applies when JUST time is typed. Manual flags disable this.",
    
    "//separator4": "",
    "//ascii_art_section": "=== ASCII ART CUSTOMIZATION ===",
    "//ascii_art1": "Customize the appearance of digits (0-9) and colon (:) in the countdown display",
    "//ascii_art2": "Each digit must be exactly 8 lines tall and have consistent width",
    "//ascii_art3": "Use any characters you want: #, *, @, █, ░, etc.",
    "//ascii_art4": "TIP: Keep all digits the same width for best alignment (11 chars recommended)",
    "//ascii_art5": "TIP: Preview your changes by running a short countdown like: wincountdown 10s",
    "//ascii_art6": "",
    
    "ascii_digits": ''' + json.dumps(DEFAULT_ASCII_DIGITS, indent=8) + '''
}'''
    
    def load(self):
        """Load configuration from file, create with defaults if it doesn't exist"""
        logger.log(f"Loading config from: {self.config_file}")
        logger.log(f"Config file exists: {os.path.exists(self.config_file)}")
        
        if not os.path.exists(self.config_file):
            logger.log("Config file does not exist, creating new one")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(self.create_config_content())
            print(f"Created default configuration file: {self.config_file}")
            print("You can edit this file to customize default settings.\n")
            return DEFAULT_CONFIG.copy()
        
        try:
            logger.log("Attempting to read config file")
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.log(f"Raw config loaded from file: {config}")
            
            # Filter out comment fields (they start with //)
            filtered_config = {k: v for k, v in config.items() if not k.startswith('//')}
            logger.log(f"Filtered config (comments removed): {filtered_config}")
            
            # Merge with defaults to ensure all keys exist
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(filtered_config)
            
            # Validate ascii_digits if present
            if 'ascii_digits' in filtered_config:
                self._validate_ascii_digits(filtered_config['ascii_digits'], merged_config)
            
            # Setup logger with debug mode from config
            logger.setup(merged_config.get('debug_mode', False), self.debug_log_file)
            logger.log(f"DEBUG mode set to: {merged_config.get('debug_mode', False)}")
            logger.log(f"Final merged config: {merged_config}")
            
            return merged_config
            
        except (json.JSONDecodeError, IOError) as e:
            error_msg = f"Warning: Could not read config file ({e}), using defaults"
            logger.log(error_msg)
            print(error_msg)
            return DEFAULT_CONFIG.copy()
    
    def _validate_ascii_digits(self, ascii_digits, merged_config):
        """Validate ASCII art digits configuration"""
        for digit in '0123456789:':
            if digit not in ascii_digits:
                logger.log(f"Warning: Missing ASCII art for '{digit}', using default")
                ascii_digits[digit] = DEFAULT_ASCII_DIGITS[digit]
            elif not isinstance(ascii_digits[digit], list) or len(ascii_digits[digit]) != ASCII_HEIGHT:
                logger.log(f"Warning: Invalid ASCII art for '{digit}' (must be {ASCII_HEIGHT} lines), using default")
                ascii_digits[digit] = DEFAULT_ASCII_DIGITS[digit]

# ============================================================================
# DISPLAY MANAGER CLASS
# ============================================================================

class DisplayManager:
    """Handles all display formatting and rendering"""
    
    def __init__(self, ascii_art):
        self.ascii_art = ascii_art
        
    def draw_border(self, char='='):
        """Draw a border line"""
        return f"  +{char * BORDER_WIDTH}+"
    
    def draw_line(self, content='', centered=False):
        """Draw a line with optional centered content"""
        if centered and content:
            padding = (BORDER_WIDTH - len(content)) // 2
            return f"  |{' ' * padding}{content}{' ' * (BORDER_WIDTH - padding - len(content))}|"
        return f"  |{content:{BORDER_WIDTH}}|"
    
    def get_ascii_digit(self, digit):
        """Return ASCII art for a single digit from config"""
        return self.ascii_art.get(digit, ["           "] * ASCII_HEIGHT)
    
    def render_time(self, hours, minutes, seconds, show_hours, show_minutes):
        """Render time as ASCII art - only show relevant units"""
        if show_hours:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif show_minutes:
            time_str = f"{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{seconds:02d}"
        
        # Use list comprehension and join for better performance
        lines = []
        for i in range(ASCII_HEIGHT):
            line_parts = []
            for char in time_str:
                digit_art = self.get_ascii_digit(char)
                line_parts.append(digit_art[i])
                line_parts.append("  ")
            lines.append(''.join(line_parts))
        
        return lines
    
    def draw_static_ui(self, total_seconds, show_hours, show_minutes, metric=False, 
                      start_time_str="", end_time_str="", console=None):
        """Draw the static parts of the UI once"""
        if console:
            console.clear_screen()
        else:
            os.system('cls')
        
        # Format the initial time for display
        if metric:
            total_metric_seconds = total_seconds // 1000
            hours = total_metric_seconds // 10000
            minutes = (total_metric_seconds % 10000) // 100
            seconds = total_metric_seconds % 100
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
        
        if show_hours:
            time_display = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif show_minutes:
            time_display = f"{minutes:02d}:{seconds:02d}"
        else:
            time_display = f"{seconds:02d}"
        
        # Top border with decoration
        print("\n")
        print(self.draw_border())
        print(self.draw_line())
        title = f">>>  C O U N T D O W N  [ {time_display} ]  <<<"
        print(self.draw_line(title, centered=True))
        print(self.draw_line())
        print(self.draw_border())
        print()
        print()
        
        # Reserve space for the time display
        for _ in range(ASCII_HEIGHT):
            print()
        
        print()
        print()
        
        # Bottom decoration with start and end times
        print(self.draw_border())
        
        # First line: labels
        start_label = "Start time:"
        center_text = "Press Ctrl+C to stop"
        end_label = "End time:"
        
        total_side_length = len(start_label) + len(end_label)
        remaining_space = BORDER_WIDTH - total_side_length - len(center_text)
        left_space = remaining_space // 2
        right_space = remaining_space - left_space
        
        print("  |" + start_label + " " * left_space + center_text + 
              " " * right_space + end_label + "|")
        
        # Second line: actual times
        space_between = BORDER_WIDTH - len(start_time_str) - len(end_time_str)
        print("  |" + start_time_str + " " * space_between + end_time_str + "|")
        
        print(self.draw_border())
        print("  stropitor")
    
    def update_time_display(self, hours, minutes, seconds, show_hours, show_minutes, console):
        """Update only the time display portion"""
        lines = self.render_time(hours, minutes, seconds, show_hours, show_minutes)
        
        # Calculate the actual width of the time display
        time_width = len(lines[0])
        
        # Center within the box - pre-calculate padding
        x_offset = 3 + (BORDER_WIDTH - time_width) // 2
        left_padding = " " * x_offset
        right_padding = " " * (120 - x_offset - time_width)
        
        # Draw all lines in one pass
        for i, line in enumerate(lines):
            console.set_position(0, 8 + i)
            # Build the full line more efficiently
            print(f"{left_padding}{line.rstrip()}{right_padding}"[:120], end='', flush=True)
    
    def draw_finished_screen(self, show_hours, show_minutes, loop=False):
        """Draw the time's up screen"""
        os.system('cls')
        
        print("\n")
        print(self.draw_border())
        print(self.draw_line())
        
        if loop:
            title = ">>>  R E S T A R T I N G . . .  <<<"
        else:
            title = ">>>  T I M E ' S   U P !  <<<"
        
        print(self.draw_line(title, centered=True))
        print(self.draw_line())
        print(self.draw_border())
        print()
        print()
        
        # Show final time (00:00:00 or 00:00 or 00)
        if show_hours:
            lines = self.render_time(0, 0, 0, True, True)
        elif show_minutes:
            lines = self.render_time(0, 0, 0, False, True)
        else:
            lines = self.render_time(0, 0, 0, False, False)
        
        # Center the final time display
        time_width = len(lines[0])
        x_offset = 2 + (BORDER_WIDTH - time_width) // 2
        
        for line in lines:
            print(" " * x_offset + line)
        
        print()
        print()
        print(self.draw_border())
        print(self.draw_line())
        print(self.draw_border())
        print("  stropitor")

# ============================================================================
# TIMER CLASS
# ============================================================================

class CountdownTimer:
    """Main countdown timer logic"""
    
    def __init__(self, config):
        self.config = config
        self.display = DisplayManager(config.get('ascii_digits', DEFAULT_ASCII_DIGITS))
        
    def parse_time(self, time_str, metric=False):
        """Parse time string in various formats"""
        hours = minutes = seconds = 0
        
        # Check if it's in HH:MM:SS format
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
            elif len(parts) == 2:
                minutes, seconds = int(parts[0]), int(parts[1])
        else:
            # Parse format like 1h30m45s - more efficient approach
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
        
        # Calculate total seconds
        real_seconds = hours * 3600 + minutes * 60 + seconds
        
        # Return milliseconds for metric, seconds for standard
        return int(real_seconds * 1000) if metric else real_seconds
    
    def play_beeps(self, freq, count, duration, gap, silent, loop):
        """Play beep sounds when timer finishes"""
        if silent:
            return
            
        try:
            beeps_to_play = 1 if loop else count
            for i in range(beeps_to_play):
                winsound.Beep(freq, duration)
                if i < beeps_to_play - 1:
                    time.sleep(gap / 1000.0)
        except:
            # Fallback to console beep
            beeps_to_play = 1 if loop else count
            for i in range(beeps_to_play):
                print('\a', end='', flush=True)
                if i < beeps_to_play - 1:
                    time.sleep(0.5)
    
    def run(self, total_seconds, beep_freq=800, beep_count=3, beep_duration=1000, 
            beep_gap=300, silent=False, loop=False, metric=False):
        """Run the countdown timer"""
        
        # Determine what units to show
        if metric:
            show_hours = total_seconds >= 10000000  # >= 1 metric hour
            show_minutes = total_seconds >= 100000   # >= 1 metric minute
        else:
            show_hours = total_seconds >= 3600
            show_minutes = total_seconds >= 60
        
        with ConsoleManager() as console:
            try:
                while True:  # Outer loop for restart functionality
                    # Calculate start and end times
                    import datetime
                    start_datetime = datetime.datetime.now()
                    start_time_str = start_datetime.strftime("%H:%M:%S")
                    
                    # Calculate end time
                    if metric:
                        duration_seconds = total_seconds / 1000
                    else:
                        duration_seconds = total_seconds
                    
                    end_datetime = start_datetime + datetime.timedelta(seconds=duration_seconds)
                    end_time_str = end_datetime.strftime("%H:%M:%S")
                    
                    self.display.draw_static_ui(total_seconds, show_hours, show_minutes, 
                                               metric, start_time_str, end_time_str, console)
                    
                    start_time = time.time()
                    last_remaining = -1
                    
                    while True:
                        if metric:
                            elapsed_ms = int((time.time() - start_time) * 1000)
                            remaining = total_seconds - elapsed_ms
                        else:
                            elapsed = int(time.time() - start_time)
                            remaining = total_seconds - elapsed
                        
                        if remaining < 0:
                            break
                        
                        # Only update display when the second changes
                        if remaining != last_remaining:
                            if metric:
                                total_metric_seconds = remaining // 1000
                                hours = total_metric_seconds // 10000
                                minutes = (total_metric_seconds % 10000) // 100
                                seconds = total_metric_seconds % 100
                            else:
                                hours = remaining // 3600
                                minutes = (remaining % 3600) // 60
                                seconds = remaining % 60
                            
                            self.display.update_time_display(hours, minutes, seconds, 
                                                            show_hours, show_minutes, console)
                            last_remaining = remaining
                        
                        time.sleep(UPDATE_INTERVAL_METRIC if metric else UPDATE_INTERVAL_STANDARD)
                    
                    # Time's up!
                    self.display.draw_finished_screen(show_hours, show_minutes, loop)
                    
                    # Play beeps
                    self.play_beeps(beep_freq, beep_count, beep_duration, beep_gap, silent, loop)
                    
                    if not loop:
                        break
                    
                    time.sleep(1)  # Wait before restarting
                    
            except KeyboardInterrupt:
                raise  # Re-raise to be handled by main

# ============================================================================
# ARGUMENT PROCESSING
# ============================================================================

def get_effective_args(config):
    """Get effective arguments considering config defaults"""
    logger.log("get_effective_args called")
    args = sys.argv[1:]
    
    logger.log(f"Initial args: {args}")
    
    # Handle no arguments case
    if not args:
        logger.log(f"No args provided, checking enable_no_args_default")
        if config.get("enable_no_args_default", False):
            cmd = config.get("no_args_default_command", "help")
            logger.log(f"Using no_args_default_command: {cmd}")
            if cmd == "help":
                return None  # Signal to show help
            return shlex.split(cmd)
        return None  # Show help by default
    
    # Handle time-only case
    user_args = [arg for arg in args if not arg.startswith('-')]
    flag_args = [arg for arg in args if arg.startswith('-')]
    
    logger.log(f"user_args: {user_args}, flag_args: {flag_args}")
    
    if len(user_args) == 1 and len(flag_args) == 0:
        if config.get("enable_time_only_defaults", False):
            default_flags = config.get("time_only_default_flags", [])
            logger.log(f"Adding time_only_default_flags: {default_flags}")
            args.extend(default_flags)
    
    logger.log(f"Final effective args: {args}")
    return args

def parse_arguments(args, config):
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        prog='wincountdown',
        description='A countdown timer with ASCII art display for Windows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    
    parser.add_argument('time', nargs='?', help='Time duration')
    parser.add_argument('-s', '--silent', action='store_true', 
                        default=config.get('default_silent', False))
    parser.add_argument('-f', '--freq', type=int, 
                        default=config.get('default_frequency', 800), metavar='HZ')
    parser.add_argument('-b', '--beeps', type=int, 
                        default=config.get('default_beeps', 3), metavar='N')
    parser.add_argument('-d', '--duration', type=int, 
                        default=config.get('default_duration', 1000), metavar='MS')
    parser.add_argument('-g', '--gap', type=int, 
                        default=config.get('default_gap', 300), metavar='MS')
    parser.add_argument('-l', '--loop', action='store_true',
                        default=config.get('default_loop', False))
    parser.add_argument('-m', '--metric', action='store_true',
                        default=config.get('default_metric', False))
    
    return parser.parse_args(args)

def validate_arguments(args, metric=False):
    """Validate argument constraints"""
    errors = []
    
    if not 37 <= args.freq <= 32767:
        errors.append("Frequency must be between 37 and 32767 Hz")
    
    if args.beeps < 1:
        errors.append("Number of beeps must be at least 1")
    
    if args.duration < 1:
        errors.append("Beep duration must be at least 1 millisecond")
    
    if args.gap < 0:
        errors.append("Beep gap cannot be negative")
    
    return errors

# ============================================================================
# HELP SCREEN
# ============================================================================

def print_help():
    """Print a beautifully formatted help screen"""
    help_text = """
  +===================================================================================================================+
  |                                                                                                                   |
  |      ##      ## #### ##     ##  ####   ####  ##     ## ##     ## ######## ####    ####  ##      ## ##     ##      |
  |      ##  ##  ##  ##  ###    ## ##  ## ##  ## ##     ## ###    ##    ##    ##  ## ##  ## ##  ##  ## ###    ##      |
  |      ##  ##  ##  ##  ####   ## ##     ##  ## ##     ## ####   ##    ##    ##  ## ##  ## ##  ##  ## ####   ##      |
  |      ##  ##  ##  ##  ## ##  ## ##     ##  ## ##     ## ## ##  ##    ##    ##  ## ##  ## ##  ##  ## ## ##  ##      |
  |      ##  ##  ##  ##  ##  ## ## ##     ##  ## ##     ## ##  ## ##    ##    ##  ## ##  ## ##  ##  ## ##  ## ##      |
  |      ##  ##  ##  ##  ##   #### ##  ## ##  ## ##     ## ##   ####    ##    ##  ## ##  ## ##  ##  ## ##   ####      |
  |      ###    ### #### ##    ###  ####   ####   #######  ##    ###    ##    ####    ####   ###  ###  ##    ###      |
  |                                                                                                                   |
  +===================================================================================================================+

  A countdown timer with ASCII art display and customizable beep alerts.

  +===================================================================================================================+
  | USAGE                                                                                                             |
  +===================================================================================================================+

    wincountdown <time> [options]

  +===================================================================================================================+
  | TIME FORMATS                                                                                                      |
  +===================================================================================================================+

    Seconds only     30s, 90s, 500s
    Minutes only     5m, 45m, 240m
    Hours only       2h, 10h
    Combined         1h30m, 2h15m30s, 45m30s
    Colon format     1:30:00 (HH:MM:SS), 45:30 (MM:SS)

  +===================================================================================================================+
  | OPTIONS                                                                                                           |
  +===================================================================================================================+

    -s, --silent              Silent mode (no beep alert)
    -f HZ, --freq HZ          Beep frequency in Hz (default: from config, or 800)
    -b N, --beeps N           Number of beeps when finished (default: from config, or 3)
    -d MS, --duration MS      Duration of each beep in milliseconds (default: from config, or 1000)
    -g MS, --gap MS           Gap between beeps in milliseconds (default: from config, or 300)
    -l, --loop                Automatically restart countdown when it reaches 0
    -m, --metric              JOKE: Display in metric time (1h=100m, 1m=100s)
    -h, --help                Show this help message

  +===================================================================================================================+
  | CONFIGURATION FILE                                                                                                |
  +===================================================================================================================+

    On first run, a 'wincountdown-config.json' file is created with default settings.
    You can edit this file to customize:
      - Default beep frequency, count, duration, and gap
      - Default silent, loop, and metric mode settings
      - Behavior when running 'wincountdown' with no arguments
      - Auto-apply flags when only providing a time argument
      - ASCII art for digits 0-9 and colon (:)

    See the config file for detailed comments on each option.

  +===================================================================================================================+
  | EXAMPLES                                                                                                          |
  +===================================================================================================================+

    Basic countdowns
      wincountdown 30s                       30 second countdown
      wincountdown 5m                        5 minute countdown
      wincountdown 1h30m                     1 hour 30 minutes
      wincountdown 90s                       Automatically displays as 01:30

    Silent and loop modes
      wincountdown 10m --silent              No beep alert
      wincountdown 25m --loop                Repeating timer
      wincountdown 5m -l -s                  Loop mode, silent

    Custom beep patterns
      wincountdown 1m --freq 440             Use 440Hz beep
      wincountdown 30s --beeps 5             Beep 5 times
      wincountdown 1h --duration 500         500ms beeps
      wincountdown 5m --gap 100              100ms gap between beeps
      wincountdown 1m -f 880 -b 3 -d 200     Fully custom pattern

    Metric time (joke mode)
      wincountdown 5m --metric               5 real minutes in metric display
      wincountdown 1h -m                     1 real hour in metric display

  +===================================================================================================================+
  | NOTES                                                                                                             |
  +===================================================================================================================+

    Maximum time              99:59:59 (or 99:99:99 in metric mode)
    Display                   Automatically shows only relevant units
    Default beep              From config file (or 800Hz, 1000ms, 3 times if config missing)
    Loop mode beep            Only one beep before restarting
    Stop timer                Press Ctrl+C at any time
    Metric mode               Input real time, display as metric (1h=100m, 1m=100s)
                              Each metric second lasts 1 real second
    Config file               Edit wincountdown-config.json to customize defaults
    ASCII art                 Customize digit appearance in config file

  +===================================================================================================================+

  Created by stropitor
"""
    print(help_text)

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main entry point"""
    # Get the directory where the script/executable is located
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize config manager
    config_manager = ConfigManager(script_dir)
    
    # Setup logger early for debugging
    logger.log("========== STARTING MAIN ==========")
    
    # Load configuration
    config = config_manager.load()
    
    logger.log(f"sys.argv initial: {sys.argv}")
    
    # Get effective arguments
    effective_args = get_effective_args(config)
    
    # Check for help flag
    if effective_args is None or '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit(0)
    
    # Parse arguments
    args = parse_arguments(effective_args, config)
    
    # Show help if no time provided
    if not args.time:
        print_help()
        sys.exit(1)
    
    # Validate arguments
    errors = validate_arguments(args, args.metric)
    if errors:
        for error in errors:
            print(f"Error: {error}")
        sys.exit(1)
    
    # Initialize timer
    timer = CountdownTimer(config)
    
    try:
        # Parse time
        total_seconds = timer.parse_time(args.time, args.metric)
        if total_seconds <= 0:
            print("Error: Time must be greater than 0")
            sys.exit(1)
        
        # Check maximum time
        max_seconds = MAX_METRIC_MILLISECONDS if args.metric else MAX_STANDARD_SECONDS
        
        if total_seconds > max_seconds:
            print(f"Error: Time exceeds maximum of 99:99:99")
            if args.metric:
                total_metric_seconds = total_seconds // 1000
                hours = total_metric_seconds // 10000
                minutes = (total_metric_seconds % 10000) // 100
                seconds = total_metric_seconds % 100
                print(f"You requested: {hours:02d}:{minutes:02d}:{seconds:02d} (metric)")
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                print(f"You requested: {hours:02d}:{minutes:02d}:{seconds:02d}")
            sys.exit(1)
        
        # Run countdown
        timer.run(total_seconds, args.freq, args.beeps, args.duration, 
                 args.gap, args.silent, args.loop, args.metric)
        
    except ValueError:
        print("Error: Invalid time format")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTimer stopped!")
        sys.exit(0)

if __name__ == "__main__":
    main()