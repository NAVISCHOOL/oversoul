"""Self-Reliance 최종 합본 스크립트"""
import os, shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))

# 나비스쿨 소개문
NAVI_INTRO = """
---

## 🦋 나비스쿨(NavieSchool) & 피닉스 퓨처 스쿨 소개

**나비스쿨**은 '지식의 나비효과'를 믿는 평생학습 커뮤니티입니다. 한 권의 책, 하나의 통찰이 당신의 인생 전체를 바꿀 수 있다는 믿음으로, 고전의 지혜를 현대적 언어로 재해석하여 전달합니다.

**피닉스 퓨처 스쿨**은 나비스쿨의 미래교육 브랜드로, AI 시대에 '생각하는 힘'과 '자기 신뢰'를 키우는 실전 프로그램을 운영합니다.

- 📺 유튜브: **책추남TV** — 고전 해설, 영성 도서 리뷰, 실전 수행법
- 🌐 웹사이트: navischool.com
- 📧 문의: navischool@gmail.com

> *"미운 오리 새끼는 자기가 백조였다는 것을 깨달을 때 날개를 펼칩니다."*
> *— 책추남*

---
"""

# 표지 + 속표지
FRONT_MATTER = """![표지](images/sr_cover.png)

---

# 자기 신뢰 (Self-Reliance)

### 책추남 불변의 지혜 시리즈 02

**랄프 왈도 에머슨 지음 | 책추남 번역·편역·해설**

---

> *"아무것도 당신에게 평화를 가져다줄 수 없습니다 — 오직 당신 자신뿐입니다."*
> *— 에머슨*

---

## 목차

- **서시** — 에머슨의 시
- **제1부: 너 자신을 믿어라** — 천재성의 발견
- **제2부: 비동조자의 길** — 순응을 거부하라
- **제3부: 영혼의 샘, 그리고 자기 신뢰의 혁명** — 직관과 실천
- **책추남 서문** — 세상에서 가장 위험한 에세이
- **심층 해설 01** — 운이 좋아지는 사람의 비밀
- **심층 해설 02** — 에머슨이 동양 고전을 만날 때
- **심층 해설 03** — 비워야 채워진다: 실전 수행법
- **심층 해설 04** — 독서 인생을 바꾼 세 문장
- **책추남 심층 해제** — 에고의 닭장에서 영혼의 백조로
- **실전 나비 퀘스트 3단계**
- **나비스쿨 & 피닉스 퓨처 스쿨 소개**

---

"""

def read(path):
    with open(os.path.join(ROOT, path), 'r', encoding='utf-8') as f:
        return f.read()

def main():
    parts = [
        FRONT_MATTER,
        "![제1부 이미지](images/sr_ch1.png)\n\n",
        read("translated/self-reliance/chunk_01.md"),
        "\n\n---\n\n![제2부 이미지](images/sr_ch2.png)\n\n",
        read("translated/self-reliance/chunk_02.md"),
        "\n\n---\n\n![제3부 이미지](images/sr_ch3.png)\n\n",
        read("translated/self-reliance/chunk_03.md"),
        "\n\n---\n\n",
        read("commentary/self-reliance/commentary.md"),
        NAVI_INTRO,
    ]
    
    final = "\n".join(parts)
    
    # 버전 파일
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    ver_path = os.path.join(ROOT, "versions", "self-reliance", f"v1.0_{ts}.md")
    with open(ver_path, 'w', encoding='utf-8') as f:
        f.write(final)
    
    # 활성 원고
    active_path = os.path.join(ROOT, "final_self_reliance.md")
    with open(active_path, 'w', encoding='utf-8') as f:
        f.write(final)
    
    print(f"합본 완료: {len(final):,}자")
    print(f"버전 파일: {ver_path}")
    print(f"활성 원고: {active_path}")

if __name__ == "__main__":
    main()
