@echo off
REM Kamerafallen Tools - Windows Build Script (Updated v2.0)
REM Run this on a Windows machine with Python and PyInstaller installed

echo 🚀 Kamerafallen Tools - Windows Packaging v2.0
echo ==================================================

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist *.spec del *.spec

echo 🧹 Cleaned build directories

REM Install requirements
echo 📦 Installing requirements...
python -m pip install -r requirements.txt
python -m pip install pyinstaller

REM Build executable using optimized approach
echo 🔧 Building Windows executable...
python -m PyInstaller --clean ^
    --onefile ^
    --windowed ^
    --name "KamerafallenTools" ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageTk ^
    --hidden-import PIL.ImageDraw ^
    --hidden-import pandas ^
    --hidden-import openpyxl ^
    --hidden-import extract_msg ^
    --hidden-import requests ^
    --hidden-import dotenv ^
    --hidden-import numpy ^
    --hidden-import argparse ^
    --add-data "github_models_analyzer.py;." ^
    --add-data "github_models_api.py;." ^
    --add-data "github_models_io.py;." ^
    --add-data "rename_images_from_excel.py;." ^
    --add-data "extract_img_email.py;." ^
    --add-data ".env.example;." ^
    --exclude-module matplotlib ^
    --exclude-module scipy ^
    --exclude-module IPython ^
    --exclude-module notebook ^
    --exclude-module PyQt5 ^
    --exclude-module PyQt6 ^
    --exclude-module PySide2 ^
    --exclude-module PySide6 ^
    main_gui.py

if exist "dist\KamerafallenTools.exe" (
    echo ✅ Build successful!
    echo 📁 Executable: dist\KamerafallenTools.exe
    
    REM Get file size
    for %%A in ("dist\KamerafallenTools.exe") do (
        set /a size_mb=%%~zA/1024/1024
        echo 📊 Size: !size_mb! MB
    )
    
    REM Copy additional files
    copy ".env.example" "dist\" >nul 2>&1
    
    REM Create package info
    echo # Kamerafallen Tools - Windows Package v2.0 > "dist\README_PACKAGE.txt"
    echo. >> "dist\README_PACKAGE.txt"
    echo This package contains the standalone Windows executable >> "dist\README_PACKAGE.txt"
    echo for the Kamerafallen Tools suite. >> "dist\README_PACKAGE.txt"
    echo. >> "dist\README_PACKAGE.txt"
    echo ## Features: >> "dist\README_PACKAGE.txt"
    echo - Email Image Extractor: Extract images from .msg files >> "dist\README_PACKAGE.txt"
    echo - GitHub Models Analyzer: AI-powered camera trap image analysis >> "dist\README_PACKAGE.txt"
    echo - Image Renamer: Batch rename images based on Excel metadata >> "dist\README_PACKAGE.txt"
    echo - Complete German language interface >> "dist\README_PACKAGE.txt"
    echo. >> "dist\README_PACKAGE.txt"
    echo ## Usage: >> "dist\README_PACKAGE.txt"
    echo Simply run KamerafallenTools.exe - no installation required! >> "dist\README_PACKAGE.txt"
    echo Optional: Configure .env file for AI features >> "dist\README_PACKAGE.txt"
    
    REM Create release package
    set RELEASE_DIR=KamerafallenTools-v2.0-windows
    if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
    mkdir "%RELEASE_DIR%"
    
    copy "dist\KamerafallenTools.exe" "%RELEASE_DIR%\"
    copy "dist\.env.example" "%RELEASE_DIR%\" 2>nul
    copy "dist\README_PACKAGE.txt" "%RELEASE_DIR%\"
    copy "README.md" "%RELEASE_DIR%\" 2>nul
    copy "ANLEITUNG.md" "%RELEASE_DIR%\" 2>nul
    
    REM Create Windows startup script
    echo @echo off > "%RELEASE_DIR%\start.bat"
    echo REM Kamerafallen Tools Startup Script >> "%RELEASE_DIR%\start.bat"
    echo echo 🚀 Starting Kamerafallen Tools... >> "%RELEASE_DIR%\start.bat"
    echo cd /d "%%~dp0" >> "%RELEASE_DIR%\start.bat"
    echo if not exist ".env" if exist ".env.example" copy ".env.example" ".env" >> "%RELEASE_DIR%\start.bat"
    echo if not exist ".env" echo ⚠️  Please create .env file for AI features >> "%RELEASE_DIR%\start.bat"
    echo KamerafallenTools.exe >> "%RELEASE_DIR%\start.bat"
    echo echo 👋 Kamerafallen Tools closed. >> "%RELEASE_DIR%\start.bat"
    echo pause >> "%RELEASE_DIR%\start.bat"
    
    REM Create user guide
    echo # Kamerafallen Tools - Windows Benutzerhandbuch > "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo. >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo ## Schnellstart >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo 1. Fuehren Sie start.bat aus (empfohlen) oder KamerafallenTools.exe >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo 2. Bei erstem Start wird eine .env-Datei erstellt >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo 3. Optional: GitHub Token in .env-Datei eintragen >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo. >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo ## Tools >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo - E-Mail Extraktor: Bilder aus .msg-Dateien extrahieren >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo - Analyzer: KI-gestuetzte Bildanalyse fuer Kamerafallen >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo - Renamer: Bilder basierend auf Excel-Daten umbenennen >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo. >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo ## Systemanforderungen >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo - Windows 10/11 >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo - Mindestens 2GB RAM >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    echo - 200MB freier Speicherplatz >> "%RELEASE_DIR%\BENUTZERHANDBUCH.txt"
    
    echo 🎉 Windows packaging complete!
    echo 📦 Package ready in: %RELEASE_DIR%\
    dir "%RELEASE_DIR%"
    
    echo.
    echo ✅ Ready to distribute: %RELEASE_DIR%\KamerafallenTools.exe
    echo 📋 Package includes: executable, documentation, startup script, .env example
) else (
    echo ❌ Build failed!
    echo Check the error messages above for details.
    exit /b 1
)

echo.
echo 💡 Distribution ready! Archive the %RELEASE_DIR% folder for distribution.
echo 📦 Create ZIP: 7z a KamerafallenTools-v2.0-windows.zip %RELEASE_DIR%\*
pause
