import sys
import subprocess
import fitz

def test_pagination_options():
    with open('pdf_builder.py', 'r', encoding='utf-8') as f:
        code = f.read()
        
    code_test = code.replace(
        'fontSize=10.5 if mode == "kmong" else 9.5',
        'fontSize=11.5 if mode == "kmong" else 10.5'
    )
    code_test = code_test.replace(
        'leading=18 if mode == "kmong" else 16',
        'leading=20 if mode == "kmong" else 18'
    )
    code_test = code_test.replace(
        'spaceAfter=12,',
        'spaceAfter=14,'
    )
    code_test = code_test.replace(
        'topMargin=20 * mm,\n            bottomMargin=20 * mm',
        'topMargin=22 * mm,\n            bottomMargin=22 * mm'
    )
    
    with open('pdf_builder_test.py', 'w', encoding='utf-8') as f:
        f.write(code_test)
        
    subprocess.run([sys.executable, 'pdf_builder_test.py'])
    
    doc_kmong = fitz.open('Emerson_Universe_Kmong_Ebook.pdf')
    doc_bookk = fitz.open('Emerson_Universe_Bookk_POD.pdf')
    print(f"RESULTS - Kmong: {doc_kmong.page_count} pages, Bookk: {doc_bookk.page_count} pages")

if __name__ == "__main__":
    test_pagination_options()
