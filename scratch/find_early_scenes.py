import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

log_path = r"C:\Users\admin\.gemini\antigravity\brain\0288e267-4399-438f-98a3-f47247c85d10\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if "scene_ch" in line.lower() and "prompt" in line.lower():
            try:
                data = json.loads(line)
                tool_calls = data.get("tool_calls", [])
                for call in tool_calls:
                    if call.get("name") == "generate_image":
                        args = call.get("args", {})
                        print(f"Line {idx+1}: {args.get('ImageName')}")
                        print(f"  Prompt: {args.get('Prompt')}")
            except:
                pass
