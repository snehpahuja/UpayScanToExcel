"""
Extended sample data generator for UPAY.
Run from the upaydash directory (where manage.py is):

  python manage.py shell < api/create_sample_data_extended.py

This script will generate:
- Users (1 admin, 2 employees)
- Documents (200+) across categories and statuses, spread over centers and users
- Attendance records (last 60-90 days)
- Grades (2-3 exams per subject per student)
- Activities (daily/weekly various types)
- Financials (budget + expenditure for last 12 months)
- Store items, requisitions, receivements
- Visitors (last 90 days)

The script is safe to re-run; it will only create data if the respective tables look empty.
"""

import random
from datetime import timedelta, datetime
from decimal import Decimal

from django.utils import timezone
from django.contrib.auth import get_user_model

from api.models import (
    Center, Category, Student, Document, ProcessingQueue,
    Attendance, Grade, Activity, Financial,
    StoreItem, StoreRequisition, StoreReceivement, Visitor
)

try:
    from faker import Faker
    fake = Faker()
except Exception:
    fake = None

User = get_user_model()

print("\n=== UPAY extended sample data generation ===")

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def rnd_choice(seq):
    return random.choice(list(seq))


def rnd_bool(p_true=0.5):
    return random.random() < p_true


def ensure_centers():
    if Center.objects.exists():
        return list(Center.objects.all())
    cities = [
        ("Mumbai", "Mumbai Center"),
        ("Pune", "Pune Center"),
        ("Delhi", "Delhi Center"),
        ("Bangalore", "Bangalore Center"),
    ]
    centers = []
    for city, name in cities:
        centers.append(Center.objects.create(
            name=name,
            city=city,
            address=(fake.address() if fake else f"{city} address")
        ))
        print(f"Created Center: {name}")
    return centers


def ensure_categories():
    # Use the Category choices defined in the model
    choice_keys = [
        'student_marksheet', 'attendance_sheet', 'class_diary',
        'store_requisition', 'store_invoice', 'survey_form', 'visitors_book'
    ]
    cats = []
    for key in choice_keys:
        obj, _ = Category.objects.get_or_create(
            category_name=key,
            defaults={
                'required_fields': [],
                'validation_rules': {}
            }
        )
        cats.append(obj)
        if _:
            print(f"Created Category: {key}")
    return cats


def ensure_users(centers):
    users = []
    # Admin
    admin = User.objects.filter(username='admin').first()
    if not admin:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@upayngo.com',
            password='adminpass'
        )
        print("Created admin user: admin/adminpass")
    users.append(admin)

    # Two employees
    for uname in ['employee1', 'employee2']:
        u = User.objects.filter(username=uname).first()
        if not u:
            u = User.objects.create_user(
                username=uname,
                email=f'{uname}@upayngo.com',
                password='password123',
                role='employee',
                assigned_center=rnd_choice(centers)
            )
            print(f"Created employee user: {uname}/password123")
        users.append(u)
    return users


def ensure_students(centers, per_center=30):
    if Student.objects.exists():
        return list(Student.objects.all())
    students = []
    for c in centers:
        for i in range(per_center):
            sid = f"{c.city[:3].upper()}{i+1:03d}"
            s = Student.objects.create(
                student_id=sid,
                name=(fake.name() if fake else f"Student {sid}"),
                center=c,
                enrollment_date=(timezone.now().date() - timedelta(days=random.randint(0, 365)))
            )
            students.append(s)
        print(f"Created {per_center} students for {c.name}")
    return students


def seed_documents(users, centers, categories, target=250):
    if Document.objects.exists():
        print("Documents already exist; skipping documents seeding.")
        return

    status_pool = ['uploaded', 'processing', 'review_pending', 'approved', 'error']
    file_types = ['pdf', 'jpg', 'png']
    now = timezone.now()

    created = 0
    for _ in range(target):
        uploader = rnd_choice(users)
        center = rnd_choice(centers)
        cat = rnd_choice(categories)
        ext = rnd_choice(file_types)
        fname = f"sample_{random.randint(1000, 9999)}.{ext}"
        size_mb = round(random.uniform(0.1, 4.5), 3)
        status = rnd_choice(status_pool)

        doc = Document.objects.create(
            original_filename=fname,
            stored_filename=f"{random.randint(10**12, 10**13-1)}.{ext}",
            file_path=f"media/uploads/documents/{fname}",
            file_size=size_mb,
            file_type=ext,
            uploader=uploader,
            status=status,
            category=cat,
            city=center,
            assigned_center=center
        )

        # Backdate upload_timestamp over the last ~180 days
        delta_days = random.randint(0, 180)
        doc.upload_timestamp = now - timedelta(days=delta_days, hours=random.randint(0, 23))
        doc.save(update_fields=['upload_timestamp'])

        # Optionally create a queue item for some docs
        if rnd_bool(0.7) and status in ['uploaded', 'processing', 'review_pending']:
            ProcessingQueue.objects.get_or_create(
                document=doc,
                defaults={
                    'status': 'queued' if status == 'uploaded' else ('processing' if status == 'processing' else 'completed'),
                    'priority': random.randint(0, 5)
                }
            )
        created += 1

    print(f"Created {created} documents.")


def seed_attendance(students):
    if Attendance.objects.exists():
        print("Attendance already exists; skipping attendance seeding.")
        return

    statuses = ['present', 'absent', 'excused']
    today = timezone.now().date()
    start_date = today - timedelta(days=90)
    created = 0

    for s in students:
        # For each student, 30-60 records between start_date and today
        dates = set()
        total_days = random.randint(30, 60)
        while len(dates) < total_days:
            d = start_date + timedelta(days=random.randint(0, 90))
            dates.add(d)
        for d in dates:
            Attendance.objects.create(
                student=s,
                center=s.center,
                date=d,
                status=random.choices(statuses, weights=[70, 25, 5])[0]
            )
            created += 1
    print(f"Created {created} attendance records.")


