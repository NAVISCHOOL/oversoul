import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

downloads_dir = r"c:\Users\admin\Downloads"

if os.path.exists(downloads_dir):
    for file in os.listdir(downloads_dir):
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".pdf")):
            file_path = os.path.join(downloads_dir, file)
            size = os.path.getsize(file_path)
            print(f"File: {file}")
            print(f"  Size: {size} bytes")
