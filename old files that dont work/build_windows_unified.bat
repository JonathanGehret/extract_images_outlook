@echo off
REM Kamerafallen Tools - Unified Windows Build Script
REM This script builds a standalone Windows executable

setlocal enabledelayedexpansion

echo.
echo =======================================================
echo 🚀 Kamerafallen Tools - Windows Build Script v3.0
echo =======================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version

REM Clean previous builds but keep the spec file
echo.
echo 🧹 Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
echo ✅ Build directories cleaned

REM Install/update requirements
echo.
echo 📦 Installing/updating requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
if errorlevel 1 (
    echo ❌ ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo ✅ Requirements installed successfully

REM Verify critical modules
echo.
echo 🔍 Verifying critical modules...
python -c "import tkinter; print('✅ tkinter available')" || (echo ❌ tkinter missing && pause && exit /b 1)
python -c "import PIL; print('✅ PIL available')" || (echo ❌ PIL missing && pause && exit /b 1)
python -c "import pandas; print('✅ pandas available')" || (echo ❌ pandas missing && pause && exit /b 1)
python -c "import openpyxl; print('✅ openpyxl available')" || (echo ❌ openpyxl missing && pause && exit /b 1)

REM Check if main files exist
echo.
echo 📋 Checking project files...
if not exist "main_gui.py" (
    echo ❌ ERROR: main_gui.py not found
    pause
    exit /b 1
)
if not exist "github_models_analyzer.py" (
    echo ❌ ERROR: github_models_analyzer.py not found
    pause
    exit /b 1
)
if not exist "github_models_io.py" (
    echo ❌ ERROR: github_models_io.py not found
    pause
    exit /b 1
)
if not exist "github_models_api.py" (
    echo ❌ ERROR: github_models_api.py not found
    pause
    exit /b 1
)
echo ✅ All required files found

REM Build executable
echo.
echo 🔧 Building Windows executable...
echo This may take several minutes...
echo.

python -m PyInstaller ^
    --clean ^
    --onefile ^
    --windowed ^
    --name="KamerafallenTools" ^
    --icon="bg_fotos_icon.ico" ^
    --add-data="github_models_analyzer.py;." ^
    --add-data="github_models_io.py;." ^
    --add-data="github_models_api.py;." ^
    --add-data="extract_img_email.py;." ^
    --add-data="rename_images_from_excel.py;." ^
    --hidden-import="tkinter" ^
    --hidden-import="tkinter.ttk" ^
    --hidden-import="tkinter.filedialog" ^
    --hidden-import="tkinter.messagebox" ^
    --hidden-import="PIL" ^
    --hidden-import="PIL.Image" ^
    --hidden-import="PIL.ImageTk" ^
    --hidden-import="PIL.ImageDraw" ^
    --hidden-import="PIL._tkinter_finder" ^
    --hidden-import="pandas" ^
    --hidden-import="openpyxl" ^
    --hidden-import="openpyxl.styles" ^
    --hidden-import="extract_msg" ^
    --hidden-import="requests" ^
    --hidden-import="dotenv" ^
    --hidden-import="numpy" ^
    --hidden-import="argparse" ^
    --hidden-import="github_models_analyzer" ^
    --hidden-import="github_models_io" ^
    --hidden-import="github_models_api" ^
    --hidden-import="extract_img_email" ^
    --hidden-import="rename_images_from_excel" ^
    --exclude-module="matplotlib" ^
    --exclude-module="scipy" ^
    --exclude-module="IPython" ^
    --exclude-module="notebook" ^
    --exclude-module="torch" ^
    --exclude-module="tensorflow" ^
    --exclude-module="PyQt5" ^
    --exclude-module="PyQt6" ^
    --exclude-module="PySide2" ^
    --exclude-module="PySide6" ^
    main_gui.py

if errorlevel 1 (
    echo.
    echo ❌ BUILD FAILED!
    echo Check the error messages above for details.
    echo Common issues:
    echo - Missing dependencies ^(install with: pip install -r requirements.txt^)
    echo - Antivirus blocking PyInstaller
    echo - Insufficient disk space
    pause
    exit /b 1
)

REM Check if executable was created
if not exist "dist\KamerafallenTools.exe" (
    echo ❌ ERROR: Executable was not created!
    if exist "dist" (
        echo Contents of dist folder:
        dir "dist"
    ) else (
        echo dist folder was not created
    )
    pause
    exit /b 1
)

echo.
echo ✅ BUILD SUCCESSFUL!
echo 📁 Executable: dist\KamerafallenTools.exe

REM Get file size
for %%A in ("dist\KamerafallenTools.exe") do (
    set /a size_mb=%%~zA/1024/1024
    echo 📊 Size: !size_mb! MB
)

REM Test the executable quickly
echo.
echo 🧪 Testing executable...
dist\KamerafallenTools.exe --help >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Executable created but may have issues. Test manually.
) else (
    echo ✅ Executable test passed
)

