import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { saveTokens, isAuthenticated, fetchWithAuth, handleApiResponse } from "../lib/auth";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [selectedPortal, setSelectedPortal] = useState('user');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated()) {
      navigate("/home");
    }
  }, [navigate]);

  // Form validation
  const isFormValid = username.trim().length > 0 && password.length > 0;

  async function onSubmit(e) {
    e.preventDefault();
    
    if (!isFormValid) {
      setError("Please enter both username and password");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (res.ok && data.access && data.refresh) {
        // Save tokens first so fetchWithAuth can use them
        saveTokens(data.access, data.refresh);

        // Try to fetch full profile to determine role
        try {
          const profileRes = await fetchWithAuth(`${API_BASE}/api/profile/`);
          const profile = await handleApiResponse(profileRes);
          // Save tokens and user profile in localStorage
          saveTokens(data.access, data.refresh, profile);
          // Determine whether account is admin (role or Django staff/superuser)
          const isAdminAccount = profile?.role === 'admin' || profile?.is_staff === true || profile?.is_superuser === true;

          // If user chose admin portal, require admin account
          if (selectedPortal === 'admin') {
            if (!isAdminAccount) {
              setError('Your account is not an admin. Please sign in to the user portal or use an admin account.');
              return;
            }
            navigate('/admin/users');
            return;
          }

          // If user chose user portal, explicitly block admin accounts from signing in as user
          if (selectedPortal === 'user') {
            if (isAdminAccount) {
              setError('Admin accounts must sign in via the Admin portal. Please select "Admin" and sign in.');
              return;
            }
            navigate('/home');
            return;
          }
          return;
        } catch (err) {
          // If profile fetch fails, fall back to home
          saveTokens(data.access, data.refresh, { username });
          navigate('/home');
          return;
        }
      } else {
        setError(data.detail || "Invalid username or password");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("Network error. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white p-8 rounded shadow">
        <h2 className="text-2xl font-semibold mb-6">Sign in to UPAY</h2>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sign in as</label>
            <div className="flex gap-4">
              <label className="inline-flex items-center">
                <input type="radio" name="portal" value="user" checked={selectedPortal==='user'} onChange={()=>setSelectedPortal('user')} className="mr-2" />
                <span className="text-sm">User</span>
              </label>
              <label className="inline-flex items-center">
                <input type="radio" name="portal" value="admin" checked={selectedPortal==='admin'} onChange={()=>setSelectedPortal('admin')} className="mr-2" />
                <span className="text-sm">Admin</span>
              </label>
            </div>
          </div>
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 w-full p-2 border rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              required
              autoComplete="username"
              disabled={loading}
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full p-2 border rounded focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              required
              autoComplete="current-password"
              disabled={loading}
            />
          </div>
          {error && (
            <div className="text-red-600 text-sm bg-red-50 p-3 rounded" role="alert">
              {error}
            </div>
          )}
          <div>
            <button
              type="submit"
              disabled={loading || !isFormValid}
              className="w-full py-2 px-4 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
