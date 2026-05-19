"""
pipeline.py — 책추남 전자책 자동 제작 파이프라인 오케스트레이터 v2.1

[v2.1 드림팀 리뷰 반영]
- A2: run_stage()에서 상태 병합(merge) 방식 적용
- A3: approve 명령에 --continue 옵션 추가
- R1: CP949 이모지 안전 출력 래퍼 적용
- U1: 체크포인트에서 검토 대상 파일 가이드 출력
- U3: list 서브커맨드 추가
- T3: 시작/종료 시각, 소요시간 기록

사용법:
  python pipeline.py run --book self-reliance          # 전체 빌드
  python pipeline.py run --book self-reliance --from 3  # Stage 3부터 재실행
  python pipeline.py status --book self-reliance        # 진행 상태 확인
  python pipeline.py approve --book self-reliance       # 체크포인트 승인
  python pipeline.py list                               # 등록된 도서 목록
"""
import argparse
import json
import os
import sys
import time
import yaml
from datetime import datetime

# [R1 수정] CP949 인코딩 문제 전역 해결
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 프로젝트 루트 경로
ROOT = os.path.dirname(os.path.abspath(__file__))

def safe_print(msg):
    """[R1] 이모지/특수문자를 안전하게 출력합니다."""
    try:
        print(msg)
    except UnicodeEncodeError:
        # 이모지를 [?]로 대체하여 출력
        safe = msg.encode('ascii', errors='replace').decode('ascii')
        print(safe)

