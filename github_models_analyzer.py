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
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import base64
import requests
import re

# --- BENUTZER KONFIGURATION ---
IMAGES_FOLDER = "/home/jonathan/Downloads/2025_extracted_images"
OUTPUT_EXCEL = "/home/jonathan/development/extract_images_outlook/analyzed_images.xlsx"
GITHUB_TOKEN = "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"  # Von https://github.com/settings/tokens
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
        self.current_image_index = START_FROM_IMAGE - 1
        self.image_files = self.get_image_files()
        self.results = []
        
        # Create GUI
        self.setup_gui()
        
    def get_image_files(self):
        """Get list of image files in the folder."""
        files = []
        for f in os.listdir(IMAGES_FOLDER):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                files.append(f)
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
   - Time: Extract time in HH:MM:SS format
   - Date: Extract date in DD-MM-YYYY format

Please format your response exactly like this:
ANIMALS: [animal name with count or "None detected"]
LOCATION: [FP1/FP2/FP3/Nische only]
TIME: [time in HH:MM:SS]
DATE: [date in DD-MM-YYYY]"""

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
            elif line.startswith('DATE:'):
                date_str = line.replace('DATE:', '').strip()
        
        return animals, location, time_str, date_str
    
    def setup_gui(self):
        """Create the GUI interface."""
        self.root = tk.Tk()
        self.root.title("Kamerafallen Bild-Analyzer - GitHub Models")
        self.root.geometry("1200x800")
        
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
        
        ttk.Label(right_frame, text="Erkannte Tiere:").pack(anchor=tk.W)
        animals_entry = tk.Text(right_frame, height=3, width=40)
        animals_entry.pack(anchor=tk.W)
        self.animals_text = animals_entry
        
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
        self.load_current_image()
    
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
        
    def clear_fields(self):
        """Clear all input fields."""
        self.location_var.set("")
        self.time_var.set("")
        self.date_var.set("")
        self.animals_text.delete(1.0, tk.END)
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
        
        # Dummy animals
        animals_options = [
            "1 Rabe", "2 Raben", "1 Steinadler", "1 Bartgeier", 
            "3 Gämse", "1 Fuchs", "2 Steinböcke", "1 Murmeltier", "Keine Tiere entdeckt"
        ]
        
        # Dummy activities
        activities = ["Fressen", "Ruhen", "Fliegen", "Laufen", "Putzen", ""]
        
        # Dummy interactions
        interactions = ["", "Aggressiv", "Territorial", "Gemeinsam fressen", "Eltern-Nachkommen"]
        
        # Dummy sonstiges
        sonstiges_options = ["", "Klares Wetter", "Neblig", "Regen", "Schnee sichtbar", "Gute Sicht"]
        
        # Generate dummy data
        self.location_var.set(random.choice(locations))
        self.time_var.set(f"{random.randint(6,18):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}")
        self.date_var.set(f"{random.randint(1,31):02d}-{random.randint(7,8):02d}-2025")
        
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.insert(1.0, random.choice(animals_options))
        
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
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.insert(1.0, "Analysiere mit KI...")
        self.root.update()
        
        # Analyze with GitHub Models
        animals, location, time_str, date_str = self.analyze_with_github_models(image_path)
        
        # Fill in the form
        self.location_var.set(location)
        self.time_var.set(time_str)
        self.date_var.set(date_str)
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.insert(1.0, animals)
    
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
        
        # Prepare Excel row data according to existing spreadsheet structure
        data = {
            'Nr. ': image_number,  # Number from filename (note the space)
            'Standort': location,  # Location (FP1/FP2/FP3/Nische)
            'Datum': date,  # Date
            'Uhrzeit': time,  # Time
            'Dagmar': '',  # Empty field as in original structure
            'Recka': '',   # Empty field as in original structure
            'Unbestimmt': 'Bg' if 'Bearded Vulture' in animals else '',  # "Bg" for Bearded Vultures
            'Aktivität': aktivitat,  # Activity column (full German spelling)
            'Art 1': '',  # Species 1 (empty for now)
            'Anzahl 1': '',  # Count 1 (empty for now)
            'Art 2': '',  # Species 2 (empty for now)
            'Anzahl 2': '',  # Count 2 (empty for now)
            'Interaktion': interaktion,  # Interaction
            'Sonstiges': sonstiges,  # Other
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
            'Sonstiges', 'Korrektur'
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
            'Sonstiges', 'Korrektur'
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
