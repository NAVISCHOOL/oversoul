# 📘 책추남 불변의 지혜 시리즈 — 전자책 자동 제작 파이프라인

> **버전:** 2.0.0  
> **최종 수정:** 2026-05-19  
> **설계자:** 나비스쿨 × Antigravity  

---

## 🎯 파이프라인 개요

영문 고전 원문을 투입하면, **7단계 에이전트 체인**이 순차적으로 가동되어
책추남TV 스타일의 프리미엄 한국어 전자책(크몽 + 부크크 PDF)을 자동 생성합니다.

### 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **토큰 최소화** | 청크 단위 점진 처리 + 캐시로 변경분만 재작업 |
| **하네스 엔지니어링** | 각 에이전트에 제어 고삐(프롬프트 가드레일) 적용 |
| **Human-in-the-Loop** | 3개 체크포인트에서 사람이 검토·수정 가능 |
| **자동 업그레이드** | 품질 미달 시 해당 단계만 자동 재시도 |
| **버전 보존** | 모든 산출물이 날짜+버전으로 저장, Git 커밋 |

---

## 🔄 7단계 파이프라인 흐름

```
  ┌─────────────────────────────────────────────────────────┐
  │                    pipeline.py run                       │
  │                                                         │
  │  [Stage 1] 원문 입력 & 청크 분할 (chunker.py)           │
  │      ↓                                                  │
  │  [Stage 2] 책추남 스타일 번역 (translator.py)           │
  │      ↓                                                  │
  │  ★ 체크포인트 A — 번역 검토 (Human-in-the-Loop)        │
  │      ↓                                                  │
  │  [Stage 3] 책추남 해설·해제 생성 (commentator.py)       │
  │      ↓                                                  │
  │  [Stage 4] 시네마틱 이미지 생성 (image_director.py)     │
  │      ↓                                                  │
  │  [Stage 5] 합본 & 품질 게이트 (assembler.py)            │
  │      ↓                                                  │
  │  ★ 체크포인트 B — 최종 원고 검토 (Human-in-the-Loop)   │
  │      ↓                                                  │
  │  [Stage 6] PDF 조판 (pdf_builder.py)                    │
  │      ↓                                                  │
  │  [Stage 7] 버전 저장 & Git 커밋 (versioner.py)          │
  │      ↓                                                  │
  │  ★ 체크포인트 C — 최종 PDF 승인 (Human-in-the-Loop)    │
  │      ↓                                                  │
  │  🎉 완료 — 업그레이드 필요 시 해당 단계만 재실행       │
  └─────────────────────────────────────────────────────────┘
```

---

## 📂 디렉터리 구조

```
oversoul/
├── pipeline.py              # 통합 오케스트레이터
├── pipeline.md              # 이 문서 (마스터 플레이북)
├── config/
│   └── books.yaml           # 도서별 메타데이터 레지스트리
├── prompts/                 # 프롬프트 템플릿 (코드와 분리)
│   ├── 01_translate.md
│   ├── 02_commentary.md
│   ├── 03_image_prompt.md
│   ├── 04_quality_check.md
│   └── 05_navieschool_intro.md
├── agents/                  # 단계별 전문 에이전트
│   ├── chunker.py           # Stage 1: 의미 단위 분할
│   ├── translator.py        # Stage 2: 청크별 번역
│   ├── commentator.py       # Stage 3: 해설 생성
│   ├── image_director.py    # Stage 4: 이미지 프롬프트 생성
│   ├── assembler.py         # Stage 5: 합본 + 품질 검수
│   ├── pdf_builder.py       # Stage 6: PDF 조판
│   └── versioner.py         # Stage 7: 버전 관리
├── input/                   # 영문 원문 (.md, .pdf, .txt)
├── chunks/                  # Stage 1 산출물
├── translated/              # Stage 2 산출물
├── commentary/              # Stage 3 산출물
├── images/                  # Stage 4 산출물 + 기존 이미지
├── versions/                # Stage 5 산출물 (버전별 최종 원고)
├── output/                  # Stage 6 산출물 (PDF)
├── state/                   # 파이프라인 진행 상태 (JSON)
├── fonts/                   # 폰트 파일
└── marketing/               # 마케팅 자료
```

---

## 📋 각 단계 상세 명세

### Stage 1: 원문 입력 & 청크 분할

| 항목 | 내용 |
|------|------|
| **에이전트** | `agents/chunker.py` |
| **입력** | `input/` 디렉터리의 영문 원문 파일 |
| **산출물** | `chunks/book_id/chunk_01.md` ~ `chunk_N.md` |
| **토큰 소모** | 0 (로컬 처리) |

