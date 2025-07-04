"""
메인 Flask 애플리케이션
- 라우팅 및 API 엔드포인트
- 요청/응답 처리
- 에러 핸들링
"""

from flask import Flask, render_template, request, jsonify
import os
from dataclasses import asdict
from dotenv import load_dotenv

# 커스텀 모듈 임포트
from dart_api import DARTClient, CompanyInfo
from gemini_chat import GeminiAnalyzer
from utils import format_analysis_result, sanitize_input, log_api_call, get_error_message

# .env 파일 로드
load_dotenv()

app = Flask(__name__)

# 전역 변수
dart_client = None
gemini_analyzer = None
current_company = None
current_financial_data = None


def initialize_clients():
    """API 클라이언트 초기화"""
    global dart_client, gemini_analyzer
    
    dart_api_key = os.getenv('DART_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not dart_api_key or not gemini_api_key:
        raise Exception("API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    
    dart_client = DARTClient(dart_api_key)
    gemini_analyzer = GeminiAnalyzer(gemini_api_key)
    
    # API 키 유효성 검사
    if not dart_client.validate_api_key():
        raise Exception("DART API 키가 유효하지 않습니다.")


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search_companies():
    """회사 검색 API"""
    try:
        # 클라이언트 초기화
        if dart_client is None:
            initialize_clients()
        
        # 요청 데이터 파싱
        data = request.get_json()
        company_name = sanitize_input(data.get('company_name', ''))
        
        if not company_name:
            return jsonify({'error': '회사명을 입력해주세요.'}), 400
        
        # 로그 기록
        log_api_call("SEARCH", company_name)
        
        # 회사 검색
        companies = dart_client.search_company(company_name)
        
        if not companies:
            return jsonify({'error': '검색된 회사가 없습니다.'}), 404
        
        # 응답 데이터 변환
        companies_dict = [asdict(company) for company in companies]
        
        return jsonify({
            'success': True,
            'companies': companies_dict,
            'count': len(companies_dict)
        })
        
    except Exception as e:
        log_api_call("SEARCH", company_name if 'company_name' in locals() else "", "error")
        return jsonify({'error': str(e)}), 500


@app.route('/api/select', methods=['POST'])
def select_company():
    """회사 선택 API"""
    global current_company, current_financial_data
    
    try:
        # 클라이언트 초기화
        if dart_client is None:
            initialize_clients()
        
        # 요청 데이터 파싱
        data = request.get_json()
        corp_code = sanitize_input(data.get('corp_code', ''))
        corp_name = sanitize_input(data.get('corp_name', ''))
        stock_code = sanitize_input(data.get('stock_code', ''))
        
        if not corp_code:
            return jsonify({'error': '회사 코드가 필요합니다.'}), 400
        
        # 로그 기록
        log_api_call("SELECT", corp_name)
        
        # 현재 선택된 회사 저장
        current_company = CompanyInfo(corp_code, corp_name, stock_code)
        
        # 재무제표 데이터 가져오기
        current_financial_data = dart_client.get_financial_statements(corp_code, "2023")
        
        return jsonify({
            'success': True,
            'message': f'{corp_name} 선택 완료',
            'company': asdict(current_company)
        })
        
    except Exception as e:
        log_api_call("SELECT", corp_name if 'corp_name' in locals() else "", "error")
        return jsonify({'error': str(e)}), 500


@app.route('/api/simple-analysis', methods=['GET'])
def get_simple_analysis():
    """간단 분석 API"""
    try:
        # 유효성 검사
        if current_company is None or current_financial_data is None:
            return jsonify({'error': '먼저 회사를 선택해주세요.'}), 400
        
        if gemini_analyzer is None:
            initialize_clients()
        
        # 로그 기록
        log_api_call("SIMPLE_ANALYSIS", current_company.corp_name)
        
        # AI 분석 실행
        analysis = gemini_analyzer.simple_analysis(
            current_company.corp_name, 
            current_financial_data
        )
        
        # HTML 포맷팅
        formatted_analysis = format_analysis_result(analysis)
        
        return jsonify({
            'success': True,
            'analysis': formatted_analysis,
            'company': current_company.corp_name
        })
        
    except Exception as e:
        log_api_call("SIMPLE_ANALYSIS", 
                    current_company.corp_name if current_company else "", 
                    "error")
        return jsonify({'error': str(e)}), 500


@app.route('/api/audit-points', methods=['GET'])
def get_audit_points():
    """감사 유의사항 API"""
    try:
        # 유효성 검사
        if current_company is None or current_financial_data is None:
            return jsonify({'error': '먼저 회사를 선택해주세요.'}), 400
        
        if gemini_analyzer is None:
            initialize_clients()
        
        # 로그 기록
        log_api_call("AUDIT_POINTS", current_company.corp_name)
        
        # AI 분석 실행
        audit_analysis = gemini_analyzer.audit_points_analysis(
            current_company.corp_name, 
            current_financial_data
        )
        
        # HTML 포맷팅
        formatted_audit_analysis = format_analysis_result(audit_analysis)
        
        return jsonify({
            'success': True,
            'analysis': formatted_audit_analysis,
            'company': current_company.corp_name
        })
        
    except Exception as e:
        log_api_call("AUDIT_POINTS", 
                    current_company.corp_name if current_company else "", 
                    "error")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """AI 챗봇 API"""
    try:
        # 유효성 검사
        if current_company is None or current_financial_data is None:
            return jsonify({'error': '먼저 회사를 선택해주세요.'}), 400
        
        if gemini_analyzer is None:
            initialize_clients()
        
        # 요청 데이터 파싱
        data = request.get_json()
        question = sanitize_input(data.get('question', ''))
        
        if not question:
            return jsonify({'error': '질문을 입력해주세요.'}), 400
        
        # 로그 기록
        log_api_call("CHAT", f"{current_company.corp_name} - Q: {question[:50]}...")
        
        # AI 응답 생성
        answer = gemini_analyzer.chat_response(
            current_company.corp_name,
            current_financial_data,
            question
        )
        
        # HTML 포맷팅
        formatted_answer = format_analysis_result(answer)
        
        return jsonify({
            'success': True,
            'answer': formatted_answer,
            'company': current_company.corp_name
        })
        
    except Exception as e:
        log_api_call("CHAT", 
                    current_company.corp_name if current_company else "", 
                    "error")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """현재 상태 확인 API"""
    return jsonify({
        'current_company': asdict(current_company) if current_company else None,
        'has_financial_data': current_financial_data is not None,
        'clients_initialized': dart_client is not None and gemini_analyzer is not None
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크 API"""
    try:
        if dart_client is None:
            initialize_clients()
        
        # DART API 연결 테스트
        dart_status = dart_client.validate_api_key()
        
        return jsonify({
            'status': 'healthy',
            'dart_api': 'connected' if dart_status else 'disconnected',
            'gemini_api': 'connected' if gemini_analyzer else 'disconnected'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return jsonify({'error': '요청된 리소스를 찾을 수 없습니다.'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500


if __name__ == '__main__':
    try:
        # 시작 시 클라이언트 초기화
        print("🚀 서버 시작 중...")
        initialize_clients()
        print("✅ API 클라이언트 초기화 완료!")
        
        # Flask 서버 실행
        print("🌐 서버가 http://localhost:5000 에서 실행됩니다.")
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        print("💡 .env 파일의 API 키를 확인해주세요.")
