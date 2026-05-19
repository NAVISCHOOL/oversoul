from PIL import Image
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

folder = r"c:\Users\admin\Downloads\08_이미지_디자인"

for file in os.listdir(folder):
    if "다운로드" in file.lower() or "선묘" in file.lower():
        path = os.path.join(folder, file)
        try:
            with Image.open(path) as img:
                print(f"Path: {path}")
                print(f"  Format: {img.format}")
                print(f"  Size: {img.size}")
                print(f"  Modified Time: {os.path.getmtime(path)}")
        except Exception as e:
            print(f"Error for {file}: {e}")
