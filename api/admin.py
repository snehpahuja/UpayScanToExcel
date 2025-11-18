from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User, Center, Session, Category, Document, ProcessingQueue,
    ExtractedData, UserPermissions, ActivityLog, Student,
    Attendance, Grade, StoreItem, StoreRequisition,
    StoreReceivement, Visitor, Activity, Financial
)


# =====================================================
# USER & AUTHENTICATION
# =====================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'assigned_center', 'is_active', 'created_at', 'is_deleted')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active', 'is_deleted', 'assigned_center')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password')
        }),
        ('Role & Center', {
            'fields': ('role', 'assigned_center')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
        ('Audit Fields', {
            'fields': ('created_by', 'updated_by', 'deleted_by', 'deleted_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'is_active', 'last_activity', 'expires_at', 'created_at')
    search_fields = ('session_id', 'user__username', 'user__email')
    list_filter = ('is_active', 'created_at', 'expires_at')
    readonly_fields = ('session_id', 'created_at', 'last_activity')
    date_hierarchy = 'created_at'


# =====================================================
# CENTER MANAGEMENT
# =====================================================

@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'contact_info', 'created_at', 'is_deleted')
    search_fields = ('name', 'city', 'address')
    list_filter = ('city', 'is_deleted', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


# =====================================================
# DOCUMENT MANAGEMENT
# =====================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'get_category_display', 'created_at', 'is_deleted')
    search_fields = ('category_name',)
    list_filter = ('category_name', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_category_display(self, obj):
        return obj.get_category_name_display()
    get_category_display.short_description = 'Display Name'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename', 'uploader', 'status', 'category', 
        'file_type', 'file_size_display', 'upload_timestamp', 'is_deleted'
    )
    search_fields = ('original_filename', 'stored_filename', 'uploader__username')
    list_filter = ('status', 'file_type', 'category', 'is_deleted', 'upload_timestamp')
    readonly_fields = ('stored_filename', 'upload_timestamp', 'created_at', 'updated_at')
    date_hierarchy = 'upload_timestamp'
    
    fieldsets = (
        ('File Information', {
            'fields': ('original_filename', 'stored_filename', 'file_path', 'file_size', 'file_type')
        }),
        ('Metadata', {
            'fields': ('uploader', 'upload_timestamp', 'status', 'category')
        }),
        ('Location', {
            'fields': ('city', 'assigned_center')
        }),
        ('Audit Fields', {
            'fields': ('created_by', 'updated_by', 'deleted_by', 'deleted_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        return f"{obj.file_size:.2f} MB"
    file_size_display.short_description = 'File Size'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('uploader', 'category', 'city', 'assigned_center')


@admin.register(ProcessingQueue)
class ProcessingQueueAdmin(admin.ModelAdmin):
    list_display = (
        'document', 'status', 'progress_display', 'priority', 
        'queued_at', 'completed_at', 'is_deleted'
    )
    search_fields = ('document__original_filename',)
    list_filter = ('status', 'priority', 'is_deleted', 'queued_at')
    readonly_fields = ('queued_at', 'completed_at', 'created_at', 'updated_at')
    date_hierarchy = 'queued_at'
    
    def progress_display(self, obj):
        color = 'green' if obj.progress_percent == 100 else 'orange' if obj.progress_percent > 0 else 'red'
        return format_html(
            '<span style="color: {};">{} %</span>',
            color,
            obj.progress_percent
        )
    progress_display.short_description = 'Progress'


@admin.register(ExtractedData)
class ExtractedDataAdmin(admin.ModelAdmin):
    list_display = (
        'document', 'field_name', 'field_value_preview', 
        'confidence_display', 'validation_status', 'created_at', 'is_deleted'
    )
    search_fields = ('document__original_filename', 'field_name', 'field_value')
    list_filter = ('validation_status', 'is_deleted', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def field_value_preview(self, obj):
        return obj.field_value[:50] + '...' if len(obj.field_value) > 50 else obj.field_value
    field_value_preview.short_description = 'Field Value'
    
    def confidence_display(self, obj):
        if obj.confidence_score >= 70:
            color = 'green'
        elif obj.confidence_score >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} %</span>',
            color,
            obj.confidence_score
        )
    confidence_display.short_description = 'Confidence'


# =====================================================
# USER PERMISSIONS & ACTIVITY
# =====================================================

@admin.register(UserPermissions)
class UserPermissionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'feature', 'can_view', 'can_edit', 'can_delete', 'created_at', 'is_deleted')
    search_fields = ('user__username', 'feature')
    list_filter = ('can_view', 'can_edit', 'can_delete', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'document', 'timestamp', 'details_preview', 'is_deleted')
    search_fields = ('user__username', 'action', 'details')
    list_filter = ('action', 'timestamp', 'is_deleted')
    readonly_fields = ('timestamp', 'created_at', 'updated_at')
    date_hierarchy = 'timestamp'
    
    def details_preview(self, obj):
        if obj.details:
            return obj.details[:50] + '...' if len(obj.details) > 50 else obj.details
        return '-'
    details_preview.short_description = 'Details'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'document')


# =====================================================
# STUDENT MANAGEMENT
# =====================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'center', 'enrollment_date', 'contact_info', 'is_deleted')
    search_fields = ('student_id', 'name', 'contact_info')
    list_filter = ('center', 'enrollment_date', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'enrollment_date'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'center', 'date', 'status', 'is_deleted')
    search_fields = ('student__name', 'student__student_id')
    list_filter = ('status', 'center', 'date', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student', 'center')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam_date', 'marks', 'grade', 'is_deleted')
    search_fields = ('student__name', 'student__student_id', 'subject')
    list_filter = ('subject', 'exam_date', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'exam_date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student')


# =====================================================
# STORE MANAGEMENT
# =====================================================

@admin.register(StoreItem)
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'item_type', 'unit', 'created_at', 'is_deleted')
    search_fields = ('item_name',)
    list_filter = ('item_type', 'is_deleted', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StoreRequisition)
class StoreRequisitionAdmin(admin.ModelAdmin):
    list_display = (
        'center', 'item', 'quantity', 'requested_by', 
        'requisition_date', 'status', 'fulfilled_at', 'is_deleted'
    )
    search_fields = ('center__name', 'item__item_name', 'requested_by__username')
    list_filter = ('status', 'center', 'requisition_date', 'is_deleted')
    readonly_fields = ('requisition_date', 'created_at', 'updated_at')
    date_hierarchy = 'requisition_date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('center', 'item', 'requested_by')


@admin.register(StoreReceivement)
class StoreReceivementAdmin(admin.ModelAdmin):
    list_display = (
        'center', 'item', 'quantity', 'received_by', 
        'received_date', 'is_deleted'
    )
    search_fields = ('center__name', 'item__item_name', 'received_by__username')
    list_filter = ('center', 'received_date', 'is_deleted')
    readonly_fields = ('received_date', 'created_at', 'updated_at')
    date_hierarchy = 'received_date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('center', 'item', 'received_by')


# =====================================================
# VISITOR MANAGEMENT
# =====================================================

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_info', 'center', 'visit_date', 'purpose_preview', 'is_deleted')
    search_fields = ('name', 'contact_info', 'purpose')
    list_filter = ('center', 'visit_date', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'visit_date'
    
    def purpose_preview(self, obj):
        return obj.purpose[:50] + '...' if len(obj.purpose) > 50 else obj.purpose
    purpose_preview.short_description = 'Purpose'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('center')


# =====================================================
# ACTIVITY & FINANCIAL
# =====================================================

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'center', 'date', 'activity_type', 'participants_count', 
        'description_preview', 'is_deleted'
    )
    search_fields = ('center__name', 'description')
    list_filter = ('activity_type', 'center', 'date', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('center')


@admin.register(Financial)
class FinancialAdmin(admin.ModelAdmin):
    list_display = (
        'center', 'transaction_type', 'amount', 'month', 'year', 
        'transaction_date', 'description_preview', 'is_deleted'
    )
    search_fields = ('center__name', 'description')
    list_filter = ('transaction_type', 'center', 'year', 'month', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'transaction_date'
    
    def description_preview(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_preview.short_description = 'Description'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('center')


# =====================================================
# CUSTOM ADMIN SITE CONFIGURATION
# =====================================================

admin.site.site_header = "UPAY Document Processing System"
admin.site.site_title = "UPAY Admin"
admin.site.index_title = "Welcome to UPAY Administration"