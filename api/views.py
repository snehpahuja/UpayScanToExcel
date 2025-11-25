from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpResponse
from .excel_generator import ExcelGenerator


import uuid
from .ocr.mock_processor import MockOCRProcessor

from .models import (
    Center, Document, ProcessingQueue, ExtractedData,
    Category, UserPermissions, ActivityLog, Student,
    Attendance, Grade, StoreItem, StoreRequisition,
    StoreReceivement, Visitor, Activity, Financial, Session
)
from .serializers import (
    UserSerializer, UserSignupSerializer, CustomTokenObtainPairSerializer,
    SessionSerializer, CenterSerializer, CategorySerializer,
    DocumentListSerializer, DocumentDetailSerializer, DocumentUploadSerializer,
    DocumentWithExtractedDataSerializer, ProcessingQueueSerializer,
    ExtractedDataSerializer, ExtractedDataUpdateSerializer,
    UserPermissionsSerializer, ActivityLogSerializer,
    StudentSerializer, AttendanceSerializer, GradeSerializer,
    StoreItemSerializer, StoreRequisitionSerializer, StoreReceivementSerializer,
    VisitorSerializer, ActivitySerializer, FinancialSerializer,
    AttendanceStatisticsSerializer, GradeStatisticsSerializer,
    EnrollmentStatisticsSerializer, FinancialStatisticsSerializer,
    RequisitionComparisonSerializer, VisitorStatisticsSerializer
)

# Add this with your other imports
from .analytics import (
    StudentPerformanceAnalytics,
    StudentFlaggingAnalytics,
    EnrollmentAnalytics,
    CenterActivityAnalytics,
    FinancialAnalytics,
    StoreRequisitionAnalytics,
    VisitorAnalytics,
    DocumentProcessingAnalytics
)



User = get_user_model()


