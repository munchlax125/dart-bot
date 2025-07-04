# formatters.py - Fixed version
"""
텍스트 포맷팅, HTML 변환, 사용자 입력 정제 등 표현(Presentation) 계층을 담당합니다.
"""
from markdown_it import MarkdownIt
import bleach

def format_analysis_result(text: str) -> str:
    """Markdown-it 라이브러리를 사용해 분석 결과를 HTML로 안전하고 안정적으로 변환합니다."""
    try:
        # MarkdownIt 인스턴스 생성 (올바른 방식)
        md = MarkdownIt('commonmark', {
            'html': True,  # HTML 태그 허용
            'linkify': True,  # 링크 자동 변환
            'typographer': True  # 타이포그래피 개선
        }).enable([
            'table',  # 테이블 지원
            'strikethrough',  # 취소선 지원
        ])
        
        # 마크다운을 HTML로 변환
        html_content = md.render(text)
        return f'<div class="analysis-container">{html_content}</div>'
        
    except Exception as e:
        # MarkdownIt 오류 시 대체 방법 사용
        print(f"MarkdownIt 오류: {e}")
        return format_analysis_result_fallback(text)

def format_analysis_result_fallback(text: str) -> str:
    """MarkdownIt 실패 시 사용하는 대체 포맷팅 함수"""
    try:
        # 간단한 마크다운 변환 (수동)
        html_content = text
        
        # 기본적인 마크다운 변환
        import re
        
        # 헤더 변환
        html_content = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        
        # 굵은 글씨 변환
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        
        # 목록 변환
        html_content = re.sub(r'^- (.*$)', r'<li>\1</li>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html_content, flags=re.DOTALL)
        
        # 구분선 변환
        html_content = re.sub(r'^---$', r'<hr>', html_content, flags=re.MULTILINE)
        
        # 줄바꿈 변환
        html_content = html_content.replace('\n', '<br>')
        
        return f'<div class="analysis-container">{html_content}</div>'
        
    except Exception as e:
        # 최종 대체 방법: 단순 텍스트
        print(f"대체 포맷팅도 실패: {e}")
        escaped_text = bleach.clean(text, tags=[], attributes={}, strip=True)
        return f'<div class="analysis-container"><pre>{escaped_text}</pre></div>'

def sanitize_input(text: str) -> str:
    """사용자 입력을 bleach를 사용해 안전하게 정제합니다."""
    if not isinstance(text, str): 
        return ""
    
    try:
        # bleach를 사용한 안전한 정제
        sanitized_text = bleach.clean(text, tags=[], attributes={}, strip=True)
        return sanitized_text.strip()[:1000]
    except Exception as e:
        # bleach 실패 시 기본적인 정제
        print(f"Bleach 오류: {e}")
        import re
        # 기본적인 HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', str(text))
        # 특수 문자 이스케이프
        clean_text = clean_text.replace('<', '&lt;').replace('>', '&gt;')
        return clean_text.strip()[:1000]