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
                    lines = f.readlines()
                for idx, line in enumerate(lines):
                    if "generate_image" in line or "book_cover" in line.lower():
                        data = json.loads(line)
                        tool_calls = data.get("tool_calls", [])
                        for call in tool_calls:
                            if call.get("name") == "generate_image":
                                args = call.get("args", {})
                                image_name = args.get("ImageName", "")
                                prompt = args.get("Prompt", "")
                                if "cover" in image_name.lower() or "cover" in prompt.lower() or "sky" in prompt.lower() or "pray" in prompt.lower() or "에머슨" in prompt:
                                    print(f"File: {log_path} Line {idx+1}")
                                    print(f"  ImageName: {image_name}")
                                    print(f"  Prompt: {prompt}")
            except Exception as e:
                pass