- 마크다운 헤더(`##`, `###`) 기준으로 의미 단위 분할
- 각 청크는 2,000~4,000 토큰 이내로 제어
- 청크마다 해시값 생성 → 원문 수정 시 변경된 청크만 감지

### Stage 2: 책추남 스타일 번역

| 항목 | 내용 |
|------|------|
| **에이전트** | `agents/translator.py` |
| **프롬프트** | `prompts/01_translate.md` |
| **입력** | `chunks/book_id/chunk_XX.md` |
| **산출물** | `translated/book_id/chunk_XX.md` |
| **하네스** | 번역투 금지, 중학생 가독성, 원문 1문장도 누락 불가 |
| **자동 재시도** | 원문 대비 문장 수 ±20% 초과 시 자동 재번역 |

### Stage 3: 책추남 해설·해제 생성

| 항목 | 내용 |
|------|------|
| **에이전트** | `agents/commentator.py` |
| **프롬프트** | `prompts/02_commentary.md` + `prompts/05_navieschool_intro.md` |
| **입력** | `translated/book_id/` 전체 번역본 |
| **산출물** | `commentary/book_id/` (서문, 심층해설 4종, 해제, 나비퀘스트, 부록, 나비스쿨 소개) |
| **하네스** | 책추남 페르소나 고삐, 동양 고전 교차 인용 필수, 실전 가이드 포함 |

### Stage 4: 시네마틱 이미지 생성

| 항목 | 내용 |
|------|------|
| **에이전트** | `agents/image_director.py` |
| **프롬프트** | `prompts/03_image_prompt.md` |
| **입력** | 각 챕터 제목 + 핵심 키워드 |
| **산출물** | `images/book_id/scene_chXX.png` |
| **스타일** | 시네마틱 실사, 8K, 따뜻한 골든아워 조명, 자연 + 영성 모티프 |

### Stage 5: 합본 & 품질 게이트

| 항목 | 내용 |
|------|------|
| **에이전트** | `agents/assembler.py` |
| **프롬프트** | `prompts/04_quality_check.md` |
| **입력** | translated/ + commentary/ + images/ |
| **산출물** | `versions/book_id/vN_날짜_상태.md` |
| **품질 기준** | 원문 누락 0건, 번역투 0건, 이미지 매핑 완전, 목차 정합 |
| **자동 업그레이드** | 미달 시 해당 청크/해설만 Stage 2~3으로 되돌려 재생성 |

### Stage 6: PDF 조판

| 항목 | 내용 |
|------|------|
| **에이전트** | `agents/pdf_builder.py` |
| **설정** | `config/books.yaml` (표지, 시리즈 번호, 제목 등 동적 로드) |
| **입력** | `versions/book_id/` 최신 승인 원고 |
| **산출물** | `output/book_id_Kmong.pdf` + `output/book_id_Bookk.pdf` |

### Stage 7: 버전 저장 & Git 커밋

| 항목 | 내용 |
|------|------|
| **에이전트** | `agents/versioner.py` |
| **동작** | 원고 + PDF를 Git 커밋, 태그 부여, CHANGELOG 자동 작성 |
| **브랜치** | `book/도서ID` 브랜치에서 작업 → 완성 시 `main` 머지 |

---

## 🎛️ 사용법

### 새 책 전체 빌드
```
python pipeline.py run --book self-reliance
```

### 특정 단계만 재실행 (업그레이드)
```
python pipeline.py run --book self-reliance --from 3 --to 5
```

### 특정 청크만 재번역
```
python pipeline.py run --book self-reliance --stage 2 --chunk 3
```

### 현재 진행 상태 확인
```
python pipeline.py status --book self-reliance
```

---

## ✅ Human-in-the-Loop 체크포인트

| 체크포인트 | 위치 | 검토 내용 |
|-----------|------|----------|
| **A** | Stage 2 완료 후 | 번역 품질, 누락 여부, 톤앤매너 |
| **B** | Stage 5 완료 후 | 합본 원고 전체 검토, 해설 퀄리티 |
| **C** | Stage 6 완료 후 | PDF 최종 검수 (표지, 목차, 페이지 번호) |

파이프라인은 체크포인트에서 자동 일시정지됩니다.  
사용자가 `--approve` 하면 다음 단계로, `--revise 3` 하면 Stage 3부터 재실행합니다.

```
python pipeline.py approve --book self-reliance --checkpoint A
python pipeline.py revise --book self-reliance --from 3
```
