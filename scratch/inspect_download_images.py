from PIL import Image
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

img1_path = r"c:\Users\admin\Downloads\Cinematic_photorealistic_magical_realism_image_of_-1779024572001.png"
img2_path = r"c:\Users\admin\Downloads\2026-05-17 22 30 02.jpg"

for path in [img1_path, img2_path]:
    try:
        with Image.open(path) as img:
            print(f"Path: {path}")
            print(f"  Format: {img.format}")
            print(f"  Size: {img.size}")
            # Try to get metadata/info
            print(f"  Info: {img.info}")
    except Exception as e:
        print(f"Error: {e}")
