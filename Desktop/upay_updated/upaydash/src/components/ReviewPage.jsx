import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchWithAuth, handleApiResponse, isAuthenticated } from "../lib/auth";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

/**
 * ReviewPage
 * Fetches document data and renders a document preview with editable extracted fields.
 */
export default function ReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [doc, setDoc] = useState(null);
  const [fields, setFields] = useState([]);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
      return;
    }

    if (!id) {
      setError("No document ID provided");
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setMessage(null);
    setError(null);

    (async () => {
      try {
        const res = await fetchWithAuth(`${API_BASE}/api/documents/${id}/`);
        const data = await handleApiResponse(res);
        
        if (cancelled) return;
        
        setDoc(data);
        
        // Normalize extracted fields array
        const extracted = data.extracted_fields || data.extracted_data || data.extracted || [];
        setFields(extracted.map((f, i) => ({
          id: f.id ?? i,
          field_name: f.field_name ?? f.name ?? `field_${i}`,
          field_value: f.field_value ?? f.value ?? '',
          confidence_score: f.confidence_score ?? f.confidence ?? null,
          validation_status: f.validation_status ?? f.validation ?? 'passed'
        })));
      } catch (err) {
        console.error("Failed to load document:", err);
        if (!cancelled) {
          setError(err.message || 'Failed to load document');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => { cancelled = true; };
  }, [id, navigate]);

  function updateField(idx, key, value) {
    setFields(prev => {
      const copy = [...prev];
      copy[idx] = { ...copy[idx], [key]: value };
      return copy;
    });
  }

  async function saveDraft() {
    if (!doc) return;
    
    setMessage({ type: 'info', text: 'Saving...' });
    setError(null);

    try {
      const payload = { extracted_fields: fields };
      const res = await fetchWithAuth(`${API_BASE}/api/documents/${doc.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const result = await handleApiResponse(res);
      setMessage({ type: 'success', text: 'Draft saved successfully' });
      
      // Update local state with backend response
      if (result && (result.extracted_fields || result.extracted_data)) {
        const extracted = result.extracted_fields || result.extracted_data || [];
        setFields(extracted.map((f, i) => ({
          id: f.id ?? i,
          field_name: f.field_name ?? f.name ?? `field_${i}`,
          field_value: f.field_value ?? f.value ?? '',
          confidence_score: f.confidence_score ?? f.confidence ?? null,
          validation_status: f.validation_status ?? f.validation ?? 'passed'
        })));
      }
    } catch (err) {
      console.error("Save failed:", err);
      setError(err.message || 'Failed to save draft');
      setMessage(null);
    }
  }

  async function acceptAndFinalize() {
    if (!doc) return;
    
    setMessage({ type: 'info', text: 'Finalizing...' });
    setError(null);

    try {
      // Try dedicated finalize endpoint first
      let res;
      try {
        res = await fetchWithAuth(`${API_BASE}/api/documents/${doc.id}/finalize/`, {
          method: 'POST',
        });
      } catch (finalizeErr) {
        // Fallback: patch status to 'approved'
        res = await fetchWithAuth(`${API_BASE}/api/documents/${doc.id}/`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'approved' })
        });
      }

      await handleApiResponse(res);
      setMessage({ 
        type: 'success', 
        text: 'Document finalized successfully! Redirecting to document list...' 
      });
      
      // Navigate to bulk review list after brief delay to show success message
      setTimeout(() => {
        navigate('/bulk-review');
      }, 2000);
    } catch (err) {
      console.error("Finalize failed:", err);
      setError(err.message || 'Failed to finalize document');
      setMessage(null);
    }
  }

  function buildImageUrl(filePath) {
    if (!filePath) return null;
    
    // Construct proper URL
    const baseUrl = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;
    const path = filePath.startsWith('/') ? filePath : `/${filePath}`;
    return `${baseUrl}${path}`;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-indigo-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600">Loading document...</p>
        </div>
      </div>
    );
  }

  if (error && !doc) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md w-full text-center">
          <svg className="h-16 w-16 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Document Not Found</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/bulk-review')}
            className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Back to Document List
          </button>
        </div>
      </div>
    );
  }

  const failedFields = fields.filter(f => f.validation_status !== 'passed').length;
  const missingFields = fields.filter(f => !f.field_value || f.field_value.trim() === '').length;

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-3">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/bulk-review')}
                className="flex items-center gap-2 text-sm text-gray-600 hover:text-indigo-600"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 17l-5-5m0 0l5-5m-5 5h12" />
                </svg>
                Back to List
              </button>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Document {doc?.id}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4 sm:p-6 lg:p-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Document Preview Pane */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-lg font-semibold">Original Document</h3>
              <p className="text-sm text-gray-500">{doc?.original_filename || 'Untitled'}</p>
            </div>
          </div>

          <div className="bg-gray-100 rounded-lg border flex items-center justify-center min-h-[70vh]">
            {doc?.file_path ? (
              <img
                src={buildImageUrl(doc.file_path)}
                alt={`Preview of ${doc.original_filename}`}
                className="w-full h-full object-contain rounded-lg"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = "https://placehold.co/600x850/e2e8f0/475569?text=Preview+Unavailable";
                }}
              />
            ) : (
              <div className="text-center text-gray-500">
                <svg className="h-24 w-24 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>No preview available</p>
              </div>
            )}
          </div>
        </div>

        {/* Data Extraction Pane */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Extracted Data</h3>
          <div className="flex gap-4 mb-4 text-sm">
            {failedFields > 0 && (
              <span className="text-red-600">
                {failedFields} field{failedFields !== 1 ? 's' : ''} need attention
              </span>
            )}
            {missingFields > 0 && (
              <span className="text-yellow-600">
                {missingFields} missing field{missingFields !== 1 ? 's' : ''}
              </span>
            )}
            {failedFields === 0 && missingFields === 0 && (
              <span className="text-green-600">All fields validated</span>
            )}
          </div>

          <div className="space-y-4 max-h-[65vh] overflow-y-auto">
            {fields.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <p>No extracted fields available</p>
              </div>
            ) : (
              fields.map((f, idx) => (
                <div
                  key={f.id}
                  className={`grid grid-cols-3 gap-4 items-center p-3 rounded-md ${
                    f.validation_status !== 'passed'
                      ? 'bg-red-50 ring-1 ring-red-200'
                      : !f.field_value
                      ? 'bg-yellow-50 ring-1 ring-yellow-200'
                      : ''
                  }`}
                >
                  <label
                    htmlFor={`field-${idx}`}
                    className={`text-sm font-medium ${
                      f.validation_status !== 'passed'
                        ? 'text-red-700'
                        : !f.field_value
                        ? 'text-yellow-700'
                        : 'text-gray-700'
                    }`}
                  >
                    {f.field_name}
                  </label>
                  <input
                    id={`field-${idx}`}
                    type="text"
                    value={f.field_value}
                    onChange={(e) => updateField(idx, 'field_value', e.target.value)}
                    className={`col-span-2 p-2 border rounded-md focus:ring-2 focus:outline-none ${
                      f.validation_status !== 'passed'
                        ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                        : !f.field_value
                        ? 'border-yellow-300 focus:ring-yellow-500 focus:border-yellow-500'
                        : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
                    }`}
                  />
                </div>
              ))
            )}
          </div>
        </div>
      </main>

      {/* Action Footer */}
      <footer className="bg-white shadow-inner sticky bottom-0 border-t">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex-1">
              {message && (
                <div
                  className={`text-sm px-4 py-2 rounded inline-block ${
                    message.type === 'success'
                      ? 'bg-green-50 text-green-700'
                      : message.type === 'error'
                      ? 'bg-red-50 text-red-700'
                      : 'bg-blue-50 text-blue-700'
                  }`}
                >
                  {message.text}
                </div>
              )}
              {error && (
                <div className="text-sm px-4 py-2 rounded inline-block bg-red-50 text-red-700">
                  {error}
                </div>
              )}
            </div>
            <div className="flex space-x-4">
              <button
                onClick={saveDraft}
                className="px-6 py-2 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors"
              >
                Save Draft
              </button>
              <button
                onClick={acceptAndFinalize}
                className="px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
              >
                Accept & Finalize
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}