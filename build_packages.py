#!/usr/bin/env python3
"""
Packaging script for Kamerafallen-Tools
Creates standalone executables for Linux and Windows
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"🔧 Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print("✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def install_pyinstaller():
    """Install PyInstaller if not present"""
    try:
        import importlib.util
        spec = importlib.util.find_spec("PyInstaller")
        if spec is not None:
            print("✅ PyInstaller already installed")
            return True
        else:
            raise ImportError("PyInstaller not found")
    except ImportError:
        print("📦 Installing PyInstaller...")
        return run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_spec_file():
    """Create PyInstaller spec file for main GUI"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files
datas = []

# Collect hidden imports
hiddenimports = [
    'PIL._tkinter_finder',
    'extract_msg',
    'pandas',
    'openpyxl', 
    'PIL',
    'requests',
    'dotenv',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'threading',
    'subprocess',
    'tempfile',
    'argparse',
    're',
    'json',
    'base64',
    'shutil',
    'glob',
    'datetime',
    'io',
    'platform',
    'webbrowser',
    'pathlib'
]

block_cipher = None

a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KamerafallenTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)
'''
    
    with open('kamerafallen_tools.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    system = platform.system().lower()
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Build executable
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "kamerafallen_tools.spec"]
    if not run_command(cmd):
        return False
    
    # Check if executable was created
    if system == "windows":
        exe_name = "KamerafallenTools.exe"
    else:
        exe_name = "KamerafallenTools"
    
    exe_path = Path("dist") / exe_name
    if exe_path.exists():
        print(f"✅ Executable created: {exe_path}")
        print(f"📁 Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        return True
    else:
        print(f"❌ Executable not found at {exe_path}")
        return False

def create_portable_package():
    """Create a portable package with all necessary files"""
    system = platform.system().lower()
    package_name = f"KamerafallenTools-{system}-portable"
    
    # Create package directory
    package_dir = Path("dist") / package_name
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)
    
    # Copy executable
    if system == "windows":
        exe_name = "KamerafallenTools.exe"
    else:
        exe_name = "KamerafallenTools"
    
    src_exe = Path("dist") / exe_name
    dst_exe = package_dir / exe_name
    
    if src_exe.exists():
        shutil.copy2(src_exe, dst_exe)
        print(f"✅ Copied executable to {dst_exe}")
    else:
        print(f"❌ Source executable not found: {src_exe}")
        return False
    
    # Copy supporting files
    supporting_files = [
        ".env.example",
        "README.md",
        "ANLEITUNG.md"
    ]
    
    for file_name in supporting_files:
        src_file = Path(file_name)
        if src_file.exists():
            dst_file = package_dir / file_name
            shutil.copy2(src_file, dst_file)
            print(f"✅ Copied {file_name}")
        else:
            print(f"⚠ Optional file not found: {file_name}")
    
    # Create startup script for convenience
    if system != "windows":
        startup_script = package_dir / "start_kamerafallen_tools.sh"
        with open(startup_script, 'w') as f:
            f.write(f'''#!/bin/bash
# Kamerafallen Tools Starter Script
cd "$(dirname "$0")"
./{exe_name}
''')
        os.chmod(startup_script, 0o755)
        print("✅ Created startup script")
    
    # Create README for the package
    readme_content = f"""# Kamerafallen-Tools - Portable Version

Dies ist eine portable Version der Kamerafallen-Tools, die ohne Python-Installation ausgeführt werden kann.

## Verwendung

### Linux:
1. Entpacken Sie das Archiv
2. Führen Sie `./KamerafallenTools` aus oder verwenden Sie `./start_kamerafallen_tools.sh`

### Windows:
1. Entpacken Sie das Archiv  
2. Doppelklicken Sie auf `KamerafallenTools.exe`

## Funktionen

- **Bilder aus E-Mail extrahieren**: Extrahiert Anhänge aus .msg-Dateien
- **GitHub Models Analyzer**: Analysiert Kamerafallen-Bilder mit KI
- **Bilder umbenennen**: Benennt Bilder basierend auf Excel-Daten um

## Konfiguration

Kopieren Sie `.env.example` zu `.env` und fügen Sie Ihren GitHub Models Token hinzu:

```
GITHUB_MODELS_TOKEN=your_token_here
ANALYZER_IMAGES_FOLDER=/path/to/images
ANALYZER_OUTPUT_EXCEL=/path/to/output.xlsx
```

## Systemvoraussetzungen

- {system.title()}: Keine zusätzlichen Abhängigkeiten erforderlich
- Für die KI-Analyse: Internetverbindung und GitHub Models Token

## Version

Erstellt am: {os.popen('date').read().strip()}
System: {platform.system()} {platform.machine()}
Python: {sys.version.split()[0]}

"""
    
    with open(package_dir / "README_PORTABLE.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Portable package created: {package_dir}")
    return True

def create_archive():
    """Create compressed archive of the portable package"""
    system = platform.system().lower()
    package_name = f"KamerafallenTools-{system}-portable"
    package_dir = Path("dist") / package_name
    
    if not package_dir.exists():
        print(f"❌ Package directory not found: {package_dir}")
        return False
    
    # Create archive
    archive_base = f"dist/KamerafallenTools-{system}-v1.0"
    
    if system == "windows":
        archive_path = f"{archive_base}.zip"
        shutil.make_archive(archive_base, 'zip', package_dir.parent, package_dir.name)
    else:
        archive_path = f"{archive_base}.tar.gz"
        shutil.make_archive(archive_base, 'gztar', package_dir.parent, package_dir.name)
    
    if os.path.exists(archive_path):
        size_mb = os.path.getsize(archive_path) / (1024*1024)
        print(f"✅ Archive created: {archive_path}")
        print(f"📁 Archive size: {size_mb:.1f} MB")
        return True
    else:
        print(f"❌ Archive creation failed: {archive_path}")
        return False

def main():
    """Main packaging workflow"""
    print("🚀 Kamerafallen-Tools Packaging Script")
    print("=" * 50)
    
    system = platform.system()
    print(f"🖥 System: {system}")
    print(f"🐍 Python: {sys.version}")
    
    steps = [
        ("Installing PyInstaller", install_pyinstaller),
        ("Creating spec file", create_spec_file),
        ("Building executable", build_executable),
        ("Creating portable package", create_portable_package),
        ("Creating archive", create_archive)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Failed at step: {step_name}")
            return False
    
    print("\n🎉 Packaging completed successfully!")
    print("\n📦 Available packages:")
    
    dist_dir = Path("dist")
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            if item.is_file() and (item.suffix in ['.zip', '.gz'] or item.name.endswith('.tar.gz')):
                size_mb = item.stat().st_size / (1024*1024)
                print(f"  📁 {item.name} ({size_mb:.1f} MB)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
