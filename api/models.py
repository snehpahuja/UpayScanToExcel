from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

# ---------------------------------------------------------------------
# Base Model
# ---------------------------------------------------------------------
class BaseModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)s_updated"
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)s_deleted"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------
# Center Model
# ---------------------------------------------------------------------
class Center(BaseModel):
    name = models.CharField(max_length=150, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_info = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"], name="idx_center_name"),
            models.Index(fields=["city"], name="idx_center_city"),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}"


# ---------------------------------------------------------------------
# User Model
# ---------------------------------------------------------------------
class User(AbstractUser, BaseModel):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    assigned_center = models.ForeignKey(
        Center, on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='users'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


# ---------------------------------------------------------------------
# Session Model
# ---------------------------------------------------------------------
class Session(BaseModel):
    session_id = models.CharField(max_length=255, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_active"], name="idx_session_user_active"),
        ]

    def __str__(self):
        return f"Session for {self.user.username}"


# ---------------------------------------------------------------------
# Category Model
# ---------------------------------------------------------------------
class Category(BaseModel):
    CATEGORY_CHOICES = [
        ('student_marksheet', 'Student Marksheet'),
        ('attendance_sheet', 'Attendance Sheet'),
        ('class_diary', 'Class Diary'),
        ('store_requisition', 'Store Requisition Voucher'),
        ('store_invoice', 'Store Invoice Voucher'),
        ('survey_form', 'Survey Form'),
        ('visitors_book', 'Visitors Book'),
    ]
    
    category_name = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        unique=True,
        db_index=True
    )
    required_fields = models.JSONField(default=list)
    validation_rules = models.JSONField(default=dict)

    def __str__(self):
        return self.get_category_name_display()


# ---------------------------------------------------------------------
# Document Model
# ---------------------------------------------------------------------
class Document(BaseModel):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('review_pending', 'Review Pending'),
        ('approved', 'Approved'),
        ('error', 'Error'),
    ]
    
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('jpg', 'JPG'),
        ('png', 'PNG'),
    ]
    
    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(max_length=255, unique=True)
    file_path = models.CharField(max_length=500)
    file_size = models.FloatField(help_text="Size in MB")
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    
    uploader = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='uploaded_documents',
        db_index=True
    )
    upload_timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='uploaded',
        db_index=True
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='documents'
    )
    
    city = models.ForeignKey(
        Center, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='documents_by_city',
        help_text="Location tag"
    )
    assigned_center = models.ForeignKey(
        Center, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_documents'
    )

    class Meta:
        indexes = [
            models.Index(fields=["uploader", "status"], name="idx_doc_uploader_status"),
            models.Index(fields=["upload_timestamp"], name="idx_doc_upload_time"),
            models.Index(fields=["category"], name="idx_doc_category"),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.status})"


# ---------------------------------------------------------------------
# Processing Queue Model
# ---------------------------------------------------------------------
class ProcessingQueue(BaseModel):
    QUEUE_STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    document = models.OneToOneField(
        Document, 
        on_delete=models.CASCADE, 
        related_name='queue_entry'
    )
    status = models.CharField(
        max_length=20, 
        choices=QUEUE_STATUS_CHOICES, 
        default='queued',
        db_index=True
    )
    progress_percent = models.PositiveSmallIntegerField(default=0)
    priority = models.PositiveIntegerField(default=0, db_index=True)
    queued_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_log = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "priority"], name="idx_queue_status_priority"),
        ]

    def __str__(self):
        return f"Queue: {self.document.original_filename} - {self.status}"


# ---------------------------------------------------------------------
# ExtractedData Model
# ---------------------------------------------------------------------
class ExtractedData(BaseModel):
    VALIDATION_STATUS_CHOICES = [
        ('passed', 'Passed'),
        ('missing', 'Missing'),
        ('invalid', 'Invalid'),
        ('manually_verified', 'Manually Verified'),
    ]
    
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE, 
        related_name='extracted_fields',
        db_index=True
    )
    field_name = models.CharField(max_length=100)
    field_value = models.TextField()
    confidence_score = models.PositiveSmallIntegerField(
        help_text="OCR confidence (0-100)"
    )
    field_position = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Coordinates/region in source"
    )
    validation_status = models.CharField(
        max_length=20, 
        choices=VALIDATION_STATUS_CHOICES,
        default='passed'
    )

    class Meta:
        indexes = [
            models.Index(fields=["document", "field_name"], name="idx_extracted_doc_field"),
            models.Index(fields=["validation_status"], name="idx_extracted_validation"),
        ]

    def __str__(self):
        return f"{self.document.original_filename} - {self.field_name}"


# ---------------------------------------------------------------------
# User Permissions Model
# ---------------------------------------------------------------------
class UserPermissions(BaseModel):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='permissions'
    )
    feature = models.CharField(max_length=100)
    can_view = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "User Permissions"

    def __str__(self):
        return f"Permissions for {self.user.username} - {self.feature}"


# ---------------------------------------------------------------------
# Activity Log Model
# ---------------------------------------------------------------------
class ActivityLog(BaseModel):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('upload', 'Upload'),
        ('review', 'Review'),
        ('approve', 'Approve'),
        ('download', 'Download'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='activity_logs',
        db_index=True
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    document = models.ForeignKey(
        Document, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activity_logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    details = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "action"], name="idx_activity_user_action"),
            models.Index(fields=["timestamp"], name="idx_activity_timestamp"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"


# ---------------------------------------------------------------------
# Student Model
# ---------------------------------------------------------------------
class Student(BaseModel):
    student_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    center = models.ForeignKey(
        Center, 
        on_delete=models.CASCADE, 
        related_name='students'
    )
    enrollment_date = models.DateField()
    contact_info = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["center"], name="idx_student_center"),
        ]

    def __str__(self):
        return f"{self.name} ({self.student_id})"


