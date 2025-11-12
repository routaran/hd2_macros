# Building Windows Executables

This guide explains how to create standalone Windows executables for the HD2 Macro Manager.

## Prerequisites

1. **Python 3.8 or higher** installed
2. **All dependencies** installed:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Quick Build (Windows)

Simply run the build script:

```cmd
build_exe.bat
```

Then choose:
- `1` for PyQt6 version (Modern UI - Recommended)
- `2` for Tkinter version (Classic UI)
- `3` for Both versions

## Quick Build (Linux/Mac)

```bash
./build_exe.sh
```

Then choose your preferred version.

## Manual Build Instructions

### Building PyQt6 Version

```bash
pyinstaller --clean build_pyqt.spec
```

Output: `dist/HD2_Macros_PyQt6.exe` (Windows) or `dist/HD2_Macros_PyQt6` (Linux/Mac)

### Building Tkinter Version

```bash
pyinstaller --clean build_tkinter.spec
```

Output: `dist/HD2_Macros_Tkinter.exe` (Windows) or `dist/HD2_Macros_Tkinter` (Linux/Mac)

## After Building

### Important Files

The executable needs these files in the **same folder**:
- `stratagems.json` - Stratagem definitions
- `macros.json` - Macro key bindings

**These files are NOT included in the .exe!** You must copy them manually.

### Distribution Package

To create a distributable package:

1. Create a new folder (e.g., `HD2_Macros_v2.1.0`)
2. Copy the executable from `dist/`
3. Copy `stratagems.json` and `macros.json` from the project root
4. Optionally include `README.md`
5. Zip the folder

Your distribution should look like:
```
HD2_Macros_v2.1.0/
├── HD2_Macros_PyQt6.exe (or HD2_Macros_Tkinter.exe)
├── stratagems.json
├── macros.json
└── README.md (optional)
```

## Customizing the Build

### Adding an Icon

1. Create or obtain a `.ico` file (Windows icon)
2. Save it as `icon.ico` in the project root
3. Edit the `.spec` file:
   ```python
   icon='icon.ico'  # Change from None to 'icon.ico'
   ```
4. Rebuild

### Changing Executable Name

Edit the `.spec` file and change the `name` parameter:

```python
exe = EXE(
    ...
    name='YourCustomName',  # Change this
    ...
)
```

### Debug Mode

To see console output (useful for troubleshooting):

Edit the `.spec` file:
```python
console=True,  # Change from False to True
```

This will show a console window with debug output.

## Troubleshooting

### "PyInstaller is not a recognized command"

**Solution:** Install PyInstaller:
```bash
pip install pyinstaller
```

### "Module not found" errors

**Solution:** Install all dependencies:
```bash
pip install -r requirements-dev.txt
```

### Executable is too large

**Solutions:**
1. Use UPX compression (already enabled in spec files)
2. Exclude unnecessary modules in the `.spec` file
3. Use `--onefile` mode is already enabled

### Antivirus False Positives

Some antivirus programs flag PyInstaller executables as suspicious. This is a known issue with PyInstaller.

**Solutions:**
- Add the executable to your antivirus exceptions
- Build from source on the target machine
- Sign the executable (requires code signing certificate)

### Permission Errors

**On Windows:**
- Run as Administrator
- Check Windows Defender settings

**On Linux/Mac:**
- Ensure `build_exe.sh` is executable: `chmod +x build_exe.sh`
- Check file permissions

## Build Artifacts

After building, you'll find:

```
project_root/
├── build/          # Temporary build files (can be deleted)
├── dist/           # Final executables here
│   ├── HD2_Macros_PyQt6.exe
│   └── HD2_Macros_Tkinter.exe
├── *.spec         # PyInstaller specification files
└── ...
```

The `build/` folder can be safely deleted after a successful build.

## Platform-Specific Notes

### Windows
- Creates `.exe` files
- Requires Visual C++ Redistributable (usually pre-installed)
- Tested on Windows 10/11 x64

### Linux
- Creates executable binaries (no extension)
- May require additional system libraries
- Tested on Ubuntu 20.04+

### macOS
- Creates `.app` bundles or executables
- May require code signing for distribution
- Tested on macOS 11+

## Advanced: Creating Installers

To create a professional installer (Windows):

### Using Inno Setup

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Create a script file (example provided):

```iss
[Setup]
AppName=HD2 Macro Manager
AppVersion=2.1.0
DefaultDirName={pf}\HD2_Macros
DefaultGroupName=HD2 Macro Manager
OutputDir=installer
OutputBaseFilename=HD2_Macros_Setup

[Files]
Source: "dist\HD2_Macros_PyQt6.exe"; DestDir: "{app}"
Source: "stratagems.json"; DestDir: "{app}"
Source: "macros.json"; DestDir: "{app}"
Source: "README.md"; DestDir: "{app}"

[Icons]
Name: "{group}\HD2 Macro Manager"; Filename: "{app}\HD2_Macros_PyQt6.exe"
```

3. Compile the script to create an installer

### Using NSIS

Similar process using [NSIS](https://nsis.sourceforge.io/).

## CI/CD Automation

For automated builds (GitHub Actions example):

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements-dev.txt
      - run: pyinstaller build_pyqt.spec
      - uses: actions/upload-artifact@v3
        with:
          name: HD2-Macros-Windows
          path: dist/HD2_Macros_PyQt6.exe
```

## Support

If you encounter issues:

1. Check the [Troubleshooting section](#troubleshooting)
2. Review PyInstaller documentation: https://pyinstaller.org/
3. Open an issue on GitHub with:
   - Your OS and version
   - Python version
   - Full error message
   - Build command used

## Version Comparison

| Version | File Size | Dependencies | Startup Time |
|---------|-----------|--------------|--------------|
| PyQt6 | ~50-70 MB | PyQt6, pynput | Fast |
| Tkinter | ~15-25 MB | pynput only | Very Fast |

**Note:** Tkinter is included with Python, so it doesn't add to the file size.
