// Authentication utilities
const API_BASE_URL = 'http://localhost:8000/api';

function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

function isAuthenticated() {
    return !!getToken();
}

function getAuthHeaders() {
    const token = getToken();
    if (token) {
        return {
            'Authorization': `Bearer ${token}`
        };
    }
    return {};
}

async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            if (data.refresh) {
                localStorage.setItem('refresh_token', data.refresh);
            }
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error refreshing token:', error);
        return false;
    }
}

async function apiRequest(url, options = {}) {
    const headers = {
        ...getAuthHeaders(),
        ...options.headers
    };

    try {
        let response = await fetch(url, { ...options, headers });

        // If unauthorized, try to refresh token
        if (response.status === 401) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                // Retry the request with new token
                const newHeaders = {
                    ...getAuthHeaders(),
                    ...options.headers
                };
                response = await fetch(url, { ...options, headers: newHeaders });
            } else {
                // Refresh failed, redirect to login
                clearTokens();
                window.location.href = '/login';
                return null;
            }
        }

        return response;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// Update UI based on authentication status
function updateAuthUI() {
    const loginLink = document.getElementById('login-link');
    const logoutBtn = document.getElementById('logout-btn');

    if (isAuthenticated()) {
        if (loginLink) loginLink.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
    } else {
        if (loginLink) loginLink.style.display = 'inline-block';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

// Logout handler
document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            clearTokens();
            window.location.href = '/';
        });
    }
});
