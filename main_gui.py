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


def extract_msg_files(input_folder, output_folder, name_pattern="fotofallen_2025_{num}.jpeg"):
    """Extract attachments from .msg files in input_folder into output_folder.

    name_pattern may include {num} and optional {idx} for multi-attachment messages.
    """
    try:
        import extract_msg
    except Exception:
        raise RuntimeError("Missing dependency 'extract_msg'. Install with: pip install extract_msg")

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
        self.title('Extract images from email (.msg)')
        self.geometry('700x320')

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.pattern_var = tk.StringVar(value='fotofallen_2025_{num}_{idx}.jpeg')

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='Input .msg folder:').grid(row=0, column=0, sticky='w')
        ttk.Entry(frame, textvariable=self.input_var, width=60).grid(row=0, column=1, sticky='w')
        ttk.Button(frame, text='Browse', command=self.browse_input).grid(row=0, column=2, padx=6)

        ttk.Label(frame, text='Output images folder:').grid(row=1, column=0, sticky='w')
        ttk.Entry(frame, textvariable=self.output_var, width=60).grid(row=1, column=1, sticky='w')
        ttk.Button(frame, text='Browse', command=self.browse_output).grid(row=1, column=2, padx=6)

        ttk.Label(frame, text='Filename pattern:').grid(row=2, column=0, sticky='w')
        ttk.Entry(frame, textvariable=self.pattern_var, width=60).grid(row=2, column=1, sticky='w')
        ttk.Label(frame, text='Use {num} and {idx} placeholders').grid(row=2, column=2, sticky='w')

        self.log = tk.Text(frame, height=10, width=90)
        self.log.grid(row=4, column=0, columnspan=3, pady=(10,0))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=8)
        ttk.Button(btn_frame, text='Run Extraction', command=self.run_extraction).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text='Close', command=self.destroy).pack(side=tk.LEFT, padx=6)

    def browse_input(self):
        path = filedialog.askdirectory()
        if path:
            self.input_var.set(path)

    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_var.set(path)

    def run_extraction(self):
        input_folder = self.input_var.get().strip()
        output_folder = self.output_var.get().strip()
        pattern = self.pattern_var.get().strip()

        if not input_folder or not os.path.isdir(input_folder):
            messagebox.showerror('Error', 'Please select a valid input folder')
            return
        if not output_folder:
            messagebox.showerror('Error', 'Please select an output folder')
            return

        self.log.insert(tk.END, f'Extracting from: {input_folder}\n')
        self.log.insert(tk.END, f'Writing to: {output_folder}\n')
        self.update()

        try:
            processed, errors = extract_msg_files(input_folder, output_folder, name_pattern=pattern)
            self.log.insert(tk.END, f'Processed: {processed} attachments\n')
            if errors:
                self.log.insert(tk.END, f'Errors: {len(errors)}\n')
                for fn, err in errors[:10]:
                    self.log.insert(tk.END, f' - {fn}: {err}\n')
            else:
                self.log.insert(tk.END, 'No extraction errors.\n')
        except Exception as e:
            self.log.insert(tk.END, f'Failed: {e}\n')
            messagebox.showerror('Error', str(e))


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Camera Trap Tools Launcher')
        self.geometry('520x240')

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='Camera Trap Tools', font=('Arial', 16, 'bold')).pack(pady=(0,10))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text='Open: Extract images from email', width=36, command=self.open_extract).grid(row=0, column=0, pady=6)
        ttk.Button(btn_frame, text='Open: GitHub Models Analyzer', width=36, command=self.open_analyzer).grid(row=1, column=0, pady=6)
        ttk.Button(btn_frame, text='Run: Rename images from Excel', width=36, command=self.run_renamer_dialog).grid(row=2, column=0, pady=6)

        info = ttk.Label(frame, text='Analyzer launches as a separate process. Renamer will run with chosen Excel/images paths.')
        info.pack(pady=(10,0))

    def open_extract(self):
        ExtractWindow(self)

    def open_analyzer(self):
        # Show a small dialog to collect optional token and paths, then launch analyzer with env
        analyzer_script = os.path.join(os.path.dirname(__file__), 'github_models_analyzer_current_broken.py')
        if not os.path.exists(analyzer_script):
            messagebox.showerror('Error', f'Analyzer script not found: {analyzer_script}')
            return

        dlg = tk.Toplevel(self)
        dlg.title('Launch Analyzer - Options')
        dlg.geometry('620x220')

        token_var = tk.StringVar()
        images_var = tk.StringVar(value='')
        out_var = tk.StringVar(value='')

        frm = ttk.Frame(dlg, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text='GitHub Models Token (optional - will set GITHUB_MODELS_TOKEN):').grid(row=0, column=0, sticky='w')
        ttk.Entry(frm, textvariable=token_var, width=60, show='*').grid(row=0, column=1, sticky='w')
        ttk.Label(frm, text='Images folder (optional - will set ANALYZER_IMAGES_FOLDER):').grid(row=1, column=0, sticky='w')
        ttk.Entry(frm, textvariable=images_var, width=60).grid(row=1, column=1, sticky='w')
        ttk.Button(frm, text='Browse', command=lambda: images_var.set(filedialog.askdirectory())).grid(row=1, column=2, padx=6)
        ttk.Label(frm, text='Output Excel (optional - will set ANALYZER_OUTPUT_EXCEL):').grid(row=2, column=0, sticky='w')
        ttk.Entry(frm, textvariable=out_var, width=60).grid(row=2, column=1, sticky='w')
        ttk.Button(frm, text='Browse', command=lambda: out_var.set(filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel','*.xlsx')]))).grid(row=2, column=2, padx=6)

        def launch():
            env = os.environ.copy()
            if token_var.get().strip():
                env['GITHUB_MODELS_TOKEN'] = token_var.get().strip()
            if images_var.get().strip():
                env['ANALYZER_IMAGES_FOLDER'] = images_var.get().strip()
            if out_var.get().strip():
                env['ANALYZER_OUTPUT_EXCEL'] = out_var.get().strip()

            subprocess.Popen([sys.executable, analyzer_script], cwd=os.path.dirname(__file__), env=env)
            messagebox.showinfo('Launched', 'Analyzer launched in a separate process')
            dlg.destroy()

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=3, pady=12)
        ttk.Button(btns, text='Launch Analyzer', command=launch).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text='Cancel', command=dlg.destroy).pack(side=tk.LEFT, padx=6)

    def run_renamer_dialog(self):
        excel_path = filedialog.askopenfilename(title='Select Excel file (Fotofallendaten)', filetypes=[('Excel files', '*.xlsx *.xls')])
        if not excel_path:
            return
        images_folder = filedialog.askdirectory(title='Select folder with extracted images')
        if not images_folder:
            return

        confirm = messagebox.askyesno('Run Renamer', f'Run renamer with:\nExcel: {excel_path}\nImages: {images_folder}\n\nThis will execute a temporary copy of the renamer script with these paths.')
        if not confirm:
            return

        try:
            self.run_renamer_with_paths(excel_path, images_folder)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def run_renamer_with_paths(self, excel_path, images_folder):
        # Read original renamer script
        renamer_src = os.path.join(os.path.dirname(__file__), 'rename_images_from_excel.py')
        if not os.path.exists(renamer_src):
            raise FileNotFoundError('rename_images_from_excel.py not found in repo')

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
        dry = messagebox.askyesno('Dry run', 'Run a dry-run (no files will be renamed)?')

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
                out_win.title('Renamer output')
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
