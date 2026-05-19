import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

downloads_dir = r"c:\Users\admin\Downloads"

for root, dirs, files in os.walk(downloads_dir):
    for file in files:
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            print(f"Path: {file_path}")
            print(f"  Size: {size} bytes")
