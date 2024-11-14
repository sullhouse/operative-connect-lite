const apiDomain = 'https://ocl-api.sullhouse.com';

document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

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