# =====================================================
# Base ViewSet (shared config)
# =====================================================
class BaseViewSet(viewsets.ModelViewSet):
    """Applies global authentication and permission logic."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# =====================================================
# AUTHENTICATION & USER MANAGEMENT
# =====================================================

class SignupView(generics.CreateAPIView):
    """
    User signup - only admins can create new users
    """
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log the activity
        ActivityLog.objects.create(
            user=request.user,
            action='create_user',
            details=f"Created user: {user.username}"
        )
        
        return Response({
            "user": UserSerializer(user).data,
            "message": "User created successfully. Temporary password sent to email."
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    User login with JWT tokens
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.get(username=request.data.get('username'))
            
            # Create session
            session_id = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(minutes=30)
            Session.objects.create(
                session_id=session_id,
                user=user,
                expires_at=expires_at,
                is_active=True
            )
            
            # Log the activity
            ActivityLog.objects.create(
                user=user,
                action='login'
            )
            
            response.data['session_id'] = session_id
        
        return response


class UserProfileView(APIView):
    """
    Get current user's profile
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        
        # Get user's document count
        document_count = Document.objects.filter(
            uploader=request.user,
            is_deleted=False
        ).count()
        
        data = serializer.data
        data['document_count'] = document_count
        
        return Response(data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserViewSet(BaseViewSet):
    """
    User management viewset
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=user.id)


# =====================================================
# CENTER MANAGEMENT
# =====================================================

class CenterViewSet(BaseViewSet):
    """
    Center CRUD operations
    """
    queryset = Center.objects.filter(is_deleted=False)
    serializer_class = CenterSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


# =====================================================
# DOCUMENT UPLOAD
# =====================================================
#@method_decorator(ratelimit(key='user', rate='100/h', method='POST'), name='dispatch')
class DocumentUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='files',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Upload one or more files',
                multiple=True
            ),
            openapi.Parameter(
                name='category',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=False,
                description='Category ID'
            ),
        ]
    )
    
    def post(self, request):
        files = request.FILES.getlist('files')
        category_id = request.data.get('category')
        
        if not files:
            return Response({"error": "No files provided"}, status=400)
        
        uploaded_documents = []
        
        for file in files:
            # Validate file type
            file_ext = file.name.split('.')[-1].lower()
            if file_ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                continue
            
            # Save file
            stored_filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = f"media/uploads/documents/{stored_filename}"
            
            # Create directory if not exists
            import os
            os.makedirs('media/uploads/documents', exist_ok=True)
            
            # Save file to disk
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # Create document record
            document = Document.objects.create(
                original_filename=file.name,
                stored_filename=stored_filename,
                file_path=file_path,
                file_size=file.size / (1024 * 1024),
                file_type=file_ext if file_ext != 'jpeg' else 'jpg',
                uploader=request.user,
                category_id=category_id if category_id else None,
                status='uploaded'
            )
            
            # Add to processing queue and process immediately
            queue = ProcessingQueue.objects.create(
                document=document,
                status='queued',
                priority=0
            )
            
            # Process with mock OCR
            self._process_document_mock(document, queue)
            
            uploaded_documents.append(document)
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='upload',
            details=f"Uploaded {len(uploaded_documents)} documents"
        )
        
        serializer = DocumentListSerializer(uploaded_documents, many=True)
        return Response({
            "message": f"{len(uploaded_documents)} documents uploaded and processed",
            "documents": serializer.data
        }, status=201)
    
    def _process_document_mock(self, document, queue):
        """Process document with mock OCR"""
        try:
            # Update queue status
            queue.status = 'processing'
            queue.progress_percent = 0
            queue.save()
            
            # Get category
            if not document.category:
                queue.status = 'failed'
                queue.error_log = 'No category assigned'
                queue.save()
                document.status = 'error'
                document.save()
                return
            
            # Process with mock OCR
            extracted_fields = MockOCRProcessor.process_document(
                document, 
                document.category
            )
            
            # Save extracted data
            for field_data in extracted_fields:
                # Determine validation status
                if field_data['confidence_score'] < 70:
                    validation_status = 'invalid'
                else:
                    validation_status = 'passed'
                
                ExtractedData.objects.create(
                    document=document,
                    field_name=field_data['field_name'],
                    field_value=field_data['field_value'],
                    confidence_score=field_data['confidence_score'],
                    field_position=field_data.get('field_position', ''),
                    validation_status=validation_status
                )
            
            # Update status
            queue.status = 'completed'
            queue.progress_percent = 100
            queue.completed_at = timezone.now()
            queue.save()
            
            document.status = 'review_pending'
            document.save()
            
        except Exception as e:
            queue.status = 'failed'
            queue.error_log = str(e)
            queue.save()
            
            document.status = 'error'
            document.save()

class BulkDocumentUploadView(DocumentUploadView):
    """
    Bulk upload endpoint (same as multi-file upload)
    POST /upload/bulk/
    """
    pass


class DocumentCategorizationView(APIView):
    """
    Assign category to uploaded documents
    POST /upload/categorize/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        document_ids = request.data.get('document_ids', [])
        category_id = request.data.get('category')
        
        if not document_ids or not category_id:
            return Response(
                {"error": "document_ids and category are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        documents = Document.objects.filter(
            id__in=document_ids,
            uploader=request.user
        )
        
        updated_count = documents.update(category_id=category_id)
        
        return Response({
            "message": f"{updated_count} documents categorized successfully"
        })


# =====================================================
# DOCUMENT MANAGEMENT
# =====================================================

class DocumentViewSet(BaseViewSet):
    """
    Document CRUD and listing with filters
    GET /documents/list?user_id=X&filters=...
    """
    serializer_class = DocumentListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        queryset = Document.objects.filter(is_deleted=False)
        
        user = self.request.user
        if user.role != 'admin':
            queryset = queryset.filter(uploader=user)
        
        # Apply filters
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        city = self.request.query_params.get('city')
        status_filter = self.request.query_params.get('status')
        
        if year:
            queryset = queryset.filter(upload_timestamp__year=year)
        if month:
            queryset = queryset.filter(upload_timestamp__month=month)
        if city:
            queryset = queryset.filter(city_id=city)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('uploader', 'category', 'assigned_center', 'city')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentListSerializer


# =====================================================
# DOCUMENT REVIEW
# =====================================================

class DocumentReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Document review interface
    GET /review/document/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DocumentWithExtractedDataSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        queryset = Document.objects.filter(is_deleted=False)
        
        user = self.request.user
        if user.role != 'admin':
            queryset = queryset.filter(uploader=user)
        
        return queryset.prefetch_related('extracted_fields')


class DocumentHighlightsView(APIView):
    """
    Get low-confidence and validation warnings
    GET /review/document/{document_id}/highlights/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id)
            
            # Check permissions
            if request.user.role != 'admin' and document.uploader != request.user:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get low-confidence fields (< 70%)
            low_confidence = ExtractedData.objects.filter(
                document=document,
                confidence_score__lt=70
            )
            
            # Get validation warnings
            validation_issues = ExtractedData.objects.filter(
                document=document,
                validation_status__in=['missing', 'invalid']
            )
            
            return Response({
                "low_confidence_fields": ExtractedDataSerializer(low_confidence, many=True).data,
                "validation_issues": ExtractedDataSerializer(validation_issues, many=True).data
            })
            
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateExtractedFieldView(APIView):
    """
    Update extracted field value
    PATCH /review/document/{document_id}/update-field/
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, document_id):
        field_id = request.data.get('field_id')
        new_value = request.data.get('new_value')
        
        if not field_id or new_value is None:
            return Response(
                {"error": "field_id and new_value are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            field = ExtractedData.objects.get(
                id=field_id,
                document_id=document_id
            )
            
            # Check permissions
            if request.user.role != 'admin' and field.document.uploader != request.user:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            field.field_value = new_value
            field.validation_status = 'manually_verified'
            field.save()
            
            return Response({
                "message": "Field updated successfully",
                "field": ExtractedDataSerializer(field).data
            })
            
        except ExtractedData.DoesNotExist:
            return Response(
                {"error": "Field not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class DocumentFinalizeView(APIView):
    """
    Approve or reject document after review
    POST /review/document/{document_id}/finalize/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, document_id):
        approval_status = request.data.get('approval_status')  # 'approved' or 'rejected'
        
        if approval_status not in ['approved', 'rejected']:
            return Response(
                {"error": "approval_status must be 'approved' or 'rejected'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            document = Document.objects.get(id=document_id)
            
            # Check permissions
            if request.user.role != 'admin' and document.uploader != request.user:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if approval_status == 'approved':
                document.status = 'approved'
            else:
                document.status = 'error'
            
            document.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='approve' if approval_status == 'approved' else 'reject',
                document=document
            )
            
            return Response({
                "message": f"Document {approval_status} successfully",
                "document": DocumentDetailSerializer(document).data
            })
            
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class DocumentPreviewView(APIView):
    """
    Final preview before Excel download
    GET /review/document/{document_id}/preview/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id)
            
            # Check permissions
            if request.user.role != 'admin' and document.uploader != request.user:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = DocumentWithExtractedDataSerializer(document)
            return Response(serializer.data)
            
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ReviewProgressView(APIView):
    """
    Get review progress for user's documents
    GET /review/progress/?user_id=X
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        documents = Document.objects.filter(
            uploader=user,
            is_deleted=False
        ).select_related('category', 'queue_entry')
        
        progress_data = []
        for doc in documents:
            queue_entry = getattr(doc, 'queue_entry', None)
            progress_data.append({
                "document_id": doc.id,
                "filename": doc.original_filename,
                "status": doc.status,
                "category": doc.category.get_category_name_display() if doc.category else None,
                "upload_timestamp": doc.upload_timestamp,
                "processing_progress": queue_entry.progress_percent if queue_entry else 0
            })
        
        return Response(progress_data)


# =====================================================
# PROCESSING & QUEUE MANAGEMENT
# =====================================================

class ProcessingQueueViewSet(BaseViewSet):
    """
    Processing queue management (admin only)
    """
    queryset = ProcessingQueue.objects.all()
    serializer_class = ProcessingQueueSerializer
    permission_classes = [permissions.IsAdminUser]


class ProcessingStatusView(APIView):
    """
    Get processing status for documents
    GET /processing/status/?user_id=X&document_ids[]=1&document_ids[]=2
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        document_ids = request.query_params.getlist('document_ids[]')
        
        queryset = ProcessingQueue.objects.select_related('document')
        
        if user.role != 'admin':
            queryset = queryset.filter(document__uploader=user)
        
        if document_ids:
            queryset = queryset.filter(document_id__in=document_ids)
        
        serializer = ProcessingQueueSerializer(queryset, many=True)
        return Response(serializer.data)


# =====================================================
# DATA EXPORT
# =====================================================

class ExcelDownloadView(APIView):
    """
    Generate and download Excel files
    GET /download/excel/?document_ids[]=1&document_ids[]=2&user_id=X
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        document_ids = request.query_params.getlist('document_ids[]')
        
        if not document_ids:
            return Response(
                {"error": "document_ids are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        documents = Document.objects.filter(
            id__in=document_ids,
            status='approved',
            is_deleted=False
        )
        
        if request.user.role != 'admin':
            documents = documents.filter(uploader=request.user)
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='download',
            details=f"Downloaded {documents.count()} documents"
        )
        
        # TODO: Implement actual Excel generation logic
        return Response({
            "message": "Excel generation initiated",
            "document_count": documents.count()
        })


# =====================================================
# STUDENT MANAGEMENT
# =====================================================

class StudentViewSet(BaseViewSet):
    queryset = Student.objects.filter(is_deleted=False)
    serializer_class = StudentSerializer


class AttendanceViewSet(BaseViewSet):
    queryset = Attendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceSerializer


class GradeViewSet(BaseViewSet):
    queryset = Grade.objects.filter(is_deleted=False)
    serializer_class = GradeSerializer


# =====================================================
# STORE MANAGEMENT
# =====================================================

class StoreItemViewSet(BaseViewSet):
    queryset = StoreItem.objects.filter(is_deleted=False)
    serializer_class = StoreItemSerializer


class StoreRequisitionViewSet(BaseViewSet):
    queryset = StoreRequisition.objects.filter(is_deleted=False)
    serializer_class = StoreRequisitionSerializer

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)


class StoreReceivementViewSet(BaseViewSet):
    queryset = StoreReceivement.objects.filter(is_deleted=False)
    serializer_class = StoreReceivementSerializer

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)


# =====================================================
# VISITOR MANAGEMENT
# =====================================================

class VisitorViewSet(BaseViewSet):
    queryset = Visitor.objects.filter(is_deleted=False)
    serializer_class = VisitorSerializer


class ConsolidatedVisitorView(APIView):
    """
    Get all visitors across centers
    GET /visitors/all/?user_id=X
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        visitors = Visitor.objects.filter(is_deleted=False)
        serializer = VisitorSerializer(visitors, many=True)
        return Response(serializer.data)


# =====================================================
# ACTIVITY & FINANCIAL
# =====================================================

class ActivityViewSet(BaseViewSet):
    queryset = Activity.objects.filter(is_deleted=False)
    serializer_class = ActivitySerializer


class FinancialViewSet(BaseViewSet):
    queryset = Financial.objects.filter(is_deleted=False)
    serializer_class = FinancialSerializer


# =====================================================
# DASHBOARD ANALYTICS
# =====================================================
#@method_decorator(ratelimit(key='user', rate='500/h', method='GET'), name='dispatch')
class AttendanceDashboardView(APIView):
    """
    GET /dashboard/attendance/?center_id=X&date_range=YYYY-MM-DD,YYYY-MM-DD&user_id=X
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        center_id = request.query_params.get('center_id')
        date_range = request.query_params.get('date_range')
        
        # Parse date range
        date_from = None
        date_to = None
        if date_range:
            dates = date_range.split(',')
            date_from = dates[0] if len(dates) > 0 else None
            date_to = dates[1] if len(dates) > 1 else None
        
        # Get statistics
        stats = StudentPerformanceAnalytics.get_attendance_statistics(
            center_id=center_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Get trend data
        trend = StudentPerformanceAnalytics.get_attendance_trend(
            center_id=center_id,
            months=6
        )
        
        # Get student details
        student_details = StudentPerformanceAnalytics.get_student_attendance_details(
            center_id=center_id,
            threshold=75
        )
        
        return Response({
            'statistics': stats,
            'trend': trend,
            'student_details': student_details[:20]  # Limit to top 20
        })


class GradesDashboardView(APIView):
    """
    GET /dashboard/grades/?center_id=X&subject=Y&date_range=...&user_id=X
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        center_id = request.query_params.get('center_id')
        subject = request.query_params.get('subject')
        date_range = request.query_params.get('date_range')
        
        queryset = Grade.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(student__center_id=center_id)
        if subject:
            queryset = queryset.filter(subject=subject)
        if date_range:
            start_date, end_date = date_range.split(',')
            queryset = queryset.filter(exam_date__range=[start_date, end_date])
        
        stats = queryset.values('subject').annotate(
            average_marks=Avg('marks'),
            highest_marks=Max('marks'),
            lowest_marks=Min('marks'),
            total_students=Count('student', distinct=True)
        )
        
        return Response(list(stats))


class AutomatedFlaggingView(APIView):
    """
    GET /dashboard/flags/?center_id=X&criteria=low_attendance
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        center_id = request.query_params.get('center_id')
        criteria = request.query_params.get('criteria', 'low_attendance')
        
        flagged_students = []
        
        if criteria == 'low_attendance':
            # Find students with < 75% attendance in last 30 days
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            
            attendance_data = Attendance.objects.filter(
                date__gte=thirty_days_ago,
                is_deleted=False
            )
            
            if center_id:
                attendance_data = attendance_data.filter(center_id=center_id)
            
            student_attendance = attendance_data.values('student').annotate(
                total_days=Count('id'),
                present_days=Count('id', filter=Q(status='present')),
                attendance_rate=F('present_days') * 100.0 / F('total_days')
            ).filter(attendance_rate__lt=75)
            
            for record in student_attendance:
                student = Student.objects.get(id=record['student'])
                flagged_students.append({
                    "student_id": student.id,
                    "student_name": student.name,
                    "attendance_rate": round(record['attendance_rate'], 2),
                    "reason": "Low attendance"
                })
        
        return Response(flagged_students)


class EnrollmentDashboardView(APIView):
    """
    GET /dashboard/enrollment/?center_id=X&date_range=...
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        center_id = request.query_params.get('center_id')
        date_range = request.query_params.get('date_range')
        
        queryset = Student.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        if date_range:
            start_date, end_date = date_range.split(',')
            new_enrollments = queryset.filter(
                enrollment_date__range=[start_date, end_date]
            ).count()
        else:
            new_enrollments = 0
        
        stats = {
            "total_students": queryset.count(),
            "new_enrollments": new_enrollments
        }
        
        return Response(stats)


class CenterActivityDashboardView(APIView):
    """
    GET /dashboard/center-activity/?center_id=X&date=YYYY-MM-DD
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        center_id = request.query_params.get('center_id')
        date = request.query_params.get('date', timezone.now().date())
        
        queryset = Activity.objects.filter(
            is_deleted=False,
            date=date
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        serializer = ActivitySerializer(queryset, many=True)
        return Response(serializer.data)


class FinancialDashboardView(APIView):
    """
    GET /dashboard/finance/?center_id=X&month=1&year=2025
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        center_id = request.query_params.get('center_id')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        queryset = Financial.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        stats = queryset.aggregate(
            total_expenditure=Sum('amount', filter=Q(transaction_type='expenditure')),
            total_budget=Sum('amount', filter=Q(transaction_type='budget'))
        )
        
        return Response(stats)


class RequisitionDashboardView(APIView):
    """
    GET /dashboard/requisitions/?center_id=X&month=1&year=2025
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        center_id = request.query_params.get('center_id')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        requisitions = StoreRequisition.objects.filter(is_deleted=False)
        receivements = StoreReceivement.objects.filter(is_deleted=False)
        
        if center_id:
            requisitions = requisitions.filter(center_id=center_id)
            receivements = receivements.filter(center_id=center_id)
        
        if month and year:
            requisitions = requisitions.filter(
                requisition_date__month=month,
                requisition_date__year=year
            )
            receivements = receivements.filter(
                received_date__month=month,
                received_date__year=year
            )
        
        comparison = []
        items = StoreItem.objects.all()
        
        for item in items:
            requested = requisitions.filter(item=item).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            received = receivements.filter(item=item).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            comparison.append({
                "item_name": item.item_name,
                "requested_quantity": requested,
                "received_quantity": received,
                "fulfillment_rate": (received / requested * 100) if requested > 0 else 0
            })
        
        return Response(comparison)


class VisitorDashboardView(APIView):
    """
    GET /dashboard/visitors/?center_id=X&date_range=...
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        center_id = request.query_params.get('center_id')
        date_range = request.query_params.get('date_range')
        
        queryset = Visitor.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        if date_range:
            start_date, end_date = date_range.split(',')
            queryset = queryset.filter(visit_date__range=[start_date, end_date])
        
        stats = queryset.values('purpose').annotate(
            count=Count('id')
        )
        
        return Response({
            "total_visitors": queryset.count(),
            "by_purpose": list(stats)
        })


# =====================================================
# ADMIN FUNCTIONS
# =====================================================

class AdminUserManagementViewSet(BaseViewSet):
    """
    Admin user management - view activity, create/deactivate users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user and invalidate their sessions"""
        user = self.get_object()
        
        if user == request.user:
            return Response(
                {"error": "Cannot deactivate your own account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save()
        
        # Invalidate all sessions
        Session.objects.filter(user=user).update(is_active=False)
        
        # Revoke permissions
        UserPermissions.objects.filter(user=user).update(
            can_view=False,
            can_edit=False,
            can_delete=False
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='deactivate_user',
            details=f"Deactivated user: {user.username}"
        )
        
        return Response({
            "message": f"User {user.username} deactivated successfully"
        })

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='activate_user',
            details=f"Activated user: {user.username}"
        )
        
        return Response({
            "message": f"User {user.username} activated successfully"
        })

    @action(detail=False, methods=['get'])
    def activity_summary(self, request):
        """Get user activity summary"""
        users = User.objects.all()
        
        summary = []
        for user in users:
            upload_count = Document.objects.filter(
                uploader=user,
                is_deleted=False
            ).count()
            
            last_activity = ActivityLog.objects.filter(
                user=user
            ).order_by('-timestamp').first()
            
            summary.append({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "total_uploads": upload_count,
                "last_activity": last_activity.timestamp if last_activity else None,
                "is_active": user.is_active
            })
        
        return Response(summary)


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View activity logs (admin only)
    """
    queryset = ActivityLog.objects.all().order_by('-timestamp')
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by date range
        date_range = self.request.query_params.get('date_range')
        if date_range:
            start_date, end_date = date_range.split(',')
            queryset = queryset.filter(timestamp__range=[start_date, end_date])
        
        return queryset


class UserPermissionsViewSet(BaseViewSet):
    """
    Manage user permissions (admin only)
    """
    queryset = UserPermissions.objects.all()
    serializer_class = UserPermissionsSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update permissions for a user"""
        user_id = request.data.get('user_id')
        permissions_data = request.data.get('permissions', [])
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_count = 0
        for perm_data in permissions_data:
            UserPermissions.objects.update_or_create(
                user_id=user_id,
                feature=perm_data.get('feature'),
                defaults={
                    'can_view': perm_data.get('can_view', True),
                    'can_edit': perm_data.get('can_edit', False),
                    'can_delete': perm_data.get('can_delete', False),
                }
            )
            updated_count += 1
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='update_permissions',
            details=f"Updated {updated_count} permissions for user {user_id}"
        )
        
        return Response({
            "message": f"{updated_count} permissions updated successfully"
        })


# =====================================================
# CATEGORY MANAGEMENT
# =====================================================

class CategoryViewSet(BaseViewSet):
    """
    Category management
    """
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    

class ExcelDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        document_ids = request.query_params.getlist('document_ids[]')
        
        if not document_ids:
            return Response({"error": "document_ids required"}, status=400)
        
        # For simplicity, handle one document at a time
        document_id = document_ids[0]
        
        try:
            document = Document.objects.get(id=document_id, status='approved')
            
            # Check permission
            if request.user.role != 'admin' and document.uploader != request.user:
                return Response({"error": "Permission denied"}, status=403)
            
            # Get extracted data
            extracted_data = ExtractedData.objects.filter(document=document)
            
            # Generate Excel
            excel_file = ExcelGenerator.generate_excel(document, extracted_data)
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action='download',
                document=document
            )
            
            # Return file
            response = HttpResponse(
                excel_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{document.original_filename}.xlsx"'
            
            return response
            
        except Document.DoesNotExist:
            return Response({"error": "Document not found or not approved"}, status=404)
        
        
  