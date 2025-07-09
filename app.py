# app.py - 2024년 데이터 지원 완전 버전
"""
메인 Flask 애플리케이션. 세션 기반으로 상태를 관리합니다.
개선사항: 로깅, 환경변수 검증, 에러 처리 강화, 보안 개선, 2024년 데이터 지원
"""
from flask import Flask, render_template, request, jsonify, session
import os
import logging
import time
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 리팩토링된 모듈 임포트
from src.dart_client import DARTClient, DARTApiException  #<- 'src.' 라는 새 주소 추가
from src.ai_analyzer import AIAnalyzer                    #<- 'src.' 라는 새 주소 추가
from src import formatters                                #<- 'src.' 라는 새 주소 추가

# .env 파일에서 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 검증
def validate_environment():
    """필수 환경 변수가 설정되었는지 확인"""
    required_keys = ['DART_API_KEY', 'GEMINI_API_KEY']
    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        raise EnvironmentError(f"필수 환경변수 누락: {', '.join(missing)}")

try:
    validate_environment()
except EnvironmentError as e:
    logger.error(f"환경 설정 오류: {e}")
    exit(1)

app = Flask(__name__)

# 보안 설정
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-super-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Rate Limiting 설정
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)

# --- 클라이언트 초기화 ---
try:
    dart_client = DARTClient(os.getenv('DART_API_KEY'))
    ai_analyzer = AIAnalyzer(os.getenv('GEMINI_API_KEY'))
    logger.info("API 클라이언트 초기화 완료")
except ValueError as e:
    logger.error(f"API 키 설정 오류: {e}")
    exit(1)

# --- 유틸리티 함수 ---
def api_response(success=True, data=None, message="", error="", status_code=200):
    """통일된 API 응답 형식"""
    response_data = {
        'success': success,
        'data': data,
        'message': message,
        'error': error
    }
    return jsonify(response_data), status_code

def validate_request_data(data, required_fields):
    """요청 데이터 검증"""
    if not data:
        return "요청 데이터가 없습니다."
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return f"필수 필드 누락: {', '.join(missing_fields)}"
    
    return None

# --- 에러 핸들러 ---
@app.errorhandler(DARTApiException)
def handle_dart_api_exception(e):
    logger.error(f"DART API Error: {e}")
    return api_response(success=False, error=str(e), status_code=503)

@app.errorhandler(ConnectionError)
def handle_ai_api_exception(e):
    logger.error(f"AI API Error: {e}")
    return api_response(success=False, error=str(e), status_code=503)

@app.errorhandler(429)
def handle_rate_limit_exceeded(e):
    logger.warning(f"Rate limit exceeded: {request.remote_addr}")
    return api_response(success=False, error="너무 많은 요청입니다. 잠시 후 다시 시도해주세요.", status_code=429)

@app.errorhandler(Exception)
def handle_generic_exception(e):
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return api_response(success=False, error="서버 내부 오류가 발생했습니다.", status_code=500)

# --- 라우팅 ---
@app.route('/')
def index():
    """메인 페이지 렌더링"""
    session.clear()
    logger.info(f"메인 페이지 접속: {request.remote_addr}")
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
@limiter.limit("20 per minute")
def search_companies():
    """회사명으로 기업 목록 검색"""
    try:
        data = request.get_json()
        logger.info(f"검색 요청 데이터: {data}")
        
        error = validate_request_data(data, ['company_name'])
        if error:
            logger.error(f"검증 실패: {error}")
            return api_response(success=False, error=error, status_code=400)
        
        company_name = formatters.sanitize_input(data.get('company_name', ''))
        if len(company_name) < 2:
            return api_response(success=False, error="회사명은 2글자 이상 입력해주세요.", status_code=400)
        
        logger.info(f"기업 검색 요청: {company_name}")
        companies = dart_client.search_company(company_name)
        logger.info(f"검색 결과: {len(companies)}개 기업")
        
        return api_response(
            success=True, 
            data={'companies': [c.__dict__ for c in companies]},
            message=f"{len(companies)}개의 기업을 찾았습니다."
        )
        
    except Exception as e:
        logger.error(f"기업 검색 오류: {e}", exc_info=True)
        return api_response(success=False, error=f"검색 중 오류가 발생했습니다: {str(e)}", status_code=500)

@app.route('/api/select', methods=['POST'])
@limiter.limit("10 per minute")
def select_company():
    """사용자가 선택한 기업의 재무 정보를 가져와 세션에 저장 (2024년 데이터 우선)"""
    try:
        data = request.get_json()
        error = validate_request_data(data, ['corp_code', 'corp_name'])
        if error:
            return api_response(success=False, error=error, status_code=400)

        corp_code = formatters.sanitize_input(data.get('corp_code', ''))
        corp_name = formatters.sanitize_input(data.get('corp_name', ''))
        
        logger.info(f"기업 선택: {corp_name} ({corp_code})")
        
        # 동적 연도 설정: 2024년 먼저 시도, 없으면 2023년, 2022년
        financial_data = None
        year_used = None
        
        for year in ["2024", "2023", "2022"]:
            try:
                logger.info(f"{corp_name} {year}년 재무데이터 조회 시도")
                financial_data = dart_client.get_financial_statements(corp_code, year)
                year_used = year
                logger.info(f"{corp_name} {year}년 재무데이터 조회 성공")
                break
            except DARTApiException as e:
                logger.warning(f"{corp_name} {year}년 데이터 조회 실패: {e}")
                continue
        
        if not financial_data:
            return api_response(
                success=False, 
                error="최근 3년간 재무제표 데이터를 찾을 수 없습니다. 다른 기업을 선택해주세요.", 
                status_code=404
            )
        
        # 데이터 크기 확인 (세션 저장소 제한 고려)
        if len(str(financial_data)) > 1000000:  # 1MB 제한
            return api_response(success=False, error="재무 데이터가 너무 큽니다.", status_code=413)
        
        # 세션에 저장
        session['corp_name'] = corp_name
        session['corp_code'] = corp_code
        session['financial_data'] = financial_data
        session['data_year'] = year_used
        session['selected_at'] = str(int(time.time()))
        
        return api_response(
            success=True,
            message=f"{corp_name} ({year_used}년 데이터) 선택 완료",
            data={'company_name': corp_name, 'data_year': year_used}
        )
        
    except Exception as e:
        logger.error(f"기업 선택 오류: {e}", exc_info=True)
        return api_response(success=False, error=f"기업 선택 중 오류가 발생했습니다: {str(e)}", status_code=500)

