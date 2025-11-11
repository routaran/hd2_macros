# Helldivers 2 - Stratagem Macros

This Python script manages stratagems for Helldivers 2. Developed in response to the absence of native support for Corsair macro functionalities in Linux, this project provides a tailored solution to enhance gaming efficiency. Designed as both a personal utility and a programming exercise, this script enables gamers to create, modify, and execute game macros by binding them to other keys on the keyboard. It represents an application of my programming skills to meet specific gaming needs, and I hope it proves beneficial to others as well.

## Prerequisites

- Python 3.8 or higher

## Installation

To install the script, follow these steps:

1. Clone the repository:
    ```
    https://github.com/routaran/hd2_macros.git
    ```
2. Navigate to the project directory:
    ```
    cd hd2_macros
    ```
Continue with the following steps if you wish to run the python script instead of the precompiled Windows executable.

3. Create a virtual environment:
    ```
    python -m venv env
    ```
4. Activate the virtual environment:
    - On Windows:
        ```
        .\env\Scripts\activate
        ```
    - On Unix or MacOS:
        ```
        source env/bin/activate
        ```
5. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

To use the program:

1. Launch via Python:
    ```
    python gui.py
    ```
Alternatively:

1. Run the precompiled Windows executable; json files MUST be in the same folder as the executable. You can move the executable anywhere you want, as long as it is with the 2 json files. I tested this on my Win10x64 and it worked, not sure about compatibility with other versions as I don't have access to other versions of Windows but it should work. The executable will not work with x86 versions of Windows.
    ```
    stratagems.exe
    ```

2. The program will open a GUI where you can manage your stratagems.

3. You can add a new stratagem by clicking the "Add Stratagem" button and entering the name and keys of the stratagem.

4. You can edit an existing stratagem by clicking the "Edit Stratagem" button, selecting the stratagem to edit, and entering the new keys.

5. You can delete an existing stratagem by clicking the "Delete Stratagem" button and selecting the stratagem to delete. If the stratagem is currently bound to a macro, the macro will be set to "Unassigned".

6. If you make a mistake and accidentally delete stratagems, you can restore the original setup by downloading and replacing the stratagem.json file from the repository. This allows you to revert back to the original stratagems without having to manually re-enter them.

7. You will need to ensure that your stratagem key is set to Left Control and you remap the stratagem arrows to i, j, k, l corresponding to Up, Left, Down, Right.

## Features

- **10 Macro Keys**: Bind stratagems to special keyboard keys (Insert, Home, Page_Up, Delete, End, Page_Down, Arrow keys)
- **30+ Pre-configured Stratagems**: Includes missions, eagle strikes, orbital support, sentries, and weapons
- **Add/Edit/Delete Stratagems**: Full management of stratagem database through GUI
- **Input Validation**: Ensures only valid directional keys (i, j, k, l) are used
- **Auto-backup**: Automatic backup of configuration files before changes
- **Error Handling**: Robust error handling with user-friendly messages
- **Status Bar**: Real-time feedback on operations
- **Keyboard Shortcuts**:
  - `Ctrl+S`: Save all changes
  - `Ctrl+Q`: Quit application
- **Logging**: Detailed execution logs saved to `stratagems.log`
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Thread-Safe**: Proper synchronization for concurrent operations

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save all changes |
| `Ctrl+Q` | Quit application |

## Configuration

The application uses three configuration files:

