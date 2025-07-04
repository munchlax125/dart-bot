from flask import Flask, render_template, request, jsonify
import os
import requests
import xml.etree.ElementTree as ET
import google.generativeai as genai
from typing import Dict, List, Optional
import json
import zipfile
import io
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import re
import html

# .env 파일 로드
load_dotenv()

app = Flask(__name__)

@dataclass
class CompanyInfo:
    corp_code: str
    corp_name: str
    stock_code: str

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
    
    # 3. 리스트 아이템 처리
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        # 불릿 포인트
        if re.match(r'^[\s]*[\*\-\+] ', line):
            content = re.sub(r'^[\s]*[\*\-\+] ', '', line)
            if not in_list:
                formatted_lines.append('<ul style="padding-left: 25px; margin: 15px 0;">')
                in_list = True
            formatted_lines.append(f'<li style="margin: 8px 0; color: #333;">{content}</li>')
        # 숫자 리스트
        elif re.match(r'^[\s]*\d+\. ', line):
            content = re.sub(r'^[\s]*\d+\. ', '', line)
            if not in_list:
                formatted_lines.append('<ol style="padding-left: 25px; margin: 15px 0;">')
                in_list = True
            formatted_lines.append(f'<li style="margin: 8px 0; color: #333;">{content}</li>')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(line)
    
    # 마지막에 열린 리스트 닫기
    if in_list:
        formatted_lines.append('</ul>')
    
    text = '\n'.join(formatted_lines)
    
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
    text = re.sub(r'(⭐+)', r'<span style="color: #ffd700; font-size: 16px;">\1</span>', text)
    text = re.sub(r'(✅|❌|⚠️|🔍|📊)', r'<span style="font-size: 16px;">\1</span>', text)
    
    # 6. 줄바꿈을 <br>로 변환
    text = re.sub(r'\n(?![<])', '<br>', text)
    
    return f'<div style="line-height: 1.8; font-size: 14px; color: #333;">{text}</div>'

