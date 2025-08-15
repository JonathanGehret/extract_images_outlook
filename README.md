# Extract Images from Outlook

A Python script to extract image attachments from Microsoft Outlook `.msg` files.

## Description

This tool processes Outlook message files (`.msg` format) and extracts all attachments to a specified output directory. It's particularly useful for batch processing multiple email files and organizing their attachments.

## Features

- Processes all `.msg` files in a specified input directory
- Extracts all attachments from each email
- Automatically creates output directory if it doesn't exist
- Preserves original filenames of attachments
- Provides console output showing extraction progress

## Requirements

- Python 3.6 or higher
- extract-msg library

## Installation

1. Clone this repository:
```bash
git clone https://github.com/JonathanGehret/extract_images_outlook.git
cd extract_images_outlook
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Edit the `extract_img_email.py` file to specify your input and output paths:
   - Change `input_folder` to the path containing your `.msg` files
   - Change `output_folder` to where you want the extracted attachments saved

2. Run the script:
```bash
python extract_img_email.py
```

## Configuration

Before running the script, update these variables in `extract_img_email.py`:

```python
input_folder = r"path\to\msg\files"      # Directory containing .msg files
output_folder = r"path\to\output\images" # Directory for extracted attachments
```

## Example

```python
input_folder = r"/home/user/email_files"
output_folder = r"/home/user/extracted_attachments"
```


## File Structure

```
extract_images_outlook/
├── extract_img_email.py         # Extracts images from .msg files
├── rename_images_from_excel.py  # Renames images based on Excel sheet
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## Image Extraction Script

See above for usage of `extract_img_email.py`.

## Image Renaming Script

`rename_images_from_excel.py` renames extracted images according to information in an Excel table.

### Usage

1. Place your Excel file (e.g., `data.xlsx`) in a known location.
2. Edit the script to set:
   - `EXCEL_PATH` to your Excel file path
   - `IMAGES_FOLDER` to your extracted images folder
   - `CAMERA_NUMBER` to the correct camera (e.g., FP1, FP2)
3. Run the script:
   ```bash
   python3 rename_images_from_excel.py
   ```

The script will rename images in the format:
`yyyy.mm.dd-FPX-YYYYY Z.jpeg`
where:
- Date is taken from the Excel sheet and reformatted
- FPX is the camera number you set
- YYYYY is the animal name or code (customizable in the script)
- Z is a number if there are multiple images with the same name

### Requirements

- pandas
- openpyxl

Install all dependencies with:
```bash
pip3 install -r requirements.txt
```

## Notes

- The extraction script processes all files with `.msg` extension (case-insensitive)
- All attachment types are extracted, not just images
- Existing files in the output directory may be overwritten
- The script creates the output directory automatically if it doesn't exist
- The renaming script expects images to be named as extracted by the first script

## Troubleshooting

- Ensure you have the correct permissions to read the input files and write to the output directory
- Make sure the `.msg` files are not corrupted or password-protected
- Check that the file paths use the correct format for your operating system
- For the renaming script, ensure your Excel file columns match the expected names

## Dependencies

- [extract-msg](https://pypi.org/project/extract-msg/): Library for extracting data from Microsoft Outlook message files
- [pandas](https://pandas.pydata.org/): Data analysis library
- [openpyxl](https://openpyxl.readthedocs.io/): Excel file reader

## License

This project is open source. Feel free to modify and distribute as needed.

## Future Improvements

The renaming script will be enhanced to handle edge cases such as:
- Different numbering systems for different camera traps
- More flexible animal detection and naming
- Support for multiple file formats and data sources

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
