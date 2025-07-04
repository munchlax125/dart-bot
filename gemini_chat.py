"""
Gemini AI 챗봇 모듈
- 사업 분석
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
    
    def business_analysis(self, company_name: str, financial_data: Dict) -> str:
        """사업분석 - 회사가 어떤 사업을 하는지 분석"""
        prompt = self._build_business_analysis_prompt(company_name, financial_data)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"사업분석 중 오류가 발생했습니다: {str(e)}"
    
    def financial_analysis(self, company_name: str, financial_data: Dict) -> str:
        """재무분석 - 재무지표와 강점, 약점 등 분석"""
        prompt = self._build_financial_analysis_prompt(company_name, financial_data)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"재무분석 중 오류가 발생했습니다: {str(e)}"
    
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
    
    def _build_business_analysis_prompt(self, company_name: str, financial_data: Dict) -> str:
        """사업분석용 프롬프트 생성"""
        return f"""
        다음은 {company_name}의 재무제표 데이터입니다:
        
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        이 데이터를 바탕으로 다음 형식으로 사업분석을 해주세요:

        ## 🏢 {company_name} 사업분석 리포트

        ### 1. 주요 사업영역
        **핵심 사업**: 매출 구성과 계정과목을 통해 파악한 주요 사업
        **사업 특성**: 제조업/서비스업/금융업 등 업종 특성
        **시장 위치**: 해당 업계에서의 예상 포지션

        ### 2. 매출 구조 분석
        **매출 규모**: 연간 매출액과 전년 대비 변화
        **수익성**: 매출총이익률과 영업이익률 분석
        **성장성**: 매출 성장 트렌드와 패턴

        ### 3. 비용 구조 특성
        **주요 비용**: 매출원가, 판관비 구성 분석
        **비용 효율성**: 비용 대비 매출 효율성
        **고정비 vs 변동비**: 비용 구조의 특성

        ### 4. 자산 운용 현황
        **자산 구성**: 유형자산, 무형자산, 금융자산 비중
        **투자 패턴**: 설비투자나 연구개발 투자 규모
        **자산 효율성**: 자산 대비 매출 창출 능력

        ### 5. 사업 모델 특성
        **수익 모델**: 어떤 방식으로 수익을 창출하는지
        **경쟁 요소**: 재무제표에서 드러나는 경쟁력 요소
        **리스크 요인**: 재무구조상 나타나는 위험 요소

        ### 6. 업계 특성 및 전망
        **업계 동향**: 해당 업종의 일반적 특성
        **성장 가능성**: 재무 데이터로 본 성장 잠재력
        **투자 매력도**: 투자자 관점에서의 매력도

        모든 분석은 재무제표 데이터에 근거하여 구체적인 수치와 함께 제시해주세요.
        """
    
    def _build_financial_analysis_prompt(self, company_name: str, financial_data: Dict) -> str:
        """재무분석용 프롬프트 생성"""
        return f"""
        다음은 {company_name}의 재무제표 데이터입니다:
        
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        이 데이터를 바탕으로 다음 형식으로 재무분석을 해주세요:

        ## 📊 {company_name} 재무분석 리포트

        ### 1. 재무 건전성 분석
        **부채비율**: XX% (계산식과 의미 설명)
        **유동비율**: XX% (단기 지급능력)
        **자기자본비율**: XX% (재무안정성)
        **이자보상배수**: XX배 (이자지급능력)

        ### 2. 수익성 분석  
        **매출액**: XX억원 (전년 대비 XX% 증감)
        **매출총이익률**: XX% (원가 효율성)
        **영업이익률**: XX% (본업 수익성)
        **순이익률**: XX% (최종 수익성)
        **ROE**: XX% (자기자본수익률)
        **ROA**: XX% (총자산수익률)

        ### 3. 성장성 분석
        **매출 증가율**: XX% (성장 동력)
        **영업이익 증가율**: XX% (수익성 개선)
        **자산 증가율**: XX% (사업 확장)
        **성장 지속가능성**: 성장의 질적 평가

        ### 4. 활동성 분석
        **총자산회전율**: XX회 (자산 활용 효율성)
        **재고자산회전율**: XX회 (재고 관리 효율성)
        **매출채권회전율**: XX회 (채권 회수 효율성)

        ### 5. 강점 분석
        **주요 강점 3가지**
        1. 첫 번째 강점과 구체적 근거
        2. 두 번째 강점과 구체적 근거  
        3. 세 번째 강점과 구체적 근거

        ### 6. 약점 및 위험요인
        **주요 약점 3가지**
        1. 첫 번째 약점과 개선 필요사항
        2. 두 번째 약점과 개선 필요사항
        3. 세 번째 약점과 개선 필요사항

        ### 7. 투자 의견
        **종합 점수**: ⭐⭐⭐⭐ (5점 만점)
        **투자 등급**: 매수/보유/매도 등급과 근거
        **목표주가**: 재무지표 기반 적정 가치 평가
        **핵심 모니터링 지표**: 지속 관찰해야 할 재무지표

        모든 수치는 구체적으로 계산하여 제시하고, 전년 대비 변화도 함께 분석해주세요.
        """
    
    def _build_audit_prompt(self, company_name: str, financial_data: Dict) -> str:
        """감사 유의사항용 프롬프트 생성"""
        return f"""
        다음은 {company_name}의 재무제표 데이터입니다:
        
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        회계감사 관점에서 다음 형식으로 분석해주세요:

        ## ⚠️ {company_name} 회계감사 유의사항

        ### 1. 수익인식 관련 위험요소
        **위험도**: 높음/보통/낮음
        **주요 검토사항**: 구체적인 위험 요소
        **감사절차**: 수행해야 할 구체적 절차
        **중요성**: 왜 이 부분이 중요한지 설명

        ### 2. 자산 손상 및 평가 이슈
        **위험도**: 높음/보통/낮음  
        **주요 검토사항**: 손상 가능성이 있는 자산
        **감사절차**: 손상 테스트 검증 방법
        **업종 특성**: 해당 업종의 특수성

        ### 3. 부채 및 충당금 적정성
        **위험도**: 높음/보통/낮음
        **주요 검토사항**: 충당금 추정의 합리성
        **감사절차**: 충당금 산정 근거 검토
        **과거 변동성**: 전년 대비 변화 분석

        ### 4. 특수관계자 거래
        **위험도**: 높음/보통/낮음
        **주요 검토사항**: 거래의 완전성과 공정성
        **감사절차**: 특수관계자 거래 검증 방법
        **공시 adequacy**: 공시의 충분성

        ### 5. 계속기업 가정
        **위험도**: 높음/보통/낮음
        **주요 검토사항**: 유동성 및 수익성 분석
        **감사절차**: 계속기업 평가 방법
        **지표 분석**: 구체적 재무 지표 검토

        ### 6. 내부통제 취약점
        **위험도**: 높음/보통/낮음
        **주요 검토사항**: 통제 환경 평가
        **감사절차**: 내부통제 테스트 방법
        **IT 통제**: 정보시스템 통제 검토

        ### 7. 업종별 특수 감사위험
        **위험도**: 높음/보통/낮음
        **업종 특성**: 해당 업종 특수 이슈
        **감사절차**: 업종별 특화 감사 방법
        **규제 환경**: 관련 법규 및 규제 변화

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
            'business': '사업분석용 프롬프트',
            'financial': '재무분석용 프롬프트',
            'audit': '감사 유의사항용 프롬프트', 
            'chat': '챗봇 대화용 프롬프트'
        }
    
    @staticmethod
    def customize_prompt(base_prompt: str, **kwargs) -> str:
        """프롬프트 커스터마이징"""
        return base_prompt.format(**kwargs)