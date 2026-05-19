import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

brain_dir = r"C:\Users\admin\.gemini\antigravity\brain"

if os.path.exists(brain_dir):
    for sub in os.listdir(brain_dir):
        sub_path = os.path.join(brain_dir, sub)
        if os.path.isdir(sub_path):
            print(f"Brain Subdir: {sub}")
            # Check for any png/jpg in it
            for root, dirs, files in os.walk(sub_path):
                for file in files:
                    if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        file_path = os.path.join(root, file)
                        print(f"  Image: {file} ({os.path.getsize(file_path)} bytes)")
