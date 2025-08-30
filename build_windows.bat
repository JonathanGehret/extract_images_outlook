@echo off
REM Simple packaging script for Windows

echo 🚀 Building Kamerafallen-Tools for Windows...

REM Install PyInstaller if needed
python -m pip install pyinstaller

REM Create the executable
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name="KamerafallenTools" ^
    --add-data="*.py;." ^
    --hidden-import="PIL._tkinter_finder" ^
    --hidden-import="extract_msg" ^
    --hidden-import="pandas" ^
    --hidden-import="openpyxl" ^
    --hidden-import="PIL" ^
    --hidden-import="requests" ^
    --hidden-import="dotenv" ^
    --hidden-import="tkinter.ttk" ^
    --hidden-import="tkinter.filedialog" ^
    --hidden-import="tkinter.messagebox" ^
    main_gui.py

if exist "dist\KamerafallenTools.exe" (
    echo ✅ Executable created successfully!
    echo 📁 Location: dist\KamerafallenTools.exe
    
    REM Create portable package
    mkdir "dist\KamerafallenTools-windows-portable" 2>nul
    copy "dist\KamerafallenTools.exe" "dist\KamerafallenTools-windows-portable\"
    copy ".env.example" "dist\KamerafallenTools-windows-portable\" 2>nul
    copy "README.md" "dist\KamerafallenTools-windows-portable\" 2>nul
    copy "ANLEITUNG.md" "dist\KamerafallenTools-windows-portable\" 2>nul
    
    REM Create batch startup script
    echo @echo off > "dist\KamerafallenTools-windows-portable\start.bat"
    echo cd /d "%%~dp0" >> "dist\KamerafallenTools-windows-portable\start.bat"
    echo KamerafallenTools.exe >> "dist\KamerafallenTools-windows-portable\start.bat"
    echo pause >> "dist\KamerafallenTools-windows-portable\start.bat"
    
    echo 📦 Portable package created: dist\KamerafallenTools-windows-portable\
) else (
    echo ❌ Build failed!
    exit /b 1
)
