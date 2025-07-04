// static/js/api.js - 완전한 버전
const api = {
    async post(endpoint, body) {
        console.log(`POST ${endpoint}:`, body);
        return this._fetch(endpoint, 'POST', body);
    },

    async get(endpoint) {
        console.log(`GET ${endpoint}`);
        return this._fetch(endpoint, 'GET');
    },

    async _fetch(endpoint, method, body = null) {
        const options = {
            method: method,
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }

        try {
            console.log(`API 요청: ${method} ${endpoint}`, options);
            
            const response = await fetch(endpoint, options);
            console.log(`API 응답 상태: ${response.status}`);
            
            const data = await response.json();
            console.log(`API 응답 데이터:`, data);

            if (!response.ok) {
                const errorMessage = data.error || `HTTP error! status: ${response.status}`;
                console.error(`API 오류: ${errorMessage}`);
                throw new Error(errorMessage);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            
            // 네트워크 오류인지 확인
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('네트워크 연결을 확인해주세요.');
            }
            
            // JSON 파싱 오류인지 확인
            if (error.name === 'SyntaxError') {
                throw new Error('서버 응답 형식이 올바르지 않습니다.');
            }
            
            throw error;
        }
    }
};

// api 객체가 정상적으로 정의되었는지 확인
console.log('✅ api.js 로드 완료:', typeof api);