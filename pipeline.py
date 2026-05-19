"""
pipeline.py — 책추남 전자책 자동 제작 파이프라인 오케스트레이터

사용법:
  python pipeline.py run --book self-reliance          # 전체 빌드
  python pipeline.py run --book self-reliance --from 3  # Stage 3부터 재실행
  python pipeline.py status --book self-reliance        # 진행 상태 확인
  python pipeline.py approve --book self-reliance       # 체크포인트 승인
"""
import argparse
import json
import os
import sys
import yaml
from datetime import datetime

# 프로젝트 루트 경로
ROOT = os.path.dirname(os.path.abspath(__file__))

def load_config(book_id):
    """books.yaml에서 도서 설정을 로드합니다."""
    config_path = os.path.join(ROOT, "config", "books.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if book_id not in config["books"]:
        print(f"[오류] '{book_id}' 도서가 config/books.yaml에 없습니다.")
        print(f"  사용 가능한 도서: {list(config['books'].keys())}")
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
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def save_state(book_id, state):
    """파이프라인 진행 상태를 저장합니다."""
    state["updated_at"] = datetime.now().isoformat()
    state_path = os.path.join(ROOT, "state", f"{book_id}.json")
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def run_stage(stage_num, book, settings, state):
    """지정된 단계를 실행합니다."""
    stages = {
        1: ("원문 입력 & 청크 분할", "agents.chunker", "run"),
        2: ("책추남 스타일 번역", "agents.translator", "run"),
        3: ("책추남 해설·해제 생성", "agents.commentator", "run"),
        4: ("시네마틱 이미지 생성", "agents.image_director", "run"),
        5: ("합본 & 품질 게이트", "agents.assembler", "run"),
        6: ("PDF 조판", "agents.pdf_builder", "run"),
        7: ("버전 저장 & Git 커밋", "agents.versioner", "run"),
    }
    
    if stage_num not in stages:
        print(f"[오류] Stage {stage_num}은 존재하지 않습니다. (1~7)")
        return False
    
    name, module_name, func_name = stages[stage_num]
    print(f"\n{'='*60}")
    print(f"  [{stage_num}/7] {name}")
    print(f"{'='*60}")
    
    try:
        # 에이전트 모듈 동적 임포트
        module = __import__(module_name, fromlist=[func_name])
        run_func = getattr(module, func_name)
        
        # 에이전트 실행
        result = run_func(book, settings, state)
        
        # 상태 업데이트
        state["stages"][str(stage_num)] = {
            "name": name,
            "status": "done" if result else "failed",
            "completed_at": datetime.now().isoformat()
        }
        state["current_stage"] = stage_num
        save_state(book["id"], state)
        
        if result:
            print(f"  [완료] {name} 성공")
        else:
            print(f"  [실패] {name} — 재시도하려면: python pipeline.py run --book {book['id']} --from {stage_num}")
        
        return result
        
    except ImportError as e:
        print(f"  [안내] 에이전트 모듈 '{module_name}'을 찾을 수 없습니다.")
        print(f"         이 단계는 Antigravity 에이전트가 대화형으로 수행합니다.")
        print(f"         에러: {e}")
        
        state["stages"][str(stage_num)] = {
            "name": name,
            "status": "manual",
            "completed_at": datetime.now().isoformat()
        }
        state["current_stage"] = stage_num
        save_state(book["id"], state)
        return True

def check_checkpoint(checkpoint_id, book, state):
    """Human-in-the-Loop 체크포인트를 확인합니다."""
    checkpoint_map = {
        "A": ("번역 검토", 2),
        "B": ("최종 원고 검토", 5),
        "C": ("PDF 최종 검수", 6)
    }
    
    if checkpoint_id not in checkpoint_map:
        return True
    
    name, after_stage = checkpoint_map[checkpoint_id]
    
    if state["checkpoints"].get(checkpoint_id, False):
        return True
    
    print(f"\n{'*'*60}")
    print(f"  ★ 체크포인트 {checkpoint_id} — {name}")
    print(f"  Stage {after_stage} 완료. 검토 후 승인해 주세요.")
    print(f"  승인: python pipeline.py approve --book {book['id']} --checkpoint {checkpoint_id}")
    print(f"  재작업: python pipeline.py run --book {book['id']} --from {{단계번호}}")
    print(f"{'*'*60}")
    
    return False  # 일시정지

def cmd_run(args):
    """파이프라인을 실행합니다."""
    book, settings = load_config(args.book)
    state = load_state(args.book)
    
    start = args.start if hasattr(args, 'start') and args.start else 1
    end = args.end if hasattr(args, 'end') and args.end else 7
    
    print(f"\n{'#'*60}")
    print(f"  책추남 불변의 지혜 시리즈 — 전자책 자동 제작 파이프라인")
    print(f"  도서: {book['series']} {book['title']} {book['orig_title']}")
    print(f"  실행 범위: Stage {start} → Stage {end}")
    print(f"{'#'*60}")
    
    # 체크포인트 위치 매핑
    checkpoints_after = {2: "A", 5: "B", 6: "C"}
    
    for stage_num in range(start, end + 1):
        success = run_stage(stage_num, book, settings, state)
        
        if not success:
            print(f"\n[중단] Stage {stage_num} 실패. 수정 후 재실행하세요.")
            break
        
        # 체크포인트 확인
        if stage_num in checkpoints_after:
            cp_id = checkpoints_after[stage_num]
            if not check_checkpoint(cp_id, book, state):
                save_state(args.book, state)
                break
    else:
        print(f"\n{'='*60}")
        print(f"  모든 단계 완료!")
        print(f"{'='*60}")

def cmd_status(args):
    """파이프라인 진행 상태를 출력합니다."""
    book, _ = load_config(args.book)
    state = load_state(args.book)
    
    print(f"\n  도서: {book['title']} ({book['orig_title']})")
    print(f"  현재 단계: Stage {state.get('current_stage', 0)}")
    print(f"  최종 갱신: {state.get('updated_at', 'N/A')}")
    print()
    
    stage_names = {
        "1": "원문 청크 분할", "2": "번역", "3": "해설 생성",
        "4": "이미지 생성", "5": "합본 & 검수", "6": "PDF 조판", "7": "버전 관리"
    }
    
    for i in range(1, 8):
        info = state.get("stages", {}).get(str(i), {})
        status = info.get("status", "대기")
        icon = {"done": "✅", "failed": "❌", "manual": "🔧", "대기": "⏳"}.get(status, "⏳")
        print(f"  {icon} Stage {i}: {stage_names[str(i)]} — {status}")
    
    print()
    for cp_id, approved in state.get("checkpoints", {}).items():
        icon = "✅" if approved else "⏸️"
        print(f"  {icon} 체크포인트 {cp_id}: {'승인됨' if approved else '대기 중'}")

def cmd_approve(args):
    """체크포인트를 승인합니다."""
    state = load_state(args.book)
    cp = args.checkpoint.upper()
    state["checkpoints"][cp] = True
    save_state(args.book, state)
    print(f"  ✅ 체크포인트 {cp} 승인 완료. 다음 단계를 실행하세요.")

def main():
    parser = argparse.ArgumentParser(description="책추남 전자책 자동 제작 파이프라인")
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
    
    args = parser.parse_args()
    
    if args.command == "run":
        cmd_run(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "approve":
        cmd_approve(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
