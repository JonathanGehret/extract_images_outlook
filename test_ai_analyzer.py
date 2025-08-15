import os
import pandas as pd
from PIL import Image
import pytesseract
import re
import base64
import openai

# --- USER CONFIGURATION ---
IMAGES_FOLDER = "/home/jonathan/Downloads/2025_extracted_images"
OUTPUT_EXCEL = "analyzed_images.xlsx"
OPENAI_API_KEY = "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"
START_FROM_IMAGE = 1

# Animal species list for AI to choose from
ANIMAL_SPECIES = [
    "Bearded Vulture", "Golden Eagle", "Raven", "Carrion Crow", 
    "Hooded Crow", "Jackdaw", "Fox", "Chamois", "Ibex", "Marmot"
]

def get_image_files():
    """Get list of image files in the folder."""
    files = []
    for f in os.listdir(IMAGES_FOLDER):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            files.append(f)
    return sorted(files)

def extract_metadata_ocr(image_path):
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
            print(f"OCR Text from crop: {text.strip()}")
        
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
            if time_matches:
                time_str = time_matches[0]
            else:
                # Handle OCR errors where digits are missing (e.g., "809851" for "09:09:51")
                # Look for 5-6 digit sequences that could be time
                potential_times = re.findall(r'\d{5,6}', all_text)
                for pot_time in potential_times:
                    if len(pot_time) == 6:
                        # Standard HHMMSS
                        time_str = f"{pot_time[:2]}:{pot_time[2:4]}:{pot_time[4:6]}"
                        break
                    elif len(pot_time) == 5:
                        # Missing first digit, prepend 0 (e.g., "80951" -> "08:09:51")
                        padded_time = "0" + pot_time
                        time_str = f"{padded_time[:2]}:{padded_time[2:4]}:{padded_time[4:6]}"
                        break
                else:
                    time_str = ""
        
        # Extract date pattern (various formats)
        date_matches = re.findall(r'\d{2}[-:.]\d{2}[-:.]\d{4}', all_text)
        if not date_matches:
            # Try different format (YYYY-MM-DD)
            date_matches = re.findall(r'\d{4}[-:.]\d{2}[-:.]\d{2}', all_text)
        if not date_matches:
            # Handle OCR errors where hyphens are missing (e.g., "2207-2025" for "22-07-2025")
            incomplete_dates = re.findall(r'\d{4}-\d{4}', all_text)
            for incomplete in incomplete_dates:
                # If we find pattern like "2207-2025", convert to "22-07-2025"
                if len(incomplete) == 9:  # Format: "DDMM-YYYY"
                    day = incomplete[:2]
                    month = incomplete[2:4]
                    year = incomplete[5:]
                    date_matches = [f"{day}-{month}-{year}"]
                    break
        if not date_matches:
            # Try even more flexible patterns for 8-digit dates
            eight_digit_dates = re.findall(r'\d{8}', all_text)
            for date_str in eight_digit_dates:
                # Could be DDMMYYYY or YYYYMMDD
                if date_str.startswith('20'):  # Likely YYYYMMDD
                    year = date_str[:4]
                    month = date_str[4:6]
                    day = date_str[6:8]
                    date_matches = [f"{day}-{month}-{year}"]
                    break
                elif len(date_str) == 8:  # Likely DDMMYYYY
                    day = date_str[:2]
                    month = date_str[2:4]
                    year = date_str[4:]
                    if int(year) > 2000:  # Sanity check
                        date_matches = [f"{day}-{month}-{year}"]
                        break
        date_str = date_matches[0] if date_matches else ""
        
        return location, time_str, date_str
        
    except Exception as e:
        print(f"OCR error: {e}")
        return "", "", ""

def analyze_animals_ai(image_path):
    """Use OpenAI Vision API to identify animals in the image."""
    # For testing without API quota, return a mock result
    print("Note: Using mock AI analysis due to API quota. Replace with real API call when ready.")
    return "Raven, Carrion Crow"  # Mock result
    
    # Uncomment below for real API call:
    """
    try:
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

def test_single_image():
    """Test the analysis on a single image."""
    image_files = get_image_files()
    if not image_files:
        print("No image files found in the folder!")
        return
    
    # Test with first image
    image_file = image_files[0]
    image_path = os.path.join(IMAGES_FOLDER, image_file)
    
    print(f"Testing with image: {image_file}")
    print("=" * 50)
    
    # Test OCR
    print("Testing OCR...")
    location, time_str, date_str = extract_metadata_ocr(image_path)
    print(f"Location: {location}")
    print(f"Time: {time_str}")
    print(f"Date: {date_str}")
    print()
    
    # Test AI analysis
    print("Testing AI analysis...")
    animals = analyze_animals_ai(image_path)
    print(f"Animals detected: {animals}")
    
    return {
        'image_file': image_file,
        'location': location,
        'time': time_str,
        'date': date_str,
        'animals': animals
    }

if __name__ == "__main__":
    print("Testing AI Image Analyzer...")
    result = test_single_image()
    if result:
        print("\nTest completed successfully!")
        print("Result:", result)
