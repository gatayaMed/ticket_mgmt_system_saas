// Authentication Service
const auth = {
    async login(username, password) {
        try {
            const data = await api.post('/auth/login/', { username, password });
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user', JSON.stringify(data.user));
            return data;
        } catch (error) {
            throw error;
        }
    },

    async register(userData) {
        try {
            const data = await api.post('/auth/register/', userData);
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user', JSON.stringify(data.user));
            return data;
        } catch (error) {
            throw error;
        }
    },

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login.html';
    },

    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    },

    async getProfile() {
        return api.get('/auth/profile/');
    }
};

// Login Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('loginError');
            
            try {
                await auth.login(username, password);
                window.location.href = '/dashboard.html';
            } catch (error) {
                errorDiv.textContent = error.error || 'Login failed. Please try again.';
                errorDiv.classList.remove('d-none');
            }
        });
    }

    // Register Form Handler
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const password2 = document.getElementById('password2').value;
            const errorDiv = document.getElementById('registerError');
            
            if (password !== password2) {
                errorDiv.textContent = 'Passwords do not match';
                errorDiv.classList.remove('d-none');
                return;
            }
            
            try {
                await auth.register({ username, email, password, password2 });
                window.location.href = '/dashboard.html';
            } catch (error) {
                errorDiv.textContent = error.error || 'Registration failed. Please try again.';
                errorDiv.classList.remove('d-none');
            }
        });
    }

    // Logout Button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            auth.logout();
        });
    }

    // Check authentication on protected pages
    const protectedPages = ['dashboard.html', 'organizations.html', 'projects.html', 'tickets.html', 'sprints.html', 'reports.html', 'webhooks.html', 'ticket-detail.html'];
    if (protectedPages.some(page => window.location.pathname.includes(page))) {
        if (!auth.isAuthenticated()) {
            window.location.href = '/login.html';
        }
        // Update user name
        const user = auth.getCurrentUser();
        if (user) {
            const userNameElements = document.querySelectorAll('#userName');
            userNameElements.forEach(el => el.textContent = user.username);
        }
    }
});