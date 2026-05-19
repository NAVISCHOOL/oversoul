import fitz
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf_path = r"c:\Users\admin\Downloads\초혼(超魂) — 책추남 편역 _ 에머슨.pdf"
out_path = r"c:\Users\admin\Desktop\antigravity\oversoul\images\cover.png"

try:
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    page = doc[0] # First page
    print(f"Rendering first page as image...")
    pix = page.get_pixmap(dpi=300) # Render at 300 DPI for high quality
    pix.save(out_path)
    print(f"Successfully extracted first page to: {out_path}")
except Exception as e:
    print(f"Error extracting cover: {e}")
