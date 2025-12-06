from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Authentication & User Management
    SignupView,
    LoginView,
    UserViewSet,
    UserProfileView,
    
    # Center Management
    CenterViewSet,
    
    # Document Management
    DocumentViewSet,
    DocumentUploadView,
    DocumentCategorizationView,
    BulkDocumentUploadView,
    
    # Document Review
    DocumentReviewViewSet,
    DocumentHighlightsView,
    UpdateExtractedFieldView,
    DocumentFinalizeView,
    DocumentPreviewView,
    ReviewProgressView,
    
    # Processing & Queue
    ProcessingQueueViewSet,
    ProcessingStatusView,
    
    # Data Export
    ExcelDownloadView,
    
    # Analytics Dashboard Endpoints
    AttendanceDashboardView,
    GradesDashboardView,
    AutomatedFlaggingView,
    EnrollmentDashboardView,
    CenterActivityDashboardView,
    FinancialDashboardView,
    RequisitionDashboardView,
    VisitorDashboardView,
    ConsolidatedVisitorView,
    
    # Student Management
    StudentViewSet,
    AttendanceViewSet,
    GradeViewSet,
    
    # Store Management
    StoreItemViewSet,
    StoreRequisitionViewSet,
    StoreReceivementViewSet,
    
    # Visitor Management
    VisitorViewSet,
    
    # Activity & Financial
    ActivityViewSet,
    FinancialViewSet,
    
    # Admin Functions
    AdminUserManagementViewSet,
    ActivityLogViewSet,
    UserPermissionsViewSet,
)

# -----------------------------
# Router for all ViewSets
# -----------------------------
router = DefaultRouter()

# User & Authentication
router.register(r'users', UserViewSet, basename='user')

# Centers
router.register(r'centers', CenterViewSet, basename='center')

# Documents
router.register(r'documents', DocumentViewSet, basename='document')

# Document Review
router.register(r'review', DocumentReviewViewSet, basename='review')

# Processing Queue
router.register(r'processing-queue', ProcessingQueueViewSet, basename='processing-queue')

# Students
router.register(r'students', StudentViewSet, basename='student')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'grades', GradeViewSet, basename='grade')

# Store Management
router.register(r'store/items', StoreItemViewSet, basename='store-item')
router.register(r'store/requisitions', StoreRequisitionViewSet, basename='store-requisition')
router.register(r'store/receivements', StoreReceivementViewSet, basename='store-receivement')

# Visitors
router.register(r'visitors', VisitorViewSet, basename='visitor')

# Activity & Financial
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'financials', FinancialViewSet, basename='financial')

# Admin
router.register(r'admin/users', AdminUserManagementViewSet, basename='admin-user')
router.register(r'admin/activity-logs', ActivityLogViewSet, basename='activity-log')
router.register(r'admin/permissions', UserPermissionsViewSet, basename='user-permissions')


# -----------------------------
# URL patterns
# -----------------------------
urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    
    # ===== Authentication & User Management =====
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # ===== Document Upload =====
    path('upload/files/', DocumentUploadView.as_view(), name='upload-files'),
    path('upload/bulk/', BulkDocumentUploadView.as_view(), name='upload-bulk'),
    path('upload/categorize/', DocumentCategorizationView.as_view(), name='upload-categorize'),
    
    # ===== Document Review =====
    path('review/document/<int:document_id>/', DocumentReviewViewSet.as_view({'get': 'retrieve'}), name='review-document'),
    path('review/document/<int:document_id>/highlights/', DocumentHighlightsView.as_view(), name='review-highlights'),
    path('review/document/<int:document_id>/update-field/', UpdateExtractedFieldView.as_view(), name='review-update-field'),
    path('review/document/<int:document_id>/finalize/', DocumentFinalizeView.as_view(), name='review-finalize'),
    path('review/document/<int:document_id>/preview/', DocumentPreviewView.as_view(), name='review-preview'),
    path('review/progress/', ReviewProgressView.as_view(), name='review-progress'),
    
    # ===== Processing & Status =====
    path('processing/status/', ProcessingStatusView.as_view(), name='processing-status'),
    
    # ===== Data Export =====
    path('download/excel/', ExcelDownloadView.as_view(), name='download-excel'),
    
    # ===== Dashboard Analytics =====
    path('dashboard/attendance/', AttendanceDashboardView.as_view(), name='dashboard-attendance'),
    path('dashboard/grades/', GradesDashboardView.as_view(), name='dashboard-grades'),
    path('dashboard/flags/', AutomatedFlaggingView.as_view(), name='dashboard-flags'),
    path('dashboard/enrollment/', EnrollmentDashboardView.as_view(), name='dashboard-enrollment'),
    path('dashboard/center-activity/', CenterActivityDashboardView.as_view(), name='dashboard-center-activity'),
    path('dashboard/finance/', FinancialDashboardView.as_view(), name='dashboard-finance'),
    path('dashboard/requisitions/', RequisitionDashboardView.as_view(), name='dashboard-requisitions'),
    path('dashboard/visitors/', VisitorDashboardView.as_view(), name='dashboard-visitors'),
    
    # ===== Consolidated Views =====
    path('visitors/all/', ConsolidatedVisitorView.as_view(), name='visitors-all'),
]

# Optional: Add app name for namespacing
app_name = 'api'
