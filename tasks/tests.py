from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Company, UserProfile, Project


class TenantIsolationTest(TestCase):
    """
    Tests that users from one company cannot access
    data belonging to another company.
    """

    def setUp(self):
        # Create two separate companies (tenants)
        self.company_a = Company.objects.create(name="Acme Corp")
        self.company_b = Company.objects.create(name="Tech Solutions")

        # Create a user for Company A
        self.user_a = User.objects.create_user(username="user_a", password="testpass123")
        UserProfile.objects.create(user=self.user_a, company=self.company_a, role="employee")

        # Create a user for Company B
        self.user_b = User.objects.create_user(username="user_b", password="testpass123")
        UserProfile.objects.create(user=self.user_b, company=self.company_b, role="employee")

        # Create a project that belongs to Company B
        self.project_b = Project.objects.create(
            name="Company B Secret Project",
            company=self.company_b,
            status="pending"
        )

        # API client to make requests
        self.client = APIClient()

    def test_user_a_cannot_see_company_b_projects(self):
        """Company A's user should see only their own projects (none in this case)."""
        # Login as Company A user
        self.client.force_authenticate(user=self.user_a)

        # Get list of projects
        response = self.client.get('/tasks/api/projects/')

        # Should return 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should NOT include Company B's project
        self.assertEqual(len(response.data), 0)

    def test_user_a_cannot_access_company_b_project_detail(self):
        """Company A's user should get 404 when trying to access Company B's project."""
        # Login as Company A user
        self.client.force_authenticate(user=self.user_a)

        # Try to access Company B's project by ID
        response = self.client.get(f'/tasks/api/projects/{self.project_b.id}/')

        # Should return 404 Not Found (not 403, to avoid leaking existence)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_a_cannot_delete_company_b_project(self):
        """Company A's user should not be able to delete Company B's project."""
        # Login as Company A user
        self.client.force_authenticate(user=self.user_a)

        # Try to delete Company B's project
        response = self.client.delete(f'/tasks/api/projects/{self.project_b.id}/')

        # Should return 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Confirm the project still exists in the database
        self.assertTrue(Project.objects.filter(id=self.project_b.id).exists())