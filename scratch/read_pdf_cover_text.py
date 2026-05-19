import fitz
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf1 = r"c:\Users\admin\Downloads\초혼(超魂) — 책추남 편역 _ 에머슨.pdf"
pdf2 = r"c:\Users\admin\Desktop\도서 보물섬\[책추남 편역] 초영혼 (The Over-Soul) - 100% 통합 완역본.pdf"

for path in [pdf1, pdf2]:
    try:
        print(f"=== Opening PDF: {path} ===")
        doc = fitz.open(path)
        print(f"Number of pages: {len(doc)}")
        page = doc[0]
        text = page.get_text()
        print(f"First page text:\n{text}")
        print("="*40)
    except Exception as e:
        print(f"Error: {e}")
