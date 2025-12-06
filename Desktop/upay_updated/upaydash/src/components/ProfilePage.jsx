import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuthUser, clearTokens, isAuthenticated, fetchWithAuth, handleApiResponse } from '../lib/auth';

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function ProfilePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
      return;
    }

    const authUser = getAuthUser();
    setUser(authUser);

    // Try to fetch additional profile data from backend
    fetchProfileData();
  }, [navigate]);

  async function fetchProfileData() {
    try {
      const res = await fetchWithAuth(`${API_BASE}/api/profile/`);
      const data = await handleApiResponse(res);
      setProfileData(data);
    } catch (err) {
      console.log('Profile API not available, using local data only');
      // Not a critical error - we can show basic info from localStorage
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    clearTokens();
    navigate('/login');
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-indigo-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-64 bg-white shadow-md relative">
          <div className="p-6">
            <div className="flex items-center">
              <svg className="h-8 w-auto text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.375a6.375 6.375 0 006.375-6.375V9.75A6.375 6.375 0 0012 3.375zM12 18.375A6.375 6.375 0 015.625 12V9.75a6.375 6.375 0 016.375-6.375zM12 18.375v-6.375" />
              </svg>
              <h1 className="ml-3 text-xl font-bold text-gray-800">UPAY</h1>
            </div>
          </div>

          <nav className="mt-6">
            <a href="/home" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span className="ml-3">Home</span>
            </a>

            <a href="/upload" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <span className="ml-3">Upload</span>
            </a>

            <a href="/bulk-review" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="ml-3">Review</span>
            </a>

            <a href="/dashboard" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span className="ml-3">Dashboard</span>
            </a>

            <a href="/profile" className="flex items-center px-6 py-3 bg-gray-200 text-gray-800 font-semibold">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span className="ml-3">Profile</span>
            </a>
          </nav>

          <div className="absolute bottom-0 w-64">
            <button
              onClick={handleLogout}
              className="flex items-center px-6 py-4 text-gray-600 hover:bg-gray-100 w-full text-left"
            >
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span className="ml-3">Logout</span>
            </button>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="bg-white shadow-sm p-4">
            <h2 className="text-2xl font-semibold text-gray-800">User Profile</h2>
          </header>

          <main className="flex-1 overflow-y-auto bg-gray-100 p-6">
            <div className="max-w-4xl mx-auto">
              {/* Profile Card */}
              <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-500 to-purple-600 h-32"></div>
                <div className="px-6 pb-6">
                  <div className="flex items-center -mt-16 mb-6">
                    <div className="bg-white rounded-full p-2 shadow-lg">
                      <div className="bg-indigo-100 rounded-full p-6">
                        <svg className="h-20 w-20 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-6 mt-16">
                      <h3 className="text-2xl font-bold text-gray-800">
                        {profileData?.username || user?.username || 'User'}
                      </h3>
                      <p className="text-gray-600">
                        {profileData?.email || 'No email provided'}
                      </p>
                    </div>
                  </div>

                  {/* Profile Information */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="text-lg font-semibold text-gray-800 mb-4">Account Information</h4>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-600">Username</label>
                        <p className="mt-1 text-gray-800">{profileData?.username || user?.username || '—'}</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-600">Email</label>
                        <p className="mt-1 text-gray-800">{profileData?.email || '—'}</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-600">Role</label>
                        <p className="mt-1 text-gray-800">
                          {profileData?.is_staff ? 'Administrator' : 'User'}
                        </p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="text-lg font-semibold text-gray-800 mb-4">Activity</h4>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-600">Member Since</label>
                        <p className="mt-1 text-gray-800">
                          {profileData?.date_joined 
                            ? new Date(profileData.date_joined).toLocaleDateString()
                            : '—'}
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-600">Last Login</label>
                        <p className="mt-1 text-gray-800">
                          {profileData?.last_login 
                            ? new Date(profileData.last_login).toLocaleDateString()
                            : '—'}
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-600">Account Status</label>
                        <span className="mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Active
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="mt-8 pt-6 border-t border-gray-200">
                    <div className="flex gap-4">
                      <button
                        onClick={() => navigate('/home')}
                        className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                      >
                        Back to Home
                      </button>
                      <button
                        onClick={handleLogout}
                        className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                      >
                        Logout
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              {/* Recent Uploads */}
              {profileData?.recent_uploads && profileData.recent_uploads.length > 0 && (
                <div className="mt-6 bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4">Your Recent Uploads</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Filename</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {profileData.recent_uploads.map(doc => (
                          <tr key={doc.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{doc.original_filename}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{doc.status}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(doc.upload_timestamp).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              {/* Additional Info Card */}
              <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start">
                  <svg className="h-5 w-5 text-blue-600 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h4 className="text-sm font-medium text-blue-800">Profile Information</h4>
                    <p className="mt-1 text-sm text-blue-700">
                      This profile page displays your account information. To update your details, please contact your system administrator.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}