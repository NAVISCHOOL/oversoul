import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

downloads_dir = r"c:\Users\admin\Downloads"

print("=== Downloads Korean Images ===")
for root, dirs, files in os.walk(downloads_dir):
    if "whisk downloads" in root.lower():
        continue
    for file in files:
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            if any('\u4e00' <= char <= '\u9fff' or '\uac00' <= char <= '\ud7a3' for char in file):
                path = os.path.join(root, file)
                print(f"Path: {path}")
                print(f"  Size: {os.path.getsize(path)} bytes")
