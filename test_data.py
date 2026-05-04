#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AttendanceSystem.settings')
django.setup()

from students.models import Course, Student, Attendance, UserProfile
from django.contrib.auth.models import User
from datetime import date

try:
    # Get or create admin user profile
    admin_user = User.objects.get(username='admin')
    profile, created = UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})
    if created:
        print(f"Created UserProfile for admin")

    # Create test course
    course, created = Course.objects.get_or_create(
        name='Python', 
        defaults={'description': 'Python Programming'}
    )
    print(f"Course: {course}")

    # Create test student
    student, created = Student.objects.get_or_create(
        name='John Doe',
        roll_number='001',
        course=course
    )
    print(f"Student: {student}")

    # Create test attendance
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        date=date.today(),
        defaults={'status': 'Present'}
    )
    print(f"Attendance: {attendance}")

    # Verify all records
    print(f"\nDatabase Status:")
    print(f"Total Students: {Student.objects.count()}")
    print(f"Total Attendance Records: {Attendance.objects.count()}")
    print(f"Total Courses: {Course.objects.count()}")
    print("\n✓ All database operations successful!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
