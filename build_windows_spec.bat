@echo off
REM Kamerafallen Tools - Alternative Windows Build Script (using spec file)
REM This version uses a dedicated Windows spec file for more control

setlocal enabledelayedexpansion

echo.
echo =======================================================
echo 🚀 Kamerafallen Tools - Windows Build (Spec Version)
echo =======================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found
    pause
    exit /b 1
)
echo ✅ Python found

REM Clean previous builds
echo.
echo 🧹 Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Install requirements
echo.
echo 📦 Installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

REM Verify spec file exists
if not exist "KamerafallenTools-Windows.spec" (
    echo ❌ ERROR: KamerafallenTools-Windows.spec not found
    pause
    exit /b 1
)

REM Build using spec file
echo.
echo 🔧 Building with Windows spec file...
python -m PyInstaller KamerafallenTools-Windows.spec

if errorlevel 1 (
    echo ❌ BUILD FAILED - Check output above
    pause
    exit /b 1
)

if not exist "dist\KamerafallenTools.exe" (
    echo ❌ Executable not created
    pause  
    exit /b 1
)

echo ✅ BUILD SUCCESS!
echo 📁 Executable: dist\KamerafallenTools.exe

REM Get size
for %%A in ("dist\KamerafallenTools.exe") do (
    set /a size_mb=%%~zA/1024/1024
    echo 📊 Size: !size_mb! MB
)

REM Create package
echo.
echo 📦 Creating package...
set PKG=KamerafallenTools-Windows-SpecBuild
if exist "%PKG%" rmdir /s /q "%PKG%"
mkdir "%PKG%"

copy "dist\KamerafallenTools.exe" "%PKG%\" >nul
if exist ".env.example" copy ".env.example" "%PKG%\" >nul
if exist "README.md" copy "README.md" "%PKG%\" >nul

echo @echo off > "%PKG%\start.bat"
echo KamerafallenTools.exe >> "%PKG%\start.bat"  
echo pause >> "%PKG%\start.bat"

echo ✅ Package ready: %PKG%\
dir "%PKG%"

echo.
echo 🎉 Build completed! Test with: %PKG%\start.bat
pause