- **stratagems.json**: Defines stratagem names and their key sequences
- **macros.json**: Maps macro keys to stratagems
- **backups/**: Automatic backups of configuration files (created when you modify settings)

### Customizing Timing

If you experience issues with macro execution speed, you can modify the timing constants in `listener.py`:

```python
STRATAGEM_ACTIVATION_DELAY = 0.1  # Delay after pressing Control key (100ms)
KEY_PRESS_DURATION = 0.05          # How long to hold each directional key (50ms)
KEY_RELEASE_DELAY = 0.05           # Delay between key presses (50ms)
```

## Troubleshooting

### Macros Not Working In-Game

**Problem**: Pressing macro keys doesn't trigger stratagems in Helldivers 2.

**Solutions**:
1. Verify your in-game key bindings:
   - Stratagem key MUST be set to `Left Control`
   - Directional keys MUST be remapped: `i`=Up, `j`=Left, `k`=Down, `l`=Right
2. Ensure the game window is focused when pressing macro keys
3. Check the console output or `stratagems.log` to confirm macros are executing
4. Try increasing timing delays if inputs are too fast for the game

### Permission Errors When Saving

**Problem**: "Permission denied" errors when saving configurations.

**Solutions**:
1. Ensure you have write permissions in the application directory
2. On Linux/Mac: Check file permissions with `ls -la`
3. Run the application from a directory where you have write access
4. On Windows: Try running as administrator (right-click → Run as administrator)

### Application Won't Start

**Problem**: Application crashes or fails to start.

**Solutions**:
1. Verify Python version: `python --version` (requires Python 3.8+)
2. Install/reinstall dependencies: `pip install -r requirements.txt`
3. Check for error messages in terminal/console
4. Delete `stratagems.log` and try again
5. Reinstall pynput: `pip uninstall pynput && pip install pynput==1.7.6`

### GUI Freezes or Becomes Unresponsive

**Problem**: The application window freezes.

**Solutions**:
1. Close and restart the application
2. Check `stratagems.log` for error messages
3. Ensure your JSON files are not corrupted:
   - Validate JSON syntax using an online validator
   - Restore from backup in `backups/` directory
4. Delete configuration files and let the app regenerate defaults

### Invalid Keys Error When Adding Stratagems

**Problem**: "Invalid keys" error when trying to add or edit stratagems.

**Solutions**:
1. Only use these characters: `i`, `j`, `k`, `l`
2. Don't use spaces or other characters
3. Sequences can be any length (e.g., `ijkl` or `ikkjli`)
4. Keys are case-sensitive - use lowercase only

### Listener Not Stopping Properly

**Problem**: Application hangs when closing.

**Solutions**:
1. Use the window's close button (X) rather than force-killing
2. Use `Ctrl+Q` keyboard shortcut to quit gracefully
3. If hung, wait 5-10 seconds before force-closing
4. Check for zombie Python processes: `ps aux | grep python` (Linux/Mac)

### Configuration Files Missing

**Problem**: `stratagems.json` or `macros.json` not found.

**Solutions**:
1. The application will auto-generate default files on first run
2. Download fresh copies from the GitHub repository
3. Restore from `backups/` directory if you made changes
4. Ensure files are in the same directory as the application

## FAQ

### Q: Can I use this with other games?
**A:** This tool is specifically designed for Helldivers 2's stratagem system. However, you could adapt it for other games that use similar key sequence patterns.

### Q: Will I get banned for using this?
**A:** This tool simulates keyboard input, which is generally allowed. It doesn't modify game files or memory. However, always check the game's terms of service. This tool is meant for accessibility and convenience, not competitive advantage.

### Q: Can I add more than 10 macro keys?
**A:** Currently, the application supports 10 pre-configured macro keys. You can modify the code to add more by editing `generate_empty_macros()` in `listener.py`.

### Q: How do I restore default stratagems?
**A:**
1. Delete `stratagems.json` and restart the application, OR
2. Download a fresh copy from the repository
3. Check the `backups/` folder for previous versions

### Q: Can I export/import my configurations?
**A:** Yes! Simply copy your `stratagems.json` and `macros.json` files. These are portable and can be shared with others.

### Q: The timing feels off - keys are pressed too fast/slow
**A:** Edit the timing constants in `listener.py` (lines 24-26). Increase values to slow down, decrease to speed up. Values are in seconds.

### Q: Does this work on Steam Deck?
**A:** Yes! Since it's Python-based and uses `pynput`, it should work on Steam Deck's Linux environment. You may need to install Python and dependencies manually.

### Q: Can I bind stratagems to mouse buttons?
**A:** Currently, only keyboard keys are supported. Mouse button support could be added in a future version.

### Q: How do I run tests?
**A:**
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov
```

### Q: How do I contribute to the project?
**A:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Run tests to ensure everything works
5. Submit a pull request

### Q: Where are logs stored?
**A:** Execution logs are saved to `stratagems.log` in the application directory. This file contains timestamped records of all stratagem executions and errors.

### Q: Can I run this on a server/headless system?
**A:** No, the application requires a graphical environment (X11, Wayland, or Windows GUI) since it uses Tkinter for the interface and pynput for keyboard control.

## Development

### Running from Source

```bash
# Clone the repository
git clone https://github.com/routaran/hd2_macros.git
cd hd2_macros

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python gui.py
```

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/

# Run with coverage report
pytest --cov --cov-report=html

# Run specific test file
pytest tests/test_listener.py
```

### Code Quality

```bash
# Format code
black gui.py listener.py

# Lint code
pylint gui.py listener.py

# Type checking
mypy gui.py listener.py
```

## Version History

### Version 2.0.0
- Added input validation for stratagem keys
- Implemented automatic backup mechanism
- Added comprehensive error handling
- Improved thread safety with locks
- Added status bar and user feedback
- Implemented keyboard shortcuts (Ctrl+S, Ctrl+Q)
- Made window resizable
- Added proper logging framework
- Fixed listener loop inefficiency
- Added comprehensive unit tests
- Added type hints throughout codebase
- Created proper package structure with pyproject.toml
- Confirmation dialogs for destructive operations
- Improved documentation and troubleshooting

### Version 1.0.0
- Initial release
- Basic macro functionality
- GUI for stratagem management
- 10 macro key bindings

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

Please make sure to:
- Write tests for new features
- Update documentation
- Follow the existing code style
- Run tests before submitting: `pytest tests/`

## License

[GPL-3](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Acknowledgments

- Built for the Helldivers 2 community
- Inspired by the lack of Corsair macro support on Linux
- Thanks to all contributors and users providing feedback
