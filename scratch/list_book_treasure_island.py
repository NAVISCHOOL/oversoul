import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

book_dir = r"c:\Users\admin\Desktop\도서 보물섬"

if os.path.exists(book_dir):
    for root, dirs, files in os.walk(book_dir):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            print(f"Path: {file_path}")
            print(f"  Size: {size} bytes")
