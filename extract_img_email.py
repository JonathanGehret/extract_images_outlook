import os
import extract_msg

input_folder = r"path\to\msg\files"
output_folder = r"path\to\output\images"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for file_name in os.listdir(input_folder):
    if file_name.lower().endswith(".msg"):
        msg = extract_msg.Message(os.path.join(input_folder, file_name))
        for attachment in msg.attachments:
            out_path = os.path.join(output_folder, attachment.longFilename)
            with open(out_path, "wb") as f:
                f.write(attachment.data)
            print(f"Extracted {attachment.longFilename}")
