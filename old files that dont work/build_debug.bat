@echo off
REM Windows Debug Build Script - Comprehensive debugging version

echo ===== Kamerafallen Tools - Debug Build Script =====
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check Python
echo 🐍 Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found. Please install Python first.
    echo Make sure Python is added to your PATH.
    pause
    exit /b 1
)
echo ✅ Python found

REM Install requirements
echo.
echo 📦 Installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo ✅ Requirements installed

REM Clean previous builds
echo.
echo 🧹 Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__

REM Create debug version first
echo.
echo 🔧 Creating DEBUG version...
python -m pyinstaller --onefile --windowed --name "KamerafallenTools-Debug" ^
    --add-data "github_models_analyzer.py;." ^
    --add-data "github_models_io.py;." ^
    --add-data "github_models_api.py;." ^
    --add-data "extract_img_email.py;." ^
    --add-data "rename_images_from_excel.py;." ^
    --add-data "requirements.txt;." ^
    --add-data ".env.example;." ^
    --hidden-import "PIL.ImageTk" ^
    --hidden-import "PIL.ImageDraw" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "dotenv" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.filedialog" ^
    --hidden-import "tkinter.messagebox" ^
    --hidden-import "pandas" ^
    --hidden-import "openpyxl" ^
    --hidden-import "requests" ^
    debug_analyzer.py

if %errorlevel% neq 0 (
    echo ❌ ERROR: Debug build failed!
    echo Check the output above for error details.
    pause
    exit /b 1
)
echo ✅ Debug version created

REM Create production version
echo.
echo 🔧 Creating PRODUCTION version...
python -m pyinstaller --onefile --windowed --name "KamerafallenTools" ^
    --add-data "github_models_analyzer.py;." ^
    --add-data "github_models_io.py;." ^
    --add-data "github_models_api.py;." ^
    --add-data "extract_img_email.py;." ^
    --add-data "rename_images_from_excel.py;." ^
    --add-data "requirements.txt;." ^
    --add-data ".env.example;." ^
    --icon "bg_fotos_icon.ico" ^
    --hidden-import "PIL.ImageTk" ^
    --hidden-import "PIL.ImageDraw" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "dotenv" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.filedialog" ^
    --hidden-import "tkinter.messagebox" ^
    --hidden-import "pandas" ^
    --hidden-import "openpyxl" ^
    --hidden-import "requests" ^
    main_gui.py

if %errorlevel% neq 0 (
    echo ❌ ERROR: Production build failed!
    echo Check the output above for error details.
    pause
    exit /b 1
)
echo ✅ Production version created

REM Setup environment files
echo.
echo 📄 Setting up environment files...

REM Copy .env.example to dist folder
copy ".env.example" "dist\.env.example" >nul
echo ✅ Copied .env.example to dist folder

REM Create a sample .env file in dist with instructions
echo # Kamerafallen Tools - Environment Configuration > "dist\.env"
echo # Copy this file and rename it to .env, then add your GitHub token >> "dist\.env"
echo. >> "dist\.env"
echo # GitHub Models API Token (required for AI analysis) >> "dist\.env"
echo GITHUB_MODELS_TOKEN=your_github_token_here >> "dist\.env"
echo. >> "dist\.env"
echo # Optional: Default folders (can be set via GUI instead) >> "dist\.env"
echo #ANALYZER_IMAGES_FOLDER=C:\path\to\your\images >> "dist\.env"
echo #ANALYZER_OUTPUT_EXCEL=C:\path\to\your\output.xlsx >> "dist\.env"

echo ✅ Created sample .env file in dist folder

REM Create startup scripts
echo.
echo 📝 Creating startup scripts...

