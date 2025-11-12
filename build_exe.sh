#!/bin/bash
# Build script for creating executables on Linux/Mac
# Run this with PyInstaller installed

echo "============================================"
echo "HD2 Macro Manager - Executable Builder"
echo "============================================"
echo ""

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "ERROR: PyInstaller is not installed!"
    echo "Please install it with: pip install pyinstaller"
    echo ""
    exit 1
fi

echo "Choose which version to build:"
echo "1. PyQt6 version (Modern UI - Recommended)"
echo "2. Tkinter version (Classic UI)"
echo "3. Both versions"
echo ""

read -p "Enter your choice (1-3): " choice

build_pyqt() {
    echo ""
    echo "Building PyQt6 version..."
    echo "============================================"
    pyinstaller --clean build_pyqt.spec
    if [ $? -ne 0 ]; then
        echo "ERROR: Build failed!"
        exit 1
    fi
    echo ""
    echo "SUCCESS! PyQt6 executable created in dist/HD2_Macros_PyQt6"
}

build_tkinter() {
    echo ""
    echo "Building Tkinter version..."
    echo "============================================"
    pyinstaller --clean build_tkinter.spec
    if [ $? -ne 0 ]; then
        echo "ERROR: Build failed!"
        exit 1
    fi
    echo ""
    echo "SUCCESS! Tkinter executable created in dist/HD2_Macros_Tkinter"
}

case $choice in
    1)
        build_pyqt
        ;;
    2)
        build_tkinter
        ;;
    3)
        echo ""
        echo "Building both versions..."
        echo "============================================"
        build_pyqt
        build_tkinter
        echo ""
        echo "SUCCESS! Both executables created in dist/ folder"
        echo "- HD2_Macros_PyQt6"
        echo "- HD2_Macros_Tkinter"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo "Build complete!"
echo ""
echo "IMPORTANT: Copy stratagems.json and macros.json"
echo "to the same folder as the executable before running."
echo "============================================"
echo ""
