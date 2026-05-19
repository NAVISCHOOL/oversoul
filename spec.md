# 에머슨 대령 헤르메스-슈퍼파워 통합 출판 명세서

1. 시스템 구동 원칙:
   - Antigravity Superpowers와 Hermes의 자율 추론/페르소나 제어 프레임워크를 가동한다.
   - 최소 비용(Gemini 3 Flash 기본 사용)으로 기성 출판사를 뛰어넘는 최상의 품질을 도출한다.

2. 파이프라인 구성 및 하네스 제어 규칙:
   - [Agent 1] `translator.py` : 원문 3페이지 분할 공급(Chunker) 및 중학생 수준 초쉬운 완역, `state.json`에 실시간 캐시 저장(Durable State).
   - [Agent 2] `commentator.py` : Hermes 페르소나 엔진을 가동하여 책추남TV 결을 100% 재현한 해제 및 3대 영성 도서 비교 분석 부록 작성. 가독성 95점 미만 시 자동 자가 수정 루프 가동.
   - [Agent 3] `pdf_builder.py` : ReportLab 기반 부크크 규격 PDF 자동 조판 및 레이아웃 검증 안전망 게이트 통과 후 최종 출력.
