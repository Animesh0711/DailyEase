// ========== Authentication Functions ==========
// API_BASE is defined in config.js

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }

    if (registerForm) {
        registerForm.addEventListener("submit", handleRegister);
    }
});

async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API_BASE}/auth/login?email=${email}&password=${password}`, {
            method: "POST"
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("user_id", data.user_id);
            localStorage.setItem("user_email", data.email);
            localStorage.setItem("user_name", data.full_name);
            localStorage.setItem("is_admin", data.is_admin);

            alert(data.message);
            window.location.href = "dashboard.html";
        } else {
            alert("Login failed. Please check your credentials.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during login.");
    }
}

async function handleRegister(e) {
    e.preventDefault();

    const formData = {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
        full_name: document.getElementById("full_name").value,
        phone: document.getElementById("phone").value,
        address: document.getElementById("address").value,
        city: document.getElementById("city").value,
        pincode: document.getElementById("pincode").value
    };

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert("Registration successful! Please login.");
            window.location.href = "login.html";
        } else {
            const error = await response.json();
            alert(`Registration failed: ${error.detail}`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during registration.");
    }
}

function logout() {
    if (confirm("Are you sure you want to logout?")) {
        localStorage.clear();
        window.location.href = "login.html";
    }
}
