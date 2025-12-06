/**
 * Utility functions for the application
 */

import { ALLOWED_FILE_TYPES, ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE } from './constants';

/**
 * Validate a single file for upload
 * @param {File} file - File to validate
 * @returns {Object} Validation result with isValid and error message
 */
export function validateFile(file) {
  // Check file type
  if (!ALLOWED_FILE_TYPES.includes(file.type)) {
    return {
      isValid: false,
      error: `Invalid file type. Allowed types: PDF, JPG, JPEG, PNG`
    };
  }
  
  // Check file extension as fallback
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
  if (!ALLOWED_FILE_EXTENSIONS.includes(fileExtension)) {
    return {
      isValid: false,
      error: `Invalid file extension. Allowed extensions: ${ALLOWED_FILE_EXTENSIONS.join(', ')}`
    };
  }
  
  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    return {
      isValid: false,
      error: `File too large. Maximum size is ${formatFileSize(MAX_FILE_SIZE)}`
    };
  }
  
  return { isValid: true, error: null };
}

/**
 * Validate multiple files for upload
 * @param {FileList|File[]} files - Files to validate
 * @returns {Object} Validation result with isValid, validFiles, and errors array
 */
export function validateFiles(files) {
  const fileArray = Array.from(files);
  const errors = [];
  const validFiles = [];
  
  fileArray.forEach(file => {
    const validation = validateFile(file);
    if (validation.isValid) {
      validFiles.push(file);
    } else {
      errors.push(`${file.name}: ${validation.error}`);
    }
  });
  
  return {
    isValid: errors.length === 0,
    validFiles,
    errors
  };
}

/**
 * Format file size in bytes to human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format date to localized string
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date
 */
export function formatDate(date) {
  if (!date) return '—';
  
  try {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return '—';
  }
}

/**
 * Format date and time to localized string
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date and time
 */
export function formatDateTime(date) {
  if (!date) return '—';
  
  try {
    return new Date(date).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return '—';
  }
}

/**
 * Build proper image URL from file path
 * @param {string} filePath - File path from API
 * @param {string} baseUrl - Base API URL
 * @returns {string|null} Complete image URL
 */
export function buildImageUrl(filePath, baseUrl) {
  if (!filePath) return null;
  
  const base = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  const path = filePath.startsWith('/') ? filePath : `/${filePath}`;
  
  return `${base}${path}`;
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email
 */
export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Debounce function to limit execution rate
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Get status color class for Tailwind
 * @param {string} status - Document status
 * @returns {string} Tailwind color classes
 */
export function getStatusColor(status) {
  switch (status?.toLowerCase()) {
    case 'processed':
    case 'approved':
      return 'bg-green-100 text-green-800';
    case 'error':
    case 'failed':
      return 'bg-red-100 text-red-800';
    case 'pending':
    case 'processing':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength = 50) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Capitalize first letter of string
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Convert snake_case to Title Case
 * @param {string} str - Snake case string
 * @returns {string} Title case string
 */
export function snakeToTitle(str) {
  if (!str) return '';
  return str
    .split('_')
    .map(word => capitalize(word))
    .join(' ');
}