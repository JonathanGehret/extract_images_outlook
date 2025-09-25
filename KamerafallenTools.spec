# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('github_models_analyzer.py', '.'), ('github_models_io.py', '.'), ('github_models_api.py', '.'), ('extract_img_email.py', '.'), ('rename_images_from_excel.py', '.')],
    hiddenimports=['PIL._tkinter_finder', 'PIL.ImageTk', 'PIL.ImageDraw', 'extract_msg', 'pandas', 'openpyxl', 'openpyxl.styles', 'PIL', 'requests', 'dotenv', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'github_models_analyzer', 'github_models_io', 'github_models_api', 'extract_img_email', 'rename_images_from_excel'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'tensorflow', 'torchvision', 'numpy.distutils', 'matplotlib', 'scipy', 'sklearn', 'cv2', 'jupyterlab', 'notebook'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='KamerafallenTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
