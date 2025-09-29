@echo off
REM Debug version of Windows build script with detailed logging

setlocal enabledelayedexpansion

echo =======================================================
echo 🐛 Kamerafallen Tools - DEBUG BUILD SCRIPT
echo =======================================================
echo.

REM Change to script directory and show current directory
cd /d "%~dp0"
echo 📁 Current directory: %CD%
echo.

REM List important files
echo 📋 Checking for required files...
if exist "main_gui.py" (echo ✅ main_gui.py found) else (echo ❌ main_gui.py MISSING)
if exist "github_models_analyzer.py" (echo ✅ github_models_analyzer.py found) else (echo ❌ github_models_analyzer.py MISSING)  
if exist "github_models_io.py" (echo ✅ github_models_io.py found) else (echo ❌ github_models_io.py MISSING)
if exist "github_models_api.py" (echo ✅ github_models_api.py found) else (echo ❌ github_models_api.py MISSING)
if exist "KamerafallenTools.spec" (echo ✅ KamerafallenTools.spec found) else (echo ❌ KamerafallenTools.spec MISSING)
if exist "requirements.txt" (echo ✅ requirements.txt found) else (echo ❌ requirements.txt MISSING)
echo.

REM Test Python
echo 🐍 Testing Python...
python --version
if errorlevel 1 (
    echo ❌ Python not found in PATH
    pause
    exit /b 1
)

REM Test pip
echo 🐍 Testing pip...
python -m pip --version
if errorlevel 1 (
    echo ❌ pip not working
    pause
    exit /b 1
)

REM Check if critical modules are already installed
echo 🔍 Checking installed packages...
python -c "import sys; print('Python executable:', sys.executable)"
python -c "import tkinter; print('✅ tkinter works')" 2>nul || echo "❌ tkinter not available"
python -c "import PIL; print('✅ PIL works')" 2>nul || echo "❌ PIL not available"  
python -c "import pandas; print('✅ pandas works')" 2>nul || echo "❌ pandas not available"
python -c "import pyinstaller; print('✅ PyInstaller available')" 2>nul || echo "❌ PyInstaller not available"
echo.

REM Install requirements with verbose output
echo 📦 Installing requirements (verbose)...
python -m pip install -r requirements.txt --verbose
echo.
python -m pip install pyinstaller --verbose
echo.

REM Clean build directories
echo 🧹 Cleaning build directories...
if exist build (
    rmdir /s /q build
    echo ✅ Removed build directory
) else (
    echo ℹ️  build directory didn't exist
)

if exist dist (
    rmdir /s /q dist  
    echo ✅ Removed dist directory
) else (
    echo ℹ️  dist directory didn't exist
)
echo.

REM Show spec file contents (first 20 lines)
echo 📄 KamerafallenTools.spec contents (first 20 lines):
echo ----------------------------------------
type "KamerafallenTools.spec" | more +0 /C:20
echo ----------------------------------------
echo.

REM Try to build with maximum verbosity
echo 🔧 Starting PyInstaller build (verbose mode)...
echo This will show detailed output...
echo.
python -m PyInstaller --log-level DEBUG KamerafallenTools.spec

REM Check results
echo.
echo 🔍 Build results:
if exist "dist" (
    echo ✅ dist directory created
    echo Contents:
    dir "dist" /b
    echo.
    
    if exist "dist\KamerafallenTools.exe" (
        echo ✅ KamerafallenTools.exe created!
        for %%A in ("dist\KamerafallenTools.exe") do (
            set /a size_mb=%%~zA/1024/1024
            echo 📊 Size: !size_mb! MB (%%~zA bytes)
        )
    ) else (
        echo ❌ KamerafallenTools.exe NOT created
        echo Contents of dist:
        dir "dist"
    )
) else (
    echo ❌ dist directory not created
)

echo.
echo 🔍 Checking for error files:
if exist "build\KamerafallenTools\warn-KamerafallenTools.txt" (
    echo ⚠️  Warning file exists:
    type "build\KamerafallenTools\warn-KamerafallenTools.txt"
    echo.
)

echo.
echo =======================================================
echo 🐛 DEBUG BUILD COMPLETE
echo =======================================================
echo.
echo If the build failed, check the detailed output above.
echo Look for error messages starting with "ERROR:" or "CRITICAL:"
echo.
pause
