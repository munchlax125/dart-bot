# 🔍 DART + Gemini 사업보고서 분석 웹 애플리케이션

## 📁 프로젝트 구조

```
dart-gemini-webapp/
├── app.py                      # Flask 백엔드 서버
├── requirements.txt            # Python 의존성
├── .env                        # 환경변수 (비공개)
├── .env_template              # 환경변수 템플릿
├── templates/                 # HTML 템플릿
│   └── index.html            # 메인 웹 페이지
├── static/                   # 정적 파일 (선택사항)
│   ├── css/
│   ├── js/
│   └── images/
└── README.md                 # 프로젝트 설명서
```

## 🚀 설치 및 실행

### 1️⃣ 환경 설정

```bash
# 프로젝트 폴더 생성
mkdir dart-gemini-webapp
cd dart-gemini-webapp

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2️⃣ 폴더 구조 생성

```bash
# 템플릿 폴더 생성
mkdir templates
mkdir static

# 파일 배치
# - app.py (루트 폴더)
# - templates/index.html
# - requirements.txt
# - .env
```

### 3️⃣ 환경변수 설정

`.env` 파일 생성:
```bash
# DART API 키
DART_API_KEY=your_dart_api_key_here

# Gemini API 키
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4️⃣ 서버 실행

```bash
python app.py
```

서버가 실행되면 브라우저에서 `http://localhost:5000` 접속

## 🌟 주요 기능

### 🏢 회사 검색
- 회사명 입력으로 DART 등록 기업 검색
- 실시간 검색 결과 표시
- 클릭으로 간편 선택

### 📊 분석 기능
- **간단 분석**: 재무 건전성, 수익성, 성장성 종합 분석
- **감사 유의사항**: 회계감사 관점의 위험요소 및 검토 포인트

### 🤖 AI 챗봇
- 선택한 회사의 재무데이터 기반 질의응답
- 실시간 대화형 인터페이스
- 구체적인 숫자와 근거 제공

## 🎨 UI/UX 특징

### 📱 반응형 디자인
- 모바일, 태블릿, 데스크톱 최적화
- 그리드 레이아웃으로 깔끔한 구성

### 🎯 사용자 경험
- 직관적인 카드 기반 인터페이스
- 실시간 로딩 인디케이터
- 명확한 성공/오류 메시지
- 부드러운 애니메이션 효과

### 🎨 모던 디자인
- 그라디언트 배경과 카드 그림자
- 호버 효과와 트랜지션
- 일관된 색상 체계 (보라-파랑 계열)

## 🔧 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 메인 페이지 |
| `/api/search` | POST | 회사 검색 |
| `/api/select` | POST | 회사 선택 |
| `/api/simple-analysis` | GET | 간단 분석 |
| `/api/audit-points` | GET | 감사 유의사항 |
| `/api/chat` | POST | AI 챗봇 |
| `/api/status` | GET | 현재 상태 확인 |

## 🛡 보안 및 오류 처리

### 🔐 보안
- API 키는 환경변수로 관리
- CORS 설정으로 크로스 도메인 보안
- 입력 데이터 검증

### ⚠️ 오류 처리
- API 호출 실패 시 사용자 친화적 메시지
- 네트워크 오류 자동 감지
- 로딩 상태 시각적 표시

## 🎯 사용 시나리오

1. **투자 분석가**: 상장기업 재무 상태 빠른 파악
2. **회계사**: 감사 계획 수립 시 위험요소 사전 파악  
3. **개인 투자자**: 투자 전 기업 분석
4. **금융 전문가**: 고객 상담용 자료 준비

## 🔄 확장 가능성

- 📊 차트 및 그래프 시각화 추가
- 📈 다년도 트렌드 분석
- 📱 모바일 앱 연동
- 🤖 더 정교한 AI 분석 모델
- 📧 분석 결과 이메일 전송
- 💾 분석 이력 저장 기능

## 🐛 문제 해결

### 일반적인 오류
1. **API 키 오류**: `.env` 파일의 API 키 확인
2. **포트 충돌**: `app.py`에서 포트 번호 변경 (기본: 5000)
3. **의존성 오류**: `pip install -r requirements.txt` 재실행

### 성능 최적화
- API 응답 캐싱 구현
- 데이터베이스 연동으로 분석 결과 저장
- CDN 사용으로 정적 파일 로딩 속도 개선