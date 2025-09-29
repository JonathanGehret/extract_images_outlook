@echo off
setlocal EnableExtensions EnableDelayedExpansion

title Kamerafallen Tools - Windows Build (debug)
echo ==================================================
echo   Kamerafallen Tools - Windows Build (debug)
echo ==================================================

pushd "%~dp0"

for /f "delims=" %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "BUILD_STAMP=%%I"
if not defined BUILD_STAMP set "BUILD_STAMP=%DATE:~6,4%%DATE:~3,2%%DATE:~0,2%-%TIME:~0,2%%TIME:~3,2%"
set "BUILD_STAMP=%BUILD_STAMP: =0%"
set "LOG_FILE=%CD%\build_windows_debug-%BUILD_STAMP%.log"

echo Logging detailed output to: %LOG_FILE%
echo ==================================================>> "%LOG_FILE%"
echo [LOG] Kamerafallen Tools debug build started %DATE% %TIME%>> "%LOG_FILE%"
echo Repository root: %CD%>> "%LOG_FILE%"

call :log "Windows version:"
ver >> "%LOG_FILE%"
call :log "System architecture:"
powershell -NoProfile -Command "(Get-CimInstance Win32_OperatingSystem).OSArchitecture" >> "%LOG_FILE%" 2>&1

call :log "PATH environment:"
powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('PATH','Process')" >> "%LOG_FILE%" 2>&1

echo.
echo [1/9] Detecting Python interpreter...
set "DETECTED_PYTHON="
for %%C in ("py -3" "py" "python3" "python") do (
    call :probe_python %%~C
    if defined DETECTED_PYTHON goto :python_found
)

echo ❌ No working Python 3 interpreter found. Install Python 3.8+ and rerun.
call :log "ERROR: No Python interpreter detected"
goto :error

:python_found
set "PYTHON_CMD=%DETECTED_PYTHON%"
call :log "Using Python command: %PYTHON_CMD%"
echo ✅ Using Python command: %PYTHON_CMD%

call :run "Python version" %PYTHON_CMD% --version
call :run "Python executable" %PYTHON_CMD% -c "import sys; print(sys.executable)"
call :run "Pip version" %PYTHON_CMD% -m pip --version

echo.
echo [2/9] Preparing virtual environment...
set "VENV_DIR=%CD%\.build_env"
if not exist "%VENV_DIR%\Scripts\python.exe" (
    call :run "Create virtual environment" %PYTHON_CMD% -m venv "%VENV_DIR%"
) else (
    call :log "Virtual environment already exists at %VENV_DIR%"
)

call :log "Activating virtual environment"
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment.
    call :log "ERROR: Failed to activate venv"
    goto :error
)

call :run "Upgrade pip/setuptools" python -m pip install --upgrade pip setuptools wheel
call :run "Install project requirements" python -m pip install -r requirements.txt
call :run "Install/upgrade PyInstaller" python -m pip install --upgrade pyinstaller
call :run "pip list" python -m pip list
call :run "pip check" python -m pip check

echo.
echo [3/9] Recording environment details...
call :run "Python path (sys.path)" python -c "import sys, pprint; pprint.pprint(sys.path)"
call :run "Active packages (sample)" python -c "import pkgutil; mods=sorted({m.module for m in pkgutil.iter_modules()}); print('Installed top-level modules (sample):'); [print(' -', name) for name in mods[:60]]; print('Total modules discovered:', len(mods))"

echo.
echo [4/9] Cleaning previous build outputs...
for %%D in (build dist __pycache__) do (
    if exist "%%D" (
        call :log "Removing %%D directory"
        rmdir /s /q "%%D"
    ) else (
        call :log "Directory %%D not present"
    )
)

echo.
echo [5/9] Verifying project files...
if not exist "KamerafallenTools-Windows.spec" (
    echo ❌ Required spec file missing: KamerafallenTools-Windows.spec
    call :log "ERROR: Spec file missing"
    goto :error
)
call :run "List key files" cmd /c "dir main_gui.py KamerafallenTools-Windows.spec requirements.txt"

echo.
echo [6/9] Running PyInstaller with debug logging...
set "PYI_TEMP_LOG=%CD%\pyinstaller-%BUILD_STAMP%.log"
set "PYINSTALLER_LOG_LEVEL=DEBUG"
call :run "PyInstaller build" python -m PyInstaller --clean --noconfirm --log-level DEBUG KamerafallenTools-Windows.spec
set "PYINSTALLER_LOG_LEVEL="
if exist "%PYI_TEMP_LOG%" del "%PYI_TEMP_LOG%" >nul 2>&1

