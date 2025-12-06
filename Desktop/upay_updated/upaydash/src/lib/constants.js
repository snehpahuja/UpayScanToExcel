// API Configuration
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// File Upload Configuration
// IMPORTANT: These must match the backend's ALLOWED_FILE_TYPES setting
// Backend allowed types: ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
// If backend changes, update these constants accordingly
export const ALLOWED_FILE_TYPES = [
  'image/jpeg',
  'image/jpg',
  'image/png',
  'application/pdf'
];

export const ALLOWED_FILE_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png'];

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// Document Categories
export const DOCUMENT_CATEGORIES = {
  ATTENDANCE_SHEET: 'attendance_sheet',
  STUDENT_RECORDS: 'student_records',
  RECEIPTS: 'receipts'
};

export const DOCUMENT_CATEGORY_LABELS = {
  [DOCUMENT_CATEGORIES.ATTENDANCE_SHEET]: 'Attendance Sheet',
  [DOCUMENT_CATEGORIES.STUDENT_RECORDS]: 'Student Records',
  [DOCUMENT_CATEGORIES.RECEIPTS]: 'Receipts'
};

// Document Status
export const DOCUMENT_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  PROCESSED: 'processed',
  APPROVED: 'approved',
  ERROR: 'error',
  FAILED: 'failed'
};

// Validation Status
export const VALIDATION_STATUS = {
  PASSED: 'passed',
  FAILED: 'failed',
  PENDING: 'pending'
};

// Routes
export const ROUTES = {
  HOME: '/home',
  LOGIN: '/login',
  UPLOAD: '/upload',
  REVIEW: '/review/:id',
  BULK_REVIEW: '/bulk-review',
  DASHBOARD: '/dashboard',
  PROFILE: '/profile'
};