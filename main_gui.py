#!/usr/bin/env python3
"""
Main launcher GUI for the camera-trap tools.

Two main buttons:
- "Extract images from email" opens a small GUI to select input (.msg) folder, output folder and run extraction.
- "Open Analyzer" launches the existing analyzer script in a separate process.
- "Run Renamer" runs the renamer script using selected Excel and image-folder settings by creating a temporary configured copy.

This file is purposely self-contained so it can be used as the single entrypoint for packaging.
"""

import os
import re
import tempfile
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw


def extract_msg_files(input_folder, output_folder, name_pattern="fotofallen_2025_{num}.jpeg"):
    """Extract attachments from .msg files in input_folder into output_folder.

    name_pattern may include {num} and optional {idx} for multi-attachment messages.
    """
    try:
        import extract_msg
    except Exception:
        raise RuntimeError("Fehlende Abhängigkeit 'extract_msg'. Installieren mit: pip install extract_msg")

    os.makedirs(output_folder, exist_ok=True)
    processed = 0
    errors = []

    for file_name in os.listdir(input_folder):
        if not file_name.lower().endswith('.msg'):
            continue
        match = re.search(r"\((\d+)\)\.msg$", file_name)
        if match:
            number = match.group(1)
        else:
            # fallback: use filename without extension
            number = os.path.splitext(file_name)[0]

        try:
            msg = extract_msg.Message(os.path.join(input_folder, file_name))
            attachments = list(msg.attachments)
            if not attachments:
                continue

            for idx, attachment in enumerate(attachments, start=1):
                _, ext = os.path.splitext(attachment.longFilename or attachment.shortFilename or '')
                if not ext:
                    ext = '.jpeg'
                if len(attachments) > 1:
                    out_filename = name_pattern.format(num=number, idx=idx)
                else:
                    out_filename = name_pattern.format(num=number, idx=idx)
                out_path = os.path.join(output_folder, out_filename)
                with open(out_path, 'wb') as f:
                    f.write(attachment.data)
                processed += 1
        except Exception as e:
            errors.append((file_name, str(e)))

    return processed, errors


class ExtractWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title('Bilder aus E-Mail extrahieren (.msg)')
        self.geometry('700x320')
        self.minsize(600, 280)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.pattern_var = tk.StringVar(value='fotofallen_2025_{num}_{idx}.jpeg')
        
        # Dialog protection
        self._dialog_open = False
        
        # Create folder icon
        try:
            self.folder_icon = self._create_folder_icon(20, 20)
        except Exception:
            self.folder_icon = None

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='Eingabe .msg-Ordner:').grid(row=0, column=0, sticky='w')
        input_entry = ttk.Entry(frame, textvariable=self.input_var, state='readonly')
        input_entry.grid(row=0, column=1, sticky='ew', padx=(5, 10))
        if self.folder_icon:
            ttk.Button(frame, image=self.folder_icon, command=self.browse_input).grid(row=0, column=2, padx=6)
        else:
            ttk.Button(frame, text='Durchsuchen', command=self.browse_input).grid(row=0, column=2, padx=6)

        ttk.Label(frame, text='Ausgabe-Bilder-Ordner:').grid(row=1, column=0, sticky='w')
        output_entry = ttk.Entry(frame, textvariable=self.output_var, state='readonly')
        output_entry.grid(row=1, column=1, sticky='ew', padx=(5, 10))
        if self.folder_icon:
            ttk.Button(frame, image=self.folder_icon, command=self.browse_output).grid(row=1, column=2, padx=6)
        else:
            ttk.Button(frame, text='Durchsuchen', command=self.browse_output).grid(row=1, column=2, padx=6)

        ttk.Label(frame, text='Dateiname-Muster:').grid(row=2, column=0, sticky='w')
        ttk.Entry(frame, textvariable=self.pattern_var).grid(row=2, column=1, sticky='ew', padx=(5, 10))
        ttk.Label(frame, text='Verwende {num} und {idx} Platzhalter').grid(row=2, column=2, sticky='w')

        # Configure column weights for expansion
        frame.columnconfigure(1, weight=1)

        self.log = tk.Text(frame, height=10, width=90)
        self.log.grid(row=4, column=0, columnspan=3, pady=(10,0), sticky='nsew')

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=8)
        ttk.Button(btn_frame, text='Extraktion ausführen', command=self.run_extraction).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text='Schließen', command=self.destroy).pack(side=tk.LEFT, padx=6)

        # Configure grid weights
        frame.rowconfigure(4, weight=1)

    def _create_folder_icon(self, w=20, h=20):
        """Create a simple folder icon for button use."""
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # folder base
        draw.rectangle([1, 6, w - 1, h - 2], fill=(220, 180, 60), outline=(140, 100, 30))
        # tab
        draw.rectangle([1, 3, w // 2, 8], fill=(240, 200, 80), outline=(140, 100, 30))
        return ImageTk.PhotoImage(img)

    def _bring_window_to_front(self):
        """Bring this dialog to the front."""
        try:
            self.lift()
            self.attributes('-topmost', True)
            self.update()
        except Exception:
            pass

    def browse_input(self):
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            self._bring_window_to_front()
            path = filedialog.askdirectory(parent=self, title="Ordner mit .msg-Dateien auswählen")
        finally:
            try:
                self.attributes('-topmost', False)
                self.focus_force()
            except Exception:
                pass
            self._dialog_open = False
        if path:
            self.input_var.set(path)

    def browse_output(self):
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            self._bring_window_to_front()
            path = filedialog.askdirectory(parent=self, title="Ausgabeordner für extrahierte Bilder auswählen")
        finally:
            try:
                self.attributes('-topmost', False)
                self.focus_force()
            except Exception:
                pass
            self._dialog_open = False
        if path:
            self.output_var.set(path)

    def run_extraction(self):
        input_folder = self.input_var.get().strip()
        output_folder = self.output_var.get().strip()
        pattern = self.pattern_var.get().strip()

        if not input_folder or not os.path.isdir(input_folder):
            messagebox.showerror('Fehler', 'Bitte wählen Sie einen gültigen Eingabeordner aus', parent=self)
            return
        if not output_folder:
            messagebox.showerror('Fehler', 'Bitte wählen Sie einen Ausgabeordner aus', parent=self)
            return

        self.log.insert(tk.END, f'Extrahiere aus: {input_folder}\n')
        self.log.insert(tk.END, f'Schreibe in: {output_folder}\n')
        self.update()

        try:
            processed, errors = extract_msg_files(input_folder, output_folder, name_pattern=pattern)
            self.log.insert(tk.END, f'Verarbeitet: {processed} Anhänge\n')
            if errors:
                self.log.insert(tk.END, f'Fehler: {len(errors)}\n')
                for fn, err in errors[:10]:
                    self.log.insert(tk.END, f' - {fn}: {err}\n')
            else:
                self.log.insert(tk.END, 'Keine Extraktionsfehler.\n')
        except Exception as e:
            self.log.insert(tk.END, f'Fehlgeschlagen: {e}\n')
            messagebox.showerror('Fehler', str(e), parent=self)


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Kamerafallen-Tools Starter')
        self.geometry('520x240')

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='Kamerafallen-Tools', font=('Arial', 16, 'bold')).pack(pady=(0,10))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text='Öffnen: Bilder aus E-Mail extrahieren', width=36, command=self.open_extract).grid(row=0, column=0, pady=6)
        ttk.Button(btn_frame, text='Öffnen: GitHub Models Analyzer', width=36, command=self.open_analyzer).grid(row=1, column=0, pady=6)
        ttk.Button(btn_frame, text='Ausführen: Bilder aus Excel umbenennen', width=36, command=self.run_renamer_dialog).grid(row=2, column=0, pady=6)

        info = ttk.Label(frame, text='Analyzer startet als separater Prozess. Renamer läuft mit gewählten Excel/Bilder-Pfaden.')
        info.pack(pady=(10,0))

    def open_extract(self):
        ExtractWindow(self)

    def open_analyzer(self):
        # Handle both packaged and development environments
        if hasattr(sys, '_MEIPASS'):
            # Running from PyInstaller bundle
            analyzer_script = os.path.join(sys._MEIPASS, 'github_models_analyzer.py')
        else:
            # Running from source
            analyzer_script = os.path.join(os.path.dirname(__file__), 'github_models_analyzer.py')
        
        if not os.path.exists(analyzer_script):
            messagebox.showerror('Fehler', f'Analyzer-Skript nicht gefunden: {analyzer_script}', parent=self)
            return

        dlg = tk.Toplevel(self)
        dlg.title('Analyzer starten - Optionen')
        dlg.geometry('620x220')
        dlg.minsize(500, 180)

        # Try to load .env and get current token
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        current_token = os.environ.get("GITHUB_MODELS_TOKEN", "")
        current_images = os.environ.get("ANALYZER_IMAGES_FOLDER", "")
        current_excel = os.environ.get("ANALYZER_OUTPUT_EXCEL", "")

        token_var = tk.StringVar(value=current_token)
        images_var = tk.StringVar(value=current_images)
        out_var = tk.StringVar(value=current_excel)

        # Dialog protection
        dlg._dialog_open = False

        def bring_dlg_to_front():
            try:
                dlg.lift()
                dlg.attributes('-topmost', True)
                dlg.update()
            except Exception:
                pass

        def browse_images():
            if dlg._dialog_open:
                return
            dlg._dialog_open = True
            try:
                bring_dlg_to_front()
                path = filedialog.askdirectory(parent=dlg, title="Bilder-Ordner auswählen")
            finally:
                try:
                    dlg.attributes('-topmost', False)
                    dlg.focus_force()
                except Exception:
                    pass
                dlg._dialog_open = False
            if path:
                images_var.set(path)

        def browse_excel():
            if dlg._dialog_open:
                return
            dlg._dialog_open = True
            try:
                bring_dlg_to_front()
                path = filedialog.asksaveasfilename(parent=dlg, title="Ausgabe-Excel-Datei auswählen",
                                                    defaultextension='.xlsx', 
                                                    filetypes=[('Excel','*.xlsx')])
            finally:
                try:
                    dlg.attributes('-topmost', False)
                    dlg.focus_force()
                except Exception:
                    pass
                dlg._dialog_open = False
            if path:
                out_var.set(path)

        frm = ttk.Frame(dlg, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)
        
        # Token row with show/hide functionality
        token_frame = ttk.Frame(frm)
        token_frame.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0, 5))
        token_frame.columnconfigure(1, weight=1)
        
        ttk.Label(token_frame, text='GitHub Models Token (automatisch aus env geladen):').grid(row=0, column=0, sticky='w')
        
        show_token_var = tk.BooleanVar()
        token_entry = ttk.Entry(token_frame, textvariable=token_var)
        token_entry.grid(row=0, column=1, sticky='ew', padx=(5, 10))
        
        def toggle_token_visibility():
            if show_token_var.get():
                token_entry.config(show='')
            else:
                token_entry.config(show='*')
        
        # Set initial state - hide token if it exists
        if current_token:
            token_entry.config(show='*')
            # Add status label
            status_text = f"✓ Token aus Umgebung geladen ({len(current_token)} Zeichen)"
            ttk.Label(token_frame, text=status_text, foreground='green', font=('Arial', 8)).grid(row=1, column=1, sticky='w', padx=(5, 0))
        else:
            show_token_var.set(True)  # Show empty field by default
            ttk.Label(token_frame, text="⚠ Kein Token in Umgebung gefunden", foreground='orange', font=('Arial', 8)).grid(row=1, column=1, sticky='w', padx=(5, 0))
            
        ttk.Checkbutton(token_frame, text='Anzeigen', variable=show_token_var, 
                       command=toggle_token_visibility).grid(row=0, column=2, padx=6)
        
        ttk.Label(frm, text='Bilder-Ordner (automatisch aus env geladen):').grid(row=1, column=0, sticky='w')
        images_entry = ttk.Entry(frm, textvariable=images_var, state='readonly')
        images_entry.grid(row=1, column=1, sticky='ew', padx=(5, 10))
        ttk.Button(frm, text='Durchsuchen', command=browse_images).grid(row=1, column=2, padx=6)
        
        ttk.Label(frm, text='Ausgabe-Excel (automatisch aus env geladen):').grid(row=2, column=0, sticky='w')
        excel_entry = ttk.Entry(frm, textvariable=out_var, state='readonly')
        excel_entry.grid(row=2, column=1, sticky='ew', padx=(5, 10))
        ttk.Button(frm, text='Durchsuchen', command=browse_excel).grid(row=2, column=2, padx=6)

        # Configure column weights
        frm.columnconfigure(1, weight=1)

        def launch():
            env = os.environ.copy()
            if token_var.get().strip():
                env['GITHUB_MODELS_TOKEN'] = token_var.get().strip()
            if images_var.get().strip():
                env['ANALYZER_IMAGES_FOLDER'] = images_var.get().strip()
            if out_var.get().strip():
                env['ANALYZER_OUTPUT_EXCEL'] = out_var.get().strip()

            # Launch analyzer - handle both packaged and development environments
            if hasattr(sys, '_MEIPASS'):
                # In packaged executable, import and run directly with parameters
                try:
                    # Import and run analyzer with selected folders
                    import github_models_analyzer
                    images_folder = images_var.get().strip() or None
                    excel_output = out_var.get().strip() or None
                    
                    # Set token in environment if provided
                    if token_var.get().strip():
                        os.environ['GITHUB_MODELS_TOKEN'] = token_var.get().strip()
                    
                    # Close this dialog first to avoid conflicts
                    dlg.destroy()
                    
                    # Start analyzer with debugging
                    print("🚀 Starting analyzer with:")
                    print(f"   Images folder: {images_folder}")
                    print(f"   Excel output: {excel_output}")
                    
                    # Schedule analyzer start in main thread after dialog closes
                    def start_analyzer_delayed():
                        try:
                            print("📱 Creating analyzer instance...")
                            github_models_analyzer.start_analyzer(
                                images_folder=images_folder, 
                                output_excel=excel_output
                            )
                            print("✅ Analyzer started successfully")
                        except Exception as e:
                            print(f"❌ Error starting analyzer: {e}")
                            import traceback
                            traceback.print_exc()
                            messagebox.showerror('Fehler', f'Fehler beim Starten des Analyzers: {e}')
                    
                    # Give main thread time to process dialog closure, then start analyzer
                    self.after(200, start_analyzer_delayed)
                except Exception as e:
                    messagebox.showerror('Fehler', f'Fehler beim Starten des Analyzers: {e}', parent=dlg)
            else:
                # In development, use subprocess as before
                subprocess.Popen([sys.executable, analyzer_script], cwd=os.path.dirname(__file__), env=env)
                messagebox.showinfo('Gestartet', 'Analyzer in separatem Prozess gestartet', parent=dlg)
            
            dlg.destroy()

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=3, pady=12)
        ttk.Button(btns, text='Analyzer starten', command=launch).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text='Abbrechen', command=dlg.destroy).pack(side=tk.LEFT, padx=6)

    def run_renamer_dialog(self):
        # Create comprehensive renamer dialog
        dlg = tk.Toplevel(self)
        dlg.title('Bilder umbenennen - Konfiguration')
        dlg.geometry('650x400')
        dlg.minsize(600, 350)
        
        # Variables for the form
        excel_var = tk.StringVar()
        images_var = tk.StringVar() 
        pattern_var = tk.StringVar(value='fotofallen_2025_{num}.jpeg')  # Default pattern
        mode_var = tk.StringVar(value='actual')  # 'preview' or 'actual'
        
        # Dialog protection
        dlg._dialog_open = False
        
        def bring_dlg_to_front():
            try:
                dlg.lift()
                dlg.attributes('-topmost', True)
                dlg.update()
            except Exception:
                pass
                
        def browse_excel():
            if dlg._dialog_open:
                return
            dlg._dialog_open = True
            try:
                bring_dlg_to_front()
                path = filedialog.askopenfilename(parent=dlg, title='Excel-Datei auswählen (Fotofallendaten)', 
                                                filetypes=[('Excel-Dateien', '*.xlsx *.xls')])
            finally:
                try:
                    dlg.attributes('-topmost', False)
                    dlg.focus_force()
                except Exception:
                    pass
                dlg._dialog_open = False
            if path:
                excel_var.set(path)
                
        def browse_images():
            if dlg._dialog_open:
                return
            dlg._dialog_open = True
            try:
                bring_dlg_to_front()
                path = filedialog.askdirectory(parent=dlg, title='Ordner mit Bildern auswählen')
            finally:
                try:
                    dlg.attributes('-topmost', False)
                    dlg.focus_force()
                except Exception:
                    pass
                dlg._dialog_open = False
            if path:
                images_var.set(path)
        
        # Main frame
        main_frame = ttk.Frame(dlg, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text='Bilder aus Excel-Daten umbenennen', font=('Arial', 12, 'bold')).pack(pady=(0, 15))
        
        # Excel file selection
        excel_frame = ttk.Frame(main_frame)
        excel_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(excel_frame, text='Excel-Datei (Fotofallendaten):').pack(anchor=tk.W)
        excel_entry_frame = ttk.Frame(excel_frame)
        excel_entry_frame.pack(fill=tk.X, pady=(2, 0))
        excel_entry = ttk.Entry(excel_entry_frame, textvariable=excel_var, state='readonly')
        excel_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(excel_entry_frame, text='Durchsuchen', command=browse_excel).pack(side=tk.RIGHT)
        
        # Images folder selection  
        images_frame = ttk.Frame(main_frame)
        images_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(images_frame, text='Bilder-Ordner:').pack(anchor=tk.W)
        images_entry_frame = ttk.Frame(images_frame)
        images_entry_frame.pack(fill=tk.X, pady=(2, 0))
        images_entry = ttk.Entry(images_entry_frame, textvariable=images_var, state='readonly')
        images_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(images_entry_frame, text='Durchsuchen', command=browse_images).pack(side=tk.RIGHT)
        
        # Image name pattern
        pattern_frame = ttk.Frame(main_frame)
        pattern_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(pattern_frame, text='Bild-Namensmuster (verwende {num} für Nummerierung):').pack(anchor=tk.W)
        pattern_entry = ttk.Entry(pattern_frame, textvariable=pattern_var)
        pattern_entry.pack(fill=tk.X, pady=(2, 0))
        
        # Help text for pattern
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill=tk.X, pady=(0, 15))
        help_text = ttk.Label(help_frame, text='Beispiele: fotofallen_2025_{num}.jpeg, IMG_{num}.jpg, kamerafalle_{num}.png', 
                             font=('Arial', 8), foreground='gray')
        help_text.pack(anchor=tk.W)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text='Ausführungsart', padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Radiobutton(mode_frame, text='Vorschau anzeigen (keine Dateien ändern)', 
                       variable=mode_var, value='preview').pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(mode_frame, text='Dateien tatsächlich umbenennen', 
                       variable=mode_var, value='actual').pack(anchor=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def run_rename():
            excel_path = excel_var.get().strip()
            images_path = images_var.get().strip()
            pattern = pattern_var.get().strip()
            
            if not excel_path:
                messagebox.showerror('Fehler', 'Bitte wählen Sie eine Excel-Datei aus.', parent=dlg)
                return
            if not images_path:
                messagebox.showerror('Fehler', 'Bitte wählen Sie einen Bilder-Ordner aus.', parent=dlg)
                return
            if not pattern or '{num}' not in pattern:
                messagebox.showerror('Fehler', 'Bitte geben Sie ein gültiges Namensmuster mit {num} ein.', parent=dlg)
                return
                
            is_preview = mode_var.get() == 'preview'
            mode_text = 'Vorschau' if is_preview else 'Umbenennung'
            
            confirm_msg = f'{mode_text} starten mit:\n\nExcel: {excel_path}\nBilder: {images_path}\nMuster: {pattern}'
            if not is_preview:
                confirm_msg += '\n\n⚠️ ACHTUNG: Dateien werden tatsächlich umbenannt!'
                
            if not messagebox.askyesno(f'{mode_text} bestätigen', confirm_msg, parent=dlg):
                return
                
            dlg.destroy()
            
            try:
                self.run_renamer_with_paths(excel_path, images_path, pattern, is_preview)
            except Exception as e:
                messagebox.showerror('Fehler', str(e), parent=self)
        
        ttk.Button(button_frame, text='Ausführen', command=run_rename).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text='Abbrechen', command=dlg.destroy).pack(side=tk.RIGHT)
        
        # Set focus to Excel browse button
        dlg.focus_set()

    def run_renamer_with_paths(self, excel_path, images_folder, pattern, is_preview):
        # Read original renamer script
        renamer_src = os.path.join(os.path.dirname(__file__), 'rename_images_from_excel.py')
        if not os.path.exists(renamer_src):
            raise FileNotFoundError('rename_images_from_excel.py nicht im Repository gefunden')

        with open(renamer_src, 'r', encoding='utf-8') as f:
            src = f.read()

        # Replace the constants EXCEL_PATH, IMAGES_FOLDER, and image pattern if present
        src_mod = re.sub(r'EXCEL_PATH\s*=\s*.*', f'EXCEL_PATH = r"{excel_path}"', src)
        src_mod = re.sub(r'IMAGES_FOLDER\s*=\s*.*', f'IMAGES_FOLDER = r"{images_folder}"', src_mod)
        
        # Try to replace image pattern if the script has this feature
        # Look for patterns like NEW_NAME_PATTERN = '...' or similar
        pattern_patterns = [
            r'NEW_NAME_PATTERN\s*=\s*.*',
            r'IMAGE_NAME_PATTERN\s*=\s*.*',
            r'FILENAME_PATTERN\s*=\s*.*'
        ]
        
        pattern_replaced = False
        for p in pattern_patterns:
            if re.search(p, src_mod):
                src_mod = re.sub(p, f'NEW_NAME_PATTERN = r"{pattern}"', src_mod)
                pattern_replaced = True
                break
        
        # If no pattern variable found, add it at the top after imports
        if not pattern_replaced:
            # Find where to insert the pattern variable
            import_lines = []
            other_lines = []
            in_imports = True
            
            for line in src_mod.split('\n'):
                if in_imports and (line.strip().startswith('import ') or line.strip().startswith('from ') or line.strip() == '' or line.strip().startswith('#')):
                    import_lines.append(line)
                else:
                    in_imports = False
                    other_lines.append(line)
            
            # Add pattern variable after imports
            import_lines.append('')
            import_lines.append('# Custom image naming pattern from GUI')
            import_lines.append(f'NEW_NAME_PATTERN = r"{pattern}"')
            import_lines.append('')
            
            src_mod = '\n'.join(import_lines + other_lines)

        # Write to a temp file and execute it
        fd, tmp_path = tempfile.mkstemp(prefix='renamer_tmp_', suffix='.py')
        os.close(fd)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(src_mod)

        # Run in a thread to avoid blocking the GUI
        def runner():
            try:
                cmd = [sys.executable, tmp_path]
                if is_preview:
                    cmd.append('--dry-run')
                proc = subprocess.run(cmd, cwd=os.path.dirname(__file__), capture_output=True, text=True)
                output = proc.stdout + '\n' + proc.stderr
                
                # Create a nice output window
                out_win = tk.Toplevel(self)
                out_win.title('Bilder umbenennen - Ergebnis')
                out_win.geometry('900x600')
                
                # Add a frame for better layout
                main_frame = ttk.Frame(out_win, padding=10)
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # Title
                mode_text = 'Vorschau' if is_preview else 'Umbenennung'
                ttk.Label(main_frame, text=f'{mode_text} - Ergebnis', font=('Arial', 12, 'bold')).pack(pady=(0, 10))
                
                # Info
                info_text = f'Excel: {excel_path}\nBilder: {images_folder}\nMuster: {pattern}'
                ttk.Label(main_frame, text=info_text, font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 10))
                
                # Scrollable text area
                text_frame = ttk.Frame(main_frame)
                text_frame.pack(fill=tk.BOTH, expand=True)
                
                txt = tk.Text(text_frame, font=('Consolas', 9), wrap=tk.WORD)
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=txt.yview)
                txt.configure(yscrollcommand=scrollbar.set)
                
                txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                txt.insert('1.0', output)
                txt.config(state='disabled')
                
                # Close button
                ttk.Button(main_frame, text='Schließen', command=out_win.destroy).pack(pady=(10, 0))
                
            except Exception as e:
                messagebox.showerror('Fehler beim Ausführen', f'Fehler beim Ausführen des Renamer-Skripts:\n{str(e)}', parent=self)
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        threading.Thread(target=runner, daemon=True).start()


def main():
    app = Launcher()
    app.mainloop()


if __name__ == '__main__':
    main()
