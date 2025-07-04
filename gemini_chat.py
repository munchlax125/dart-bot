"""
Gemini AI 챗봇 모듈
- 재무 분석
- 감사 유의사항 분석
- 대화형 챗봇
"""

import google.generativeai as genai
from typing import Dict
import json


class GeminiAnalyzer:
    """Gemini AI 기반 재무 분석기"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    def simple_analysis(self, company_name: str, financial_data: Dict) -> str:
        """간단 재무 분석"""
        prompt = self._build_simple_analysis_prompt(company_name, financial_data)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"분석 중 오류가 발생했습니다: {str(e)}"
    
    def audit_points_analysis(self, company_name: str, financial_data: Dict) -> str:
        """회계감사 유의사항 분석"""
        prompt = self._build_audit_prompt(company_name, financial_data)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"감사 분석 중 오류가 발생했습니다: {str(e)}"
    
    def chat_response(self, company_name: str, financial_data: Dict, user_question: str) -> str:
        """대화형 챗봇 응답"""
        prompt = self._build_chat_prompt(company_name, financial_data, user_question)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"답변 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _build_simple_analysis_prompt(self, company_name: str, financial_data: Dict) -> str:
        """간단 분석용 프롬프트 생성"""
        return f"""
        다음은 {company_name}의 재무제표 데이터입니다:
        
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        이 데이터를 바탕으로 다음 항목들에 대해 간단하고 명확한 분석을 제공해주세요:
        
        ## 📊 재무 분석 리포트
        
        ### 1. 재무 건전성 ⭐⭐⭐⭐⭐
        - 부채비율, 유동비율, 자기자본비율 등 분석
        - 전년 대비 변화와 업종 평균 대비 평가
        
        ### 2. 수익성 분석 ⭐⭐⭐⭐⭐
        - 매출액, 영업이익, 당기순이익 변화 분석
        - 수익성 지표 (ROE, ROA, 영업이익률 등) 평가
        
        ### 3. 성장성 분석 ⭐⭐⭐⭐⭐
        - 전년 대비 주요 지표 변화율
        - 성장 동력과 지속가능성 평가
        
        ### 4. 투자 포인트
        **강점:**
        - 구체적인 강점 3가지
        
        **약점:**  
        - 주의해야 할 약점 3가지
        
        ### 5. 종합 평가
        - **점수**: ⭐⭐⭐⭐ (5점 만점)
        - **한줄평**: "구체적이고 직관적인 평가"
        
        분석은 일반 투자자가 이해하기 쉽도록 구체적인 숫자와 비율을 포함하여 작성해주세요.
        """
    
    def _build_audit_prompt(self, company_name: str, financial_data: Dict) -> str:
        """감사 유의사항용 프롬프트 생성"""
        return f"""
        다음은 {company_name}의 재무제표 데이터입니다:
        
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        회계감사 관점에서 다음 사항들을 검토하고 유의사항을 제시해주세요:
        
        ## ⚠️ 회계감사 유의사항 체크리스트
        
        ### 1. 수익인식 관련 위험요소
        - 수익인식 기준의 적정성
        - 다중요소계약 수익배분 검토사항
        - 장기계약 진행률 검토 포인트
        - **감사절차**: 구체적인 감사 방법 제시
        
        ### 2. 자산 손상 및 평가 이슈
        - 유형자산 손상 검토 필요성
        - 무형자산 손상 테스트 중요성
        - 재고자산 저가법 적용 검토
        - **감사절차**: 손상 테스트 검증 방법
        
        ### 3. 부채 및 충당금 적정성
        - 우발부채 인식 검토
        - 충당금 추정의 합리성
        - 금융부채 공정가치 평가
        - **감사절차**: 충당금 산정 근거 검토
        
        ### 4. 특수관계자 거래
        - 특수관계자 거래의 완전성
        - 거래가격의 공정성 검토
        - 공시의 충분성
        - **감사절차**: 특수관계자 거래 검증
        
        ### 5. 계속기업 가정
        - 유동성 위험 평가
        - 영업현금흐름 분석
        - 차입금 상환능력 검토
        - **감사절차**: 계속기업 평가 방법
        
        ### 6. 내부통제 취약점
        - 재무보고 내부통제 평가
        - IT 통제 환경 검토
        - 경영진 감시체계 평가
        - **감사절차**: 내부통제 테스트 방법
        
        ### 7. 업종별 특수 감사위험
        - 해당 업종의 특수한 회계 이슈
        - 규제 환경 변화 영향
        - 기술 변화에 따른 위험
        - **감사절차**: 업종별 특화 감사 방법
        
        각 항목별로 구체적인 감사절차와 검토 포인트를 제시해주세요.
        감사인이 실무에서 바로 활용할 수 있는 실용적인 내용으로 작성해주세요.
        """
    
    def _build_chat_prompt(self, company_name: str, financial_data: Dict, user_question: str) -> str:
        """챗봇 대화용 프롬프트 생성"""
        return f"""
        당신은 {company_name}의 재무제표를 분석하는 전문 AI 어시스턴트입니다.
        
        ## 📊 회사 재무정보:
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        ## 💬 사용자 질문: 
        {user_question}
        
        ## 📋 답변 가이드라인:
        1. 위 재무정보를 바탕으로 정확하고 도움이 되는 답변 제공
        2. 구체적인 숫자와 근거를 포함하여 설명
        3. 전문용어는 쉽게 풀어서 설명
        4. 필요시 업종 평균이나 경쟁사와 비교
        5. 투자자 관점에서 실용적인 조언 포함
        
        사용자의 질문에 친절하고 전문적으로 답변해주세요.
        """


class PromptManager:
    """프롬프트 관리 클래스"""
    
    @staticmethod
    def get_analysis_prompts():
        """분석용 프롬프트 템플릿들"""
        return {
            'simple': '간단 분석용 프롬프트',
            'audit': '감사 유의사항용 프롬프트', 
            'chat': '챗봇 대화용 프롬프트'
        }
    
    @staticmethod
    def customize_prompt(base_prompt: str, **kwargs) -> str:
        """프롬프트 커스터마이징"""
        return base_prompt.format(**kwargs)