def _get_session_data():
    """세션에서 회사 이름과 재무 데이터를 가져오는 헬퍼 함수"""
    corp_name = session.get('corp_name')
    financial_data = session.get('financial_data')
    data_year = session.get('data_year', 'Unknown')
    
    if not corp_name or not financial_data:
        raise ValueError('분석할 회사를 먼저 선택해주세요.')
    
    logger.info(f"세션 데이터 조회: {corp_name} ({data_year}년)")
    return corp_name, financial_data

@app.route('/api/business-analysis', methods=['GET'])
@limiter.limit("5 per minute")
def get_business_analysis():
    """사업 분석 수행"""
    try:
        corp_name, financial_data = _get_session_data()
        logger.info(f"사업 분석 요청: {corp_name}")
        
        analysis = ai_analyzer.business_analysis(corp_name, financial_data)
        formatted_analysis = formatters.format_analysis_result(analysis)
        
        return api_response(
            success=True,
            data={'analysis': formatted_analysis},
            message="사업 분석이 완료되었습니다."
        )
        
    except ValueError as e:
        return api_response(success=False, error=str(e), status_code=400)
    except Exception as e:
        logger.error(f"사업 분석 오류: {e}", exc_info=True)
        return api_response(success=False, error=f"분석 중 오류가 발생했습니다: {str(e)}", status_code=500)

@app.route('/api/financial-analysis', methods=['GET'])
@limiter.limit("5 per minute")
def get_financial_analysis():
    """재무 분석 수행"""
    try:
        corp_name, financial_data = _get_session_data()
        logger.info(f"재무 분석 요청: {corp_name}")
        
        analysis = ai_analyzer.financial_analysis(corp_name, financial_data)
        formatted_analysis = formatters.format_analysis_result(analysis)
        
        return api_response(
            success=True,
            data={'analysis': formatted_analysis},
            message="재무 분석이 완료되었습니다."
        )
        
    except ValueError as e:
        return api_response(success=False, error=str(e), status_code=400)
    except Exception as e:
        logger.error(f"재무 분석 오류: {e}", exc_info=True)
        return api_response(success=False, error=f"분석 중 오류가 발생했습니다: {str(e)}", status_code=500)

@app.route('/api/audit-points', methods=['GET'])
@limiter.limit("5 per minute")
def get_audit_points():
    """감사 포인트 분석 수행"""
    try:
        corp_name, financial_data = _get_session_data()
        logger.info(f"감사 포인트 분석 요청: {corp_name}")
        
        analysis = ai_analyzer.audit_points_analysis(corp_name, financial_data)
        formatted_analysis = formatters.format_analysis_result(analysis)
        
        return api_response(
            success=True,
            data={'analysis': formatted_analysis},
            message="감사 포인트 분석이 완료되었습니다."
        )
        
    except ValueError as e:
        return api_response(success=False, error=str(e), status_code=400)
    except Exception as e:
        logger.error(f"감사 포인트 분석 오류: {e}", exc_info=True)
        return api_response(success=False, error=f"분석 중 오류가 발생했습니다: {str(e)}", status_code=500)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("15 per minute")
def chat_with_ai():
    """AI 채팅 응답"""
    try:
        corp_name, financial_data = _get_session_data()
        
        data = request.get_json()
        error = validate_request_data(data, ['question'])
        if error:
            return api_response(success=False, error=error, status_code=400)
        
        question = formatters.sanitize_input(data.get('question', ''))
        if len(question) > 500:
            return api_response(success=False, error="질문은 500자 이내로 입력해주세요.", status_code=400)
        
        logger.info(f"채팅 질문: {corp_name} - {question[:50]}...")
        
        answer = ai_analyzer.chat_response(corp_name, financial_data, question)
        formatted_answer = formatters.format_analysis_result(answer)
        
        return api_response(
            success=True,
            data={'answer': formatted_answer},
            message="응답이 생성되었습니다."
        )
        
    except ValueError as e:
        return api_response(success=False, error=str(e), status_code=400)
    except Exception as e:
        logger.error(f"채팅 응답 오류: {e}", exc_info=True)
        return api_response(success=False, error=f"응답 생성 중 오류가 발생했습니다: {str(e)}", status_code=500)

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return api_response(
        success=True,
        data={'status': 'healthy', 'version': '1.0.0'},
        message="서비스가 정상 작동 중입니다."
    )

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    logger.info(f"🌐 서버가 http://localhost:{port} 에서 실행됩니다.")
    logger.info("✅ 2024년 재무데이터 지원 활성화")
    app.run(debug=debug, host='0.0.0.0', port=port)