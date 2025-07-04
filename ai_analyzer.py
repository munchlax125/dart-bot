# ai_analyzer.py
"""Gemini AI와 연동하여 실제 분석을 수행합니다."""
import google.generativeai as genai
import json
from typing import Dict
# NEW: prompts 모듈에서 프롬프트 템플릿 임포트
from prompts import BUSINESS_ANALYSIS, FINANCIAL_ANALYSIS, AUDIT_POINTS_ANALYSIS, CHAT_RESPONSE

class AIAnalyzer:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API 키가 필요합니다.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')

    def _generate_response(self, prompt: str) -> str:
        """AI 모델 응답 생성 및 예외 처리 (재사용 가능한 private 메소드)"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # 실제 운영 환경에서는 logging 사용 권장
            print(f"Gemini API Error: {e}")
            raise ConnectionError(f"AI 모델 응답 생성 중 오류가 발생했습니다: {e}")

    def _create_prompt(self, template: str, company_name: str, financial_data: Dict, user_question: str = "") -> str:
        """프롬프트 생성 로직"""
        data_json = json.dumps(financial_data, ensure_ascii=False, indent=2)
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