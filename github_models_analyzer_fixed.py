import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import base64
import requests
import json
import re
from datetime import datetime

# --- USER CONFIGURATION ---
IMAGES_FOLDER = "/home/jonathan/Downloads/2025_extracted_images"
OUTPUT_EXCEL = "analyzed_images.xlsx"
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
        # Check for GitHub token
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            print("\n" + "="*60)
            print("GITHUB TOKEN REQUIRED")
            print("="*60)
            print("Please set up your GitHub token with 'Models' scope:")
            print()
            print("1. Go to: https://github.com/settings/tokens")
            print("2. Click 'Generate new token (classic)'")
            print("3. Give it a name like 'GitHub Models Access'")
            print("4. Check the 'Models' scope checkbox")
            print("5. Click 'Generate token'")
            print("6. Copy the generated token")
            print("7. Run this command in your terminal:")
            print("   export GITHUB_TOKEN='your_token_here'")
            print("8. Restart this script")
            print()
            print("="*60)
            exit(1)
            
        self.current_image_index = START_FROM_IMAGE - 1
        self.analyzed_data = []
        
        # Set up GUI
        self.root = tk.Tk()
        self.root.title("Camera Trap Image Analyzer - GitHub Models")
        self.root.geometry("1200x800")
        
        self.setup_gui()
        self.load_images()
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Image display
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Image label
        self.image_label = ttk.Label(left_frame, text="Loading images...")
        self.image_label.pack(pady=10)
        
        # Navigation buttons
        nav_frame = ttk.Frame(left_frame)
        nav_frame.pack(pady=10)
        
        ttk.Button(nav_frame, text="Previous", command=self.prev_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Next", command=self.next_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Analyze with AI", command=self.analyze_current_image).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(left_frame, text="")
        self.status_label.pack(pady=5)
        
        # Right side - Analysis controls
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Analysis results
        ttk.Label(right_frame, text="Analysis Results:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Date/Time
        ttk.Label(right_frame, text="Date:").pack(anchor=tk.W, pady=(10, 0))
        self.date_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.date_var, width=20).pack(anchor=tk.W)
        
        ttk.Label(right_frame, text="Time:").pack(anchor=tk.W, pady=(5, 0))
        self.time_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.time_var, width=20).pack(anchor=tk.W)
        
        # Location
        ttk.Label(right_frame, text="Location:").pack(anchor=tk.W, pady=(10, 0))
        self.location_var = tk.StringVar()
        location_combo = ttk.Combobox(right_frame, textvariable=self.location_var, values=["FP1", "FP2", "FP3", "Nische"], width=17)
        location_combo.pack(anchor=tk.W)
        
        # Animal species
        ttk.Label(right_frame, text="Animal Species:").pack(anchor=tk.W, pady=(10, 0))
        self.species_var = tk.StringVar()
        species_combo = ttk.Combobox(right_frame, textvariable=self.species_var, values=ANIMAL_SPECIES, width=17)
        species_combo.pack(anchor=tk.W)
        
        # Notes
        ttk.Label(right_frame, text="Notes:").pack(anchor=tk.W, pady=(10, 0))
        self.notes_text = tk.Text(right_frame, height=4, width=25)
        self.notes_text.pack(anchor=tk.W)
        
        # Save button
        ttk.Button(right_frame, text="Save & Next", command=self.save_and_next).pack(pady=20)
        
        # AI Response (scrollable)
        ttk.Label(right_frame, text="AI Response:").pack(anchor=tk.W, pady=(10, 0))
        self.ai_response_text = tk.Text(right_frame, height=8, width=25, wrap=tk.WORD)
        self.ai_response_text.pack(anchor=tk.W, fill=tk.BOTH, expand=True)
        
        # Progress
        self.progress_label = ttk.Label(right_frame, text="")
        self.progress_label.pack(anchor=tk.W, pady=(10, 0))
        
    def load_images(self):
        """Load all image files from the folder."""
        if not os.path.exists(IMAGES_FOLDER):
            messagebox.showerror("Error", f"Images folder not found: {IMAGES_FOLDER}")
            return
            
        self.image_files = []
        for file in os.listdir(IMAGES_FOLDER):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.image_files.append(file)
        
        self.image_files.sort()  # Sort alphabetically
        
        if not self.image_files:
            messagebox.showerror("Error", "No image files found in the folder!")
            return
            
        self.display_current_image()
        
    def display_current_image(self):
        """Display the current image and update status."""
        if not self.image_files:
            return
            
        # Update progress
        total_images = len(self.image_files)
        current_num = self.current_image_index + 1
        self.progress_label.config(text=f"Image {current_num} of {total_images}")
        
        # Load and display image
        image_path = os.path.join(IMAGES_FOLDER, self.image_files[self.current_image_index])
        
        try:
            # Open and resize image for display
            pil_image = Image.open(image_path)
            
            # Calculate display size (max 600x400)
            display_width, display_height = 600, 400
            img_width, img_height = pil_image.size
            
            # Calculate scaling factor
            scale = min(display_width/img_width, display_height/img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(pil_image)
            self.image_label.config(image=self.photo, text="")
            
            # Update window title with filename
            self.root.title(f"Camera Trap Analyzer - {self.image_files[self.current_image_index]}")
            
        except Exception as e:
            self.image_label.config(image="", text=f"Error loading image: {str(e)}")
            
    def prev_image(self):
        """Go to previous image."""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_current_image()
            self.clear_fields()
            
    def next_image(self):
        """Go to next image."""
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.display_current_image()
            self.clear_fields()
            
    def clear_fields(self):
        """Clear all input fields."""
        self.date_var.set("")
        self.time_var.set("")
        self.location_var.set("")
        self.species_var.set("")
        self.notes_text.delete(1.0, tk.END)
        self.ai_response_text.delete(1.0, tk.END)
        
    def encode_image_to_base64(self, image_path):
        """Convert image to base64 for API."""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None
            
    def analyze_current_image(self):
        """Analyze current image using GitHub Models API."""
        if not self.image_files:
            return
            
        image_path = os.path.join(IMAGES_FOLDER, self.image_files[self.current_image_index])
        self.status_label.config(text="Analyzing with AI...")
        self.root.update()
        
        # Encode image
        base64_image = self.encode_image_to_base64(image_path)
        if not base64_image:
            self.status_label.config(text="Error: Could not encode image")
            return
            
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json"
        }
        
        # Comprehensive prompt for camera trap analysis
        prompt = f"""Analyze this camera trap image and extract the following information:

1. ANIMALS: Identify any animals from this list: {', '.join(ANIMAL_SPECIES)}
   If you see an animal, specify which one(s).
   If no animals are visible, say "No animals detected".

2. DATE/TIME: Look for any timestamp or date/time display in the image.
   Common formats: DD/MM/YYYY HH:MM:SS or MM/DD/YYYY HH:MM:SS
   Extract both date and time if visible.

3. LOCATION: Look for any location identifier in the image.
   Common identifiers: FP1, FP2, FP3, Nische
   These might appear as text overlays.

4. CAMERA INFO: Note any camera model, serial number, or other metadata visible.

5. ENVIRONMENTAL CONDITIONS: Describe lighting, weather, visibility conditions.

Please provide your analysis in this format:
ANIMALS: [list any animals detected or "None"]
DATE: [DD/MM/YYYY or MM/DD/YYYY if visible]
TIME: [HH:MM:SS if visible] 
LOCATION: [FP1/FP2/FP3/Nische if visible]
CAMERA_INFO: [any camera metadata visible]
CONDITIONS: [brief description of conditions]
CONFIDENCE: [High/Medium/Low for overall analysis]

Be specific and only report what you can clearly see in the image."""

        # Try multiple API endpoints and models
        api_configs = [
            {"url": f"{GITHUB_API_BASE}/chat/completions", "model": "gpt-5"},
            {"url": f"{GITHUB_API_BASE}/chat/completions", "model": "gpt-4o"},
            {"url": "https://api.github.com/models/chat/completions", "model": "gpt-5"},
            {"url": "https://models.github.com/chat/completions", "model": "gpt-4o"}
        ]
        
        for config in api_configs:
            try:
                payload = {
                    "model": config["model"],
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
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
                
                print(f"Trying {config['url']} with model {config['model']}...")
                response = requests.post(config["url"], headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    
                    # Display AI response
                    self.ai_response_text.delete(1.0, tk.END)
                    self.ai_response_text.insert(1.0, ai_response)
                    
                    # Try to parse and auto-fill fields
                    self.parse_ai_response(ai_response)
                    
                    self.status_label.config(text=f"Analysis complete! (using {config['model']})")
                    return
                    
                else:
                    print(f"API Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"Error with {config['url']}: {e}")
                continue
                
        # If all endpoints failed
        self.status_label.config(text="Error: All API endpoints failed")
        self.ai_response_text.delete(1.0, tk.END)
        self.ai_response_text.insert(1.0, "API Error: Could not connect to GitHub Models.\n\nPlease check:\n1. GitHub token is valid\n2. Token has 'Models' scope\n3. Internet connection")
        
    def parse_ai_response(self, response):
        """Parse AI response and auto-fill fields."""
        try:
            # Extract date
            date_match = re.search(r'DATE:\s*([^\n]+)', response, re.IGNORECASE)
            if date_match:
                date_str = date_match.group(1).strip()
                if date_str and date_str.lower() != "not visible":
                    self.date_var.set(date_str)
            
            # Extract time
            time_match = re.search(r'TIME:\s*([^\n]+)', response, re.IGNORECASE)
            if time_match:
                time_str = time_match.group(1).strip()
                if time_str and time_str.lower() != "not visible":
                    self.time_var.set(time_str)
            
            # Extract location
            location_match = re.search(r'LOCATION:\s*([^\n]+)', response, re.IGNORECASE)
            if location_match:
                location_str = location_match.group(1).strip()
                if location_str and location_str.lower() != "not visible":
                    self.location_var.set(location_str)
            
            # Extract animals
            animals_match = re.search(r'ANIMALS:\s*([^\n]+)', response, re.IGNORECASE)
            if animals_match:
                animals_str = animals_match.group(1).strip()
                # Check if any of our species are mentioned
                for species in ANIMAL_SPECIES:
                    if species.lower() in animals_str.lower():
                        self.species_var.set(species)
                        break
                        
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            
    def save_and_next(self):
        """Save current data and move to next image."""
        # Collect data
        data = {
            'filename': self.image_files[self.current_image_index],
            'date': self.date_var.get(),
            'time': self.time_var.get(),
            'location': self.location_var.get(),
            'species': self.species_var.get(),
            'notes': self.notes_text.get(1.0, tk.END).strip(),
            'ai_response': self.ai_response_text.get(1.0, tk.END).strip(),
            'analyzed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.analyzed_data.append(data)
        
        # Save to Excel
        df = pd.DataFrame(self.analyzed_data)
        df.to_excel(OUTPUT_EXCEL, index=False)
        
        print(f"Saved analysis for {data['filename']}")
        
        # Move to next image
        if self.current_image_index < len(self.image_files) - 1:
            self.next_image()
        else:
            messagebox.showinfo("Complete", f"All images analyzed! Results saved to {OUTPUT_EXCEL}")
            
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageAnalyzer()
    app.run()
