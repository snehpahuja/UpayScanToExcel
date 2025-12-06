import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchWithAuth, handleApiResponse, isAuthenticated } from "../lib/auth";
import { ALLOWED_FILE_TYPES, ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE } from "../lib/constants";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function UploadPage() {
  const [files, setFiles] = useState([]);
  const [category, setCategory] = useState("attendance_sheet");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    }
  }, [navigate]);

  function validateFiles(fileList) {
    const errors = [];
    
    for (const file of fileList) {
      // Check file type
      if (!ALLOWED_FILE_TYPES.includes(file.type)) {
        errors.push(`${file.name}: Invalid file type. Allowed types: PDF, JPG, JPEG, PNG`);
      }
      
      // Also check file extension as a fallback
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      if (!ALLOWED_FILE_EXTENSIONS.includes(fileExtension)) {
        errors.push(`${file.name}: Invalid file extension. Allowed extensions: ${ALLOWED_FILE_EXTENSIONS.join(', ')}`);
      }
      
      // Check file size
      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name}: File too large. Maximum size is 10MB`);
      }
    }
    
    return errors;
  }

  function onFilesChange(e) {
    const selectedFiles = Array.from(e.target.files || []);
    const validationErrors = validateFiles(selectedFiles);
    
    if (validationErrors.length > 0) {
      setError(validationErrors.join('\n'));
      setFiles([]);
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }
    
    setError(null);
    setFiles(selectedFiles);
  }

  async function onSubmit(e) {
    e.preventDefault();
    
    if (!files.length) {
      setError("Please select at least one file to upload");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    fd.append("category", category);

    try {
      const res = await fetchWithAuth(`${API_BASE}/api/upload/files/`, {
        method: "POST",
        body: fd,
      });

      const data = await handleApiResponse(res);
      
      if (data && Array.isArray(data.created_document_ids) && data.created_document_ids.length > 0) {
        setSuccess(`Successfully uploaded ${data.created_document_ids.length} document(s)`);
        const firstId = data.created_document_ids[0];
        
        // Navigate after a brief delay to show success message
        setTimeout(() => {
          navigate(`/review/${firstId}`);
        }, 1000);
      } else {
        setError("Upload completed but no documents were created");
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || "Upload failed. Please try again.");
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setFiles([]);
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate('/home')}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-indigo-600"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 17l-5-5m0 0l5-5m-5 5h12" />
            </svg>
            Back to Home
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-6">Upload Documents</h2>

          <form onSubmit={onSubmit} className="space-y-6">
            <div>
              <label htmlFor="files" className="block text-sm font-medium text-gray-700 mb-2">
                Select Files
              </label>
              <input
                id="files"
                ref={fileInputRef}
                onChange={onFilesChange}
                type="file"
                name="files"
                multiple
                accept=".pdf,.jpg,.jpeg,.png"
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                disabled={loading}
              />
              <p className="mt-2 text-xs text-gray-500">
                Accepted formats: PDF, JPG, JPEG, PNG (max 10MB per file)
              </p>
              <p className="mt-1 text-xs text-amber-600">
                Note: Only PDF, JPG, JPEG, and PNG files are supported by the backend
              </p>
              {files.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-gray-700">Selected files:</p>
                  <ul className="mt-1 text-sm text-gray-600">
                    {files.map((file, idx) => (
                      <li key={idx}>• {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                Document Category
              </label>
              <select
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={loading}
              >
                <option value="attendance_sheet">Attendance Sheet</option>
                <option value="student_records">Student Records</option>
                <option value="receipts">Receipts</option>
              </select>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded whitespace-pre-line" role="alert">
                <strong className="font-bold">Error: </strong>
                <span className="block sm:inline">{error}</span>
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded" role="alert">
                <strong className="font-bold">Success! </strong>
                <span className="block sm:inline">{success}</span>
              </div>
            )}

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading || files.length === 0}
                className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Uploading...
                  </span>
                ) : (
                  "Upload Documents"
                )}
              </button>
              
              <button
                type="button"
                onClick={() => navigate('/home')}
                disabled={loading}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}