const apiDomain = 'https://ocl-api.sullhouse.com';

// Validation helper functions
function validateUsername(username) {
    if (!username || typeof username !== 'string') {
        return { valid: false, message: "Username is required" };
    }

    if (username.length < 3 || username.length > 50) {
        return { valid: false, message: "Username must be between 3 and 50 characters" };
    }

    const usernameRegex = /^[a-zA-Z0-9_\-\.@]+$/;
    if (!usernameRegex.test(username)) {
        return { valid: false, message: "Username can only contain letters, numbers, dots, @, hyphens, and underscores" };
    }

    return { valid: true };
}

function validatePassword(password) {
    if (!password || typeof password !== 'string') {
        return { valid: false, message: "Password is required" };
    }

    if (password.length < 8) {
        return { valid: false, message: "Password must be at least 8 characters long" };
    }

    if (!/[A-Z]/.test(password)) {
        return { valid: false, message: "Password must contain at least one uppercase letter" };
    }

    if (!/[a-z]/.test(password)) {
        return { valid: false, message: "Password must contain at least one lowercase letter" };
    }

    if (!/\d/.test(password)) {
        return { valid: false, message: "Password must contain at least one number" };
    }

    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        return { valid: false, message: "Password must contain at least one special character" };
    }

    return { valid: true };
}

async function refreshToken() {
    const token = getCookie('token');
    if (!token) {
        alert('No token found. Please log in first.');
        return;
    }

    const response = await fetch(`${apiDomain}/auth/refresh`, {
        method: 'POST',
        headers: {
            'x-access-token': token
        }
    });

    const data = await response.json();
    if (response.ok) {
        document.cookie = `token=${data.token}; path=/`;
        alert('Token refreshed successfully!');
    } else {
        alert(data.message);
    }
}

document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    // Validate username
    const usernameValidation = validateUsername(username);
    if (!usernameValidation.valid) {
        alert(usernameValidation.message);
        return;
    }

    // Validate password
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
        alert(passwordValidation.message);
        return;
    }

    const response = await fetch(`${apiDomain}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (response.ok) {
        document.cookie = `token=${data.token}; path=/`;
        alert('Login successful!');
    } else {
        alert(data.message);
    }
});

document.getElementById('register-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    // Validate username
    const usernameValidation = validateUsername(username);
    if (!usernameValidation.valid) {
        alert(usernameValidation.message);
        return;
    }

    // Validate password
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
        alert(passwordValidation.message);
        return;
    }

    const response = await fetch(`${apiDomain}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (response.ok) {
        alert('Registration successful! You can now log in.');
        showLoginForm();
    } else {
        alert(data.message);
    }
});

document.getElementById('protected-button').addEventListener('click', async function() {
    const token = getCookie('token');
    if (!token) {
        alert('No token found. Please log in first.');
        return;
    }

    const response = await fetch(`${apiDomain}/auth/protected`, {
        method: 'GET',
        headers: {
            'x-access-token': token
        }
    });

    const data = await response.json();
    if (response.ok) {
        alert(`Protected endpoint response: ${data.message}`);
    } else {
        alert(data.message);
    }
});

document.getElementById('show-register').addEventListener('click', function(event) {
    event.preventDefault();
    showRegisterForm();
});

document.getElementById('show-login').addEventListener('click', function(event) {
    event.preventDefault();
    showLoginForm();
});

function showRegisterForm() {
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('register-container').style.display = 'block';
}

function showLoginForm() {
    document.getElementById('login-container').style.display = 'block';
    document.getElementById('register-container').style.display = 'none';
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}