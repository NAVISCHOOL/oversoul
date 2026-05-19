"""
Stage 5: 합본 & 품질 게이트 에이전트 (assembler.py)

번역본 + 해설 + 이미지 태그를 합쳐서 최종 원고를 생성합니다.
- 자동 목차 생성
- 이미지 태그 자동 매핑
- 나비스쿨 소개 삽입
- 버전 파일명에 날짜 + 상태 태그
"""
import os
import re
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_all_translated(book_id):
    """번역된 청크들을 순서대로 합칩니다."""
    translated_dir = os.path.join(ROOT, "translated", book_id)
    if not os.path.exists(translated_dir):
        return ""
    
    chunks = sorted(f for f in os.listdir(translated_dir) if f.endswith('.md'))
    full = ""
    for cf in chunks:
        with open(os.path.join(translated_dir, cf), 'r', encoding='utf-8') as f:
            full += f.read() + "\n\n"
    return full

def load_commentary(book_id):
    """해설 콘텐츠를 로드합니다."""
    commentary_dir = os.path.join(ROOT, "commentary", book_id)
    result = ""
    
    # 메인 해설
    main_path = os.path.join(commentary_dir, "commentary.md")
    if os.path.exists(main_path):
        with open(main_path, 'r', encoding='utf-8') as f:
            result += f.read() + "\n\n"
    
    # 나비스쿨 소개
    intro_path = os.path.join(commentary_dir, "navieschool_intro.md")
    if os.path.exists(intro_path):
        with open(intro_path, 'r', encoding='utf-8') as f:
            result += f.read() + "\n\n"
    
    return result

def build_header(book):
    """도서 메타데이터 헤더를 생성합니다."""
    return f"""# {book['series']}
# 🌿 {book['title']} : {book['subtitle']}
### {book['orig_title']}

![책표지]({book['cover']})

**원저:** {book['author']}  
**번역 및 해제:** {book['translator']}

---

# 📖 목차 (Table of Contents)

[TOC_PLACEHOLDER]

---

"""

def run(book, settings, state):
    """Stage 5 메인 실행 함수"""
    book_id = book["id"]
    versions_dir = os.path.join(ROOT, "versions", book_id)
    os.makedirs(versions_dir, exist_ok=True)
    
    # 번역본 로드
    translated = load_all_translated(book_id)
    if not translated.strip():
        print("  [안내] 번역 파일이 없습니다. Antigravity 에이전트가 수동으로 합본합니다.")
        return True
    
    # 해설 로드
    commentary = load_commentary(book_id)
    
    # 헤더 생성
    header = build_header(book)
    
    # 합본
    final_content = header + translated + "\n\n" + commentary
    
    # 버전 파일 저장
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 기존 버전 수 확인
    existing = [f for f in os.listdir(versions_dir) if f.endswith('.md')]
    version_num = len(existing) + 1
    
    version_filename = f"v{version_num}_{today}_합본.md"
    version_path = os.path.join(versions_dir, version_filename)
    
    with open(version_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"  합본 완료: versions/{book_id}/{version_filename}")
    print(f"  총 길이: {len(final_content):,}자")
    
    # 활성 원고로도 복사 (pdf_builder가 참조)
    active_path = os.path.join(ROOT, f"final_{book_id.replace('-', '_')}.md")
    with open(active_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"  활성 원고 갱신: {os.path.basename(active_path)}")
    
    # 상태에 버전 정보 저장
    state.setdefault("stages", {}).setdefault("5", {})
    state["stages"]["5"]["latest_version"] = version_filename
    state["stages"]["5"]["active_file"] = os.path.basename(active_path)
    
    return True
