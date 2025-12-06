import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import LoginPage from './components/LoginPage';
import HomePage from './components/HomePage';
import UploadPage from './components/UploadPage';
import ReviewPage from './components/ReviewPage';
import BulkReviewList from './components/BulkReviewList';
import ProfilePage from './components/ProfilePage';
import DashboardPage from './components/DashboardPage';
import AdminUsers from './components/AdminUsers';

/**
 * NotFound component for 404 pages
 */
function NotFound() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-800 mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-6">Page not found</p>
        <a
          href="/home"
          className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 inline-block"
        >
          Go to Home
        </a>
      </div>
    </div>
  );
}

/**
 * Main App component with routing
 */
export default function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/review/:id" element={<ReviewPage />} />
          <Route path="/bulk-review" element={<BulkReviewList />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/admin/users" element={<AdminUsers />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}
