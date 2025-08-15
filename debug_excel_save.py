#!/usr/bin/env python3
"""
Debug script to test Excel saving with the same method as the main application.
"""

import pandas as pd
import os

OUTPUT_EXCEL = "analyzed_images.xlsx"

# Sample data that mimics what the GUI would save (with correct structure)
sample_results = [
    {
        'Nr. ': 1,
        'Standort': 'FP1',
        'Datum': '01-08-2025',
        'Uhrzeit': '10:04:03',
        'Dagmar': '',
        'Recka': '',
        'Unbestimmt': '',
        'Aktivität': 'Walking',
        'Art 1': '',
        'Anzahl 1': '',
        'Art 2': '',
        'Anzahl 2': '',
        'Interaktion': 'Territorial',
        'Sonstiges': 'Clear weather',
        'Korrektur': ''
    },
    {
        'Nr. ': 2,
        'Standort': 'FP3',
        'Datum': '28-08-2025',
        'Uhrzeit': '08:27:03',
        'Dagmar': '',
        'Recka': '',
        'Unbestimmt': '',
        'Aktivität': 'Feeding',
        'Art 1': '',
        'Anzahl 1': '',
        'Art 2': '',
        'Anzahl 2': '',
        'Interaktion': 'Peaceful',
        'Sonstiges': 'Morning light',
        'Korrektur': ''
    }
]

def debug_save_results(results):
    """Debug version of save_results with detailed logging."""
    print(f"Starting save_results with {len(results)} results")
    
    if not results:
        print("No results to save")
        return
        
    # Group results by location (Standort)
    location_groups = {}
    for result in results:
        location = result.get('Standort', 'Unknown')
        if location not in location_groups:
            location_groups[location] = []
        location_groups[location].append(result)
    
    print(f"Location groups: {list(location_groups.keys())}")
    
    # Load existing Excel file or create new one
    try:
        # Load existing Excel file
        with pd.ExcelFile(OUTPUT_EXCEL) as xls:
            existing_sheets = xls.sheet_names
        print(f"Found existing Excel file with sheets: {existing_sheets}")
    except FileNotFoundError:
        print("Excel file not found, will create new sheets")
        existing_sheets = []
    
    # Save to appropriate sheets
    try:
        print(f"Opening Excel writer with mode='a', if_sheet_exists='overlay'")
        with pd.ExcelWriter(OUTPUT_EXCEL, mode='a' if existing_sheets else 'w', 
                           if_sheet_exists='overlay' if existing_sheets else None) as writer:
            
            for location, data_list in location_groups.items():
                print(f"\nProcessing location: {location}")
                if location and location in ['FP1', 'FP2', 'FP3', 'Nische']:
                    df = pd.DataFrame(data_list)
                    print(f"Created DataFrame with {len(df)} rows")
                    print(f"DataFrame columns: {list(df.columns)}")
                    
                    # Try to load existing data from this sheet
                    try:
                        if location in existing_sheets:
                            print(f"Reading existing {location} sheet")
                            existing_df = pd.read_excel(OUTPUT_EXCEL, sheet_name=location)
                            print(f"Found {len(existing_df)} existing rows")
                            # Append new data to existing
                            df = pd.concat([existing_df, df], ignore_index=True)
                            print(f"Combined DataFrame now has {len(df)} rows")
                        else:
                            print(f"Creating new {location} sheet")
                    except Exception as e:
                        print(f"Error reading existing {location} sheet: {e}")
                    
                    # Write to sheet named after location
                    print(f"Writing DataFrame to {location} sheet")
                    df.to_excel(writer, sheet_name=location, index=False)
                    print(f"✅ Successfully saved {len(data_list)} images to {location} sheet")
                else:
                    print(f"❌ Skipping unknown location: {location}")
                    
    except Exception as e:
        print(f"❌ Error during Excel writing: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"Results should be saved to {OUTPUT_EXCEL}")

if __name__ == "__main__":
    print("=== Debug Excel Save Test ===")
    debug_save_results(sample_results)
    
    print("\n=== Verifying saved data ===")
    try:
        xl_file = pd.ExcelFile(OUTPUT_EXCEL)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        for sheet in xl_file.sheet_names:
            df = pd.read_excel(OUTPUT_EXCEL, sheet_name=sheet)
            print(f"\n{sheet} sheet ({len(df)} rows):")
            if not df.empty:
                print(df.to_string(index=False))
            else:
                print("  (Empty)")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
