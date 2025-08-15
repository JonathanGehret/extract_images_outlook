import os
import pandas as pd
from collections import defaultdict

# --- USER CONFIGURATION ---
EXCEL_PATH = "/home/jonathan/development/extract_images_outlook/Fotofallendaten_2025.xlsx"  # Set to your Excel file path
IMAGES_FOLDER = "/home/jonathan/Downloads/2025_extracted_images"  # Folder with extracted images

def process_animals_from_row(row):
    """Process animal information from Excel row according to new specifications."""
    animals = []
    
    # Handle "Unbestimmt" column for Bartgeier
    if 'Unbestimmt' in row and str(row['Unbestimmt']).strip().upper() == 'BG':
        animals.append("Bartgeier_unbestimmt")
    
    # Handle Art 1 and Art 2 columns with quantities
    for art_col, count_col in [('Art 1', 'Anz. 1'), ('Art 2', 'Anz. 2')]:
        if art_col in row and pd.notna(row[art_col]):
            animal = str(row[art_col]).strip()
            count = ""
            
            # Get count if available
            if count_col in row and pd.notna(row[count_col]):
                try:
                    count_val = int(float(row[count_col]))
                    if count_val > 1:
                        count = f"_{count_val}"
                except (ValueError, TypeError):
                    pass
            
            # Handle special animal codes
            if animal.upper() == 'RK':
                animals.append(f"Rabenkrähe{count}")
            elif animal.lower() == 'rk':
                animals.append(f"Kolkrabe{count}")
            elif animal.upper() == 'RV':
                animals.append(f"Kolkrabe{count}")  # Assuming RV is also Kolkrabe
            elif animal.lower() in ['fuchs', 'marder']:
                animals.append(f"{animal.capitalize()}{count}")
            elif animal.lower() == 'gams':
                animals.append(f"Gämse{count}")
            elif animal:  # Any other animal
                animals.append(f"{animal}{count}")
    
    return animals

def get_special_names_from_row(row):
    """Get Generl and Luisa names if marked with X."""
    special_names = []
    
    # Check for Generl
    if 'Generl' in row and str(row['Generl']).strip().lower() == 'x':
        special_names.append("Generl")
    elif 'General' in row and str(row['General']).strip().lower() == 'x':
        special_names.append("Generl")
    
    # Check for Luisa
    if 'Luisa' in row and str(row['Luisa']).strip().lower() == 'x':
        special_names.append("Luisa")
    
    return special_names

def convert_date_to_new_format(date_str):
    """Convert date from DD.MM.YYYY to MM.DD.YY format."""
    try:
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
            print(f"Warning: Unrecognized date format: {date_str}")
            return str(date_str)

# Read Excel file
print(f"Reading Excel file: {EXCEL_PATH}")
try:
    excel_file = pd.ExcelFile(EXCEL_PATH)
    print(f"Available sheets: {excel_file.sheet_names}")
    
    # Process all sheets
    all_data = []
    for sheet_name in excel_file.sheet_names:
        if sheet_name in ['FP1', 'FP2', 'FP3', 'Nische']:
            print(f"Reading sheet: {sheet_name}")
            sheet_data = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)
            sheet_data.columns = sheet_data.columns.str.strip()
            
            # Add location column based on sheet name
            sheet_data['Location'] = sheet_name
            all_data.append(sheet_data)
    
    if not all_data:
        print("No valid sheets found!")
        exit(1)
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    print(f"Total rows across all sheets: {len(combined_data)}")

except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit(1)

# Clean column names and show available columns
combined_data.columns = combined_data.columns.str.strip()
print(f"Available columns: {list(combined_data.columns)}")

# Track duplicate names for numbering
name_counts = defaultdict(int)
successful_renames = 0
failed_renames = 0

print(f"\nProcessing {len(combined_data)} rows...")

for idx, row in combined_data.iterrows():
    try:
        # Get basic info
        nr = None
        for nr_col in ['Nr.', 'Nr', 'Nr. ']:
            if nr_col in row and pd.notna(row[nr_col]):
                nr = row[nr_col]
                break
                
        if nr is None:
            print(f"Warning: No number column found for row {idx}")
            continue
            
        nr = int(float(nr))  # Handle potential float numbers
        
        # Get location from the Location column we added
        location = row['Location'] if 'Location' in row else None
        
        if not location:
            print(f"Warning: No location found for row {idx}, skipping")
            continue
        
        # Get date
        date = row['Datum'] if 'Datum' in row else None
        if pd.isna(date):
            print(f"Warning: No date found for row {idx}, skipping")
            continue
            
        date_str = convert_date_to_new_format(date)
        
        # Get special names (Generl, Luisa)
        special_names = get_special_names_from_row(row)
        special_str = "_".join(special_names) if special_names else ""
        
        # Get animals
        animals = process_animals_from_row(row)
        animal_str = "_".join(animals) if animals else "Unknown"
        
        # Build new filename: location_NRNR_MM.DD.YY_[Generl_][Luisa_]Animal_count.jpeg
        if special_str:
            new_name = f"{location}_{nr:04d}_{date_str}_{special_str}_{animal_str}.jpeg"
        else:
            new_name = f"{location}_{nr:04d}_{date_str}_{animal_str}.jpeg"
        
        # Handle duplicates
        base_name = new_name[:-5]  # Remove .jpeg
        name_counts[base_name] += 1
        if name_counts[base_name] > 1:
            new_name = f"{base_name}_{name_counts[base_name]}.jpeg"
        
        # Find and rename the image file
        old_name = f"fotofallen_2025_{nr}.jpeg"
        old_path = os.path.join(IMAGES_FOLDER, old_name)
        
        if not os.path.exists(old_path):
            print(f"Image not found: {old_path}")
            failed_renames += 1
            continue
            
        new_path = os.path.join(IMAGES_FOLDER, new_name)
        
        # Create backup if needed
        if os.path.exists(new_path):
            print(f"Warning: Target file already exists: {new_name}")
            failed_renames += 1
            continue
            
        os.rename(old_path, new_path)
        print(f"✅ Renamed: {old_name} -> {new_name}")
        successful_renames += 1
        
    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        failed_renames += 1
        continue

print("\n🎉 Renaming complete!")
print(f"✅ Successful renames: {successful_renames}")
print(f"❌ Failed renames: {failed_renames}")
print(f"📊 Total processed: {successful_renames + failed_renames}")
