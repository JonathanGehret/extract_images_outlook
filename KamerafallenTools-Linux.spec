# -*- mode: python ; coding: utf-8 -*-# -*- mode: python ; coding: utf-8 -*-

# Linux-specific PyInstaller spec file for Kamerafallen Tools# Linux-specific PyInstaller spec file for Kamerafallen Tools



import sysimport sys

import osimport os



# Add the project directory to the path# Add the project directory to the path

project_dir = os.path.dirname(os.path.abspath(SPEC))project_dir = os.path.dirname(os.path.abspath(SPEC))



a = Analysis(a = Analysis(

    ['main_gui.py'],    ['main_gui.py'],

    pathex=[project_dir],    pathex=[project_dir],

    binaries=[],    binaries=[],

    datas=[    datas=[

        ('github_models_analyzer.py', '.'),        ('github_models_analyzer.py', '.'),

        ('github_models_io.py', '.'),        ('github_models_io.py', '.'),

        ('github_models_api.py', '.'),        ('github_models_api.py', '.'),

        ('extract_img_email.py', '.'),        ('extract_img_email.py', '.'),

        ('rename_images_from_excel.py', '.'),        ('rename_images_from_excel.py', '.'),

        ('.env.example', '.'),        ('.env.example', '.'),

    ],    ],

    hiddenimports=[    hiddenimports=[

        # Tkinter and GUI        # Tkinter and GUI

        'tkinter',        'tkinter',

        'tkinter.ttk',        'tkinter.ttk',

        'tkinter.filedialog',        'tkinter.filedialog',

        'tkinter.messagebox',        'tkinter.messagebox',

        'tkinter.scrolledtext',        'tkinter.scrolledtext',

                

        # PIL/Pillow        # PIL/Pillow

        'PIL',        'PIL',

        'PIL.Image',        'PIL.Image',

        'PIL.ImageTk',        'PIL.ImageTk',

        'PIL.ImageDraw',        'PIL.ImageDraw',

        'PIL._tkinter_finder',        'PIL._tkinter_finder',

        'PIL.ImageFile',        'PIL.ImageFile',

        'PIL.JpegImagePlugin',        'PIL.JpegImagePlugin',

        'PIL.PngImagePlugin',        'PIL.PngImagePlugin',

                

        # Data processing        # Data processing

        'pandas',        'pandas',

        'pandas.io.formats.style',        'pandas.io.formats.style',

        'openpyxl',        'openpyxl',

        'openpyxl.styles',        'openpyxl.styles',

        'openpyxl.workbook',        'openpyxl.workbook',

        'openpyxl.worksheet',        'openpyxl.worksheet',

                

        # Email processing        # Email processing

        'extract_msg',        'extract_msg',

                

        # Network        # Network

        'requests',        'requests',

        'urllib3',        'urllib3',

                

        # Configuration        # Configuration

        'dotenv',        'dotenv',

                

        # Numerical        # Numerical

        'numpy',        'numpy',

                

        # Standard library        # Standard library

        'argparse',        'argparse',

        'threading',        'threading',

        'concurrent.futures',        'concurrent.futures',

        'tempfile',        'tempfile',

        'subprocess',        'subprocess',

        'json',        'json',

        're',        're',

        'os',        'os',

        'sys',        'sys',

        'time',        'time',

        'datetime',        'datetime',

                

        # Project modules        # Project modules

        'github_models_analyzer',        'github_models_analyzer',

        'github_models_io',        'github_models_io',

        'github_models_api',        'github_models_api',

        'extract_img_email',        'extract_img_email',

        'rename_images_from_excel',        'rename_images_from_excel',

    ],    ],

    hookspath=[],    hookspath=[],

    hooksconfig={},    hooksconfig={},

    runtime_hooks=[],    runtime_hooks=[],

    excludes=[    excludes=[

        # Exclude heavy ML libraries not used        # Exclude heavy ML libraries not used

        'torch',        'torch',

        'tensorflow',        'tensorflow',

        'torchvision',        'torchvision',

        'sklearn',        'sklearn',

        'scipy',        'scipy',

        'matplotlib',        'matplotlib',

        'seaborn',        'seaborn',

        'plotly',        'plotly',

                

        # Exclude development tools        # Exclude development tools

        'IPython',        'IPython',

        'jupyter',        'jupyter',

        'notebook',        'notebook',

        'jupyterlab',        'jupyterlab',

                

        # Exclude unused GUI frameworks        # Exclude unused GUI frameworks

        'PyQt5',        'PyQt5',

        'PyQt6',        'PyQt6',

        'PySide2',        'PySide2',

        'PySide6',        'PySide6',

        'wx',        'wx',

                

        # Exclude testing frameworks        # Exclude testing frameworks

        'pytest',        'pytest',

        'unittest',        'unittest',

        'nose',        'nose',

                

        # Exclude build tools        # Exclude build tools

        'setuptools',        'setuptools',

        'distutils',        'distutils',

        'wheel',        'wheel',

        'pip',        'pip',

    ],    ],

    noarchive=False,    noarchive=False,

    optimize=0,    optimize=0,

))

pyz = PYZ(a.pure)pyz = PYZ(a.pure)



exe = EXE(exe = EXE(

    pyz,    pyz,

    a.scripts,    a.scripts,

    a.binaries,    a.binaries,

    a.datas,    a.datas,

    [],    [],

    name='KamerafallenTools-Linux',    name='KamerafallenTools-Linux',

    debug=False,    debug=False,

    bootloader_ignore_signals=False,    bootloader_ignore_signals=False,

    strip=False,    strip=False,

    upx=True,    upx=True,

    upx_exclude=[],    upx_exclude=[],

    runtime_tmpdir=None,    runtime_tmpdir=None,

    console=False,    console=False,

    disable_windowed_traceback=False,    disable_windowed_traceback=False,

    argv_emulation=False,    argv_emulation=False,

    target_arch=None,    target_arch=None,

    codesign_identity=None,    codesign_identity=None,

    entitlements_file=None,    entitlements_file=None,

))

