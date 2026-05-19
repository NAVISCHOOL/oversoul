"""
Stage 3: 책추남 해설·해제 생성 에이전트 (commentator.py)

번역 완료된 본문을 읽고 책추남 스타일의 해설 콘텐츠를 생성합니다.
- 서문, 심층 해설 4종, 해제, 나비 퀘스트, 부록 등 7개 섹션
- 나비스쿨/피닉스 퓨처 스쿨 소개 자동 삽입
"""
import os
import google.generativeai as genai

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_translated_text(book_id):
    """번역된 청크들을 합쳐서 전체 번역본을 구성합니다."""
    translated_dir = os.path.join(ROOT, "translated", book_id)
    if not os.path.exists(translated_dir):
        return None
    
    chunks = sorted(os.listdir(translated_dir))
    full_text = ""
    for chunk_file in chunks:
        if chunk_file.endswith('.md'):
            path = os.path.join(translated_dir, chunk_file)
            with open(path, 'r', encoding='utf-8') as f:
                full_text += f.read() + "\n\n"
    return full_text

def load_navieschool_intro():
    """나비스쿨/피닉스 퓨처 스쿨 소개문을 로드합니다."""
    intro_path = os.path.join(ROOT, "prompts", "05_navieschool_intro.md")
    if os.path.exists(intro_path):
        with open(intro_path, 'r', encoding='utf-8') as f:
            # 프롬프트 지시문 제거, 순수 소개문만 추출
            content = f.read()
            # "## 삽입할 소개문" 이후 부분만 추출
            marker = "## 삽입할 소개문"
            if marker in content:
                content = content[content.index(marker) + len(marker):]
            return content.strip()
    return ""

def run(book, settings, state):
    """Stage 3 메인 실행 함수"""
    book_id = book["id"]
    commentary_dir = os.path.join(ROOT, "commentary", book_id)
    model_name = settings.get("model_commentary", "gemini-2.0-flash")
    
    os.makedirs(commentary_dir, exist_ok=True)
    
    # 번역본 로드
    translated_text = load_translated_text(book_id)
    if not translated_text:
        print("  [오류] Stage 2에서 생성된 번역 파일이 없습니다.")
        return False
    
    # 프롬프트 로드
    prompt_path = os.path.join(ROOT, "prompts", "02_commentary.md")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # API 키 확인
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("  [안내] GEMINI_API_KEY가 설정되지 않았습니다.")
        print("         이 단계는 Antigravity 에이전트가 대화형으로 수행합니다.")
        print(f"         프롬프트 템플릿: prompts/02_commentary.md")
        print(f"         번역본 위치: translated/{book_id}/")
        
        # 나비스쿨 소개문은 별도 저장
        intro = load_navieschool_intro()
        if intro:
            intro_path = os.path.join(commentary_dir, "navieschool_intro.md")
            with open(intro_path, 'w', encoding='utf-8') as f:
                f.write(intro)
            print(f"  나비스쿨 소개문 저장: {intro_path}")
        
        return True
    
    # API 기반 생성
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # 번역본이 너무 길면 앞부분 4000자만 전송 (토큰 절약)
    input_text = translated_text[:8000] if len(translated_text) > 8000 else translated_text
    prompt = prompt_template.replace("{translated_text}", input_text)
    
    print("  책추남 해설 생성 중...")
    response = model.generate_content(prompt)
    
    if response and response.text:
        # 해설 저장
        output_path = os.path.join(commentary_dir, "commentary.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # 나비스쿨 소개문 저장
        intro = load_navieschool_intro()
        if intro:
            intro_path = os.path.join(commentary_dir, "navieschool_intro.md")
            with open(intro_path, 'w', encoding='utf-8') as f:
                f.write(intro)
        
        print(f"  해설 생성 완료: {output_path}")
        return True
    
    print("  [오류] 해설 생성 실패")
    return False
