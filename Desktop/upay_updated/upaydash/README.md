# UPAY Frontend Dashboard

A modern React-based frontend for the UPAY document processing system.

## 🚀 Features

- **User Authentication**: JWT-based authentication with automatic token refresh
- **Document Upload**: Upload multiple documents with validation
  - Supported formats: PDF, JPG, JPEG, PNG (matches Django backend)
  - File size limit: 10MB per file
- **Document Review**: Review and edit OCR-extracted data with visual preview
- **Bulk Management**: View and manage all uploaded documents
- **Responsive Design**: Built with Tailwind CSS for mobile-first design
- **Error Handling**: Comprehensive error boundaries and user feedback
- **Clean Code**: Following React best practices and clean coding principles

## 🛠️ Tech Stack

- **Framework**: React 18.2
- **Build Tool**: Vite 5.0
- **Styling**: Tailwind CSS 3.4
- **Routing**: React Router DOM 6.14
- **Package Manager**: npm

## 📋 Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Django backend running on http://localhost:8000 (or configured API endpoint)

## 🔧 Installation

1. **Clone the repository** (if not already done)

2. **Install dependencies**:
   ```bash
   cd upaydash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your API base URL:
   ```env
   VITE_API_BASE=http://localhost:8000
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```
   
   The app will open at http://localhost:3000

## 🏗️ Build for Production

```bash
npm run build
```

The production-ready files will be in the `dist/` directory.

## 📁 Project Structure

```
upaydash/
├── src/
│   ├── components/          # React components
│   │   ├── LoginPage.jsx   # Authentication page
│   │   ├── HomePage.jsx    # Main dashboard
│   │   ├── UploadPage.jsx  # Document upload
│   │   ├── ReviewPage.jsx  # Document review/edit
│   │   ├── BulkReviewList.jsx  # Document listing
│   │   ├── ErrorBoundary.jsx   # Error handling
│   │   └── HTMLLoader.jsx  # Legacy prototype loader
│   ├── lib/                # Utilities
│   │   ├── auth.js        # Authentication utilities
│   │   ├── constants.js   # App constants
│   │   └── utils.js       # Helper functions
│   ├── App.jsx            # Main app with routing
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── index.html            # HTML template
├── vite.config.mjs       # Vite configuration
├── tailwind.config.cjs   # Tailwind configuration
└── package.json          # Dependencies

```

## 🔑 Key Improvements (Latest Refactor)

### ✅ Fixed Critical Bugs
1. **Authentication System**: Fixed localStorage key mismatch between LoginPage and auth.js
2. **ES Module Compatibility**: Removed problematic `require()` calls in ReviewPage
3. **Centralized Auth**: Single `fetchWithAuth` implementation across all components
4. **Error Handling**: Comprehensive error handling with user-friendly messages

### ✅ Code Quality Enhancements
1. **No Code Duplication**: Centralized utilities in `lib/` directory
2. **Input Validation**: All forms validate user input before submission
3. **Accessibility**: Added ARIA labels, proper form labels, keyboard navigation
4. **Loading States**: Proper loading indicators and disabled states
5. **Error Boundaries**: React error boundary to prevent app crashes

### ✅ Security Improvements
1. **Token Management**: Secure token storage and automatic refresh
2. **Protected Routes**: Authentication checks on all protected pages
3. **Input Sanitization**: Validation of file uploads and form inputs

### ✅ User Experience
1. **Better Feedback**: Clear success/error messages for all actions
2. **Navigation**: Proper SPA navigation (no full page reloads)
3. **Responsive Design**: Works on mobile, tablet, and desktop
4. **Visual Indicators**: Status badges, loading spinners, progress feedback

## 🔐 Authentication Flow

1. User logs in with username/password
2. Backend returns JWT access and refresh tokens
3. Tokens stored in localStorage
4. All API requests include access token in Authorization header
5. If token expires (401), automatically refresh and retry
6. If refresh fails, redirect to login

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## 🌐 API Integration

The app expects the following Django API endpoints:

- `POST /api/token/` - Login (get JWT tokens)
- `POST /api/token/refresh/` - Refresh access token
- `GET /api/documents/` - List all documents
- `GET /api/documents/:id/` - Get document details
- `PATCH /api/documents/:id/` - Update document
- `POST /api/documents/:id/finalize/` - Finalize document
- `POST /api/upload/files/` - Upload documents

## 🐛 Debugging

### Common Issues

**"Network error" on login**:
- Check if Django backend is running
- Verify `VITE_API_BASE` in `.env` is correct
- Check browser console for CORS errors

**"Authentication failed"**:
- Clear localStorage: `localStorage.clear()`
- Refresh page and try logging in again

**Components not loading**:
- Check browser console for errors
- Verify all dependencies are installed: `npm install`

## 🤝 Contributing

When contributing, please follow these guidelines:
1. Use functional components with hooks
2. Follow existing code style and naming conventions
3. Add proper error handling for all async operations
4. Include loading states for all API calls
5. Validate all user inputs
6. Add comments for complex logic
7. Test on multiple screen sizes

## 📄 License

This project is part of the UPAY document processing system.

## 🔗 Related Projects

- **Backend**: Django REST API for document processing
- **OCR Engine**: Python-based OCR processing

---

**Last Updated**: December 2024  
**Version**: 1.0.0 (Refactored)