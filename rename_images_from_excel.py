import os
import pandas as pd
from collections import defaultdict

# --- USER CONFIGURATION ---
EXCEL_PATH = "/home/jonathan/development/extract_images_outlook/Fotofallendaten_2022.xlsx"  # Set to your Excel file path
IMAGES_FOLDER = "/home/jonathan/Downloads/2025_extracted_images"  # Folder with extracted images
CAMERA_NUMBER = "FP1"  # Set camera number manually (e.g., FP1, FP2, etc.)

# Animal code mapping (customize as needed)
ANIMAL_CODES = {
    "Dagmar": "Dagmar",  # Bearded vulture name example
    "Kolkrabe": "KR",
    "Rabenkrähe": "RK",
    "Fuchs": "Fuchs",
    "Gams": "Gams",
    # Add more as needed
}

# Read Excel
sheet = pd.read_excel(EXCEL_PATH)
sheet.columns = sheet.columns.str.strip()  # Strip all column names

# Track duplicate names for numbering
name_counts = defaultdict(int)

for idx, row in sheet.iterrows():
    nr = row["Nr."]  # Now always use stripped column name
    date = row["Datum"]
    # Robust date handling
    try:
        # If it's a pandas Timestamp or datetime object
        date_str = pd.to_datetime(date).strftime("%Y.%m.%d")
    except Exception:
        # If it's a string, try to split
        parts = str(date).split(".")
        if len(parts) == 3:
            day, month, year = parts
            date_str = f"{year}.{month}.{day}"
        else:
            print(f"Warning: Unrecognized date format for row {idx}: {date}")
            date_str = str(date)

    # Get animal names/codes
    animals = []
    # Example: check columns for animal presence
    for col in ANIMAL_CODES:
        if col in row and str(row[col]).strip().lower() == "x":
            animals.append(ANIMAL_CODES[col])
    # Also check 'Art 1' and 'Art 2' columns for animal type
    for art_col in ["Art 1", "Art 2"]:
        if art_col in row and pd.notna(row[art_col]):
            animal = row[art_col]
            if animal in ANIMAL_CODES:
                animals.append(ANIMAL_CODES[animal])
            else:
                animals.append(str(animal))
    # Remove duplicates
    animals = list(dict.fromkeys(animals))
    animal_str = "-".join(animals) if animals else "Unknown"

    # Build new filename
    base_name = f"{date_str}-{CAMERA_NUMBER}-{animal_str}"
    name_counts[base_name] += 1
    if name_counts[base_name] > 1:
        new_name = f"{base_name} {name_counts[base_name]}.jpeg"
    else:
        new_name = f"{base_name}.jpeg"

    # Find image file by number
    old_name = f"fotofallen_2025_{nr}.jpeg"
    old_path = os.path.join(IMAGES_FOLDER, old_name)
    if not os.path.exists(old_path):
        print(f"Image not found: {old_path}")
        continue
    new_path = os.path.join(IMAGES_FOLDER, new_name)
    os.rename(old_path, new_path)
    print(f"Renamed {old_name} -> {new_name}")

print("Done renaming images.")
