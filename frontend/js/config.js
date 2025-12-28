const API_BASE = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://localhost:8000/api"
    : "https://dailyeaze.onrender.com/api"; // Default to production URL (will update after deployment)
