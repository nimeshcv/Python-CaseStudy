from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CourseForm, SignupForm, StudentForm, SubjectForm, TeacherForm, TeacherUpdateForm
from .models import Attendance, Course, Student, Subject, UserProfile


def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'


def is_teacher_or_admin(user):
    return hasattr(user, 'profile') and user.profile.role in ['teacher', 'admin']


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')

    return render(request, 'students/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        role = 'admin' if not UserProfile.objects.filter(role='admin').exists() else 'teacher'
        UserProfile.objects.create(user=user, role=role)
        if role == 'admin':
            messages.success(request, 'Admin account created successfully. Please login.')
        else:
            messages.success(request, 'Teacher account created successfully. Please login.')
        return redirect('login')

    return render(request, 'students/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    total_students = Student.objects.count()
    today = date.today()

    present = Attendance.objects.filter(date=today, status='Present').count()
    absent = Attendance.objects.filter(date=today, status='Absent').count()
    marked_today = present + absent

    attendance_records = Attendance.objects.all()
    attendance_rate = 0
    if attendance_records.exists():
        total_present = attendance_records.filter(status='Present').count()
        attendance_rate = int((total_present / attendance_records.count()) * 100)

    total_attendance_days = attendance_records.values('date').distinct().count()
    recent_dates = list(
        attendance_records.order_by('-date')
        .values_list('date', flat=True)
        .distinct()[:3]
    )

    return render(request, 'students/dashboard.html', {
        'total': total_students,
        'present': present,
        'absent': absent,
        'marked_today': marked_today,
        'attendance_rate': attendance_rate,
        'attendance_days': total_attendance_days,
        'recent_dates': recent_dates,
    })


@login_required(login_url='login')
def view_students(request):
    search_query = request.GET.get('q', '').strip()
    students = Student.objects.all().order_by('roll_number')

    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(roll_number__icontains=search_query) |
            Q(course__name__icontains=search_query)
        )

    return render(request, 'students/view_students.html', {
        'students': students,
        'search_query': search_query,
    })


@login_required(login_url='login')
def add_student(request):
    if not is_teacher_or_admin(request.user):
        messages.error(request, 'Only teachers or admin can add students.')
        return redirect('students')

    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Student added successfully.')
        return redirect('students')

    return render(request, 'students/add_student.html', {
        'form': form,
        'page_title': 'Add Student',
        'submit_text': 'Add Student',
    })


@login_required(login_url='login')
def edit_student(request, id):
    if not is_teacher_or_admin(request.user):
        messages.error(request, 'Only teachers or admin can edit students.')
        return redirect('students')

    student = get_object_or_404(Student, id=id)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('students')

    return render(request, 'students/add_student.html', {
        'form': form,
        'page_title': 'Edit Student',
        'submit_text': 'Save Changes',
    })


@login_required(login_url='login')
def delete_student(request, id):
    if not is_teacher_or_admin(request.user):
        messages.error(request, 'Only teachers or admin can delete students.')
        return redirect('students')

    student = get_object_or_404(Student, id=id)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
    return redirect('students')


@login_required(login_url='login')
def mark_attendance(request):
    students = Student.objects.all().order_by('roll_number')
    today = date.today()

    if request.method == "POST":
        for student in students:
            status = request.POST.get(str(student.id), 'Present')
            Attendance.objects.update_or_create(
                student=student,
                date=today,
                defaults={'status': status}
            )
        return redirect('dashboard')

    attendance_today = Attendance.objects.filter(date=today)
    attendance_map = {item.student_id: item.status for item in attendance_today}
    present_count = attendance_today.filter(status="Present").count()
    absent_count = attendance_today.filter(status="Absent").count()

    student_rows = [
        {
            'student': student,
            'status': attendance_map.get(student.id, 'Present')
        }
        for student in students
    ]

    return render(request, 'students/mark_attendance.html', {
        'student_rows': student_rows,
        'today': today,
        'present_count': present_count,
        'absent_count': absent_count,
        'total_students': students.count(),
    })


@login_required(login_url='login')
def records(request):
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = date.fromisoformat(selected_date)
        except ValueError:
            selected_date = None

    if not selected_date:
        selected_date = Attendance.objects.order_by('-date').values_list('date', flat=True).first() or date.today()

    records = Attendance.objects.filter(date=selected_date).select_related('student').order_by('student__roll_number')
    present_count = records.filter(status='Present').count()
    absent_count = records.filter(status='Absent').count()
    available_dates = Attendance.objects.order_by('-date').values_list('date', flat=True).distinct()

    return render(request, 'students/records.html', {
        'records': records,
        'selected_date': selected_date,
        'present_count': present_count,
        'absent_count': absent_count,
        'available_dates': available_dates,
    })


@login_required(login_url='login')
def manage_courses(request):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can manage courses.')
        return redirect('dashboard')

    form = CourseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Course added successfully.')
        return redirect('manage_courses')

    courses = Course.objects.all().order_by('name')
    return render(request, 'students/manage_courses.html', {
        'form': form,
        'courses': courses,
    })


@login_required(login_url='login')
def delete_course(request, id):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can delete courses.')
        return redirect('dashboard')

    course = get_object_or_404(Course, id=id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
    return redirect('manage_courses')


@login_required(login_url='login')
def edit_course(request, id):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can edit courses.')
        return redirect('dashboard')

    course = get_object_or_404(Course, id=id)
    form = CourseForm(request.POST or None, instance=course)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Course updated successfully.')
        return redirect('manage_courses')

    courses = Course.objects.all().order_by('name')
    return render(request, 'students/manage_courses.html', {
        'form': form,
        'courses': courses,
        'form_title': 'Edit Course',
        'submit_text': 'Update Course',
        'edit_course_id': course.id,
    })


@login_required(login_url='login')
def manage_subjects(request):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can manage subjects.')
        return redirect('dashboard')

    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Subject added successfully.')
        return redirect('manage_subjects')

    subjects = Subject.objects.all().order_by('name')
    return render(request, 'students/manage_subjects.html', {
        'form': form,
        'subjects': subjects,
    })


@login_required(login_url='login')
def edit_subject(request, id):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can edit subjects.')
        return redirect('dashboard')

    subject = get_object_or_404(Subject, id=id)
    form = SubjectForm(request.POST or None, instance=subject)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Subject updated successfully.')
        return redirect('manage_subjects')

    subjects = Subject.objects.all().order_by('name')
    return render(request, 'students/manage_subjects.html', {
        'form': form,
        'subjects': subjects,
        'form_title': 'Edit Subject',
        'submit_text': 'Update Subject',
        'edit_subject_id': subject.id,
    })


@login_required(login_url='login')
def delete_subject(request, id):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can delete subjects.')
        return redirect('dashboard')

    subject = get_object_or_404(Subject, id=id)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully.')
    return redirect('manage_subjects')


@login_required(login_url='login')
def manage_teachers(request):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can manage teachers.')
        return redirect('dashboard')

    teachers = User.objects.filter(profile__role='teacher').select_related('profile').order_by('username')
    return render(request, 'students/manage_teachers.html', {
        'teachers': teachers,
    })


@login_required(login_url='login')
def add_teacher(request):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can add teachers.')
        return redirect('dashboard')

    form = TeacherForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Teacher added successfully.')
        return redirect('manage_teachers')

    return render(request, 'students/add_teacher.html', {
        'form': form,
        'page_title': 'Add Teacher',
        'submit_text': 'Create Teacher',
    })


@login_required(login_url='login')
def edit_teacher(request, id):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can edit teachers.')
        return redirect('dashboard')

    teacher = get_object_or_404(User, id=id, profile__role='teacher')
    form = TeacherUpdateForm(request.POST or None, instance=teacher)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Teacher updated successfully.')
        return redirect('manage_teachers')

    return render(request, 'students/add_teacher.html', {
        'form': form,
        'page_title': 'Edit Teacher',
        'submit_text': 'Save Changes',
    })


@login_required(login_url='login')
def delete_teacher(request, id):
    if not is_admin(request.user):
        messages.error(request, 'Only admin users can delete teachers.')
        return redirect('dashboard')

    teacher = get_object_or_404(User, id=id, profile__role='teacher')
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Teacher deleted successfully.')
    return redirect('manage_teachers')
