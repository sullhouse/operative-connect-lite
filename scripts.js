// const apiDomain = 'https://ocl-api.sullhouse.com';
const apiDomain = 'http://127.0.0.1:5000';

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

async function fetchOrganizations() {
    const token = getCookie('token');
    if (!token) {
        alert('No token found. Please log in first.');
        return;
    }

    const response = await fetch(`${apiDomain}/organizations/list`, {
        method: 'GET',
        headers: {
            'x-access-token': token
        }
    });

    const data = await response.json();
    if (response.ok) {
        displayOrganizations(data.organizations);
    } else {
        alert(data.message);
    }
}

async function fetchPartnerships() {
    const token = getCookie('token');
    if (!token) {
        alert('No token found. Please log in first.');
        return;
    }

    const response = await fetch(`${apiDomain}/organizations/partnerships/list`, {
        method: 'GET',
        headers: {
            'x-access-token': token
        }
    });

    const data = await response.json();
    if (response.ok) {
        displayPartnerships(data.partnerships);
    } else {
        alert(data.message);
    }
}

function displayOrganizations(organizations) {
    const orgList = document.getElementById('organization-list');
    orgList.innerHTML = '';
    organizations.forEach(org => {
        const li = document.createElement('li');
        li.textContent = `${org.organization_name} (Created by: ${org.created_by})`;
        orgList.appendChild(li);
    });
}

function displayPartnerships(partnerships) {
    const partnershipList = document.getElementById('partnership-list');
    partnershipList.innerHTML = '';
    partnerships.forEach(partnership => {
        const li = document.createElement('li');
        li.textContent = `${partnership.demand_organization.organization_name} <-> ${partnership.supply_organization.organization_name}`;
        partnershipList.appendChild(li);
    });
}

document.getElementById('add-organization-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const orgName = document.getElementById('new-organization-name').value;

    const response = await fetch(`${apiDomain}/organizations/create`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-access-token': getCookie('token')
        },
        body: JSON.stringify({ organization_name: orgName })
    });

    const data = await response.json();
    if (response.ok) {
        alert('Organization created successfully!');
        fetchOrganizations();
    } else {
        alert(data.message);
    }
});

document.getElementById('add-partnership-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const demandOrgId = document.getElementById('demand-org-id').value;
    const supplyOrgId = document.getElementById('supply-org-id').value;

    const response = await fetch(`${apiDomain}/organizations/partnerships/create`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-access-token': getCookie('token')
        },
        body: JSON.stringify({ demand_org_id: demandOrgId, supply_org_id: supplyOrgId })
    });

    const data = await response.json();
    if (response.ok) {
        alert('Partnership created successfully!');
        fetchPartnerships();
    } else {
        alert(data.message);
    }
});

function showHomeView() {
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('register-container').style.display = 'none';
    document.getElementById('home-container').style.display = 'block';
    fetchOrganizations();
    fetchPartnerships();
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
        showHomeView();
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

async function checkIfLoggedIn() {
    const token = getCookie('token');
    if (!token) {
        showLoginForm();
        return;
    }

    const response = await fetch(`${apiDomain}/auth/validate-token`, {
        method: 'GET',
        headers: {
            'x-access-token': token
        }
    });

    if (response.ok) {
        showHomeView();
    } else {
        showLoginForm();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    checkIfLoggedIn();
});