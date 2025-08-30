#!/usr/bin/env python3
"""
Kamerafallen Bild-Analyzer mit GitHub Models API
================================================

Ein GUI-Tool zur Analyse von Kamerafallen-Bildern mit KI-Unterstützung.
Analysiert Bilder automatisch und speichert Ergebnisse in Excel-Dateien.

Funktionen:
- Automatische Bilderkennung von Tieren
- Manuelle Datenbearbeitung
- Export in strukturierte Excel-Arbeitsblätter
- GitHub Models API Integration (GPT-4o/GPT-5)

Autor: GitHub Copilot für Jonathan Gehret
Datum: August 2025
"""

import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import base64
import requests
import re

# --- BENUTZER KONFIGURATION ---
# Defaults can be overridden via environment variables
IMAGES_FOLDER = os.environ.get("ANALYZER_IMAGES_FOLDER", "")
OUTPUT_EXCEL = os.environ.get("ANALYZER_OUTPUT_EXCEL", "")
# Read GitHub token from env to avoid storing secrets in code
GITHUB_TOKEN = os.environ.get("GITHUB_MODELS_TOKEN", "")
START_FROM_IMAGE = 1

# GitHub Models API endpoint
GITHUB_API_BASE = "https://models.inference.ai.azure.com"

# Animal species list for AI to choose from
ANIMAL_SPECIES = [
    "Bearded Vulture", "Golden Eagle", "Raven", "Carrion Crow", 
    "Hooded Crow", "Jackdaw", "Fox", "Chamois", "Ibex", "Marmot"
]

