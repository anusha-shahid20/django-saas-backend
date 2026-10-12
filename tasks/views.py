from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Project, Task, Company, UserProfile
from .serializers import ProjectSerializer, TaskSerializer, CompanySerializer, UserProfileSerializer


def hello_backend(request):
    """Simple test view that returns a plain text response."""
    return HttpResponse("Hello Backend")


# ============ PROJECT VIEWS ============

class ProjectListAPIView(APIView):
    """
    Handles listing and creating projects.
    GET  -> returns all projects belonging to the current user's company.
    POST -> creates a new project for the current user's company.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only fetch projects that belong to the user's company (tenant isolation)
        projects = Project.objects.filter(company=request.user.profile.company)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically assign the project to the user's company
            serializer.save(company=request.user.profile.company)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ProjectDetailAPIView(APIView):
    """
    Handles retrieve, update, and delete for a single project.
    Only projects belonging to the current user's company are accessible.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Helper: fetch a project by ID, but only from the user's own company."""
        try:
            # Filter by both ID and company to prevent cross-tenant access
            return Project.objects.get(pk=pk, company=user.profile.company)
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
        project.delete()
        return Response({"message": "Project deleted"}, status=204)


# ============ TASK VIEWS ============

class TaskListAPIView(APIView):
    """
    Handles listing and creating tasks.
    GET  -> returns all tasks whose project belongs to the user's company.
    POST -> creates a new task, but only under a project the user owns.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filter tasks through the related project's company (tenant isolation)
        tasks = Task.objects.filter(project__company=request.user.profile.company)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            # Make sure the project being assigned belongs to the user's company
            project_id = request.data.get('project')
            try:
                project = Project.objects.get(pk=project_id, company=request.user.profile.company)
            except Project.DoesNotExist:
                return Response(
                    {"error": "Project not found in your company"},
                    status=400
                )
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TaskDetailAPIView(APIView):
    """
    Handles retrieve, update, partial update, and delete for a single task.
    Only tasks belonging to the user's company are accessible.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Helper: fetch a task by ID, but only from the user's own company."""
        try:
            # Filter by project's company to prevent cross-tenant access
            return Task.objects.get(pk=pk, project__company=user.profile.company)
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
        # partial=True allows updating only some fields instead of all
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
    """
    Handles updating only the status of a task.
    PATCH -> changes the status of a task belonging to the user's company.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            # Only allow access to tasks from the user's own company
            task = Task.objects.get(pk=pk, project__company=request.user.profile.company)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        new_status = request.data.get('status')
        # Validate that the new status is one of the allowed choices
        if new_status not in ['pending', 'in_progress', 'completed']:
            return Response(
                {"error": "Invalid status. Choose from: pending, in_progress, completed"},
                status=400
            )

        task.status = new_status
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data)