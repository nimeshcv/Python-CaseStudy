from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Course, Student, Subject, UserProfile


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'course']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Student full name', 'required': True}
            ),
            'roll_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Roll number', 'required': True}
            ),
            'course': forms.Select(
                attrs={'class': 'form-control', 'required': True}
            ),
        }
        labels = {
            'name': 'Name',
            'roll_number': 'Roll Number',
            'course': 'Course',
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Course name', 'required': True}
            ),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Course description', 'rows': 4}
            ),
        }
        labels = {
            'name': 'Course Name',
            'description': 'Description',
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Subject name', 'required': True}
            ),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Subject description', 'rows': 4}
            ),
        }
        labels = {
            'name': 'Subject Name',
            'description': 'Description',
        }


class TeacherForm(UserCreationForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    assigned_course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'assigned_course', 'subjects']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                role='teacher',
                assigned_course=self.cleaned_data.get('assigned_course')
            )
            profile.subjects.set(self.cleaned_data.get('subjects'))
        return user


class TeacherUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    assigned_course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['assigned_course'].initial = profile.assigned_course
            self.fields['subjects'].initial = profile.subjects.all()

    def save(self, commit=True):
        user = super().save(commit=commit)
        if hasattr(user, 'profile'):
            profile = user.profile
        else:
            profile = UserProfile(user=user, role='teacher')
        profile.assigned_course = self.cleaned_data.get('assigned_course')
        profile.save()
        profile.subjects.set(self.cleaned_data.get('subjects'))
        return user
