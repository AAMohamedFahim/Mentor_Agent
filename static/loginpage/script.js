const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

// Basic client-side form validation for Sign-Up
document.getElementById('signupForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const errorElement = document.getElementById('signupError');

    if (password.length < 6) {
        errorElement.textContent = 'Password must be at least 6 characters long';
        return;
    }

    // If validation passes, send data to backend
    signUp(name, email, password);
});

// Client-side form validation for Login
document.getElementById('loginForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    // Send login data to backend
    login(email, password);
});

// API function to connect with backend for Sign-Up
async function signUp(name, email, password) {
    try {
        const response = await fetch('http://0.0.0.0:8000/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password }),
        });

        const data = await response.json();
        if (response.status === 200) {
            // Registration successful, redirect to Chatbot page
            window.location.href = '/static/chatbotpage/userdatachat.html';
        } else {
            // Handle error message
            document.getElementById('signupError').textContent = data.detail || 'Registration failed!';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('signupError').textContent = 'Error connecting to the server!';
    }
}

// API function to connect with backend for Login
async function login(email, password) {
    try {
        const response = await fetch('http://0.0.0.0:8000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        if (response.status === 200) {
            // Login successful, redirect to Home page
            window.location.href = '/static/homepage/home.html';
        } else {
            // Handle error message
            document.getElementById('loginError').textContent = data.detail || 'Login failed!';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loginError').textContent = 'Error connecting to the server!';
    }
}
