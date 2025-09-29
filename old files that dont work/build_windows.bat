@echo off
REM Simple packaging script for Windows

echo 🚀 Building Kamerafallen-Tools for Windows...

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python and add it to your PATH
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install/update PyInstaller and requirements
echo 📦 Installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
if errorlevel 1 (
    echo ❌ ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Check if spec file exists
if not exist "KamerafallenTools.spec" (
    echo ❌ ERROR: KamerafallenTools.spec not found
    echo Make sure you're running this from the project directory
    pause
    exit /b 1
)

REM Create the executable using the spec file
echo 🔧 Building executable...
python -m PyInstaller KamerafallenTools.spec
if errorlevel 1 (
    echo ❌ ERROR: PyInstaller build failed
    echo Check the error messages above for details
    pause
    exit /b 1
)

if exist "dist\KamerafallenTools.exe" (
    echo ✅ Executable created successfully!
    echo 📁 Location: dist\KamerafallenTools.exe
    
    REM Get file size
    for %%A in ("dist\KamerafallenTools.exe") do (
        set /a size_mb=%%~zA/1024/1024
        echo 📊 Size: !size_mb! MB
    )
    
    REM Create portable package
    set PKG_DIR=KamerafallenTools-Windows-Portable
    if exist "%PKG_DIR%" rmdir /s /q "%PKG_DIR%"
    mkdir "%PKG_DIR%"
    
    copy "dist\KamerafallenTools.exe" "%PKG_DIR%\" >nul
    if exist ".env.example" copy ".env.example" "%PKG_DIR%\" >nul
    if exist "README.md" copy "README.md" "%PKG_DIR%\" >nul
    if exist "ANLEITUNG.md" copy "ANLEITUNG.md" "%PKG_DIR%\" >nul
    
    REM Create batch startup script
    echo @echo off > "%PKG_DIR%\start.bat"
    echo cd /d "%%~dp0" >> "%PKG_DIR%\start.bat"
    echo echo 🚀 Starting Kamerafallen Tools... >> "%PKG_DIR%\start.bat"
    echo KamerafallenTools.exe >> "%PKG_DIR%\start.bat"
    echo echo Application closed. >> "%PKG_DIR%\start.bat"
    echo pause >> "%PKG_DIR%\start.bat"
    
    echo 📦 Portable package created: %PKG_DIR%\
    echo.
    echo ✅ BUILD SUCCESSFUL!
    echo You can now test with: %PKG_DIR%\start.bat
) else (
    echo ❌ Build failed! Executable not found
    if exist dist (
        echo Contents of dist folder:
        dir dist
    )
    pause
    exit /b 1
)

echo.
pause
