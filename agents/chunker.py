"""
Stage 1: 원문 청크 분할 에이전트 (chunker.py)

영문 원문을 의미 단위(챕터/섹션)로 분할합니다.
- 마크다운 헤더(##, ###) 기준 분할
- PDF인 경우 텍스트 추출 후 분할
- 각 청크에 해시값 부여 → 변경 감지용
"""
import os
import re
import json
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extract_text_from_pdf(pdf_path):
    """PDF에서 텍스트를 추출합니다."""
    import fitz
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text

def extract_text_from_md(md_path):
    """마크다운 파일에서 텍스트를 읽습니다."""
    with open(md_path, 'r', encoding='utf-8') as f:
        return f.read()

def split_into_chunks(text, max_tokens=3000):
    """텍스트를 의미 단위로 분할합니다."""
    # 마크다운 헤더(## 또는 ###) 기준으로 1차 분할
    sections = re.split(r'\n(?=#{1,3}\s)', text)
    
    chunks = []
    current_chunk = ""
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # 대략적인 토큰 수 추정 (한글 1자 ≈ 2토큰, 영문 1단어 ≈ 1.3토큰)
        estimated_tokens = len(section.split()) * 1.3
        
        if estimated_tokens > max_tokens and current_chunk:
            # 현재 청크를 저장하고 새 청크 시작
            chunks.append(current_chunk.strip())
            current_chunk = section
        elif len((current_chunk + "\n\n" + section).split()) * 1.3 > max_tokens:
            # 합치면 초과하므로 현재 청크 저장
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = section
        else:
            # 현재 청크에 합침
            current_chunk = (current_chunk + "\n\n" + section).strip()
    
    # 마지막 청크 저장
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def compute_hash(text):
    """텍스트의 MD5 해시를 계산합니다."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:8]

def run(book, settings, state):
    """Stage 1 메인 실행 함수"""
    book_id = book["id"]
    input_path = os.path.join(ROOT, book["input"])
    chunks_dir = os.path.join(ROOT, "chunks", book_id)
    max_tokens = settings.get("chunk_max_tokens", 3000)
    
    # 입력 파일 확인
    if not os.path.exists(input_path):
        print(f"  [오류] 입력 파일이 없습니다: {input_path}")
        return False
    
    # 텍스트 추출
    input_type = book.get("input_type", "md")
    if input_type == "pdf":
        print(f"  PDF에서 텍스트 추출 중: {input_path}")
        text = extract_text_from_pdf(input_path)
    else:
        print(f"  마크다운 파일 읽는 중: {input_path}")
        text = extract_text_from_md(input_path)
    
    # 청크 분할
    chunks = split_into_chunks(text, max_tokens)
    print(f"  {len(chunks)}개 청크로 분할 완료")
    
    # 청크 저장
    os.makedirs(chunks_dir, exist_ok=True)
    chunk_manifest = {}
    
    for i, chunk in enumerate(chunks, 1):
        chunk_id = f"chunk_{i:02d}"
        chunk_path = os.path.join(chunks_dir, f"{chunk_id}.md")
        chunk_hash = compute_hash(chunk)
        
        # 기존 청크와 해시 비교 → 변경된 것만 갱신
        old_hash = state.get("stages", {}).get("1", {}).get("chunks", {}).get(chunk_id, {}).get("hash", "")
        
        if chunk_hash != old_hash:
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.write(chunk)
            print(f"    [{chunk_id}] 저장 (해시: {chunk_hash})")
        else:
            print(f"    [{chunk_id}] 변경 없음 (스킵)")
        
        chunk_manifest[chunk_id] = {
            "hash": chunk_hash,
            "tokens": len(chunk.split()),
            "changed": chunk_hash != old_hash
        }
    
    # 상태에 청크 매니페스트 저장
    if "1" not in state.get("stages", {}):
        state.setdefault("stages", {})["1"] = {}
    state["stages"]["1"]["chunks"] = chunk_manifest
    state["stages"]["1"]["total_chunks"] = len(chunks)
    
    return True
