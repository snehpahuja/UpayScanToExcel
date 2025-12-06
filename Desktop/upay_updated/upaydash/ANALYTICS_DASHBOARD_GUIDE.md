# Analytics Dashboard Integration Guide

## Overview

The Dashboard has been completely redesigned to render **charts and graphs** based on the analytics data from `api/analytics.py`. It now displays comprehensive visual analytics instead of just document lists.

## What's Displayed

### 📊 Key Metrics Cards (Top Row)
1. **Attendance Rate** - Overall attendance percentage with present/total counts
2. **Budget Utilization** - Percentage of budget spent with amounts
3. **Documents Processed** - Total documents with completion count
4. **Students Flagged** - Number of students needing attention

### 📈 Charts and Visualizations

#### 1. Attendance Trend (Line Chart)
- **Data Source**: `StudentPerformanceAnalytics.get_attendance_trend()`
- **Endpoint**: `GET /api/analytics/attendance/trend/`
- **Shows**: 6-month attendance rate trend
- **X-Axis**: Month (YYYY-MM format)
- **Y-Axis**: Attendance Rate (%)

#### 2. Grade Distribution (Pie Chart)
- **Data Source**: `StudentPerformanceAnalytics.get_grade_distribution()`
- **Endpoint**: `GET /api/analytics/grades/distribution/`
- **Shows**: Distribution across 5 grade ranges
  - Excellent (90-100) - Green
  - Good (75-89) - Blue
  - Average (60-74) - Yellow
  - Below Average (40-59) - Red
  - Poor (0-39) - Gray

#### 3. Enrollment Growth (Dual-Line Chart)
- **Data Source**: `EnrollmentAnalytics.get_enrollment_growth()`
- **Endpoint**: `GET /api/analytics/enrollment/growth/`
- **Shows**: 
  - New students per month (left Y-axis)
  - Cumulative total students (right Y-axis)

#### 4. Monthly Expenditure Trend (Bar Chart)
- **Data Source**: `FinancialAnalytics.get_expenditure_trend()`
- **Endpoint**: `GET /api/analytics/financial/expenditure-trend/`
- **Shows**: Monthly spending over 12 months
- **X-Axis**: Month
- **Y-Axis**: Expenditure amount ($)

#### 5. Flagged Students Table
- **Data Source**: `StudentFlaggingAnalytics.flag_low_attendance_students()`
- **Endpoint**: `GET /api/analytics/flagging/low-attendance/`
- **Shows**: Students with attendance below threshold
- **Columns**: Student ID, Name, Center, Attendance Rate, Reason, Severity

## Required Backend Endpoints

### Analytics API Structure

Create these endpoints in your Django backend (`api/views.py`):

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .analytics import (
    StudentPerformanceAnalytics,
    StudentFlaggingAnalytics,
    EnrollmentAnalytics,
    FinancialAnalytics,
    DocumentProcessingAnalytics
)

# Attendance Analytics
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_statistics(request):
    center_id = request.query_params.get('center_id')
    data = StudentPerformanceAnalytics.get_attendance_statistics(center_id=center_id)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_trend(request):
    center_id = request.query_params.get('center_id')
    data = StudentPerformanceAnalytics.get_attendance_trend(center_id=center_id, months=6)
    return Response(data)

# Grade Analytics
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def grade_distribution(request):
    center_id = request.query_params.get('center_id')
    data = StudentPerformanceAnalytics.get_grade_distribution(center_id=center_id)
    return Response(data)

# Enrollment Analytics
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def enrollment_growth(request):
    center_id = request.query_params.get('center_id')
    data = EnrollmentAnalytics.get_enrollment_growth(center_id=center_id, months=12)
    return Response(data)

# Financial Analytics
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_utilization(request):
    center_id = request.query_params.get('center_id')
    data = FinancialAnalytics.get_budget_utilization(center_id=center_id)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expenditure_trend(request):
    center_id = request.query_params.get('center_id')
    data = FinancialAnalytics.get_expenditure_trend(center_id=center_id, months=12)
    return Response(data)

# Document Analytics
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def document_summary(request):
    user_id = request.user.id if not request.user.is_staff else None
    data = DocumentProcessingAnalytics.get_processing_summary(user_id=user_id)
    return Response(data)

# Student Flagging
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def flagged_students(request):
    center_id = request.query_params.get('center_id')
    data = StudentFlaggingAnalytics.flag_low_attendance_students(
        threshold=75,
        days=30,
        center_id=center_id
    )
    return Response(data)
