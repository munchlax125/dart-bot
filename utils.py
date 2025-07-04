"""
유틸리티 함수 모듈
- HTML 포맷팅
- 데이터 변환
- 검증 함수들
"""

import re
import html
from typing import Dict, Any


def format_analysis_result(text: str) -> str:
    """분석 결과를 HTML 형식으로 변환"""
    # HTML 이스케이프 (안전성)
    text = html.escape(text)
    
    # 1. 헤딩 변환 (순서 중요 - 큰 것부터)
    text = re.sub(
        r'^### (.*?)$', 
        r'<h3 style="color: #667eea; font-size: 18px; font-weight: bold; margin: 20px 0 10px 0;">\1</h3>', 
        text, 
        flags=re.MULTILINE
    )
    text = re.sub(
        r'^## (.*?)$', 
        r'<h2 style="color: #667eea; font-size: 20px; font-weight: bold; margin: 25px 0 15px 0;">\1</h2>', 
        text, 
        flags=re.MULTILINE
    )
    text = re.sub(
        r'^# (.*?)$', 
        r'<h1 style="color: #667eea; font-size: 24px; font-weight: bold; margin: 30px 0 20px 0;">\1</h1>', 
        text, 
        flags=re.MULTILINE
    )
    
    # 2. 볼드/이탤릭 (순서 중요 - ** 먼저)
    text = re.sub(
        r'\*\*(.*?)\*\*', 
        r'<strong style="color: #764ba2; font-weight: bold;">\1</strong>', 
        text
    )
    text = re.sub(
        r'(?<!\*)\*([^*]+?)\*(?!\*)', 
        r'<em style="color: #555; font-style: italic;">\1</em>', 
        text
    )
    
    # 3. 리스트 처리
    text = _process_lists(text)
    
    # 4. 구분선
    text = re.sub(
        r'^={3,}$', 
        '<hr style="margin: 20px 0; border: none; border-top: 2px solid #667eea; opacity: 0.7;">', 
        text, 
        flags=re.MULTILINE
    )
    text = re.sub(
        r'^-{3,}$', 
        '<hr style="margin: 20px 0; border: none; border-top: 1px solid #dee2e6;">', 
        text, 
        flags=re.MULTILINE
    )
    
    # 5. 특수 패턴 (이모지)
    text = _format_emojis(text)
    
    # 6. 줄바꿈을 <br>로 변환
    text = re.sub(r'\n(?![<])', '<br>', text)
    
    return f'<div style="line-height: 1.8; font-size: 14px; color: #333;">{text}</div>'


def _process_lists(text: str) -> str:
    """리스트 아이템 처리"""
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    list_type = None
    
    for line in lines:
        # 불릿 포인트
        if re.match(r'^[\s]*[\*\-\+] ', line):
            content = re.sub(r'^[\s]*[\*\-\+] ', '', line)
            if not in_list or list_type != 'ul':
                if in_list:
                    formatted_lines.append(f'</{list_type}>')
                formatted_lines.append('<ul style="padding-left: 25px; margin: 15px 0;">')
                in_list = True
                list_type = 'ul'
            formatted_lines.append(f'<li style="margin: 8px 0; color: #333;">{content}</li>')
        # 숫자 리스트
        elif re.match(r'^[\s]*\d+\. ', line):
            content = re.sub(r'^[\s]*\d+\. ', '', line)
            if not in_list or list_type != 'ol':
                if in_list:
                    formatted_lines.append(f'</{list_type}>')
                formatted_lines.append('<ol style="padding-left: 25px; margin: 15px 0;">')
                in_list = True
                list_type = 'ol'
            formatted_lines.append(f'<li style="margin: 8px 0; color: #333;">{content}</li>')
        else:
            if in_list:
                formatted_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            formatted_lines.append(line)
    
    # 마지막에 열린 리스트 닫기
    if in_list:
        formatted_lines.append(f'</{list_type}>')
    
    return '\n'.join(formatted_lines)


def _format_emojis(text: str) -> str:
    """이모지 및 특수 문자 포맷팅"""
    # 별점 이모지
    text = re.sub(r'(⭐+)', r'<span style="color: #ffd700; font-size: 16px;">\1</span>', text)
    
    # 일반 이모지들
    emoji_patterns = [
        r'(✅|❌|⚠️|🔍|📊|📈|📉|💰|🏢|🔧|💡|🎯|📋)',
        r'(🚀|✨|🎉|🔥|💎|🌟|⚡|🎨|🎪|🎭)'
    ]
    
    for pattern in emoji_patterns:
        text = re.sub(pattern, r'<span style="font-size: 16px;">\1</span>', text)
    
    return text


def validate_financial_data(data: Dict) -> bool:
    """재무 데이터 유효성 검사"""
    if not isinstance(data, dict):
        return False
    
    required_fields = ['status', 'list']
    return all(field in data for field in required_fields)


