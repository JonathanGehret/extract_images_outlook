#!/usr/bin/env python3
"""
Kamerafallen Bild-Analyzer mit GitHub Models API
================================================

Ein GUI-Tool zur Analyse von Kamerafallen-Bildern mit KI-Unterstützung.
Analysiert Bilder automatisch und speichert Ergebnisse in Excel-Dateien.

Dieses File ist die bereinigte, modulare Version und delegiert API- und I/O-Aufgaben
an `github_models_api` und `github_models_io`.

Autor: GitHub Copilot
Datum: 2025
"""

import os
import sys
import argparse
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import github_models_api as gm_api
import github_models_io as gm_io

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, continue without it

# Configuration (can be overridden by env)
IMAGES_FOLDER = os.environ.get("ANALYZER_IMAGES_FOLDER", "")
OUTPUT_EXCEL = os.environ.get("ANALYZER_OUTPUT_EXCEL", "")
GITHUB_TOKEN = os.environ.get("GITHUB_MODELS_TOKEN", "")
START_FROM_IMAGE = 1

ANIMAL_SPECIES = [
    "Bartgeier", "Steinadler", "Kolkabe",
    "Alpendohle", "Fuchs", "Gams", "Steinbock", 
    "Murmeltier", "Marder", "Reh", "Hirsch", "Rabenkrähe",
    "Mensch"
]


class AnalysisBuffer:
    """Manages asynchronous analysis with rolling buffer for smooth user experience."""
    
    def __init__(self, analyzer_instance):
        self.analyzer = analyzer_instance
        self.buffer = {}  # {image_index: analysis_result}
        self.analyzing = set()  # Currently being analyzed
        self.failed = set()  # Failed analyses
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.buffer_size = 3  # Keep 3 images ahead analyzed
        
    def get_analysis(self, image_index, force_analysis=False):
        """Get analysis result for image, trigger batch if not available.
        
        Args:
            image_index: Index of image to analyze
            force_analysis: If True, forces analysis even if not explicitly requested
        """
        print(f"DEBUG: Getting analysis for image {image_index}, force_analysis={force_analysis}")
        print(f"DEBUG: Buffer state - buffered: {len(self.buffer)}, analyzing: {len(self.analyzing)}, failed: {len(self.failed)}")
        
        if image_index in self.buffer:
            result = self.buffer.pop(image_index)
            print(f"DEBUG: Found result in buffer for image {image_index}: {result.get('animals', 'N/A')}")
            # Trigger next batch analysis only if force_analysis is True (from analyze button)
            if force_analysis:
                self._ensure_buffer_ahead(image_index + 1)
            return result
        elif image_index in self.analyzing:
            print(f"DEBUG: Image {image_index} is currently being analyzed")
            return "analyzing"
        elif image_index in self.failed:
            print(f"DEBUG: Image {image_index} analysis failed previously")
            return "failed"
        else:
            # Only start analysis if explicitly requested (from analyze button)
            if force_analysis:
                print(f"DEBUG: Starting batch analysis from image {image_index}")
                self._start_batch_analysis(image_index)
                return "analyzing"
            else:
                print(f"DEBUG: Analysis not started for image {image_index} (not forced)")
                return "not_analyzed"
    
    def _ensure_buffer_ahead(self, current_index):
        """Ensure we have buffer_size images analyzed ahead."""
        for i in range(current_index, min(current_index + self.buffer_size, len(self.analyzer.image_files))):
            if (i not in self.buffer and 
                i not in self.analyzing and 
                i not in self.failed):
                self._start_single_analysis(i)
    
    def _start_batch_analysis(self, start_index):
        """Start analyzing a batch of up to 5 images."""
        batch_size = min(5, len(self.analyzer.image_files) - start_index)
        for i in range(start_index, start_index + batch_size):
            if i not in self.buffer and i not in self.analyzing:
                self._start_single_analysis(i)
    
    def _start_single_analysis(self, image_index):
        """Start analyzing a single image asynchronously."""
        if image_index >= len(self.analyzer.image_files):
            return
            
        self.analyzing.add(image_index)
        future = self.executor.submit(self._analyze_image, image_index)
        future.add_done_callback(lambda f: self._analysis_complete(image_index, f))
    
    def _analyze_image(self, image_index):
        """Perform the actual image analysis."""
        try:
            # Get the image file path
            image_file = self.analyzer.image_files[image_index]
            images_folder = self.analyzer.images_folder or IMAGES_FOLDER
            image_path = os.path.join(images_folder, image_file)
            
            # Check if token is available
            if not GITHUB_TOKEN:
                return {
                    'animals': 'Token fehlt',
                    'location': 'Unbekannt',
                    'date': '',
                    'time': '',
                    'error': 'GITHUB_MODELS_TOKEN nicht gesetzt'
                }
            
            # Use existing AI analysis function
            animals, location, time_str, date_str = gm_api.analyze_with_github_models(
                image_path, GITHUB_TOKEN, ANIMAL_SPECIES
            )
            
            return {
                'animals': animals or 'Keine Tiere erkannt',
                'location': location or 'Unbekannt',
                'date': date_str or '',
                'time': time_str or '',
                'error': None
            }
                
        except Exception as e:
            print(f"Analysis error for image {image_index}: {e}")
            return {
                'animals': 'Fehler bei Analyse',
                'location': 'Unbekannt',
                'date': '',
                'time': '',
                'error': str(e)
            }
    
    def _analysis_complete(self, image_index, future):
        """Handle completion of image analysis."""
        self.analyzing.discard(image_index)
        
        try:
            result = future.result()
            if result.get('error'):
                self.failed.add(image_index)
                print(f"Analysis failed for image {image_index}: {result['error']}")
            else:
                self.buffer[image_index] = result
                print(f"✓ Analysis complete for image {image_index}: {result['animals']}")
                
                # Update UI if this is the current image
                if image_index == self.analyzer.current_image_index:
                    self.analyzer.root.after(0, lambda r=result: self._update_current_image_ui(r))
                    
                # Update buffer status
                self.analyzer.root.after(0, self._update_buffer_status)
                    
        except Exception as e:
            self.failed.add(image_index)
            print(f"Exception in analysis for image {image_index}: {e}")
    
    def _update_current_image_ui(self, result):
        """Update UI with analysis result if it's for current image."""
        try:
            # Parse animals to species and populate fields
            self.analyzer.parse_animals_to_species(result['animals'])
            
            # Update location and other fields
            self.analyzer.location_var.set(result['location'])
            if result['date']:
                self.analyzer.date_var.set(result['date'])
            if result['time']:
                self.analyzer.time_var.set(result['time'])
            
            # Update status
            if hasattr(self.analyzer, 'analysis_status_label'):
                self.analyzer.analysis_status_label.config(text="✓ Analyse abgeschlossen", foreground="green")
        except Exception as e:
            print(f"Error updating UI: {e}")
    
    def _update_buffer_status(self):
        """Update buffer status display."""
        if hasattr(self.analyzer, 'buffer_status_label'):
            if self.analyzer.dummy_mode_var.get():
                self.analyzer.buffer_status_label.config(text="Buffer: Testmodus - keine KI-Analyse")
            else:
                status = self.get_buffer_status()
                buffer_text = f"Buffer: {status['buffered']} bereit, {status['analyzing']} analysieren, {status['failed']} fehlgeschlagen"
                self.analyzer.buffer_status_label.config(text=buffer_text)
    
    def get_buffer_status(self):
        """Get current buffer status for display."""
        return {
            'buffered': len(self.buffer),
            'analyzing': len(self.analyzing),
            'failed': len(self.failed)
        }
    
    def cleanup(self):
        """Clean up resources."""
        self.executor.shutdown(wait=False)


