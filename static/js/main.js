// static/js/main.js - Enhanced version
document.addEventListener('DOMContentLoaded', () => {
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

    // 이벤트 리스너 등록
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

    // UI 제어 함수들
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

    // 회사 검색
    async function searchCompany() {
        const companyName = companyNameInput.value.trim();
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
            const data = await api.post('/api/search', { company_name: companyName });
            displaySearchResults(data.companies);
        } catch (error) {
            showError(error.message || '검색 중 오류가 발생했습니다.');
            console.error('Search error:', error);
        } finally {
            hideLoading();
            searchBtn.disabled = false;
        }
    }

    function displaySearchResults(companies) {
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
        showLoading(`${corpName} 재무정보를 가져오고 있습니다...`);
        
        try {
            await api.post('/api/select', { corp_code: corpCode, corp_name: corpName });
            
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
            
        } catch (error) {
            showError(error.message || '기업 선택 중 오류가 발생했습니다.');
            console.error('Selection error:', error);
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
            const data = await api.get(endpoint);
            
            analysisResultDiv.innerHTML = data.analysis;
            analysisResultDiv.style.display = 'block';
            
            // 부드러운 스크롤
            setTimeout(() => {
                analysisResultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
            
        } catch (error) {
            showError(error.message || '분석 중 오류가 발생했습니다.');
            console.error('Analysis error:', error);
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
            const data = await api.post('/api/chat', { question });
            removeTypingIndicator(typingId);
            addChatMessage('ai', data.answer);
        } catch (error) {
            removeTypingIndicator(typingId);
            addChatMessage('ai', `❌ 죄송합니다. 오류가 발생했습니다: ${error.message}`);
            console.error('Chat error:', error);
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

    // 페이지 로드 시 입력 필드에 포커스
    companyNameInput.focus();
});