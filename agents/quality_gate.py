"""
Stage 5.5: 품질 게이트 에이전트 (quality_gate.py)

합본된 최종 원고의 품질을 자동 검수합니다.
- 구조 완성도 검증 (필수 섹션 존재 여부)
- 번역투 패턴 자동 감지
- 이미지 태그 매핑 확인
- 점수 미달 시 False 반환 → 파이프라인 재시도
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 번역투 금지 패턴
BANNED_PATTERNS = [
    r'~함에\s*다름\s*아니다',
    r'~한\s*바이다',
    r'~하는\s*것이\s*가능하다',
    r'~라\s*할\s*수\s*있겠다',
    r'~에\s*지나지\s*않는\s*것이다',
    r'~임에\s*틀림\s*없다',
]

# 필수 섹션 키워드 (하나라도 없으면 구조 미달)
REQUIRED_SECTIONS = [
    "서문",
    "제1부",
    "제2부", 
    "제3부",
    "심층 해설",
    "심층 해제",
    "나비 퀘스트",
]

def check_structure(content):
    """필수 섹션 존재 여부를 확인합니다."""
    missing = []
    for section in REQUIRED_SECTIONS:
        if section not in content:
            missing.append(section)
    return missing

def check_banned_patterns(content):
    """번역투 패턴을 감지합니다."""
    found = []
    for pattern in BANNED_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            found.extend(matches)
    return found

def check_image_tags(content):
    """이미지 태그가 올바르게 매핑되어 있는지 확인합니다."""
    tags = re.findall(r'!\[.*?\]\((.*?)\)', content)
    missing_files = []
    for tag_path in tags:
        full_path = os.path.join(ROOT, tag_path)
        if not os.path.exists(full_path):
            missing_files.append(tag_path)
    return tags, missing_files

def run(book, settings, state):
    """품질 게이트 실행 함수"""
    book_id = book["id"]
    threshold = settings.get("quality_threshold", 85)
    
    # 활성 원고 경로
    active_file = state.get("stages", {}).get("5", {}).get("active_file", "")
    if not active_file:
        active_file = f"final_{book_id.replace('-', '_')}.md"
    
    active_path = os.path.join(ROOT, active_file)
    
    if not os.path.exists(active_path):
        print(f"  [안내] 활성 원고가 없습니다: {active_file}")
        print(f"         Antigravity 에이전트가 수동으로 품질 검수합니다.")
        return True
    
    with open(active_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"  원고 분석 중: {active_file} ({len(content):,}자)")
    
    # 1. 구조 검수 (20점)
    missing = check_structure(content)
    structure_score = max(0, 20 - len(missing) * 3)
    if missing:
        print(f"  [구조] 누락 섹션: {', '.join(missing)}")
    else:
        print(f"  [구조] 모든 필수 섹션 존재 ✅")
    
    # 2. 번역투 검수 (20점)
    banned = check_banned_patterns(content)
    translation_score = max(0, 20 - len(banned) * 2)
    if banned:
        print(f"  [번역투] 금지 패턴 {len(banned)}건 감지: {banned[:3]}")
    else:
        print(f"  [번역투] 금지 패턴 0건 ✅")
    
    # 3. 이미지 태그 검수 (20점)
    tags, missing_imgs = check_image_tags(content)
    image_score = 20 if not missing_imgs else max(0, 20 - len(missing_imgs) * 5)
    print(f"  [이미지] 태그 {len(tags)}개, 누락 파일 {len(missing_imgs)}개")
    
    # 4. 분량 검수 (20점) — 너무 짧으면 감점
    word_count = len(content)
    volume_score = 20 if word_count > 10000 else int(20 * word_count / 10000)
    print(f"  [분량] {word_count:,}자 (기준: 10,000자 이상)")
    
    # 5. 메타데이터 검수 (20점)
    has_toc = "[TOC_PLACEHOLDER]" in content or "목차" in content
    has_cover = "![" in content
    meta_score = 0
    if has_toc: meta_score += 10
    if has_cover: meta_score += 10
    print(f"  [메타] 목차: {'✅' if has_toc else '❌'}, 표지: {'✅' if has_cover else '❌'}")
    
    # 종합
    total = structure_score + translation_score + image_score + volume_score + meta_score
    passed = total >= threshold
    
    print(f"\n  ┌────────────────────────────────┐")
    print(f"  │ 품질 점수: {total}/100 {'✅ 통과' if passed else '❌ 미달'} (기준: {threshold}점) │")
    print(f"  │ 구조: {structure_score}/20  번역: {translation_score}/20  이미지: {image_score}/20 │")
    print(f"  │ 분량: {volume_score}/20  메타: {meta_score}/20               │")
    print(f"  └────────────────────────────────┘")
    
    # 상태에 품질 점수 기록
    state.setdefault("stages", {}).setdefault("5", {})
    state["stages"]["5"]["quality_score"] = total
    state["stages"]["5"]["quality_passed"] = passed
    
    return passed