class DARTAnalyzer:
    def __init__(self, dart_api_key: str, gemini_api_key: str):
        self.dart_api_key = dart_api_key
        self.dart_base_url = "https://opendart.fss.or.kr/api"
        
        # Gemini API 설정
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    def search_company(self, company_name: str) -> List[CompanyInfo]:
        """회사명으로 DART 기업 검색"""
        url = f"{self.dart_base_url}/corpCode.xml"
        params = {'crtfc_key': self.dart_api_key}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"DART API 호출 실패: {response.status_code}")
            
            content = response.content
            
            # ZIP 파일인지 확인 및 압축 해제
            if content.startswith(b'PK'):
                with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                    file_list = zip_file.namelist()
                    if file_list:
                        xml_content = zip_file.read(file_list[0])
                        content = xml_content
            
            # XML 파싱
            try:
                if isinstance(content, bytes):
                    xml_string = content.decode('utf-8')
                else:
                    xml_string = content
                
                # BOM 제거
                if xml_string.startswith('\ufeff'):
                    xml_string = xml_string[1:]
                
                root = ET.fromstring(xml_string)
                
            except UnicodeDecodeError:
                xml_string = content.decode('euc-kr')
                root = ET.fromstring(xml_string)
            
            # 회사 검색
            companies = []
            for corp in root.findall('.//list'):
                corp_name = corp.find('corp_name')
                corp_code = corp.find('corp_code')
                stock_code = corp.find('stock_code')
                
                if corp_name is not None and corp_code is not None:
                    corp_name_text = corp_name.text if corp_name.text else ""
                    if company_name.lower() in corp_name_text.lower():
                        companies.append(CompanyInfo(
                            corp_code=corp_code.text,
                            corp_name=corp_name_text,
                            stock_code=stock_code.text if stock_code is not None and stock_code.text else ""
                        ))
                        
            return companies[:10]
            
        except Exception as e:
            raise Exception(f"기업 검색 실패: {str(e)}")
    
    def get_financial_statements(self, corp_code: str, year: str = "2023") -> Dict:
        """재무제표 정보 조회"""
        url = f"{self.dart_base_url}/fnlttSinglAcnt.json"
        params = {
            'crtfc_key': self.dart_api_key,
            'corp_code': corp_code,
            'bsns_year': year,
            'reprt_code': '11011',
            'fs_div': 'CFS'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"재무제표 조회 실패: {response.status_code}")
            
            result = response.json()
            
            if result.get('status') == '013':
                # 연결재무제표가 없으면 개별재무제표 시도
                params['fs_div'] = 'OFS'
                response = requests.get(url, params=params, timeout=30)
                result = response.json()
                
                if result.get('status') != '000':
                    raise Exception("재무제표 데이터를 찾을 수 없습니다.")
                    
            elif result.get('status') != '000':
                raise Exception(f"API 오류: {result.get('message', '알 수 없는 오류')}")
                
            return result
            
        except Exception as e:
            raise Exception(f"재무제표 조회 실패: {str(e)}")
    
    def simple_analysis(self, company_name: str, financial_data: Dict) -> str:
        """간단분석 수행"""
        prompt = f"""
        다음은 {company_name}의 재무제표 데이터입니다:
        
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        이 데이터를 바탕으로 다음 항목들에 대해 간단하고 명확한 분석을 제공해주세요:
        
        1. 재무 건전성 (부채비율, 유동비율 등)
        2. 수익성 (매출액, 영업이익, 당기순이익 변화)
        3. 성장성 (전년 대비 주요 지표 변화율)
        4. 투자 포인트 (강점과 약점)
        5. 종합 평가 (5점 만점 점수와 한줄 평가)
        
        분석은 일반 투자자가 이해하기 쉽도록 작성해주세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"분석 중 오류가 발생했습니다: {str(e)}"
    
    def audit_points(self, company_name: str, financial_data: Dict) -> str:
        """회계감사시 유의사항 분석"""
        prompt = f"""
        다음은 {company_name}의 재무제표 데이터입니다:
        
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        회계감사 관점에서 다음 사항들을 검토하고 유의사항을 제시해주세요:
        
        1. 수익인식 관련 위험요소
        2. 자산 손상 및 평가 이슈
        3. 부채 및 충당금 적정성
        4. 특수관계자 거래
        5. 계속기업 가정
        6. 내부통제 취약점 가능성
        7. 업종별 특수 감사위험
        
        각 항목별로 구체적인 감사절차와 검토 포인트를 제시해주세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"감사 분석 중 오류가 발생했습니다: {str(e)}"
    
    def chat_with_ai(self, company_name: str, financial_data: Dict, user_question: str) -> str:
        """AI 챗봇 기능"""
        prompt = f"""
        당신은 {company_name}의 재무제표를 분석하는 전문 AI 어시스턴트입니다.
        
        회사 재무정보:
        {json.dumps(financial_data, ensure_ascii=False, indent=2)}
        
        사용자 질문: {user_question}
        
        위 재무정보를 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 제공해주세요.
        답변은 구체적인 숫자와 근거를 포함하여 설명해주세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"답변 생성 중 오류가 발생했습니다: {str(e)}"

# 전역 변수
analyzer = None
current_company = None
current_financial_data = None

def init_analyzer():
    """분석기 초기화"""
    global analyzer
    dart_api_key = os.getenv('DART_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not dart_api_key or not gemini_api_key:
        raise Exception("API 키가 설정되지 않았습니다.")
    
    analyzer = DARTAnalyzer(dart_api_key, gemini_api_key)

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_companies():
    """회사 검색 API"""
    try:
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        
        if not company_name:
            return jsonify({'error': '회사명을 입력해주세요.'}), 400
        
        if analyzer is None:
            init_analyzer()
        
        companies = analyzer.search_company(company_name)
        
        if not companies:
            return jsonify({'error': '검색된 회사가 없습니다.'}), 404
        
        # 데이터클래스를 딕셔너리로 변환
        companies_dict = [asdict(company) for company in companies]
        
        return jsonify({
            'success': True,
            'companies': companies_dict
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/select', methods=['POST'])
def select_company():
    """회사 선택 API"""
    global current_company, current_financial_data
    
    try:
        data = request.get_json()
        corp_code = data.get('corp_code')
        corp_name = data.get('corp_name')
        stock_code = data.get('stock_code')
        
        if not corp_code:
            return jsonify({'error': '회사 코드가 필요합니다.'}), 400
        
        if analyzer is None:
            init_analyzer()
        
        # 현재 선택된 회사 저장
        current_company = CompanyInfo(corp_code, corp_name, stock_code)
        
        # 재무제표 데이터 가져오기
        current_financial_data = analyzer.get_financial_statements(corp_code, "2023")
        
        return jsonify({
            'success': True,
            'message': f'{corp_name} 선택 완료',
            'company': asdict(current_company)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simple-analysis', methods=['GET'])
def get_simple_analysis():
    """간단 분석 API"""
    try:
        if current_company is None or current_financial_data is None:
            return jsonify({'error': '먼저 회사를 선택해주세요.'}), 400
        
        if analyzer is None:
            init_analyzer()
        
        analysis = analyzer.simple_analysis(current_company.corp_name, current_financial_data)
        formatted_analysis = format_analysis_result(analysis)
        
        return jsonify({
            'success': True,
            'analysis': formatted_analysis,
            'company': current_company.corp_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit-points', methods=['GET'])
def get_audit_points():
    """감사 유의사항 API"""
    try:
        if current_company is None or current_financial_data is None:
            return jsonify({'error': '먼저 회사를 선택해주세요.'}), 400
        
        if analyzer is None:
            init_analyzer()
        
        audit_analysis = analyzer.audit_points(current_company.corp_name, current_financial_data)
        formatted_audit_analysis = format_analysis_result(audit_analysis)
        
        return jsonify({
            'success': True,
            'analysis': formatted_audit_analysis,
            'company': current_company.corp_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """AI 챗봇 API"""
    try:
        if current_company is None or current_financial_data is None:
            return jsonify({'error': '먼저 회사를 선택해주세요.'}), 400
        
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': '질문을 입력해주세요.'}), 400
        
        if analyzer is None:
            init_analyzer()
        
        answer = analyzer.chat_with_ai(current_company.corp_name, current_financial_data, question)
        formatted_answer = format_analysis_result(answer)
        
        return jsonify({
            'success': True,
            'answer': formatted_answer,
            'company': current_company.corp_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """현재 상태 확인 API"""
    return jsonify({
        'current_company': asdict(current_company) if current_company else None,
        'has_financial_data': current_financial_data is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)