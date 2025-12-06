"""
UPAY Dashboard Analytics Logic
This module contains all the business logic for generating dashboard analytics
"""

from django.db.models import Count, Avg, Sum, Q, F, Max, Min, Case, When, Value, IntegerField
from django.db.models.functions import TruncMonth, TruncYear, TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
import json

from .models import (
    Student, Attendance, Grade, Center, Activity,
    Financial, StoreRequisition, StoreReceivement,
    Visitor, Document, StoreItem
)


# =====================================================
# STUDENT PERFORMANCE ANALYTICS
# =====================================================

class StudentPerformanceAnalytics:
    """Analytics for student attendance and grades"""
    
    @staticmethod
    def get_attendance_statistics(center_id=None, date_from=None, date_to=None, student_id=None):
        """
        Calculate attendance statistics with filters
        Returns: dict with attendance metrics
        """
        queryset = Attendance.objects.filter(is_deleted=False)
        
        # Apply filters
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # Calculate statistics
        total_records = queryset.count()
        present_count = queryset.filter(status='present').count()
        absent_count = queryset.filter(status='absent').count()
        excused_count = queryset.filter(status='excused').count()
        
        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        
        return {
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'excused_count': excused_count,
            'attendance_rate': round(attendance_rate, 2),
            'period': f"{date_from} to {date_to}" if date_from and date_to else "All time"
        }
    
    @staticmethod
    def get_attendance_trend(center_id=None, months=6):
        """
        Get monthly attendance trends
        Returns: list of monthly attendance rates
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30 * months)
        
        queryset = Attendance.objects.filter(
            is_deleted=False,
            date__gte=start_date,
            date__lte=end_date
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        # Group by month
        monthly_data = queryset.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent'))
        ).order_by('month')
        
        # Calculate rates
        trend_data = []
        for item in monthly_data:
            attendance_rate = (item['present'] / item['total'] * 100) if item['total'] > 0 else 0
            trend_data.append({
                'month': item['month'].strftime('%Y-%m'),
                'attendance_rate': round(attendance_rate, 2),
                'total_days': item['total'],
                'present_days': item['present'],
                'absent_days': item['absent']
            })
        
        return trend_data
    
    @staticmethod
    def get_student_attendance_details(center_id=None, threshold=75):
        """
        Get individual student attendance details
        Returns: list of students with their attendance rates
        """
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        
        queryset = Attendance.objects.filter(
            is_deleted=False,
            date__gte=thirty_days_ago
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        # Aggregate by student
        student_data = queryset.values('student').annotate(
            total_days=Count('id'),
            present_days=Count('id', filter=Q(status='present')),
            absent_days=Count('id', filter=Q(status='absent')),
            attendance_rate=F('present_days') * 100.0 / F('total_days')
        ).order_by('-attendance_rate')
        
        # Enrich with student details
        results = []
        for data in student_data:
            student = Student.objects.get(id=data['student'])
            results.append({
                'student_id': student.student_id,
                'student_name': student.name,
                'center_name': student.center.name,
                'total_days': data['total_days'],
                'present_days': data['present_days'],
                'absent_days': data['absent_days'],
                'attendance_rate': round(data['attendance_rate'], 2),
                'flag_low_attendance': data['attendance_rate'] < threshold
            })
        
        return results
    
    @staticmethod
    def get_grade_statistics(center_id=None, subject=None, date_from=None, date_to=None):
        """
        Calculate grade statistics
        Returns: dict with grade metrics by subject
        """
        queryset = Grade.objects.filter(is_deleted=False)
        
        # Apply filters
        if center_id:
            queryset = queryset.filter(student__center_id=center_id)
        if subject:
            queryset = queryset.filter(subject=subject)
        if date_from:
            queryset = queryset.filter(exam_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(exam_date__lte=date_to)
        
        # Aggregate by subject
        subject_stats = queryset.values('subject').annotate(
            average_marks=Avg('marks'),
            highest_marks=Max('marks'),
            lowest_marks=Min('marks'),
            total_students=Count('student', distinct=True),
            total_exams=Count('id')
        ).order_by('subject')
        
        return list(subject_stats)
    
    @staticmethod
    def get_grade_distribution(center_id=None, subject=None):
        """
        Get distribution of grades
        Returns: dict with grade ranges and counts
        """
        queryset = Grade.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(student__center_id=center_id)
        if subject:
            queryset = queryset.filter(subject=subject)
        
        # Define grade ranges
        distribution = queryset.aggregate(
            excellent=Count('id', filter=Q(marks__gte=90)),  # 90-100
            good=Count('id', filter=Q(marks__gte=75, marks__lt=90)),  # 75-89
            average=Count('id', filter=Q(marks__gte=60, marks__lt=75)),  # 60-74
            below_average=Count('id', filter=Q(marks__gte=40, marks__lt=60)),  # 40-59
            poor=Count('id', filter=Q(marks__lt=40))  # 0-39
        )
        
        return distribution
    
    @staticmethod
    def get_student_performance_details(center_id=None, subject=None):
        """
        Get individual student performance details
        Returns: list of students with their performance metrics
        """
        queryset = Grade.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(student__center_id=center_id)
        if subject:
            queryset = queryset.filter(subject=subject)
        
        # Aggregate by student
        student_performance = queryset.values('student').annotate(
            average_marks=Avg('marks'),
            highest_marks=Max('marks'),
            lowest_marks=Min('marks'),
            total_exams=Count('id')
        )
        
        # Enrich with student details
        results = []
        for perf in student_performance:
            student = Student.objects.get(id=perf['student'])
            results.append({
                'student_id': student.student_id,
                'student_name': student.name,
                'center_name': student.center.name,
                'average_marks': round(perf['average_marks'], 2),
                'highest_marks': perf['highest_marks'],
                'lowest_marks': perf['lowest_marks'],
                'total_exams': perf['total_exams']
            })
        
        return results


# =====================================================
# STUDENT FLAGGING SYSTEM
# =====================================================

class StudentFlaggingAnalytics:
    """Automated system to flag students needing attention"""
    
    @staticmethod
    def flag_low_attendance_students(threshold=75, days=30, center_id=None):
        """
        Flag students with attendance below threshold
        """
        date_threshold = timezone.now().date() - timedelta(days=days)
        
        queryset = Attendance.objects.filter(
            is_deleted=False,
            date__gte=date_threshold
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        # Calculate attendance rates
        student_attendance = queryset.values('student').annotate(
            total_days=Count('id'),
            present_days=Count('id', filter=Q(status='present')),
            attendance_rate=F('present_days') * 100.0 / F('total_days')
        ).filter(attendance_rate__lt=threshold)
        
        flagged = []
        for record in student_attendance:
            student = Student.objects.get(id=record['student'])
            flagged.append({
                'student_id': student.student_id,
                'student_name': student.name,
                'center_name': student.center.name,
                'attendance_rate': round(record['attendance_rate'], 2),
                'present_days': record['present_days'],
                'total_days': record['total_days'],
                'reason': f"Low attendance ({round(record['attendance_rate'], 2)}%)",
                'severity': 'high' if record['attendance_rate'] < 50 else 'medium'
            })
        
        return flagged
    
    @staticmethod
    def flag_low_performance_students(threshold=40, center_id=None, subject=None):
        """
        Flag students with consistently low grades
        """
        queryset = Grade.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(student__center_id=center_id)
        if subject:
            queryset = queryset.filter(subject=subject)
        
        # Find students with average below threshold
        low_performers = queryset.values('student').annotate(
            average_marks=Avg('marks'),
            total_exams=Count('id')
        ).filter(average_marks__lt=threshold, total_exams__gte=2)
        
        flagged = []
        for record in low_performers:
            student = Student.objects.get(id=record['student'])
            flagged.append({
                'student_id': student.student_id,
                'student_name': student.name,
                'center_name': student.center.name,
                'average_marks': round(record['average_marks'], 2),
                'total_exams': record['total_exams'],
                'reason': f"Low performance (avg: {round(record['average_marks'], 2)})",
                'severity': 'high' if record['average_marks'] < 30 else 'medium'
            })
        
        return flagged
    
    @staticmethod
    def flag_declining_performance_students(center_id=None):
        """
        Flag students with declining grade trends (last 3 exams)
        """
        from django.db.models import Window, F
        from django.db.models.functions import RowNumber
        
        # Get last 3 grades for each student
        queryset = Grade.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(student__center_id=center_id)
        
        # Get students where grades are consistently declining
        flagged = []
        students = Student.objects.filter(is_deleted=False)
        
        if center_id:
            students = students.filter(center_id=center_id)
        
        for student in students:
            recent_grades = Grade.objects.filter(
                student=student,
                is_deleted=False
            ).order_by('-exam_date')[:3].values_list('marks', flat=True)
            
            if len(recent_grades) >= 3:
                grades_list = list(recent_grades)
                # Check if declining
                if grades_list[0] < grades_list[1] < grades_list[2]:
                    flagged.append({
                        'student_id': student.student_id,
                        'student_name': student.name,
                        'center_name': student.center.name,
                        'recent_grades': grades_list,
                        'reason': "Declining performance trend",
                        'severity': 'medium'
                    })
        
        return flagged


# =====================================================
# ENROLLMENT ANALYTICS
# =====================================================

class EnrollmentAnalytics:
    """Track student enrollment and growth"""
    
    @staticmethod
    def get_enrollment_summary(center_id=None):
        """
        Get total enrollment summary
        """
        queryset = Student.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        total_students = queryset.count()
        
        # Get enrollments by center
        by_center = queryset.values('center__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'total_students': total_students,
            'by_center': list(by_center)
        }
    
    @staticmethod
    def get_enrollment_growth(center_id=None, months=12):
        """
        Get monthly enrollment growth
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30 * months)
        
        queryset = Student.objects.filter(
            is_deleted=False,
            enrollment_date__gte=start_date
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        # Group by month
        monthly_enrollments = queryset.annotate(
            month=TruncMonth('enrollment_date')
        ).values('month').annotate(
            new_students=Count('id')
        ).order_by('month')
        
        # Calculate cumulative
        growth_data = []
        cumulative = 0
        for item in monthly_enrollments:
            cumulative += item['new_students']
            growth_data.append({
                'month': item['month'].strftime('%Y-%m'),
                'new_students': item['new_students'],
                'cumulative_students': cumulative
            })
        
        return growth_data
    
    @staticmethod
    def get_enrollment_by_center_trend(months=6):
        """
        Get enrollment trends across all centers
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30 * months)
        
        centers = Center.objects.filter(is_deleted=False)
        
        result = {}
        for center in centers:
            enrollments = Student.objects.filter(
                center=center,
                is_deleted=False,
                enrollment_date__gte=start_date
            ).annotate(
                month=TruncMonth('enrollment_date')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            
            result[center.name] = list(enrollments)
        
        return result


# =====================================================
# CENTER ACTIVITY ANALYTICS
# =====================================================

class CenterActivityAnalytics:
    """Analytics for center activities"""
    
    @staticmethod
    def get_daily_activities(center_id=None, date=None):
        """
        Get activities for a specific day
        """
        if date is None:
            date = timezone.now().date()
        
        queryset = Activity.objects.filter(
            is_deleted=False,
            date=date
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        activities = queryset.values(
            'center__name', 'activity_type', 'description', 'participants_count'
        )
        
        return list(activities)
    
    @staticmethod
    def get_activity_summary(center_id=None, date_from=None, date_to=None):
        """
        Get summary of activities by type
        """
        queryset = Activity.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        summary = queryset.values('activity_type').annotate(
            count=Count('id'),
            total_participants=Sum('participants_count')
        ).order_by('-count')
        
        return list(summary)
    
    @staticmethod
    def get_homework_completion_rate(center_id=None, days=30):
        """
        Calculate homework completion rates
        """
        date_threshold = timezone.now().date() - timedelta(days=days)
        
        queryset = Activity.objects.filter(
            is_deleted=False,
            activity_type='homework',
            date__gte=date_threshold
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        # Group by center
        homework_stats = queryset.values('center__name').annotate(
            total_activities=Count('id'),
            avg_participants=Avg('participants_count')
        )
        
        return list(homework_stats)


# =====================================================
# FINANCIAL ANALYTICS
# =====================================================

class FinancialAnalytics:
    """Analytics for financial tracking"""
    
    @staticmethod
    def get_monthly_expenditure(center_id=None, month=None, year=None):
        """
        Get monthly expenditure summary
        """
        queryset = Financial.objects.filter(
            is_deleted=False,
            transaction_type='expenditure'
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        total_expenditure = queryset.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # By center
        by_center = queryset.values('center__name').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        return {
            'total_expenditure': float(total_expenditure),
            'by_center': list(by_center)
        }
    
    @staticmethod
    def get_budget_utilization(center_id=None, month=None, year=None):
        """
        Calculate budget utilization rates
        """
        queryset = Financial.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        # Get budget and expenditure
        budget = queryset.filter(
            transaction_type='budget'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenditure = queryset.filter(
            transaction_type='expenditure'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        utilization_rate = (expenditure / budget * 100) if budget > 0 else 0
        
        return {
            'total_budget': float(budget),
            'total_expenditure': float(expenditure),
            'utilization_rate': round(utilization_rate, 2),
            'remaining_budget': float(budget - expenditure)
        }
    
    @staticmethod
    def get_expenditure_trend(center_id=None, months=12):
        """
        Get monthly expenditure trends
        """
        end_date = timezone.now()
        current_year = end_date.year
        current_month = end_date.month
        
        queryset = Financial.objects.filter(
            is_deleted=False,
            transaction_type='expenditure'
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        # Get data for last N months
        trend_data = []
        for i in range(months):
            month_offset = current_month - i
            year = current_year
            month = month_offset
            
            if month <= 0:
                month = 12 + month_offset
                year = current_year - 1
            
            monthly_exp = queryset.filter(
                year=year,
                month=month
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            trend_data.append({
                'year': year,
                'month': month,
                'expenditure': float(monthly_exp)
            })
        
        return list(reversed(trend_data))


# =====================================================
# STORE REQUISITION ANALYTICS
# =====================================================

class StoreRequisitionAnalytics:
    """Analytics for store requisitions and receivements"""
    
    @staticmethod
    def get_requisition_vs_received(center_id=None, month=None, year=None):
        """
        Compare requested vs received items
        """
        req_queryset = StoreRequisition.objects.filter(is_deleted=False)
        rec_queryset = StoreReceivement.objects.filter(is_deleted=False)
        
        if center_id:
            req_queryset = req_queryset.filter(center_id=center_id)
            rec_queryset = rec_queryset.filter(center_id=center_id)
        
        if month and year:
            req_queryset = req_queryset.filter(
                requisition_date__month=month,
                requisition_date__year=year
            )
            rec_queryset = rec_queryset.filter(
                received_date__month=month,
                received_date__year=year
            )
        
        # Aggregate by item
        items = StoreItem.objects.filter(is_deleted=False)
        comparison = []
        
        for item in items:
            requested = req_queryset.filter(item=item).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            received = rec_queryset.filter(item=item).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            fulfillment_rate = (received / requested * 100) if requested > 0 else 0
            
            comparison.append({
                'item_id': item.id,
                'item_name': item.item_name,
                'item_type': item.item_type,
                'unit': item.unit,
                'requested_quantity': requested,
                'received_quantity': received,
                'fulfillment_rate': round(fulfillment_rate, 2),
                'shortage': requested - received
            })
        
        return comparison
    
    @staticmethod
    def get_requisition_status_summary(center_id=None):
        """
        Get summary of requisition statuses
        """
        queryset = StoreRequisition.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        status_summary = queryset.values('status').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        )
        
        return list(status_summary)
    
    @staticmethod
    def get_top_requested_items(center_id=None, limit=10):
        """
        Get most frequently requested items
        """
        queryset = StoreRequisition.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        top_items = queryset.values('item__item_name', 'item__item_type').annotate(
            total_quantity=Sum('quantity'),
            request_count=Count('id')
        ).order_by('-total_quantity')[:limit]
        
        return list(top_items)


# =====================================================
# VISITOR ANALYTICS
# =====================================================

class VisitorAnalytics:
    """Analytics for visitor tracking"""
    
    @staticmethod
    def get_visitor_summary(center_id=None, date_from=None, date_to=None):
        """
        Get visitor count summary
        """
        queryset = Visitor.objects.filter(is_deleted=False)
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        if date_from:
            queryset = queryset.filter(visit_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(visit_date__lte=date_to)
        
        total_visitors = queryset.count()
        
        # By purpose
        by_purpose = queryset.values('purpose').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # By center
        by_center = queryset.values('center__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'total_visitors': total_visitors,
            'by_purpose': list(by_purpose),
            'by_center': list(by_center)
        }
    
    @staticmethod
    def get_visitor_trend(center_id=None, months=6):
        """
        Get monthly visitor trends
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30 * months)
        
        queryset = Visitor.objects.filter(
            is_deleted=False,
            visit_date__gte=start_date
        )
        
        if center_id:
            queryset = queryset.filter(center_id=center_id)
        
        # Group by month
        monthly_visitors = queryset.annotate(
            month=TruncMonth('visit_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return list(monthly_visitors)
    
    @staticmethod
    def get_consolidated_visitors():
        """
        Get all visitors with contact info for outreach
        """
        visitors = Visitor.objects.filter(
            is_deleted=False
        ).exclude(
            contact_info__isnull=True
        ).exclude(
            contact_info=''
        ).values(
            'name', 'contact_info', 'center__name', 'visit_date', 'purpose'
        ).order_by('-visit_date')
        
        return list(visitors)


# =====================================================
# DOCUMENT PROCESSING ANALYTICS
# =====================================================

class DocumentProcessingAnalytics:
    """Analytics for document processing"""
    
    @staticmethod
    def get_processing_summary(user_id=None):
        """
        Get document processing summary
        """
        queryset = Document.objects.filter(is_deleted=False)
        
        if user_id:
            queryset = queryset.filter(uploader_id=user_id)
        
        summary = {
            'total_documents': queryset.count(),
            'by_status': {},
            'by_category': {},
            'by_user': []
        }
        
        # By status
        by_status = queryset.values('status').annotate(
            count=Count('id')
        )
        summary['by_status'] = {item['status']: item['count'] for item in by_status}
        
        # By category
        by_category = queryset.values('category__category_name').annotate(
            count=Count('id')
        )
        summary['by_category'] = list(by_category)
        
        # By user (if admin view)
        if not user_id:
            by_user = queryset.values('uploader__username').annotate(
                count=Count('id')
            ).order_by('-count')
            summary['by_user'] = list(by_user)
        
        return summary
    
    @staticmethod
    def get_upload_trend(user_id=None, months=6):
        """
        Get upload trends over time
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30 * months)
        
        queryset = Document.objects.filter(
            is_deleted=False,
            upload_timestamp__gte=start_date
        )
        
        if user_id:
            queryset = queryset.filter(uploader_id=user_id)
        
        # Group by month
        monthly_uploads = queryset.annotate(
            month=TruncMonth('upload_timestamp')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return list(monthly_uploads)