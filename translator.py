import os
import json
import time
import fitz  # PyMuPDF
import google.generativeai as genai
from typing import List

# API 설정
API_KEY = os.getenv("GEMINI_API_KEY")

def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """PDF에서 텍스트를 페이지별로 추출합니다."""
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    return pages

def translate_chunk(chunk_text: str) -> str:
    """Gemini API를 사용하여 텍스트를 중학생 수준으로 번역합니다."""
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
랄프 왈도 에머슨의 'The Over-Soul' 원문입니다.
중학생도 읽자마자 감탄할 수 있도록 초쉬운 완역본으로 만들어주세요.

[필수 제어 고삐 (Harness)]
- 톤: 중학생도 한 번에 읽고 감동하는 다정한 에세이 톤.
- 규칙: 
  - 무겁고 딱딱한 철학 문장을 부드럽고 친절한 에세이처럼 새로 씁니다.
  - 번역투 문장(~함에 다름아니다, ~한 바이다 등)을 절대 사용하지 말고 자연스러운 한국어로 씁니다.
  - 에머슨의 깊은 통찰을 쉬운 비유를 들어 설명해줘도 좋습니다.
  - 마크다운 형식을 사용하여 가독성을 높이세요.

원문:
{chunk_text}
"""
    response = model.generate_content(prompt)
    return response.text

def main():
    pdf_path = "input/The-Over-Soul 에머슨 원문.pdf"
    state_path = "state.json"
    output_path = "translated_soul.md"
    
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} 파일을 찾을 수 없습니다.")
        return

    # 상태 로드 (Durable State)
    if os.path.exists(state_path):
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
    else:
        state = {"last_page": 0, "content": ""}

    pages = extract_text_from_pdf(pdf_path)
    total_pages = len(pages)
    
    current_page = state["last_page"]
    
    while current_page < total_pages:
        end_page = min(current_page + 3, total_pages)
        print(f"진행 중: {current_page + 1} ~ {end_page} 페이지 번역 중...")
        
        chunk_text = "\n".join(pages[current_page:end_page])
        
        try:
            translated = translate_chunk(chunk_text)
            
            state["content"] += translated + "\n\n"
            state["last_page"] = end_page
            
            # 상태 저장 (Durable State)
            with open(state_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            # 중간 결과 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(state["content"])
                
            current_page = end_page
            print(f"완료: {end_page}/{total_pages} 페이지 완료")
            time.sleep(2) # Rate limit 방지
            
        except Exception as e:
            print(f"오류 발생: {e}")
            break

    print("모든 번역 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()