def load_config(book_id=None):
    """books.yaml에서 도서 설정을 로드합니다."""
    config_path = os.path.join(ROOT, "config", "books.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if book_id is None:
        return config
    
    if book_id not in config["books"]:
        safe_print(f"[오류] '{book_id}' 도서가 config/books.yaml에 없습니다.")
        safe_print(f"  사용 가능한 도서: {list(config['books'].keys())}")
        sys.exit(1)
    
    book = config["books"][book_id]
    book["id"] = book_id
    settings = config.get("settings", {})
    return book, settings

def load_state(book_id):
    """파이프라인 진행 상태를 로드합니다."""
    state_path = os.path.join(ROOT, "state", f"{book_id}.json")
    if os.path.exists(state_path):
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "book_id": book_id,
        "current_stage": 0,
        "stages": {},
        "checkpoints": {"A": False, "B": False, "C": False},
        "total_tokens": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def save_state(book_id, state):
    """[R4 수정] 원자적 쓰기로 상태를 안전하게 저장합니다."""
    state["updated_at"] = datetime.now().isoformat()
    state_path = os.path.join(ROOT, "state", f"{book_id}.json")
    temp_path = state_path + ".tmp"
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    # 원자적 교체 (임시 파일 -> 실제 파일)
    if os.path.exists(state_path):
        os.replace(temp_path, state_path)
    else:
        os.rename(temp_path, state_path)

def run_stage(stage_num, book, settings, state):
    """지정된 단계를 실행합니다."""
    stages = {
        1: ("원문 입력 & 청크 분할", "agents.chunker", "run"),
        2: ("책추남 스타일 번역", "agents.translator", "run"),
        3: ("책추남 해설/해제 생성", "agents.commentator", "run"),
        4: ("시네마틱 이미지 생성", "agents.image_director", "run"),
        5: ("합본 & 품질 게이트", "agents.assembler", "run"),
        6: ("PDF 조판", "agents.pdf_builder", "run"),
        7: ("버전 저장 & Git 커밋", "agents.versioner", "run"),
    }
    
    if stage_num not in stages:
        safe_print(f"[오류] Stage {stage_num}은 존재하지 않습니다. (1~7)")
        return False
    
    name, module_name, func_name = stages[stage_num]
    safe_print(f"\n{'='*60}")
    safe_print(f"  [{stage_num}/7] {name}")
    safe_print(f"{'='*60}")
    
    stage_start = time.time()
    
    try:
        # 에이전트 모듈 동적 임포트
        module = __import__(module_name, fromlist=[func_name])
        run_func = getattr(module, func_name)
        
        # 에이전트 실행
        result = run_func(book, settings, state)
        
        elapsed = round(time.time() - stage_start, 1)
        
        # [A2 수정] 상태를 병합(merge)하여 기존 데이터 보존
        stage_key = str(stage_num)
        existing_stage = state.get("stages", {}).get(stage_key, {})
        existing_stage.update({
            "name": name,
            "status": "done" if result else "failed",
            "completed_at": datetime.now().isoformat(),
            "elapsed_seconds": elapsed
        })
        state.setdefault("stages", {})[stage_key] = existing_stage
        state["current_stage"] = stage_num
        save_state(book["id"], state)
        
        if result:
            safe_print(f"  [완료] {name} ({elapsed}초 소요)")
        else:
            safe_print(f"  [실패] {name} -- 재시도: python pipeline.py run --book {book['id']} --from {stage_num}")
        
        return result
        
    except ImportError as e:
        safe_print(f"  [안내] 에이전트 '{module_name}'을 찾을 수 없습니다.")
        safe_print(f"         이 단계는 Antigravity 에이전트가 대화형으로 수행합니다.")
        safe_print(f"         에러: {e}")
        
        stage_key = str(stage_num)
        existing_stage = state.get("stages", {}).get(stage_key, {})
        existing_stage.update({
            "name": name,
            "status": "manual",
            "completed_at": datetime.now().isoformat()
        })
        state.setdefault("stages", {})[stage_key] = existing_stage
        state["current_stage"] = stage_num
        save_state(book["id"], state)
        return True

def check_checkpoint(checkpoint_id, book, state):
    """[U1 개선] 체크포인트를 확인하고 검토 가이드를 출력합니다."""
    checkpoint_map = {
        "A": ("번역 검토", 2, [
            f"  검토 파일: translated/{book['id']}/ 디렉터리의 각 청크 번역본",
            "  확인 사항:",
            "    - 원문 문장이 누락 없이 번역되었는가?",
            "    - 번역투(~함에 다름아니다) 없이 자연스러운가?",
            "    - 중학생이 읽어도 이해 가능한가?",
        ]),
        "B": ("최종 원고 검토", 5, [
            f"  검토 파일: versions/{book['id']}/ 디렉터리의 최신 합본 원고",
            "  확인 사항:",
            "    - 본문 3부 + 심층 해설 4종 + 해제 + 나비 퀘스트가 모두 있는가?",
            "    - 이미지 태그가 올바르게 매핑되어 있는가?",
            "    - 나비스쿨/피닉스 퓨처 스쿨 소개가 포함되어 있는가?",
        ]),
        "C": ("PDF 최종 검수", 6, [
            f"  검토 파일: output/ 디렉터리의 PDF 파일",
            "  확인 사항:",
            "    - 표지, 속표지, 목차가 해당 도서 정보와 일치하는가?",
            "    - 페이지 번호가 목차와 정확히 대응하는가?",
            "    - 상단 헤더에 올바른 도서명이 표시되는가?",
        ])
    }
    
    if checkpoint_id not in checkpoint_map:
        return True
    
    name, after_stage, guide_lines = checkpoint_map[checkpoint_id]
    
    if state["checkpoints"].get(checkpoint_id, False):
        return True
    
    safe_print(f"\n{'*'*60}")
    safe_print(f"  >> 체크포인트 {checkpoint_id} -- {name}")
    safe_print(f"  Stage {after_stage} 완료. 검토 후 승인해 주세요.")
    safe_print(f"")
    for line in guide_lines:
        safe_print(line)
    safe_print(f"")
    safe_print(f"  승인: python pipeline.py approve --book {book['id']} --checkpoint {checkpoint_id}")
    safe_print(f"  재작업: python pipeline.py run --book {book['id']} --from <단계번호>")
    safe_print(f"{'*'*60}")
    
    return False  # 일시정지

def cmd_run(args):
    """파이프라인을 실행합니다."""
    book, settings = load_config(args.book)
    state = load_state(args.book)
    
    start = args.start if hasattr(args, 'start') and args.start else 1
    end = args.end if hasattr(args, 'end') and args.end else 7
    
    pipeline_start = time.time()
    
    safe_print(f"\n{'#'*60}")
    safe_print(f"  책추남 불변의 지혜 시리즈 -- 전자책 자동 제작 파이프라인 v2.1")
    safe_print(f"  도서: {book['series']} {book['title']} {book['orig_title']}")
    safe_print(f"  실행 범위: Stage {start} -> Stage {end}")
    safe_print(f"{'#'*60}")
    
    # 체크포인트 위치 매핑
    checkpoints_after = {2: "A", 5: "B", 6: "C"}
    
    for stage_num in range(start, end + 1):
        success = run_stage(stage_num, book, settings, state)
        
        if not success:
            safe_print(f"\n[중단] Stage {stage_num} 실패. 수정 후 재실행하세요.")
            break
        
        # 합본(Stage 5) 직후 품질 게이트 자동 실행
        if stage_num == 5:
            try:
                from agents.quality_gate import run as qg_run
                safe_print(f"\n  --- 품질 게이트 자동 검수 ---")
                qg_passed = qg_run(book, settings, state)
                if not qg_passed:
                    safe_print(f"  [품질 미달] 해당 단계를 수정 후 재실행하세요.")
                    save_state(args.book, state)
                    break
            except ImportError:
                pass
        
        # 체크포인트 확인
        if stage_num in checkpoints_after:
            cp_id = checkpoints_after[stage_num]
            if not check_checkpoint(cp_id, book, state):
                save_state(args.book, state)
                break
    else:
        elapsed_total = round(time.time() - pipeline_start, 1)
        safe_print(f"\n{'='*60}")
        safe_print(f"  모든 단계 완료! (총 소요: {elapsed_total}초)")
        safe_print(f"{'='*60}")

def cmd_status(args):
    """[U2 개선] 파이프라인 진행 상태를 상세히 출력합니다."""
    book, _ = load_config(args.book)
    state = load_state(args.book)
    
    safe_print(f"\n  도서: {book['title']} ({book['orig_title']})")
    safe_print(f"  현재 단계: Stage {state.get('current_stage', 0)}")
    safe_print(f"  최종 갱신: {state.get('updated_at', 'N/A')}")
    safe_print(f"  누적 토큰: {state.get('total_tokens', 0):,}")
    safe_print("")
    
    stage_names = {
        "1": "원문 청크 분할", "2": "번역", "3": "해설 생성",
        "4": "이미지 생성", "5": "합본 & 검수", "6": "PDF 조판", "7": "버전 관리"
    }
    
    for i in range(1, 8):
        info = state.get("stages", {}).get(str(i), {})
        status = info.get("status", "대기")
        elapsed = info.get("elapsed_seconds", "")
        elapsed_str = f" ({elapsed}초)" if elapsed else ""
        icon = {"done": "[OK]", "failed": "[NG]", "manual": "[수동]", "대기": "[..]"}.get(status, "[..]")
        safe_print(f"  {icon} Stage {i}: {stage_names[str(i)]} -- {status}{elapsed_str}")
    
    # 품질 점수
    quality = state.get("stages", {}).get("5", {}).get("quality_score", None)
    if quality is not None:
        safe_print(f"\n  품질 점수: {quality}/100")
    
    safe_print("")
    for cp_id, approved in state.get("checkpoints", {}).items():
        icon = "[OK]" if approved else "[대기]"
        safe_print(f"  {icon} 체크포인트 {cp_id}: {'승인됨' if approved else '대기 중'}")

def cmd_approve(args):
    """[A3 개선] 체크포인트를 승인하고 선택적으로 다음 단계를 자동 재개합니다."""
    book, settings = load_config(args.book)
    state = load_state(args.book)
    cp = args.checkpoint.upper()
    state["checkpoints"][cp] = True
    save_state(args.book, state)
    safe_print(f"  [OK] 체크포인트 {cp} 승인 완료.")
    
    # --continue 옵션: 승인 후 다음 단계부터 자동 재개
    if hasattr(args, 'auto_continue') and args.auto_continue:
        checkpoint_next = {"A": 3, "B": 6, "C": 7}
        next_stage = checkpoint_next.get(cp, None)
        if next_stage:
            safe_print(f"  Stage {next_stage}부터 자동 재개합니다...")
            args.start = next_stage
            args.end = 7
            cmd_run(args)

def cmd_list(args):
    """[U3 신규] 등록된 도서 목록을 출력합니다."""
    config = load_config()
    books = config.get("books", {})
    
    safe_print(f"\n  등록된 도서 목록 ({len(books)}권)")
    safe_print(f"  {'─'*50}")
    
    for book_id, info in books.items():
        safe_print(f"  {info.get('series', '')}  {info.get('title', '')} {info.get('orig_title', '')}")
        safe_print(f"    ID: {book_id}")
        safe_print(f"    입력: {info.get('input', 'N/A')}")
        safe_print("")

def main():
    parser = argparse.ArgumentParser(description="책추남 전자책 자동 제작 파이프라인 v2.1")
    sub = parser.add_subparsers(dest="command")
    
    # run 명령
    run_parser = sub.add_parser("run", help="파이프라인 실행")
    run_parser.add_argument("--book", required=True, help="도서 ID (예: self-reliance)")
    run_parser.add_argument("--from", dest="start", type=int, default=1, help="시작 단계 (1~7)")
    run_parser.add_argument("--to", dest="end", type=int, default=7, help="종료 단계 (1~7)")
    
    # status 명령
    status_parser = sub.add_parser("status", help="진행 상태 확인")
    status_parser.add_argument("--book", required=True, help="도서 ID")
    
    # approve 명령
    approve_parser = sub.add_parser("approve", help="체크포인트 승인")
    approve_parser.add_argument("--book", required=True, help="도서 ID")
    approve_parser.add_argument("--checkpoint", required=True, help="체크포인트 ID (A, B, C)")
    approve_parser.add_argument("--continue", dest="auto_continue", action="store_true", help="승인 후 자동 재개")
    
    # list 명령 [U3 신규]
    sub.add_parser("list", help="등록된 도서 목록 출력")
    
    args = parser.parse_args()
    
    if args.command == "run":
        cmd_run(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "approve":
        cmd_approve(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
