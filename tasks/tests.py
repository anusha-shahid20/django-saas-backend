from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Company, UserProfile, Project, Task


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
        """Company A's user should see only their own projects."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get('/tasks/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_user_a_cannot_access_company_b_project_detail(self):
        """Company A's user should get 404 when accessing Company B's project."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(f'/tasks/api/projects/{self.project_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_a_cannot_delete_company_b_project(self):
        """Company A's user should not be able to delete Company B's project."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(f'/tasks/api/projects/{self.project_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Project.objects.filter(id=self.project_b.id).exists())


class AuthenticationTest(TestCase):
    """Tests for JWT authentication."""

    def setUp(self):
        self.company = Company.objects.create(name="Test Corp")
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        UserProfile.objects.create(user=self.user, company=self.company, role="admin")
        self.client = APIClient()

    def test_login_with_valid_credentials(self):
        """Valid credentials should return access and refresh tokens."""
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_credentials(self):
        """Invalid credentials should return 401."""
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_request_is_rejected(self):
        """Requests without a token should return 401."""
        response = self.client.get('/tasks/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProjectCRUDTest(TestCase):
    """Tests for project CRUD operations."""

    def setUp(self):
        self.company = Company.objects.create(name="Test Corp")
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        UserProfile.objects.create(user=self.user, company=self.company, role="admin")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        """Authenticated user can create a new project."""
        response = self.client.post('/tasks/api/projects/', {
            'name': 'New Project',
            'description': 'Test project',
            'status': 'pending'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Project')

    def test_create_project_with_empty_name(self):
        """Project name cannot be empty."""
        response = self.client.post('/tasks/api/projects/', {
            'name': '',
            'description': 'Test'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_project_with_short_name(self):
        """Project name must be at least 3 characters."""
        response = self.client.post('/tasks/api/projects/', {
            'name': 'AB',
            'description': 'Test'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_projects(self):
        """User should see projects belonging to their company."""
        Project.objects.create(name="Project 1", company=self.company)
        Project.objects.create(name="Project 2", company=self.company)
        response = self.client.get('/tasks/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_soft_delete_project(self):
        """Deleting a project should mark it as deleted, not remove it."""
        project = Project.objects.create(name="To Delete", company=self.company)
        response = self.client.delete(f'/tasks/api/projects/{project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Project still exists in DB but is_deleted=True
        project.refresh_from_db()
        self.assertTrue(project.is_deleted)

        # Project not visible in list
        response = self.client.get('/tasks/api/projects/')
        self.assertEqual(len(response.data), 0)


class TaskCRUDTest(TestCase):
    """Tests for task CRUD operations."""

    def setUp(self):
        self.company = Company.objects.create(name="Test Corp")
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        UserProfile.objects.create(user=self.user, company=self.company, role="admin")
        self.project = Project.objects.create(name="Test Project", company=self.company)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_task(self):
        """Authenticated user can create a task under their project."""
        response = self.client.post('/tasks/api/tasks/', {
            'title': 'New Task',
            'description': 'Test task',
            'project': self.project.id,
            'status': 'pending'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')

    def test_update_task_status(self):
        """User can update only the status of a task via PATCH."""
        task = Task.objects.create(
            title="Task 1",
            project=self.project,
            status="pending"
        )
        response = self.client.patch(
            f'/tasks/api/tasks/{task.id}/status/',
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_update_task_status_invalid(self):
        """Invalid status should return 400."""
        task = Task.objects.create(
            title="Task 1",
            project=self.project,
            status="pending"
        )
        response = self.client.patch(
            f'/tasks/api/tasks/{task.id}/status/',
            {'status': 'invalid_status'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)