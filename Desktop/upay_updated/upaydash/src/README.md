# UPAY Dashboard - Source Code Documentation

## Project Structure

```
src/
├── components/          # React components
│   ├── LoginPage.jsx   # User authentication
│   ├── HomePage.jsx    # Main dashboard
│   ├── UploadPage.jsx  # Document upload interface
│   ├── ReviewPage.jsx  # Document review and editing
│   ├── BulkReviewList.jsx  # List of all documents
│   └── HTMLLoader.jsx  # Legacy HTML prototype loader
├── lib/                # Utility libraries
│   ├── auth.js        # Authentication utilities
│   ├── constants.js   # Application constants
│   └── utils.js       # Helper functions
├── App.jsx            # Main app component with routing
├── main.jsx           # Application entry point
└── index.css          # Global styles (Tailwind)
```

## Key Features

### Authentication System
- JWT-based authentication with automatic token refresh
- Centralized auth utilities in `lib/auth.js`
- Protected routes with redirect to login

### Document Management
- Upload documents with validation (file type, size)
  - Supported formats: **PDF, JPG, JPEG, PNG only** (matches backend)
  - Maximum file size: 10MB per file
- Review and edit extracted OCR data
- Bulk document listing with status indicators
- Real-time status updates

### Code Quality Improvements
- Consistent error handling across all components
- Proper loading states and user feedback
- Input validation on all forms
- Accessibility improvements (ARIA labels, keyboard navigation)
- No code duplication - centralized utilities

## Environment Variables

Create a `.env` file in the project root:

```env
VITE_API_BASE=http://localhost:8000
```

## API Integration

All API calls use the centralized `fetchWithAuth` function from `lib/auth.js`:

```javascript
import { fetchWithAuth, handleApiResponse } from '../lib/auth';

const response = await fetchWithAuth(`${API_BASE}/api/endpoint/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
});

const result = await handleApiResponse(response);
```

## Component Guidelines

### State Management
- Use React hooks (useState, useEffect)
- Keep state local to components when possible
- Lift state up only when needed

### Error Handling
- Always wrap API calls in try-catch blocks
- Display user-friendly error messages
- Log errors to console for debugging

### Validation
- Validate all user inputs before submission
- Provide immediate feedback on validation errors
- Use HTML5 validation attributes where appropriate

### Accessibility
- Use semantic HTML elements
- Include proper ARIA labels
- Ensure keyboard navigation works
- Provide alt text for images

## Common Patterns

### Protected Routes
```javascript
useEffect(() => {
  if (!isAuthenticated()) {
    navigate('/login');
  }
}, [navigate]);
```

### API Calls with Loading States
```javascript
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

async function fetchData() {
  setLoading(true);
  setError(null);
  try {
    const response = await fetchWithAuth(url);
    const data = await handleApiResponse(response);
    // Handle success
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
}
```

## Testing

(To be implemented)
- Unit tests for utility functions
- Integration tests for API calls
- Component tests with React Testing Library

## Future Improvements

- [ ] Add TypeScript for better type safety
- [ ] Implement comprehensive test suite
- [ ] Add form validation library (e.g., React Hook Form)
- [ ] Implement state management (Redux/Zustand) if needed
- [ ] Add internationalization (i18n)
- [ ] Implement dark mode
- [ ] Add progressive web app (PWA) features