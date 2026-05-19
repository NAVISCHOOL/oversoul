import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

search_dirs = [r"c:\Users\admin\Downloads", r"c:\Users\admin\Desktop"]

for sdir in search_dirs:
    if os.path.exists(sdir):
        for root, dirs, files in os.walk(sdir):
            for file in files:
                if any(k in file for k in ["내", "안", "우주", "초영혼", "초혼"]):
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    print(f"Path: {file_path}")
                    print(f"  Size: {size} bytes")
