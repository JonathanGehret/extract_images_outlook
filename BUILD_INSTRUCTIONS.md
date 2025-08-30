# Kamerafallen Tools - Build Instructions

## Overview
This document provides instructions for building standalone executables for the Kamerafallen Tools suite on both Linux and Windows platforms.

## Prerequisites

### Linux:
- Python 3.8 or higher
- pip package manager
- All dependencies from `requirements.txt`

### Windows:
- Python 3.8 or higher (from python.org)
- pip package manager
- All dependencies from `requirements.txt`
- Windows 10/11 recommended

## Quick Build Commands

### Linux:
```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build executable
python3 build_final.py

# Create distribution package
python3 create_release.py
```

### Windows:
```batch
REM Install dependencies
python -m pip install -r requirements.txt
python -m pip install pyinstaller

REM Build executable
build_windows_v2.bat
```

## Build Scripts Available

### Linux Scripts:
- **`build_final.py`** - Main optimized build script
- **`create_release.py`** - Creates distribution package with docs
- **`build_linux.sh`** - Simple shell script alternative

### Windows Scripts:
- **`build_windows_v2.bat`** - Updated optimized build script (RECOMMENDED)
- **`build_windows.bat`** - Legacy build script

## Output Structure

### Linux Package:
```
KamerafallenTools-v2.0-YYYYMMDD/
├── KamerafallenTools                 # Main executable (129MB)
├── start.sh                         # Smart startup script
├── .env.example                     # Environment template
├── README.md                        # Project documentation
├── ANLEITUNG.md                     # German instructions
├── BENUTZERHANDBUCH.md             # User guide
└── requirements.txt                 # Dependencies list
```

### Windows Package:
```
KamerafallenTools-v2.0-windows/
├── KamerafallenTools.exe            # Main executable (~100-150MB)
├── start.bat                        # Windows startup script
├── .env.example                     # Environment template
├── README_PACKAGE.txt               # Package documentation
├── BENUTZERHANDBUCH.txt            # German user guide
├── README.md                        # Project documentation
└── ANLEITUNG.md                     # German instructions
```

## Features Included in Executables

✅ **Email Image Extractor**
- Extract images from .msg email files
- Configurable filename patterns
- Batch processing capability

✅ **GitHub Models Analyzer**
- AI-powered image analysis
- Camera trap specific detection
- Excel report generation
- German language interface

✅ **Image Renamer**
- Batch rename based on Excel data
- Automatic backup creation
- Preview functionality

✅ **Integrated Workflow**
- Single launcher interface
- Environment auto-configuration
- Professional German GUI

## Build Optimization

### Included Dependencies:
- tkinter (GUI framework)
- PIL/Pillow (Image processing)
- pandas (Excel handling)
- openpyxl (Excel files)
- extract_msg (Email processing)
- requests (HTTP client)
- python-dotenv (Environment)
- numpy (Data processing)

### Excluded to Reduce Size:
- matplotlib
- scipy
- IPython
- Jupyter notebooks
- Qt frameworks
- Development tools

## Distribution

### Linux:
1. Run `python3 create_release.py`
2. Archive: `KamerafallenTools-v2.0-YYYYMMDD-linux.zip`
3. Size: ~128MB compressed

### Windows:
1. Run `build_windows_v2.bat`
2. Archive the `KamerafallenTools-v2.0-windows/` folder
3. Expected size: ~100-150MB

## Troubleshooting

### Common Issues:

**Build fails with import errors:**
- Ensure all requirements are installed: `pip install -r requirements.txt`
- Update PyInstaller: `pip install --upgrade pyinstaller`

**Large executable size:**
- This is normal for bundled Python applications
- Size includes Python runtime + all dependencies

**GUI doesn't start on target system:**
- Ensure target system has required system libraries
- On Linux: check GTK/Tcl/Tk libraries
- On Windows: should work on Windows 10/11 out of the box

**Analyzer button opens wrong window:**
- This issue is fixed in v2.0 scripts
- Rebuild using the updated scripts

### Platform-Specific Notes:

**Linux:**
- Built on Ubuntu/Debian will work on most distributions
- May need additional libraries on minimal systems
- Test on target distribution before distribution

**Windows:**
- Must be built on Windows for Windows
- Works on Windows 10/11 without additional software
- No administrator rights required to run

## Version History

- **v2.0**: Fixed analyzer button, optimized builds, German interface
- **v1.0**: Initial release with basic functionality

## Support

For build issues or questions:
1. Check this documentation
2. Verify all prerequisites are installed
3. Check the error messages in build output
4. Ensure you're using the correct build script for your platform

## Cross-Platform Building

**Note**: Each platform must be built on its respective OS:
- Linux executables: Build on Linux
- Windows executables: Build on Windows
- No cross-compilation currently supported

For automated builds, consider using CI/CD with platform-specific runners.