def extract_key_metrics(financial_data: Dict) -> Dict[str, Any]:
    """주요 재무 지표 추출"""
    if not validate_financial_data(financial_data):
        return {}
    
    metrics = {}
    
    try:
        for item in financial_data.get('list', []):
            account_name = item.get('account_nm', '')
            current_amount = item.get('thstrm_amount', '0')
            previous_amount = item.get('frmtrm_amount', '0')
            
            # 주요 계정 매핑
            if '매출액' in account_name:
                metrics['revenue_current'] = _safe_convert_to_int(current_amount)
                metrics['revenue_previous'] = _safe_convert_to_int(previous_amount)
            elif '영업이익' in account_name:
                metrics['operating_income_current'] = _safe_convert_to_int(current_amount)
                metrics['operating_income_previous'] = _safe_convert_to_int(previous_amount)
            elif '당기순이익' in account_name:
                metrics['net_income_current'] = _safe_convert_to_int(current_amount)
                metrics['net_income_previous'] = _safe_convert_to_int(previous_amount)
            elif '자산총계' in account_name:
                metrics['total_assets_current'] = _safe_convert_to_int(current_amount)
                metrics['total_assets_previous'] = _safe_convert_to_int(previous_amount)
            elif '부채총계' in account_name:
                metrics['total_liabilities_current'] = _safe_convert_to_int(current_amount)
                metrics['total_liabilities_previous'] = _safe_convert_to_int(previous_amount)
    
    except Exception as e:
        print(f"지표 추출 중 오류: {e}")
        return {}
    
    return metrics


def calculate_ratios(metrics: Dict[str, Any]) -> Dict[str, float]:
    """재무 비율 계산"""
    ratios = {}
    
    try:
        # 부채비율
        if 'total_liabilities_current' in metrics and 'total_assets_current' in metrics:
            if metrics['total_assets_current'] > 0:
                ratios['debt_ratio'] = (metrics['total_liabilities_current'] / metrics['total_assets_current']) * 100
        
        # 매출 증가율
        if 'revenue_current' in metrics and 'revenue_previous' in metrics:
            if metrics['revenue_previous'] > 0:
                ratios['revenue_growth'] = ((metrics['revenue_current'] - metrics['revenue_previous']) / metrics['revenue_previous']) * 100
        
        # 영업이익률
        if 'operating_income_current' in metrics and 'revenue_current' in metrics:
            if metrics['revenue_current'] > 0:
                ratios['operating_margin'] = (metrics['operating_income_current'] / metrics['revenue_current']) * 100
    
    except Exception as e:
        print(f"비율 계산 중 오류: {e}")
        return {}
    
    return ratios


def _safe_convert_to_int(value: str) -> int:
    """안전한 정수 변환"""
    try:
        # 쉼표 제거 후 정수 변환
        return int(str(value).replace(',', '').replace('-', '0'))
    except (ValueError, TypeError):
        return 0


def format_currency(amount: int, unit: str = "원") -> str:
    """통화 형식 포맷팅"""
    if amount >= 100000000:  # 1억 이상
        return f"{amount // 100000000:,}억 {unit}"
    elif amount >= 10000:  # 1만 이상
        return f"{amount // 10000:,}만 {unit}"
    else:
        return f"{amount:,} {unit}"


def get_grade_from_score(score: float) -> str:
    """점수를 등급으로 변환"""
    if score >= 4.5:
        return "⭐⭐⭐⭐⭐ (최우수)"
    elif score >= 4.0:
        return "⭐⭐⭐⭐ (우수)"
    elif score >= 3.5:
        return "⭐⭐⭐ (보통)"
    elif score >= 3.0:
        return "⭐⭐ (주의)"
    else:
        return "⭐ (위험)"


def sanitize_input(text: str) -> str:
    """사용자 입력 검증 및 정제"""
    if not isinstance(text, str):
        return ""
    
    # 기본 정제
    text = text.strip()
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 특수 문자 제한
    text = re.sub(r'[<>"\']', '', text)
    
    # 길이 제한 (최대 1000자)
    if len(text) > 1000:
        text = text[:1000]
    
    return text


def log_api_call(api_name: str, company_name: str = "", status: str = "success"):
    """API 호출 로그 (개발용)"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {api_name} - {company_name} - {status}")


def get_error_message(error_code: str) -> str:
    """에러 코드에 따른 사용자 친화적 메시지"""
    error_messages = {
        '010': '정상',
        '011': '필수값 누락',
        '012': '기타오류',
        '013': '검색된 데이터가 없습니다',
        '020': '정기공시 조회제한 초과',
        '100': 'API 키가 등록되지 않은 키입니다',
        '101': 'API 키가 유효하지 않습니다',
        '800': '처리중 오류가 발생했습니다',
        '900': '일시적으로 사용할 수 없는 서비스입니다'
    }
    
    return error_messages.get(error_code, f"알 수 없는 오류 (코드: {error_code})")


def create_summary_stats(financial_data: Dict) -> Dict[str, Any]:
    """재무 데이터 요약 통계"""
    metrics = extract_key_metrics(financial_data)
    ratios = calculate_ratios(metrics)
    
    summary = {
        'company_metrics': metrics,
        'financial_ratios': ratios,
        'analysis_date': datetime.datetime.now().strftime("%Y-%m-%d"),
        'data_quality': 'good' if len(metrics) > 5 else 'limited'
    }
    
    return summary