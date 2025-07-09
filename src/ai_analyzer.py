# ai_analyzer.py - 응답 정제 강화 버전
"""Gemini AI와 연동하여 실제 분석을 수행합니다."""
import google.generativeai as genai
import json
import re
from typing import Dict
from src.prompts import BUSINESS_ANALYSIS, FINANCIAL_ANALYSIS, AUDIT_POINTS_ANALYSIS, CHAT_RESPONSE

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
        """AI 모델 응답 생성 및 후처리"""
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # 1단계: 인식사항 섹션 제거
            result_text = self._remove_instruction_sections(result_text)
            
            # 2단계: 불확실성 표현 제거
            result_text = self._clean_uncertainty_phrases(result_text)
            
            return result_text
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            raise ConnectionError(f"AI 모델 응답 생성 중 오류가 발생했습니다: {e}")

    def _remove_instruction_sections(self, text: str) -> str:
        """응답에서 인식사항 및 지시문 섹션 제거"""
        patterns_to_remove = [
            r'⚠️.*?인식.*?사항.*?(?=##|\n\n|$)',  # ⚠️ 인식사항 섹션
            r'\*\*⚠️.*?인식.*?사항.*?\*\*.*?(?=##|\n\n|$)',  # **⚠️ 인식사항** 섹션
            r'아래.*?제공된.*?재무데이터.*?표현하세요\.?',  # 데이터 설명 문장
            r'절대로.*?"예상된다".*?표현하세요\.?',  # 지시문 제거
            r'모든.*?수치는.*?표현하세요\.?',  # 지시문 제거
            r'감사를.*?받은.*?확정된.*?실적입니다\.?',  # 데이터 설명
        ]
        
        cleaned_text = text
        for pattern in patterns_to_remove:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL | re.MULTILINE)
        
        # 연속된 줄바꿈 정리
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        return cleaned_text.strip()

    def _clean_uncertainty_phrases(self, text: str) -> str:
        """불확실성 표현 제거 및 정제"""
        uncertain_phrases = [
            "예상됩니다", "예상된다", "추정됩니다", "추정된다", 
            "추정치", "예상치", "잠정", "보입니다", "것으로 사료됩니다",
            "것으로 보인다", "것으로 추정", "것으로 예상", "추정할 수 있습니다",
            "으로 예상됩니다", "로 추정됩니다", "것으로 판단됩니다"
        ]
        
        for phrase in uncertain_phrases:
            text = text.replace(phrase, "입니다")
            text = text.replace(phrase.upper(), "입니다")
        
        # 중복된 "입니다" 정리
        text = re.sub(r'입니다\s*입니다', '입니다', text)
        
        return text

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