class ImageAnalyzer:
    def __init__(self, images_folder=None, output_excel=None):
        # Accept parameters from launcher, fallback to environment/config
        self.images_folder = images_folder or IMAGES_FOLDER
        self.output_excel = output_excel or OUTPUT_EXCEL
        self.current_image_index = START_FROM_IMAGE - 1
        self.image_files = []
        self.results = []
        self.current_excel_entry = None  # Track current image's Excel entry for renaming
        # Simple guards to avoid double-opening dialogs
        self._dialog_open = False
        self._manager_opening = False
        
        # Initialize the analysis buffer
        self.analysis_buffer = None  # Will be initialized after GUI setup

        self.setup_gui()
        self.refresh_image_files()
        
        # Initialize buffer after image files are loaded
        self.analysis_buffer = AnalysisBuffer(self)
        
        # Clear fields for the first image (since no analysis exists yet)
        self.clear_fields()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Kamerafallen Bild-Analyzer - GitHub Models")
        
        # Get screen dimensions and set appropriate window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Use 85% of screen height, but cap at reasonable limits
        window_width = min(1200, int(screen_width * 0.9))
        window_height = min(800, int(screen_height * 0.85))
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 600)

        # Top: folder selectors
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Images folder label + entry + icon button
        ttk.Label(folder_frame, text="Bilder-Ordner:").pack(side=tk.LEFT)
        self.images_folder_var = tk.StringVar(value=self.images_folder or "")
        self.images_folder_entry = ttk.Entry(folder_frame, textvariable=self.images_folder_var, state='readonly')
        self.images_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))

        # Create a small folder icon for the browse buttons
        try:
            self.folder_icon = self._create_folder_icon(24, 24)
        except Exception:
            self.folder_icon = None

        if self.folder_icon:
            ttk.Button(folder_frame, image=self.folder_icon, command=self.choose_images_folder).pack(side=tk.LEFT)
        else:
            ttk.Button(folder_frame, text="Wählen...", command=self.choose_images_folder).pack(side=tk.LEFT)

        ttk.Button(folder_frame, text="Im Dateimanager öffnen", command=self.open_images_folder_in_manager).pack(side=tk.LEFT, padx=(5, 10))

        # Output Excel label + entry + icon button
        ttk.Label(folder_frame, text="  Ausgabe Excel:").pack(side=tk.LEFT, padx=(20, 0))
        self.output_excel_var = tk.StringVar(value=self.output_excel or "")
        self.output_excel_entry = ttk.Entry(folder_frame, textvariable=self.output_excel_var, state='readonly')
        self.output_excel_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))

        if self.folder_icon:
            ttk.Button(folder_frame, image=self.folder_icon, command=self.choose_output_excel).pack(side=tk.LEFT)
        else:
            ttk.Button(folder_frame, text="Wählen...", command=self.choose_output_excel).pack(side=tk.LEFT)

        # Create main frames
        left_frame = ttk.Frame(self.root, width=600)
        right_container = ttk.Frame(self.root, width=600)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left - image (fixed, no scrolling)
        ttk.Label(left_frame, text="Bild", font=("Arial", 14)).pack()
        self.image_label = ttk.Label(left_frame)
        self.image_label.pack(pady=10)

        # Right - scrollable form
        # Create canvas and scrollbar for the right side
        canvas = tk.Canvas(right_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas for smooth scrolling (cross-platform)
        def _on_mousewheel(event):
            # Windows and MacOS
            if event.delta:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # Linux
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/Mac
            canvas.bind_all("<Button-4>", _on_mousewheel)    # Linux
            canvas.bind_all("<Button-5>", _on_mousewheel)    # Linux
            
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
            
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Now use self.scrollable_frame instead of right_frame for all form elements
        right_frame = self.scrollable_frame
        ttk.Label(right_frame, text="Bildanalyse", font=("Arial", 14)).pack(pady=(0, 10))

        ttk.Label(right_frame, text="Standort:").pack(anchor=tk.W)
        self.location_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.location_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Uhrzeit:").pack(anchor=tk.W)
        self.time_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.time_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Datum:").pack(anchor=tk.W)
        self.date_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.date_var, width=30).pack(anchor=tk.W)

        # Generl / Luisa
        special_frame = ttk.Frame(right_frame)
        special_frame.pack(anchor=tk.W, pady=(10, 5))
        ttk.Label(special_frame, text="Spezielle Markierungen:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.generl_var = tk.BooleanVar()
        self.luisa_var = tk.BooleanVar()
        checkboxes_frame = ttk.Frame(special_frame)
        checkboxes_frame.pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(checkboxes_frame, text="Generl", variable=self.generl_var, command=self.on_generl_toggle).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(checkboxes_frame, text="Luisa", variable=self.luisa_var, command=self.on_luisa_toggle).pack(side=tk.LEFT, padx=10)

        # Species fields (updated to 4)
        ttk.Label(right_frame, text="Tierarten und Anzahl:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        # Species 1
        species_frame1 = ttk.Frame(right_frame)
        species_frame1.pack(anchor=tk.W, fill=tk.X, pady=2)
        ttk.Label(species_frame1, text="Art 1:").pack(side=tk.LEFT)
        self.species1_var = tk.StringVar()
        ttk.Entry(species_frame1, textvariable=self.species1_var, width=20).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(species_frame1, text="Anzahl:").pack(side=tk.LEFT)
        self.count1_var = tk.StringVar()
        ttk.Entry(species_frame1, textvariable=self.count1_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        # Species 2
        species_frame2 = ttk.Frame(right_frame)
        species_frame2.pack(anchor=tk.W, fill=tk.X, pady=2)
        ttk.Label(species_frame2, text="Art 2:").pack(side=tk.LEFT)
        self.species2_var = tk.StringVar()
        ttk.Entry(species_frame2, textvariable=self.species2_var, width=20).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(species_frame2, text="Anzahl:").pack(side=tk.LEFT)
        self.count2_var = tk.StringVar()
        ttk.Entry(species_frame2, textvariable=self.count2_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        # Species 3 (new)
        species_frame3 = ttk.Frame(right_frame)
        species_frame3.pack(anchor=tk.W, fill=tk.X, pady=2)
        ttk.Label(species_frame3, text="Art 3:").pack(side=tk.LEFT)
        self.species3_var = tk.StringVar()
        ttk.Entry(species_frame3, textvariable=self.species3_var, width=20).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(species_frame3, text="Anzahl:").pack(side=tk.LEFT)
        self.count3_var = tk.StringVar()
        ttk.Entry(species_frame3, textvariable=self.count3_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        # Species 4 (new)
        species_frame4 = ttk.Frame(right_frame)
        species_frame4.pack(anchor=tk.W, fill=tk.X, pady=2)
        ttk.Label(species_frame4, text="Art 4:").pack(side=tk.LEFT)
        self.species4_var = tk.StringVar()
        ttk.Entry(species_frame4, textvariable=self.species4_var, width=20).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(species_frame4, text="Anzahl:").pack(side=tk.LEFT)
        self.count4_var = tk.StringVar()
        ttk.Entry(species_frame4, textvariable=self.count4_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(right_frame, text="Zusammenfassung:").pack(anchor=tk.W, pady=(10, 0))
        self.animals_text = tk.Text(right_frame, height=2, width=40, state='disabled')
        self.animals_text.pack(anchor=tk.W, fill=tk.X)

        # Bind traces (updated to include species 3 and 4)
        self.species1_var.trace('w', self.update_animals_summary)
        self.count1_var.trace('w', self.update_animals_summary)
        self.species2_var.trace('w', self.update_animals_summary)
        self.count2_var.trace('w', self.update_animals_summary)
        self.species3_var.trace('w', self.update_animals_summary)
        self.count3_var.trace('w', self.update_animals_summary)
        self.species4_var.trace('w', self.update_animals_summary)
        self.count4_var.trace('w', self.update_animals_summary)

        # extras
        ttk.Label(right_frame, text="Aktivität:").pack(anchor=tk.W, pady=(10, 0))
        self.aktivitat_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.aktivitat_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Interaktion:").pack(anchor=tk.W)
        self.interaktion_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.interaktion_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Sonstiges:").pack(anchor=tk.W)
        self.sonstiges_text = tk.Text(right_frame, height=2, width=40)
        self.sonstiges_text.pack(anchor=tk.W, fill=tk.X)

        # Testing mode
        self.dummy_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_frame, text="Testdaten verwenden (Testmodus)", 
                       variable=self.dummy_mode_var, command=self.on_dummy_mode_toggle).pack(anchor=tk.W, pady=(10, 0))

        # Buttons - reorganized workflow
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(pady=20)
        
        # Row 1: Analysis and confirmation
        row1 = ttk.Frame(button_frame)
        row1.pack(pady=(0, 5))
        ttk.Button(row1, text="Aktuelles Bild analysieren", command=self.analyze_current_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="Bestätigen (in Excel speichern)", command=self.confirm_entry).pack(side=tk.LEFT, padx=5)
        
        # Row 2: Image actions and navigation
        row2 = ttk.Frame(button_frame)
        row2.pack()
        self.rename_button = ttk.Button(row2, text="Bild umbenennen", command=self.rename_current_image, state='disabled')
        self.rename_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="Nächstes Bild", command=self.next_image).pack(side=tk.LEFT, padx=5)

        # Analysis and buffer status
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(pady=(10, 5), fill=tk.X)
        
        self.analysis_status_label = ttk.Label(status_frame, text="Bereit für Analyse", font=('Arial', 9, 'bold'))
        self.analysis_status_label.pack()
        
        self.buffer_status_label = ttk.Label(status_frame, text="Buffer: Bereit für Batch-Analyse", 
                                           font=('Arial', 8), foreground='gray')
        self.buffer_status_label.pack(pady=(2, 0))

        # Progress and status
        self.progress_var = tk.StringVar()
        ttk.Label(right_frame, textvariable=self.progress_var).pack(pady=10)
        
        # Add filename preview for rename functionality
        self.filename_preview_var = tk.StringVar()
        self.filename_preview_label = ttk.Label(right_frame, textvariable=self.filename_preview_var, 
                                                font=('Arial', 8), foreground='blue')
        self.filename_preview_label.pack(pady=(0, 5))
        
        # Bind form changes to update filename preview
        self.location_var.trace('w', self.update_filename_preview)
        self.date_var.trace('w', self.update_filename_preview)
        self.species1_var.trace('w', self.update_filename_preview)
        self.count1_var.trace('w', self.update_filename_preview)
        self.species2_var.trace('w', self.update_filename_preview)
        self.count2_var.trace('w', self.update_filename_preview)
        self.species3_var.trace('w', self.update_filename_preview)
        self.count3_var.trace('w', self.update_filename_preview)
        self.species4_var.trace('w', self.update_filename_preview)
        self.count4_var.trace('w', self.update_filename_preview)
        self.generl_var.trace('w', self.update_filename_preview)
        self.luisa_var.trace('w', self.update_filename_preview)

    def choose_images_folder(self):
        # Ensure our window is on top so the native dialog appears in front
        initial = self.images_folder or os.path.expanduser('~')
        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            self._bring_root_to_front()
            folder = filedialog.askdirectory(parent=self.root, title="Wähle Bilder-Ordner", initialdir=initial)
        finally:
            # restore normal stacking and focus
            try:
                self.root.attributes('-topmost', False)
                self.root.focus_force()
            except Exception:
                pass
            self._dialog_open = False

        if folder:
            self.images_folder = folder
            self.images_folder_var.set(folder)
            self.refresh_image_files()

    def choose_output_excel(self):
        # Bring our window forward so the file dialog is visible on top
        # If an output path exists, open dialog in that folder
        initial_dir = None
        initial_file = None
        if self.output_excel:
            initial_dir = os.path.dirname(self.output_excel) or os.path.expanduser('~')
            initial_file = os.path.basename(self.output_excel)
        else:
            initial_dir = os.path.expanduser('~')

        if self._dialog_open:
            return
        self._dialog_open = True
        try:
            self._bring_root_to_front()
            path = filedialog.asksaveasfilename(parent=self.root, title="Wähle Ausgabe-Excel-Datei",
                                                initialdir=initial_dir,
                                                initialfile=initial_file,
                                                defaultextension=".xlsx",
                                                filetypes=[("Excel Dateien", "*.xlsx"), ("Alle Dateien", "*")])
        finally:
            try:
                self.root.attributes('-topmost', False)
                self.root.focus_force()
            except Exception:
                pass
            self._dialog_open = False

        if path:
            self.output_excel = path
            self.output_excel_var.set(path)

    def open_images_folder_in_manager(self):
        folder = self.images_folder or IMAGES_FOLDER or os.path.expanduser('~')
        try:
            if self._manager_opening:
                return
            self._manager_opening = True
            # Best-effort: raise our window before launching the manager so it doesn't open hidden
            try:
                self._bring_root_to_front()
            except Exception:
                pass

            if sys.platform.startswith('linux'):
                subprocess.Popen(['xdg-open', folder])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', folder])
            elif os.name == 'nt':
                subprocess.Popen(['explorer', os.path.normpath(folder)])
            else:
                subprocess.Popen(['xdg-open', folder])

            # We can't reliably force another app to the foreground on every platform
            # (window managers differ). We do a best-effort to return focus to the file manager
            # by briefly releasing topmost status here.
            try:
                self.root.attributes('-topmost', False)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Ordner nicht im Dateimanager öffnen: {e}", parent=self.root)
        finally:
            self._manager_opening = False

    def _bring_root_to_front(self):
        """Bring the main window to the front in a best-effort, cross-platform way.

        This sets the window temporarily topmost, lifts it and updates the UI so
        native file dialogs spawned as children are more likely to appear on top.
        """
        try:
            # lift the window and make it temporarily topmost
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.update()
        except Exception:
            # Some platforms/window managers may not support these attributes.
            pass

    def refresh_image_files(self):
        self.image_files = gm_io.get_image_files(self.images_folder)
        self.current_image_index = 0
        if self.image_files:
            self.load_current_image()
        else:
            self.image_label.config(image='')
            self.progress_var.set("Keine Bilder im ausgewählten Ordner")

    def load_current_image(self):
        if self.current_image_index >= len(self.image_files):
            messagebox.showinfo("Fertig", "Alle Bilder wurden verarbeitet!", parent=self.root)
            self.save_results()
            return
        image_file = self.image_files[self.current_image_index]
        images_folder = self.images_folder or IMAGES_FOLDER
        image_path = os.path.join(images_folder, image_file)
        try:
            image = Image.open(image_path)
            image.thumbnail((500, 400))
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except Exception as e:
            print(f"Fehler beim Laden des Bildes {image_path}: {e}")
            self.image_label.configure(image='')
        progress = f"Image {self.current_image_index + 1} of {len(self.image_files)}: {image_file}"
        self.progress_var.set(progress)
        # Update filename preview for current image
        self.update_filename_preview()
        # DON'T automatically clear fields - let navigation methods handle this

    def update_animals_summary(self, *args):
        parts = []
        for species_var, count_var in [(self.species1_var, self.count1_var), (self.species2_var, self.count2_var), (self.species3_var, self.count3_var), (self.species4_var, self.count4_var)]:
            if species_var.get().strip():
                c = count_var.get().strip()
                parts.append(f"{c} {species_var.get().strip()}" if c else species_var.get().strip())
        summary = ", ".join(parts) if parts else "Keine Tiere entdeckt"
        self.animals_text.config(state='normal')
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.insert(1.0, summary)
        self.animals_text.config(state='disabled')

    def update_filename_preview(self, *args):
        """Update the filename preview when form fields change."""
        try:
            if not self.image_files or self.current_image_index >= len(self.image_files):
                self.filename_preview_var.set("")
                return
            
            # If we have an Excel entry, show the actual filename that will be used for renaming
            if hasattr(self, 'current_excel_entry') and self.current_excel_entry:
                # Generate the filename that will be used based on Excel data
                data = self.current_excel_entry
                try:
                    # Generate the filename that will be created (without actually renaming)
                    new_filename = self._generate_preview_filename(data)
                    if new_filename:
                        self.filename_preview_var.set(f"✅ Neuer Name: {new_filename}")
                    else:
                        self.filename_preview_var.set("⚠ Fehler beim Generieren des Dateinamens")
                except Exception as e:
                    print(f"Error generating preview filename: {e}")
                    self.filename_preview_var.set("⚠ Fehler beim Generieren des Dateinamens")
            else:
                # Before confirmation, just show "Neuer Name:" without any filename
                location = self.location_var.get().strip()
                date = self.date_var.get().strip()
                
                if location and location in ['FP1', 'FP2', 'FP3', 'Nische'] and date:
                    self.filename_preview_var.set("🔄 Neuer Name:")
                else:
                    self.filename_preview_var.set("ℹ Standort und Datum erforderlich für Umbenennung")
        except Exception:
            self.filename_preview_var.set("")

    def clear_fields(self):
        self.location_var.set("")
        self.time_var.set("")
        self.date_var.set("")
        self.species1_var.set("")
        self.count1_var.set("")
        self.species2_var.set("")
        self.count2_var.set("")
        self.species3_var.set("")  # New
        self.count3_var.set("")    # New
        self.species4_var.set("")  # New
        self.count4_var.set("")    # New
        self.animals_text.config(state='normal')
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.config(state='disabled')
        self.aktivitat_var.set("")
        self.interaktion_var.set("")
        self.sonstiges_text.delete(1.0, tk.END)
        self.filename_preview_var.set("")

    def analyze_current_image(self):
        """Analyze current image using smart buffer system or dummy data."""
        print(f"DEBUG: Analyze button pressed - Dummy mode: {self.dummy_mode_var.get()}")
        
        if self.dummy_mode_var.get():
            # Use dummy data - no real AI analysis
            print("DEBUG: Using dummy data, no real analysis")
            self.use_dummy_data()
            self.analysis_status_label.config(text="✓ Testdaten eingefügt", foreground="green")
            return
            
        # Real AI analysis mode
        if not self.image_files:
            messagebox.showwarning("Keine Bilder", "Bitte wählen Sie zuerst einen Bilder-Ordner.", parent=self.root)
            return

        if not self.analysis_buffer:
            messagebox.showerror("Fehler", "Analysis Buffer nicht initialisiert.", parent=self.root)
            return

        print("DEBUG: Starting real AI analysis with buffer system")
        # Update status
        self.analysis_status_label.config(text="🔄 Analysiere mit KI...", foreground="blue")
        
        # Get analysis from buffer (will trigger batch because analyze button was pressed)
        result = self.analysis_buffer.get_analysis(self.current_image_index, force_analysis=True)
        
        if result == "analyzing":
            # Analysis in progress, show loading state
            self.analysis_status_label.config(text="🔄 KI-Analyse läuft... (Batch wird verarbeitet)", foreground="orange")
            # The UI will be updated automatically when analysis completes
        elif result == "failed":
            # Analysis failed
            self.analysis_status_label.config(text="❌ KI-Analyse fehlgeschlagen", foreground="red")
            messagebox.showerror("Fehler", "Die KI-Analyse für dieses Bild ist fehlgeschlagen.", parent=self.root)
        else:
            # Analysis result available immediately
            self._apply_analysis_result(result)
            self.analysis_status_label.config(text="✓ KI-Analyse abgeschlossen", foreground="green")
        
        # Update buffer status
        self.analysis_buffer._update_buffer_status()

    def _apply_analysis_result(self, result):
        """Apply analysis result to the GUI fields."""
        # Parse animals to species and populate fields
        self.parse_animals_to_species(result['animals'])
        
        # Update location and other fields
        self.location_var.set(result['location'])
        if result.get('date'):
            self.date_var.set(result['date'])
        if result.get('time'):
            self.time_var.set(result['time'])

    def _navigate_to_next_image(self):
        """Navigate to the next image with proper buffer handling."""
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            print(f"DEBUG: Navigating to image {self.current_image_index + 1}/{len(self.image_files)}")
            
            # Load the image and clear fields
            self.load_current_image()
            self.clear_fields()
            
            # Only use buffer if NOT in dummy mode
            if self.analysis_buffer and not self.dummy_mode_var.get():
                result = self.analysis_buffer.get_analysis(self.current_image_index, force_analysis=False)
                if result not in ["analyzing", "failed", "not_analyzed"]:
                    # Auto-fill if already analyzed
                    print(f"DEBUG: Image {self.current_image_index} already analyzed")
                    self._apply_analysis_result(result)
                    self.analysis_status_label.config(text="✓ Bereits analysiert", foreground="green")
                else:
                    self.analysis_status_label.config(text="Bereit für Analyse", foreground="black")
                
                # Update buffer status
                self.analysis_buffer._update_buffer_status()
            else:
                # In dummy mode or no buffer - just show ready state
                if self.dummy_mode_var.get():
                    self.analysis_status_label.config(text="Testmodus - bereit für Dummy-Daten", foreground="blue")
                else:
                    self.analysis_status_label.config(text="Bereit für Analyse", foreground="black")
            return True
        else:
            messagebox.showinfo("Ende", "Sie haben das letzte Bild erreicht.", parent=self.root)
            return False

    def use_dummy_data(self):
        import random
        locations = ["FP1", "FP2", "FP3", "Nische"]
        species_options = [
            ("Rabe", ["1", "2", "3"]),
            ("Steinadler", ["1"]),
            ("Bartgeier", ["1"]),
            ("Gämse", ["1", "2", "3", "4", "5"]),
            ("Fuchs", ["1"]),
            ("Steinbock", ["1", "2", "3"]),
            ("Murmeltier", ["1", "2"]),
            ("", [""]),
        ]
        activities = ["Fressen", "Ruhen", "Fliegen", "Laufen", "Putzen", ""]
        interactions = ["", "Aggressiv", "Territorial", "Gemeinsam fressen", "Eltern-Nachkommen"]
        sonstiges_options = ["", "Klares Wetter", "Neblig", "Regen", "Schnee sichtbar", "Gute Sicht"]

        self.location_var.set(random.choice(locations))
        self.time_var.set(f"{random.randint(6,18):02d}:{random.randint(0,59):02d}:00")
        self.date_var.set(f"{random.randint(1,31):02d}.{random.randint(7,8):02d}.2025")

        num_species = random.choices([0, 1, 2, 3, 4], weights=[10, 40, 30, 15, 5])[0]  # Updated to allow up to 4

        species_vars = [self.species1_var, self.species2_var, self.species3_var, self.species4_var]  # New
        count_vars = [self.count1_var, self.count2_var, self.count3_var, self.count4_var]          # New

        for i in range(num_species):
            species, counts = random.choice(species_options[:-1])
            species_vars[i].set(species)
            count_vars[i].set(random.choice(counts))

        # Clear unused species
        for i in range(num_species, 4):
            species_vars[i].set("")
            count_vars[i].set("")

        self.aktivitat_var.set(random.choice(activities))
        self.interaktion_var.set(random.choice(interactions))

        self.sonstiges_text.delete(1.0, tk.END)
        self.sonstiges_text.insert(1.0, random.choice(sonstiges_options))

        print("Mit Testdaten gefüllt")

    def analyze_with_ai(self):
        image_file = self.image_files[self.current_image_index]
        images_folder = self.images_folder or IMAGES_FOLDER
        image_path = os.path.join(images_folder, image_file)
        try:
            animals, location, time_str, date_str = gm_api.analyze_with_github_models(image_path, GITHUB_TOKEN, ANIMAL_SPECIES)

            # Set checkboxes based on animals string
            if "Generl und Luisa" in animals or "Luisa und Generl" in animals:
                # Both are present
                self.generl_var.set(True)
                self.luisa_var.set(True)
            elif "(Luisa)" in animals:
                # Only Luisa
                self.luisa_var.set(True)
                self.generl_var.set(False)
            elif "(Generl)" in animals:
                # Only Generl
                self.generl_var.set(True)
                self.luisa_var.set(False)
            elif "unbestimmt" in animals:
                # Unidentified, so neither
                self.generl_var.set(False)
                self.luisa_var.set(False)
            else:
                # Default: neither
                self.generl_var.set(False)
                self.luisa_var.set(False)

            # Populate other fields as before
            self.location_var.set(location)
            self.time_var.set(time_str)
            self.date_var.set(date_str)
            self.parse_animals_to_species(animals)
        except Exception as e:
            print(f"Fehler bei KI-Analyse: {e}")
            animals, location, time_str, date_str = "", "", "", ""
            self.location_var.set(location)
            self.time_var.set(time_str)
            self.date_var.set(date_str)
            self.parse_animals_to_species(animals)

    def parse_animals_to_species(self, animals_str):
        """Parse the animals detection string and populate species fields."""
        if not animals_str or animals_str.strip() == "":
            return
        
        # Simple parsing - split by comma and try to extract species and counts
        parts = [p.strip() for p in animals_str.split(',')]
        
        # Clear existing fields
        self.species1_var.set("")
        self.count1_var.set("")
        self.species2_var.set("")
        self.count2_var.set("")
        self.species3_var.set("")  # New
        self.count3_var.set("")    # New
        self.species4_var.set("")  # New
        self.count4_var.set("")    # New
        
        species_vars = [self.species1_var, self.species2_var, self.species3_var, self.species4_var]  # New
        count_vars = [self.count1_var, self.count2_var, self.count3_var, self.count4_var]          # New
        
        for i, part in enumerate(parts[:4]):  # Updated to handle up to 4
            # Try to extract number and species name
            import re
            match = re.match(r'(\d+)\s*(.+)', part.strip())
            if match:
                count, species = match.groups()
                species_vars[i].set(species.strip())
                count_vars[i].set(count)
            else:
                # No number found, assume count is 1
                species_vars[i].set(part.strip())
                count_vars[i].set("1")

    def rename_current_image(self):
        """Rename the current image using the Excel entry data"""
        if not self.current_excel_entry:
            messagebox.showerror("Fehler", "Bitte bestätigen Sie zuerst die Analyse (in Excel speichern)", parent=self.root)
            return
            
        if not self.image_files:
            return
            
        image_file = self.image_files[self.current_image_index]
        data = self.current_excel_entry
        
        # Rename the image file using the Excel data
        new_image_name = gm_io.create_backup_and_rename_image(
            self.images_folder, image_file, 
            data['Standort'], data['Datum'], 
            data['Art 1'], data['Anzahl 1'], 
            data['Art 2'], data['Anzahl 2'], 
            data['Nr. '], 
            data['Generl'] == 'X', 
            data['Luisa'] == 'X'
        )
        
        if new_image_name is None:
            messagebox.showerror("Fehler", "Fehler beim Umbenennen des Bildes", parent=self.root)
            return
            
        # Update the Excel entry with the new filename
        data['filename'] = new_image_name
        gm_io.save_single_result(self.output_excel or OUTPUT_EXCEL, data['Standort'], data)
        
        # Update the image files list to reflect the rename
        new_path = os.path.join(self.images_folder, new_image_name)
        self.image_files[self.current_image_index] = new_path
        
        # Disable rename button since this image is now processed
        self.rename_button.config(state='disabled')
        print(f"✅ Image renamed to: {new_image_name}")
        messagebox.showinfo("Erfolg", f"✅ Bild erfolgreich umbenannt!\n\nNeuer Name:\n{new_image_name}", parent=self.root)

    def confirm_entry(self):
        """Wrapper method for button compatibility"""
        self.confirm_and_save_to_excel()

    def _generate_preview_filename(self, data):
        """Generate the preview filename based on Excel entry data (without actually renaming)"""
        try:
            location = data['Standort']
            date = data['Datum']
            species1 = data['Art 1']
            count1 = data['Anzahl 1']
            species2 = data['Art 2']
            count2 = data['Anzahl 2']
            new_id = data['Nr. ']
            generl_checked = data['Generl'] == 'X'
            luisa_checked = data['Luisa'] == 'X'
            
            # Generate animals string
            animals = []
            if species1:
                animals.append(f"{species1}_{count1 or '1'}")
            if species2:
                animals.append(f"{species2}_{count2 or '1'}")
            animal_str = "_".join(animals) if animals else "Unknown"
            
            # Format date
            try:
                if '.' in date:
                    day, month, year = date.split('.')
                    short_year = year[-2:] if len(year) == 4 else year
                    date_str = f"{month}.{day}.{short_year}"
                else:
                    date_str = date
            except Exception:
                date_str = date
            
            # Special names
            special_names = []
            if generl_checked:
                special_names.append("Generl")
            if luisa_checked:
                special_names.append("Luisa")
            special_str = "_".join(special_names) if special_names else ""
            
            # Generate filename
            if special_str:
                new_name = f"{location}_{new_id:04d}_{date_str}_{special_str}_{animal_str}.jpeg"
            else:
                new_name = f"{location}_{new_id:04d}_{date_str}_{animal_str}.jpeg"
            
            return new_name
        except Exception as e:
            print(f"Error generating preview filename: {e}")
            return None

    def _generate_new_filename(self, current_filename, location, date, species1, count1, species2, count2, species3, count3, species4, count4, generl_checked, luisa_checked):  # Updated signature
        import re
        
        # Extract number from current filename (e.g., fotofallen_2025_123.jpeg -> 123)
        nr = None
        match = re.search(r'fotofallen_2025_(\d+)', current_filename)
        if match:
            nr = int(match.group(1))
        else:
            # Try other patterns like location_NNNN_date_animals.jpeg
            match = re.search(r'_(\d{4})_', current_filename)
            if match:
                nr = int(match.group(1))
            else:
                # Use timestamp as fallback
                import time
                nr = int(time.time()) % 10000
        
        # Convert date from DD.MM.YYYY to MM.DD.YY format
        date_str = self._convert_date_to_new_format(date)
        
        # Process animals (updated to include species 3 and 4)
        animals = self._process_animals_for_filename(species1, count1, species2, count2, species3, count3, species4, count4)  # Updated
        animal_str = "_".join(animals) if animals else "Unknown"
        
        # Get special names
        special_names = []
        if generl_checked:
            special_names.append("Generl")
        if luisa_checked:
            special_names.append("Luisa")
        special_str = "_".join(special_names) if special_names else ""
        
        # Build new filename: location_NRNR_MM.DD.YY_[Generl_][Luisa_]Animal_count.jpeg
        if special_str:
            new_name = f"{location}_{nr:04d}_{date_str}_{special_str}_{animal_str}.jpeg"
        else:
            new_name = f"{location}_{nr:04d}_{date_str}_{animal_str}.jpeg"
            
        return new_name

    def _convert_date_to_new_format(self, date_str):
        """Convert date from DD.MM.YYYY to MM.DD.YY format."""
        try:
            import pandas as pd
            # If it's a pandas Timestamp or datetime object
            date_obj = pd.to_datetime(date_str)
            # Convert to MM.DD.YY format
            return date_obj.strftime("%m.%d.%y")
        except Exception:
            # If it's a string, try to parse DD.MM.YYYY
            parts = str(date_str).split(".")
            if len(parts) == 3:
                day, month, year = parts
                # Convert to MM.DD.YY format (last 2 digits of year)
                short_year = year[-2:] if len(year) == 4 else year
                return f"{month.zfill(2)}.{day.zfill(2)}.{short_year}"
            else:
                print(f"Warnung: Unerkanntes Datumsformat: {date_str}")
                return str(date_str)

    def _process_animals_for_filename(self, species1, count1, species2, count2, species3, count3, species4, count4):  # Updated signature
        """Process animal information for filename according to renamer specifications."""
        animals = []
        
        # Handle Art 1 to Art 4 columns with quantities
        for animal, count in [(species1, count1), (species2, count2), (species3, count3), (species4, count4)]:  # Updated
            if animal:
                count_suffix = ""
                
                # Get count if available
                if count:
                    try:
                        count_val = int(float(count))
                        if count_val > 1:
                            count_suffix = f"_{count_val}"
                    except (ValueError, TypeError):
                        pass
                
                # Handle special animal codes (matching the renamer script logic)
                if animal.upper() == 'RK':
                    animals.append(f"Rabenkrähe{count_suffix}")
                elif animal.lower() == 'rk':
                    animals.append(f"Kolkrabe{count_suffix}")
                elif animal.upper() == 'RV':
                    animals.append(f"Kolkrabe{count_suffix}")  # Assuming RV is also Kolkrabe
                elif animal.lower() in ['fuchs', 'marder']:
                    animals.append(f"{animal.capitalize()}{count_suffix}")
                elif animal.lower() == 'gams':
                    animals.append(f"Gämse{count_suffix}")
                elif animal:  # Any other animal
                    animals.append(f"{animal}{count_suffix}")
        
        return animals

    def _rename_image_file(self, old_filename, new_filename):
        """Rename the image file with backup creation."""
        images_folder = self.images_folder or IMAGES_FOLDER
        old_path = os.path.join(images_folder, old_filename)
        new_path = os.path.join(images_folder, new_filename)
        
        if not os.path.exists(old_path):
            raise FileNotFoundError(f"Original-Datei nicht gefunden: {old_filename}")
            
        if os.path.exists(new_path):
            raise FileExistsError(f"Ziel-Datei existiert bereits: {new_filename}")
            
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(images_folder, "backup_originals")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup
        backup_path = os.path.join(backup_dir, old_filename)
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(old_path, backup_path)
            print(f"Backup created: {backup_path}")
        
        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed: {old_filename} -> {new_filename}")
        
        return True

    def confirm_and_save_to_excel(self):
        """Confirm current image analysis and save to Excel (enables rename button)"""
        if not self.image_files:
            return
            
        # Collect data from GUI fields
        image_file = self.image_files[self.current_image_index]
        location = self.location_var.get()
        date = self.date_var.get()
        time_str = self.time_var.get()
        
        # Validation
        if not location or location not in ['FP1', 'FP2', 'FP3', 'Nische']:
            messagebox.showerror("Fehler", "Bitte geben Sie einen gültigen Standort ein (FP1, FP2, FP3, Nische)", parent=self.root)
            return
        if not date:
            messagebox.showerror("Fehler", "Bitte geben Sie ein Datum ein", parent=self.root)
            return

        # Get the next ID for this location from Excel (I/O function)
        new_id = gm_io.get_next_id_for_location(self.output_excel or OUTPUT_EXCEL, location)

        # Convert date and time to proper formats for Excel
        processed_date = self._process_date_for_excel(date)
        processed_time = self._process_time_for_excel(time_str)

        # Prepare data structure
        data = {
            'Nr. ': new_id,
            'Standort': location,
            'Datum': processed_date,    # Use processed date
            'Uhrzeit': processed_time,  # Use processed time
            'Generl': 'X' if self.generl_var.get() else '',
            'Luisa': 'X' if self.luisa_var.get() else '',
            'Unbestimmt': 'Bg' if 'Bartgeier' in self.animals_text.get(1.0, tk.END) else '',
            'Aktivität': self.aktivitat_var.get(),
            'Art 1': self.species1_var.get().strip(),
            'Anzahl 1': self.count1_var.get().strip(),
            'Art 2': self.species2_var.get().strip(),
            'Anzahl 2': self.count2_var.get().strip(),
            'Art 3': self.species3_var.get().strip(),
            'Anzahl 3': self.count3_var.get().strip(),
            'Art 4': self.species4_var.get().strip(),
            'Anzahl 4': self.count4_var.get().strip(),
            'Interaktion': self.interaktion_var.get(),
            'Sonstiges': self.sonstiges_text.get(1.0, tk.END).strip(),
            'filename': os.path.basename(image_file),
            'original_filename': image_file
        }

        # Save to Excel using I/O module (no duplication)
        try:
            gm_io.save_single_result(self.output_excel or OUTPUT_EXCEL, location, data)
            
            # Store the Excel entry for renaming (GUI logic)
            self.current_excel_entry = data
            
            # Enable the rename button (GUI logic)
            self.rename_button.config(state='normal')
            
            # Update the filename preview (GUI logic)
            self.update_filename_preview()
            
            print(f"✅ Analysis saved to Excel with ID {new_id} - Rename button enabled")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern in Excel: {e}", parent=self.root)

    def _process_date_for_excel(self, date_str):
        """Convert date string to Excel-compatible format."""
        if not date_str:
            return date_str
        
        # Try to convert DD.MM.YYYY to Excel date number
        try:
            from datetime import datetime
            if '.' in date_str:
                parts = date_str.split('.')
                if len(parts) == 3:
                    day, month, year = parts
                    if len(year) == 2:
                        year = '20' + year
                    dt = datetime(int(year), int(month), int(day))
                    # Convert to Excel date number (days since 1900-01-01)
                    excel_date = (dt - datetime(1900, 1, 1)).days + 2
                    return excel_date
        except:
            pass
        
        # If conversion fails, return as string
        return date_str

    def _process_time_for_excel(self, time_str):
        """Convert time string to Excel-compatible format."""
        if not time_str:
            return time_str
            
        # Try to convert HH:MM:SS to Excel time fraction
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) >= 2:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = int(parts[2]) if len(parts) > 2 else 0
                    # Convert to fraction of day
                    time_fraction = (hours + minutes/60 + seconds/3600) / 24
                    return time_fraction
        except:
            pass
        
        # If conversion fails, return as string
        return time_str

    def next_image(self):
        """Navigate to next image"""
        print("DEBUG: Next image button pressed")
        
        # Reset Excel entry and disable rename button for new image
        self.current_excel_entry = None
        self.rename_button.config(state='disabled')
        
        # Update filename preview for the new image
        self.update_filename_preview()
        
        if not self._navigate_to_next_image():
            # We've reached the end
            self.save_results()
            out = self.output_excel or OUTPUT_EXCEL
            messagebox.showinfo("Fertig", f"Analyse abgeschlossen! Ergebnisse gespeichert in {out}", parent=self.root)

    def skip_image(self):
        """Skip to next image."""
        print("DEBUG: Skip button pressed")
        self._navigate_to_next_image()

    def save_results(self):
        out = self.output_excel or OUTPUT_EXCEL
        for r in self.results:
            loc = r.get('Standort')
            try:
                gm_io.save_single_result(out, loc, r)
            except Exception:
                print(f"Fehler beim Speichern von Ergebnis für {loc}")

    def on_generl_toggle(self):
        print("✅ Generl markiert" if self.generl_var.get() else "❌ Generl entfernt")

    def on_luisa_toggle(self):
        print("✅ Luisa markiert" if self.luisa_var.get() else "❌ Luisa entfernt")

    def on_dummy_mode_toggle(self):
        """Handle dummy mode checkbox toggle."""
        if self.dummy_mode_var.get():
            print("✅ Testmodus aktiviert - keine KI-Analyse")
            self.analysis_status_label.config(text="Testmodus - bereit für Dummy-Daten", foreground="blue")
        else:
            print("❌ Testmodus deaktiviert - KI-Analyse verfügbar")
            self.analysis_status_label.config(text="Bereit für KI-Analyse", foreground="black")
        
        # Update buffer status display
        if self.analysis_buffer:
            self.analysis_buffer._update_buffer_status()

    def run(self):
        """Run the analyzer with proper cleanup."""
        try:
            self.root.mainloop()
        finally:
            # Clean up the analysis buffer
            if self.analysis_buffer:
                self.analysis_buffer.cleanup()

    def _create_folder_icon(self, w=24, h=24):
        """Create a simple folder icon (PIL -> PhotoImage) for button use."""
        try:
            # Check if we can create images in the current environment
            if not hasattr(self, 'root') or not self.root:
                raise Exception("No root window available")
                
            img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # folder base
            draw.rectangle([2, 8, w - 2, h - 3], fill=(220, 180, 60), outline=(140, 100, 30))
            # tab
            draw.rectangle([2, 4, w // 2, 10], fill=(240, 200, 80), outline=(140, 100, 30))
            
            # Create PhotoImage with explicit master
            photo = ImageTk.PhotoImage(img, master=self.root)
            
            # Keep a reference to prevent garbage collection
            if not hasattr(self, '_image_refs'):
                self._image_refs = []
            self._image_refs.append(photo)
            
            return photo
        except Exception as e:
            print(f"Failed to create folder icon: {e}")
            return None


def start_analyzer(images_folder=None, output_excel=None):
    """Start the analyzer with optional folder and output file parameters.
    
    This function can be called from other modules to launch the analyzer
    with pre-selected folders, bypassing the environment variable approach.
    """
    analyzer = ImageAnalyzer(images_folder=images_folder, output_excel=output_excel)
    analyzer.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-gui', action='store_true', help='Schneller Test ohne GUI ausführen')
    parser.add_argument('--images-folder', help='Path to images folder')
    parser.add_argument('--output-excel', help='Path to output Excel file')
    args = parser.parse_args()

    if not GITHUB_TOKEN:
        print("Warnung: GITHUB_MODELS_TOKEN Umgebungsvariable nicht gesetzt. Setzen Sie diese, um GitHub Models API-Aufrufe zu aktivieren.")

    if args.no_gui:
        print("Test ohne GUI: Token vorhanden:", bool(GITHUB_TOKEN))
        sys.exit(0)

    # Use command line arguments if provided, otherwise fall back to environment
    analyzer = ImageAnalyzer(
        images_folder=args.images_folder if hasattr(args, 'images_folder') else None,
        output_excel=args.output_excel if hasattr(args, 'output_excel') else None
    )
    analyzer.run()