# data_processors.py
"""
재무 데이터 처리, 지표 추출, 비율 계산 등 순수 데이터 로직을 담당합니다.
"""
from typing import Dict, Any

def _safe_convert_to_int(value: Any) -> int:
    """안전한 정수 변환. 문자열의 쉼표를 제거하고 음수를 올바르게 처리합니다."""
    if value is None: return 0
    try:
        # FIX: .replace('-', '0')를 제거하여 음수 값을 정상적으로 처리합니다.
        return int(str(value).replace(',', ''))
    except (ValueError, TypeError):
        return 0

def extract_key_metrics(financial_data: Dict) -> Dict[str, Any]:
    """주요 재무 지표 추출"""
    metrics = {}
    if not isinstance(financial_data.get('list'), list):
        return {}
    
    for item in financial_data['list']:
        account_name = item.get('account_nm', '')
        current_amount = item.get('thstrm_amount')
        previous_amount = item.get('frmtrm_amount')

        if '매출액' in account_name:
            metrics['revenue_current'] = _safe_convert_to_int(current_amount)
            metrics['revenue_previous'] = _safe_convert_to_int(previous_amount)
        elif '영업이익' in account_name:
            metrics['operating_income_current'] = _safe_convert_to_int(current_amount)
            metrics['operating_income_previous'] = _safe_convert_to_int(previous_amount)
        elif '당기순이익' in account_name:
            metrics['net_income_current'] = _safe_convert_to_int(current_amount)
            metrics['net_income_previous'] = _safe_convert_to_int(previous_amount)

    return metrics