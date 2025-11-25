"""
Create sample data for testing
Run: python manage.py shell < api/create_sample_data.py
"""

from api.models import Center, Student, Category
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker()

# Create centers
centers = []
for city in ['Mumbai', 'Delhi', 'Bangalore']:
    center = Center.objects.create(
        name=f"{city} Center",
        city=city,
        address=fake.address()
    )
    centers.append(center)
    print(f"Created {center.name}")

# Create categories
categories_data = [
    ('student_marksheet', 'Student Marksheet'),
    ('attendance_sheet', 'Attendance Sheet'),
    ('class_diary', 'Class Diary'),
]

for cat_name, cat_display in categories_data:
    Category.objects.get_or_create(
        category_name=cat_name,
        defaults={'required_fields': [], 'validation_rules': {}}
    )
    print(f"Created category: {cat_display}")

# Create students
for center in centers:
    for i in range(25):
        Student.objects.create(
            student_id=f"{center.city[:3].upper()}{i+1:03d}",
            name=fake.name(),
            center=center,
            enrollment_date=fake.date_this_year()
        )
    print(f"Created 25 students for {center.name}")

print("\n✅ Sample data created!")