from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=[('teacher', 'Teacher'), ('admin', 'Admin')], default='teacher')
    assigned_course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_teachers'
    )
    subjects = models.ManyToManyField('Subject', blank=True, related_name='teachers')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ('roll_number', 'course')


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10)  # Present / Absent

    def __str__(self):
        return f"{self.student.name} - {self.status}"
