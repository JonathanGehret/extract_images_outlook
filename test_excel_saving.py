#!/usr/bin/env python3
"""
Test script to verify Excel saving functionality with dummy data
"""
import pandas as pd
import os

# Test data for different locations
test_data = {
    'FP1': [
        {'Nr': '001', 'Standort': 'FP1', 'Datum': '01-08-2025', 'Uhrzeit': '08:15:30', 
         'Aktivät': 'Feeding', 'Interaktion': '', 'Sonstiges': 'Clear weather', 'Unbestimmt': ''},
        {'Nr': '002', 'Standort': 'FP1', 'Datum': '01-08-2025', 'Uhrzeit': '09:22:15', 
         'Aktivät': 'Flying', 'Interaktion': 'Territorial', 'Sonstiges': 'Good visibility', 'Unbestimmt': 'Bg'},
    ],
    'FP2': [
        {'Nr': '003', 'Standort': 'FP2', 'Datum': '02-08-2025', 'Uhrzeit': '10:45:00', 
         'Aktivät': 'Resting', 'Interaktion': '', 'Sonstiges': 'Foggy', 'Unbestimmt': ''},
    ],
    'FP3': [
        {'Nr': '004', 'Standort': 'FP3', 'Datum': '03-08-2025', 'Uhrzeit': '14:30:45', 
         'Aktivät': 'Walking', 'Interaktion': 'Feeding together', 'Sonstiges': 'Rain', 'Unbestimmt': ''},
    ]
}

def test_excel_saving():
    """Test the Excel saving functionality"""
    output_file = "test_analyzed_images.xlsx"
    
    # Remove existing test file
    if os.path.exists(output_file):
        os.remove(output_file)
    
    print("Testing Excel saving functionality...")
    
    # Save data to different sheets
    with pd.ExcelWriter(output_file) as writer:
        for location, data_list in test_data.items():
            df = pd.DataFrame(data_list)
            df.to_excel(writer, sheet_name=location, index=False)
            print(f"Created {location} sheet with {len(data_list)} rows")
    
    # Verify the file was created
    if os.path.exists(output_file):
        print(f"\n✅ Successfully created {output_file}")
        
        # Read and display the content
        with pd.ExcelFile(output_file) as xls:
            print(f"📄 Available sheets: {xls.sheet_names}")
            
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                print(f"\n📊 {sheet} sheet content:")
                print(df.to_string(index=False))
    else:
        print("❌ Failed to create Excel file")

if __name__ == "__main__":
    test_excel_saving()
