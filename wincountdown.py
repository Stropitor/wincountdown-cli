import sys
import time
import os
import ctypes
import winsound
import argparse
from ctypes import wintypes

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

def main():
    parser = argparse.ArgumentParser(
        prog='wincountdown',
        description='A countdown timer with ASCII art display for Windows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Time Format Options:
  Seconds only:     30s, 90s, 500s
  Minutes only:     5m, 45m, 240m
  Hours only:       2h, 10h
  Combined:         1h30m, 2h15m30s, 45m30s
  Colon format:     1:30:00 (HH:MM:SS), 45:30 (MM:SS)

Examples:
  wincountdown 30s                    - 30 second countdown
  wincountdown 90s                    - 1 minute 30 seconds (displays as 01:30)
  wincountdown 5m                     - 5 minute countdown
  wincountdown 300s                   - 5 minutes (displays as 05:00)
  wincountdown 1h30m                  - 1 hour 30 minute countdown
  wincountdown 2h15m30s               - 2 hours 15 minutes 30 seconds
  wincountdown 45:30                  - 45 minutes 30 seconds
  wincountdown 5m --silent            - Silent countdown (no beep)
  wincountdown 10m --loop             - Loop continuously (beeps once per loop)
  wincountdown 30s --freq 880         - Use 880Hz beep frequency
  wincountdown 1m --beeps 3           - Beep 3 times when finished
  wincountdown 5m --duration 500      - Each beep lasts 500ms
  wincountdown 30s --gap 100          - 100ms gap between beeps
  wincountdown 30s -f 880 -b 3 -d 500 - 880Hz beep, 3 times, 500ms each
  wincountdown 1m -f 440 -b 5 -d 200 -g 100 - Custom beep pattern
  wincountdown 5m -l -s               - Loop mode, silent
  wincountdown 5m --metric            - JOKE: 5 real minutes displayed as metric time
  wincountdown 1h -m                  - JOKE: 1 real hour displayed as metric time

Notes:
  - Maximum time: 99:59:59
  - The timer automatically shows only relevant units
  - When countdown finishes, plays a beep (800Hz, 1000ms, 3 times by default)
  - In loop mode, plays only one beep before restarting
  - Press Ctrl+C to stop the timer at any time
  - Metric mode (JOKE): Input real time, display as metric (1h=100m, 1m=100s)
    Each metric second lasts 1 real second. Example: 60 real seconds = 60 metric seconds
        '''
    )
    
    parser.add_argument('time', nargs='?', help='Time duration (e.g., 30s, 5m, 1h30m, 1:30:00)')
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode (no beep alert)')
    parser.add_argument('-f', '--freq', type=int, default=800, metavar='HZ',
                        help='Beep frequency in Hz (default: 800, range: 37-32767)')
    parser.add_argument('-b', '--beeps', type=int, default=3, metavar='N',
                        help='Number of beeps when finished (default: 3)')
    parser.add_argument('-d', '--duration', type=int, default=1000, metavar='MS',
                        help='Duration of each beep in milliseconds (default: 1000)')
    parser.add_argument('-g', '--gap', type=int, default=300, metavar='MS',
                        help='Gap between beeps in milliseconds (default: 300)')
    parser.add_argument('-l', '--loop', action='store_true',
                        help='Automatically restart countdown when it reaches 0 (beeps once per loop)')
    parser.add_argument('-m', '--metric', action='store_true',
                        help='JOKE: Display in metric time (1h=100m, 1m=100s, 1 metric second = 1 real second). Input time is still real time.')
    
    args = parser.parse_args()
    
    # Show help if no time argument provided
    if not args.time:
        parser.print_help()
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