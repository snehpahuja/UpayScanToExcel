const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Standardized token key names
const ACCESS_TOKEN_KEY = "access";
const REFRESH_TOKEN_KEY = "refresh";
const AUTH_USER_KEY = "authUser";

// Read tokens
export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getAuthUser() {
  const user = localStorage.getItem(AUTH_USER_KEY);
  return user ? JSON.parse(user) : null;
}

// Save tokens
export function saveTokens(access, refresh, user = null) {
  if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  if (user) localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
}

// Delete tokens (logout)
export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

// Check if user is authenticated
export function isAuthenticated() {
  return !!getAccessToken();
}

// Refresh token flow
export async function refreshAccessToken() {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  try {
    const res = await fetch(`${API_BASE}/api/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh })
    });

    if (!res.ok) {
      clearTokens();
      return null;
    }

    const data = await res.json();
    if (data.access) {
      saveTokens(data.access, data.refresh || refresh);
      return data.access;
    }
    return null;
  } catch (error) {
    console.error("Token refresh failed:", error);
    clearTokens();
    return null;
  }
}

// Centralized authenticated fetch wrapper
export async function fetchWithAuth(url, options = {}) {
  const access = getAccessToken();

  if (!access) {
    throw new Error("No authentication token available");
  }

  const opts = {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${access}`,
    },
  };

  let res = await fetch(url, opts);

  // If token expired, try to refresh and retry once
  if (res.status === 401) {
    const newAccess = await refreshAccessToken();
    
    if (!newAccess) {
      // Refresh failed, redirect to login
      window.location.href = "/login";
      throw new Error("Authentication failed");
    }

    // Retry request with new token
    opts.headers.Authorization = `Bearer ${newAccess}`;
    res = await fetch(url, opts);
  }

  return res;
}

// Helper to handle API errors consistently
export async function handleApiResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ 
      detail: `HTTP ${response.status}: ${response.statusText}` 
    }));
    throw new Error(error.detail || error.message || "API request failed");
  }
  return response.json();
}

// Export alias for compatibility
export { fetchWithAuth as authFetch };