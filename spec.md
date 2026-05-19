# 📘 Oversoul 프로젝트 사양서 (Project Specification)

> 이 파일은 새로운 AI 에이전트 또는 협업자가 프로젝트에 투입될 때
> **가장 먼저 읽어야 하는 단일 진실의 원천(Single Source of Truth)**입니다.

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | 내 안의 우주 : 랄프 왈도 에머슨의 영혼을 깨우는 초월주의 에세이 |
| **원제** | The Over-Soul (1841) |
| **저자** | 랄프 왈도 에머슨 (Ralph Waldo Emerson) |
| **번역/해제** | 책추남 (책추남TV) |
| **출판사** | 나비스쿨 |
| **시리즈** | 책추남 불변의 지혜 시리즈 01 |
| **타겟 독자** | 자기계발·영성 서적에 관심 있는 20~50대 한국인 독자 |
| **출판 채널** | 크몽 전자책 (A5 디지털) + 부크크 POD 종이책 (A5 인쇄) |

---

## 2. 프로젝트 디렉토리 구조

```
oversoul/
├── .gitignore              # Git 추적 제외 규칙
├── spec.md                 # 📌 이 파일 (프로젝트 사양서)
├── final_content.md        # 빌드용 마스터 원고 (v4에서 자동 동기화)
├── pdf_builder.py          # ReportLab 기반 PDF 조판 엔진
├── commentator.py          # [레거시] 책추남 페르소나 해설 생성기 (참고용)
├── translator.py           # [레거시] 원문 분할 번역기 (참고용)
├── refined_translation.md  # 초벌 번역본 원고
├── translated_soul.md      # 번역 중간 결과물
├── images/                 # 표지 + 내지 일러스트 15장
│   ├── cover.png           # 📌 최종 확정 표지
│   ├── scene_ch1~10.png    # 챕터별 일러스트
│   ├── prompts.md          # 이미지 생성 프롬프트 레지스트리
│   └── ...
├── versions/               # 마크다운 원고 버전 아카이브
│   ├── final_content_v1.md
│   ├── final_content_v2.md
│   ├── final_content_v3.md
│   └── final_content_v4.md # 📌 현행 마스터
├── marketing/              # 크몽 상세페이지 마케팅 자료
│   ├── kmong_promotion_blueprint.md
│   ├── card1~5.png         # 카드뉴스 이미지
│   └── thumbnail.png       # 대표 썸네일
├── input/                  # 원문 PDF (The Over-Soul 원문)
└── scratch/                # [.gitignore] 일회성 디버깅 스크립트 (Git 미추적)
```

---

## 3. 빌드 방법

```bash
# 크몽 전자책 + 부크크 종이책 PDF 동시 빌드
python pdf_builder.py
```

- `versions/final_content_v4.md` → `final_content.md`로 자동 동기화 후 빌드
- 산출물: `Emerson_Universe_Kmong_Ebook.pdf`, `Emerson_Universe_Bookk_POD.pdf`

---

## 4. 5단계 파이프라인 (Agentic Workflow)

| Phase | 담당 | 산출물 | Git 커밋 메시지 |
|-------|------|--------|-----------------|
| 1. 원문 추출 | 데이터 엔지니어 AI | `raw_text.md` | `feat: 원문 텍스트 추출 완료` |
| 2. 번역/해설 | 번역가 AI + 해설가 AI | `translated_content.md` | `feat: 번역 및 해설 완료` |
| 3. 비주얼 생성 | 디자이너 AI | `images/` 폴더 | `feat: 표지 및 일러스트 확정` |
| 4. 조판/빌드 | 편집자 AI + `pdf_builder.py` | `final_content.md` + PDF | `release: vX.X 조판 완료` |
| 5. 마케팅 | 마케터 AI | `marketing/` 폴더 | `feat: 마케팅 자료 완료` |

각 Phase 완료 후 **반드시 사용자 리뷰(Human Checkpoint)** → **승인 시 Git Commit**.

---

## 5. Git 커밋 컨벤션

```
feat:     새 기능/콘텐츠 추가
fix:      오류 수정
refactor: 코드/구조 개선
release:  최종 빌드 출시
docs:     문서 수정
```

---

## 6. ⚠️ 절대 규칙 (Inviolable Rules)

> [!CAUTION]
> 아래 규칙을 위반하면 프로젝트 자산이 훼손됩니다.

1. **이미지 잠금:** `images/` 폴더 내의 모든 표지 및 내지 일러스트는 **최종 확정 상태**입니다.
   AI는 어떠한 경우에도 `generate_image`를 호출하여 기존 이미지를 임의로 덮어쓰거나 대체해서는 안 됩니다.
   이미지 변경이 필요하면 반드시 **사용자의 명시적 승인**을 받은 후 진행하세요.

2. **마스터 원고:** `versions/final_content_v4.md`가 현행 마스터입니다.
   원고를 수정할 때는 반드시 이 파일을 수정하세요. `final_content.md`는 빌드 시 자동 덮어쓰기됩니다.

3. **PDF는 Git에 넣지 않습니다.** `python pdf_builder.py`로 언제든 재생성 가능하므로 `.gitignore`에서 제외합니다.

4. **한자 병기 유지:** 핵심 철학 용어(대령[大靈], 일원론[一元論] 등)의 한자 표기를 삭제하지 마세요.
