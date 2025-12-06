import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { clearTokens, isAuthenticated, fetchWithAuth, handleApiResponse } from '../lib/auth';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// Color palette for charts
const COLORS = {
  primary: '#4F46E5',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#3B82F6',
  purple: '#8B5CF6',
  pink: '#EC4899',
  teal: '#14B8A6'
};

const PIE_COLORS = [COLORS.primary, COLORS.success, COLORS.warning, COLORS.danger, COLORS.info];

export default function DashboardPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCenter, setSelectedCenter] = useState(null);
  
  // Analytics data states
  const [attendanceStats, setAttendanceStats] = useState(null);
  const [attendanceTrend, setAttendanceTrend] = useState([]);
  const [gradeDistribution, setGradeDistribution] = useState(null);
  const [enrollmentGrowth, setEnrollmentGrowth] = useState([]);
  const [financialData, setFinancialData] = useState(null);
  const [expenditureTrend, setExpenditureTrend] = useState([]);
  const [documentStats, setDocumentStats] = useState(null);
  const [flaggedStudents, setFlaggedStudents] = useState([]);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
      return;
    }
    fetchAllAnalytics();
  }, [navigate, selectedCenter]);

  async function fetchAllAnalytics() {
    setLoading(true);
    setError(null);

    try {
      const centerParam = selectedCenter ? `?center_id=${selectedCenter}` : '';
      
      // Fetch all analytics endpoints
      const endpoints = [
        { key: 'attendance', url: `/api/analytics/attendance/statistics/${centerParam}` },
        { key: 'attendanceTrend', url: `/api/analytics/attendance/trend/${centerParam}` },
        { key: 'gradeDistribution', url: `/api/analytics/grades/distribution/${centerParam}` },
        { key: 'enrollmentGrowth', url: `/api/analytics/enrollment/growth/${centerParam}` },
        { key: 'financial', url: `/api/analytics/financial/budget-utilization/${centerParam}` },
        { key: 'expenditureTrend', url: `/api/analytics/financial/expenditure-trend/${centerParam}` },
        { key: 'documentStats', url: `/api/analytics/documents/summary/${centerParam}` },
        { key: 'flaggedStudents', url: `/api/analytics/flagging/low-attendance/${centerParam}` }
      ];

      const results = await Promise.allSettled(
        endpoints.map(async ({ key, url }) => {
          try {
            const res = await fetchWithAuth(`${API_BASE}${url}`);
            const data = await handleApiResponse(res);
            return { key, data };
          } catch (err) {
            console.log(`${key} endpoint not available:`, err.message);
            return { key, data: null };
          }
        })
      );

      // Process results
      results.forEach(result => {
        if (result.status === 'fulfilled' && result.value.data) {
          const { key, data } = result.value;
          switch (key) {
            case 'attendance':
              setAttendanceStats(data);
              break;
            case 'attendanceTrend':
              setAttendanceTrend(data);
              break;
            case 'gradeDistribution':
              setGradeDistribution(data);
              break;
            case 'enrollmentGrowth':
              setEnrollmentGrowth(data);
              break;
            case 'financial':
              setFinancialData(data);
              break;
            case 'expenditureTrend':
              setExpenditureTrend(data);
              break;
            case 'documentStats':
              setDocumentStats(data);
              break;
            case 'flaggedStudents':
              setFlaggedStudents(data);
              break;
          }
        }
      });

    } catch (err) {
      console.error('Analytics fetch error:', err);
      setError('Some analytics data could not be loaded. Displaying available data.');
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    clearTokens();
    navigate('/login');
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-indigo-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600">Loading analytics dashboard...</p>
        </div>
      </div>
    );
  }

  // Transform grade distribution for pie chart
  const gradeChartData = gradeDistribution ? [
    { name: 'Excellent (90-100)', value: gradeDistribution.excellent, color: COLORS.success },
    { name: 'Good (75-89)', value: gradeDistribution.good, color: COLORS.info },
    { name: 'Average (60-74)', value: gradeDistribution.average, color: COLORS.warning },
    { name: 'Below Average (40-59)', value: gradeDistribution.below_average, color: COLORS.danger },
    { name: 'Poor (0-39)', value: gradeDistribution.poor, color: '#6B7280' }
  ].filter(item => item.value > 0) : [];

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-64 bg-white shadow-md relative flex-shrink-0">
          <div className="p-6">
            <div className="flex items-center">
              <svg className="h-8 w-auto text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.375a6.375 6.375 0 006.375-6.375V9.75A6.375 6.375 0 0012 3.375zM12 18.375A6.375 6.375 0 015.625 12V9.75a6.375 6.375 0 016.375-6.375zM12 18.375v-6.375" />
              </svg>
              <h1 className="ml-3 text-xl font-bold text-gray-800">UPAY</h1>
            </div>
          </div>

          <nav className="mt-6">
            <a href="/home" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span className="ml-3">Home</span>
            </a>

            <a href="/upload" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <span className="ml-3">Upload</span>
            </a>

            <a href="/bulk-review" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="ml-3">Review</span>
            </a>

            <a href="/dashboard" className="flex items-center px-6 py-3 bg-gray-200 text-gray-800 font-semibold">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span className="ml-3">Dashboard</span>
            </a>

            <a href="/profile" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100">
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span className="ml-3">Profile</span>
            </a>
          </nav>

          <div className="absolute bottom-0 w-64">
            <button
              onClick={handleLogout}
              className="flex items-center px-6 py-4 text-gray-600 hover:bg-gray-100 w-full text-left"
            >
              <svg className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span className="ml-3">Logout</span>
            </button>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="bg-white shadow-sm p-4">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-gray-800">Analytics Dashboard</h2>
              <button
                onClick={fetchAllAnalytics}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm flex items-center gap-2"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
            </div>
          </header>

          <main className="flex-1 overflow-y-auto bg-gray-100 p-6">
            {error && (
              <div className="mb-6 bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded" role="alert">
                <strong className="font-bold">Note: </strong>
                <span className="block sm:inline">{error}</span>
              </div>
            )}

            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {/* Attendance Rate */}
              {attendanceStats && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Attendance Rate</p>
                      <p className="text-3xl font-bold text-green-600 mt-2">
                        {attendanceStats.attendance_rate}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {attendanceStats.present_count}/{attendanceStats.total_records} present
                      </p>
                    </div>
                    <div className="bg-green-100 rounded-full p-3">
                      <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  </div>
                </div>
              )}

              {/* Budget Utilization */}
              {financialData && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Budget Utilization</p>
                      <p className="text-3xl font-bold text-indigo-600 mt-2">
                        {financialData.utilization_rate}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        ${financialData.total_expenditure.toLocaleString()} / ${financialData.total_budget.toLocaleString()}
                      </p>
                    </div>
                    <div className="bg-indigo-100 rounded-full p-3">
                      <svg className="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  </div>
                </div>
              )}

              {/* Documents Processed */}
              {documentStats && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Documents Processed</p>
                      <p className="text-3xl font-bold text-blue-600 mt-2">
                        {documentStats.total_documents || 0}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {documentStats.by_status?.processed || 0} completed
                      </p>
                    </div>
                    <div className="bg-blue-100 rounded-full p-3">
                      <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                  </div>
                </div>
              )}

              {/* Flagged Students */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Students Flagged</p>
                    <p className="text-3xl font-bold text-red-600 mt-2">
                      {flaggedStudents.length}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Need attention
                    </p>
                  </div>
                  <div className="bg-red-100 rounded-full p-3">
                    <svg className="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Attendance Trend */}
              {attendanceTrend.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Attendance Trend (6 Months)</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={attendanceTrend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="attendance_rate" stroke={COLORS.success} strokeWidth={2} name="Attendance Rate %" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Grade Distribution */}
              {gradeChartData.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Grade Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={gradeChartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {gradeChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Enrollment Growth */}
              {enrollmentGrowth.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Enrollment Growth</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={enrollmentGrowth}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Line yAxisId="left" type="monotone" dataKey="new_students" stroke={COLORS.primary} strokeWidth={2} name="New Students" />
                      <Line yAxisId="right" type="monotone" dataKey="cumulative_students" stroke={COLORS.success} strokeWidth={2} name="Total Students" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Expenditure Trend */}
              {expenditureTrend.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Monthly Expenditure Trend</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={expenditureTrend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="expenditure" fill={COLORS.warning} name="Expenditure ($)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Flagged Students Table */}
            {flaggedStudents.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Students Requiring Attention</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Center</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attendance Rate</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {flaggedStudents.slice(0, 10).map((student, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{student.student_id}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{student.student_name}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{student.center_name}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{student.attendance_rate}%</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{student.reason}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              student.severity === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {student.severity}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* No Data Message */}
            {!attendanceStats && !financialData && !documentStats && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                <svg className="h-12 w-12 text-blue-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <h3 className="text-lg font-medium text-blue-800 mb-2">Analytics Dashboard Ready</h3>
                <p className="text-sm text-blue-700">
                  Connect the backend analytics endpoints to view comprehensive charts and insights.
                  The dashboard will display attendance trends, grade distributions, enrollment growth,
                  financial analytics, and student performance metrics.
                </p>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}