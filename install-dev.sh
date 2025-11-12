#!/bin/bash
# Installation script for development dependencies
# Handles evdev compilation issues on Linux systems

echo "Installing development dependencies for hd2-macros..."
echo "================================================="

# Check Python version
python_version=$(python --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Upgrade pip first
echo -e "\n1. Upgrading pip..."
python -m pip install --upgrade pip

# Install pynput without evdev dependency
echo -e "\n2. Installing pynput (without evdev)..."
pip install --no-deps pynput==1.7.6

# Install pynput's X11 dependencies
echo -e "\n3. Installing pynput X11 dependencies..."
pip install python-xlib six

# Install all other dependencies
echo -e "\n4. Installing remaining development dependencies..."
pip install \
    PyQt6>=6.6.0 \
    pytest>=7.4.0 \
    pytest-cov>=4.1.0 \
    pytest-mock>=3.11.1 \
    black>=23.7.0 \
    pylint>=2.17.5 \
    flake8>=6.1.0 \
    mypy>=1.4.1 \
    types-setuptools \
    build>=0.10.0 \
    wheel>=0.41.0 \
    pyinstaller>=6.0.0

echo -e "\n5. Verifying installation..."
python -c "
import sys
packages = ['pynput', 'PyQt6', 'pytest', 'black', 'pylint', 'flake8', 'mypy', 'build']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print('❌ Missing packages: ' + ', '.join(missing))
    sys.exit(1)
else:
    print('✅ All core packages installed successfully!')
"

# Check PyInstaller
if command -v pyinstaller &> /dev/null; then
    echo "✅ PyInstaller installed: $(pyinstaller --version)"
else
    echo "❌ PyInstaller not found in PATH"
    exit 1
fi

echo -e "\n================================================="
echo "Installation complete!"
echo ""
echo "NOTE: evdev dependency was skipped due to compilation issues."
echo "pynput will work for most keyboard/mouse operations but some"
echo "advanced Linux input device features may be limited."
echo ""
echo "If you need full evdev support, install these system packages:"
echo "  Ubuntu/Debian: sudo apt-get install python3-dev linux-headers-generic"
echo "  Fedora/RHEL:  sudo dnf install python3-devel kernel-headers"
echo "  Arch:         sudo pacman -S python linux-headers"
echo ""
echo "Then run: pip install evdev"
echo "================================================="