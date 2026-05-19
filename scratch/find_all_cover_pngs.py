import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

search_dir = r"c:\Users\admin\Desktop\antigravity"

for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.lower() in ["cover.png", "cover.jpg", "cover.jpeg", "cover.webp"]:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            print(f"Path: {file_path}")
            print(f"  Size: {size} bytes")
