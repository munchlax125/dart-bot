# app.py
"""
메인 Flask 애플리케이션. 세션 기반으로 상태를 관리합니다.
"""
from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv

# 리팩토링된 모듈 임포트
from dart_client import DARTClient, DARTApiException
from ai_analyzer import AIAnalyzer
import formatters

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)
# NEW: 세션 사용을 위한 시크릿 키 설정. .env 파일에서 가져옵니다.
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-for-development')

# --- 클라이언트 초기화 ---
# 애플리케이션 시작 시 클라이언트를 한 번만 초기화합니다.
try:
    dart_client = DARTClient(os.getenv('DART_API_KEY'))
    ai_analyzer = AIAnalyzer(os.getenv('GEMINI_API_KEY'))
except ValueError as e:
    print(f"API 키 설정 오류: {e}")
    exit(1)

# --- 에러 핸들러 ---
# NEW: 커스텀 에러 및 일반 서버 에러를 중앙에서 처리합니다.
@app.errorhandler(DARTApiException)
def handle_dart_api_exception(e):
    app.logger.error(f"DART API Error: {e}")
    return jsonify({'error': str(e)}), 503 # Service Unavailable

@app.errorhandler(ConnectionError)
def handle_ai_api_exception(e):
    app.logger.error(f"AI API Error: {e}")
    return jsonify({'error': str(e)}), 503

@app.errorhandler(Exception)
def handle_generic_exception(e):
    app.logger.error(f"An unexpected error occurred: {e}")
    return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

# --- 라우팅 ---
@app.route('/')
def index():
    """메인 페이지 렌더링"""
    session.clear() # 메인 페이지 접속 시 세션 초기화
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_companies():
    """회사명으로 기업 목록 검색"""
    data = request.get_json()
    company_name = formatters.sanitize_input(data.get('company_name', ''))
    if not company_name:
        return jsonify({'error': '회사명을 입력해주세요.'}), 400
    
    companies = dart_client.search_company(company_name)
    return jsonify({'companies': [c.__dict__ for c in companies]})

@app.route('/api/select', methods=['POST'])
def select_company():
    """사용자가 선택한 기업의 재무 정보를 가져와 세션에 저장"""
    data = request.get_json()
    corp_code = formatters.sanitize_input(data.get('corp_code', ''))
    if not corp_code:
        return jsonify({'error': '회사 코드가 필요합니다.'}), 400

    # NEW: 전역 변수 대신 세션에 회사 정보와 재무 데이터를 저장
    session['corp_name'] = formatters.sanitize_input(data.get('corp_name', ''))
    session['financial_data'] = dart_client.get_financial_statements(corp_code, "2023")
    
    return jsonify({'success': True, 'message': f"{session['corp_name']} 선택 완료"})

def _get_session_data():
    """세션에서 회사 이름과 재무 데이터를 가져오는 헬퍼 함수"""
    corp_name = session.get('corp_name')
    financial_data = session.get('financial_data')
    if not corp_name or not financial_data:
        raise ValueError('분석할 회사를 먼저 선택해주세요.')
    return corp_name, financial_data

@app.route('/api/business-analysis', methods=['GET'])
def get_business_analysis():
    corp_name, financial_data = _get_session_data()
    analysis = ai_analyzer.business_analysis(corp_name, financial_data)
    return jsonify({'analysis': formatters.format_analysis_result(analysis)})

@app.route('/api/financial-analysis', methods=['GET'])
def get_financial_analysis():
    corp_name, financial_data = _get_session_data()
    analysis = ai_analyzer.financial_analysis(corp_name, financial_data)
    return jsonify({'analysis': formatters.format_analysis_result(analysis)})

@app.route('/api/audit-points', methods=['GET'])
def get_audit_points():
    corp_name, financial_data = _get_session_data()
    analysis = ai_analyzer.audit_points_analysis(corp_name, financial_data)
    return jsonify({'analysis': formatters.format_analysis_result(analysis)})

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    corp_name, financial_data = _get_session_data()
    data = request.get_json()
    question = formatters.sanitize_input(data.get('question', ''))
    if not question:
        return jsonify({'error': '질문을 입력해주세요.'}), 400
    
    answer = ai_analyzer.chat_response(corp_name, financial_data, question)
    return jsonify({'answer': formatters.format_analysis_result(answer)})

if __name__ == '__main__':
    print("🌐 서버가 http://localhost:5000 에서 실행됩니다.")
    app.run(debug=True, host='0.0.0.0', port=5000)