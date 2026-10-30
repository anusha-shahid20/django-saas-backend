from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.db import transaction
from .models import Project, Task, Company, UserProfile, Note
from .serializers import ProjectSerializer, TaskSerializer, CompanySerializer, UserProfileSerializer, NoteSerializer


def hello_backend(request):
    """Simple test view that returns a plain text response."""
    return HttpResponse("Hello Backend")


# ============ SIGNUP VIEW ============

class SignupAPIView(APIView):
    permission_classes = [] 
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        company_name = request.data.get('company_name')

        if not username or not password or not company_name:
            return Response({"error": "Username, password, and company name are required."}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=400)

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password, email=email)
                company = Company.objects.create(name=company_name)
                UserProfile.objects.create(user=user, company=company, role='admin')
            return Response({"message": "Account created successfully!"}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# ============ ADD EMPLOYEE VIEW ============

class AddEmployeeAPIView(APIView):
    """
    Allows an Admin/HR to add a new employee to their own company.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.profile.role != 'admin':
            return Response({"error": "Only Admins can add employees."}, status=403)

        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=400)

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password)
                UserProfile.objects.create(
                    user=user, 
                    company=request.user.profile.company, 
                    role='employee'
                )
            return Response({"message": "Employee added successfully."}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# ============ CHANGE PASSWORD VIEW ============

class ChangePasswordAPIView(APIView):
    """
    Allows a logged-in user to change their password.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({"error": "Both old and new passwords are required."}, status=400)

        # Check if the old password matches
        if not user.check_password(old_password):
            return Response({"error": "Incorrect old password."}, status=400)

        # Set the new password securely
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully!"}, status=200)


# ============ NOTE VIEWS ============

class NoteListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notes = Note.objects.filter(company=request.user.profile.company)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=request.user.profile.company)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class NoteDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Note.objects.get(pk=pk, company=user.profile.company)
        except Note.DoesNotExist:
            return None

    def get(self, request, pk):
        note = self.get_object(pk, request.user)
        if note is None:
            return Response({"error": "Note not found"}, status=404)
        serializer = NoteSerializer(note)
        return Response(serializer.data)

    def put(self, request, pk):
        note = self.get_object(pk, request.user)
        if note is None:
            return Response({"error": "Note not found"}, status=404)
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# ============ PROJECT VIEWS ============

class ProjectListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.filter(company=request.user.profile.company, is_deleted=False)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=request.user.profile.company)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ProjectDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Project.objects.get(pk=pk, company=user.profile.company, is_deleted=False)
        except Project.DoesNotExist:
            return None

    def get(self, request, pk):
        project = self.get_object(pk, request.user)
        if project is None:
            return Response({"error": "Project not found"}, status=404)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, pk):
        project = self.get_object(pk, request.user)
        if project is None:
            return Response({"error": "Project not found"}, status=404)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        project = self.get_object(pk, request.user)
        if project is None:
            return Response({"error": "Project not found"}, status=404)
        project.is_deleted = True
        project.save()
        return Response({"message": "Project deleted"}, status=204)


# ============ TASK VIEWS ============

class TaskListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(project__company=request.user.profile.company, project__is_deleted=False)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            project_id = request.data.get('project')
            try:
                Project.objects.get(pk=project_id, company=request.user.profile.company, is_deleted=False)
            except Project.DoesNotExist:
                return Response({"error": "Project not found in your company"}, status=400)
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TaskDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Task.objects.get(pk=pk, project__company=user.profile.company, project__is_deleted=False)
        except Task.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self.get_object(pk, request.user)
        if task is None:
            return Response({"error": "Task not found"}, status=404)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = self.get_object(pk, request.user)
        if task is None:
            return Response({"error": "Task not found"}, status=404)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        task = self.get_object(pk, request.user)
        if task is None:
            return Response({"error": "Task not found"}, status=404)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        task = self.get_object(pk, request.user)
        if task is None:
            return Response({"error": "Task not found"}, status=404)
        task.delete()
        return Response({"message": "Task deleted"}, status=204)


class TaskStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, project__company=request.user.profile.company, project__is_deleted=False)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        new_status = request.data.get('status')
        if new_status not in ['pending', 'in_progress', 'completed']:
            return Response({"error": "Invalid status. Choose from: pending, in_progress, completed"}, status=400)

        task.status = new_status
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data)


# ============ FILE UPLOAD VIEW ============

class FileUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=400)
        return Response({"message": "File uploaded successfully", "filename": file_obj.name, "size": file_obj.size}, status=201)