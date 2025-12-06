import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function fetchWithAuth(url, opts = {}) {
  const access = localStorage.getItem("access");
  const refresh = localStorage.getItem("refresh");
  const headers = new Headers(opts.headers || {});
  if (access) headers.set("Authorization", `Bearer ${access}`);
  opts.headers = headers;
  let res = await fetch(url, opts);
  if (res.status === 401 && refresh) {
    // try refresh once
    const r = await fetch(`${API_BASE}/api/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (r.ok) {
      const d = await r.json();
      if (d.access) {
        localStorage.setItem("access", d.access);
        headers.set("Authorization", `Bearer ${d.access}`);
        opts.headers = headers;
        res = await fetch(url, opts);
      }
    }
  }
  return res;
}

export default function UploadPage() {
  const [files, setFiles] = useState([]);
  const [category, setCategory] = useState("attendance_sheet");
  const [loading, setLoading] = useState(false);
  const [responseJson, setResponseJson] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  function onFilesChange(e) {
    setFiles(Array.from(e.target.files || []));
  }

  async function onSubmit(e) {
    e.preventDefault();
    if (!files.length) return;
    setLoading(true);
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    fd.append("category", category);

    try {
      const res = await fetchWithAuth(`${API_BASE}/api/upload/files/`, {
        method: "POST",
        body: fd,
      });
      const data = await res.json();
      setResponseJson(data);
      if (res.ok && data && Array.isArray(data.created_document_ids) && data.created_document_ids.length > 0) {
        const firstId = data.created_document_ids[0];
        navigate(`/review/${firstId}`);
        return;
      }
    } catch (err) {
      setResponseJson({ error: "upload failed" });
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setFiles([]);
    }
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Upload documents</h2>

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Files</label>
          <input
            ref={fileInputRef}
            onChange={onFilesChange}
            type="file"
            name="files"
            multiple
            className="mt-1"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="mt-1 p-2 border rounded"
          >
            <option value="attendance_sheet">Attendance</option>
            <option value="student_records">Student Records</option>
            <option value="receipts">Receipts</option>
          </select>
        </div>

        <div>
          <button type="submit" disabled={loading} className="px-4 py-2 bg-indigo-600 text-white rounded">
            {loading ? "Uploading..." : "Upload"}
          </button>
        </div>
      </form>

      <div className="mt-6">
        {responseJson && (
          <div className="bg-gray-50 p-4 rounded">
            <pre className="text-xs">{JSON.stringify(responseJson, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

