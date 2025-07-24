# 🗒️ 개요

## **프로젝트 설명**

1. DART API를 활용해 공시보고서 데이터를 실시간으로 가져온다.
2. Gemini를 이용해 데이터를 분석하고 결과를 제공한다.
3. 추가로 궁금한 부분은 AI 챗봇을 이용해 질문한다.

## **사용 기술 및 특징**

- **AI**: Google Generative AI
- **데이터**: 금융감독원 DART Open API
- **백엔드**: Python(Flask)
- **프론트엔드**: JavaScript, CSS



# ⭐ 주요 기능

- **실시간 기업 검색**: DART에 등록된 모든 상장기업 검색 및 선택
- **3가지 AI 분석**: 사업분석, 재무분석, 감사 포인트 분석
- **AI 채팅**: 선택 기업의 재무데이터 기반 실시간 질의응답



# 환경 설정

### **API 키 및 인증 파일 준비**

**DART API키 받기:** https://opendart.fss.or.kr/

**Gemini API키 받기:** https://aistudio.google.com/apikey?hl=ko

```bash
# .env 파일 생성
DART_API_KEY=our-dart-api-key
GEMINI_API_KEY=your-gemini-api-key
FLASK_SECRET_KEY=your-super-secret-key-change-in-production
```

### 실행 단계

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 서버 실행
python app.py
```
