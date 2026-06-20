// API Configuration
const API_BASE_URL = 'http://localhost:8500/api';

// API Client
const api = {
    async request(endpoint, options = {}) {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        // Handle token refresh
        if (response.status === 401) {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    const refreshResponse = await fetch(`${API_BASE_URL}/token/refresh/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ refresh: refreshToken })
                    });
                    
                    if (refreshResponse.ok) {
                        const data = await refreshResponse.json();
                        localStorage.setItem('access_token', data.access);
                        // Save new refresh token if rotated
                        if (data.refresh) {
                            localStorage.setItem('refresh_token', data.refresh);
                        }
                        // Retry original request
                        return this.request(endpoint, options);
                    } else {
                        // Refresh failed — clear tokens and redirect
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('refresh_token');
                        window.location.href = '/login.html';
                    }
                } catch (e) {
                    // Network error during refresh — still try redirect
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login.html';
                }
            } else {
                // No refresh token available
                localStorage.removeItem('access_token');
                window.location.href = '/login.html';
            }
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw error;
        }

        return response.json();
    },

    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    upload(endpoint, formData) {
        const token = localStorage.getItem('access_token');
        const headers = {};
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers,
            body: formData
        }).then(async response => {
            if (response.status === 401) {
                // Handle token refresh
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    try {
                        const refreshResponse = await fetch(`${API_BASE_URL}/token/refresh/`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ refresh: refreshToken })
                        });
                        
                        if (refreshResponse.ok) {
                            const data = await refreshResponse.json();
                            localStorage.setItem('access_token', data.access);
                            if (data.refresh) {
                                localStorage.setItem('refresh_token', data.refresh);
                            }
                            return this.upload(endpoint, formData);
                        }
                    } catch (e) {
                        window.location.href = '/login.html';
                    }
                }
            }
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw error;
            }
            return response.json();
        });
    }
};