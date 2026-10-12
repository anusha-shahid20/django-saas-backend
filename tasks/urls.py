from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_backend, name='hello_backend'),
    path('api/projects/', views.ProjectListAPIView.as_view(), name='project-list'),
    path('api/projects/<int:pk>/', views.ProjectDetailAPIView.as_view(), name='project-detail'),
    path('api/tasks/', views.TaskListAPIView.as_view(), name='task-list'),
    path('api/tasks/<int:pk>/', views.TaskDetailAPIView.as_view(), name='task-detail'),
    path('api/tasks/<int:pk>/status/', views.TaskStatusUpdateAPIView.as_view(), name='task-status-update'),
]