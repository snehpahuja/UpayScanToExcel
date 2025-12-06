import React, {useState, useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchWithAuth, handleApiResponse, getAuthUser, isAuthenticated, clearTokens } from '../lib/auth';

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function AdminUsers() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('employee');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleCreate(e) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      // Client-side validation
      if (!username || !email || !password) {
        setMessage({ type: 'error', text: 'Please fill username, email and password.' });
        setLoading(false);
        return;
      }
      if (!email.endsWith('@upayngo.com')) {
        setMessage({ type: 'error', text: 'Email must be an @upayngo.com address.' });
        setLoading(false);
        return;
      }

      const payload = { username, email, role, password };
      const res = await fetchWithAuth(`${API_BASE}/api/signup/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      // If server returns validation errors, read and show them
      if (!res.ok) {
        let errBody = null;
        try {
          errBody = await res.json();
        } catch (jsonErr) {
          errBody = { detail: `HTTP ${res.status} ${res.statusText}` };
        }

        // Format error messages (DRF returns dict of field -> [errors])
        let messageText = '';
        if (errBody.detail) {
          messageText = errBody.detail;
        } else if (typeof errBody === 'object') {
          const parts = [];
          Object.keys(errBody).forEach(k => {
            const v = errBody[k];
            if (Array.isArray(v)) parts.push(`${k}: ${v.join(', ')}`);
            else parts.push(`${k}: ${JSON.stringify(v)}`);
          });
          messageText = parts.join(' | ');
        } else {
          messageText = String(errBody);
        }

        setMessage({ type: 'error', text: messageText || 'Signup failed' });
        setLoading(false);
        return;
      }

      const data = await res.json();
      setMessage({ type: 'success', text: data.message || 'User created' });
      setUsername(''); setEmail(''); setRole('employee'); setPassword('');
      // Refresh list to include the newly created user
      fetchUsers();
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to create user' });
    } finally {
      setLoading(false);
    }
  }

  // Fetch list of users for admin
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // Protect route on client side
    if (!isAuthenticated()) {
      window.location.href = '/login';
      return;
    }
    const authUser = getAuthUser();
    // Allow access if stored profile indicates admin role OR staff flag
    if (!authUser || (authUser.role !== 'admin' && !authUser.is_staff && !authUser.is_superuser)) {
      window.location.href = '/home';
      return;
    }
    fetchUsers();
  }, []);

  async function fetchUsers() {
    try {
      const res = await fetchWithAuth(`${API_BASE}/api/users/`);
      const data = await handleApiResponse(res);
      // API may return paginated response {count, next, previous, results}
      const list = Array.isArray(data) ? data : (data.results || data.items || []);
      setUsers(list);
    } catch (err) {
      console.error('Failed to load users', err);
    }
  }

  async function handleDelete(userId) {
    if (!confirm('Delete this user? This action cannot be undone.')) return;
    try {
      const res = await fetchWithAuth(`${API_BASE}/api/users/${userId}/`, {
        method: 'DELETE'
      });
      if (res.status === 204 || res.ok) {
        setUsers(prev => prev.filter(u => u.id !== userId));
      } else {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || 'Failed to delete user');
      }
    } catch (err) {
      console.error('Delete user error', err);
      alert('Delete failed');
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-2xl mx-auto bg-white p-6 rounded shadow">
        <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold mb-4">Admin: Create User</h2>
          <div>
            <button
              onClick={() => { clearTokens(); navigate('/login'); }}
              className="px-3 py-1 bg-red-600 text-white rounded text-sm"
            >
              Logout
            </button>
          </div>
        </div>
        {message && (
          <div className={`p-3 rounded mb-4 ${message.type==='success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {message.text}
          </div>
        )}
        <form onSubmit={handleCreate}>
          <label className="block mb-2">Username</label>
          <input value={username} onChange={(e)=>setUsername(e.target.value)} className="w-full p-2 border rounded mb-4" />

          <label className="block mb-2">Email</label>
          <input value={email} onChange={(e)=>setEmail(e.target.value)} className="w-full p-2 border rounded mb-4" />

          <label className="block mb-2">Password</label>
          <input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" className="w-full p-2 border rounded mb-4" />

          <label className="block mb-2">Role</label>
          <select value={role} onChange={(e)=>setRole(e.target.value)} className="w-full p-2 border rounded mb-4">
            <option value="employee">Employee</option>
            <option value="admin">Admin</option>
          </select>

          <button type="submit" disabled={loading} className="px-4 py-2 bg-indigo-600 text-white rounded">
            {loading ? 'Creating…' : 'Create User'}
          </button>
        </form>
        
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2">Existing Users</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Username</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map(u => (
                  <tr key={u.id}>
                    <td className="px-4 py-2 text-sm text-gray-700">{u.id}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{u.username}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{u.email}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{u.role}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">
                      <button onClick={() => handleDelete(u.id)} className="px-3 py-1 bg-red-600 text-white rounded text-sm">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
