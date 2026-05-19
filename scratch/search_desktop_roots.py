import os
from PIL import Image
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Search desktop root
desktop_dir = r"c:\Users\admin\Desktop"
print("=== Desktop Root Images ===")
for file in os.listdir(desktop_dir):
    if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        path = os.path.join(desktop_dir, file)
        print(f"File: {file}, Size: {os.path.getsize(path)}")

# Search oversoul root
oversoul_dir = r"c:\Users\admin\Desktop\antigravity\oversoul"
print("\n=== Oversoul Root Images ===")
for file in os.listdir(oversoul_dir):
    if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        path = os.path.join(oversoul_dir, file)
        print(f"File: {file}, Size: {os.path.getsize(path)}")
