import os
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

brain_dir = r"C:\Users\admin\.gemini\antigravity\brain"

for root, dirs, files in os.walk(brain_dir):
    for file in files:
        if file == "overview.txt":
            log_path = os.path.join(root, file)
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    for idx, line in enumerate(f):
                        if "generate_image" in line:
                            # Let's search for keywords
                            if any(k in line.lower() for k in ["cover", "emerson", "sky", "pray", "에머슨", "우주", "기도", "하늘"]):
                                print(f"File: {log_path} Line {idx+1}")
                                print(f"  {line[:400]}")
            except Exception as e:
                pass
