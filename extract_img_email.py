
import os
import extract_msg
import re

input_folder = r"path\to\msg\files"
output_folder = r"path\to\output\images"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

import re

for file_name in os.listdir(input_folder):
    if file_name.lower().endswith(".msg"):
        match = re.search(r"\\((\\d+)\\)\\.msg$", file_name)
        if not match:
            print(f"Skipping file with unexpected name format: {file_name}")
            continue
        number = match.group(1)
        msg = extract_msg.Message(os.path.join(input_folder, file_name))
        if not msg.attachments:
            print(f"No attachments found in {file_name}")
            continue
        for idx, attachment in enumerate(msg.attachments, 1):
            # Get extension from original filename
            _, ext = os.path.splitext(attachment.longFilename)
            if len(msg.attachments) > 1:
                out_filename = f"fotofallen_2025_{number}_{idx}{ext}"
            else:
                out_filename = f"fotofallen_2025_{number}{ext}"
            out_path = os.path.join(output_folder, out_filename)
            with open(out_path, "wb") as f:
                f.write(attachment.data)
            print(f"Extracted {out_filename}")
