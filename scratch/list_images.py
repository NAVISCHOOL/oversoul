import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

img_dir = r"c:\Users\admin\Desktop\antigravity\oversoul\images"

for file in os.listdir(img_dir):
    if file.lower().endswith((".png", ".jpg", ".jpeg")):
        file_path = os.path.join(img_dir, file)
        print(f"File: {file}")
        print(f"  Size: {os.path.getsize(file_path)} bytes")
        print(f"  Modified: {os.path.getmtime(file_path)}")
