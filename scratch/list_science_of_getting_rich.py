import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

rich_dir = r"c:\Users\admin\Desktop\나비스쿨 출판사\부자가 되는 과학적인 방법"

if os.path.exists(rich_dir):
    for root, dirs, files in os.walk(rich_dir):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            print(f"Path: {file_path}")
            print(f"  Size: {size} bytes")
