import os
from PIL import Image
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

search_dirs = [r"c:\Users\admin\Desktop"]

for sdir in search_dirs:
    if os.path.exists(sdir):
        print(f"--- Recursive Search in: {sdir} ---")
        for root, dirs, files in os.walk(sdir):
            # Skip node_modules or virtual environments to speed up and prevent spam
            if any(k in root.lower() for k in ["node_modules", ".venv", "env", "site-packages", "git"]):
                continue
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        # We only care about high-res images (greater than 100KB)
                        if size > 100000:
                            print(f"Path: {file_path}")
                            print(f"  Size: {size} bytes")
                    except Exception as e:
                        pass
