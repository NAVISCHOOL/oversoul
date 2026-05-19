import os
from PIL import Image
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

search_dir = r"c:\Users\admin\Desktop\antigravity"

for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            file_path = os.path.join(root, file)
            try:
                with Image.open(file_path) as img:
                    print(f"Path: {file_path}")
                    print(f"  Size: {os.path.getsize(file_path)} bytes")
                    print(f"  Dims: {img.size}")
            except Exception as e:
                pass
