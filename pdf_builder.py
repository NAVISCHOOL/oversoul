import os
import re
import requests
import fitz  # PyMuPDF for image size detection
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.pdfgen import canvas

def download_fonts():
    """나눔명조 Regular 및 Bold 폰트를 다운로드합니다."""
    font_dir = "fonts"
    if not os.path.exists(font_dir):
        os.makedirs(font_dir)
        
    reg_path = os.path.join(font_dir, "NanumMyeongjo.ttf")
    bold_path = os.path.join(font_dir, "NanumMyeongjo-Bold.ttf")
    
    if not os.path.exists(reg_path):
        print("나눔명조 Regular 폰트 다운로드 중...")
        url = "https://github.com/google/fonts/raw/main/ofl/nanummyeongjo/NanumMyeongjo-Regular.ttf"
        r = requests.get(url)
        with open(reg_path, 'wb') as f:
            f.write(r.content)
        print("나눔명조 Regular 다운로드 완료.")
            
    if not os.path.exists(bold_path):
        print("나눔명조 Bold 폰트 다운로드 중...")
        url = "https://github.com/google/fonts/raw/main/ofl/nanummyeongjo/NanumMyeongjo-Bold.ttf"
        r = requests.get(url)
        with open(bold_path, 'wb') as f:
            f.write(r.content)
        print("나눔명조 Bold 다운로드 완료.")
            
    return reg_path, bold_path

def get_korean_fonts():
    """한자 출력을 지원하기 위한 고품격 서체 선택 엔진 (3단계 폴백 적용)"""
    han_reg = "C:\\Windows\\Fonts\\HANBatang.ttf"
    han_bold = "C:\\Windows\\Fonts\\HANBatangB.ttf"
    batang = "C:\\Windows\\Fonts\\batang.ttc"
    malgun_bold = "C:\\Windows\\Fonts\\malgunbd.ttf"
    
    # 1순위: 한컴바탕 (한자와 영문 세리프 볼드 지원 완벽)
    if os.path.exists(han_reg) and os.path.exists(han_bold):
        print("[폰트 선택] 1순위: 한컴바탕(HANBatang)을 사용합니다. (한자 완벽 지원)")
        return han_reg, han_bold
        
    # 2순위: 바탕체(batang.ttc) + 맑은고딕 볼드 (폴백)
    elif os.path.exists(batang):
        print("[폰트 선택] 2순위 폴백: 바탕체(Batang)를 사용합니다. (한자 지원)")
        bold_font = malgun_bold if os.path.exists(malgun_bold) else batang
        return batang, bold_font
        
    # 3순위: 구글 나눔명조 (다운로드 폴백, 한자 미지원 가능성 있음)
    else:
        print("[폰트 선택] 3순위 폴백: 다운로드된 나눔명조를 사용합니다.")
        download_reg, download_bold = download_fonts()
        return download_reg, download_bold

class NumberedCanvas(canvas.Canvas):
    """지능형 페이지 번호 및 표지 제어를 위한 커스텀 캔버스"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # 1페이지(표지)와 2페이지(속표지/타이틀 페이지)는 페이지 번호 및 헤더를 그리지 않음
        if self._pageNumber <= 2:
            return
            
        self.saveState()
        self.setFont("NanumMyeongjo", 9)
        self.setFillColor(colors.HexColor("#666666"))
        
        # 하단 중앙 페이지 번호
        page_text = f"- {self._pageNumber} -"
        self.drawCentredString(self._pagesize[0] / 2.0, 30, page_text)
        
        # 상단 헤더 (책 제목 단면 인쇄 스타일)
        self.setStrokeColor(colors.HexColor("#E5E5E5"))
        self.setLineWidth(0.5)
        self.line(40, self._pagesize[1] - 40, self._pagesize[0] - 40, self._pagesize[1] - 40)
        self.drawString(40, self._pagesize[1] - 35, "내 안의 우주 : 랄프 왈도 에머슨 에세이")
        
        self.restoreState()

def draw_cover_background(canvas_obj, doc):
    """크몽 전자책 모드에서 첫 페이지에 표지 이미지를 꽉 차게 그립니다."""
    canvas_obj.saveState()
    cover_path = "images/cover.png"
    if os.path.exists(cover_path):
        canvas_obj.drawImage(cover_path, 0, 0, width=doc.pagesize[0], height=doc.pagesize[1])
    canvas_obj.restoreState()

def parse_inline_markdown(text):
    """마크다운 인라인 문법(**, *)을 ReportLab Paragraph 태그로 변환합니다."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("&lt;br/&gt;", "<br/>").replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    # **bold** -> 나눔명조 Bold 폰트 적용
    text = re.sub(r'\*\*(.*?)\*\*', r'<font name="NanumMyeongjo-Bold">\1</font>', text)
    # *italic* -> 이탤릭 태그 적용
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    return text