REM Create release package
echo.
echo 📦 Creating release package...
set RELEASE_DIR=KamerafallenTools-Windows-v3.0
if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"

REM Copy executable
copy "dist\KamerafallenTools.exe" "%RELEASE_DIR%\" >nul
if errorlevel 1 (
    echo ❌ Failed to copy executable
    pause
    exit /b 1
)

REM Copy documentation and config files
if exist ".env.example" copy ".env.example" "%RELEASE_DIR%\" >nul
if exist "README.md" copy "README.md" "%RELEASE_DIR%\" >nul
if exist "ANLEITUNG.md" copy "ANLEITUNG.md" "%RELEASE_DIR%\" >nul

REM Create startup script
echo @echo off > "%RELEASE_DIR%\start.bat"
echo REM Kamerafallen Tools Startup Script >> "%RELEASE_DIR%\start.bat"
echo echo 🚀 Starting Kamerafallen Tools... >> "%RELEASE_DIR%\start.bat"
echo cd /d "%%~dp0" >> "%RELEASE_DIR%\start.bat"
echo. >> "%RELEASE_DIR%\start.bat"
echo REM Create .env file if it doesn't exist >> "%RELEASE_DIR%\start.bat"
echo if not exist ".env" if exist ".env.example" copy ".env.example" ".env" >> "%RELEASE_DIR%\start.bat"
echo if not exist ".env" echo ⚠️  Create .env file for AI features ^(copy from .env.example^) >> "%RELEASE_DIR%\start.bat"
echo. >> "%RELEASE_DIR%\start.bat"
echo REM Start the application >> "%RELEASE_DIR%\start.bat"
echo KamerafallenTools.exe >> "%RELEASE_DIR%\start.bat"
echo. >> "%RELEASE_DIR%\start.bat"
echo echo 👋 Kamerafallen Tools closed >> "%RELEASE_DIR%\start.bat"
echo pause >> "%RELEASE_DIR%\start.bat"

REM Create README for the package
echo # Kamerafallen Tools - Windows Package > "%RELEASE_DIR%\README_PACKAGE.txt"
echo. >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo Diese Distribution enthält die eigenständige Windows-Version >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo der Kamerafallen Tools Suite. >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo. >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo ## Schnellstart: >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo 1. Führen Sie start.bat aus ^(empfohlen^) >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo 2. Oder starten Sie KamerafallenTools.exe direkt >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo 3. Optional: GitHub Token in .env-Datei eintragen für KI-Features >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo. >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo ## Enthaltene Tools: >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo - E-Mail Bild-Extraktor: Bilder aus .msg-Dateien extrahieren >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo - KI-Analyzer: Automatische Kamerafallen-Bildanalyse >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo - Bild-Renamer: Umbenennung basierend auf Excel-Daten >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo. >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo ## Systemanforderungen: >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo - Windows 10/11 >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo - Mindestens 4GB RAM >> "%RELEASE_DIR%\README_PACKAGE.txt"
echo - 300MB freier Speicherplatz >> "%RELEASE_DIR%\README_PACKAGE.txt"

echo ✅ Release package created: %RELEASE_DIR%\

REM Show contents
echo.
echo 📋 Package contents:
dir "%RELEASE_DIR%"

echo.
echo =======================================================
echo 🎉 BUILD COMPLETED SUCCESSFULLY!
echo =======================================================
echo.
echo 📁 Executable: %RELEASE_DIR%\KamerafallenTools.exe
echo 📁 Package folder: %RELEASE_DIR%\
echo.
echo ✅ You can now:
echo   1. Test the executable: %RELEASE_DIR%\start.bat
echo   2. Distribute the entire %RELEASE_DIR% folder
echo   3. Create a ZIP archive for easy distribution
echo.
echo 💡 To create ZIP: right-click %RELEASE_DIR% folder ^> Send to ^> Compressed folder
echo.
pause
