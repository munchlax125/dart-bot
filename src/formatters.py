# formatters.py - 단순화된 안전 버전
"""
텍스트 포맷팅, HTML 변환, 사용자 입력 정제 등 표현(Presentation) 계층을 담당합니다.
"""
import bleach
import re
import logging

logger = logging.getLogger(__name__)

def format_analysis_result(text: str) -> str:
    """분석 결과를 HTML로 변환합니다."""
    try:
        # 1차 시도: markdown-it 사용
        from markdown_it import MarkdownIt
        md = MarkdownIt()
        html_content = md.render(text)
        return f'<div class="analysis-container">{html_content}</div>'
        
    except Exception as e:
        logger.warning(f"MarkdownIt 사용 실패: {e}")
        # 2차 시도: 수동 HTML 변환
        return format_with_simple_html(text)

def format_with_simple_html(text: str) -> str:
    """간단한 HTML 포맷팅 (안전한 방법)"""
    try:
        html_content = str(text)
        
        # 기본적인 마크다운 변환
        # 헤더 변환
        html_content = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        
        # 굵은 글씨 변환
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        
        # 리스트 변환 (간단한 방법)
        lines = html_content.split('\n')
        result_lines = []
        in_list = False
        
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                result_lines.append(f'<li>{stripped_line[2:]}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        html_content = '\n'.join(result_lines)
        
        # 구분선 변환
        html_content = re.sub(r'^---+$', r'<hr>', html_content, flags=re.MULTILINE)
        
        # 줄바꿈 변환
        html_content = html_content.replace('\n', '<br>\n')
        
        return f'<div class="analysis-container">{html_content}</div>'
        
    except Exception as e:
        logger.error(f"HTML 변환 실패: {e}")
        # 최종 대체: 단순 텍스트
        safe_text = bleach.clean(str(text), tags=[], attributes={}, strip=True)
        return f'<div class="analysis-container"><pre style="white-space: pre-wrap; font-family: inherit;">{safe_text}</pre></div>'

def sanitize_input(text: str) -> str:
    """사용자 입력을 안전하게 정제합니다."""
    if not isinstance(text, str): 
        return ""
    
    try:
        # bleach 사용
        sanitized_text = bleach.clean(text, tags=[], attributes={}, strip=True)
        return sanitized_text.strip()[:1000]
    except Exception as e:
        logger.warning(f"Bleach 정제 실패: {e}")
        # 기본적인 정제
        clean_text = re.sub(r'<[^>]+>', '', str(text))
        clean_text = clean_text.replace('<', '&lt;').replace('>', '&gt;')
        return clean_text.strip()[:1000]