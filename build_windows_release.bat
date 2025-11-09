@echo off
setlocal EnableExtensions EnableDelayedExpansion

title Kamerafallen Tools - Windows Build
echo ==================================================
echo   Kamerafallen Tools - Windows Build (release)
echo ==================================================

rem Change to repository root
pushd "%~dp0"

rem Timestamp for artifacts
for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "BUILD_STAMP=%%I"
if not defined BUILD_STAMP set "BUILD_STAMP=%DATE:~6,4%%DATE:~3,2%%DATE:~0,2%-%TIME:~0,2%%TIME:~3,2%"
set "BUILD_STAMP=%BUILD_STAMP: =0%"

echo.
echo [1/7] Detecting Python interpreter...
set "DETECTED_PYTHON="
py -3 --version >nul 2>&1 && set "DETECTED_PYTHON=py -3"
if not defined DETECTED_PYTHON (
    py --version >nul 2>&1 && set "DETECTED_PYTHON=py"
)
if not defined DETECTED_PYTHON (
    python3 --version >nul 2>&1 && set "DETECTED_PYTHON=python3"
)
if not defined DETECTED_PYTHON (
    python --version >nul 2>&1 && set "DETECTED_PYTHON=python"
)
if not defined DETECTED_PYTHON (
    echo ❌ No suitable Python interpreter found. Please install Python 3.8+.
    goto :error
)
set "PYTHON_CMD=%DETECTED_PYTHON%"
echo ✅ Using Python command: %PYTHON_CMD%

echo.
echo [2/7] Preparing dedicated virtual environment...
set "VENV_DIR=%CD%\.build_env"
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating venv in %VENV_DIR% ...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment.
        goto :error
    )
)
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ Unable to activate virtual environment.
    goto :error
)

echo Upgrading pip/setuptools...
python -m pip install --upgrade pip setuptools wheel >nul
if errorlevel 1 (
    echo ❌ Failed to upgrade pip/setuptools.
    goto :error
)

echo Installing project requirements...
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found.
    goto :error
)
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Requirement installation failed.
    goto :error
)

echo Ensuring PyInstaller is available...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ❌ Failed to install PyInstaller.
    goto :error
)

echo.
echo [3/7] Cleaning previous build artifacts...
for %%D in (build dist __pycache__) do (
    if exist "%%D" (
        echo Removing %%D\
        rmdir /s /q "%%D"
    )
)

echo.
echo [4/7] Verifying spec file...
if not exist "KamerafallenTools-Windows.spec" (
    echo ❌ KamerafallenTools-Windows.spec not found.
    goto :error
)

echo.
echo [5/7] Building executable with PyInstaller (this can take a few minutes)...
python -m PyInstaller --clean --noconfirm --log-level WARN KamerafallenTools-Windows.spec
if errorlevel 1 (
    echo ❌ PyInstaller build failed.
    goto :error
)

if not exist "dist\KamerafallenTools\KamerafallenTools.exe" (
    echo ❌ Expected executable not found in dist\KamerafallenTools\
    goto :error
)

echo.
echo [6/7] Creating portable distribution folder...
set "PORTABLE_DIR=dist\KamerafallenTools-windows-portable"
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%"
if errorlevel 1 (
    echo ❌ Could not create %PORTABLE_DIR%.
    goto :error
)

robocopy "dist\KamerafallenTools" "%PORTABLE_DIR%" /E >nul
if errorlevel 8 (
    echo ❌ Failed to copy build output into portable directory.
    goto :error
)

for %%F in (".env.example" "README.md" "ANLEITUNG.md" "README_PACKAGE.md" "requirements.txt") do (
    if exist %%F copy /Y %%F "%PORTABLE_DIR%" >nul
)

(
    echo @echo off
    echo setlocal
    echo cd /d "%%~dp0"
    echo if not exist ".env" if exist ".env.example" copy ".env.example" ".env" ^>nul
    echo start "Kamerafallen Tools" "KamerafallenTools.exe"
    echo endlocal
) > "%PORTABLE_DIR%\start.bat"


echo.
echo [7/7] Creating zip archive...
set "ZIP_PATH=dist\KamerafallenTools-windows-%BUILD_STAMP%.zip"
powershell -NoProfile -Command "Compress-Archive -Path \"%PORTABLE_DIR%\*\" -DestinationPath \"%ZIP_PATH%\" -Force" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Could not create ZIP automatically. You can create it manually if needed.
) else (
    echo 📦 Created archive: %ZIP_PATH%
)

echo.
echo ✅ Build complete!
for %%A in ("%PORTABLE_DIR%\KamerafallenTools.exe") do (
    if exist %%A (
        set "_SIZE=%%~zA"
        set /a "_SIZE_MB=_SIZE/1024/1024"
        echo 📁 Executable: %%~fA (approx !_SIZE_MB! MB)
    )
)
echo 📂 Portable folder: %PORTABLE_DIR%
if exist "%ZIP_PATH%" echo 📦 Archive: %ZIP_PATH%

goto :cleanup

:error
echo.
echo Build aborted due to errors.

:cleanup
if exist "%VENV_DIR%\Scripts\deactivate.bat" call "%VENV_DIR%\Scripts\deactivate.bat" >nul 2>&1
popd
endlocal
exit /b
