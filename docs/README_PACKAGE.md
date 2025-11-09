Packaging notes - Camera Trap Tools
=================================

This repo contains utilities for extracting images from Outlook .msg files, analyzing images with a GUI, and renaming images from an Excel workbook.

Files of interest:
- `main_gui.py` - single-entry Tkinter launcher that opens the extractor GUI, launches the analyzer, and runs the renamer with chosen paths.
- `extract_img_email.py` - legacy script to extract attachments from .msg files.
- `rename_images_from_excel.py` - batch renamer that reads `Fotofallendaten_2025.xlsx` and renames images.
- `github_models_analyzer_current_broken.py` - analyzer GUI (may need token configuration).

Quick packaging tips (create a self-contained executable without Python installed):

1) PyInstaller (recommended for simple desktop packaging):

   - Install: `pip install pyinstaller`
   - Build single-file exe on Linux:

     ```bash
     pyinstaller --onefile --add-data "./:./" main_gui.py
     ```

   - This creates a standalone executable in `dist/main_gui` (Linux binary). For Windows, run PyInstaller on Windows or use cross-compilation tools.

2) Dependencies:
   - See `requirements.txt` for Python dependencies used by the tools.

3) Notes:
   - The analyzer uses a GitHub Models API token; configure `GITHUB_TOKEN` inside `github_models_analyzer_current_broken.py` or provide it via env var and modify script to read env var.
   - Large Excel workbooks and image folders will increase memory usage; test on a representative machine before wide distribution.

   Security and local configuration
   --------------------------------

   - A sample env file is provided as `.env.example`. Copy it to `.env` and fill in `GITHUB_MODELS_TOKEN`:

      1. cp .env.example .env
      2. Edit `.env` and set GITHUB_MODELS_TOKEN to your personal token (do not commit `.env`).

   - `.env` is already ignored by `.gitignore` in this repository to prevent accidental commits of secrets.

4) Testing the packaged app:
   - The extracted executable will run the launcher GUI. The analyzer is launched in a separate process and still requires a working Python environment (unless you package the analyzer script as well).
