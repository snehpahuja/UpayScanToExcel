const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Read tokens
export function getAccessToken() {
  return localStorage.getItem("access_token");
}

export function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}

// Save tokens
export function saveTokens(access, refresh) {
  if (access) localStorage.setItem("access_token", access);
  if (refresh) localStorage.setItem("refresh_token", refresh);
}

// Delete tokens (logout)
export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
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

    if (!res.ok) return null;

    const data = await res.json();
    if (data.access) {
      saveTokens(data.access, data.refresh || refresh);
      return data.access;
    }
    return null;
  } catch {
    return null;
  }
}

// Wrapper fetch that auto-refreshes token.
// Kept name fetchWithAuth for compatibility with current imports.
export async function fetchWithAuth(url, options = {}) {
  const access = getAccessToken();

  const opts = {
    ...options,
    headers: {
      ...(options && options.headers ? options.headers : {}),
      Authorization: access ? `Bearer ${access}` : "",
    },
  };

  let res = await fetch(url, opts);

  // If expired token -> try one refresh and retry once
  if (res.status === 401) {
    const newAccess = await refreshAccessToken();
    if (!newAccess) return res;

    // retry request with new token
    opts.headers = {
      ...(opts.headers || {}),
      Authorization: `Bearer ${newAccess}`,
    };

    // If body is a stream (e.g. already-consumed FormData), callers should recreate it before retry.
    // We're retrying with same opts; in typical cases (FormData or JSON) this will work.
    res = await fetch(url, opts);
  }

  return res;
}

// Export alias for older name if any code imports authFetch
export { fetchWithAuth as authFetch };
