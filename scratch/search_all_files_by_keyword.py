import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

search_dirs = [r"c:\Users\admin\Downloads", r"c:\Users\admin\Desktop"]

keywords = ["내 안의 우주", "내안의우주", "내_안의_우주", "에머슨", "emerson", "초혼", "chohon", "oversoul", "over-soul"]

for sdir in search_dirs:
    if os.path.exists(sdir):
        print(f"--- Recursive Keyword Search in: {sdir} ---")
        for root, dirs, files in os.walk(sdir):
            for file in files:
                if any(k in file.lower() for k in keywords):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        print(f"Path: {file_path}")
                        print(f"  Size: {size} bytes")
                    except:
                        pass
