// static/js/main.js - API 객체 포함 버전 (백업용)
document.addEventListener('DOMContentLoaded', () => {
    // API 객체 직접 정의 (api.js가 로드되지 않는 경우 대비)
    if (typeof api === 'undefined') {
        console.warn('⚠️ api.js에서 로드되지 않아 내장 API 객체를 사용합니다.');
        
        window.api = {
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
    }
    
    console.log('✅ API 객체 확인됨:', api);
    
    // DOM 요소 가져오기
    const searchBtn = document.getElementById('searchBtn');
    const companyNameInput = document.getElementById('companyNameInput');
    const searchResults = document.getElementById('searchResults');
    const selectedCompanyDiv = document.getElementById('selectedCompany');
    const analysisSection = document.getElementById('analysisSection');
    const chatSection = document.getElementById('chatSection');
    const analysisResultDiv = document.getElementById('analysisResult');
    const chatMessagesDiv = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const loadingOverlay = document.getElementById('loading');
    const errorToast = document.getElementById('errorMsg');
    const errorText = errorToast.querySelector('.error-text');
    const errorClose = errorToast.querySelector('.error-close');

    // UI 제어 함수들 먼저 정의
    const showLoading = (message = '처리 중입니다...') => {
        const loadingText = loadingOverlay.querySelector('p');
        if (loadingText) loadingText.textContent = message;
        loadingOverlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    };

    const hideLoading = () => {
        loadingOverlay.style.display = 'none';
        document.body.style.overflow = 'auto';
    };

    const showError = (message) => {
        errorText.textContent = message;
        errorToast.style.display = 'flex';
        
        // 5초 후 자동으로 숨기기
        setTimeout(hideError, 5000);
    };

    const hideError = () => {
        errorToast.style.display = 'none';
    };

    const updateButtonStates = (activeButton = null) => {
        const buttons = document.querySelectorAll('.analysis-btn');
        buttons.forEach(btn => {
            btn.classList.remove('active');
            btn.disabled = false;
        });
        
        if (activeButton) {
            activeButton.classList.add('active');
            activeButton.disabled = true;
        }
    };

    // 회사 검색 함수
    async function searchCompany() {
        const companyName = companyNameInput.value.trim();
        console.log('검색 시작:', companyName);
        
        if (!companyName) {
            showError('회사명을 입력해주세요.');
            companyNameInput.focus();
            return;
        }

        if (companyName.length < 2) {
            showError('회사명은 2글자 이상 입력해주세요.');
            return;
        }

        showLoading('기업을 검색하고 있습니다...');
        searchBtn.disabled = true;
        
        try {
            console.log('API 호출 중...');
            const response = await api.post('/api/search', { company_name: companyName });
            console.log('API 응답:', response);
            
            if (response.success) {
                displaySearchResults(response.data.companies);
            } else {
                showError(response.error || '검색 중 오류가 발생했습니다.');
            }
        } catch (error) {
            console.error('검색 오류:', error);
            showError(error.message || '검색 중 오류가 발생했습니다.');
        } finally {
            hideLoading();
            searchBtn.disabled = false;
        }
    }

    function displaySearchResults(companies) {
        console.log('검색 결과 표시:', companies);
        
        if (!companies || companies.length === 0) {
            searchResults.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search" style="font-size: 2rem; color: var(--text-secondary); margin-bottom: 1rem;"></i>
                    <p>검색된 기업이 없습니다.</p>
                    <small>다른 키워드로 검색해보세요.</small>
                </div>
            `;
        } else {
            searchResults.innerHTML = companies.map(c => `
                <div class="company-item" data-corp-code="${c.corp_code}" data-corp-name="${c.corp_name}">
                    <div class="company-info">
                        <div class="company-name">${c.corp_name}</div>
                        <div class="company-code">기업코드: ${c.corp_code} ${c.stock_code ? `| 주식코드: ${c.stock_code}` : ''}</div>
                    </div>
                    <i class="fas fa-chevron-right" style="color: var(--text-secondary);"></i>
                </div>
            `).join('');
            
            // 동적으로 생성된 항목에 이벤트 리스너 추가
            document.querySelectorAll('.company-item').forEach(item => {
                item.addEventListener('click', () => selectCompany(item.dataset));
            });
        }
        searchResults.style.display = 'block';
    }

    async function selectCompany({ corpCode, corpName }) {
        console.log('기업 선택:', corpName, corpCode);
        showLoading(`${corpName} 재무정보를 가져오고 있습니다...`);
        
        try {
            const response = await api.post('/api/select', { corp_code: corpCode, corp_name: corpName });
            console.log('선택 응답:', response);
            
            if (response.success) {
                selectedCompanyDiv.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    <strong>${corpName}</strong> 선택 완료
                    <small style="margin-left: auto; opacity: 0.8;">분석 준비 완료</small>
                `;
                
                selectedCompanyDiv.style.display = 'flex';
                analysisSection.style.display = 'block';
                chatSection.style.display = 'block';
                searchResults.style.display = 'none';
                
                // 부드러운 스크롤
                analysisSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                // 분석 결과 초기화
                analysisResultDiv.style.display = 'none';
                chatMessagesDiv.innerHTML = '';
                updateButtonStates();
            } else {
                showError(response.error || '기업 선택 중 오류가 발생했습니다.');
            }
            
        } catch (error) {
            console.error('선택 오류:', error);
            showError(error.message || '기업 선택 중 오류가 발생했습니다.');
        } finally {
            hideLoading();
        }
    }

    async function getAnalysis(endpoint, type) {
        const button = document.getElementById(`${type === 'business' ? 'businessAnalysisBtn' : type === 'financial' ? 'financialAnalysisBtn' : 'auditPointsBtn'}`);
        
        showLoading('AI가 분석을 수행하고 있습니다...');
        updateButtonStates(button);
        analysisResultDiv.style.display = 'none';
        
        try {
            const response = await api.get(endpoint);
            console.log('분석 응답:', response);
            
            if (response.success) {
                analysisResultDiv.innerHTML = response.data.analysis;
                analysisResultDiv.style.display = 'block';
                
                // 부드러운 스크롤
                setTimeout(() => {
                    analysisResultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            } else {
                showError(response.error || '분석 중 오류가 발생했습니다.');
                updateButtonStates();
            }
            
        } catch (error) {
            console.error('분석 오류:', error);
            showError(error.message || '분석 중 오류가 발생했습니다.');
            updateButtonStates();
        } finally {
            hideLoading();
        }
    }

    async function sendChatMessage() {
        const question = chatInput.value.trim();
        if (!question) {
            chatInput.focus();
            return;
        }

        if (question.length > 500) {
            showError('질문은 500자 이내로 입력해주세요.');
            return;
        }

        // 사용자 메시지 추가
        addChatMessage('user', question);
        chatInput.value = '';
        chatInput.disabled = true;
        chatSendBtn.disabled = true;

        // 타이핑 인디케이터 추가
        const typingId = addTypingIndicator();

        try {
            const response = await api.post('/api/chat', { question });
            console.log('채팅 응답:', response);
            
            removeTypingIndicator(typingId);
            
            if (response.success) {
                addChatMessage('ai', response.data.answer);
            } else {
                addChatMessage('ai', `❌ 오류: ${response.error}`);
            }
        } catch (error) {
            console.error('채팅 오류:', error);
            removeTypingIndicator(typingId);
            addChatMessage('ai', `❌ 죄송합니다. 오류가 발생했습니다: ${error.message}`);
        } finally {
            chatInput.disabled = false;
            chatSendBtn.disabled = false;
            chatInput.focus();
        }
    }

    function addChatMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const time = new Date().toLocaleTimeString('ko-KR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
            <div class="message-sender">
                ${sender === 'user' ? '👤 사용자' : '🤖 AI 어시스턴트'} 
                <span style="font-weight: normal; opacity: 0.7;">${time}</span>
            </div>
            <div class="message-content">${message}</div>
        `;
        
        chatMessagesDiv.appendChild(messageDiv);
        chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
        
        return messageDiv;
    }

    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai typing';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="message-sender">🤖 AI 어시스턴트</div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        chatMessagesDiv.appendChild(typingDiv);
        chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
        
        return typingDiv.id;
    }

    function removeTypingIndicator(typingId) {
        const typingDiv = document.getElementById(typingId);
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    // 초기 환영 메시지
    function showWelcomeMessage() {
        if (chatMessagesDiv.children.length === 0) {
            addChatMessage('ai', '안녕하세요! 선택하신 기업의 재무정보에 대해 궁금한 점을 자유롭게 질문해주세요. 📊');
        }
    }

    // 채팅 섹션이 표시될 때 환영 메시지 추가
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && 
                mutation.attributeName === 'style' && 
                chatSection.style.display === 'block') {
                showWelcomeMessage();
            }
        });
    });

    observer.observe(chatSection, { 
        attributes: true, 
        attributeFilter: ['style'] 
    });

    // 이벤트 리스너 등록 (함수들이 정의된 후에 등록)
    searchBtn.addEventListener('click', searchCompany);
    companyNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            searchCompany();
        }
    });
    
    document.getElementById('businessAnalysisBtn').addEventListener('click', () => getAnalysis('/api/business-analysis', 'business'));
    document.getElementById('financialAnalysisBtn').addEventListener('click', () => getAnalysis('/api/financial-analysis', 'financial'));
    document.getElementById('auditPointsBtn').addEventListener('click', () => getAnalysis('/api/audit-points', 'audit'));
    
    chatSendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendChatMessage();
        }
    });

    // 에러 토스트 닫기
    errorClose.addEventListener('click', hideError);

    // 페이지 로드 시 입력 필드에 포커스
    companyNameInput.focus();
    
    // 디버깅용 로그
    console.log('페이지 로드 완료, 이벤트 리스너 등록됨');
});