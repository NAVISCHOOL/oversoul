import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

log_path = r"C:\Users\admin\.gemini\antigravity\brain\0288e267-4399-438f-98a3-f47247c85d10\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find any call to generate_image or book_cover prompt
# We can search for prompts or imagenames
matches = re.finditer(r'"Prompt"\s*:\s*"([^"]+)"', text)
for m in matches:
    prompt = m.group(1)
    # Print the prompt if it contains keywords
    if any(k in prompt.lower() for k in ["cover", "emerson", "sky", "pray", "에머슨", "우주", "기도", "하늘"]):
        print(f"Match: {prompt[:300]}")