def seed_grades(students):
    if Grade.objects.exists():
        print("Grades already exist; skipping grades seeding.")
        return

    subjects = ['Math', 'Science', 'English']
    created = 0

    for s in students:
        for subj in subjects:
            # 2-3 exams per subject
            for _ in range(random.randint(2, 3)):
                exam_date = timezone.now().date() - timedelta(days=random.randint(0, 180))
                marks = random.randint(25, 100)
                Grade.objects.create(
                    student=s,
                    subject=subj,
                    exam_date=exam_date,
                    marks=marks,
                    grade=None
                )
                created += 1
    print(f"Created {created} grade records.")


def seed_activities(centers):
    if Activity.objects.exists():
        print("Activities already exist; skipping activities seeding.")
        return

    types = ['homework', 'extra_activity', 'class_activity', 'other']
    created = 0

    for c in centers:
        # For last 60 days, create 0-2 activities per day
        start_date = timezone.now().date() - timedelta(days=60)
        for i in range(61):
            if rnd_bool(0.5):
                for _ in range(random.randint(0, 2)):
                    Activity.objects.create(
                        center=c,
                        date=start_date + timedelta(days=i),
                        activity_type=rnd_choice(types),
                        description=(fake.sentence(nb_words=8) if fake else 'Activity description'),
                        participants_count=random.randint(5, 60)
                    )
                    created += 1
    print(f"Created {created} activity records.")


def seed_financials(centers):
    if Financial.objects.exists():
        print("Financials already exist; skipping financials seeding.")
        return

    created = 0
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    for c in centers:
        # last 12 months
        for i in range(12):
            month_offset = current_month - i
            year = current_year
            month = month_offset
            if month <= 0:
                month = 12 + month_offset
                year = current_year - 1

            # budget
            budget_amount = Decimal(random.randint(40000, 80000))
            Financial.objects.create(
                center=c,
                transaction_type='budget',
                amount=budget_amount,
                month=month,
                year=year,
                description='Monthly budget allocation',
                transaction_date=timezone.now().date() - timedelta(days=(i*30))
            )
            created += 1

            # expenditure
            exp_amount = Decimal(random.randint(20000, int(budget_amount)))
            Financial.objects.create(
                center=c,
                transaction_type='expenditure',
                amount=exp_amount,
                month=month,
                year=year,
                description='Monthly expenditure',
                transaction_date=timezone.now().date() - timedelta(days=(i*30 - 5))
            )
            created += 1
    print(f"Created {created} financial records (budget + expenditure).")


def ensure_store_items():
    if StoreItem.objects.exists():
        return list(StoreItem.objects.all())
    names_types = [
        ('Notebook', 'stationary'),
        ('Pencil', 'stationary'),
        ('Textbook', 'books'),
        ('Uniform Shirt', 'uniforms'),
        ('Uniform Trousers', 'uniforms'),
    ]
    items = []
    for name, t in names_types:
        items.append(StoreItem.objects.create(item_name=name, item_type=t, unit='pcs'))
        print(f"Created StoreItem: {name}")
    return items


def seed_store_requisition_and_receivements(centers, items):
    if StoreRequisition.objects.exists() or StoreReceivement.objects.exists():
        print("Store requisitions/receivements already exist; skipping seeding.")
        return

    created_req = 0
    created_rec = 0

    for c in centers:
        for _ in range(20):
            item = rnd_choice(items)
            qty = random.randint(10, 200)
            status = rnd_choice(['pending', 'approved', 'fulfilled'])
            req = StoreRequisition.objects.create(
                center=c,
                item=item,
                quantity=qty,
                requested_by=User.objects.order_by('?').first(),
                status=status
            )
            created_req += 1

            if status in ['approved', 'fulfilled'] and rnd_bool(0.8):
                received_qty = max(1, int(qty * random.uniform(0.5, 1.0)))
                StoreReceivement.objects.create(
                    center=c,
                    item=item,
                    quantity=received_qty,
                    received_by=User.objects.order_by('?').first()
                )
                created_rec += 1

    print(f"Created {created_req} requisitions and {created_rec} receivements.")


def seed_visitors(centers):
    if Visitor.objects.exists():
        print("Visitors already exist; skipping visitors seeding.")
        return

    purposes = ['Donation', 'Inspection', 'Parent Meeting', 'Supplier', 'Volunteer']
    created = 0

    for c in centers:
        for _ in range(50):
            Visitor.objects.create(
                name=(fake.name() if fake else 'Visitor'),
                contact_info=(fake.phone_number() if fake else 'N/A'),
                visit_date=timezone.now().date() - timedelta(days=random.randint(0, 90)),
                purpose=rnd_choice(purposes),
                center=c
            )
            created += 1
    print(f"Created {created} visitor records.")


# ------------------------------------------------------------
# Execution
# ------------------------------------------------------------

centers = ensure_centers()
categories = ensure_categories()
users = ensure_users(centers)
students = ensure_students(centers)

seed_documents(users, centers, categories, target=300)
seed_attendance(students)
seed_grades(students)
seed_activities(centers)
seed_financials(centers)
items = ensure_store_items()
seed_store_requisition_and_receivements(centers, items)
seed_visitors(centers)

print("\n✅ Extended sample data generated successfully.")
