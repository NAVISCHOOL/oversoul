import json

log_path = r"C:\Users\admin\.gemini\antigravity\brain\0288e267-4399-438f-98a3-f47247c85d10\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

import sys
import io

# 콘솔 출력 인코딩을 utf-8로 강제 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for idx, line in enumerate(lines):
    if "cover.png" in line.lower() or "book_cover" in line.lower():
        try:
            data = json.loads(line)
            print(f"Line {idx+1}: type={data.get('type')}, created_at={data.get('created_at')}")
            def search_dict(d):
                if isinstance(d, dict):
                    for k, v in d.items():
                        if k.lower() in ["commandline", "prompt", "imagename", "targetfile", "imagepaths", "codecontent"]:
                            print(f"  {k}: {str(v)[:300]}")
                        else:
                            search_dict(v)
                elif isinstance(d, list):
                    for item in d:
                        search_dict(item)
            search_dict(data)
        except Exception as e:
            try:
                print(f"Line {idx+1} (raw): {line[:300]}")
            except:
                pass

