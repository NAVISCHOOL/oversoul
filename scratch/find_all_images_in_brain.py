import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

brain_dir = r"C:\Users\admin\.gemini\antigravity\brain"

for root, dirs, files in os.walk(brain_dir):
    for file in files:
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            if "cover" in file.lower() or "emerson" in file.lower():
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                print(f"Path: {file_path}")
                print(f"  Size: {size} bytes")

