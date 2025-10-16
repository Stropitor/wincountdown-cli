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

# Configuration file path
CONFIG_FILE = "wincountdown-config.json"
DEBUG_LOG_FILE = "wincountdown-debug.log"

# DEBUG will be loaded from config
DEBUG = False

def debug_log(message):
    """Write debug message to log file if DEBUG is enabled"""
    if DEBUG:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}\n"
        with open(DEBUG_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message)
        # Also print to console
        print(log_message.rstrip())

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
    "time_only_default_flags": []
}

def create_config_with_comments():
    """Create a configuration file with detailed comments"""
    config_content = '''{
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
    "//timeonly_flags7": "Note: Only applies when JUST time is typed. Manual flags disable this."
}'''
    return config_content

def load_config():
    """Load configuration from file, create with defaults if it doesn't exist"""
    global DEBUG
    
    debug_log(f"load_config() called")
    debug_log(f"Checking for config file: {CONFIG_FILE}")
    debug_log(f"Config file exists: {os.path.exists(CONFIG_FILE)}")
    
    if not os.path.exists(CONFIG_FILE):
        # Create config file with detailed comments
        debug_log("Config file does not exist, creating new one")
        with open(CONFIG_FILE, 'w') as f:
            f.write(create_config_with_comments())
        print(f"Created default configuration file: {CONFIG_FILE}")
        print("You can edit this file to customize default settings.\n")
        return DEFAULT_CONFIG.copy()
    
    try:
        debug_log("Attempting to read config file")
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        debug_log(f"Raw config loaded from file: {config}")
        
        # Filter out comment fields (they start with //)
        filtered_config = {k: v for k, v in config.items() if not k.startswith('//')}
        
        debug_log(f"Filtered config (comments removed): {filtered_config}")
        
        # Merge with defaults to ensure all keys exist
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(filtered_config)
        
        # Update global DEBUG variable from config
        DEBUG = merged_config.get('debug_mode', False)
        debug_log(f"DEBUG mode set to: {DEBUG}")
        
        debug_log(f"Final merged config: {merged_config}")
        
        return merged_config
    except (json.JSONDecodeError, IOError) as e:
        error_msg = f"Warning: Could not read config file ({e}), using defaults"
        debug_log(error_msg)
        print(error_msg)
        return DEFAULT_CONFIG.copy()

def apply_no_args_default(config):
    """Apply default behavior when no arguments are provided"""
    debug_log("apply_no_args_default called")
    debug_log(f"enable_no_args_default = {config.get('enable_no_args_default', False)}")
    debug_log(f"no_args_default_command = {config.get('no_args_default_command', 'help')}")
    
    if config.get("enable_no_args_default", False):
        default_cmd = config.get("no_args_default_command", "help")
        
        debug_log(f"Applying no-args default with command: {default_cmd}")
        
        if default_cmd == "help":
            print_help()
            sys.exit(0)
        else:
            # Insert the default command into sys.argv
            # This simulates the user typing: wincountdown <default_cmd>
            import shlex
            # Use shlex to properly split the command (handles quotes and spaces)
            sys.argv.extend(shlex.split(default_cmd))
            
            debug_log(f"sys.argv after extending: {sys.argv}")

def apply_time_only_defaults(config, args_list):
    """Apply default flags when only time argument is provided"""
    debug_log("apply_time_only_defaults called")
    debug_log(f"args_list = {args_list}")
    debug_log(f"enable_time_only_defaults = {config.get('enable_time_only_defaults', False)}")
    debug_log(f"time_only_default_flags = {config.get('time_only_default_flags', [])}")
    
    if config.get("enable_time_only_defaults", False):
        # Check if only one argument was provided (the time)
        # Count only non-program-name arguments
        user_args = [arg for arg in args_list if not arg.startswith('-')]
        flag_args = [arg for arg in args_list if arg.startswith('-')]
        
        debug_log(f"user_args = {user_args}")
        debug_log(f"flag_args = {flag_args}")
        
        # If there's exactly one user argument (time) and no flags
        if len(user_args) == 1 and len(flag_args) == 0:
            default_flags = config.get("time_only_default_flags", [])
            
            debug_log(f"Condition met! Adding default flags: {default_flags}")
            
            if default_flags:
                # Insert default flags after the time argument
                # Make sure we're adding them as separate arguments
                for flag in default_flags:
                    sys.argv.append(flag)
                
                debug_log(f"sys.argv after adding flags: {sys.argv}")
        else:
            debug_log(f"Condition NOT met (user_args={len(user_args)}, flag_args={len(flag_args)})")

