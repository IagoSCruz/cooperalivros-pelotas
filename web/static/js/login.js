// Login page functionality
const API_BASE_URL = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', () => {
    // Redirect if already logged in
    if (isAuthenticated()) {
        window.location.href = '/';
        return;
    }

    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', handleLogin);
});

async function handleLogin(e) {
    e.preventDefault();

    const loginMessage = document.getElementById('login-message');
    loginMessage.style.display = 'none';

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            throw new Error('Invalid credentials');
        }

        const data = await response.json();

        // Store tokens
        setToken(data.access, data.refresh);

        // Show success message
        loginMessage.className = 'form-message success';
        loginMessage.textContent = 'Login realizado com sucesso! Redirecionando...';
        loginMessage.style.display = 'block';

        // Redirect to home page
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
    } catch (error) {
        console.error('Login error:', error);

        loginMessage.className = 'form-message error';
        loginMessage.textContent = 'Usuário ou senha inválidos. Por favor, tente novamente.';
        loginMessage.style.display = 'block';
    }
}