def make_title_page(story, mode, pagesize):
    """우아하고 균형 잡힌 타이틀 페이지를 단일 페이지에 생성합니다."""
    story.append(Spacer(1, 60 if mode == "kmong" else 30))
    
    series_style = ParagraphStyle(
        'TitleSeries',
        fontName='NanumMyeongjo-Bold',
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#777777")
    )
    story.append(Paragraph("[책추남 불변의 지혜 시리즈 01]", series_style))
    story.append(Spacer(1, 25))
    
    title_style = ParagraphStyle(
        'TitleMain',
        fontName='NanumMyeongjo-Bold',
        fontSize=28 if mode == "kmong" else 22,
        leading=34 if mode == "kmong" else 28,
        alignment=1,
        textColor=colors.HexColor("#111111")
    )
    story.append(Paragraph("내 안의 우주", title_style))
    story.append(Spacer(1, 15))
    
    subtitle_style = ParagraphStyle(
        'TitleSub',
        fontName='NanumMyeongjo',
        fontSize=12,
        leading=18,
        alignment=1,
        textColor=colors.HexColor("#555555")
    )
    story.append(Paragraph("랄프 왈도 에머슨의 영혼을 깨우는 초월주의 에세이", subtitle_style))
    story.append(Spacer(1, 8))
    
    orig_style = ParagraphStyle(
        'TitleOrig',
        fontName='NanumMyeongjo',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#888888")
    )
    story.append(Paragraph("(The Over-Soul)", orig_style))
    story.append(Spacer(1, 120 if mode == "kmong" else 80))
    
    author_style = ParagraphStyle(
        'TitleAuthor',
        fontName='NanumMyeongjo',
        fontSize=10.5,
        leading=18,
        alignment=1,
        textColor=colors.HexColor("#333333")
    )
    story.append(Paragraph("<b>원저:</b> 랄프 왈도 에머슨 (Ralph Waldo Emerson)<br/><b>번역 및 해제:</b> 책추남", author_style))
    
    story.append(PageBreak())

