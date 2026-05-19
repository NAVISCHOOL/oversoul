import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

log_path = r"C:\Users\admin\.gemini\antigravity\brain\0288e267-4399-438f-98a3-f47247c85d10\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if "1778927581310" in line or "emerson_classic" in line.lower() or "v2" in line.lower():
            print(f"Line {idx+1}: {line[:300]}...")
