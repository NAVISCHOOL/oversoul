import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

log_path = r"C:\Users\admin\.gemini\antigravity\brain\0288e267-4399-438f-98a3-f47247c85d10\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "cover.png" in line.lower() or "copy-item" in line.lower() or "copy" in line.lower():
        try:
            data = json.loads(line)
            # Search in tool_calls
            tool_calls = data.get("tool_calls", [])
            for call in tool_calls:
                args = call.get("args", {})
                cmd = args.get("CommandLine", "")
                if "cover.png" in cmd.lower() or "cover" in cmd.lower() or "copy" in cmd.lower():
                    print(f"Line {idx+1}: {cmd}")
        except Exception as e:
            pass
