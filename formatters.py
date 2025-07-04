# formatters.py
"""
텍스트 포맷팅, HTML 변환, 사용자 입력 정제 등 표현(Presentation) 계층을 담당합니다.
"""
from markdown_it import MarkdownIt
import bleach

def format_analysis_result(text: str) -> str:
    """Markdown-it 라이브러리를 사용해 분석 결과를 HTML로 안전하고 안정적으로 변환합니다."""
    md = MarkdownIt(html=True) # allow html tags
    # NEW: 검증된 마크다운 라이브러리를 사용하여 안정성 확보
    html_content = md.render(text)
    return f'<div class="analysis-container">{html_content}</div>'

def sanitize_input(text: str) -> str:
    """사용자 입력을 bleach를 사용해 안전하게 정제합니다."""
    if not isinstance(text, str): return ""
    # NEW: 보안에 취약한 정규식 대신 bleach 라이브러리 사용
    sanitized_text = bleach.clean(text, tags=[], attributes={}, strip=True)
    return sanitized_text.strip()[:1000]