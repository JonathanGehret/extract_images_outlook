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
├── extract_img_email.py    # Main script
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .gitignore            # Git ignore rules
```

## Notes

- The script processes all files with `.msg` extension (case-insensitive)
- All attachment types are extracted, not just images
- Existing files in the output directory may be overwritten
- The script creates the output directory automatically if it doesn't exist

## Troubleshooting

- Ensure you have the correct permissions to read the input files and write to the output directory
- Make sure the `.msg` files are not corrupted or password-protected
- Check that the file paths use the correct format for your operating system

## Dependencies

- [extract-msg](https://pypi.org/project/extract-msg/): Library for extracting data from Microsoft Outlook message files

## License

This project is open source. Feel free to modify and distribute as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
