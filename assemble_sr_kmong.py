"""Self-Reliance 크몽용 전자책 최종 합본 스크립트"""
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))

def read(path):
    with open(os.path.join(ROOT, path), 'r', encoding='utf-8') as f:
        return f.read()

def main():
    # 1. 표지 + 속표지 + 목차
    front = """![표지](images/sr_cover.png)

---

# 자기 신뢰 (Self-Reliance)

### 책추남 불변의 지혜 시리즈 02

**랄프 왈도 에머슨 지음 | 책추남 번역·편역·해설**

---

> *"아무것도 당신에게 평화를 가져다줄 수 없습니다 — 오직 당신 자신뿐입니다."*
> *— 랄프 왈도 에머슨*

---

## 목차

**본문**
- 서시 — 에머슨의 시
- 제1부: 너 자신을 믿어라 — 천재성의 발견
- 제2부: 비동조자의 길 — 순응을 거부하라
- 제3부: 영혼의 샘, 그리고 자기 신뢰의 혁명

**책추남 해설**
- 📖 책추남 서문 — 세상에서 가장 위험한 에세이
- 🔥 심층 해설 01 — 운(運)이 좋아지는 사람의 비밀
- 🌏 심층 해설 02 — 에머슨이 동양 고전을 만날 때
- 🦋 심층 해설 03 — 비워야 채워진다: 실전 수행법 3가지
- 📚 심층 해설 04 — 독서 인생을 바꾼 세 문장
- 🦢 책추남 심층 해제 — 에고의 닭장에서 영혼의 백조로
- 📊 3대 영성 도서 입체 분석
- 🎯 실전 나비 퀘스트 3단계

**부록**
- 추천 도서
- 🦋 나비스쿨 & 책추남 코코치 소개

---

"""
    # 2. 번역 본문
    ch1 = read("translated/self-reliance/chunk_01.md")
    ch2 = read("translated/self-reliance/chunk_02.md")
    ch3 = read("translated/self-reliance/chunk_03.md")
    
    body = f"""
![제1부](images/sr_ch1.png)

{ch1}

---

![제2부](images/sr_ch2.png)

{ch2}

---

![제3부](images/sr_ch3.png)

{ch3}

---

"""
    # 3. 해설
    commentary = read("commentary/self-reliance/commentary.md")
    
    # 4. 나비스쿨 소개
    navi = read("config/navieschool_intro.md")
    
    # 5. 크몽 저작권 & 면책
    colophon = """
---

## 저작권 안내

**자기 신뢰 (Self-Reliance)**
책추남 불변의 지혜 시리즈 02

- **원저:** Ralph Waldo Emerson, *Self-Reliance* (1841, Roycrofters Edition 1908)
- **번역·편역·해설:** 책추남 코코치
- **출판:** 나비스쿨 출판
- **초판 발행:** 2026년 5월

본 전자책의 번역, 해설, 편역 콘텐츠에 대한 저작권은 나비스쿨에 있습니다.
원문(Self-Reliance, 1841)은 퍼블릭 도메인 저작물입니다.
무단 복제·전재·재배포를 금합니다.

📺 책추남TV: https://www.youtube.com/booktuber
🌐 나비스쿨: https://navischool.kr

---

*애벌레가 나비로 날아오르듯, 나답게 자유롭게 충만하게!*
*이제 당신이 날아오를 차례입니다!* 🦋
"""

    # 합본
    final = front + body + "\n\n" + commentary + "\n\n---\n\n" + navi + colophon
    
    # 저장
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 크몽용 최종본
    kmong_path = os.path.join(ROOT, "output", f"self_reliance_kmong_{ts}.md")
    os.makedirs(os.path.dirname(kmong_path), exist_ok=True)
    with open(kmong_path, 'w', encoding='utf-8') as f:
        f.write(final)
    
    # 버전 파일
    ver_path = os.path.join(ROOT, "versions", "self-reliance", f"kmong_v1.0_{ts}.md")
    os.makedirs(os.path.dirname(ver_path), exist_ok=True)
    with open(ver_path, 'w', encoding='utf-8') as f:
        f.write(final)
    
    # 활성 원고 갱신
    active_path = os.path.join(ROOT, "final_self_reliance.md")
    with open(active_path, 'w', encoding='utf-8') as f:
        f.write(final)
    
    print(f"  크몽용 전자책 합본 완료!")
    print(f"  총 분량: {len(final):,}자")
    print(f"  크몽 파일: {kmong_path}")
    print(f"  버전 파일: {ver_path}")
    print(f"  활성 원고: {active_path}")

if __name__ == "__main__":
    main()
