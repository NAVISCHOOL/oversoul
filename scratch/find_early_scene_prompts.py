import re
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

log_path = r"C:\Users\admin\.gemini\antigravity\brain\0288e267-4399-438f-98a3-f47247c85d10\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for generate_image tool calls inside the log text
matches = re.finditer(r'("name"\s*:\s*"generate_image".*?})', text, re.DOTALL)
for m in matches:
    content = m.group(1)
    if any(k in content for k in ["scene_ch1", "scene_ch2", "scene_ch3", "scene_ch4", "scene_ch5", "scene_ch6"]):
        print(content[:500])
