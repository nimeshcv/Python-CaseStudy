from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):
    def test_superuser_without_profile_can_view_dashboard(self):
        user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="pass12345",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_superuser_without_profile_can_view_students(self):
        user = User.objects.create_superuser(
            username="admin2",
            email="admin2@example.com",
            password="pass12345",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("students"))

        self.assertEqual(response.status_code, 200)
