import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import base64
import requests
import re

# --- USER CONFIGURATION ---
IMAGES_FOLDER = "/home/jonathan/Downloads/2025_extracted_images"
OUTPUT_EXCEL = "/home/jonathan/development/extract_images_outlook/analyzed_images.xlsx"
GITHUB_TOKEN = "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"  # Get from https://github.com/settings/tokens
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
        self.root.title("Camera Trap Image Analyzer - GitHub Models")
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
        ttk.Label(right_frame, text="Image Analysis", font=("Arial", 14)).pack()
        
        # Form fields
        ttk.Label(right_frame, text="Location:").pack(anchor=tk.W)
        self.location_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.location_var, width=30).pack(anchor=tk.W)
        
        ttk.Label(right_frame, text="Time:").pack(anchor=tk.W)
        self.time_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.time_var, width=30).pack(anchor=tk.W)
        
        ttk.Label(right_frame, text="Date:").pack(anchor=tk.W)
        self.date_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.date_var, width=30).pack(anchor=tk.W)
        
        ttk.Label(right_frame, text="Animals Detected:").pack(anchor=tk.W)
        animals_entry = tk.Text(right_frame, height=3, width=40)
        animals_entry.pack(anchor=tk.W)
        self.animals_text = animals_entry
        
        # Control buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Analyze Current Image", 
                  command=self.analyze_current_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Confirm & Next", 
                  command=self.confirm_and_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Skip Image", 
                  command=self.skip_image).pack(side=tk.LEFT, padx=5)
        
        # Progress info
        self.progress_var = tk.StringVar()
        ttk.Label(right_frame, textvariable=self.progress_var).pack(pady=10)
        
        # Load first image
        self.load_current_image()
    
    def load_current_image(self):
        """Load and display the current image."""
        if self.current_image_index >= len(self.image_files):
            messagebox.showinfo("Complete", "All images have been processed!")
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
    
    def analyze_current_image(self):
        """Analyze the current image with GitHub Models."""
        image_file = self.image_files[self.current_image_index]
        image_path = os.path.join(IMAGES_FOLDER, image_file)
        
        # Show analysis in progress
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.insert(1.0, "Analyzing with AI...")
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
        
        # Prepare Excel row data according to your spreadsheet columns
        data = {
            'Nr': image_number,  # Number from filename
            'Standort': location,  # Location (FP1/FP2/FP3/Nische)
            'Datum': date,  # Date
            'Uhrzeit': time,  # Time
            'Aktivät': '',  # Activity column (empty for now)
            'Art 1': '',  # Species 1 (empty for now)
            'Anzahl': '',  # Count (empty for now)
            'Art 2': '',  # Species 2 (empty for now)
            'Anzahl.1': '',  # Count 2 (empty for now)
            'Interaction': '',  # Interaction (empty for now)
            'Sonstiges': '',  # Other (empty for now)
            'Konstruk': '',  # Construction (empty for now)
            'Unbestimmt': 'Bg' if 'Bearded Vulture' in animals else '',  # "Bg" for Bearded Vultures
            'filename': image_file  # Keep filename for reference
        }
        
        # Add to results
        self.results.append(data)
        print(f"Saved data for image {image_number}: {location}, {date}, {time}")
        
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
        """Save results to Excel file with proper column mapping."""
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_excel(OUTPUT_EXCEL, index=False)
            print(f"Results saved to {OUTPUT_EXCEL}")
            print(f"Analyzed {len(self.results)} images")
            print("Excel columns:")
            print("- Nr: Image number from filename") 
            print("- Standort: Location (FP1/FP2/FP3/Nische)")
            print("- Datum: Date")
            print("- Uhrzeit: Time")
            print("- Unbestimmt: 'Bg' for Bearded Vultures")
        else:
            print("No results to save")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

if __name__ == "__main__":
    # Check if GitHub token is set
    if GITHUB_TOKEN == "your-github-token-here":
        print("Please set your GitHub token in the GITHUB_TOKEN variable.")
        print("Get a token from: https://github.com/settings/tokens")
        print("Make sure to enable 'Models' scope when creating the token.")
        exit(1)
    
    print("GitHub Models Image Analyzer")
    print("=" * 40)
    print("If you get a 401 error:")
    print("1. Go to https://github.com/settings/tokens")
    print("2. Create a new token with 'Models' scope enabled")
    print("3. Update GITHUB_TOKEN in this script")
    print("=" * 40)
    
    analyzer = ImageAnalyzer()
    analyzer.run()
