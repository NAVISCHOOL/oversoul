"""
Stage 2: 책추남 스타일 번역 에이전트 (translator.py)

각 청크를 개별적으로 번역합니다.
- 프롬프트 템플릿을 prompts/01_translate.md에서 로드
- 변경된 청크만 재번역 (해시 기반 캐시)
- 실패 시 자동 재시도 (최대 N회)
"""
import os
import json
import time
import google.generativeai as genai

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_prompt_template():
    """번역 프롬프트 템플릿을 로드합니다."""
    prompt_path = os.path.join(ROOT, "prompts", "01_translate.md")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def translate_chunk(chunk_text, model_name, prompt_template):
    """단일 청크를 번역합니다."""
    prompt = prompt_template.replace("{chunk_text}", chunk_text)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("  [안내] GEMINI_API_KEY가 설정되지 않았습니다.")
        print("         이 단계는 Antigravity 에이전트가 대화형으로 수행합니다.")
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text

def run(book, settings, state):
    """Stage 2 메인 실행 함수"""
    book_id = book["id"]
    chunks_dir = os.path.join(ROOT, "chunks", book_id)
    translated_dir = os.path.join(ROOT, "translated", book_id)
    model_name = settings.get("model_translate", "gemini-2.0-flash")
    max_retries = settings.get("max_retries", 3)
    
    os.makedirs(translated_dir, exist_ok=True)
    
    # 프롬프트 템플릿 로드
    prompt_template = load_prompt_template()
    
    # 청크 매니페스트 로드
    chunk_info = state.get("stages", {}).get("1", {}).get("chunks", {})
    if not chunk_info:
        print("  [오류] Stage 1이 먼저 실행되어야 합니다.")
        return False
    
    total = len(chunk_info)
    translated_count = 0
    skipped_count = 0
    
    for chunk_id, info in sorted(chunk_info.items()):
        chunk_path = os.path.join(chunks_dir, f"{chunk_id}.md")
        output_path = os.path.join(translated_dir, f"{chunk_id}.md")
        
        # 이미 번역 완료 + 원문 변경 없음 → 스킵
        if os.path.exists(output_path) and not info.get("changed", True):
            skipped_count += 1
            print(f"    [{chunk_id}] 캐시 히트 (스킵)")
            continue
        
        # 청크 읽기
        with open(chunk_path, 'r', encoding='utf-8') as f:
            chunk_text = f.read()
        
        # 번역 실행 (재시도 포함)
        for attempt in range(1, max_retries + 1):
            print(f"    [{chunk_id}] 번역 중... (시도 {attempt}/{max_retries})")
            
            result = translate_chunk(chunk_text, model_name, prompt_template)
            
            if result is None:
                # API 키 없음 → 수동 모드 표시
                print(f"    [{chunk_id}] 수동 번역 필요 (API 키 미설정)")
                break
            
            # 간단한 품질 검증: 결과가 너무 짧으면 재시도
            if len(result) < len(chunk_text) * 0.3:
                print(f"    [{chunk_id}] 번역 결과가 너무 짧음 → 재시도")
                time.sleep(2)
                continue
            
            # 번역 결과 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
            
            translated_count += 1
            print(f"    [{chunk_id}] 번역 완료 ({translated_count}/{total})")
            time.sleep(1)  # 레이트 리밋 방지
            break
    
    print(f"\n  번역 완료: {translated_count}개 신규, {skipped_count}개 캐시 활용")
    return True
