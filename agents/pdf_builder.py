"""
Stage 6: PDF 조판 에이전트 래퍼 (pdf_builder.py)

기존 루트의 pdf_builder.py를 호출하여 PDF를 조판합니다.
- config/books.yaml의 동적 설정 기반
- 크몽 전자책 + 부크크 POD 동시 생성
"""
import os
import sys
import importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(book, settings, state):
    """Stage 6 메인 실행 함수 — 기존 pdf_builder.py를 래핑합니다."""
    # 기존 조판 엔진 경로
    builder_path = os.path.join(ROOT, "pdf_builder.py")
    
    if not os.path.exists(builder_path):
        print("  [오류] pdf_builder.py가 프로젝트 루트에 없습니다.")
        return False
    
    # 활성 원고 파일 확인
    active_file = state.get("stages", {}).get("5", {}).get("active_file", "")
    active_path = os.path.join(ROOT, active_file) if active_file else ""
    
    if active_file and os.path.exists(active_path):
        print(f"  활성 원고: {active_file}")
    else:
        print("  [안내] Stage 5에서 합본된 활성 원고가 없습니다.")
        print("         기존 final_content.md를 사용하여 빌드합니다.")
    
    # 기존 pdf_builder.py를 모듈로 로드하여 실행
    try:
        spec = importlib.util.spec_from_file_location("root_pdf_builder", builder_path)
        builder_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder_module)
        
        # main() 또는 빌드 함수 호출
        if hasattr(builder_module, 'main'):
            builder_module.main()
        else:
            print("  [안내] pdf_builder.py에 main() 함수가 없습니다.")
            print("         터미널에서 직접 실행하세요: python pdf_builder.py")
        
        print("  PDF 조판 완료")
        return True
        
    except Exception as e:
        print(f"  [오류] PDF 빌드 중 에러 발생: {e}")
        print(f"         터미널에서 직접 실행하세요: python pdf_builder.py")
        return False
