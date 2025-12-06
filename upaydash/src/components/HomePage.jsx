import React from 'react';

export default function HomePage() {
  return (
    <div className="bg-gray-100 min-h-screen">
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
            <a href="/home" className="flex items-center px-6 py-3 bg-gray-200 text-gray-800 font-semibold">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
              <span className="ml-3">Home</span>
            </a>

            <a href="/upload" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
              <span className="ml-3">Upload</span>
            </a>

            <a href="/dashboard" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
              <span className="ml-3">Dashboard</span>
            </a>

            <a href="/profile" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
              <span className="ml-3">Profile</span>
            </a>
          </nav>

          <div className="absolute bottom-0 w-64">
            <button
              onClick={() => {
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");
                localStorage.removeItem("authUser");
                window.location.href = "/login";
              }}
              className="flex items-center px-6 py-4 text-gray-600 hover:bg-gray-100 w-full text-left"
            >
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
              <span className="ml-3">Logout</span>
            </button>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="bg-white shadow-sm p-4">
            <h2 className="text-2xl font-semibold text-gray-800">Welcome, User!</h2>
          </header>

          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <a href="/upload" className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 flex flex-col items-center justify-center text-center">
                <div className="bg-indigo-100 text-indigo-600 rounded-full p-4">
                  <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                </div>
                <h3 className="mt-4 text-xl font-semibold text-gray-900">Upload New Documents</h3>
                <p className="mt-2 text-gray-500">Start processing new student records, attendance sheets, and more.</p>
              </a>

              <a href="/dashboard" className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 flex flex-col items-center justify-center text-center">
                <div className="bg-green-100 text-green-600 rounded-full p-4">
                  <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                </div>
                <h3 className="mt-4 text-xl font-semibold text-gray-900">Go To Dashboard</h3>
                <p className="mt-2 text-gray-500">View analytics, track performance, and manage your data.</p>
              </a>
            </div>

            <div className="mt-12 bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Database Overview</h3>

              <div className="flex flex-wrap items-center gap-4 mb-6">
                <select className="p-2 border rounded-md bg-gray-50 focus:ring-indigo-500 focus:border-indigo-500">
                  <option>All Document Types</option>
                  <option>Student Records</option>
                  <option>Attendance</option>
                </select>

                <input type="date" defaultValue="2025-09-29" className="p-2 border rounded-md bg-gray-50 focus:ring-indigo-500 focus:border-indigo-500" />

                <select className="p-2 border rounded-md bg-gray-50 focus:ring-indigo-500 focus:border-indigo-500">
                  <option>All Cities</option>
                  <option>Mumbai</option>
                  <option>Pune</option>
                </select>
              </div>

              <div className="bg-indigo-50 p-6 rounded-lg text-center">
                <p className="text-sm font-medium text-indigo-600">Total Documents in Database</p>
                <p className="text-4xl font-bold text-indigo-900 mt-2">1,254</p>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