if not exist "dist\KamerafallenTools\KamerafallenTools.exe" (
    echo ❌ PyInstaller finished but executable missing.
    call :log "ERROR: Executable missing after build"
    goto :error
)
call :log "PyInstaller executable located at dist\\KamerafallenTools\\KamerafallenTools.exe"

echo.
echo [7/9] Creating portable distribution...
set "PORTABLE_DIR=dist\KamerafallenTools-windows-portable"
if exist "%PORTABLE_DIR%" (
    call :log "Removing old portable directory"
    rmdir /s /q "%PORTABLE_DIR%"
)
mkdir "%PORTABLE_DIR%"
if errorlevel 1 (
    echo ❌ Cannot create portable directory.
    call :log "ERROR: Failed to create portable directory"
    goto :error
)

call :run "Copy PyInstaller output" xcopy /E /I /Y "dist\KamerafallenTools\" "%PORTABLE_DIR%\"
for %%F in (".env.example" "README.md" "ANLEITUNG.md" "README_PACKAGE.md" "requirements.txt") do (
    if exist %%F (
        call :run "Copy %%~nxF" copy /Y %%F "%PORTABLE_DIR%\"
    ) else (
        call :log "Note: %%~nxF not found, skipping"
    )
)

(
    echo @echo off
    echo setlocal
    echo cd /d "%%~dp0"
    echo if not exist ".env" if exist ".env.example" copy ".env.example" ".env" ^>nul
    echo start "Kamerafallen Tools" "KamerafallenTools.exe"
    echo endlocal
) > "%PORTABLE_DIR%\start.bat"
call :log "start.bat created"

echo.
echo [8/9] Creating ZIP archive...
set "ZIP_PATH=dist\KamerafallenTools-windows-%BUILD_STAMP%.zip"
call :run "Compress archive" powershell -NoProfile -Command "Compress-Archive -Path \"%PORTABLE_DIR%\*\" -DestinationPath \"%ZIP_PATH%\" -Force"

echo.
echo [9/9] Capturing final artifact details...
call :run "List dist contents" cmd /c "dir dist"
call :run "Executable size" powershell -NoProfile -Command "$size = (Get-Item 'dist\\KamerafallenTools\\KamerafallenTools.exe').Length / 1MB; '{0:N2} MB' -f $size"

echo.
echo ✅ Debug build finished. Review %LOG_FILE% for full details.
echo Portable folder: %PORTABLE_DIR%
echo Archive: %ZIP_PATH%

call :log "Build completed successfully"
call "%VENV_DIR%\Scripts\deactivate.bat" >nul 2>&1
popd
endlocal
exit /b 0

:probe_python
setlocal EnableDelayedExpansion
set "CAND=%*"
call :log "Probing python command: %CAND% --version"
%CAND% --version >> "%LOG_FILE%" 2>&1
if not errorlevel 1 (
    endlocal & set "DETECTED_PYTHON=%CAND%" & goto :eof
)
endlocal & goto :eof

:run
setlocal EnableDelayedExpansion
set "DESC=%~1"
if "%DESC%"=="" set "DESC=(no description)"
shift
set "CMD=%*"
if "%CMD%"=="" (
    echo ❌ Missing command for task: %DESC%
    call :log "ERROR: Missing command for %DESC%"
    endlocal & exit /b 1
)
echo ► %DESC%
powershell -NoProfile -Command "param($command,$log,$desc) $ts=[DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss'); Add-Content -Path $log -Value \"[$ts] START $desc\"; Add-Content -Path $log -Value \"[$ts] CMD   $command\"; & cmd /c $command 2>&1 ^| Tee-Object -FilePath $log -Append; $code=$LASTEXITCODE; $ts2=[DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss'); Add-Content -Path $log -Value \"[$ts2] END   $desc (exit $code)\"; exit $code" "%CMD%" "%LOG_FILE%" "%DESC%"
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
    echo ✖ %DESC% (exit code %ERR%)
    call :log "ERROR: %DESC% failed with exit %ERR%"
    endlocal & exit /b %ERR%
)
echo ✓ %DESC%
endlocal & exit /b 0

:log
setlocal EnableDelayedExpansion
set "MSG=%~1"
for /f "delims=" %%T in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd\ HH:mm:ss"') do set "TS=%%T"
>> "%LOG_FILE%" echo [%TS%] %MSG%
endlocal & goto :eof

:error
echo.
echo ❌ Debug build encountered errors. See %LOG_FILE% for full details.
if exist "%LOG_FILE%" (
    echo ------- Last 40 log lines -------
    powershell -NoProfile -Command "Get-Content -Path \"%LOG_FILE%\" -Tail 40"
    echo --------------------------------
)
call "%VENV_DIR%\Scripts\deactivate.bat" >nul 2>&1
popd
endlocal
exit /b 1
