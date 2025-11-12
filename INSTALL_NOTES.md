# Installation Notes for HD2 Macros Development Environment

## Issue Summary
The original `requirements-dev.txt` fails to install on Linux systems due to the `evdev` package (a dependency of `pynput`) requiring compilation of C extensions and Linux kernel headers that may not be available.

## Solution
We've created a workaround that installs `pynput` without the `evdev` dependency. This allows the application to work for most keyboard and mouse operations while avoiding compilation issues.

## Installation Methods

### Method 1: Use the Installation Script (Recommended)
```bash
./install-dev.sh
```

### Method 2: Manual Installation
```bash
# 1. Upgrade pip
python -m pip install --upgrade pip

# 2. Install pynput without evdev
pip install --no-deps pynput==1.7.6

# 3. Install pynput's X11 dependencies
pip install python-xlib six

# 4. Install remaining packages
pip install -r requirements-dev-fixed.txt
```

### Method 3: Fix evdev Compilation (Optional)
If you need full Linux input device support, install system dependencies first:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev linux-headers-generic
pip install -r requirements-dev.txt
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-devel kernel-headers
pip install -r requirements-dev.txt
```

**Arch Linux:**
```bash
sudo pacman -S python linux-headers
pip install -r requirements-dev.txt
```

## Platform Requirements

### Windows
- **Fully Supported** - All features work out of the box
- No special requirements

### Linux (X11)
- **Fully Supported** - Requires X11 display server
- Set `DISPLAY` environment variable (usually `:0`)
- The application will check for DISPLAY and exit with an error if not set

### Linux (Wayland)
- **Not Supported** - This application requires X11 for keyboard event capture
- Please run on a system with X11 or switch to an X11 session
- Wayland support would require significant refactoring

## What's Affected?
- **Working:** Regular keyboard and mouse operations, GUI functionality, all development tools
- **Limited:** Advanced Linux input device features that specifically require evdev
- **No Impact:** PyQt6 GUI, testing, linting, building executables

## Files Created
- `requirements-dev-fixed.txt` - Updated requirements without evdev issues
- `install-dev.sh` - Automated installation script
- `INSTALL_NOTES.md` - This documentation

## Verification
Run the following to verify installation:
```bash
python -c "import pynput, PyQt6, pytest; print('Core packages OK')"
pyinstaller --version
```