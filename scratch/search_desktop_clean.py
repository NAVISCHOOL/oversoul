import os
from PIL import Image
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

desktop_dir = r"c:\Users\admin\Desktop"

for root, dirs, files in os.walk(desktop_dir):
    # Exclude massive system or development directories
    if any(k in root.lower() for k in ["node_modules", ".venv", "env", "site-packages", "git", "피닉스", "ppt", "thesis"]):
        continue
    for file in files:
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 50000: # 50KB or larger
                    print(f"Path: {file_path}")
                    print(f"  Size: {size} bytes")
            except:
                pass
