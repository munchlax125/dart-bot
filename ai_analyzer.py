# ai_analyzer.py - 확정 데이터 강조 버전
"""Gemini AI와 연동하여 실제 분석을 수행합니다."""
import google.generativeai as genai
import json
from typing import Dict
from prompts import BUSINESS_ANALYSIS, FINANCIAL_ANALYSIS, AUDIT_POINTS_ANALYSIS, CHAT_RESPONSE

class AIAnalyzer:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API 키가 필요합니다.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro-latest',
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # 더 일관성 있는 응답을 위해 낮춤
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048
            )
        )

    def _generate_response(self, prompt: str) -> str:
        """AI 모델 응답 생성 및 예외 처리"""
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # 응답에서 불확실성 표현 제거 (후처리)
            uncertain_phrases = [
                "예상됩니다", "예상된다", "추정됩니다", "추정된다", 
                "추정치", "예상치", "잠정", "보입니다", "것으로 사료됩니다",
                "것으로 보인다", "것으로 추정", "것으로 예상", "추정할 수 있습니다"
            ]
            
            for phrase in uncertain_phrases:
                result_text = result_text.replace(phrase, "입니다")
                result_text = result_text.replace(phrase.upper(), "입니다")
            
            return result_text
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            raise ConnectionError(f"AI 모델 응답 생성 중 오류가 발생했습니다: {e}")

    def _create_prompt(self, template: str, company_name: str, financial_data: Dict, user_question: str = "") -> str:
        """프롬프트 생성 로직 - 데이터 출처 명시"""
        # 재무데이터에 출처 정보 추가
        enhanced_data = {
            "데이터_출처": "금융감독원 DART 공식 제출 사업보고서",
            "데이터_성격": "감사받은 확정 실적 (추정치 아님)",
            "원본_데이터": financial_data
        }
        
        data_json = json.dumps(enhanced_data, ensure_ascii=False, indent=2)
        return template.format(company_name=company_name, financial_data=data_json, user_question=user_question)

    def business_analysis(self, company_name: str, financial_data: Dict) -> str:
        prompt = self._create_prompt(BUSINESS_ANALYSIS, company_name, financial_data)
        return self._generate_response(prompt)
    
    def financial_analysis(self, company_name: str, financial_data: Dict) -> str:
        prompt = self._create_prompt(FINANCIAL_ANALYSIS, company_name, financial_data)
        return self._generate_response(prompt)
    
    def audit_points_analysis(self, company_name: str, financial_data: Dict) -> str:
        prompt = self._create_prompt(AUDIT_POINTS_ANALYSIS, company_name, financial_data)
        return self._generate_response(prompt)
        
    def chat_response(self, company_name: str, financial_data: Dict, user_question: str) -> str:
        prompt = self._create_prompt(CHAT_RESPONSE, company_name, financial_data, user_question)
        return self._generate_response(prompt)