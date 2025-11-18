from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Center, Document, ProcessingQueue, ExtractedData, 
    Category, UserPermissions, ActivityLog, Student, 
    Attendance, Grade, StoreItem, StoreRequisition, 
    StoreReceivement, Visitor, Activity, Financial, Session
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# -------------------- Base Serializer --------------------
class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        fields = [
            'created_by', 'created_at',
            'updated_by', 'updated_at',
            'deleted_by', 'deleted_at',
            'is_deleted'
        ]


# -------------------- User & Authentication Serializers --------------------
class UserSerializer(BaseModelSerializer):
    center_name = serializers.CharField(source='assigned_center.name', read_only=True)
    
    class Meta:
        model = User
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'assigned_center', 'center_name'
        ]
        read_only_fields = ['id']


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 'assigned_center']

    def validate_email(self, value):
        """Ensure email is from @upayngo.com domain"""
        if not value.endswith('@upayngo.com'):
            raise serializers.ValidationError("Email must be from @upayngo.com domain")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'employee'),
            assigned_center=validated_data.get('assigned_center')
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            "user_id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
            "center_id": self.user.assigned_center.id if self.user.assigned_center else None,
        })
        return data


# -------------------- Session Serializer --------------------
class SessionSerializer(BaseModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Session
        fields = BaseModelSerializer.Meta.fields + [
            'session_id', 'user', 'username', 'last_activity', 
            'expires_at', 'is_active'
        ]
        read_only_fields = ['session_id', 'last_activity']


# -------------------- Center Serializer --------------------
class CenterSerializer(BaseModelSerializer):
    class Meta:
        model = Center
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'name', 'city', 'address', 'contact_info'
        ]


# -------------------- Category Serializer --------------------
class CategorySerializer(BaseModelSerializer):
    category_display = serializers.CharField(source='get_category_name_display', read_only=True)
    
    class Meta:
        model = Category
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'category_name', 'category_display', 
            'required_fields', 'validation_rules'
        ]


# -------------------- Document Serializers --------------------
class DocumentListSerializer(BaseModelSerializer):
    """Lightweight serializer for document lists"""
    uploader_name = serializers.CharField(source='uploader.username', read_only=True)
    category_name = serializers.CharField(source='category.get_category_name_display', read_only=True)
    center_name = serializers.CharField(source='assigned_center.name', read_only=True)
    city_name = serializers.CharField(source='city.city', read_only=True)
    
    class Meta:
        model = Document
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'original_filename', 'file_type', 'file_size',
            'uploader', 'uploader_name', 'upload_timestamp',
            'status', 'category', 'category_name',
            'city_name', 'center_name'
        ]
        read_only_fields = ['id', 'upload_timestamp', 'uploader']


class DocumentDetailSerializer(BaseModelSerializer):
    """Detailed serializer with full document information"""
    uploader_name = serializers.CharField(source='uploader.username', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    center_details = CenterSerializer(source='assigned_center', read_only=True)
    
    class Meta:
        model = Document
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'original_filename', 'stored_filename', 'file_path',
            'file_size', 'file_type', 'uploader', 'uploader_name',
            'upload_timestamp', 'status', 'category', 'category_details',
            'city', 'assigned_center', 'center_details'
        ]
        read_only_fields = ['id', 'upload_timestamp', 'stored_filename', 'file_path']


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload"""
    
    class Meta:
        model = Document
        fields = ['original_filename', 'file_type', 'file_size', 'category', 'city', 'assigned_center']

    def create(self, validated_data):
        # The uploader will be set in the view
        return super().create(validated_data)


# -------------------- Processing Queue Serializer --------------------
class ProcessingQueueSerializer(BaseModelSerializer):
    document_name = serializers.CharField(source='document.original_filename', read_only=True)
    
    class Meta:
        model = ProcessingQueue
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'document', 'document_name', 'status', 
            'progress_percent', 'priority', 'queued_at', 
            'completed_at', 'error_log'
        ]
        read_only_fields = ['id', 'queued_at', 'completed_at']


# -------------------- Extracted Data Serializers --------------------
class ExtractedDataSerializer(BaseModelSerializer):
    class Meta:
        model = ExtractedData
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'document', 'field_name', 'field_value',
            'confidence_score', 'field_position', 'validation_status'
        ]
        read_only_fields = ['id']


class ExtractedDataUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating extracted field values"""
    
    class Meta:
        model = ExtractedData
        fields = ['field_value', 'validation_status']


class DocumentWithExtractedDataSerializer(DocumentDetailSerializer):
    """Document with all extracted fields"""
    extracted_fields = ExtractedDataSerializer(many=True, read_only=True)
    
    class Meta(DocumentDetailSerializer.Meta):
        fields = DocumentDetailSerializer.Meta.fields + ['extracted_fields']


# -------------------- User Permissions Serializer --------------------
class UserPermissionsSerializer(BaseModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserPermissions
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'user', 'username', 'feature',
            'can_view', 'can_edit', 'can_delete'
        ]


