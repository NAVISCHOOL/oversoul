import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

search_dirs = [r"c:\Users\admin\Downloads", r"c:\Users\admin\Desktop"]

for sdir in search_dirs:
    if os.path.exists(sdir):
        print(f"--- Recursive Image Search in: {sdir} ---")
        for root, dirs, files in os.walk(sdir):
            # Exclude large development paths
            if any(k in root.lower() for k in ["node_modules", ".venv", "env", "site-packages", "git", "피닉스", "ppt", "thesis"]):
                continue
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    # Check if filename has Korean characters
                    if any('\u4e00' <= char <= '\u9fff' or '\uac00' <= char <= '\ud7a3' for char in file):
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            if size > 10000: # 10KB or larger
                                print(f"Path: {file_path}")
                                print(f"  Size: {size} bytes")
                        except:
                            pass
