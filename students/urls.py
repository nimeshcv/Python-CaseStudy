from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('students/', views.view_students, name='students'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:id>/', views.delete_student, name='delete_student'),
    path('courses/', views.manage_courses, name='manage_courses'),
    path('courses/edit/<int:id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:id>/', views.delete_course, name='delete_course'),
    path('subjects/', views.manage_subjects, name='manage_subjects'),
    path('subjects/edit/<int:id>/', views.edit_subject, name='edit_subject'),
    path('subjects/delete/<int:id>/', views.delete_subject, name='delete_subject'),
    path('teachers/', views.manage_teachers, name='manage_teachers'),
    path('teachers/add/', views.add_teacher, name='add_teacher'),
    path('teachers/edit/<int:id>/', views.edit_teacher, name='edit_teacher'),
    path('teachers/delete/<int:id>/', views.delete_teacher, name='delete_teacher'),
    path('attendance/', views.mark_attendance, name='attendance'),
    path('records/', views.records, name='records'),
]