REM Debug startup script
echo @echo off > "dist\start-debug.bat"
echo REM Debug Startup Script for Kamerafallen Tools >> "dist\start-debug.bat"
echo echo 🐛 Starting DEBUG version... >> "dist\start-debug.bat"
echo echo This will show detailed debug information. >> "dist\start-debug.bat"
echo echo. >> "dist\start-debug.bat"
echo cd /d "%%~dp0" >> "dist\start-debug.bat"
echo KamerafallenTools-Debug.exe >> "dist\start-debug.bat"
echo echo. >> "dist\start-debug.bat"
echo echo Debug session ended. >> "dist\start-debug.bat"
echo pause >> "dist\start-debug.bat"

REM Production startup script
echo @echo off > "dist\start.bat"
echo REM Startup Script for Kamerafallen Tools >> "dist\start.bat"
echo echo 🚀 Starting Kamerafallen Tools... >> "dist\start.bat"
echo cd /d "%%~dp0" >> "dist\start.bat"
echo. >> "dist\start.bat"
echo REM Check if .env exists, if not, remind user >> "dist\start.bat"
echo if not exist ".env" ( >> "dist\start.bat"
echo     echo ⚠️  No .env file found! >> "dist\start.bat"
echo     echo For AI features, copy .env.example to .env and add your GitHub token >> "dist\start.bat"
echo     echo. >> "dist\start.bat"
echo ) >> "dist\start.bat"
echo. >> "dist\start.bat"
echo KamerafallenTools.exe >> "dist\start.bat"
echo echo. >> "dist\start.bat"
echo echo Application closed. >> "dist\start.bat"
echo pause >> "dist\start.bat"

echo ✅ Created startup scripts

REM Create user guide
echo.
echo 📚 Creating user guide...
echo # Kamerafallen Tools - Windows User Guide > "dist\GUIDE.txt"
echo. >> "dist\GUIDE.txt"
echo ## Quick Start >> "dist\GUIDE.txt"
echo 1. For debugging: Run start-debug.bat >> "dist\GUIDE.txt"
echo 2. For normal use: Run start.bat >> "dist\GUIDE.txt"
echo. >> "dist\GUIDE.txt"
echo ## Setting up AI Features >> "dist\GUIDE.txt"
echo 1. Copy .env.example to .env >> "dist\GUIDE.txt"
echo 2. Edit .env and replace 'your_github_token_here' with your actual token >> "dist\GUIDE.txt"
echo 3. Get a GitHub token at: https://github.com/settings/tokens >> "dist\GUIDE.txt"
echo    - Create "Personal access token (classic)" >> "dist\GUIDE.txt"
echo    - Enable "Models" permission >> "dist\GUIDE.txt"
echo. >> "dist\GUIDE.txt"
echo ## Troubleshooting >> "dist\GUIDE.txt"
echo - If images don't load: Check folder permissions >> "dist\GUIDE.txt"
echo - If AI doesn't work: Check your .env file and GitHub token >> "dist\GUIDE.txt"
echo - If GUI looks wrong: Try running as administrator >> "dist\GUIDE.txt"
echo. >> "dist\GUIDE.txt"
echo ## Files in this package: >> "dist\GUIDE.txt"
echo - KamerafallenTools.exe: Main application >> "dist\GUIDE.txt"
echo - KamerafallenTools-Debug.exe: Debug version >> "dist\GUIDE.txt"
echo - start.bat: Normal startup script >> "dist\GUIDE.txt"
echo - start-debug.bat: Debug startup script >> "dist\GUIDE.txt"
echo - .env: Environment configuration (edit this!) >> "dist\GUIDE.txt"
echo - .env.example: Template for environment file >> "dist\GUIDE.txt"

echo ✅ Created user guide

echo.
echo ===== BUILD COMPLETE =====
echo.
echo 📁 Files created in dist folder:
dir "dist" /b
echo.
echo 🎯 NEXT STEPS:
echo 1. First run: start-debug.bat (to see what's happening)
echo 2. Set up AI: Edit dist\.env and add your GitHub token  
echo 3. Normal use: start.bat
echo.
echo 🐛 If you have issues:
echo - The debug version will show exactly what's wrong
echo - Check the GUIDE.txt file for troubleshooting
echo.
echo Ready to test! 🚀
pause
