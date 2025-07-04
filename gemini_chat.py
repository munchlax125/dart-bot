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
        """간단 분석용 프롬프트 생성 (UI 개선 버전)"""
        return f"""
        다음은 {company_name}의 재무제표 데이터입니다:
        
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        이 데이터를 바탕으로 다음 형식으로 분석해주세요:

        ## 📊 {company_name} 재무 분석 리포트

        ### 1. 재무 건전성
        부채비율: XX%
        유동비율: XX%
        자기자본비율: XX%
        전년 대비 변화: 개선/악화 및 구체적 수치

        ### 2. 수익성 분석  
        매출액: XX억원 (전년 대비 XX% 증감)
        영업이익: XX억원 (영업이익률 XX%)
        당기순이익: XX억원 (전년 대비 XX% 증감)
        ROE: XX%

        ### 3. 성장성 분석
        매출 증가율: XX%
        영업이익 증가율: XX%
        총자산 증가율: XX%
        성장 동력: 구체적인 성장 요인 설명

        ### 4. 투자 포인트

        **강점**
        1. 첫 번째 강점
        2. 두 번째 강점  
        3. 세 번째 강점

        **약점**
        1. 첫 번째 약점
        2. 두 번째 약점
        3. 세 번째 약점

        ### 5. 종합 평가
        점수: ⭐⭐⭐⭐ (5점 만점)
        한줄평: "구체적이고 직관적인 평가 한 문장"

        모든 수치는 구체적인 숫자로 제시하고, 각 항목은 줄바꿈으로 구분해주세요.
        이탤릭체나 복잡한 서식 대신 명확한 구분을 위해 줄바꿈을 활용해주세요.
        """
    
    def _build_audit_prompt(self, company_name: str, financial_data: Dict) -> str:
        """감사 유의사항용 프롬프트 생성 (UI 개선 버전)"""
        return f"""
        다음은 {company_name}의 재무제표 데이터입니다:
        
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        회계감사 관점에서 다음 형식으로 분석해주세요:

        ## ⚠️ {company_name} 회계감사 유의사항

        ### 1. 수익인식 관련 위험요소
        위험도: 높음/보통/낮음
        주요 검토사항: 구체적인 위험 요소
        감사절차: 수행해야 할 구체적 절차
        중요성: 왜 이 부분이 중요한지 설명

        ### 2. 자산 손상 및 평가 이슈
        위험도: 높음/보통/낮음  
        주요 검토사항: 손상 가능성이 있는 자산
        감사절차: 손상 테스트 검증 방법
        업종 특성: 해당 업종의 특수성

        ### 3. 부채 및 충당금 적정성
        위험도: 높음/보통/낮음
        주요 검토사항: 충당금 추정의 합리성
        감사절차: 충당금 산정 근거 검토
        과거 변동성: 전년 대비 변화 분석

        ### 4. 특수관계자 거래
        위험도: 높음/보통/낮음
        주요 검토사항: 거래의 완전성과 공정성
        감사절차: 특수관계자 거래 검증 방법
        공시 adequacy: 공시의 충분성

        ### 5. 계속기업 가정
        위험도: 높음/보통/낮음
        주요 검토사항: 유동성 및 수익성 분석
        감사절차: 계속기업 평가 방법
        지표 분석: 구체적 재무 지표 검토

        ### 6. 내부통제 취약점
        위험도: 높음/보통/낮음
        주요 검토사항: 통제 환경 평가
        감사절차: 내부통제 테스트 방법
        IT 통제: 정보시스템 통제 검토

        ### 7. 업종별 특수 감사위험
        위험도: 높음/보통/낮음
        업종 특성: 해당 업종 특수 이슈
        감사절차: 업종별 특화 감사 방법
        규제 환경: 관련 법규 및 규제 변화

        각 항목을 명확히 구분하여 작성하고, 실무에서 바로 활용할 수 있는 구체적인 내용으로 작성해주세요.
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