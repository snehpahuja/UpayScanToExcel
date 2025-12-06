import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function BulkReviewList() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/documents/`)
      .then((r) => r.json())
      .then((data) => {
        if (data.results) setDocs(data.results);
        else setDocs([]);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="bg-gray-100 min-h-screen flex">
      <div className="w-64 bg-white shadow-md">
        <div className="p-6 flex items-center">
          <svg
            className="h-8 w-auto text-indigo-600"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 18.375a6.375 6.375 0 006.375-6.375V9.75A6.375 6.375 0 0012 3.375zM12 18.375A6.375 6.375 0 015.625 12V9.75a6.375 6.375 0 016.375-6.375zM12 18.375v-6.375"
            />
          </svg>
          <h1 className="ml-3 text-xl font-bold text-gray-800">UPAY</h1>
        </div>

        <nav className="mt-6">
          <Link
            to="/home"
            className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100"
          >
            Home
          </Link>

          <Link
            to="/upload"
            className="flex items-center px-6 py-3 bg-gray-200 text-gray-800 font-semibold"
          >
            Upload
          </Link>

          <Link
            to="/dashboard"
            className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100"
          >
            Dashboard
          </Link>

          <Link
            to="/profile"
            className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100"
          >
            Profile
          </Link>
        </nav>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm p-4 flex justify-between items-center">
          <h2 className="text-2xl font-semibold text-gray-800">
            Review Uploaded Documents
          </h2>
        </header>

        <main className="flex-1 overflow-y-auto bg-gray-100 p-6">
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Stage
                  </th>
                  <th className="px-6 py-3"></th>
                </tr>
              </thead>

              <tbody className="bg-white divide-y divide-gray-200">
                {docs.map((doc) => (
                  <tr key={doc.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {doc.original_filename}
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doc.category || "—"}
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={
                          "px-2 inline-flex text-xs leading-5 font-semibold rounded-full " +
                          (doc.status === "processed"
                            ? "bg-green-100 text-green-800"
                            : doc.status === "error"
                            ? "bg-red-100 text-red-800"
                            : "bg-yellow-100 text-yellow-800")
                        }
                      >
                        {doc.status}
                      </span>
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <Link
                        to={`/review/${doc.id}`}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        Review
                      </Link>
                    </td>
                  </tr>
                ))}

                {docs.length === 0 && (
                  <tr>
                    <td colSpan="4" className="px-6 py-4 text-gray-500">
                      No documents found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </div>
  );
}

