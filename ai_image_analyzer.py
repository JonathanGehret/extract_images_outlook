import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pytesseract
import re
import openai

# --- USER CONFIGURATION ---
IMAGES_FOLDER = "/home/jonathan/Downloads/2025_extracted_images"
OUTPUT_EXCEL = "analyzed_images.xlsx"
OPENAI_API_KEY = "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"  # Set your OpenAI API key
START_FROM_IMAGE = 1  # Set starting image number for continuation

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
        
        # Initialize OpenAI
        openai.api_key = OPENAI_API_KEY
        
        # Create GUI
        self.setup_gui()
        
    def get_image_files(self):
        """Get list of image files in the folder."""
        files = []
        for f in os.listdir(IMAGES_FOLDER):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                files.append(f)
        return sorted(files)
    
    def extract_metadata_ocr(self, image_path):
        """Extract timestamp and location from image using OCR."""
        try:
            # Use OCR to read text from bottom portion of image
            image = Image.open(image_path)
            width, height = image.size
            
            # Try different crops to find the metadata
            crops = [
                (0, height * 0.9, width, height),  # Bottom 10%
                (0, height * 0.85, width, height),  # Bottom 15%
                (0, height * 0.95, width, height),  # Bottom 5%
            ]
            
            all_text = ""
            for crop_box in crops:
                crop = image.crop(crop_box)
                # Convert to grayscale and increase contrast
                crop = crop.convert('L')
                # Scale up for better OCR
                crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
                
                text = pytesseract.image_to_string(crop, config='--psm 8')
                all_text += " " + text
            
            print(f"Combined OCR Text: {all_text.strip()}")
            
            # Extract patterns for camera location - look for specific known locations
            known_locations = ["FP1", "FP2", "FP3", "Nische"]
            location = ""
            
            # Check for each known location in the OCR text (case insensitive)
            for loc in known_locations:
                if loc.lower() in all_text.lower():
                    location = loc
                    break  # Take the first match found
            
            # If no exact match, try fuzzy matching for common OCR errors
            if not location:
                # FP1 might be read as FPI, F1, etc.
                if any(pattern in all_text.upper() for pattern in ["FPI", "FP1", "F1"]):
                    location = "FP1"
                elif any(pattern in all_text.upper() for pattern in ["FP2", "F2"]):
                    location = "FP2"
                elif any(pattern in all_text.upper() for pattern in ["FP3", "F3"]):
                    location = "FP3"
                elif any(pattern in all_text.upper() for pattern in ["NISCHE", "NPB"]):
                    location = "Nische"
            
            # If still no match, try pattern matching as fallback
            if not location:
                location_matches = re.findall(r'[FP]+\d+', all_text, re.IGNORECASE)
                if not location_matches:
                    # Try alternative patterns
                    location_matches = re.findall(r'[NLPF]+\s*[FP]*\d+', all_text, re.IGNORECASE)
                location = location_matches[0] if location_matches else ""
            
            # Extract time pattern - look for 6 consecutive digits (HHMMSS format)
            time_matches = re.findall(r'\d{6}', all_text)
            if time_matches:
                # Convert HHMMSS to HH:MM:SS
                time_raw = time_matches[0]
                time_str = f"{time_raw[:2]}:{time_raw[2:4]}:{time_raw[4:6]}"
            else:
                # Try traditional HH:MM:SS format
                time_matches = re.findall(r'\d{1,2}[:.]\d{2}[:.]\d{2}', all_text)
                time_str = time_matches[0] if time_matches else ""
            
            # Extract date pattern (various formats)
            date_matches = re.findall(r'\d{2}[-:.]\d{2}[-:.]\d{4}', all_text)
            if not date_matches:
                # Try different format
                date_matches = re.findall(r'\d{4}[-:.]\d{2}[-:.]\d{2}', all_text)
            date_str = date_matches[0] if date_matches else ""
            
            return location, time_str, date_str
            
        except Exception as e:
            print(f"OCR error: {e}")
            return "", "", ""
    
    def analyze_animals_ai(self, image_path):
        """Use OpenAI Vision API to identify animals in the image."""
        # For testing without API quota, return a mock result
        print("Note: Using mock AI analysis due to API quota.")
        return "Raven, Carrion Crow"  # Mock result
        
        # Uncomment below for real API call:
        """
        try:
            import base64
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
                
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-4o",  # Updated model name
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Analyze this camera trap image and identify any animals present. Choose only from this list: {', '.join(ANIMAL_SPECIES)}. List each animal you can clearly identify, separated by commas. If unsure or no animals visible, say 'None detected'."
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
                    max_tokens=300
                )
                
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"AI analysis error: {e}")
            return "Error in analysis"
        """
    
    def setup_gui(self):
        """Create the GUI interface."""
        self.root = tk.Tk()
        self.root.title("Camera Trap Image Analyzer")
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
        self.animals_var = tk.StringVar()
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
        self.location_var.set("")
        self.time_var.set("")
        self.date_var.set("")
        self.animals_text.delete(1.0, tk.END)
    
    def analyze_current_image(self):
        """Analyze the current image with OCR and AI."""
        image_file = self.image_files[self.current_image_index]
        image_path = os.path.join(IMAGES_FOLDER, image_file)
        
        # Extract metadata with OCR
        location, time_str, date_str = self.extract_metadata_ocr(image_path)
        
        # Fill in the form
        self.location_var.set(location)
        self.time_var.set(time_str)
        self.date_var.set(date_str)
        
        # Analyze animals with AI
        animals = self.analyze_animals_ai(image_path)
        self.animals_text.delete(1.0, tk.END)
        self.animals_text.insert(1.0, animals)
    
    def confirm_and_next(self):
        """Save current data and move to next image."""
        # Get data from form
        image_file = self.image_files[self.current_image_index]
        data = {
            'image_file': image_file,
            'location': self.location_var.get(),
            'time': self.time_var.get(),
            'date': self.date_var.get(),
            'animals': self.animals_text.get(1.0, tk.END).strip()
        }
        
        self.results.append(data)
        self.current_image_index += 1
        self.load_current_image()
    
    def skip_image(self):
        """Skip current image without saving data."""
        self.current_image_index += 1
        self.load_current_image()
    
    def save_results(self):
        """Save results to Excel file."""
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_excel(OUTPUT_EXCEL, index=False)
            print(f"Results saved to {OUTPUT_EXCEL}")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import pytesseract
        import openai
        from PIL import Image, ImageTk
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install with: pip install pytesseract openai pillow")
        exit(1)
    
    analyzer = ImageAnalyzer()
    analyzer.run()
