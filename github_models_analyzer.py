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
from PIL import Image, ImageTk
import github_models_api as gm_api
import github_models_io as gm_io

# Configuration (can be overridden by env)
IMAGES_FOLDER = os.environ.get("ANALYZER_IMAGES_FOLDER", "")
OUTPUT_EXCEL = os.environ.get("ANALYZER_OUTPUT_EXCEL", "")
GITHUB_TOKEN = os.environ.get("GITHUB_MODELS_TOKEN", "")
START_FROM_IMAGE = 1

ANIMAL_SPECIES = [
    "Bearded Vulture", "Golden Eagle", "Raven", "Carrion Crow",
    "Hooded Crow", "Jackdaw", "Fox", "Chamois", "Ibex", "Marmot"
]


class ImageAnalyzer:
    def __init__(self):
        self.images_folder = IMAGES_FOLDER
        self.output_excel = OUTPUT_EXCEL
        self.current_image_index = START_FROM_IMAGE - 1
        self.image_files = []
        self.results = []

        self.setup_gui()
        self.refresh_image_files()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Kamerafallen Bild-Analyzer - GitHub Models")
        self.root.geometry("1200x800")

        # Top: folder selectors
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        ttk.Label(folder_frame, text="Bilder-Ordner:").pack(side=tk.LEFT)
        self.images_folder_var = tk.StringVar(value=self.images_folder or "Nicht ausgewählt")
        ttk.Label(folder_frame, textvariable=self.images_folder_var, width=60).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(folder_frame, text="Wählen...", command=self.choose_images_folder).pack(side=tk.LEFT)
        ttk.Button(folder_frame, text="Im Dateimanager öffnen", command=self.open_images_folder_in_manager).pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(folder_frame, text="  Ausgabe Excel:").pack(side=tk.LEFT, padx=(20, 0))
        self.output_excel_var = tk.StringVar(value=self.output_excel or "Nicht ausgewählt")
        ttk.Label(folder_frame, textvariable=self.output_excel_var, width=40).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(folder_frame, text="Wählen...", command=self.choose_output_excel).pack(side=tk.LEFT)

        # Create main frames
        left_frame = ttk.Frame(self.root, width=600)
        right_frame = ttk.Frame(self.root, width=600)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left - image
        ttk.Label(left_frame, text="Image", font=("Arial", 14)).pack()
        self.image_label = ttk.Label(left_frame)
        self.image_label.pack(pady=10)

        # Right - form
        ttk.Label(right_frame, text="Bildanalyse", font=("Arial", 14)).pack()

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

        # Species fields
        ttk.Label(right_frame, text="Tierarten und Anzahl:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        species_frame1 = ttk.Frame(right_frame)
        species_frame1.pack(anchor=tk.W, fill=tk.X, pady=2)
        ttk.Label(species_frame1, text="Art 1:").pack(side=tk.LEFT)
        self.species1_var = tk.StringVar()
        ttk.Entry(species_frame1, textvariable=self.species1_var, width=20).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(species_frame1, text="Anzahl:").pack(side=tk.LEFT)
        self.count1_var = tk.StringVar()
        ttk.Entry(species_frame1, textvariable=self.count1_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        species_frame2 = ttk.Frame(right_frame)
        species_frame2.pack(anchor=tk.W, fill=tk.X, pady=2)
        ttk.Label(species_frame2, text="Art 2:").pack(side=tk.LEFT)
        self.species2_var = tk.StringVar()
        ttk.Entry(species_frame2, textvariable=self.species2_var, width=20).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(species_frame2, text="Anzahl:").pack(side=tk.LEFT)
        self.count2_var = tk.StringVar()
        ttk.Entry(species_frame2, textvariable=self.count2_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(right_frame, text="Zusammenfassung:").pack(anchor=tk.W, pady=(10, 0))
        self.animals_text = tk.Text(right_frame, height=2, width=40, state='disabled')
        self.animals_text.pack(anchor=tk.W)

        # Bind traces
        self.species1_var.trace('w', self.update_animals_summary)
        self.count1_var.trace('w', self.update_animals_summary)
        self.species2_var.trace('w', self.update_animals_summary)
        self.count2_var.trace('w', self.update_animals_summary)

        # extras
        ttk.Label(right_frame, text="Aktivität:").pack(anchor=tk.W, pady=(10, 0))
        self.aktivitat_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.aktivitat_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Interaktion:").pack(anchor=tk.W)
        self.interaktion_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.interaktion_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Sonstiges:").pack(anchor=tk.W)
        self.sonstiges_text = tk.Text(right_frame, height=2, width=40)
        self.sonstiges_text.pack(anchor=tk.W)

        # Testing mode
        self.dummy_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_frame, text="Testdaten verwenden (Testmodus)", variable=self.dummy_mode_var).pack(anchor=tk.W, pady=(10, 0))

        # Buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Aktuelles Bild analysieren", command=self.analyze_current_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Bestätigen & Weiter", command=self.confirm_and_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Bild überspringen", command=self.skip_image).pack(side=tk.LEFT, padx=5)

        # Progress
        self.progress_var = tk.StringVar()
        ttk.Label(right_frame, textvariable=self.progress_var).pack(pady=10)

    def choose_images_folder(self):
        initial = self.images_folder or os.path.expanduser('~')
        folder = filedialog.askdirectory(title="Wähle Bilder-Ordner", initialdir=initial)
        if folder:
            self.images_folder = folder
            self.images_folder_var.set(folder)
            self.refresh_image_files()

    def choose_output_excel(self):
        initial = self.output_excel or os.path.expanduser('~')
        path = filedialog.asksaveasfilename(title="Wähle Ausgabe-Excel-Datei", initialdir=initial,
                                            defaultextension=".xlsx",
                                            filetypes=[("Excel Dateien", "*.xlsx"), ("Alle Dateien", "*")])
        if path:
            self.output_excel = path
            self.output_excel_var.set(path)

    def open_images_folder_in_manager(self):
        folder = self.images_folder or IMAGES_FOLDER or os.path.expanduser('~')
        try:
            if sys.platform.startswith('linux'):
                subprocess.Popen(['xdg-open', folder])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', folder])
            elif os.name == 'nt':
                subprocess.Popen(['explorer', os.path.normpath(folder)])
            else:
                subprocess.Popen(['xdg-open', folder])
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Ordner nicht im Dateimanager öffnen: {e}")

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
            messagebox.showinfo("Fertig", "Alle Bilder wurden verarbeitet!")
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
        self.clear_fields()

    def update_animals_summary(self, *args):
        parts = []
        if self.species1_var.get().strip():
            c = self.count1_var.get().strip()
            parts.append(f"{c} {self.species1_var.get().strip()}" if c else self.species1_var.get().strip())
        if self.species2_var.get().strip():
            c = self.count2_var.get().strip()
            parts.append(f"{c} {self.species2_var.get().strip()}" if c else self.species2_var.get().strip())
        summary = ", ".join(parts) if parts else "Keine Tiere entdeckt"
        self.animals_text.config(state='normal')
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.insert(1.0, summary)
        self.animals_text.config(state='disabled')

    def clear_fields(self):
        self.location_var.set("")
        self.time_var.set("")
        self.date_var.set("")
        self.species1_var.set("")
        self.count1_var.set("")
        self.species2_var.set("")
        self.count2_var.set("")
        self.animals_text.config(state='normal')
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.config(state='disabled')
        self.aktivitat_var.set("")
        self.interaktion_var.set("")
        self.sonstiges_text.delete(1.0, tk.END)

    def analyze_current_image(self):
        if self.dummy_mode_var.get():
            self.use_dummy_data()
        else:
            self.analyze_with_ai()

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

        num_species = random.choices([0, 1, 2], weights=[20, 60, 20])[0]

        if num_species >= 1:
            species1, counts1 = random.choice(species_options[:-1])
            self.species1_var.set(species1)
            self.count1_var.set(random.choice(counts1))
        else:
            self.species1_var.set("")
            self.count1_var.set("")

        if num_species >= 2:
            available_species = [s for s in species_options[:-1] if s[0] != self.species1_var.get()]
            if available_species:
                species2, counts2 = random.choice(available_species)
                self.species2_var.set(species2)
                self.count2_var.set(random.choice(counts2))
            else:
                self.species2_var.set("")
                self.count2_var.set("")
        else:
            self.species2_var.set("")
            self.count2_var.set("")

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
        except Exception as e:
            print(f"Fehler bei KI-Analyse: {e}")
            animals, location, time_str, date_str = "", "", "", ""
        self.location_var.set(location)
        self.time_var.set(time_str)
        self.date_var.set(date_str)
        self.parse_animals_to_species(animals)

    def confirm_and_next(self):
        if not self.image_files:
            return
        image_file = self.image_files[self.current_image_index]
        location = self.location_var.get()
        date = self.date_var.get()
        time = self.time_var.get()
        animals = self.animals_text.get(1.0, tk.END).strip()
        aktivitat = self.aktivitat_var.get()
        interaktion = self.interaktion_var.get()
        sonstiges = self.sonstiges_text.get(1.0, tk.END).strip()
        species1 = self.species1_var.get().strip()
        count1 = self.count1_var.get().strip()
        species2 = self.species2_var.get().strip()
        count2 = self.count2_var.get().strip()
        generl_checked = self.generl_var.get()
        luisa_checked = self.luisa_var.get()

        if not location or location not in ['FP1', 'FP2', 'FP3', 'Nische']:
            messagebox.showerror("Fehler", "Bitte geben Sie einen gültigen Standort ein (FP1, FP2, FP3, Nische)")
            return
        if not date:
            messagebox.showerror("Fehler", "Bitte geben Sie ein Datum ein")
            return

        new_id = gm_io.get_next_id_for_location(self.output_excel or OUTPUT_EXCEL, location)

        new_image_name = gm_io.create_backup_and_rename_image(
            self.images_folder, image_file, location, date, species1, count1, species2, count2, new_id, generl_checked, luisa_checked
        )
        if new_image_name is None:
            messagebox.showerror("Fehler", "Fehler beim Umbenennen des Bildes. Eintrag wird trotzdem gespeichert.")
            new_image_name = image_file

        data = {
            'Nr. ': new_id,
            'Standort': location,
            'Datum': date,
            'Uhrzeit': time,
            'Dagmar': '',
            'Recka': '',
            'Unbestimmt': 'Bg' if 'Bartgeier' in animals else '',
            'Aktivität': aktivitat,
            'Art 1': species1,
            'Anzahl 1': count1,
            'Art 2': species2,
            'Anzahl 2': count2,
            'Interaktion': interaktion,
            'Sonstiges': sonstiges,
            'General': 'X' if generl_checked else '',
            'Luisa': 'X' if luisa_checked else '',
            'Korrektur': '',
            'animals_detected': animals,
            'filename': new_image_name,
            'original_filename': image_file
        }

        self.results.append(data)
        gm_io.save_single_result(self.output_excel or OUTPUT_EXCEL, location, data)

        # Advance
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.refresh_image_files()
            self.load_current_image()
        else:
            self.save_results()
            out = self.output_excel or OUTPUT_EXCEL
            messagebox.showinfo("Fertig", f"Analyse abgeschlossen! Ergebnisse gespeichert in {out}")

    def skip_image(self):
        self.current_image_index += 1
        self.load_current_image()

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

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-gui', action='store_true', help='Run a quick headless check')
    args = parser.parse_args()

    if not GITHUB_TOKEN:
        print("Warning: GITHUB_MODELS_TOKEN environment variable not set. Set it to enable GitHub Models API calls.")

    if args.no_gui:
        print("Headless check: token present:", bool(GITHUB_TOKEN))
        sys.exit(0)

    analyzer = ImageAnalyzer()
    analyzer.run()