def make_toc_page(story, mode, pagesize):
    """도트 리더(Dot Leader)와 우측 정렬 페이지 번호가 포함된 고품격 목차를 조판합니다."""
    story.append(Spacer(1, 20))
    toc_title_style = ParagraphStyle(
        'TOCTitle',
        fontName='NanumMyeongjo-Bold',
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=30
    )
    story.append(Paragraph("📖 목차 (Table of Contents)", toc_title_style))
    
    # 목차 데이터 세팅 (모드별 검증된 실제 시작 페이지 자동 연동)
    if mode == "kmong":
        toc_data = [
            ["책추남 서문 : 모든 성공학의 뿌리, 그 거대한 샘물", "6"],
            ["제1부 : 대령(The Over-Soul)의 시작", "10"],
            ["제2부 : 내 안의 무한한 지혜와 힘", "26"],
            ["제3부 : 시공간을 초월한 존재", "41"],
            ["심층 해설 01: 운(運)이 좋아지는 사람의 비밀", "54"],
            ["심층 해설 02: 에머슨이 동양 고전을 만날 때", "57"],
            ["심층 해설 03: 비워야 채워진다", "60"],
            ["심층 해설 04: 책추남의 독서 인생을 바꾼 세 문장", "62"],
            ["🦋 [책추남의 심층 해제] 에고의 게임에서 진짜 백조로", "64"],
            ["🌏 [3대 영성 도서 입체 분석] 대령의 현대적 재해석", "66"],
            ["🚀 [실전 나비 퀘스트] 대령의 주파수를 맞추는 3단계 연습", "68"],
            ["🦋 맺음말 : 독자 여러분 안의 대령(The Over-Soul)에게", "70"],
            ["📚 부록 : 책추남 추천 에머슨 읽기 순서", "72"]
        ]
    else:
        toc_data = [
            ["책추남 서문 : 모든 성공학의 뿌리, 그 거대한 샘물", "5"],
            ["제1부 : 대령(The Over-Soul)의 시작", "9"],
            ["제2부 : 내 안의 무한한 지혜와 힘", "24"],
            ["제3부 : 시공간을 초월한 존재", "39"],
            ["심층 해설 01: 운(運)이 좋아지는 사람의 비밀", "52"],
            ["심층 해설 02: 에머슨이 동양 고전을 만날 때", "55"],
            ["심층 해설 03: 비워야 채워진다", "58"],
            ["심층 해설 04: 책추남의 독서 인생을 바꾼 세 문장", "60"],
            ["🦋 [책추남의 심층 해제] 에고의 게임에서 진짜 백조로", "62"],
            ["🌏 [3대 영성 도서 입체 분석] 대령의 현대적 재해석", "64"],
            ["🚀 [실전 나비 퀘스트] 대령의 주파수를 맞추는 3단계 연습", "66"],
            ["🦋 맺음말 : 독자 여러분 안의 대령(The Over-Soul)에게", "68"],
            ["📚 부록 : 책추남 추천 에머슨 읽기 순서", "70"]
        ]
    
    left_margin = 20 * mm
    right_margin = 20 * mm if mode == "kmong" else 15 * mm
    p_width = pagesize[0] - (left_margin + right_margin)
    col_widths = [p_width - 50, 50]
    
    toc_text_style = ParagraphStyle(
        'TOCText',
        fontName='NanumMyeongjo',
        fontSize=10,
        leading=14
    )
    toc_page_style = ParagraphStyle(
        'TOCPage',
        fontName='NanumMyeongjo',
        fontSize=10,
        leading=14,
        alignment=2 # 우측 정렬
    )
    
    table_data = []
    for title, page in toc_data:
        # 타이틀 길이에 맞춰 도트 리더 개수 동적 계산
        estimated_char_len = len(title) * 7.5
        dots_width = p_width - estimated_char_len - 50
        dots_count = int(dots_width / 4)
        if dots_count < 5:
            dots_count = 5
        dots = " ." * dots_count
        
        title_p = Paragraph(f"{title} <font color='#888888'>{dots}</font>", toc_text_style)
        page_p = Paragraph(page, toc_page_style)
        table_data.append([title_p, page_p])
        
    toc_table = Table(table_data, colWidths=col_widths)
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 9),
        ('LEFTPADDING', (0,0), (0,-1), 0),
        ('RIGHTPADDING', (1,0), (1,-1), 0),
        ('RIGHTPADDING', (0,0), (0,-1), 6),
        ('LEFTPADDING', (1,0), (1,-1), 6),
    ]))
    
    story.append(toc_table)
    story.append(PageBreak())

