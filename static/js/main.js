// static/js/main.js
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

    // 이벤트 리스너 등록
    searchBtn.addEventListener('click', searchCompany);
    companyNameInput.addEventListener('keypress', (e) => e.key === 'Enter' && searchCompany());
    document.getElementById('businessAnalysisBtn').addEventListener('click', () => getAnalysis('/api/business-analysis'));
    document.getElementById('financialAnalysisBtn').addEventListener('click', () => getAnalysis('/api/financial-analysis'));
    document.getElementById('auditPointsBtn').addEventListener('click', () => getAnalysis('/api/audit-points'));
    chatSendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendChatMessage());

    // UI 제어 함수들
    const showLoading = () => document.getElementById('loading').style.display = 'block';
    const hideLoading = () => document.getElementById('loading').style.display = 'none';
    const showError = (message) => {
        const errorDiv = document.getElementById('errorMsg');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => errorDiv.style.display = 'none', 5000);
    };

    // 회사 검색
    async function searchCompany() {
        const companyName = companyNameInput.value.trim();
        if (!companyName) return showError('회사명을 입력해주세요.');

        showLoading();
        try {
            const data = await api.post('/api/search', { company_name: companyName });
            displaySearchResults(data.companies);
        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading();
        }
    }

    function displaySearchResults(companies) {
        if (!companies || companies.length === 0) {
            searchResults.innerHTML = '<p class="no-results">검색된 회사가 없습니다.</p>';
        } else {
            searchResults.innerHTML = companies.map(c => `
                <div class="company-item" data-corp-code="${c.corp_code}" data-corp-name="${c.corp_name}">
                    <div class="company-info">
                        <div class="company-name">${c.corp_name}</div>
                        <div class="company-code">기업코드: ${c.corp_code}</div>
                    </div>
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
        showLoading();
        try {
            await api.post('/api/select', { corp_code: corpCode, corp_name: corpName });
            selectedCompanyDiv.innerHTML = `<div class="selected-company">✅ <strong>${corpName}</strong> 선택 완료</div>`;
            selectedCompanyDiv.style.display = 'block';
            analysisSection.style.display = 'block';
            chatSection.style.display = 'block';
            searchResults.style.display = 'none';
        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading();
        }
    }

    async function getAnalysis(endpoint) {
        showLoading();
        analysisResultDiv.style.display = 'none';
        try {
            const data = await api.get(endpoint);
            analysisResultDiv.innerHTML = data.analysis;
            analysisResultDiv.style.display = 'block';
            analysisResultDiv.scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading();
        }
    }

    async function sendChatMessage() {
        const question = chatInput.value.trim();
        if (!question) return;

        addChatMessage('user', question);
        chatInput.value = '';
        showLoading();

        try {
            const data = await api.post('/api/chat', { question });
            addChatMessage('ai', data.answer);
        } catch (error) {
            addChatMessage('ai', `❌ 오류: ${error.message}`);
        } finally {
            hideLoading();
        }
    }

    function addChatMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = `
            <div class="message-sender">${sender === 'user' ? '👤 사용자' : '🤖 AI'}</div>
            <div class="message-content">${message}</div>`;
        chatMessagesDiv.appendChild(messageDiv);
        chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
    }
});