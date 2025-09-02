# Build Scripts Overview

This repository contains cross-platform build scripts for creating standalone executables.

## 🐧 Linux Build Files
- **`build_final.py`** - Main optimized build script (RECOMMENDED)
- **`create_release.py`** - Creates distribution package with documentation
- **`build_linux.sh`** - Simple shell script alternative

## 🪟 Windows Build Files  
- **`build_windows_v2.bat`** - Updated optimized build script (RECOMMENDED)
- **`build_windows.bat`** - Legacy build script (use v2 instead)

## 📚 Documentation
- **`BUILD_INSTRUCTIONS.md`** - Comprehensive build guide for both platforms
- **`requirements.txt`** - Python dependencies needed for building

## 🚀 Quick Start

### On Linux:
```bash
python3 build_final.py && python3 create_release.py
```

### On Windows:
```batch
build_windows_v2.bat
```

## ✅ What's Included in Git
✓ All source Python files (.py)
✓ Build scripts (.py, .bat, .sh)  
✓ Documentation (.md)
✓ Requirements (requirements.txt)
✓ Environment template (.env.example)

## ❌ What's Excluded from Git
❌ Generated executables (KamerafallenTools*)
❌ Build artifacts (build/, dist/)
❌ Compiled packages (*.zip)
❌ PyInstaller spec files (*.spec)
❌ Test images and data files

## 📦 Expected Output
Both platforms create ~130MB standalone executables with complete German GUI interface.
