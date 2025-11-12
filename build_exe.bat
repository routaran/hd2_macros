@echo off
REM Build script for creating Windows executables
REM Run this on Windows with PyInstaller installed

echo ============================================
echo HD2 Macro Manager - Windows Executable Builder
echo ============================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed!
    echo Please install it with: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo Choose which version to build:
echo 1. PyQt6 version (Modern UI - Recommended)
echo 2. Tkinter version (Classic UI)
echo 3. Both versions
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto build_pyqt
if "%choice%"=="2" goto build_tkinter
if "%choice%"=="3" goto build_both
echo Invalid choice!
pause
exit /b 1

:build_pyqt
echo.
echo Building PyQt6 version...
echo ============================================
pyinstaller --clean build_pyqt.spec
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo.
echo SUCCESS! PyQt6 executable created in dist/HD2_Macros_PyQt6.exe
goto end

:build_tkinter
echo.
echo Building Tkinter version...
echo ============================================
pyinstaller --clean build_tkinter.spec
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo.
echo SUCCESS! Tkinter executable created in dist/HD2_Macros_Tkinter.exe
goto end

:build_both
echo.
echo Building both versions...
echo ============================================
echo.
echo Building PyQt6 version...
pyinstaller --clean build_pyqt.spec
if errorlevel 1 (
    echo ERROR: PyQt6 build failed!
    pause
    exit /b 1
)
echo.
echo Building Tkinter version...
pyinstaller --clean build_tkinter.spec
if errorlevel 1 (
    echo ERROR: Tkinter build failed!
    pause
    exit /b 1
)
echo.
echo SUCCESS! Both executables created in dist/ folder
echo - HD2_Macros_PyQt6.exe
echo - HD2_Macros_Tkinter.exe

:end
echo.
echo ============================================
echo Build complete!
echo.
echo IMPORTANT: Copy stratagems.json and macros.json
echo to the same folder as the .exe file before running.
echo ============================================
echo.
pause
