from PIL import Image
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r"C:\Users\admin\.gemini\antigravity\brain\77e40789-ca60-4d23-8034-86ca0a33fca2\report_cover_1773740051983.png"

try:
    with Image.open(path) as img:
        print(f"Format: {img.format}")
        print(f"Size: {img.size}")
        print(f"Info: {img.info}")
except Exception as e:
    print(f"Error: {e}")