class ImageAnalyzer:
    def __init__(self):
        # Instance-configurable paths (set via UI or env)
        self.images_folder = IMAGES_FOLDER
        self.output_excel = OUTPUT_EXCEL

        self.current_image_index = START_FROM_IMAGE - 1
        self.image_files = []
        self.results = []

        # Create GUI
        self.setup_gui()

        # Populate images list (if folder already set via env)
        self.refresh_image_files()
        
    def get_image_files(self):
        """Get list of image files in the folder."""
        files = []
        if not self.images_folder:
            return []

        try:
            for f in os.listdir(self.images_folder):
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    files.append(f)
        except FileNotFoundError:
            return []

        return sorted(files)
    
    def analyze_with_github_models(self, image_path):
        """Use GitHub Models to analyze the image for both animals and metadata."""
        # Try different API endpoints and models
        endpoints_and_models = [
            ("https://models.inference.ai.azure.com", "gpt-5"),
            ("https://models.inference.ai.azure.com", "gpt-4o"),
            ("https://api.github.com/models", "gpt-5"),
            ("https://api.github.com/models", "gpt-4o"),
        ]
        
        for api_base, model_name in endpoints_and_models:
            try:
                result = self._try_api_call(image_path, api_base, model_name)
                if result != ("Error in analysis", "", "", ""):
                    return result
            except Exception as e:
                print(f"Failed with {api_base} and {model_name}: {e}")
                continue
        
        return "Error in analysis", "", "", ""
    
    def _try_api_call(self, image_path, api_base, model_name):
        """Try a specific API endpoint and model."""
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            print(f"Trying: {api_base}/chat/completions with {model_name}")
            
            # Create comprehensive prompt for both tasks
            prompt = f"""Analyze this camera trap image and provide the following information:

1. ANIMALS: Identify any animals visible in the image. Choose only from this list: {', '.join(ANIMAL_SPECIES)}
   - For Bearded Vultures: just say "Bearded Vulture" (no count needed)
   - For all other animals: include the count (e.g., "2 Ravens", "1 Fox", "3 Chamois")
   - If no animals visible, say "None detected"

2. METADATA: Read the text at the bottom of the image and extract:
   - Location: Look for FP1, FP2, FP3, or Nische (ignore any "NLP" prefix)
   - Time: Extract time in HH:MM:SS format (with seconds)
   - Date: Extract date in DD.MM.YYYY format (German format with dots)

Please format your response exactly like this:
ANIMALS: [animal name with count or "None detected"]
LOCATION: [FP1/FP2/FP3/Nische only]
TIME: [time in HH:MM:SS]
DATE: [date in DD.MM.YYYY]"""

            # Prepare the payload (use correct parameter based on model)
            if model_name == "gpt-5":
                # GPT-5 uses max_completion_tokens and doesn't support custom temperature
                payload = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_completion_tokens": 500
                }
            else:
                # GPT-4o and other models use max_tokens
                payload = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1
                }
            
            # Make API request
            response = requests.post(
                f"{api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                return self.parse_analysis_response(analysis_text)
            else:
                print(f"API error: {response.status_code} - {response.text}")
                raise Exception(f"API returned {response.status_code}")
                
        except Exception as e:
            print(f"API call error: {e}")
            raise e
    
    def parse_analysis_response(self, analysis_text):
        """Parse the structured response from the AI model."""
        print(f"AI Response: {analysis_text}")
        
        # Default values
        animals = "None detected"
        location = ""
        time_str = ""
        date_str = ""
        
        # Parse the response
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('ANIMALS:'):
                animals = line.replace('ANIMALS:', '').strip()
            elif line.startswith('LOCATION:'):
                location = line.replace('LOCATION:', '').strip()
                # Clean up location - remove "NLP" prefix and extract only FP1/FP2/FP3/Nische
                if 'FP1' in location.upper():
                    location = 'FP1'
                elif 'FP2' in location.upper():
                    location = 'FP2'
                elif 'FP3' in location.upper():
                    location = 'FP3'
                elif 'NISCHE' in location.upper():
                    location = 'Nische'
            elif line.startswith('TIME:'):
                time_str = line.replace('TIME:', '').strip()
                # Convert HH:MM to HH:MM:00 if needed
                if len(time_str.split(':')) == 2:
                    time_str = f"{time_str}:00"
            elif line.startswith('DATE:'):
                date_str = line.replace('DATE:', '').strip()
                # Convert DD-MM-YYYY to DD.MM.YYYY if needed
                if '-' in date_str and '.' not in date_str:
                    date_str = date_str.replace('-', '.')
        
        return animals, location, time_str, date_str
    
    def setup_gui(self):
        """Create the GUI interface."""
        self.root = tk.Tk()
        self.root.title("Kamerafallen Bild-Analyzer - GitHub Models")
        self.root.geometry("1200x800")
        
        # Initialize Generl and Luisa tracking variables
        self.generl_var = tk.BooleanVar()
        self.luisa_var = tk.BooleanVar()
        # Top: folder selectors
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(fill=tk.X, padx=10, pady=(10,0))

        ttk.Label(folder_frame, text="Bilder-Ordner:").pack(side=tk.LEFT)
        self.images_folder_var = tk.StringVar(value=self.images_folder or "Nicht ausgewählt")
        ttk.Label(folder_frame, textvariable=self.images_folder_var, width=60).pack(side=tk.LEFT, padx=(5,10))
        ttk.Button(folder_frame, text="Wählen...", command=self.choose_images_folder).pack(side=tk.LEFT)

        ttk.Label(folder_frame, text="  Ausgabe Excel:").pack(side=tk.LEFT, padx=(20,0))
        self.output_excel_var = tk.StringVar(value=self.output_excel or "Nicht ausgewählt")
        ttk.Label(folder_frame, textvariable=self.output_excel_var, width=40).pack(side=tk.LEFT, padx=(5,10))
        ttk.Button(folder_frame, text="Wählen...", command=self.choose_output_excel).pack(side=tk.LEFT)

        # Create main frames
        left_frame = ttk.Frame(self.root, width=600)
        right_frame = ttk.Frame(self.root, width=600)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left side - Image display
        ttk.Label(left_frame, text="Image", font=("Arial", 14)).pack()
        self.image_label = ttk.Label(left_frame)
        self.image_label.pack(pady=10)

        # Right side - Data entry form
        ttk.Label(right_frame, text="Bildanalyse", font=("Arial", 14)).pack()

        # Form fields
        ttk.Label(right_frame, text="Standort:").pack(anchor=tk.W)
        self.location_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.location_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Uhrzeit:").pack(anchor=tk.W)
        self.time_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.time_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Datum:").pack(anchor=tk.W)
        self.date_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.date_var, width=30).pack(anchor=tk.W)

        # Generl and Luisa checkboxes
        special_frame = ttk.Frame(right_frame)
        special_frame.pack(anchor=tk.W, pady=(10,5))
        ttk.Label(special_frame, text="Spezielle Markierungen:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        checkboxes_frame = ttk.Frame(special_frame)
        checkboxes_frame.pack(anchor=tk.W, pady=5)

        generl_checkbox = ttk.Checkbutton(checkboxes_frame, text="Generl", 
                                         variable=self.generl_var,
                                         command=self.on_generl_toggle)
        generl_checkbox.pack(side=tk.LEFT, padx=(0,10))

        luisa_checkbox = ttk.Checkbutton(checkboxes_frame, text="Luisa", 
                                       variable=self.luisa_var,
                                       command=self.on_luisa_toggle)
        luisa_checkbox.pack(side=tk.LEFT, padx=10)

        # Animal species and count fields
        ttk.Label(right_frame, text="Tierarten und Anzahl:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10,5))

        # First species
        species_frame1 = ttk.Frame(right_frame)
        species_frame1.pack(anchor=tk.W, fill=tk.X, pady=2)
        ttk.Label(species_frame1, text="Art 1:").pack(side=tk.LEFT)
        self.species1_var = tk.StringVar()
        ttk.Entry(species_frame1, textvariable=self.species1_var, width=20).pack(side=tk.LEFT, padx=(5,10))
        ttk.Label(species_frame1, text="Anzahl:").pack(side=tk.LEFT)
        self.count1_var = tk.StringVar()
        ttk.Entry(species_frame1, textvariable=self.count1_var, width=8).pack(side=tk.LEFT, padx=(5,0))

        # Second species
        species_frame2 = ttk.Frame(right_frame)
        species_frame2.pack(anchor=tk.W, fill=tk.X, pady=2)
        ttk.Label(species_frame2, text="Art 2:").pack(side=tk.LEFT)
        self.species2_var = tk.StringVar()
        ttk.Entry(species_frame2, textvariable=self.species2_var, width=20).pack(side=tk.LEFT, padx=(5,10))
        ttk.Label(species_frame2, text="Anzahl:").pack(side=tk.LEFT)
        self.count2_var = tk.StringVar()
        ttk.Entry(species_frame2, textvariable=self.count2_var, width=8).pack(side=tk.LEFT, padx=(5,0))

        # Summary field for reference (read-only)
        ttk.Label(right_frame, text="Zusammenfassung:").pack(anchor=tk.W, pady=(10,0))
        animals_entry = tk.Text(right_frame, height=2, width=40, state='disabled')
        animals_entry.pack(anchor=tk.W)
        self.animals_text = animals_entry

        # Bind events to update summary when species/count fields change
        self.species1_var.trace('w', self.update_animals_summary)
        self.count1_var.trace('w', self.update_animals_summary)
        self.species2_var.trace('w', self.update_animals_summary)
        self.count2_var.trace('w', self.update_animals_summary)

        # Additional fields for Excel columns
        ttk.Label(right_frame, text="Aktivität:").pack(anchor=tk.W, pady=(10,0))
        self.aktivitat_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.aktivitat_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Interaktion:").pack(anchor=tk.W)
        self.interaktion_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.interaktion_var, width=30).pack(anchor=tk.W)

        ttk.Label(right_frame, text="Sonstiges:").pack(anchor=tk.W)
        self.sonstiges_text = tk.Text(right_frame, height=2, width=40)
        self.sonstiges_text.pack(anchor=tk.W)

        # Testing mode checkbox
        self.dummy_mode_var = tk.BooleanVar(value=True)  # Default to dummy mode
        dummy_checkbox = ttk.Checkbutton(right_frame, text="Testdaten verwenden (Testmodus)", 
                                       variable=self.dummy_mode_var)
        dummy_checkbox.pack(anchor=tk.W, pady=(10,0))

        # Control buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Aktuelles Bild analysieren", 
                  command=self.analyze_current_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Bestätigen & Weiter", 
                  command=self.confirm_and_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Bild überspringen", 
                  command=self.skip_image).pack(side=tk.LEFT, padx=5)

        # Progress info
        self.progress_var = tk.StringVar()
        ttk.Label(right_frame, textvariable=self.progress_var).pack(pady=10)

        # Load first image
        # Loading of the current image happens after images list is populated
        # via self.refresh_image_files()

    def choose_images_folder(self):
        """Open a folder dialog to choose the images folder and refresh list."""
        folder = filedialog.askdirectory(title="Wähle Bilder-Ordner")
        if folder:
            self.images_folder = folder
            self.images_folder_var.set(folder)
            self.refresh_image_files()

    def choose_output_excel(self):
        """Open a save-as dialog to choose the output Excel file."""
        path = filedialog.asksaveasfilename(title="Wähle Ausgabe-Excel-Datei",
                                            defaultextension=".xlsx",
                                            filetypes=[("Excel Dateien", "*.xlsx"), ("Alle Dateien", "*")])
        if path:
            self.output_excel = path
            self.output_excel_var.set(path)

    def refresh_image_files(self):
        """Refresh the internal list of image files from the selected folder."""
        self.image_files = self.get_image_files()
        self.current_image_index = 0
        if self.image_files:
            self.load_current_image()
        else:
            self.image_label.config(image='')
            self.progress_var.set("Keine Bilder im ausgewählten Ordner")
    
    def on_generl_toggle(self):
        """Handle Generl checkbox toggle."""
        if self.generl_var.get():
            print("✅ Generl markiert")
        else:
            print("❌ Generl entfernt")
    
    def on_luisa_toggle(self):
        """Handle Luisa checkbox toggle."""
        if self.luisa_var.get():
            print("✅ Luisa markiert")
        else:
            print("❌ Luisa entfernt")
    
    def load_current_image(self):
        """Lädt und zeigt das aktuelle Bild an."""
        if self.current_image_index >= len(self.image_files):
            messagebox.showinfo("Fertig", "Alle Bilder wurden verarbeitet!")
            self.save_results()
            return
            
        image_file = self.image_files[self.current_image_index]
        image_path = os.path.join(IMAGES_FOLDER, image_file)
        
        # Load and resize image for display
        image = Image.open(image_path)
        image.thumbnail((500, 400))
        photo = ImageTk.PhotoImage(image)
        
        self.image_label.configure(image=photo)
        self.image_label.image = photo  # Keep a reference
        
        # Update progress
        progress = f"Image {self.current_image_index + 1} of {len(self.image_files)}: {image_file}"
        self.progress_var.set(progress)
        
        # Clear form
        self.clear_fields()
        
    def update_animals_summary(self, *args):
        """Update the animals summary field based on species and count inputs."""
        summary_parts = []
        
        # Add first species if specified
        if self.species1_var.get().strip():
            species1 = self.species1_var.get().strip()
            count1 = self.count1_var.get().strip()
            if count1:
                summary_parts.append(f"{count1} {species1}")
            else:
                summary_parts.append(species1)
        
        # Add second species if specified
        if self.species2_var.get().strip():
            species2 = self.species2_var.get().strip()
            count2 = self.count2_var.get().strip()
            if count2:
                summary_parts.append(f"{count2} {species2}")
            else:
                summary_parts.append(species2)
        
        # Update summary field
        summary_text = ", ".join(summary_parts) if summary_parts else "Keine Tiere entdeckt"
        
        self.animals_text.config(state='normal')
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.insert(1.0, summary_text)
        self.animals_text.config(state='disabled')
    
    def clear_fields(self):
        """Clear all input fields."""
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
        """Analyze the current image with GitHub Models or use dummy data."""
        if self.dummy_mode_var.get():
            # Use dummy data for testing
            self.use_dummy_data()
        else:
            # Use real AI analysis
            self.analyze_with_ai()
            
    def use_dummy_data(self):
        """Fill fields with realistic dummy data for testing."""
        import random
        
        # Dummy locations
        locations = ["FP1", "FP2", "FP3", "Nische"]
        
        # Dummy species and their possible counts
        species_options = [
            ("Rabe", ["1", "2", "3"]),
            ("Steinadler", ["1"]),
            ("Bartgeier", ["1"]),
            ("Gämse", ["1", "2", "3", "4", "5"]),
            ("Fuchs", ["1"]),
            ("Steinbock", ["1", "2", "3"]),
            ("Murmeltier", ["1", "2"]),
            ("", [""]),  # No animals option
        ]
        
        # Dummy activities
        activities = ["Fressen", "Ruhen", "Fliegen", "Laufen", "Putzen", ""]
        
        # Dummy interactions
        interactions = ["", "Aggressiv", "Territorial", "Gemeinsam fressen", "Eltern-Nachkommen"]
        
        # Dummy sonstiges
        sonstiges_options = ["", "Klares Wetter", "Neblig", "Regen", "Schnee sichtbar", "Gute Sicht"]
        
        # Generate dummy data
        self.location_var.set(random.choice(locations))
        self.time_var.set(f"{random.randint(6,18):02d}:{random.randint(0,59):02d}:00")
        self.date_var.set(f"{random.randint(1,31):02d}.{random.randint(7,8):02d}.2025")
        
        # Generate 1-2 random species
        num_species = random.choices([0, 1, 2], weights=[20, 60, 20])[0]  # More likely to have 1 species
        
        if num_species >= 1:
            species1, counts1 = random.choice(species_options[:-1])  # Exclude empty option
            self.species1_var.set(species1)
            self.count1_var.set(random.choice(counts1))
        else:
            self.species1_var.set("")
            self.count1_var.set("")
            
        if num_species >= 2:
            # Ensure second species is different from first
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
        """Analyze the current image with GitHub Models API."""
        image_file = self.image_files[self.current_image_index]
        image_path = os.path.join(IMAGES_FOLDER, image_file)
        
        # Show analysis in progress
        self.animals_text.config(state='normal')
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.insert(1.0, "Analysiere mit KI...")
        self.animals_text.config(state='disabled')
        self.root.update()
        
        # Analyze with GitHub Models
        animals, location, time_str, date_str = self.analyze_with_github_models(image_path)
        
        # Fill in the form
        self.location_var.set(location)
        self.time_var.set(time_str)
        self.date_var.set(date_str)
        
        # Parse animals string and populate species fields
        self.parse_animals_to_species(animals)
    
    def parse_animals_to_species(self, animals_text):
        """Parse the animals description and populate species/count fields."""
        # Clear existing data
        self.species1_var.set("")
        self.count1_var.set("")
        self.species2_var.set("")
        self.count2_var.set("")
        
        if not animals_text or animals_text.lower() in ["none detected", "keine tiere entdeckt", ""]:
            return
        
        # Split by comma for multiple species
        species_parts = [part.strip() for part in animals_text.split(',')]
        
        for i, part in enumerate(species_parts[:2]):  # Only handle first two species
            # Try to extract count and species from patterns like "2 Ravens", "1 Fox"
            import re
            match = re.match(r'(\d+)\s+(.+)', part.strip())
            if match:
                count = match.group(1)
                species = match.group(2)
            else:
                # No count found, assume count is 1
                count = "1"
                species = part.strip()
            
            # Set the appropriate fields
            if i == 0:
                self.species1_var.set(species)
                self.count1_var.set(count)
            elif i == 1:
                self.species2_var.set(species)
                self.count2_var.set(count)
    
    def confirm_and_next(self):
        """Save current data and move to next image."""
        if not self.image_files:
            return
            
        # Get the current image filename
        image_file = self.image_files[self.current_image_index]
        
        # Extract number from filename (e.g., "fotofallen_2025_123.jpg" -> 123)
        number_match = re.search(r'fotofallen_2025_(\d+)', image_file)
        image_number = number_match.group(1) if number_match else ""
        
        # Get the analyzed data
        location = self.location_var.get()
        date = self.date_var.get()
        time = self.time_var.get()
        animals = self.animals_text.get(1.0, tk.END).strip()
        aktivitat = self.aktivitat_var.get()
        interaktion = self.interaktion_var.get()
        sonstiges = self.sonstiges_text.get(1.0, tk.END).strip()
        
        # Get species and count data
        species1 = self.species1_var.get().strip()
        count1 = self.count1_var.get().strip()
        species2 = self.species2_var.get().strip()
        count2 = self.count2_var.get().strip()
        
        # Get Generl and Luisa values
        generl_checked = self.generl_var.get()
        luisa_checked = self.luisa_var.get()
        
        # Prepare Excel row data according to existing spreadsheet structure
        data = {
            'Nr. ': image_number,  # Number from filename (note the space)
            'Standort': location,  # Location (FP1/FP2/FP3/Nische)
            'Datum': date,  # Date
            'Uhrzeit': time,  # Time
            'Dagmar': '',  # Empty field as in original structure
            'Recka': '',   # Empty field as in original structure
            'Unbestimmt': 'Bg' if 'Bartgeier' in animals else '',  # "Bg" for Bearded Vultures
            'Aktivität': aktivitat,  # Activity column (full German spelling)
            'Art 1': species1,  # Species 1
            'Anzahl 1': count1,  # Count 1
            'Art 2': species2,  # Species 2
            'Anzahl 2': count2,  # Count 2
            'Interaktion': interaktion,  # Interaction
            'Sonstiges': sonstiges,  # Other
            'General': 'X' if generl_checked else '',  # General column
            'Luisa': 'X' if luisa_checked else '',  # Luisa column
            'Korrektur': '',  # Correction field (empty for now)
            'animals_detected': animals,  # Keep for reference
            'filename': image_file  # Keep filename for reference
        }
        
        # Add to results
        self.results.append(data)
        print(f"Daten gespeichert für Bild {image_number}: {location}, {date}, {time}")
        
        # Immediately save this entry to Excel
        self.save_single_result(data)
        
        # Move to next image
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_current_image()
        else:
            # Save results when done with all images
            self.save_results()
            messagebox.showinfo("Complete", f"Analysis complete! Results saved to {OUTPUT_EXCEL}")
    
    def skip_image(self):
        """Skip current image without saving data."""
        self.current_image_index += 1
        self.load_current_image()
    
    def save_results(self):
        """Save results to Excel file with proper sheet mapping based on location."""
        if not self.results:
            print("Keine Ergebnisse zu speichern")
            return
            
        # Group results by location (Standort)
        location_groups = {}
        for result in self.results:
            location = result.get('Standort', 'Unknown')
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(result)
        
        # Define the proper column order for existing Excel structure
        expected_columns = [
            'Nr. ', 'Standort', 'Datum', 'Uhrzeit', 'Dagmar', 'Recka', 'Unbestimmt',
            'Aktivität', 'Art 1', 'Anzahl 1', 'Art 2', 'Anzahl 2', 'Interaktion', 
            'Sonstiges', 'General', 'Luisa', 'Korrektur'
        ]
        
        # Load existing Excel file or create new one
        try:
            # Load existing Excel file
            with pd.ExcelFile(OUTPUT_EXCEL) as xls:
                existing_sheets = xls.sheet_names
            print(f"Bestehende Excel-Datei gefunden mit Arbeitsblättern: {existing_sheets}")
        except FileNotFoundError:
            print("Excel-Datei nicht gefunden, erstelle neue Arbeitsblätter")
            existing_sheets = []
        
        # Save to appropriate sheets
        try:
            with pd.ExcelWriter(OUTPUT_EXCEL, mode='a' if existing_sheets else 'w', 
                               if_sheet_exists='replace' if existing_sheets else None) as writer:
                
                for location, data_list in location_groups.items():
                    if location and location in ['FP1', 'FP2', 'FP3', 'Nische']:
                        # Create DataFrame with only the expected columns
                        filtered_data = []
                        for item in data_list:
                            filtered_item = {col: item.get(col, '') for col in expected_columns}
                            filtered_data.append(filtered_item)
                        
                        new_df = pd.DataFrame(filtered_data)
                        
                        # Try to load existing data from this sheet
                        try:
                            if location in existing_sheets:
                                existing_df = pd.read_excel(OUTPUT_EXCEL, sheet_name=location)
                                # Only keep columns that exist in our expected structure
                                existing_df = existing_df.reindex(columns=expected_columns, fill_value='')
                                # Append new data to existing
                                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                                print(f"Füge {len(data_list)} Zeilen zu bestehendem {location} Arbeitsblatt hinzu")
                            else:
                                combined_df = new_df
                                print(f"Erstelle neues {location} Arbeitsblatt mit {len(data_list)} Zeilen")
                        except Exception as e:
                            print(f"Konnte bestehendes {location} Arbeitsblatt nicht lesen: {e}")
                            combined_df = new_df
                        
                        # Write to sheet named after location
                        combined_df.to_excel(writer, sheet_name=location, index=False)
                        print(f"✅ {len(data_list)} Bilder in {location} Arbeitsblatt gespeichert")
                    else:
                        print(f"❌ Überspringe unbekannten Standort: {location}")
                        
        except Exception as e:
            print(f"Fehler beim Speichern in Excel: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"Ergebnisse gespeichert in {OUTPUT_EXCEL}")
    
    def save_single_result(self, data):
        """Save a single result immediately to Excel file."""
        location = data.get('Standort', 'Unknown')
        
        if not location or location not in ['FP1', 'FP2', 'FP3', 'Nische']:
            print(f"❌ Skipping unknown location: {location}")
            return
        
        # Define the proper column order for existing Excel structure
        expected_columns = [
            'Nr. ', 'Standort', 'Datum', 'Uhrzeit', 'Dagmar', 'Recka', 'Unbestimmt',
            'Aktivität', 'Art 1', 'Anzahl 1', 'Art 2', 'Anzahl 2', 'Interaktion', 
            'Sonstiges', 'General', 'Luisa', 'Korrektur'
        ]
        
        try:
            # Filter data to only include expected columns
            filtered_data = {col: data.get(col, '') for col in expected_columns}
            new_row = pd.DataFrame([filtered_data])
            
            # Try to read existing data from this sheet
            try:
                existing_df = pd.read_excel(OUTPUT_EXCEL, sheet_name=location)
                # Only keep columns that exist in our expected structure
                existing_df = existing_df.reindex(columns=expected_columns, fill_value='')
                # Append new data to existing
                combined_df = pd.concat([existing_df, new_row], ignore_index=True)
                print(f"✅ Füge 1 Zeile zu bestehendem {location} Arbeitsblatt hinzu (jetzt {len(combined_df)} Zeilen insgesamt)")
            except Exception as e:
                print(f"Konnte bestehendes {location} Arbeitsblatt nicht lesen: {e}")
                combined_df = new_row
                print(f"✅ Erstelle neuen Eintrag in {location} Arbeitsblatt")
            
            # Write to the specific sheet using ExcelWriter
            with pd.ExcelWriter(OUTPUT_EXCEL, mode='a', if_sheet_exists='replace') as writer:
                combined_df.to_excel(writer, sheet_name=location, index=False)
            
            print(f"📝 Eintrag sofort in {location} Arbeitsblatt in {OUTPUT_EXCEL} gespeichert")
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern des einzelnen Ergebnisses in Excel: {e}")
            import traceback
            traceback.print_exc()
        print(f"Insgesamt analysiert: {len(self.results)} Bilder")
        print("Neue Felder enthalten:")
        print("- Aktivität: Aktivitätsinformationen")
        print("- Interaktion: Interaktionsdetails") 
        print("- Sonstiges: Zusätzliche Notizen")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

if __name__ == "__main__":
    # Check if GitHub token is set
    if GITHUB_TOKEN == "your-github-token-here":
        print("Bitte setzen Sie Ihr GitHub Token in der GITHUB_TOKEN Variable.")
        print("Token erhalten von: https://github.com/settings/tokens")
        print("Stellen Sie sicher, dass Sie die 'Models' Berechtigung aktivieren.")
        exit(1)
    
    print("GitHub Models Kamerafallen-Analyzer")
    print("=" * 40)
    print("Bei 401-Fehler:")
    print("1. Gehe zu https://github.com/settings/tokens")
    print("2. Erstelle ein neues Token mit 'Models' Berechtigung")
    print("3. Aktualisiere GITHUB_TOKEN in diesem Skript")
    print("=" * 40)
    
    analyzer = ImageAnalyzer()
    analyzer.run()
