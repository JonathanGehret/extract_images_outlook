@echo off
REM Quick rebuild and test script for Windows debugging

echo 🔧 Quick Windows Build and Test
echo ===============================

REM Clean and rebuild
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build using debug script (most comprehensive)
call build_windows_debug.bat

REM If successful, try to run it
if exist "dist\KamerafallenTools.exe" (
    echo.
    echo ✅ Build successful! 
    echo 🧪 Starting executable for testing...
    echo Press Ctrl+C in this window to stop testing
    echo.
    
    REM Start the executable
    start "" "dist\KamerafallenTools.exe"
    
    echo.
    echo 📋 While testing, check for:
    echo   1. Folder paths visible in entry fields
    echo   2. Dummy mode checkbox behavior
    echo   3. Species fields filling when using dummy data
    echo   4. Token loading messages in console
    echo.
    pause
) else (
    echo ❌ Build failed - check output above
    pause
)
