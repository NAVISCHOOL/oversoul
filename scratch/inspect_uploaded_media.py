from PIL import Image
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

img_path = r"C:\Users\admin\.gemini\antigravity\brain\0288e267-4399-438f-98a3-f47247c85d10\uploaded_media_1778908814125.img"

try:
    with Image.open(img_path) as img:
        print(f"Format: {img.format}")
        print(f"Size: {img.size}")
        print(f"Mode: {img.mode}")
except Exception as e:
    print(f"Error reading image: {e}")
