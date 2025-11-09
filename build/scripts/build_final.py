#!/usr/bin/env python3
"""
Final packaging script for Kamerafallen Tools
Creates optimized executables for Linux and Windows
"""

import os
import sys
import shutil
import subprocess
import platform

def run_command(cmd, description):
    """Run a command with error handling"""
    print(f"\n🔧 {description}")
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e.stderr}")
        return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}/")
            shutil.rmtree(dir_name)

def create_spec_file():
    """Create optimized PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Include all necessary modules
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'pandas',
    'openpyxl',
    'extract_msg',
    'requests',
    'dotenv',
    'numpy',
    'argparse',
    'os',
    'sys',
    'shutil',
    'tempfile',
    'threading',
    'subprocess',
    're',
    'json',
    'base64',
    'io',
    'datetime',
    'pathlib',
]

# Data files to include
datas = [
    ('github_models_analyzer.py', '.'),
    ('github_models_api.py', '.'),
    ('github_models_io.py', '.'),
    ('rename_images_from_excel.py', '.'),
    ('extract_img_email.py', '.'),
    ('.env.example', '.'),
]

a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'IPython',
        'notebook',
        'qtconsole',
        'spyder',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
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
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Could add an icon here
)
'''
    
    with open('KamerafallenTools_optimized.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created optimized spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    system = platform.system().lower()
    
    # Create spec file
    create_spec_file()
    
    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',  # Clean cache
        'KamerafallenTools_optimized.spec'
    ]
    
    success = run_command(cmd, f"Building {system} executable")
    
    if success:
        exe_name = 'KamerafallenTools.exe' if system == 'windows' else 'KamerafallenTools'
        exe_path = os.path.join('dist', exe_name)
        
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print("\n🎉 Build successful!")
            print(f"📁 Executable: {exe_path}")
            print(f"📊 Size: {file_size:.1f} MB")
            print(f"🖥️  Platform: {platform.system()} {platform.machine()}")
            return True
        else:
            print(f"❌ Executable not found at {exe_path}")
            return False
    
    return False

def create_package_info():
    """Create package information file"""
    system = platform.system()
    info_content = f"""# Kamerafallen Tools - Standalone Package

## Package Information
- **Version**: 2.0
- **Build Date**: {subprocess.check_output(['date'], text=True).strip()}
- **Platform**: {system} {platform.machine()}
- **Python Version**: {sys.version}

## Contents
This package contains a standalone executable of the Kamerafallen Tools suite:

### Main Features:
- **Email Image Extractor**: Extract images from .msg email files
- **GitHub Models Analyzer**: AI-powered image analysis for camera trap photos
- **Image Renamer**: Batch rename images based on Excel metadata
- **Integrated Workflow**: Complete German language interface

### Included Tools:
- `KamerafallenTools{'.exe' if system == 'Windows' else ''}` - Main application launcher

## Usage
Simply run the executable - no Python installation required!

### System Requirements:
- {system} operating system
- Minimum 2GB RAM
- 100MB free disk space

## Files Needed:
- The executable can run standalone
- Optional: `.env` file for GitHub token configuration
- Excel files for image metadata (when using renamer)

## Support
For issues or questions, refer to the documentation in the source repository.
"""
    
    with open('dist/README_PACKAGE.txt', 'w') as f:
        f.write(info_content)
    
    print("✅ Created package information")

def main():
    """Main packaging function"""
    print("🚀 Kamerafallen Tools - Final Packaging")
    print("=" * 50)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if build_executable():
        # Create package info
        create_package_info()
        
        # Copy example files
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', 'dist/')
            print("✅ Copied .env.example")
        
        print("\n🎉 Packaging Complete!")
        print("\n📦 Package Contents:")
        for item in os.listdir('dist'):
            item_path = os.path.join('dist', item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path) / (1024 * 1024)
                print(f"   📄 {item} ({size:.1f} MB)")
        
        print("\n✅ Ready to distribute: dist/")
        return True
    else:
        print("\n❌ Packaging failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
