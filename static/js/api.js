// static/js/api.js
const api = {
    async post(endpoint, body) {
        return this._fetch(endpoint, 'POST', body);
    },

    async get(endpoint) {
        return this._fetch(endpoint, 'GET');
    },

    async _fetch(endpoint, method, body = null) {
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) {
            options.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(endpoint, options);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};