# -------------------- Activity Log Serializer --------------------
class ActivityLogSerializer(BaseModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    document_name = serializers.CharField(source='document.original_filename', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'user', 'username', 'action', 
            'document', 'document_name', 'timestamp', 'details'
        ]
        read_only_fields = ['id', 'timestamp']


# -------------------- Student Serializers --------------------
class StudentSerializer(BaseModelSerializer):
    center_name = serializers.CharField(source='center.name', read_only=True)
    
    class Meta:
        model = Student
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'student_id', 'name', 'center', 'center_name',
            'enrollment_date', 'contact_info'
        ]


# -------------------- Attendance Serializer --------------------
class AttendanceSerializer(BaseModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    center_name = serializers.CharField(source='center.name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'student', 'student_name', 'center', 
            'center_name', 'date', 'status'
        ]


# -------------------- Grade Serializer --------------------
class GradeSerializer(BaseModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    
    class Meta:
        model = Grade
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'student', 'student_name', 'subject',
            'exam_date', 'marks', 'grade'
        ]


# -------------------- Store Item Serializer --------------------
class StoreItemSerializer(BaseModelSerializer):
    class Meta:
        model = StoreItem
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'item_name', 'item_type', 'unit'
        ]


# -------------------- Store Requisition Serializer --------------------
class StoreRequisitionSerializer(BaseModelSerializer):
    center_name = serializers.CharField(source='center.name', read_only=True)
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    
    class Meta:
        model = StoreRequisition
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'center', 'center_name', 'item', 'item_name',
            'quantity', 'requested_by', 'requested_by_name',
            'requisition_date', 'status', 'fulfilled_at'
        ]
        read_only_fields = ['id', 'requisition_date', 'requested_by']


# -------------------- Store Receivement Serializer --------------------
class StoreReceivementSerializer(BaseModelSerializer):
    center_name = serializers.CharField(source='center.name', read_only=True)
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.username', read_only=True)
    
    class Meta:
        model = StoreReceivement
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'center', 'center_name', 'item', 'item_name',
            'quantity', 'received_by', 'received_by_name', 'received_date'
        ]
        read_only_fields = ['id', 'received_date', 'received_by']


# -------------------- Visitor Serializer --------------------
class VisitorSerializer(BaseModelSerializer):
    center_name = serializers.CharField(source='center.name', read_only=True)
    
    class Meta:
        model = Visitor
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'name', 'contact_info', 'visit_date',
            'purpose', 'center', 'center_name'
        ]


# -------------------- Activity Serializer --------------------
class ActivitySerializer(BaseModelSerializer):
    center_name = serializers.CharField(source='center.name', read_only=True)
    
    class Meta:
        model = Activity
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'center', 'center_name', 'date',
            'activity_type', 'description', 'participants_count'
        ]


# -------------------- Financial Serializer --------------------
class FinancialSerializer(BaseModelSerializer):
    center_name = serializers.CharField(source='center.name', read_only=True)
    
    class Meta:
        model = Financial
        fields = BaseModelSerializer.Meta.fields + [
            'id', 'center', 'center_name', 'transaction_type',
            'amount', 'month', 'year', 'description', 'transaction_date'
        ]


# -------------------- Dashboard Statistics Serializers --------------------
class AttendanceStatisticsSerializer(serializers.Serializer):
    """Serializer for attendance dashboard statistics"""
    total_students = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
    date_range = serializers.CharField()


class GradeStatisticsSerializer(serializers.Serializer):
    """Serializer for grade dashboard statistics"""
    subject = serializers.CharField()
    average_marks = serializers.FloatField()
    highest_marks = serializers.IntegerField()
    lowest_marks = serializers.IntegerField()
    total_students = serializers.IntegerField()


class EnrollmentStatisticsSerializer(serializers.Serializer):
    """Serializer for enrollment tracking"""
    center_name = serializers.CharField()
    total_students = serializers.IntegerField()
    new_enrollments = serializers.IntegerField()
    period = serializers.CharField()


class FinancialStatisticsSerializer(serializers.Serializer):
    """Serializer for financial tracking"""
    center_name = serializers.CharField()
    total_expenditure = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    utilization_rate = serializers.FloatField()
    month = serializers.IntegerField()
    year = serializers.IntegerField()


class RequisitionComparisonSerializer(serializers.Serializer):
    """Serializer for requisition vs received comparison"""
    item_name = serializers.CharField()
    requested_quantity = serializers.IntegerField()
    received_quantity = serializers.IntegerField()
    fulfillment_rate = serializers.FloatField()


class VisitorStatisticsSerializer(serializers.Serializer):
    """Serializer for visitor analytics"""
    center_name = serializers.CharField()
    total_visitors = serializers.IntegerField()
    period = serializers.CharField()
    purposes = serializers.DictField(child=serializers.IntegerField())