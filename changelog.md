# Changelog

### Added
- **Clock Mode** - Display current system time with `-c` or `--clock` flag
  - Shows time in 24-hour format (HH:MM:SS) using ASCII art display
  - Always displays 24-hour format regardless of system settings
  - Press Ctrl+C to exit clock mode
  - Uses same customizable ASCII art as countdown timer

- **Debug Flag** - New `--debug` command-line flag for easier troubleshooting
  - Enables debug logging without editing config file
  - Overrides `debug_mode` setting in config file
  - Creates `wincountdown-debug.log` with detailed execution information
  - Recommended method for troubleshooting over config file setting

### Changed
- **Help Screen Rewrite** - Completely redesigned help screen for better clarity
  - Reorganized OPTIONS into logical categories (Countdown, Beep Customization, Other Modes, Utility)
  - Added "Common Use Cases" section with practical examples (Pomodoro timer, silent timer, etc.)
  - New "KEY FEATURES" section highlighting main capabilities
  - New "QUICK TIPS" section with practical advice
  - Better alignment with README documentation
  - Clearer descriptions and more intuitive organization
  - Added clock mode examples and documentation

- **Config File Comments** - Significantly improved configuration file documentation
  - Clearer, more concise explanations for each setting
  - Better organization with logical grouping
  - More practical examples (e.g., "440 (musical A)" for frequency)
  - Added clock mode option to no-args behavior examples
  - Improved ASCII art customization instructions
  - Better explanations of advanced behaviors

- **README Documentation** - Updated README with new features
  - Added clock mode to features list and usage examples
  - Added `--debug` flag to options table and examples
  - Updated Debug Mode section with both flag and config options
  - Added clock mode notes explaining 24-hour format behavior
  - Updated troubleshooting section with `--debug` flag recommendations
  - Improved formatting and clarity throughout

### Technical Details
- Clock mode implementation uses `datetime.now()` for system time
- Clock display updates only when seconds change for efficiency
- Debug flag is checked early in execution to capture config loading
- All new features maintain backward compatibility with existing configurations

### Developer Notes
- Clock mode located in `CountdownTimer.run_clock()` method
- Clock UI rendering in `DisplayManager.draw_clock_ui()` method
- Debug flag processing in `main()` function before config loading
- Updated help screen in `print_help()` function
- Config generation in `ConfigManager.create_config_content()` method

---

## Previous Releases

_No previous releases documented. This is the first major feature update._