# Windows console API structures and functions
class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("bVisible", wintypes.BOOL)]

# Get handle to console
kernel32 = ctypes.windll.kernel32
h_console = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE

def hide_cursor():
    """Hide the console cursor to prevent flickering"""
    cursor_info = CONSOLE_CURSOR_INFO()
    cursor_info.dwSize = 100
    cursor_info.bVisible = False
    kernel32.SetConsoleCursorInfo(h_console, ctypes.byref(cursor_info))

def show_cursor():
    """Show the console cursor again"""
    cursor_info = CONSOLE_CURSOR_INFO()
    cursor_info.dwSize = 100
    cursor_info.bVisible = True
    kernel32.SetConsoleCursorInfo(h_console, ctypes.byref(cursor_info))

def set_cursor_position(x, y):
    """Move cursor to specific position without clearing"""
    coord = COORD(x, y)
    kernel32.SetConsoleCursorPosition(h_console, coord)

def clear_screen():
    """Clear screen once at the start"""
    os.system('cls')

def get_ascii_digit(digit):
    """Return ASCII art for a single digit - bigger, blockier style"""
    digits = {
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
    return digits.get(digit, ["           "] * 8)

def render_time(hours, minutes, seconds, show_hours, show_minutes):
    """Render time as ASCII art - only show relevant units"""
    if show_hours:
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    elif show_minutes:
        time_str = f"{minutes:02d}:{seconds:02d}"
    else:
        time_str = f"{seconds:02d}"
    
    lines = [""] * 8
    for char in time_str:
        digit_art = get_ascii_digit(char)
        for i in range(8):
            lines[i] += digit_art[i] + "  "
    
    return lines

def parse_time(time_str, metric=False):
    """Parse time string in format like '1h30m', '45m', '30s', or '1:30:00'"""
    hours = 0
    minutes = 0
    seconds = 0
    
    # Check if it's in HH:MM:SS format
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
        elif len(parts) == 2:
            minutes = int(parts[0])
            seconds = int(parts[1])
    else:
        # Parse format like 1h30m45s
        time_str = time_str.lower()
        if 'h' in time_str:
            h_parts = time_str.split('h')
            hours = int(h_parts[0])
            time_str = h_parts[1] if len(h_parts) > 1 else ''
        if 'm' in time_str:
            m_parts = time_str.split('m')
            minutes = int(m_parts[0])
            time_str = m_parts[1] if len(m_parts) > 1 else ''
        if 's' in time_str:
            s_parts = time_str.split('s')
            seconds = int(s_parts[0]) if s_parts[0] else 0
    
    # Always parse as real time first (in seconds)
    real_seconds = hours * 3600 + minutes * 60 + seconds
    
    if metric:
        # Convert real seconds to milliseconds for metric display
        return int(real_seconds * 1000)
    else:
        # Standard time in seconds
        return real_seconds

def draw_static_ui(total_seconds, show_hours, show_minutes, metric=False, start_time_str="", end_time_str=""):
    """Draw the static parts of the UI once"""
    clear_screen()
    
    # Format the initial time for display
    if metric:
        # Convert milliseconds to metric time units
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
    print("  +" + "=" * 115 + "+")
    print("  |" + " " * 115 + "|")
    title = f">>>  C O U N T D O W N  [ {time_display} ]  <<<"
    padding = (115 - len(title)) // 2
    print("  |" + " " * padding + title + " " * (115 - padding - len(title)) + "|")
    print("  |" + " " * 115 + "|")
    print("  +" + "=" * 115 + "+")
    print()
    print()
    
    # Reserve space for the time display (8 lines now)
    for _ in range(8):
        print()
    
    print()
    print()
    
    # Bottom decoration with start and end times
    print("  +" + "=" * 115 + "+")
    
    # First line: "Start time:" on left, "Press Ctrl+C to stop" centered, "End time:" on right
    start_label = "Start time:"
    center_text = "Press Ctrl+C to stop"
    end_label = "End time:"
    
    # Calculate spacing
    total_side_length = len(start_label) + len(end_label)
    remaining_space = 115 - total_side_length - len(center_text)
    left_space = remaining_space // 2
    right_space = remaining_space - left_space
    
    print("  |" + start_label + " " * left_space + center_text + " " * right_space + end_label + "|")
    
    # Second line: actual times, left and right aligned
    space_between = 115 - len(start_time_str) - len(end_time_str)
    print("  |" + start_time_str + " " * space_between + end_time_str + "|")
    
    print("  +" + "=" * 115 + "+")
    print("  stropitor")

def update_time_display(hours, minutes, seconds, show_hours, show_minutes):
    """Update only the time display portion"""
    lines = render_time(hours, minutes, seconds, show_hours, show_minutes)
    
    # Calculate the actual width of the time display
    time_width = len(lines[0])
    
    # Center within the 115-character box (plus 2 spaces + | on left = 3 chars)
    x_offset = 3 + (115 - time_width) // 2
    
    # Draw all lines in one pass to avoid distortion
    for i, line in enumerate(lines):
        set_cursor_position(0, 8 + i)
        # Total terminal width needs padding to clear the line
        # Create spacing + content + spacing (no borders on these lines)
        left_padding = " " * (x_offset)
        right_padding = " " * (120 - x_offset - time_width)
        full_line = left_padding + line.rstrip() + right_padding
        print(full_line[:120], end='', flush=True)

def countdown(total_seconds, beep_freq=800, beep_count=3, beep_duration=1000, beep_gap=300, silent=False, loop=False, metric=False):
    """Run the countdown timer"""
    hide_cursor()
    
    # For metric mode, we're working in milliseconds
    # 1 metric second = 1000ms (same as real second)
    # 1 metric minute = 100 metric seconds = 100000ms
    # 1 metric hour = 100 metric minutes = 10000000ms
    if metric:
        show_hours = total_seconds >= 10000000  # >= 1 metric hour
        show_minutes = total_seconds >= 100000   # >= 1 metric minute
    else:
        # Determine what units to show based on total time
        show_hours = total_seconds >= 3600  # Show hours if >= 1 hour
        show_minutes = total_seconds >= 60   # Show minutes if >= 1 minute
    
    try:
        while True:  # Outer loop for restart functionality
            # Calculate start and end times
            import datetime
            start_datetime = datetime.datetime.now()
            start_time_str = start_datetime.strftime("%H:%M:%S")
            
            # Calculate end time based on real seconds (not metric)
            if metric:
                duration_seconds = total_seconds / 1000  # Convert milliseconds to seconds
            else:
                duration_seconds = total_seconds
            
            end_datetime = start_datetime + datetime.timedelta(seconds=duration_seconds)
            end_time_str = end_datetime.strftime("%H:%M:%S")
            
            draw_static_ui(total_seconds, show_hours, show_minutes, metric, start_time_str, end_time_str)
            
            start_time = time.time()
            last_remaining = -1
            
            while True:
                if metric:
                    # In metric mode, track milliseconds
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
                        # Convert milliseconds to metric time units
                        # 1 metric second = 1000ms
                        total_metric_seconds = remaining // 1000
                        hours = total_metric_seconds // 10000
                        minutes = (total_metric_seconds % 10000) // 100
                        seconds = total_metric_seconds % 100
                    else:
                        hours = remaining // 3600
                        minutes = (remaining % 3600) // 60
                        seconds = remaining % 60
                    
                    update_time_display(hours, minutes, seconds, show_hours, show_minutes)
                    last_remaining = remaining
                
                time.sleep(0.01 if metric else 0.05)  # Check more frequently in metric mode
            
            # Time's up!
            clear_screen()
            print("\n")
            print("  +" + "=" * 115 + "+")
            print("  |" + " " * 115 + "|")
            if loop:
                title = ">>>  R E S T A R T I N G . . .  <<<"
            else:
                title = ">>>  T I M E ' S   U P !  <<<"
            padding = (115 - len(title)) // 2
            print("  |" + " " * padding + title + " " * (115 - padding - len(title)) + "|")
            print("  |" + " " * 115 + "|")
            print("  +" + "=" * 115 + "+")
            print()
            print()
            
            # Show final time in same format
            if show_hours:
                lines = render_time(0, 0, 0, True, True)
            elif show_minutes:
                lines = render_time(0, 0, 0, False, True)
            else:
                lines = render_time(0, 0, 0, False, False)
            
            # Center the final time display
            time_width = len(lines[0])
            x_offset = 2 + (115 - time_width) // 2
                
            for line in lines:
                print(" " * x_offset + line)
            
            print()
            print()
            print("  +" + "=" * 115 + "+")
            print("  |" + " " * 115 + "|")
            print("  +" + "=" * 115 + "+")
            print("  stropitor")
            
            # Play a beep sound alert (unless silent)
            if not silent:
                try:
                    # For loop mode, just one beep
                    beeps_to_play = 1 if loop else beep_count
                    for i in range(beeps_to_play):
                        winsound.Beep(beep_freq, beep_duration)  # frequency, duration in ms
                        # Add gap between beeps (but not after the last one)
                        if i < beeps_to_play - 1:
                            time.sleep(beep_gap / 1000.0)
                except:
                    # Fallback to console beep if winsound fails
                    beeps_to_play = 1 if loop else beep_count
                    for i in range(beeps_to_play):
                        print('\a', end='', flush=True)
                        if i < beeps_to_play - 1:
                            time.sleep(0.5)
            
            # If not looping, exit
            if not loop:
                break
            
            # Wait a moment before restarting
            time.sleep(1)
    
    finally:
        show_cursor()

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

  +===================================================================================================================+

  Created by stropitor
"""
    print(help_text)

def main():
    # Clear previous debug log if DEBUG is enabled
    if DEBUG and os.path.exists(DEBUG_LOG_FILE):
        os.remove(DEBUG_LOG_FILE)
    
    debug_log("========== STARTING MAIN ==========")
    
    # Load configuration first
    config = load_config()
    
    debug_log(f"sys.argv initial: {sys.argv}")
    debug_log(f"len(sys.argv) = {len(sys.argv)}")
    debug_log("")
    
    # Check if no arguments were provided (only program name)
    if len(sys.argv) == 1:
        debug_log("No arguments provided, calling apply_no_args_default")
        apply_no_args_default(config)
    
    debug_log(f"sys.argv after no-args processing: {sys.argv}")
    debug_log("")
    
    # Check for help flag before parsing
    if '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit(0)
    
    # Apply time-only defaults if configured (before parsing)
    if len(sys.argv) > 1:
        debug_log(f"Calling apply_time_only_defaults with args: {sys.argv[1:]}")
        apply_time_only_defaults(config, sys.argv[1:])
    
    debug_log(f"sys.argv after time-only processing: {sys.argv}")
    debug_log("========== END DEBUG INFO ==========")
    debug_log("")
    
    parser = argparse.ArgumentParser(
        prog='wincountdown',
        description='A countdown timer with ASCII art display for Windows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # Disable default help to use custom
    )
    
    parser.add_argument('time', nargs='?', help='Time duration (e.g., 30s, 5m, 1h30m, 1:30:00)')
    parser.add_argument('-s', '--silent', action='store_true', 
                        default=config.get('default_silent', False),
                        help='Silent mode (no beep alert)')
    parser.add_argument('-f', '--freq', type=int, 
                        default=config.get('default_frequency', 800), 
                        metavar='HZ',
                        help=f'Beep frequency in Hz (default: {config.get("default_frequency", 800)}, range: 37-32767)')
    parser.add_argument('-b', '--beeps', type=int, 
                        default=config.get('default_beeps', 3), 
                        metavar='N',
                        help=f'Number of beeps when finished (default: {config.get("default_beeps", 3)})')
    parser.add_argument('-d', '--duration', type=int, 
                        default=config.get('default_duration', 1000), 
                        metavar='MS',
                        help=f'Duration of each beep in milliseconds (default: {config.get("default_duration", 1000)})')
    parser.add_argument('-g', '--gap', type=int, 
                        default=config.get('default_gap', 300), 
                        metavar='MS',
                        help=f'Gap between beeps in milliseconds (default: {config.get("default_gap", 300)})')
    parser.add_argument('-l', '--loop', action='store_true',
                        default=config.get('default_loop', False),
                        help='Automatically restart countdown when it reaches 0 (beeps once per loop)')
    parser.add_argument('-m', '--metric', action='store_true',
                        default=config.get('default_metric', False),
                        help='JOKE: Display in metric time (1h=100m, 1m=100s, 1 metric second = 1 real second). Input time is still real time.')
    
    args = parser.parse_args()
    
    # Show custom help if no time argument provided
    if not args.time:
        print_help()
        sys.exit(1)
    
    # Validate frequency range
    if args.freq < 37 or args.freq > 32767:
        print("Error: Frequency must be between 37 and 32767 Hz")
        sys.exit(1)
    
    # Validate beep count
    if args.beeps < 1:
        print("Error: Number of beeps must be at least 1")
        sys.exit(1)
    
    # Validate beep duration
    if args.duration < 1:
        print("Error: Beep duration must be at least 1 millisecond")
        sys.exit(1)
    
    # Validate beep gap
    if args.gap < 0:
        print("Error: Beep gap cannot be negative")
        sys.exit(1)
    
    # Handle metric mode
    metric_mode = args.metric
    
    try:
        total_seconds = parse_time(args.time, metric_mode)
        if total_seconds <= 0:
            print("Error: Time must be greater than 0")
            sys.exit(1)
        
        # Cap at 99:99:99
        if metric_mode:
            # In metric mode, max is 99h 99m 99s in metric time (converted to milliseconds)
            # 99:99:99 metric = 99*10000 + 99*100 + 99 = 999999 metric seconds = 999999000 milliseconds
            max_seconds = 999999000
        else:
            # Standard time: 359999 seconds
            max_seconds = 99 * 3600 + 59 * 60 + 59
            
        if total_seconds > max_seconds:
            print(f"Error: Time exceeds maximum of 99:99:99")
            if metric_mode:
                total_metric_seconds = total_seconds // 1000
                print(f"You requested: {total_metric_seconds // 10000:02d}:{(total_metric_seconds % 10000) // 100:02d}:{total_metric_seconds % 100:02d} (metric)")
            else:
                print(f"You requested: {total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}:{total_seconds % 60:02d}")
            sys.exit(1)
        
        countdown(total_seconds, args.freq, args.beeps, args.duration, args.gap, args.silent, args.loop, metric_mode)
    except ValueError:
        print("Error: Invalid time format")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTimer stopped!")
        show_cursor()
        sys.exit(0)

if __name__ == "__main__":
    main()