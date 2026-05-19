import re
import json

log_path = r"C:\Users\admin\.gemini\antigravity\brain\0288e267-4399-438f-98a3-f47247c85d10\.system_generated\logs\overview.txt"

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "cover" in line.lower() or "png" in line.lower() or "generate_image" in line.lower():
        try:
            data = json.loads(line)
            # data를 문자열로 직렬화하여 키워드 매칭
            dump = json.dumps(data, ensure_ascii=False).lower()
            if "prompt" in dump or "imagename" in dump or "cover" in dump or "png" in dump:
                print(f"Line {idx+1}: type={data.get('type')}, created_at={data.get('created_at')}")
                # 재귀적으로 키/값을 찾아 출력
                def search_dict(d):
                    if isinstance(d, dict):
                        for k, v in d.items():
                            if k.lower() in ["commandline", "prompt", "imagename", "targetfile", "imagepaths"]:
                                print(f"  {k}: {v}")
                            else:
                                search_dict(v)
                    elif isinstance(d, list):
                        for item in d:
                            search_dict(item)
                search_dict(data)
        except Exception as e:
            pass

