"""
Stage 7: 버전 저장 & Git 커밋 에이전트 (versioner.py)

파이프라인 산출물을 Git에 커밋하고 태그를 부여합니다.
- 자동 CHANGELOG 작성
- 도서별 브랜치 관리
"""
import os
import subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_git(cmd):
    """Git 명령을 실행합니다."""
    result = subprocess.run(
        cmd, shell=True, cwd=ROOT,
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    return result.returncode == 0, result.stdout.strip()

def run(book, settings, state):
    """Stage 7 메인 실행 함수"""
    book_id = book["id"]
    today = datetime.now().strftime("%Y-%m-%d")
    
    # CHANGELOG 업데이트
    changelog_path = os.path.join(ROOT, "versions", book_id, "CHANGELOG.md")
    os.makedirs(os.path.dirname(changelog_path), exist_ok=True)
    
    version_info = state.get("stages", {}).get("5", {}).get("latest_version", "unknown")
    
    entry = f"\n## [{today}] {version_info}\n"
    entry += f"- 도서: {book['title']} {book['orig_title']}\n"
    
    stages_done = []
    for i in range(1, 8):
        s = state.get("stages", {}).get(str(i), {})
        if s.get("status") in ("done", "manual"):
            stages_done.append(f"Stage {i}")
    entry += f"- 실행 단계: {', '.join(stages_done)}\n"
    entry += f"- 타임스탬프: {datetime.now().isoformat()}\n"
    
    # 기존 CHANGELOG에 추가
    existing = ""
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            existing = f.read()
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(f"# CHANGELOG — {book['title']}\n")
        f.write(entry)
        if existing:
            # 기존 헤더 제거 후 내용만 추가
            lines = existing.split('\n')
            content_start = 0
            for i, line in enumerate(lines):
                if line.startswith('## '):
                    content_start = i
                    break
            f.write('\n'.join(lines[content_start:]))
    
    print(f"  CHANGELOG 업데이트: versions/{book_id}/CHANGELOG.md")
    
    # Git 스테이징 & 커밋
    commit_msg = f"build({book_id}): {book['title']} 파이프라인 빌드 {today}"
    
    success, _ = run_git("git add -A")
    if success:
        success, output = run_git(f'git commit -m "{commit_msg}"')
        if success:
            print(f"  Git 커밋 완료: {commit_msg}")
        elif "nothing to commit" in output:
            print(f"  변경 사항 없음 (커밋 스킵)")
        else:
            print(f"  [안내] Git 커밋 수동 필요: {output}")
    
    return True