```

### URL Configuration (`api/urls.py`)

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... existing patterns ...
    
    # Analytics endpoints
    path('analytics/attendance/statistics/', views.attendance_statistics),
    path('analytics/attendance/trend/', views.attendance_trend),
    path('analytics/grades/distribution/', views.grade_distribution),
    path('analytics/enrollment/growth/', views.enrollment_growth),
    path('analytics/financial/budget-utilization/', views.budget_utilization),
    path('analytics/financial/expenditure-trend/', views.expenditure_trend),
    path('analytics/documents/summary/', views.document_summary),
    path('analytics/flagging/low-attendance/', views.flagged_students),
]
```

## Frontend Features

### 1. **Automatic Data Fetching**
- Fetches all analytics on page load
- Uses `Promise.allSettled()` to handle partial failures
- Shows available data even if some endpoints fail

### 2. **Graceful Degradation**
- If an endpoint is unavailable, that chart is simply not displayed
- Shows informative message if no data is available
- No crashes or errors, just missing sections

### 3. **Refresh Functionality**
- "Refresh" button in header to reload all analytics
- Useful for seeing updated data after changes

### 4. **Responsive Design**
- Charts adapt to screen size using ResponsiveContainer
- Grid layout adjusts for mobile, tablet, desktop
- Scrollable content area

### 5. **Visual Design**
- Color-coded metrics (green=good, red=needs attention)
- Professional chart styling with Recharts
- Consistent color palette across all visualizations

## Data Flow

```
User Opens Dashboard
    ↓
Frontend fetches from 8 endpoints in parallel
    ↓
Each endpoint returns analytics data
    ↓
Data is transformed for chart format
    ↓
Charts render with Recharts library
    ↓
User sees visual analytics
```

## Testing the Dashboard

### 1. Without Backend (Development)
```bash
cd upaydash
npm run dev
```
- Navigate to `/dashboard`
- Will show "Analytics Dashboard Ready" message
- No errors, graceful handling

### 2. With Backend
```bash
# Terminal 1: Start Django
cd upaydash
python manage.py runserver

# Terminal 2: Start React
cd upaydash
npm run dev
```
- Navigate to `/dashboard`
- Should see all charts populated with real data

### 3. Test Individual Endpoints
```bash
# Get attendance stats
curl -X GET http://localhost:8000/api/analytics/attendance/statistics/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected response:
{
  "total_records": 1500,
  "present_count": 1200,
  "absent_count": 250,
  "excused_count": 50,
  "attendance_rate": 80.0,
  "period": "All time"
}
```

## Charting Library: Recharts

### Why Recharts?
- **React-native**: Built specifically for React
- **Responsive**: Auto-adjusts to container size
- **Composable**: Easy to customize and extend
- **Well-documented**: Great documentation and examples
- **Lightweight**: Smaller bundle size than alternatives

### Charts Used:
1. **LineChart** - For trends over time (attendance, enrollment)
2. **BarChart** - For comparing values (expenditure)
3. **PieChart** - For distributions (grades)

### Customization:
All charts use a consistent color palette defined in the component:
```javascript
const COLORS = {
  primary: '#4F46E5',   // Indigo
  success: '#10B981',   // Green
  warning: '#F59E0B',   // Yellow
  danger: '#EF4444',    // Red
  info: '#3B82F6'       // Blue
};
```

## Future Enhancements

### Potential Additions:
1. **Date Range Filters** - Allow users to select custom date ranges
2. **Center Selection** - Filter analytics by specific center
3. **Export Functionality** - Download charts as images or PDF
4. **Real-time Updates** - WebSocket integration for live data
5. **Drill-down Views** - Click on chart elements for detailed views
6. **Comparison Mode** - Compare multiple centers side-by-side
7. **Predictive Analytics** - Forecast future trends
8. **Custom Dashboards** - Let users configure their own views

### Additional Charts:
- **Activity Summary** (from `CenterActivityAnalytics`)
- **Store Requisition vs Received** (from `StoreRequisitionAnalytics`)
- **Visitor Trends** (from `VisitorAnalytics`)
- **Student Performance Details** (detailed drill-down)

## Troubleshooting

### Issue: Charts not displaying
**Solution**: Check browser console for API errors. Verify endpoints are accessible.

### Issue: "Analytics Dashboard Ready" message
**Solution**: Backend endpoints not implemented yet. This is expected behavior.

### Issue: Some charts missing
**Solution**: Normal - only charts with available data are displayed.

### Issue: Data looks incorrect
**Solution**: Verify database has sample data. Check analytics.py logic.

## Summary

The Dashboard is now a **full-featured analytics visualization tool** that:
- ✅ Displays charts and graphs (not document lists)
- ✅ Uses data from `analytics.py` classes
- ✅ Handles missing endpoints gracefully
- ✅ Provides actionable insights
- ✅ Is production-ready for integration

The frontend is complete and waiting for backend analytics endpoints!