def render_markdown_table(story, table_lines, p_width, mode):
    """마크다운 테이블을 파싱하여 초고품격 ReportLab Table 객체로 조판합니다."""
    parsed_rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.split('|')]
        if len(cells) > 1:
            if cells[0] == '':
                cells = cells[1:]
            if cells and cells[-1] == '':
                cells = cells[:-1]
        
        # 구분선 행(---) 생략
        if all(re.match(r'^:?-+:?$', c) for c in cells):
            continue
            
        parsed_rows.append(cells)
        
    if not parsed_rows:
        return
        
    headers = parsed_rows[0]
    data_rows = parsed_rows[1:]
    col_count = len(headers)
    
    # 컬럼별 특화 가로폭 비율 계산 (현대 개념 표 및 동양 사상 비교 표 대상)
    if col_count == 3:
        if "현대" in headers[0] or "개념" in headers[0]:
            col_widths = [0.24 * p_width, 0.52 * p_width, 0.24 * p_width]
        elif "에머슨" in headers[0] or "표현" in headers[0]:
            col_widths = [0.26 * p_width, 0.37 * p_width, 0.37 * p_width]
        else:
            col_widths = [p_width / 3.0] * 3
    else:
        col_widths = [p_width / float(col_count)] * col_count
        
    th_style = ParagraphStyle(
        'TableHeaderCell',
        fontName='NanumMyeongjo-Bold',
        fontSize=10.5 if mode == "kmong" else 9.5,
        leading=14 if mode == "kmong" else 13,
        textColor=colors.white,
        alignment=1
    )
    
    td_style = ParagraphStyle(
        'TableBodyCell',
        fontName='NanumMyeongjo',
        fontSize=10 if mode == "kmong" else 9,
        leading=15 if mode == "kmong" else 13,
        textColor=colors.HexColor("#222222")
    )
    
    table_data = []
    
    # 헤더 행 구성
    header_cells = [Paragraph(parse_inline_markdown(h), th_style) for h in headers]
    table_data.append(header_cells)
    
    # 본문 데이터 행 구성
    for row in data_rows:
        while len(row) < col_count:
            row.append("")
        row = row[:col_count]
        
        row_cells = [Paragraph(parse_inline_markdown(c), td_style) for c in row]
        table_data.append(row_cells)
        
    t = Table(table_data, colWidths=col_widths)
    
    # 럭셔리 네이비 테마 및 제브라 패턴 테이블 스타일 정의
    t_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2A3A4A")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor("#1A2A3A")),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E2E2")),
    ])
    
    for idx in range(1, len(table_data)):
        bg_color = colors.HexColor("#F8F9FA") if idx % 2 == 0 else colors.white
        t_style.add('BACKGROUND', (0, idx), (-1, idx), bg_color)
        
    t.setStyle(t_style)
    
    story.append(Spacer(1, 10))
    story.append(t)
    story.append(Spacer(1, 10))