# ---------------------------------------------------------------------
# Attendance Model
# ---------------------------------------------------------------------
class Attendance(BaseModel):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='attendance_records',
        db_index=True
    )
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('student', 'date')
        indexes = [
            models.Index(fields=["student", "date"], name="idx_attendance_student_date"),
            models.Index(fields=["center", "date"], name="idx_attendance_center_date"),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"


# ---------------------------------------------------------------------
# Grade Model
# ---------------------------------------------------------------------
class Grade(BaseModel):
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='grades',
        db_index=True
    )
    subject = models.CharField(max_length=100, db_index=True)
    exam_date = models.DateField(db_index=True)
    marks = models.PositiveIntegerField()
    grade = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["student", "subject"], name="idx_grade_student_subject"),
            models.Index(fields=["exam_date"], name="idx_grade_exam_date"),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.subject} - {self.marks}"


# ---------------------------------------------------------------------
# Store Item Model
# ---------------------------------------------------------------------
class StoreItem(BaseModel):
    ITEM_TYPE_CHOICES = [
        ('stationary', 'Stationary'),
        ('books', 'Books'),
        ('uniforms', 'Uniforms'),
        ('other', 'Other'),
    ]
    
    item_name = models.CharField(max_length=150, db_index=True)
    item_type = models.CharField(max_length=50, choices=ITEM_TYPE_CHOICES)
    unit = models.CharField(max_length=20, help_text="e.g., pcs, kg")

    def __str__(self):
        return f"{self.item_name} ({self.unit})"


# ---------------------------------------------------------------------
# Store Requisition Model
# ---------------------------------------------------------------------
class StoreRequisition(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('fulfilled', 'Fulfilled'),
    ]
    
    center = models.ForeignKey(
        Center, 
        on_delete=models.CASCADE, 
        related_name='requisitions',
        db_index=True
    )
    item = models.ForeignKey(
        StoreItem, 
        on_delete=models.CASCADE, 
        related_name='requisitions'
    )
    quantity = models.PositiveIntegerField()
    requested_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='requisitions_made'
    )
    requisition_date = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        db_index=True
    )
    fulfilled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["center", "status"], name="idx_requisition_center_status"),
        ]

    def __str__(self):
        return f"{self.center.name} - {self.item.item_name} x{self.quantity}"


# ---------------------------------------------------------------------
# Store Receivement Model
# ---------------------------------------------------------------------
class StoreReceivement(BaseModel):
    center = models.ForeignKey(
        Center, 
        on_delete=models.CASCADE, 
        related_name='receivements',
        db_index=True
    )
    item = models.ForeignKey(
        StoreItem, 
        on_delete=models.CASCADE, 
        related_name='receivements'
    )
    quantity = models.PositiveIntegerField()
    received_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='receivements_logged'
    )
    received_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["center", "received_date"], name="idx_receive_center_date"),
        ]

    def __str__(self):
        return f"{self.center.name} received {self.item.item_name} x{self.quantity}"


# ---------------------------------------------------------------------
# Visitor Model
# ---------------------------------------------------------------------
class Visitor(BaseModel):
    name = models.CharField(max_length=150)
    contact_info = models.CharField(max_length=100, blank=True, null=True)
    visit_date = models.DateField(db_index=True)
    purpose = models.TextField()
    center = models.ForeignKey(
        Center, 
        on_delete=models.CASCADE, 
        related_name='visitors',
        db_index=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["center", "visit_date"], name="idx_visitor_center_date"),
        ]

    def __str__(self):
        return f"{self.name} visited {self.center.name} on {self.visit_date}"


# ---------------------------------------------------------------------
# Center Activity Model (for daily activity monitoring)
# ---------------------------------------------------------------------
class Activity(BaseModel):
    ACTIVITY_TYPE_CHOICES = [
        ('homework', 'Homework Completion'),
        ('extra_activity', 'Extra Activity'),
        ('class_activity', 'Class Activity'),
        ('other', 'Other'),
    ]
    
    center = models.ForeignKey(
        Center, 
        on_delete=models.CASCADE, 
        related_name='activities',
        db_index=True
    )
    date = models.DateField(db_index=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField()
    participants_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Activities"
        indexes = [
            models.Index(fields=["center", "date"], name="idx_activity_center_date"),
        ]

    def __str__(self):
        return f"{self.center.name} - {self.activity_type} on {self.date}"


# ---------------------------------------------------------------------
# Financial Model (for expenditure tracking)
# ---------------------------------------------------------------------
class Financial(BaseModel):
    TRANSACTION_TYPE_CHOICES = [
        ('expenditure', 'Expenditure'),
        ('budget', 'Budget Allocation'),
    ]
    
    center = models.ForeignKey(
        Center, 
        on_delete=models.CASCADE, 
        related_name='financials',
        db_index=True
    )
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPE_CHOICES
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["center", "year", "month"], name="idx_financial_center_period"),
        ]

    def __str__(self):
        return f"{self.center.name} - {self.transaction_type} - {self.amount}"