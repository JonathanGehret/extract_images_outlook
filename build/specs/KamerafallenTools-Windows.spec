# -*- mode: python ; coding: utf-8 -*-
# Windows-specific PyInstaller spec file for Kamerafallen Tools

import sys
import os

# Add the project directory to the path
project_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main_gui.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        ('github_models_analyzer.py', '.'),
        ('github_models_io.py', '.'),
        ('github_models_api.py', '.'),
        ('extract_img_email.py', '.'),
        ('rename_images_from_excel.py', '.'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        # Tkinter and GUI
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        
        # PIL/Pillow
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',  
        'PIL.ImageDraw',
        'PIL._tkinter_finder',
        'PIL.ImageFile',
        'PIL.JpegImagePlugin',
        'PIL.PngImagePlugin',
        
        # Data processing
        'pandas',
        'pandas.io.formats.style',
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        
        # Email processing
        'extract_msg',
        
        # Network
        'requests',
        'urllib3',
        
        # Configuration
        'dotenv',
        
        # Numerical
        'numpy',
        
        # Standard library
        'argparse',
        'threading',
        'concurrent.futures',
        'tempfile',
        'subprocess',
        'json',
        're',
        'os',
        'sys',
        'time',
        'datetime',
        
        # Project modules
        'github_models_analyzer',
        'github_models_io', 
        'github_models_api',
        'extract_img_email',
        'rename_images_from_excel',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy ML libraries not used
        'torch',
        'tensorflow',
        'torchvision',
        'sklearn',
        'scipy',
        'matplotlib',
        'seaborn',
        'plotly',
        
        # Exclude development tools
        'IPython',
        'jupyter',
        'notebook',
        'jupyterlab',
        
        # Exclude unused GUI frameworks
        'PyQt5',
        'PyQt6', 
        'PySide2',
        'PySide6',
        'wx',
        
        # Exclude testing frameworks
        'pytest',
        'unittest',
        'nose',
        
        # Exclude build tools
        'setuptools',
        'distutils',
        'wheel',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

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
    upx=True,  # Enable UPX compression to reduce size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window for GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='bg_fotos_icon.ico' if os.path.exists('bg_fotos_icon.ico') else None,
)