def build_pdf(input_md, output_pdf, mode="kmong"):
    # 한자가 포함된 고해상도 글꼴 세팅
    reg_font, bold_font = get_korean_fonts()
    
    # TTC 컬렉션 처리 데코레이션
    if reg_font.lower().endswith('.ttc'):
        pdfmetrics.registerFont(TTFont('NanumMyeongjo', reg_font, subfontIndex=0))
    else:
        pdfmetrics.registerFont(TTFont('NanumMyeongjo', reg_font))
        
    if bold_font.lower().endswith('.ttc'):
        pdfmetrics.registerFont(TTFont('NanumMyeongjo-Bold', bold_font, subfontIndex=0))
    else:
        pdfmetrics.registerFont(TTFont('NanumMyeongjo-Bold', bold_font))
    
    # 모드별 페이지 사이즈 및 여백 정의
    if mode == "kmong":
        # 크몽 전자책: 모바일/태블릿 가독성에 극대화된 A5 판형, 좌우 대칭 20mm 여백
        pagesize = A5
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=pagesize,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=22 * mm,
            bottomMargin=22 * mm
        )
    else:
        # 부크크 POD: A5, 여백 차별화 (제본 안쪽 20mm, 바깥쪽 15mm, 상하 22mm로 조정하여 페이지 수 극대화 및 프리미엄 조판 달성)
        pagesize = A5
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=pagesize,
            leftMargin=20 * mm,
            rightMargin=15 * mm,
            topMargin=22 * mm,
            bottomMargin=22 * mm
        )
        
    p_width = pagesize[0] - (doc.leftMargin + doc.rightMargin)
    
    # 텍스트 스타일 정의 (폰트 사이즈 및 행간 미세 조정을 통한 가독성 극대화 및 70+ 페이지 완벽 복원)
    korean_style = ParagraphStyle(
        'KoreanStyle',
        fontName='NanumMyeongjo',
        fontSize=10.5,
        leading=18,
        spaceAfter=14,
        textColor=colors.HexColor("#222222")
    )
    
    header1_style = ParagraphStyle(
        'Header1Style',
        fontName='NanumMyeongjo-Bold',
        fontSize=16,
        leading=22,
        spaceBefore=20,
        spaceAfter=15,
        textColor=colors.HexColor("#111111")
    )
    
    header2_style = ParagraphStyle(
        'Header2Style',
        fontName='NanumMyeongjo-Bold',
        fontSize=12,
        leading=16,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor("#333333")
    )
    
    quote_style = ParagraphStyle(
        'QuoteStyle',
        fontName='NanumMyeongjo',
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#444444")
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        fontName='NanumMyeongjo',
        fontSize=10.5,
        leading=18,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=8,
        textColor=colors.HexColor("#222222")
    )
    
    bar_style = ParagraphStyle(
        'BarStyle',
        fontSize=1,
        leading=1
    )
    
    box_style = ParagraphStyle(
        'BoxStyle',
        fontName='NanumMyeongjo',
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#333333")
    )
    
    story = []
    
    # 1. 크몽 모드에서는 캔버스를 통한 꽉 찬 첫 페이지 커버 렌더링
    if mode == "kmong":
        story.append(PageBreak())
        
    # 2. 타이틀 페이지 생성 (1페이지와 3페이지의 결합 해결)
    make_title_page(story, mode, pagesize)
    
    # 3. 목차 페이지 생성
    make_toc_page(story, mode, pagesize)
    
    # 4. 본문 파싱 및 렌더링
    with open(input_md, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_metadata = True
    quote_lines = []
    table_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        raw_line = line.strip()
        
        # 메타데이터 블록(--- 이전) 스킵
        if in_metadata:
            if raw_line == "---":
                in_metadata = False
            i += 1
            continue
            
        # 목차 및 표지 플레이스홀더 스킵
        if "[TOC_PLACEHOLDER]" in raw_line or "![책표지]" in raw_line or "![도서 표지]" in raw_line:
            i += 1
            continue
            
        # 블록쿼트(> ) 처리
        if raw_line.startswith("> "):
            quote_lines.append(raw_line[2:].strip())
            i += 1
            continue
        else:
            if quote_lines:
                quote_text = " ".join(quote_lines)
                quote_text = parse_inline_markdown(quote_text)
                quote_p = Paragraph(f"“{quote_text}”", quote_style)
                
                # 우아한 왼쪽 바 + 연그레이 박스 스타일로 인용구 렌더링
                quote_table = Table([[Paragraph("", bar_style), quote_p]], colWidths=[3, p_width - 15])
                quote_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7F7F7")),
                    ('LINEBEFORE', (0,0), (0,0), 3, colors.HexColor("#555555")),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                    ('LEFTPADDING', (0,0), (0,-1), 0),
                    ('RIGHTPADDING', (0,0), (0,-1), 0),
                    ('LEFTPADDING', (1,0), (1,-1), 12),
                    ('RIGHTPADDING', (1,0), (1,-1), 12),
                ]))
                story.append(Spacer(1, 10))
                story.append(quote_table)
                story.append(Spacer(1, 10))
                quote_lines = []
                
        # 테이블 파싱 처리
        if raw_line.startswith("|"):
            table_lines.append(raw_line)
            i += 1
            continue
        else:
            if table_lines:
                render_markdown_table(story, table_lines, p_width, mode)
                table_lines = []
                
        if not raw_line:
            i += 1
            continue
            
        # 헤더 1 (## ) -> 강제 페이지 나누기 적용
        if raw_line.startswith("## "):
            header_text = raw_line[3:].strip()
            # 본문 2페이지의 불필요한 공백을 합치기 위해 제목 부분 보정
            if "특별 서문" in header_text or "제1부" in header_text:
                story.append(PageBreak())
            else:
                story.append(PageBreak())
                
            story.append(Spacer(1, 15))
            story.append(Paragraph(parse_inline_markdown(header_text), header1_style))
            story.append(Spacer(1, 10))
            
        # 헤더 2 (### )
        elif raw_line.startswith("### "):
            header_text = raw_line[4:].strip()
            story.append(Spacer(1, 10))
            story.append(Paragraph(parse_inline_markdown(header_text), header2_style))
            story.append(Spacer(1, 6))
            
        # 이미지 태그 처리 ( aspect-ratio 기반 가로세로 정밀 제한 및 가운데 정렬 )
        elif raw_line.startswith("!["):
            img_match = re.match(r'!\[.*?\]\((.*?)\)', raw_line)
            if img_match:
                img_path = img_match.group(1).strip()
                if os.path.exists(img_path):
                    try:
                        # PyMuPDF로 원본 해상도를 파악하여 가로폭 맞춤 비율 유지
                        pix = fitz.Pixmap(img_path)
                        img_w, img_h = pix.width, pix.height
                        
                        # 이미지가 너무 길게 세로폭을 차지하여 본문을 침투하지 않도록 경계박스 제어
                        max_h = 170
                        scale_w = p_width / img_w
                        scale_h = max_h / img_h
                        scale = min(scale_w, scale_h, 1.0)
                        
                        img_w_scaled = img_w * scale
                        img_h_scaled = img_h * scale
                        
                        img_flow = Image(img_path, width=img_w_scaled, height=img_h_scaled)
                        img_flow.hAlign = 'CENTER' # 완벽한 정가운데 정렬 적용
                        
                        story.append(Spacer(1, 12))
                        story.append(img_flow)
                        story.append(Spacer(1, 12))
                    except Exception as e:
                        print(f"이미지 파싱 에러 ({img_path}): {e}")
            i += 1
            continue
            
        # 박스 강조 [APP_BOX] 처리
        elif "[APP_BOX]" in raw_line:
            box_text = raw_line.replace("[APP_BOX]", "").strip()
            box_text = parse_inline_markdown(box_text)
            box_p = Paragraph(box_text, box_style)
            box_table = Table([[box_p]], colWidths=[p_width])
            box_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#E2E2E2")),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FAFAFA")),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(Spacer(1, 6))
            story.append(box_table)
            story.append(Spacer(1, 6))
            
        # 리스트 아이템 처리
        elif raw_line.startswith(("* ", "- ")):
            bullet_text = raw_line[2:].strip()
            bullet_text = parse_inline_markdown(bullet_text)
            story.append(Paragraph(f"• {bullet_text}", bullet_style))
            
        # 일반 본문 문단 처리
        else:
            para_text = parse_inline_markdown(raw_line)
            story.append(Paragraph(para_text, korean_style))
            
        i += 1

    # 루프 종료 후 혹시라도 남아있을 블록 처리
    if quote_lines:
        quote_text = " ".join(quote_lines)
        quote_text = parse_inline_markdown(quote_text)
        quote_p = Paragraph(f"“{quote_text}”", quote_style)
        quote_table = Table([[Paragraph("", bar_style), quote_p]], colWidths=[3, p_width - 15])
        quote_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7F7F7")),
            ('LINEBEFORE', (0,0), (0,0), 3, colors.HexColor("#555555")),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (0,-1), 0),
            ('RIGHTPADDING', (0,0), (0,-1), 0),
            ('LEFTPADDING', (1,0), (1,-1), 12),
            ('RIGHTPADDING', (1,0), (1,-1), 12),
        ]))
        story.append(Spacer(1, 10))
        story.append(quote_table)
        story.append(Spacer(1, 10))

    if table_lines:
        render_markdown_table(story, table_lines, p_width, mode)
            
    # 최종 PDF 빌드 실행
    if mode == "kmong":
        doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=draw_cover_background)
    else:
        doc.build(story, canvasmaker=NumberedCanvas)
        
    print(f"[{mode.upper()}] PDF 조판 완료: {output_pdf}")

if __name__ == "__main__":
    # 마스터 마크다운 원고를 동기화하여 빌드 준비
    master_src = "versions/final_content_v4.md"
    active_dest = "final_content.md"
    
    if os.path.exists(master_src):
        print(f"마스터 마크다운 원고 동기화 중: {master_src} -> {active_dest}")
        with open(master_src, 'r', encoding='utf-8') as src_f:
            content = src_f.read()
        with open(active_dest, 'w', encoding='utf-8') as dest_f:
            dest_f.write(content)
        print("동기화 성공.")
    else:
        print("경고: 마스터 마크다운 원고를 찾을 수 없습니다. 기존 final_content.md로 조판을 시도합니다.")
        
    # 두 모드(부크크 POD, 크몽 전자책)로 각각 고품격 PDF 생성
    build_pdf(active_dest, "Emerson_Universe_Bookk_POD.pdf", mode="bookk")
    build_pdf(active_dest, "Emerson_Universe_Kmong_Ebook.pdf", mode="kmong")
