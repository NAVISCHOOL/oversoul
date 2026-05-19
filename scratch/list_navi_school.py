import os
from PIL import Image
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

search_dirs = [r"c:\Users\admin\Desktop\나비스쿨 출판사", r"c:\Users\admin\Desktop\썸네일 이미지"]

for sdir in search_dirs:
    if os.path.exists(sdir):
        print(f"--- Search in: {sdir} ---")
        for root, dirs, files in os.walk(sdir):
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
