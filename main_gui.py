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
                # In packaged executable, import and run directly
                try:
                    # Set environment variables before importing
                    for key, value in env.items():
                        os.environ[key] = value
                    
                    # Import and run analyzer directly
                    import github_models_analyzer
                    analyzer = github_models_analyzer.ImageAnalyzer()
                    threading.Thread(target=analyzer.run, daemon=True).start()
                    messagebox.showinfo('Gestartet', 'Analyzer wurde gestartet', parent=dlg)
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
        excel_path = filedialog.askopenfilename(parent=self, title='Excel-Datei auswählen (Fotofallendaten)', filetypes=[('Excel-Dateien', '*.xlsx *.xls')])
        if not excel_path:
            return
        images_folder = filedialog.askdirectory(parent=self, title='Ordner mit extrahierten Bildern auswählen')
        if not images_folder:
            return

        confirm = messagebox.askyesno('Renamer ausführen', f'Renamer ausführen mit:\nExcel: {excel_path}\nBilder: {images_folder}\n\nDies führt eine temporäre Kopie des Renamer-Skripts mit diesen Pfaden aus.', parent=self)
        if not confirm:
            return

        try:
            self.run_renamer_with_paths(excel_path, images_folder)
        except Exception as e:
            messagebox.showerror('Fehler', str(e), parent=self)

    def run_renamer_with_paths(self, excel_path, images_folder):
        # Read original renamer script
        renamer_src = os.path.join(os.path.dirname(__file__), 'rename_images_from_excel.py')
        if not os.path.exists(renamer_src):
            raise FileNotFoundError('rename_images_from_excel.py nicht im Repository gefunden')

        with open(renamer_src, 'r', encoding='utf-8') as f:
            src = f.read()

        # Replace the constants EXCEL_PATH and IMAGES_FOLDER if present
        src_mod = re.sub(r'EXCEL_PATH\s*=\s*.*', f'EXCEL_PATH = r"{excel_path}"', src)
        src_mod = re.sub(r'IMAGES_FOLDER\s*=\s*.*', f'IMAGES_FOLDER = r"{images_folder}"', src_mod)

        # Write to a temp file and execute it
        fd, tmp_path = tempfile.mkstemp(prefix='renamer_tmp_', suffix='.py')
        os.close(fd)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(src_mod)

        # Ask whether dry-run
        dry = messagebox.askyesno('Probelauf', 'Probelauf ausführen (keine Dateien werden umbenannt)?', parent=self)

        # Run in a thread to avoid blocking the GUI
        def runner():
            try:
                cmd = [sys.executable, tmp_path]
                if dry:
                    cmd.append('--dry-run')
                proc = subprocess.run(cmd, cwd=os.path.dirname(__file__), capture_output=True, text=True)
                output = proc.stdout + '\n' + proc.stderr
                # Show a simple dialog with the result (could be long)
                out_win = tk.Toplevel(self)
                out_win.title('Renamer-Ausgabe')
                txt = tk.Text(out_win, width=100, height=30)
                txt.pack(fill=tk.BOTH, expand=True)
                txt.insert('1.0', output)
                txt.config(state='disabled')
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
