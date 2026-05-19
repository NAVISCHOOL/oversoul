import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

gemini_dir = r"C:\Users\admin\.gemini\antigravity"

for root, dirs, files in os.walk(gemini_dir):
    for file in files:
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            if any(k in file.lower() for k in ["cover", "emerson", "sky", "pray", "에머슨", "우주", "기도", "하늘"]):
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                print(f"Path: {file_path}")
                print(f"  Size: {size} bytes")
